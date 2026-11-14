import difflib
import json
import os
import platform
import subprocess
import time
from functools import lru_cache
from pathlib import Path

import psutil
from langchain_core.tools import tool

ALIASES = {
    "vscode": "visualstudiocode",
    "code": "visualstudiocode",
    "chrome": "googlechrome",
    "ppt": "microsoftpowerpoint",
}

MAC_FOLDERS = [
    "/Applications",
    "/Applications/Utilities",
    "/System/Applications",
    "/System/Applications/Utilities",
    "/System/Volumes/Preboot/Cryptexes/App/System/Applications",
    str(Path.home() / "Applications"),
]


def _norm(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalnum())


@lru_cache(maxsize=1)
def _installed() -> dict:
    """Map each installed app's display name to what is needed to launch it."""
    system = platform.system()
    apps = {}

    if system == "Darwin":
        for folder in MAC_FOLDERS:
            path = Path(folder)
            if path.is_dir():
                for item in sorted(path.glob("*.app")):
                    apps.setdefault(item.stem, str(item))
        finder = Path("/System/Library/CoreServices/Finder.app")
        if finder.exists():
            apps.setdefault("Finder", str(finder))

    elif system == "Windows":
        script = "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-StartApps | ConvertTo-Json"
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        ).stdout
        data = json.loads(out) if out.strip() else []
        if isinstance(data, dict):
            data = [data]
        for item in data:
            apps.setdefault(item["Name"], item["AppID"])

    return apps


def _find(query: str, pool=None) -> list:
    names = {_norm(name): name for name in (pool if pool is not None else _installed())}
    q = _norm(query)
    q = ALIASES.get(q, q)
    if not q:
        return []
    if q in names:
        return [names[q]]
    for test in (lambda k: k.startswith(q), lambda k: q in k):
        hits = [name for key, name in names.items() if test(key)]
        if hits:
            return hits
    close = difflib.get_close_matches(q, list(names), n=3, cutoff=0.75)
    return [names[k] for k in close]


@tool
def open_app(app_name: str) -> str:
    """Open any application installed on this computer (macOS or Windows) by its name."""
    system = platform.system()
    if system not in ("Darwin", "Windows"):
        return "Unsupported operating system."

    try:
        matches = _find(app_name)
        if not matches:
            return f"I couldn't find an app called {app_name} on this computer."
        if len(matches) > 1:
            return "Several apps match: " + ", ".join(matches[:5]) + ". Ask the user which one."

        name = matches[0]
        target = _installed()[name]

        if system == "Darwin":
            result = subprocess.run(["open", target], capture_output=True)
            if result.returncode != 0:
                return f"{name} could not be opened."
        else:
            subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{target}"])

        return f"Opening {name}."

    except Exception as e:
        return f"Could not open application: {e}"


PROTECTED = {"finder", "dock", "explorer", "applicationframehost", "searchhost"}


def _running() -> dict:
    """Map each open, user-facing app to what is needed to close it."""
    system = platform.system()
    apps = {}

    if system == "Darwin":
        folders = {str(Path(f)) for f in MAC_FOLDERS}
        for proc in psutil.process_iter(["exe"]):
            exe = proc.info.get("exe") or ""
            if ".app/" not in exe:
                continue
            bundle = Path(exe[: exe.index(".app/") + 4])
            if str(bundle.parent) in folders:
                apps.setdefault(bundle.stem, str(bundle))

    elif system == "Windows":
        script = (
            "[Console]::OutputEncoding=[Text.Encoding]::UTF8; "
            "Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -or $_.Path -like '*\\WindowsApps\\*' } | "
            "ForEach-Object { [pscustomobject]@{ Id = $_.Id; Name = $_.ProcessName; "
            "Desc = $(try { $_.MainModule.FileVersionInfo.FileDescription } catch { $null }) } } "
            "| ConvertTo-Json"
        )
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        ).stdout
        data = json.loads(out) if out.strip() else []
        if isinstance(data, dict):
            data = [data]
        for item in data:
            label = (item.get("Desc") or "").strip() or item["Name"]
            apps.setdefault(label, []).append(int(item["Id"]))

    return apps


def _hosts_marvin(system: str, target) -> bool:
    """True if the app is running Marvin itself (for example the terminal window)."""
    try:
        parents = psutil.Process().parents()
    except Exception:
        return False
    for parent in parents:
        try:
            if system == "Darwin":
                if (parent.exe() or "").startswith(target + "/"):
                    return True
            elif parent.pid in target or os.getpid() in target:
                return True
        except Exception:
            continue
    return False


@tool
def is_app_open(app_name: str) -> str:
    """Check whether an application is currently open on this computer."""
    if platform.system() not in ("Darwin", "Windows"):
        return "Unsupported operating system."
    try:
        open_now = _find(app_name, _running())
        if open_now:
            return "Open: " + ", ".join(open_now[:5]) + "."
        if _find(app_name):
            return f"{app_name} is installed but not open."
        return f"I couldn't find an app called {app_name} on this computer."
    except Exception as e:
        return f"Could not check applications: {e}"


@tool
def close_app(app_name: str) -> str:
    """Close an application that is currently open on this computer (macOS or Windows)."""
    system = platform.system()
    if system not in ("Darwin", "Windows"):
        return "Unsupported operating system."

    if _norm(app_name) in PROTECTED:
        return f"I won't close {app_name} because it is a system app."

    try:
        running = _running()
        matches = _find(app_name, running)

        if not matches:
            if _find(app_name):
                return f"{app_name} is not open right now."
            return f"I couldn't find an app called {app_name} on this computer."
        if len(matches) > 1:
            return "Several open apps match: " + ", ".join(matches[:5]) + ". Ask the user which one."

        name = matches[0]
        target = running[name]

        if _norm(name) in PROTECTED or _hosts_marvin(system, target):
            return f"I won't close {name} because it is a system app or it is running Marvin."

        if system == "Darwin":
            safe = name.replace("\\", "\\\\").replace('"', '\\"')
            subprocess.run(
                ["osascript", "-e", f'tell application "{safe}" to quit'],
                capture_output=True, timeout=10,
            )
        else:
            for pid in target:
                subprocess.run(["taskkill", "/PID", str(int(pid))], capture_output=True)

        for _ in range(6):
            time.sleep(0.5)
            if name not in _running():
                return f"Closed {name}."
        return f"I asked {name} to close, but it is still open. It may be waiting for you to save your work."

    except Exception as e:
        return f"Could not close application: {e}"


APP_TOOLS = [open_app, close_app, is_app_open]

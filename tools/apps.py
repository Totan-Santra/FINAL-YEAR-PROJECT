import platform
import subprocess

from langchain_core.tools import tool

@tool
def open_app(app_name: str) -> str:
    """Open an approved application on macOS or Windows."""

    apps = {
        "mac": {
            "safari": "Safari",
            "chrome": "Google Chrome",
            "vscode": "Visual Studio Code",
            "visualstudiocode": "Visual Studio Code",
            "code": "Visual Studio Code",
            "googlechrome": "Google Chrome",
            "calculator": "Calculator",
            "terminal": "Terminal",
            "notes": "Notes",
            "finder": "Finder"
        },

        "windows": {
            "chrome": "chrome",
            "vscode": "code",
            "visualstudiocode": "code",
            "code": "code",
            "googlechrome": "chrome",
            "calculator": "calc.exe",
            "terminal": "wt.exe",
            "notepad": "notepad.exe",
            "explorer": "explorer.exe"
        }
    }

    os_name = platform.system()
    key = "".join(c for c in app_name.lower() if c.isalnum())

    try:

        if os_name == "Darwin":

            app = apps["mac"].get(key)

            if not app:
                return "Application not supported on macOS."

            subprocess.Popen(["open", "-a", app])

        elif os_name == "Windows":

            app = apps["windows"].get(key)

            if not app:
                return "Application not supported on Windows."

            subprocess.Popen(["cmd", "/c", "start", "", app])

        else:
            return "Unsupported operating system."

        return f"Opening {app_name} successfully."

    except FileNotFoundError:
        return f"{app_name} is not installed or not available."

    except Exception as e:
        return f"Could not open application: {e}"
    
CLOSABLE = {
    "mac": {
        "safari": "Safari",
        "chrome": "Google Chrome",
        "googlechrome": "Google Chrome",
        "vscode": "Visual Studio Code",
        "visualstudiocode": "Visual Studio Code",
        "code": "Visual Studio Code",
        "calculator": "Calculator",
        "notes": "Notes",
    },
    "windows": {
        "chrome": "chrome.exe",
        "googlechrome": "chrome.exe",
        "vscode": "Code.exe",
        "visualstudiocode": "Code.exe",
        "code": "Code.exe",
        "calculator": "CalculatorApp.exe",
        "notepad": "notepad.exe",
    },
}


@tool
def close_app(app_name: str) -> str:
    """Close an approved application on macOS or Windows."""
    key = "".join(c for c in app_name.lower() if c.isalnum())
    os_name = platform.system()

    try:
        if os_name == "Darwin":
            app = CLOSABLE["mac"].get(key)
            if not app:
                return "I can't close that application."
            result = subprocess.run(
                ["osascript", "-e", f'tell application "{app}" to quit'],
                capture_output=True, text=True,
            )
        elif os_name == "Windows":
            app = CLOSABLE["windows"].get(key)
            if not app:
                return "I can't close that application."
            result = subprocess.run(
                ["taskkill", "/IM", app], capture_output=True, text=True
            )
        else:
            return "Unsupported operating system."

        if result.returncode != 0:
            return f"{app_name} is not running or could not be closed."
        return f"Closed {app_name}."

    except Exception as e:
        return f"Could not close application: {e}"


APP_TOOLS = [open_app, close_app]


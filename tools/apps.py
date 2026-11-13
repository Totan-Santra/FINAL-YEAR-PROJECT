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
    
APP_TOOLS = [open_app]


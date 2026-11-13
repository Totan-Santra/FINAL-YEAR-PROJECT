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
            "calculator": "Calculator",
            "terminal": "Terminal",
            "notes": "Notes",
            "finder": "Finder"
        },

        "windows": {
            "chrome": "chrome",
            "vscode": "code",
            "calculator": "calc.exe",
            "terminal": "wt.exe",
            "notepad": "notepad.exe",
            "explorer": "explorer.exe"
        }
    }

    os_name = platform.system()

    try:

        if os_name == "Darwin":

            app = apps["mac"].get(app_name.lower().strip())

            if not app:
                return "Application not supported on macOS."

            subprocess.Popen(["open", "-a", app])

        elif os_name == "Windows":

            app = apps["windows"].get(app_name.lower().strip())

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


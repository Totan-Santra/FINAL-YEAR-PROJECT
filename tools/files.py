from langchain_core.tools import tool
from langgraph.errors import GraphBubbleUp
from langgraph.types import interrupt

from settings import WORKSPACE
from tools.common import is_yes

BASE_DIR = WORKSPACE.resolve()
BASE_DIR.mkdir(parents=True, exist_ok=True)

@tool
def file_manager(
    operation: str,
    filename: str = "",
    content: str = "",
    new_filename: str = ""
) -> str:
    """
    Manage files inside workspace.

    Operations:
    create, read, write, append, delete, list, rename.
    """

    allowed_extensions = {".txt", ".py", ".md"}

    try:

        if operation == "list":
            files = [
                str(p.relative_to(BASE_DIR))
                for p in BASE_DIR.rglob("*")
                if p.is_file()
            ]

            return "\n".join(files) if files else "Workspace is empty."

        if not filename:
            return "Filename is required."

        file_path = (BASE_DIR / filename).resolve()

        if not file_path.is_relative_to(BASE_DIR):
            return "Access denied."

        if file_path.suffix.lower() not in allowed_extensions:
            return "Unsupported file type."

        if operation == "create":

            if file_path.exists():
                return "File already exists."

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

            return "File created successfully."

        elif operation == "read":

            if not file_path.is_file():
                return "File not found."

            return file_path.read_text(encoding="utf-8")

        elif operation == "write":

            if file_path.exists():
                return "File already exists. Use append or obtain overwrite approval."

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

            return "File written successfully."

        elif operation == "append":

            if not file_path.is_file():
                return "File not found."

            with file_path.open("a", encoding="utf-8") as file:
                file.write(content)

            return "Content appended successfully."

        elif operation == "delete":

            if not file_path.is_file():
                return "File not found."

            file_path.unlink()

            return "File deleted successfully."

        elif operation == "rename":

            if not new_filename:
                return "New filename is required."

            new_path = (BASE_DIR / new_filename).resolve()

            if not new_path.is_relative_to(BASE_DIR):
                return "Access denied."

            if not file_path.is_file():
                return "File not found."

            if new_path.exists():
                return "Destination already exists."

            if new_path.suffix.lower() not in allowed_extensions:
                return "Unsupported destination file type."

            new_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.rename(new_path)

            return "File renamed successfully."

        return "Invalid operation."

    except Exception as e:
        return f"File operation failed: {e}"

FILE_TOOLS = [file_manager]


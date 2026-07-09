import os

def get_project_root() -> str:
    current_path = os.path.abspath(__file__) #/Users/Desktop/myproject/utils/file_handler.py

    while True:
        current_path= os.path.dirname(current_path)#/Users/Desktop/myproject/utils， /Users/Desktop/myproject
 
        if os.path.exists(os.path.join(current_path, "pyproject.toml")):#/Users/Desktop/myproject/utils/pyproject.toml
            return current_path #/Users/Desktop/myproject/utils， /Users/Desktop/myproject
        if current_path == os.path.dirname(current_path): # "/" == "/" → True
            raise RuntimeError("Project root not found")

def get_abs_path(relative_path: str) -> str:
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)
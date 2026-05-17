import os
import subprocess
import datetime
import config
from config import CHROME_PATH

KNOWN_FOLDERS = {
    "desktop": os.path.join(os.environ["USERPROFILE"], "Desktop"),
    "documents": os.path.join(os.environ["USERPROFILE"], "Documents"),
    "downloads": os.path.join(os.environ["USERPROFILE"], "Downloads"),
    "pictures": os.path.join(os.environ["USERPROFILE"], "Pictures"),
    "videos": os.path.join(os.environ["USERPROFILE"], "Videos"),
    "music": os.path.join(os.environ["USERPROFILE"], "Music"),
}

def get_time() -> str:
    now = datetime.datetime.now()
    return now.strftime("It's %I:%M %p on %A, %B %d, %Y.")

def open_folder(folder_path: str) -> str:
    if os.path.exists(folder_path):
        config.current_folder = folder_path
        subprocess.Popen(["explorer", folder_path])
        return f"Opening folder: {os.path.basename(folder_path)}"
    else:
        return f"Sorry, I couldn't find the folder: {folder_path}"

def find_and_open_folder(folder_name: str) -> str:
    folder_name_lower = folder_name.lower()

    if config.current_folder and os.path.exists(config.current_folder):
        try:
            with os.scandir(config.current_folder) as it:
                for entry in it:
                    if entry.is_dir() and folder_name_lower in entry.name.lower():
                        return open_folder(entry.path)
        except (PermissionError, OSError):
            pass

    if folder_name_lower in KNOWN_FOLDERS:
        return open_folder(KNOWN_FOLDERS[folder_name_lower])

    search_roots = ["D:\\", "E:\\"]
    max_depth = 4

    for root in search_roots:
        if not os.path.exists(root):
            continue
            
        queue = [(root, 0)]
        
        while queue:
            current_path, depth = queue.pop(0)
            
            if depth > max_depth:
                continue
                
            try:
                with os.scandir(current_path) as it:
                    for entry in it:
                        if entry.is_dir():
                            # Ignore hidden folders like .git, .vscode, $RECYCLE.BIN
                            if entry.name.startswith('.') or entry.name.startswith('$'):
                                continue
                                
                            if folder_name_lower in entry.name.lower():
                                return open_folder(entry.path)
                            
                            if depth < max_depth:
                                queue.append((entry.path, depth + 1))
            except (PermissionError, OSError):
                continue

    return f"Sorry, no file or folder found named '{folder_name}'."

def create_folder(folder_name: str, location: str = None) -> str:
    if location is None:
        location = KNOWN_FOLDERS["desktop"]

    folder_path = os.path.join(location, folder_name)
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Created folder '{folder_name}' on your Desktop."
    except Exception as e:
        return f"Sorry, I couldn't create the folder: {e}"

def create_file(file_name: str, location: str = None) -> str:
    if location is None:
        location = KNOWN_FOLDERS["desktop"]

    if "." not in file_name:
        file_name += ".txt"

    file_path = os.path.join(location, file_name)
    try:
        with open(file_path, "w") as f:
            pass
        return f"Created file '{file_name}' on your Desktop."
    except Exception as e:
        return f"Sorry, I couldn't create the file: {e}"

def build_app_map():
    if config._app_map:
        return
        
    paths = [
        r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs',
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs')
    ]
    
    for p in paths:
        if not os.path.exists(p):
            continue
        try:
            for r, d, files in os.walk(p):
                for f in files:
                    if f.endswith('.lnk'):
                        app_name = f[:-4].lower()
                        config._app_map[app_name] = os.path.join(r, f)
        except Exception:
            pass

def open_app(app_name: str) -> str:
    build_app_map()
    
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "file explorer": "explorer.exe",
        "command prompt": "cmd.exe",
        "task manager": "taskmgr.exe",
        "settings": "ms-settings:",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "chrome": CHROME_PATH,
        "whatsapp": "whatsapp:",
    }

    key = app_name.lower().strip()
    
    executable = app_map.get(key)
    
    if not executable and key in config._app_map:
        executable = config._app_map[key]
        
    if not executable:
        for mapped_name, mapped_path in config._app_map.items():
            if key in mapped_name or mapped_name in key:
                executable = mapped_path
                break

    if executable:
        try:
            if executable.endswith(".lnk") or executable.startswith("ms-") or executable.endswith(":"):
                os.startfile(executable)
            else:
                subprocess.Popen(executable, shell=True)
            return f"Opening {app_name} for you."
        except Exception as e:
            return f"Sorry, I couldn't open {app_name}: {e}"
    else:
        return f"I don't know how to open '{app_name}'. I couldn't find it installed on your PC."

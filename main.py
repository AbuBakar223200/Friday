import sys
import os
import subprocess

# Auto-activate/re-execute in virtual environment if available
venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv')
if os.path.exists(venv_path):
    if os.name == 'nt':
        venv_python = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join(venv_path, 'bin', 'python')

    if os.path.exists(venv_python):
        current_exe = os.path.realpath(sys.executable)
        venv_exe = os.path.realpath(venv_python)
        if current_exe != venv_exe:
            try:
                sys.exit(subprocess.call([venv_python] + sys.argv))
            except KeyboardInterrupt:
                print("\n[friday] Friday systems offline.")
                sys.exit(130)
            except Exception as e:
                print(f"[SYSTEM] Failed to re-execute in virtual environment: {e}")

from friday.app import main
from friday.audio.tts import stop_speaking

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_speaking()
        print("\n[friday] Friday systems offline.")

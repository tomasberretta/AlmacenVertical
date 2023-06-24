import os
import platform
import subprocess

from dotenv import load_dotenv

load_dotenv()

run_env = []
to_run = []

system = platform.system()

if system == "Windows":
    run_env.append("venv\\Scripts\\activate.bat")
else:
    run_env.append("source")
    run_env.append("venv/bin/activate")

run_start_back = run_env + ["&&", "python", "back.py"]
to_run.append(run_start_back)

for run in to_run:
    cmd = " ".join(run)
    cmd = cmd + " & pause"

    if system == "Windows":
        from subprocess import CREATE_NEW_CONSOLE
        subprocess.Popen(["cmd", "/c", cmd], creationflags=CREATE_NEW_CONSOLE)

    elif system == "Linux":
        subprocess.Popen(["xterm", "-hold", "-e", cmd])

    elif system == "Darwin":
        directory = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen(["open", "-a", "Terminal.app", "--args", "-c", f"cd {directory} && {cmd}"])

    else:
        print(f"Unsupported system: {system}")

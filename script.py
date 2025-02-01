import subprocess
import time

subprocess.run(["python3", "manage.py", "migrate"])
time.sleep(2)
subprocess.run(["python3", "manage.py", "runserver"])

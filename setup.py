import os
import datetime

def build():
    os.system("apt update")
    os.system("apt install git")
    os.system("git config --global user.name 'CBcodes03'")
    os.system("git config --global user.email 'chiragbudakoti12334@gmail.com'")
    os.system("git init")
    os.system("git checkout local")
    os.system("git add .")
    os.system("git commit -m 'git setup-done'")
    # Secure token retrieval from environment variable
    token = os.getenv("GITHUB_TOKEN")
    if token:
        os.system(f"git remote add origin https://CBcodes03:{token}@github.com/CBcodes03/cbblogs.git")
        os.system("git push -u origin local")  # Using 'local' branch for push
    else:
        print("Error: GitHub token not found in environment variables.")
    return None

def pushing_func():
    os.system("git checkout local")
    os.system("git add .")
    os.system(f"git commit -m '{datetime.datetime.now()}'")
    os.system("git push -u origin local")  # Push to 'local' branch
    return None

def pulling_func():
    os.system("git pull origin local")  # Pull from 'local' branch
    return None

build()
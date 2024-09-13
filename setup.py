import os
import datetime
def build():
    os.system("apt update")
    os.system("apt install git")
    os.system("git config --global user.name CBcodes03")
    os.system("git config --global user.email chiragbudakoti12334@gmail.com")
    os.system("git init")
    os.system("git add .")
    os.system("git commit -m 'git setup-done'")
    os.system("git remote add origin https://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@github.com/CBcodes03/test.git")
    os.system("git push -u origin main")
    return None
build()

def pushing_func():
    os.system("git add .")
    os.system(f"git commit -m '{datetime.datetime.now()}'")
    os.system("git push -u origin main")
    return None

def pulling_func():
    os.system("git pull origin main")
    return None
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
    os.system("git remote add origin https://CBcodes03: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@github.com/CBcodes03/cbblogs.git")
    os.system("git push -u origin local")
    return None
build()

def pushing_func():
    os.system("git add .")
    os.system(f"git commit -m '{datetime.datetime.now()}'")
    os.system("git push -u origin local")
    return None

def pulling_func():
    os.system("git pull origin local")
    return None

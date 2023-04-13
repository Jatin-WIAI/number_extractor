import sys
import os

os.system("pip install -r requirements.txt")
os.system("git clone https://github.com/Jatin-WIAI/indic-ITN.git")
os.system("cd indic-ITN && bash install.sh")
os.system("cd indic-ITN && python setup.py bdist_wheel")
os.system("cd indic-ITN && pip install -e .")


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


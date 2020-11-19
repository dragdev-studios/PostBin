from os import path
from sys import argv

from postbin import postSync

if len(argv) >= 2:
    text = ' '.join(argv[1:])
else:
    text = input(
        "What text would you like to put on hastebin?\nIf you provide a filepath, it will post that file's content\n\n> ")
if path.exists(text):
    try:
        with open(text) as rfile:
            text = rfile.read()
    except:
        print("Attempted to open a file, but was unable to. Assuming you didn't want to.")
print("\nPosting...")
url = postSync(text, retry=10)
try:
    import webbrowser

    webbrowser.open(url, 0)
except ImportError:
    webbrowser = None
    print("Tried to open in browser, but webbrowser was not installed.")
    print()
print("URL:", url)
exit(0)
#

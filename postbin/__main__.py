from postbin import postSync
text = input("What text would you like to put on hastebin?\nP.S: provide a .txt file path to post it's content\n\n> ")
if text.lower().endswith(".txt"):
    try:
        with open(text) as rfile:
            text = rfile.read()
    except:
        print("Attempted to open a file, but was unable to. Assuming you didn't want to.")
print(postSync(text))
exit(0)

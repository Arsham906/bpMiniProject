import json
import inquirer
from getpass import getpass
import curses
# from curses import wrapper

def main(stdscr):
    stdscr.clear()

    # Don't do this:
    # for char in stdscr:  # This will raise the TypeError

    # Instead, use curses methods to access window content
    y, x = stdscr.getyx()  # Get cursor position
    stdscr.addstr(y, x, "Hello, world!")
    stdscr.refresh()
    stdscr.getch()
    

data = '''
[
    {
        "lable": null,
        "note": ["note", "aval"],
        "time stamp": "smth"
    },
    {
        "lable": "mammad",
        "note": ["note", "dovom"],
        "time stamp": "smth"
    }
] 
'''

password = getpass("password: ")
print("password was: ", password)

curses.wrapper(main)
cmdList = ["view", "change a note", "delete a note", "add a note", "quite"]

cmd = inquirer.list_input("what do you wanna do?", choices=cmdList)

if cmd == cmdList[0]:
    print("hexb")
notes = json.loads(data)
notes[0]["note"] = ["note", "dovom", "?"]
print(type(notes))
print(notes)

cmd = input("$ ")
if cmd == "less":
    curses.wrapper(main)

def addNote(path, notes, note, timestamp, lable = None):
    with open(path, 'w') as fw:
        tmpDict = {"lable": lable, "note": note, "time stamp": timestamp}
        notes.append(tmpDict)
        json.dump(notes, fw)

addNote("test.txt", notes, "newNote", "time")

def readNotes(path):
    with open(path, 'r') as fr:
        notes = []
        notes = json.load(fr)
        
    return notes

newNotes = readNotes("test.txt")
print(type(newNotes))
print(newNotes)
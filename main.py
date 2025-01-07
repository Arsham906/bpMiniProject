import os
import datetime
from cryptography.fernet import Fernet
import json
import inquirer
from getpass import getpass
import curses
import subprocess

PROFILE = "profile.txt"

def clear():
    operatingSystem = os.sys.platform
    if operatingSystem == 'win32':
        subprocess.run('cls', shell=True)
    elif operatingSystem == 'linux' or operatingSystem == 'darwin':
        subprocess.run('clear', shell=True)
        
def less(stdscr):
    stdscr.clear()
    stdscr.addstr("notes...\n")
    hBars = 1
    helpBar = curses.newwin(hBars, curses.COLS - 1, curses.LINES - 1, 0)
    helpBar.refresh()
    helpBar.addstr("nextPage(n), previousPage(p), dow(s), up(w), quit(q)")
    pad = curses.newpad(1000, 1000)
    for i in range(999):
        pad.addstr("~\n")
    pad.move(0, 0)
    stdscr.refresh()
    helpBar.refresh()
    # lineCtr = 0
    # for i in range(len(notes)):
    #     tmp = str(i) + ': '
    #     if notes[i]["label"]:
    #         tmp += '(' + notes[i]['label'] + ') '
    #     lineCount = len(notes[i]["note"])
    #     lineCtr += lineCount
    #     for ln in range(lineCount):
    #         if ln == lineCount - 1:
    #             tmp += notes[i]["note"][ln]
    #             break
    #         tmp += notes[i]["note"][ln] + '\n'
    #     tmp += ' (' + notes[i]["timeStamp"] + ')\n'
    lineCtr, tmp = xtrctNote(notes)
    pad.addstr(tmp)
    pad.refresh(0, 0, 0, 0, curses.LINES - 1 - hBars, curses.COLS - 1)
    line = 0
    stdscr.nodelay(True)
    while True:
        try:
            key = stdscr.getkey()
        except:
            key = None

        if key == 's':
            if line + 1 < lineCtr:
                line += 1
        elif key == 'w':
            if line > 0:
                line -= 1
        elif key == "q":
            break
        elif key == 'n':
            if line + curses.LINES <= lineCtr:
                line += curses.LINES - hBars
        elif key == 'p':
            if line - curses.LINES > 1:
                line -= curses.LINES - hBars
            else:
                line = 0 
            
        pad.refresh(line, 0, 0, 0, curses.LINES - 2, curses.COLS - 1)                

    stdscr.getch()

def encryptFile(path, key):
    f = Fernet(key)
    with open(path, 'rb') as fr:
        oCon = fr.read()
    eCon = f.encrypt(oCon)
    with open(path, 'wb') as fwb:
        fwb.write(eCon)

def decryptFile(path, key):
    f = Fernet(key)
    with open(path, 'rb') as fr:
        eCon = fr.read()
    dCon = f.decrypt(eCon)
    with open(path, 'wb') as fw:
        fw.write(dCon)

def getUserFiles(u, notes: bool, label: bool):
    tmpN = ''
    tmpL = ''
    if notes:
        tmpN = u.capitalize() + '/' + u + '.txt'
    if label:
        tmpL = u.capitalize() + '/' + u + 'label.txt'
    return [tmpN, tmpL]

def isInteger(s):
    for c in s:
        if not (ord(c) >= ord('0') and ord(c) <= ord('9')):
            return False
    return True

def signUp(u, p):
    key = Fernet.generate_key()
    f = open(PROFILE, 'a')
    f.write(u + " | " +  p + " | " + key.decode('utf-8') + '\n')
    f.close()
    return key

# -1: bad error / 0: no account / key: account was found
def login(u, p):
    try:
        with open(PROFILE, 'r') as f:
            lines = f.readlines()
            for line in lines:
                tmp = line.split('|')
                if tmp[0].strip() == u and tmp[1].strip() == p:
                    key = tmp[2].strip().encode('utf-8')
                    return key
            return 0
    except FileNotFoundError:
        return 0
        
    return -1

# notes: success / empty list: failure
def readNotes(user, key):
    path = getUserFiles(user, True, False)[0]
    try:
        decryptFile(path, key)
    except:
        pass
    try:
        with open(path, 'r') as fr:
            notes = []
            tmp = fr.read().strip('=')
            notes = json.loads(tmp)
            encryptFile(path, key)
            return notes
    except:
        try:
            encryptFile(path, key)
        except:
            pass
        return []

# new list of notes: success / 0: faliure
def _addNote(user, key, notes: list, note: str, label = None):
    path = getUserFiles(user, True, False)[0]
    try:
        decryptFile(path, key)
    except:
        if not os.path.isdir(user.capitalize()):
            os.mkdir(user.capitalize())
        f = open(path, 'w')
        f.close()
    try:
        with open(path, 'w') as fw:
            tmpDict = {"label": label, "note": note, "timeStamp": str(datetime.datetime.now())}
            notes.append(tmpDict)
            json.dump(notes, fw)
        encryptFile(path, key)
        return notes
    except:
        try:
            encryptFile(path, key)
        except:
            pass
        return 0
    
def seeNoteBylabel(user, key, label: list):
    path = getUserFiles(user, True, False)[0]
    try:
        decryptFile(path, key)
    except:
        pass
    try:
        with open(path, 'r') as fr:
            tmp = fr.read().strip('=')
            notes = json.loads(tmp)
            chosenNotes = []
            for note in notes:
                if note["label"] in label:
                    chosenNotes.append(note)
            encryptFile(path, key)
            return chosenNotes
    except:
        try:
            encryptFile(path, key)
        except:
            pass
        return 0
    
def showNote(note, timeStamp = True):
    label = note["label"]
    context = note["note"]
    print("_ ", end='')
    if label != None:
        print(label)
    for i in range(len(context)):
        if i == len(context) - 1:
            print(context[i], end='')
            break
        print(context[i])
    if timeStamp:
        time = note["timeStamp"]
        print(time)
    else:
        print()

# deleted note: success / 0: failure
def _deleteNote(notes, idx):
    while idx < len(notes) - 1:
        notes[idx] = notes[idx + 1]
        idx += 1
    deletedNote = notes.pop(idx)
    path = getUserFiles(user, True, False)[0]
    try:
        decryptFile(path, key)
    except:
        if not os.path.isdir(user.capitalize()):
            os.mkdir(user.capitalize())
        f = open(path, 'w')
        f.close()
    try:
        with open(path, 'w') as fw:
            json.dump(notes, fw)
        encryptFile(path, key)
        return deletedNote
    except:
        try:
            encryptFile(path, key)
        except:
            pass
        return 0

# 1: success / 0: failure
def _changeNote(user, key, notes, idx, note):
    prvNote = _deleteNote(notes, idx)
    anErr = _addNote(user, key, notes, note, prvNote["label"])
    try:
        if anErr == 0:
            return 0
        else:
            return 1
    except:
        return 1

def _addlabel(user, key, notes, idx, note, label):
    _deleteNote(notes, idx)
    anErr = _addNote(user, key, notes, note, label)
    try:
        if anErr == 0:
            return 0
    except:
        return 1

# list/string of labels: there is a label file / False: there isn'n a label file
def xtrctLable(u, key, list = True):
    tmp = getUserFiles(u, False, True)[1]

    exits = os.path.isfile(tmp)
    if exits:
        decryptFile(tmp, key)
        f = open(tmp, 'r')
        if list:
            lines = f.readlines()
            lineL = []
            for line in lines:
                lineL.append(line[:len(line) - 2])
            lines = lineL
        else:
            lines = f.read()
        f.close()
        encryptFile(tmp, key)
        return lineL
    return False

# [total line count, string of content]
def xtrctNote(noteList):
    lineCtr = 0
    sNotes = ''
    for i in range(len(noteList)):
        tmp = str(i) + ': '
        if noteList[i]["label"]:
            tmp += '(' + noteList[i]['label'] + ') '
        lineCount = len(noteList[i]["note"])
        lineCtr += lineCount
        for ln in range(lineCount):
            if ln == lineCount - 1:
                tmp += noteList[i]["note"][ln]
                break
            tmp += noteList[i]["note"][ln] + '\n'
        tmp += ' (' + noteList[i]["timeStamp"] + ')\n'
        sNotes += tmp
    return [lineCtr, sNotes]

def addlabelToFile(u, key, label):
    # tmp = u + "labels.txt"
    tmp = getUserFiles(u, False, True)[1]
    exits = os.path.isfile(tmp)
    if not exits:
        if not os.path.isdir(u.capitalize()):
            os.mkdir(u.capitalize())
        f = open(getUserFiles(u, False, True)[1], 'w')
        encryptFile(tmp, key)
        f.close()
    try:
        decryptFile(tmp, key)
        with open(tmp, 'rt') as fr:
            lExits = False
            lines = fr.readlines()
            for line in lines:
                if line == label + '\n':
                    lExits = True      
            if not lExits:
                with open(tmp, 'w') as fw:
                    for l in lines:
                        fw.write(l)
                    fw.write(label + '\n')
        encryptFile(tmp, key)
    except:
        print("addlabel ERROR!")
        return -1
        
    return 0

# -1: no such file / 0: no such string / 1: string found
def strIsInFile(fileName, key, string):
    try:
        decryptFile(fileName, key)
        with open(fileName, 'r') as fr:
            lines = fr.readlines()
            for line in lines:
                r = line.find(string)
                if r != -1:
                    encryptFile(fileName, key)
                    return 1
        encryptFile(fileName, key)
        return 0
    except FileNotFoundError:
        try:
            encryptFile(fileName, key)
        except:
            pass
        return -1

def sumNotes(noteList, nChar = 10, padd = '...'):
    lSmdNotes = []
    for i in range(len(noteList)):
        chrCnt = 0
        tmp = str(i) + ': '
        if noteList[i]["label"]:
            tmp += '(' + noteList[i]['label'] + ') '
        lineCount = len(noteList[i]["note"])
        for ln in range(lineCount):
            tmpCnt = chrCnt + len(noteList[i]["note"][ln])
            if tmpCnt >= nChar:
                tmp += noteList[i]["note"][ln][:nChar - chrCnt]
                break
            else:
                chrCnt = tmpCnt
            tmp += noteList[i]["note"][ln] + ' '
        tmp += padd + ' (' + noteList[i]["timeStamp"] + ')'
        lSmdNotes.append(tmp)
    return lSmdNotes
    
def viewHandle():
    notes = readNotes(user, key)
    if len(notes) == 0:
        print("no notes yet...")
    else:
        llabels = xtrctLable(user, key)
        if not llabels:
            print("no labels yet...")
        else:
            print("labels: ")
            print(llabels)

        which = input("wich notes(label name / all): ")
        if which == 'all':
            print(xtrctNote(notes)[1])
        else:
            chosenNotes = seeNoteBylabel(user, key, [which])
            if len(chosenNotes) == 0:
                print("no note with such label...")
            else:
                print(xtrctNote(chosenNotes)[1])

def addHandle():
    tmp = input("add thy note: ")
    n = []
    n.append(tmp)
    while True:
        tmp = input()
        if tmp == '':
            break
        n.append(tmp)
    _addNote(user, key, notes, n)
    lab = input("label(press enter if no labels): ")
    if len(lab) == 0:
        lab = None
    else:
        addlabelToFile(user, key, lab)
        _addlabel(user, key, notes, len(notes) - 1, notes[len(notes) - 1]["note"], lab)

def deleteHandle():
    print(xtrctNote(notes)[1])
    sn = sumNotes(notes)
    sn.append("quit")
    ln = inquirer.list_input("Notes:", choices=sn)
    if ln == "quit":
        return 0
    dnErr = _deleteNote(notes, sn.index(ln))
    if dnErr == 0:
        print("...note was not deleted")
    else:
        print("note deleted...")

def changeHandle():
    print(xtrctNote(notes)[1])
    sn = sumNotes(notes)
    sn.append("quit")
    ln = inquirer.list_input("Notes:", choices=sn)
    if ln == "quit":
        return 0

    # while True:
    #     try:
    #         nNum = int(input("which note do you wanna change? "))
    #         break
    #     except:
    #         print("...ENTER A NUMBER!")

    tmp = input("new note: ")
    note = []
    note.append(tmp)
    while True:
        tmp = input()
        if tmp == '':
            break
        note.append(tmp)
    
    cnErr = _changeNote(user, key, notes, sn.index(ln), note)
    if not cnErr:
        print("...couldn't change note")
    else:
        print("note changed...")

def labelHandle():
    labels = xtrctLable(user, key)
    label = 0
    if labels:
        labels.append("new label")
        labels.append("quit")
        label = inquirer.list_input("Labels:", choices=labels)
        if label == "quit":
            return 0
    else:
        print("No labels yet...")
        
    choic = ['yes', 'no', 'quit']
    if label == 0 or label == "new label":
        label = input("label name: ")
        isl = inquirer.list_input("Wanna also add it to a note?", choices=choic)
    else:
        isl = choic[0]
    lNumL = []
    if isl == choic[0]:
        for sn in sumNotes(notes):
            print(sn)

        while True:
            tmp = input("note number(q to exit): ")
            if tmp.lower() == 'q':
                isIn = False
                break   
            lNumL.append(int(tmp))
        for ln in lNumL:
            addlabelToFile(user, key, label)
            _addlabel(user, key, notes, ln, notes[ln]["note"], label)
    elif isl == choic[1]:
        if strIsInFile(getUserFiles(user, False, True)[1], key, label) > 0:
            print("already exists...")
        addlabelToFile(user, key, label)
        print("new label created...")
    elif isl == choic[2]:
        pass  

def optionHandle(opt, options):
    if opt == options[5]:
        return 0
    if opt == options[0]:
        viewHandle()

    if opt == options[3]:
        addHandle()

    if opt == options[2]:
        deleteHandle()
        
    if opt == options[1]:
        changeHandle()
            
    if opt == options[4]:
        labelHandle()

ls = input("login(l)/signUp(s): ")
F = True
user = ''
pas = ''

while F:
    if ls.lower() == 's':
        user = input("username: ")
        pas = getpass("password: ")
        key = signUp(user, pas)
        F = False
    elif ls.lower() == 'l':
        user = input("username: ")
        pas = getpass("password: ")
        key = login(user, pas)
        if type(key) == bytes:
            notes = readNotes(user, key)
            F = False
        else:
            print("...username/passwrod was wrong")
    else:
        ls = input("login(l)/signUp(s): ")

options = ["view", "change a note", "delete a note", "add a note", "add label", "quite"]
opt = 0
F = True
flags = [None, "options", "less", "view", "del", "add", "ch", "lb", "q", "clear"]
flag = flags[0]
while F:
    flag = flags[0]

    cmd = input("$ ")
    if cmd == "options" or cmd == "opts":
        flag = flags[1]
    elif cmd == "less":
        flag = flags[2]
    elif cmd == "view":
        flag = flags[3]
    elif cmd == "del":
        flag = flags[4]
    elif cmd == "add":
        flag = flags[5]
    elif cmd == "ch":
        flag = flags[6]
    elif cmd == "lb":
        flag = flags[7]
    elif cmd == "q":
        flag = flags[8]
    elif cmd == "clear":
        flag = flags[9]

    if flag == flags[2]:
        curses.wrapper(less)
    elif flag == flags[1]:    
        opt = inquirer.list_input("Options:", choices=options)

        if optionHandle(opt, options) == 0:

            break
    elif flag == flags[3]:
        viewHandle()
    elif flag == flags[4]:
        deleteHandle()
    elif flag == flags[5]:
        addHandle()
    elif flag == flags[6]:
        changeHandle()
    elif flag == flags[7]:
        labelHandle()
    elif flag == flags[8]:
        break
    elif flag == flags[9]:
        clear()
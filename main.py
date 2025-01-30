import os
import datetime
from cryptography.fernet import Fernet
import json
from getpass import getpass
import curses
import subprocess
import questionary

PROFILE = "profile.txt"
isNote = True
SUMMCOUNT = 10
SUMMPADD = '.'

# 0: success / -1: failure
def setConfig(user, key):
    path = getUserFiles(user, False, False, True)[2]
    try:
        decryptFile(path, key)
    except:
        if not os.path.isdir(user.capitalize()):
            os.mkdir(user.capitalize())
        f = open(path, 'w')
        f.close()
    
    try:
        with open(path, 'w') as fw:
            fw.write(str(SUMMCOUNT) + '\n')
            fw.write(SUMMPADD)
        encryptFile(path, key)
        return 0
    except:
        return -1

# -2: no such file or bad encryption / -1: failed to read the file / 0: success
def getConfig(user, key):
    path = getUserFiles(user, False, False, True)[2]
    try:
        # encryptFile(path, key)
        decryptFile(path, key)
    except:
        return -2
    try:
        with open(path, 'r') as fr:
            count = fr.readline()
            padd = fr.readline()
        encryptFile(path, key)
        return [count, padd]
    except:
        return -1

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
    if isNote:
        lineCtr, tmp = xtrctNote(notes)
    else:
        tmp = xtrctLable(user, key, False)
        if type(tmp) == str:
            lineCtr = tmp.count('\n')
        else:
            tmp = ''
            lineCtr = 0
        
    pad.addstr(tmp)
    pad.refresh(0, 0, 0, 0, curses.LINES - 1 - hBars, curses.COLS - 1)
    line = 0
    stdscr.nodelay(True)
    while True:
        try:
            keyStrk = stdscr.getkey()
        except:
            keyStrk = None

        if keyStrk == 's':
            if line + 1 < lineCtr:
                line += 1
        elif keyStrk == 'w':
            if line > 0:
                line -= 1
        elif keyStrk == "q":
            break
        elif keyStrk == 'n':
            if line + curses.LINES <= lineCtr:
                line += curses.LINES - hBars
        elif keyStrk == 'p':
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

def getUserFiles(u, notes: bool, label: bool, config: bool):
    tmpN = ''
    tmpL = ''
    tmpC = ''
    if notes:
        tmpN = u.capitalize() + '/' + u + '.txt'
    if label:
        tmpL = u.capitalize() + '/' + u + 'label.txt'
    if config:
        tmpC += u.capitalize() + '/' + u + 'config.txt'
    return [tmpN, tmpL, tmpC]

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

def logout():
    u = ''
    p = ''
    notes = []
    key = ''
    return [u, p, key, notes]

# notes: success / empty list: failure
def readNotes(user, key):
    path = getUserFiles(user, True, False, False)[0]
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
    path = getUserFiles(user, True, False, False)[0]
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
    path = getUserFiles(user, True, False, False)[0]
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
        return []
    
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
    deletedNote = notes.pop(idx)
    path = getUserFiles(user, True, False, False)[0]
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
    
# deleted label: success / 0: failure
def _deleteLabel(labels, idx):
    deletedLabel = labels.pop(idx)
    path = getUserFiles(user, False, True, False)[1]
    try:
        decryptFile(path, key)
    except:
        if not os.path.isdir(user.capitalize()):
            os.mkdir(user.capitalize())
        f = open(path, 'w')
        f.close
    try:
        with open(path, 'w') as fw:
            for label in labels:
                fw.write(label + '\n')
        encryptFile(path, key)
        return deletedLabel
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

# list/string of labels: there is a label file / 0: there isn'n a label file
# -1: the label file is empty
def xtrctLable(u, key, list = True):
    tmp = getUserFiles(u, False, True, False)[1]

    exits = os.path.isfile(tmp)
    if exits:
        try:
            decryptFile(tmp, key)
            f = open(tmp, 'r')
            if list:
                lines = f.readlines()
                lineL = []
                for line in lines:
                    lineL.append(line[:len(line) - 1])
                lines = lineL
            else:
                lines = f.read()
            f.close()
            encryptFile(tmp, key)
            return lines
        except:
            try:
                encryptFile(tmp, key)
            except:
                pass
            return -1
    return 0

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
    tmp = getUserFiles(u, False, True, False)[1]
    exits = os.path.isfile(tmp)
    if not exits:
        if not os.path.isdir(u.capitalize()):
            os.mkdir(u.capitalize())
        f = open(getUserFiles(u, False, True, False)[1], 'w')
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
        
    return lExits

# -1: no such file / 0: no such string / 1: string found
def strIsInFile(fileName, key, string):
    try:
        if key:
            decryptFile(fileName, key)
        with open(fileName, 'r') as fr:
            lines = fr.readlines()
            for line in lines:
                r = line.find(string)
                if r != -1:
                    if key:
                        encryptFile(fileName, key)
                    return 1
        if key:
            encryptFile(fileName, key)
        return 0
    except FileNotFoundError:
        try:
            if key:
                encryptFile(fileName, key)
        except:
            pass
        return -1

def sumNotes(noteList, nChar, padd, withnum = True):
    lSmdNotes = []
    for i in range(len(noteList)):
        chrCnt = 0
        if withnum:
            tmp = str(i) + ': '
        else:
            tmp = ''
        if noteList[i]["label"]:
            tmp += '(' + noteList[i]['label'] + ') '
        lineCount = len(noteList[i]["note"])
        for ln in range(lineCount):
            tmpCnt = chrCnt + len(noteList[i]["note"][ln])
            if tmpCnt >= nChar:
                if ln == lineCount - 1:
                    tmp += noteList[i]["note"][ln][:nChar - chrCnt]
                else:
                    tmp += noteList[i]["note"][ln][:nChar - chrCnt] + ' '
                break
            else:
                chrCnt = tmpCnt
            if ln == lineCount - 1:
                tmp += noteList[i]["note"][ln][:nChar - chrCnt]
            else:
                tmp += noteList[i]["note"][ln][:nChar - chrCnt] + ' '
        tmp += padd*3 + ' (' + noteList[i]["timeStamp"] + ')'
        lSmdNotes.append(tmp)
    return lSmdNotes
    
def viewHandle():
    notes = readNotes(user, key)
    if len(notes) == 0:
        print("no notes yet...")
    else:
        llabels = xtrctLable(user, key)
        if type(llabels) != list or len(llabels) == 0:
            print("no labels yet...")
            choices = ["all", "summarize", "quit"]
        else:
            print("labels: ")
            print(llabels)
            choices = ["by label", "all", "summarize", "quit"]

        ans = questionary.select("how: ", choices=choices).ask()
        # which = input("wich notes(label name / all): ")
        if ans == "quit":
            return 0
        if ans == "all":
            print(xtrctNote(notes)[1])
        elif ans == "summarize":
            sn = sumNotes(notes, SUMMCOUNT, SUMMPADD)
            for n in sn:
                print(n)
        elif ans == "by label":
            which = questionary.checkbox("which labels? ", choices=llabels).ask()
            chosenNotes = seeNoteBylabel(user, key, which)
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
    lLabels = xtrctLable(user, key)
    if lLabels == 0:
        print("no labels yet...")
        lab = questionary.select("wanna add label?", choices=["no labels", "new label"]).ask()
    else:
        lLabels.append("new label")
        lLabels.append("no labels")
        lab = questionary.select("wanna add label? ", choices=lLabels).ask()
    # lab = input("label(press enter if no labels): ")
    if lab == "no labels":
        lab = None
    elif lab == "new label":
        lab = input("new lable: ")
        le = addlabelToFile(user, key, lab)
        _addlabel(user, key, notes, len(notes) - 1, notes[len(notes) - 1]["note"], lab)
        if le:
            print("label already exists...")
    else:
        addlabelToFile(user, key, lab)
        _addlabel(user, key, notes, len(notes) - 1, notes[len(notes) - 1]["note"], lab)
        

def deleteHandle(label = False):
    if not label:
        sn = sumNotes(notes, SUMMCOUNT, SUMMPADD, withnum=False)
        if len(sn) == 0:
            print("no notes yet...")
            return 0
        ln = questionary.checkbox("Notes: ", choices=sn).ask()
        ans = questionary.select("are you sure? ", choices=["yes", "no"]).ask()
        if ans == "yes":
            for e in ln:
                dnErr = _deleteNote(notes, sn.index(e))
                if dnErr == 0:
                    print("...note was not deleted")
                else:
                    print("note deleted...")
                sn = sumNotes(notes, SUMMCOUNT, SUMMPADD, withnum=False)
        else:
            print("aborted...")
            pass
    else:
        lLabels = xtrctLable(user, key, True)
        if type(lLabels) == list:
            ln = questionary.checkbox("Labels: ", choices=lLabels).ask()
            effectedNotes = seeNoteBylabel(user, key, ln)
            if len(effectedNotes) != 0:
                ans = questionary.select("some notes have some of these labels. " + \
                                        "are you sure you want to delete it? ",\
                                            choices=["yes", "no"]).ask()
            else:
                ans = questionary.select("are you sure? ", choices=["yes", "no"]).ask()

            if ans == "yes":
                wd = True
            else:
                wd = False
            for i in range(len(notes)):
                for l in ln:
                    if type(notes[i]['label']) == str: 
                        if l in notes[i]['label']:
                            notes[i]['label'] = None
                            _changeNote(user, key, notes, i, notes[i]['note'])
            if wd:
                for e in ln:
                    dlErr = _deleteLabel(lLabels, lLabels.index(e))
                    if dlErr == 0:
                        print("...label was not deleted")
                    else:
                        print("label deleted...")
                    lLabels = xtrctLable(user, key, True)
        else:
            print("no labels yet...")
def changeHandle():
    sn = sumNotes(notes, SUMMCOUNT, SUMMPADD)
    if len(sn) == 0:
        print("no notes yet...")
        return 0
    print(xtrctNote(notes)[1])
    sn.append("quit")
    ln = questionary.select("Notes:", choices=sn).ask()
    if ln == "quit":
        print("aborted...")
        return 0

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
    labels = xtrctLable(user, key, True)
    label = 0
    if type(labels) == list:
        labels.append("new label")
        labels.append("quit")
    else:
        print("No labels yet...")
        labels = []
        labels.append("new label")
        labels.append("quit")

    label = questionary.select("Labels:", choices=labels).ask()
    if label == "quit":
        return 0
        
    choic = ['yes', 'no', 'quit']
    if label == 0 or label == "new label":
        label = input("label name: ")
        isl = questionary.select("Wanna also add it to a note?", choices=choic).ask()
    else:
        isl = choic[0]

    lNumL = []
    if isl == choic[0]:
        if len(notes) > 0:
            sn = sumNotes(notes, SUMMCOUNT, SUMMPADD, withnum=False)
            chosenNotes = questionary.checkbox("which notes? ", choices=sn).ask()
            for note in chosenNotes:
                lNumL.append(sn.index(note))
                addlabelToFile(user, key, label)
                _addlabel(user, key, notes, sn.index(note), notes[sn.index(note)]["note"], label)
                sn = sumNotes(notes, SUMMCOUNT, SUMMPADD, withnum=False)
        else:
            print("...no notes yet")
            
    elif isl == choic[1]:
        if strIsInFile(getUserFiles(user, False, True, False)[1], key, label) > 0:
            print("already exists...")
        addlabelToFile(user, key, label)
        print("new label created...")
    elif isl == choic[2]:
        print("aborted...")
        return 0

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

def signHandle():
    while True:
        ls = input("login(l)/signUp(s)/quit(q): ")
        if ls.lower() == 's':
            user = input("username: ")
            pas = getpass("password: ")
            if strIsInFile(PROFILE, None, user) == 1:
                print("...user already exits")
                continue
            key = signUp(user, pas)
            setConfig(user, key)
            notes = []
            return [user, pas, key, notes]
        elif ls.lower() == 'l':
            user = input("username: ")
            pas = getpass("password: ")
            key = login(user, pas)
            if type(key) == bytes:
                configs = getConfig(user, key)
                if type(configs) == list:
                    global SUMMCOUNT
                    global SUMMPADD
                    SUMMCOUNT, SUMMPADD = configs
                    SUMMCOUNT = int(SUMMCOUNT)
                                    
                notes = readNotes(user, key)
                return [user, pas, key, notes]
            else:
                print("...username/passwrod was wrong")
        elif ls.lower() == 'q':
            return [0, 0, 0, 0]
        # else:
        #     ls = input("login(l)/signUp(s): ")

user, pas, key, notes = signHandle()

options = ["view", "change a note", "delete a note", "add a note", "add label", "quite"]
opt = 0
F = True
if user == 0 and pas == 0 and key == 0 and notes == 0:
    F = False
flags = [None, "options", "less n", "less l", "view", "del n", "add", "ch", "lb", "q", "clear",\
        "setSummCount", "setSummpadd", "logout", "help", "del l"]
print("logout(logout), option menu(opt, options), less notes(less n), less labels(less l)\n" + \
    "view(view), delete note(del n), delete label(del l), add note(add), add label(lb)\n" + \
    "change(ch), quit(q), clear(clear), set summarization count(setSummCount)\n" + \
    "set summarization padding char(setSummPad), help(?)")
while F:
    
    flag = flags[0]

    cmd = input("$ ")
    if cmd == "options" or cmd == "opt":
        flag = flags[1]
    elif cmd == "less n":
        flag = flags[2]
    elif cmd == "less l":
        flag = flags[3]
    elif cmd == "view":
        flag = flags[4]
    elif cmd == "del n":
        flag = flags[5]
    elif cmd == "add":
        flag = flags[6]
    elif cmd == "ch":
        flag = flags[7]
    elif cmd == "lb":
        flag = flags[8]
    elif cmd == "q":
        flag = flags[9]
    elif cmd == "clear":
        flag = flags[10]
    elif cmd == "setSummCount":
        flag = flags[11]
    elif cmd == "setSummPadd":
        flag = flags[12]
    elif cmd == "logout":
        flag = flags[13]
    elif cmd == "?":
        flag = flags[14]
    elif cmd == "del l":
        flag = flags[15]

    if flag == flags[2]:
        isNote = True
        curses.wrapper(less)
    if flag == flags[3]:
        isNote = False
        curses.wrapper(less)
    elif flag == flags[1]:    
        opt = questionary.select("Options:", choices=options).ask()
        # opt = inquirer.list_input("Options:", choices=options)

        if optionHandle(opt, options) == 0:

            break
    elif flag == flags[4]:
        viewHandle()
    elif flag == flags[5]:
        deleteHandle()
    elif flag == flags[6]:
        addHandle()
    elif flag == flags[7]:
        changeHandle()
    elif flag == flags[8]:
        labelHandle()
    elif flag == flags[9]:
        break
    elif flag == flags[10]:
        clear()
    elif flag == flags[11]:
        try:
            tmp = int(input("new summarize count: "))
            SUMMCOUNT = tmp
            setConfig(user, key)
        except:
            print("...summarize count should be an integer")
    elif flag == flags[12]:
        tmp = input("summarize padding: ")
        if len(tmp) > 1:
            print("...summarize padding can only be one character")
        else:
            SUMMPADD = tmp
            setConfig(user, key)
    elif flag == flags[13]:
        user, pas, key, notes = logout()
        user, pas, key, notes = signHandle()
        if user == 0 and pas == 0 and key == 0 and notes == 0:
            break
    elif flag == flags[14]:
        print("logout(logout), option menu(opt, options), less notes(less n), less labels(less l)\n" + \
    "view(view), delete(del), add note(add), add label(lb), change(ch), quit(q)\n" + \
    "clear(clear), set summarization count(setSummCount), set summarization padding char(setSummPad)\n" + \
    "help(?)")
    elif flag == flags[15]:
        deleteHandle(True)
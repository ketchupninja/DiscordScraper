class Message:
    """stores info about a motd line"""
    def __init__(self, author, body):
        self.author = author
        self.body = body

msgStartList = [False]
#Initalize with one False boolean, will fill out in decideMsgStartList
#Assigns a boolean to every line of text

def promptLogname():
    "Prompt the user to input the name of the file to get the chatlog from."
    chatlogFilename = input("Please name chatlog filename >")
    chatlogFilename = chatlogFilename + ".txt"
    try:
        f = open(chatlogFilename)
        f.close()
    except IOError:
        print('Not a valid file. Leave off \".txt\".')
        promptLogname()

    return chatlogFilename
    
def isMsgStart(lineArray, index):
    """Check if a single line is a valid message starting line."""
    if (lineArray[index - 1] != "") or (index >= len(lineArray)):
        return False
    line = lineArray[index]
    if len(line) >= 19:
        if puncGood(line) and numbGood(line) and lettGood(line) and usidGood(line):
            return True;     
    return False 
    
def puncGood(line):
    """Checks to see if punctuation characters & whitespaces are conistent with
a message start line."""
    if line[0] == '[' and line[3] == '-' and line[7] == '-' and line[10] == ' ':
        if line[13] == ':' and line[16] == ' ' and line[19] == ']':
            return True
        
def numbGood(line):
    """Checks to see if the right characters are numerals in a message for it
to be a message start line, excluding user ID."""
    charsToCheck = [line[1], line[2], line[8], line[9], line[11], line[12],
                    line[14], line[15]]
    for char in charsToCheck:
        if not char.isdigit():
            #If any of these characters aren't digits
            return False
    #if all of checked chars are digits    
    return True

def lettGood(line):
    """Checks to see if the right characters are letters."""
    charsToCheck = [line[4], line[5], line[6], line[17], line[18]]
    for char in charsToCheck:
        if not char.isalpha():
            return False
    #Else if all characters are alphabetical letters
    return True

def usidGood(line):
    """Checks if the userID at the end of the string is formatted validly."""
    length = len(line)
    lastFourChars = [line[length -1], line[length -2], line[length - 3], line[length -4]]
    for char in lastFourChars:
        if not char.isdigit():
            return False
    
    fifthLast = line[length - 5]
    if not fifthLast == '#':
        return False
    
    return True
            
def setUpMessageArray(lineArray):
    """Creates an array of Message objects corresponding to messages sent
by users"""
        
    messageArray = []
    #Go through lineArray
    #if that is a msg start: make a new msg, grab author
    #body will be all lines until next msg start
    for index in range(len(lineArray)):
        if isMsgStart(lineArray, index):
            #A msg starts here
            thisLine = lineArray[index]
            #print(thisLine)
            author = thisLine[21:-5]
            #Message body will be all the lines until next msg start
            #Start on the next line:
            body = lineArray[index + 1]
            newMsg = Message(author, body)
            messageArray.append(newMsg)
            
    return messageArray

def askForScanStartsWith():
    """Allow user to specify only writing msgs to file if they start with given string"""
    print("If you would like to only record messages that")
    print("begin with a certain string, please enter that string now.")
    print("To write all messages, enter an empty line.")
    startingString = input(">")
    return startingString
                   
def askSave():
    """Ask user if they want to enable !save command"""
    resp = input("Enable !save? (y/n) >")
    if resp == "y":
        return True
    else:
        return False
    
def askAuthorCheck():
    resp = input("Output by author? (y/n) >")
    if resp == "y":
        return True
    else:
        return False
    
def askAuthorName():
    resp = input("What author name to output? >")
    return resp

#Main

scanForStart = False
authorCheck = False;
name = "N/A"
                           
chatlogFilename = promptLogname()
outputFilename = input("Please choose output filename >")

saveEnabled = askSave()
if not saveEnabled:
    startString = askForScanStartsWith()
    if startString != "":
        scanForStart = True
    else:
        authorCheck = askAuthorCheck()
        if (authorCheck):
            name = askAuthorName()
    

f = open(chatlogFilename, "r", encoding="utf8")
if f.mode == 'r':
    contents = f.read()
    #Reconstruct the contents character by character to strip out characters
    #outside range of Tcl
    char_list_master = [contents[j] for j in range(len(contents))
                        if ord(contents[j]) in range(65536)]
    parsedContents = ''
    for j in char_list_master:
        parsedContents = parsedContents + j
    contents = parsedContents
    
    content_lines = contents.splitlines()
    messages = setUpMessageArray(content_lines)
    #List of message objects

            
    c = open(outputFilename, "w+", encoding="utf8")
    
    #array to be used when save command enabled
    savedMessages = []
    
    for i in range(len(messages)):
        currentMsg = messages[i]
        curBody = currentMsg.body
        
        #If doing !save behavior
        if saveEnabled:
            if curBody.startswith("!save"):
                saver = currentMsg.author
                #get number of lines to save
                saveQuantity = [int(i) for i in curBody.split() if i.isdigit()]
                for j in range (0, saveQuantity[0]):
                    msgToSave = messages[i - (saveQuantity[0] - j)]
                    savedMessages.append(msgToSave)
                    outputString = msgToSave.author + "|" + msgToSave.body + " [[Saved by " + saver + "]]" + "\n"
                    c.write(outputString)
        
        #As long as we're not doing scanForStart
        elif not scanForStart:
            if authorCheck:
                if(currentMsg.author == name):
                    #FOR OPENAI PROCESSING
                    outputString = currentMsg.body + "\n"
                    if not outputString.startswith("https"):   
                        c.write(outputString)
                
            if not authorCheck:
                #Normal
                outputString = currentMsg.body + "\n"
                if not outputString.startswith("https"):
                    c.write(outputString)
            
        #If we are doing scanForStart
        else:
            #Start scan
            if currentMsg.body.startswith(startString):
                outputString = currentMsg.author + "|" + currentMsg.body + "\n"
                #print(outputString)
                c.write(outputString)
                           
    f.close()
    c.close()
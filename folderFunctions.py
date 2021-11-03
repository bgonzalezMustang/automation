# import time module, Observer, FileSystemEventHandler
import os
import winshell
import pythoncom
from pathlib import Path
import shutil
import time

# refData.py contains all of our desired reference data
from refData import *

#iterateS through all files in a folder, creates text file with number of files called "!LOG_FILE-"
def createLog(cadFiles):
    fileCount = 1

    for folder in os.walk(cadFiles['folderPath']):
        if folder[0] == cadFiles['folderPath']:
            for item in folder[2]:
                if "!LOG_FILE" in item:
                    os.remove(cadFiles['folderPath']+ "/" + item)
                else:
                    fileCount +=  1
            return fileCount
    Path(cadFiles['folderPath']+ "/!LOG_FILE-" + str(fileCount) + ".txt").touch()
    return None

#modified by bgon
#function for verifying that the number of files in a folder is equal to the number of files declared by the log file
#returns as a boolean, true when there is a log file in the folder and the number of files in the folder is equal to the log count
def verifyLog(folderPath):
    logCount = 0
    fileCount = 0
    for folder in os.walk(folderPath):
        if folder[0] == folderPath:
            for item in folder[2]:
                fileCount += 1
                if "!LOG_FILE" in item:
                    # !LOG_FILE-4.txt -> 4.txt -> 4
                   logCount = int(item.split("-")[1].split(".")[0])
    return (logCount > 0 and logCount == fileCount)

#modified by bgon
def checkLog(folderPath):
    currentWait=0
    maxWait=300
    isLog = False
    while isLog != True and currentWait<maxWait:
        time.delay(5)
        currentWait+=5
        isLog=verifyLog(folderPath)
    return isLog

#modified by bgon
# Given a folder, identify the non-OLD cad pdf (should be the only pdf that contains BRK and does not contain OLD)
# From the pdf name, identify the builder
def identifyCAD(folderPath):
    for folder in os.walk(folderPath):
        if folder[0] == folderPath:
            for item in folder[2]:
                pdfMatch = pdfBrickRegex.match(item)
                if pdfMatch:
                    pdfName = pdfMatch.group(1)
                    for suffix in suffixList:
                        pdfNameOld = pdfName
                        pdfName = pdfName.removesuffix(suffix)
                        if pdfName != pdfNameOld:
                            shutil.move(folder[0]+'/'+pdfNameOld+'.pdf',folder[0]+'/'+pdfName+'.pdf')
                    builder = builderRegex.match(item).group(1).strip()
                    return pdfName, builder
    return None, None

# Count the number of pdfs that start with "OLD" and contain "BRK", then copy the
def createOldCopy(cadFiles):
    count = 1
    for folder in os.walk(cadFiles['folderPath']):
        if folder[0] == cadFiles['folderPath']:
            for item in folder[2]:
                pdfMatch = oldPdfBrickRegex.match(item)
                if pdfMatch:
                    count += 1
    shutil.copy(cadFiles['folderPath']+'/'+cadFiles['pdfName']+'.pdf', cadFiles['folderPath']+'/OLD'+str(count)+'-'+cadFiles['pdfName']+'.pdf')

def parsePDF(folderPath, pdfName):
    return False

#modified by bgon
def checkScript(cadFiles):
    if checkLog(cadFiles['folderPath']):
        passTest = parsePDF(cadFiles['folderPath'], cadFiles['pdfName'])
        # If pass, move to Ready For Check
        if passTest:
            shutil.move(cadFiles['folderPath'],readyToCheckPath+'/DRAWN BY '+cadFiles['author']+'/'+cadFiles['folderName'])
        # Else, kick back to In Progress
        else:
            shutil.move(cadFiles['folderPath'],cadInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName'])
    else:
        Path(cadFiles['folderPath']+"/!SYNCING_ERROR.txt").touch()
    return None

#modified by bgon
def moveToFinished(cadFiles):
    # If builder on list, move to FINISHED FROM CAD in the respective builder file
    if checkLog(cadFiles['folderPath']):
        if (cadFiles['builder'] in builderPaths.keys()):
            shutil.move(cadFiles['folderPath'],publicDownloadsPath+'/'+cadFiles['folderName'])
            shutil.move(publicDownloadsPath+'/'+cadFiles['folderName'],finishedFromCADPath+'/'+builderPaths[cadFiles['builder']]['FFC']+'/'+cadFiles['folderName'])
        # If builder not on list (likely PEBKAC), move back to NEEDS CORRECTIONS w/ note
        else:
            shutil.move(cadFiles['folderPath'],checkInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName'])
            Path(checkInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName']+'/'+'ERROR - BUILDER NAME NOT FOUND.txt').touch()
    else:
        Path(cadFiles['folderPath']+"/!SYNCING_ERROR.txt").touch()
    return None


#modified by bgon
def moveToInProgress(cadFiles):
    #Evaluating whether or not the number of files is correct and there is a log file before it is moved
    if checkLog(cadFiles['folderPath']):   
        shutil.move(cadFiles['folderPath'],cadInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName'])
    else:
        Path(cadFiles['folderPath']+"/!SYNCING_ERROR.txt").touch()
    return None

# searches builder directory for dwg with same name as pdf
def createShortcut(cadFiles):
    # Ends if a shortcut already exists
    for folder in os.walk(cadFiles['folderPath']):
        if folder[0] == cadFiles['folderPath']:
            for item in folder[2]:
                if item.endswith('.lnk'):
                    return None
    # Sets target to none, then searches the builder path for a DWG with the PDF's name
    target = None
    if not(cadFiles['builder'] is None):
        for folder in os.walk(cadDWGsPath + '/' + builderPaths[cadFiles['builder']]['DWG']):
            if target != None:
                break
            for item in folder[2]:
                if item != None and cadFiles['pdfName'] in item and '.dwg' in item:
                    target = folder[0] + '/' + item
                    break
    # If a target is found, make a shortcut
    if target != None:
        pythoncom.CoInitialize()
        with winshell.shortcut(cadFiles['folderPath']+'/!SHORTCUT-'+cadFiles['pdfName']+'.lnk') as link:
            link.path = target
        pythoncom.CoUninitialize()
    # if not, make a text file with an error
    else:
        Path(cadFiles['folderPath']+'/!issue finding dwg file.txt').touch()
    return None
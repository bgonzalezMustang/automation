# import time module, Observer, FileSystemEventHandler
import os
import winshell
import pythoncom
from pathlib import Path
import shutil
import time

# refData.py contains all of our desired reference data
from refData import *
from checkPDF import *

# Given a folder, identify the non-OLD cad pdf (should be the only pdf that contains BRK and does not contain OLD)
# From the pdf name, identify the builder
def identifyCAD(folderPath):
    try:
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
                        builder = None
                        builderMatch = builderRegex.match(item)
                        if builderMatch:
                            builder = builderMatch.group(1).strip()
                        return pdfName, builder
    except:
        print("identifyCAD()")
    return None, None

# Count the number of pdfs that start with "OLD" and contain "BRK", then copy the
def createOldCopy(cadFiles):
    try:
        count = 1
        for folder in os.walk(cadFiles['folderPath']):
            if folder[0] == cadFiles['folderPath']:
                for item in folder[2]:
                    pdfMatch = oldPdfBrickRegex.match(item)
                    if pdfMatch:
                        count += 1
        shutil.copy(cadFiles['folderPath']+'/'+cadFiles['pdfName']+'.pdf', cadFiles['folderPath']+'/OLD'+str(count)+'-'+cadFiles['pdfName']+'.pdf')
    except:
        print("createOldCopy() issue")


def checkScript(cadFiles):
    pdfChecker = PDFChecker()
    passTest = pdfChecker.checkPDF(cadFiles['folderPath'] + '/' + cadFiles['pdfName'] + '.pdf')
    print(passTest)
    # If pass, move to Ready For Check
    if passTest:
        shutil.move(cadFiles['folderPath'],readyToCheckPath+'/DRAWN BY '+cadFiles['author'])
        print('moved to '+readyToCheckPath+'/DRAWN BY '+cadFiles['author']+'/'+cadFiles['folderName'] + '\n')
    # Else, kick back to In Progress
    else:
        createShortcut(cadFiles)
        moveToInProgress(cadFiles)
        print('moved to '+cadInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName'] + '\n')
    return None

def moveToFinished(cadFiles):
    # If builder on list, move to FINISHED FROM CAD in the respective builder file
    if cadFiles['builder'] in builderPaths.keys():
        shutil.move(cadFiles['folderPath'],publicDownloadsPath)
        time.sleep(15)
        shutil.move(publicDownloadsPath+'/'+cadFiles['folderName'],finishedFromCADPath+'/'+builderPaths[cadFiles['builder']]['FFC'])
    # If builder not on list (likely PEBKAC), move back to NEEDS CORRECTIONS w/ note
    else:
        shutil.move(cadFiles['folderPath'],checkInProgressPath+'/'+cadFiles['author'])
        Path(checkInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName']+'/'+'!ERROR - BUILDER NAME NOT FOUND.txt').touch()
    return None

def moveToInProgress(cadFiles):
    shutil.move(cadFiles['folderPath'],cadInProgressPath+'/'+cadFiles['author'])
    try:
        pdfChecker = PDFChecker()
        passTest = pdfChecker.checkPDF(cadFiles['folderPath'] + '/' + cadFiles['pdfName'] + '.pdf')
        print(passTest)
        # If pass, move to Ready For Check
        if passTest:
            shutil.move(cadFiles['folderPath'],readyToCheckPath+'/DRAWN BY '+cadFiles['author']+'/'+cadFiles['folderName'])
            print('moved to '+readyToCheckPath+'/DRAWN BY '+cadFiles['author']+'/'+cadFiles['folderName'] + '\n')
        # Else, kick back to In Progress
        else:
            createShortcut(cadFiles)
            shutil.move(cadFiles['folderPath'],cadInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName'])
            print('moved to '+cadInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName'] + '\n')
    except:
        print("checkScript() issue")
    return None

def moveToFinished(cadFiles):
    try:
        # If builder on list, move to FINISHED FROM CAD in the respective builder file
        if cadFiles['builder'] in builderPaths.keys():
            shutil.move(cadFiles['folderPath'],publicDownloadsPath+'/'+cadFiles['folderName'])
            time.sleep(15)
            shutil.move(publicDownloadsPath+'/'+cadFiles['folderName'],finishedFromCADPath+'/'+builderPaths[cadFiles['builder']]['FFC']+'/'+cadFiles['folderName'])
        # If builder not on list (likely PEBKAC), move back to NEEDS CORRECTIONS w/ note
        else:
            shutil.move(cadFiles['folderPath'],checkInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName'])
            Path(checkInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName']+'/'+'!ERROR - BUILDER NAME NOT FOUND.txt').touch()
    except:
        print("moveToFinished() issue")
    return None

def moveToInProgress(cadFiles):
    try:
        shutil.move(cadFiles['folderPath'],cadInProgressPath+'/'+cadFiles['author']+'/'+cadFiles['folderName'])
    except:
        print("moveToInProgress() issue")
    return None

# searches builder directory for dwg with same name as pdf
def createShortcut(cadFiles):
    try:
        # Ends if a shortcut already exists
        for folder in os.walk(cadFiles['folderPath']):
            if folder[0] == cadFiles['folderPath']:
                for item in folder[2]:
                    if item.endswith('.lnk'):
                        return None
        # Sets target to none, then searches the builder path for a DWG with the PDF's name
        target = None
        if cadFiles['builder'] is builderPaths.keys():
            for folder in os.walk(cadDWGsPath + '/' + builderPaths[cadFiles['builder']]['DWG']):
                if target != None:
                    break
                for item in folder[2]:
                    if item != None and cadFiles['pdfName'] in item and '.dwg' in item:
                        target = folder[0] + '/' + item
                        break
        else:
            for folder in os.walk(cadDWGsPath):
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
    except:
        print("createShortcut() issue")
    return None
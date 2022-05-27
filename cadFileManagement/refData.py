#Description:
#Holds some hard coded data referenced in other files, such as dir paths and builder lists.
#References Finished from builder paths fromt the builderInfo.json file included
#References builder correct spellings from builderInfo.json file included


import re
import os
import json

homePath = 'C:' + os.environ['HOMEPATH'].replace('\\','/') + '/'
# publicDownloadsPath = 'C:/Users/Public/Downloads'
# needsCorrectionPath = homePath + 'Mustang Plumbing/CAD Plans - General/CAD - WORKING/! - NEEDS CORRECTION'
# makeShortcutPath = homePath + 'Mustang Plumbing/CAD Plans - General/CAD - WORKING/- SCRIPT FOLDERS/(0) - MAKE SHORTCUT'
# checkScriptPath = homePath + 'Mustang Plumbing/CAD Plans - General/CAD - WORKING/- SCRIPT FOLDERS/(1) - CHECK SCRIPT'
# moveToFinishedPath = homePath + 'Mustang Plumbing/CAD Plans - General/CAD - WORKING/- SCRIPT FOLDERS/(2) - MOVE TO FINISHED'
# moveToRTCPath = homePath + 'Mustang Plumbing/CAD Plans - General/CAD - WORKING/- SCRIPT FOLDERS/(1) - MOVE TO RTC'

# cadInProgressPath = homePath + 'Mustang Plumbing/CAD Plans - General/CAD - WORKING/0 - IN PROGRESS'
# readyToCheckPath = homePath + 'Mustang Plumbing/CAD Plans - General/CAD - WORKING/1 - READY TO CHECK'          #Note: full path will include /DRAWN BY <AUTHOR>, instead of /AUTHOR
# checkInProgressPath = homePath + 'Mustang Plumbing/CAD Plans - General/CAD - WORKING/2 - CHECK IN PROGRESS'
# finishedFromCADPath = homePath + 'Mustang Plumbing/CAD Plans - General/FINISHED FROM CAD'

cadDWGsPath = 'S:/CAD/Plans'

#Load info from the builderInfo.json file to create two dictionaries
with open("S:\\Public\\CAD CODE REFERENCE\\builderInfo.json") as my_json:
    builder_json = json.load(my_json)

builderCorrectSpellings = builder_json["builderCorrectSpellings"]
builderPaths = builder_json["builderPaths"]

#Load info from scriptFolderPaths.json to fill path variables (In json so folder structure can change)
with open("S:\\Public\\CAD CODE REFERENCE\\scriptFolderPaths.json") as my_json:
    path_json = json.load(my_json)

publicDownloadsPath = path_json["publicDownloadsPath"]
needsCorrectionPath = homePath + path_json["needsCorrectionPath"]
makeShortcutPath = homePath + path_json["makeShortcutPath"]
checkScriptPath = homePath + path_json["checkScriptPath"]
moveToFinishedPath = homePath + path_json["moveToFinishedPath"]
moveToRTCPath = homePath + path_json["moveToRTCPath"]

cadInProgressPath = homePath + path_json["cadInProgressPath"]
readyToCheckPath = homePath + path_json["readyToCheckPath"]        #Note: full path will include /DRAWN BY <AUTHOR>, instead of /AUTHOR
checkInProgressPath = homePath + path_json["checkInProgressPath"]
finishedFromCADPath = homePath + path_json["finishedFromCADPath"]


watchedDirectories = [needsCorrectionPath,
                      makeShortcutPath,
                      checkScriptPath,
                      moveToRTCPath,
                      moveToFinishedPath]

pdfBrickRegex = re.compile("^(?!OLD)(.*BRK-.*)\.pdf$")
oldPdfBrickRegex = re.compile("^OLD.*BRK-.*\.pdf$")
builderRegex = re.compile(".*BRK-([^-]*)-")
dwgBrickRegex = re.compile(".*BRK.*\.dwg$")

suffixList = ['-LANDSCAPE',
                '-LEFT',
                '-L',
                '-RIGHT',
                '-R']

builders = ["-" + char for char in builderPaths.keys()]
suffixList.extend(builders)

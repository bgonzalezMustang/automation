#https://mustangplumbingrr.webhook.office.com/webhookb2/480b28ef-9e5f-41ea-a054-69b691add8d5@f1799ac8-2ec2-4176-9072-180ec0e2aeca/IncomingWebhook/a8e96abd9fb64dccafce90bf026b3817/cb9afd51-7b6c-433e-a359-1145dec1b260
#^webhook for notifications bot

import pymsteams
import os
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import math

class MonitorFolder(FileSystemEventHandler):
   def on_created(self, event):
        print(event.src_path, event.event_type)
        myMsg = pymsteams.connectorcard("https://mustangplumbingrr.webhook.office.com/webhookb2/480b28ef-9e5f-41ea-a054-69b691add8d5@f1799ac8-2ec2-4176-9072-180ec0e2aeca/IncomingWebhook/a8e96abd9fb64dccafce90bf026b3817/cb9afd51-7b6c-433e-a359-1145dec1b260")
        pathName = str(event.src_path)
        fileName= pathName.split("\\")
        blah = fileName[len(fileName)-1]

        print(getProblemReport(event))
        

        myMsg.text(blah + " is in \"!!Needs Builder Info\". It has a problem report:\n" + getProblemReport(event))
        

        myMsg.send()

class Folder:
    def __init__(self, path):
        self.path = path
        nameArray = str(self.path).split("\\")
        self.name = nameArray[len(nameArray)-1]
        self.createTime = time.ctime(os.path.getctime(self.path))
        self.age = math.ceil(int(time.time() - os.path.getctime(self.path)) / (60 * 60 * 24))
        self.amIOld(self.age)
        self.ProblemReport()
    def amIOld(self, age):
        if age > 10:
            self.old = True
        else:
            self.old = False
    def ProblemReport(self):
        txtList = [f for f in os.listdir(self.path) if f.endswith('.txt')]

        for title in txtList:
            if "problem" or "Problem" or "PROBLEM" in str(title):
                pRPath = str(self.path + "\\" + title)
                #self.problemReportPath = problemReportPath
            else:
                return
        try:
            with open(pRPath, 'r') as blah:
                self.pRText = blah.read()
        except:
            return
        # return problemReportText



def generateLateList():
    needsBuilderInfoPath = "C:\\Users\\bgonzalez\\Mustang Plumbing\\CAD Plans - General\\!! NEEDS BUILDER INFO"
    folderList = []
    oldFolderList = []

    oldIndex = 0
    index = 0
    for entry in os.listdir(needsBuilderInfoPath):
        pathName = needsBuilderInfoPath + "\\" +  str(entry)
        folderList.append(Folder(pathName))

        print(f"Address: {folderList[index].name} is {folderList[index].age} days old")
        
        if folderList[index].old:
            oldFolderList.append(folderList[index])
            print(f" and is old, with Problem: \n{folderList[index].pRText}")
        
        index += 1


def getProblemReport(event):
    txtList = [f for f in os.listdir(event.src_path) if f.endswith('.txt')]
    for title in txtList:
        if "problem" or "Problem" or "PROBLEM" in str(title):
            problemReportPath = str(event.src_path + "\\" + title)
    with open(problemReportPath, 'r') as blah:
        problemReportText = blah.read()
    return(problemReportText)
    #return problemReportText

if __name__ == "__main__":
    #src_path = sys.argv[1]
    src_path = "C:\\Users\\bgonzalez\\Mustang Plumbing\\CAD Plans - General\\!! NEEDS BUILDER INFO"
    
    event_handler=MonitorFolder()
    observer = Observer()
    observer.schedule(event_handler, path=src_path)
    print("Monitoring started")
    #generateLateList()
    observer.start()
    try:
        while(True):
           time.sleep(1)
           
    except KeyboardInterrupt:
            observer.stop()
            observer.join()

myMsg = pymsteams.connectorcard("https://mustangplumbingrr.webhook.office.com/webhookb2/480b28ef-9e5f-41ea-a054-69b691add8d5@f1799ac8-2ec2-4176-9072-180ec0e2aeca/IncomingWebhook/a8e96abd9fb64dccafce90bf026b3817/cb9afd51-7b6c-433e-a359-1145dec1b260")
myMsg.text("This is a test notification")

myMsg.send()

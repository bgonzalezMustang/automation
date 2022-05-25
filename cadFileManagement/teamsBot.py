#https://mustangplumbingrr.webhook.office.com/webhookb2/480b28ef-9e5f-41ea-a054-69b691add8d5@f1799ac8-2ec2-4176-9072-180ec0e2aeca/IncomingWebhook/a8e96abd9fb64dccafce90bf026b3817/cb9afd51-7b6c-433e-a359-1145dec1b260
#^webhook for notifications bot

import pymsteams
import os
import time
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import math

from refData import *


eventMsg = pymsteams.connectorcard("webhook url")


def getProblemReport(event):
    print("Getting Problem Report...")
    time.sleep(30)
    txtList = [f for f in os.listdir(event.src_path) if f.endswith('.txt')]
    for title in txtList:
        if "problem" or "Problem" or "PROBLEM" in str(title):
            problemReportPath = str(event.src_path + "\\" + title)
            print("Located problem report...")
            
    try:
        with open(problemReportPath, 'r') as f:
            problemReportText = f.read()
            print(event.src_path, event.event_type)
            pathName = str(event.src_path)
            fileName= pathName.split("\\")
            blah = fileName[len(fileName)-1]

            myMsg = pymsteams.connectorcard("other webhook url")
            myMsg.color("a10d14")
            myMsg.text(blah + " is in \"!!Needs Builder Info\". It has a problem report:\n" + problemReportText)
            myMsg.send() 

            
        return(problemReportText)
    except:
        print("OOPS, not reading problem report")
        # eventMsg.text(f"Get Problem Report failed for {event.src_path}")
        # eventMsg.send()

class MonitorFolder(FileSystemEventHandler):
    def on_created(self, event):
        print(event.src_path, event.event_type)
        pathName = str(event.src_path)
        fileName= pathName.split("\\")
        blah = fileName[len(fileName)-1]

        print(getProblemReport(event))
    def on_moved(self, event):
        print(f"{event.src_path} was moved")

        eventMsg.text(f"{event.src_path} was moved")
        eventMsg.send()
    def on_deleted(self, event):
        print(f"{event.src_path} was deleted/moved")

        eventMsg.text(f"{event.src_path} was deleted/moved")
        eventMsg.send()
    

if __name__ == "__main__":
    src_path = "C:\\Users\\bgonzalez\\Mustang Plumbing\\CAD Plans - General\\!! NEEDS BUILDER INFO"
    
    event_handler=MonitorFolder()
    observer = Observer()
    observer.schedule(event_handler, path=src_path)
    print("Monitoring started")

    eventMsg.color("0cc715")
    eventMsg.text("Script is running...")
    eventMsg.send()
    observer.start()
    try:
        while(True):
           time.sleep(1)
           
    except KeyboardInterrupt:
            eventMsg.color("ed0707")
            eventMsg.text("SCRIPT IS DOWN!!!!")
            eventMsg.send()

            observer.stop()
            observer.join()

print("SCRIPT IS DOWN")

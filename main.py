#https://mustangplumbingrr.webhook.office.com/webhookb2/480b28ef-9e5f-41ea-a054-69b691add8d5@f1799ac8-2ec2-4176-9072-180ec0e2aeca/IncomingWebhook/a8e96abd9fb64dccafce90bf026b3817/cb9afd51-7b6c-433e-a359-1145dec1b260
#^webhook for notifications bot

import pymsteams
import os
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MonitorFolder(FileSystemEventHandler):
   def on_created(self, event):
        print(event.src_path, event.event_type)
        myMsg = pymsteams.connectorcard("https://mustangplumbingrr.webhook.office.com/webhookb2/480b28ef-9e5f-41ea-a054-69b691add8d5@f1799ac8-2ec2-4176-9072-180ec0e2aeca/IncomingWebhook/a8e96abd9fb64dccafce90bf026b3817/cb9afd51-7b6c-433e-a359-1145dec1b260")
        pathName = str(event.src_path)
        fileName= pathName.split("\\")
        blah = fileName[len(fileName)-1]

        print(getProblemReport(event))
        #print(getProblemReport(event))

        myMsg.text(blah + " is in \"!!Needs Builder Info\". It has a problem report:\n" + getProblemReport(event))
        

        myMsg.send()


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

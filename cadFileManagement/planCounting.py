import os
import sys
import time
from datetime import date
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

daily_plan_count = 0

today_date = date.today()
current_date = date.today()

date_text = str(today_date)
data_path = "C:\\Users\\bgonzalez\Mustang Plumbing\\CAD Plans - General\\- CAD Data\\Daily_Plans_Incoming"
average_text_path =  "C:\\Users\\bgonzalez\Mustang Plumbing\\CAD Plans - General\\- CAD Data\\Incoming_Plan_Average.txt"

class MonitorFolder(FileSystemEventHandler):
    def on_created(self, event):
        #Increment count when plan added
        daily_plan_count += 1
        print(f"New Plan added, total of {daily_plan_count} plans")
        text_file = open(file_path, 'w')
        text_file.write(daily_plan_count)
        text_file.close()

def getRollingAverage(path):
    return 0

#Start of New Day...
while(True):
    while(current_date == today_date):
        file_path = data_path + "\\" + date_text + ".txt"
    
    average_text_file = open(average_text_path, 'w')
    average_text_file.write(getRollingAverage(data_path))
    average_text_file.close()
    daily_plan_count = 0
    today_date = current_date





if __name__ == "__main__":
    src_path = "C:\\Users\\bgonzalez\Mustang Plumbing\\CAD Plans - General\\READY FOR CAD"
    
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
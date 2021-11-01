# import time module, Observer, FileSystemEventHandler
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# refData.py contains all of our desired reference data
from refData import *
from folderFunctions import *


class OnMyWatch:
    # Set the directory on watch
    watchDirectory = "C:/Users/dwanegar/Desktop/Mustang Plumbing/CAD Plans - General/CAD - WORKING"
  
    def __init__(self):
        self.observer = Observer()
  
    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()
  
  
class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory and event.event_type == 'created':
            # Event is created, you can process it now
            # print("Watchdog received created event - % s." % event.src_path)

            eventPath = event.src_path.replace('\\','/')
            # Determine whether folder is in Needs Correction, Make Shortcut, Check Script, or Move To Finished
            eventPathStringset = eventPath.split('/')
            eventLocation = '/'.join(eventPathStringset[:-2])
            print(eventLocation)
            # print(eventPath)

            if(eventLocation in watchedDirectories):
                # If any of the above, identify non-old CAD pdf
                # If NC/MS/CS, determine which user is associated with it for sorting
                # Else if MTF, determine the builder
                pdfName, builder = identifyCAD(eventPath)
                if pdfName is None:
                    Path(eventPath+'/'+'ERROR - COULD NOT DETERMINE CAD PDF.txt').touch()
                    return None
                if builder is None:
                    Path(eventPath+'/'+'ERROR - COULD NOT DETERMINE BUILDER.txt').touch()
                    return None
                if builder in builderCorrectSpellings.keys():
                    builder = builderCorrectSpellings[builder]
                if not (builder in builderPaths.keys()):
                    Path(eventPath+'/'+'ERROR - BUILDER NAME NOT FOUND.txt').touch()
                authorName = eventPathStringset[-2]
                folderName = eventPathStringset[-1]
                cadFiles = {
                    'pdfName': pdfName,
                    'builder': builder,
                    'author': authorName,
                    'folderName': folderName,
                    'folderPath': eventPath
                }

                try:
                    # If NC create 'OLD#-' duplicate of CAD
                        # If no shortcut, find dwg file and make shortcut
                    if(eventLocation == needsCorrectionPath):
                        print("needs correction")
                        createOldCopy(cadFiles)
                        createShortcut(cadFiles)

                    # Else if MS and no shortcut exists, find dwg file and make shortcut
                    elif(eventLocation == makeShortcutPath):
                        print("make shortcut")
                        createShortcut(cadFiles)
                        moveToInProgress(cadFiles)

                    # Else if CS, run checking script which
                        # If pass, move to Ready For Check
                        # Else, kick back to In Progress
                        # Both cases add a note about table structure, fixture counts, and includes any fail reasons
                    elif(eventLocation == checkScriptPath):
                        print("check script")
                        checkScript(cadFiles)
                    
                    # Else if MTF,
                        # If builder not on list (likely PEBKAC), move back to CHECK IN PROGRESS w/ note
                        # If builder on list, move to FINISHED FROM CAD in the respective builder file
                    elif(eventLocation == moveToFinishedPath):
                        print("move to finished")
                        moveToFinished(cadFiles)

                except:
                    Path(eventPath+'/'+'ERROR - SOMETHING WENT WRONG.txt').touch()
        return None
              
if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()

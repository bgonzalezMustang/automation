This is the cad file management system. There are multiple python files, some of which are interconnected and some which are not.
Below is the grouping of the files, and a description of their purpose.

"Script folders":
    These files handle moving files around on the cad onedrive. The check if a file is in a specific "script" folder, locate a cad plan based on the title of the pdf, and perform some operation based on the folder they are in.
    They can move folders, create new files, copy files, change the name of files.
        -folderFunctions.py
        -main.py
        -refData.py
        -builderInfo.json

"Needs Builder info":
    This file checks for when a plan is put in the "Needs builder info" folder, finds a problem report file within the folder, pulls the information from the problem report, and puts all of that into a teams message which is sent to the coordinators.
        -teamsBot.py

"Cad Data tracking":
    This file counts the number of incoming plans in ready for cad. As each plan is added, it modifies a text file containing the count titled that day's date.
        -planCounting.py

"Check PDF":
    This file is depreciated. The current method of drawing plans is incompatible with the check script.
        -checkPDF.py

----------------------------------------------------------------------

Where and how these scripts are run/hosted:
    These scripts are run on a remote computer that was at some point also running quickbooks.
    They are launched with a .bat file that runs command line commands to run the files.
    This .bat file is automatically scheduled with Task Scheduler on the remote computer to run on startup of the machine. (This allows automatic resumption in the case of a power outage)

    -myStartup.bat
        This file actually launches the python files
        It is triggered on startup of the machine
    -test.bat
        This file ends all existing python instances, then restarts the computer
        It is triggered on a schedule at 3:00 AM.
        This is done to help prevent Onedrive Syncing issues

-----------------------------------------------------------------------

Known bugs and issues
    "Script folders":
        -BUG: A file will occasionally get stuck in a script folder.
            -FIX 1: Check if an error log was created. Usually the issue is that a 'CAD plan was not found'. To solve this, make sure that the syntax of the cad file goes "PLAN#-ELEVATION-SWING-#BRK-BUILDER-ADDRESS".
            -FIX 2: Occasionally the remote computer will have issues syncing Onedrive. This will cause it to not notice when a plan is put in its folder. To solve, restart Onedrive on the remote computer.
            -FIX 3: Restart the remote computer. This will cause the script to restart as well.
        -BUG: A shortcut will not be created when a plan is placed in Ready To Check script folder
            -FIX 1: Check that the Cad file name's syntax is correct, and run it through the folder again
            -FIX 2: Check that the Cad file name is the EXACT same as the dwg file on the server
            -FIX 3: Check that the dwg is saved into the correct folder on the server
    
    "Needs Builder Info":
        -BUG: The problem report will not be included in the message sent to coordinators
            -FIX 1: Check that there is a text file called 'Problem Report' in the file before being uploaded
            -FIX 2: Check the spelling of the problem report file
        -BUG: No message is sent to the coordinators message
            -FIX 1: Check that the remote computer is syncing properly. It could be a OneDrive issue.
            -FIX 2: Restart the remote computer. This will restart the script and OneDrive.
    
    "CAD Data tracking":
        -BUG: The number of plans does not get reset daily
            -FIX 1: Honestly, this code is terrible, truly terrible. It only resets the count when the script starts over, not sure why. Restart the script or computer to fix.
            -FIX 2: Abandon code, write something better.

    Task Scheduler:
        -BUG: The CAD script did not launch upon startup
            -FIX 1: Restart the computer without powershell commands.
            -FIX 2: Remove the scheduled restart and manually restart computer as issues arise.

-------------------------------------------------------------------------

General debugging

    -Restarting the remote computer should solve most of these problems.
    -Periodically check all script folders to ensure that they are being moved properly.
    -Ensure that your own OneDrive is syncing properly
    
    -To add a new builder to the Move to Finished script
        -Navigate to the json called builderInfo.json on the public user of the server at "S:Public/CAD CODE REFERENCE/builderInfo.json"
        -You can edit this file in any text editor
        -Follow the naming convention in the other builders in the json
        -Save the file to update changes
        -Restart the script to have changes take effect

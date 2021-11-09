# Import pdfreader for reading
from pdfreader import SimplePDFViewer

# Import re for regex manipulation
import re


# Fixture object stores data about various pulls
class Fixture:
    def __init__(self, fixtureName, downpullInches, downpullDim, sidepullInches, sidepullDim):
        self.name = fixtureName
        self.downpullInches = downpullInches
        self.downpullDim = downpullDim
        self.sidepullInches = sidepullInches
        self.sidepullDim = sidepullDim

# Stack Counter object counts various types of stacks to verify that the number in tables and number in the drawing are the same
class StackCounter:
    def __init__(self):
        self.stacksCount2inFloating = 0
        self.stacksCount2inTables = 0
        self.stacksCount3inFloating = 0
        self.stacksCount3inTables = 0
    
    def addStack(self, stackString, isFixture):
        if stackString.upper() == "2\" STACK":
            if isFixture:
                self.stacksCount2inTables += 1
            else:
                self.stacksCount2inFloating += 1
        elif stackString.upper() == "3\" STACK":
            if isFixture:
                self.stacksCount3inTables += 1
            else:
                self.stacksCount3inFloating += 1
    
    def verify(self):
        outString = ""
        if (self.stacksCount2inFloating != self.stacksCount2inTables):
            outString = outString + "Issues with 2\" STACK count. Identifying " + str(self.stacksCount2inFloating) + " in the drawing and " + str(self.stacksCount2inTables) + " in the tables. Please verify.\n"
        if (self.stacksCount3inFloating != self.stacksCount3inTables):
            outString = outString + "Issues with 3\" STACK count. Identifying " + str(self.stacksCount3inFloating) + " in the drawing and " + str(self.stacksCount3inTables) + " in the tables. Please verify.\n"
        return outString
    
    def discrepancy(self):
        return ((self.stacksCount2inTables + self.stacksCount3inTables) - (self.stacksCount2inFloating + self.stacksCount3inFloating))/2

    def isOdd(self):
        if ((self.stacksCount2inFloating + self.stacksCount2inTables)%2 == 1) or ((self.stacksCount3inFloating + self.stacksCount3inTables)%2 == 1):
            return True
        else:
            return False


class PDFChecker:

    def __init__(self):
        self.streetAddressRegex = r'(\d+\s\w+)'

        self.addressMatch = False

        self.longTextRegex = re.compile(r".*[\w\s]{13,}")#saying that any string that has 13 chars or more and is composed of letters
        # or spaces is considered long and is probably a note or something
        #^include punctuation, plus right now it excludes all numbers which could lead to some broken cases
        #^on that note, I don't see why we shouldn't just look for a regex of length 13 of any type of characters
        #examples: "3" Stack pulls from M.Bth bay"

        self.columnTitle = ["FIXTURE", "DOWNPULL", "SIDEPULL"]

        #These are the regexes for table titles
        self.tableTitleRegexes = [
            re.compile(r"BATH"),
            re.compile(r"KITCHEN"),
            re.compile(r"UTILITY"),
            re.compile(r"POWDER"),
            re.compile(r"PATIO")
        ]

        # These regexes could probably be improved. I imagine there are scenarios that break them. Maybe we just fix them as
        # issues are discovered?
        self.fixtureRegexesFiveSet = [
            re.compile(r"(?:c|ow|tw|.*[\'\"]c|.*[\'\"]ow|.*[\'\"]tw|.*overall|\'|\d+\'-\d+(?:1\/2)?\"|[\w\s]{14,}|.*[\'\"])$"),
            #re.compile(r"(?:c|ow|tw|.*overall|\'|\d+\'-\d+(?:1\/2)?\"|[\w\s]{14,})"),
            #re.compile(r"(?:c|ow|tw|overall|\d+\'-\d+(?:1\/2)?\")"), #This needs to be tested better
                #list of characters that must be EXCLUDED in the name/first row of a fixture
            re.compile(r"\d+\'-\d+(?:\s1\/2)?\""),
                #list of characters that must be INCLUDED in the second column of a fixture, meaning it is a number/measurement
            re.compile(r"(?:c|ow|tw)"),
                #list of strings that must be included for third column, meaning the suffix
            re.compile(r"\d+\'-\d+(?:\s1\/2)?\""),
            re.compile(r"(?:c|ow|tw)")
        ]

        #does the same thing as fixtureRegexesFiveSet, but for three column table types
        self.fixtureRegexesThreeSet = [
            re.compile(r"(?:c|ow|tw|.*[\'\"]c|.*[\'\"]ow|.*[\'\"]tw|.*overall|\d+\'(?:-\d+(?:1\/2)?\")?(?:c|ow|tw|overall)|[\w\s]{13,}|.*[\'\"])$"),
            re.compile(r"\d+\'-\d+(?:\s1\/2)?\"(?:c|ow|tw)"),
            re.compile(r"\d+\'-\d+(?:\s1\/2)?\"(?:c|ow|tw)")
        ]

        self.pullShortRegex = r'^(\d+)\'-(\d+)\"(\w+)$'
        self.pullLongRegex = r'^(\d+)\'-(\d+)\"$'

    def checkAddress(self, myString, myAddress):
        regexMatch = re.compile(self.streetAddressRegex).match(myString)
        if regexMatch:
            return regexMatch[1] == myAddress
        return False

    # Detects if a five string set is a fixture
    def fixtureDetectorFiveString(self, stringSet):
        isFixture = True
        if self.fixtureRegexesFiveSet[0].match(stringSet[0]):
            isFixture = False
            #saying that the first column may not contain any of the excluded regexes for it to be a valid fuixture
        for i in range(1,4):
            if not self.fixtureRegexesFiveSet[i].match(stringSet[i]):
                isFixture = False
                break
                #saying that columns 2-5 all must INCLUDE the include regex list regexes for it to be a valid fixture row
        return isFixture

    def convertStringToPulls(self, stringSet):
        if type(stringSet) == str:
            return self.readPullShort(stringSet)
        elif len(stringSet) == 2:
            return self.readPullLong(stringSet)
        return None, None

    def fixtureDetectorBeta(self, stringset):
        isFixture = True
        fixtureTitle = ""
        pullCount = 0
        pullInches = []
        pullDim = []
        if self.fixtureRegexesThreeSet[0].match(stringset[0]):
            return False, None
        else:
            fixtureTitle = stringset[0]
        i = 1
        while (i < len(stringset) and pullCount < 2):
            if self.fixtureRegexesThreeset[1].match(stringset[i]):
                numInches, strDim = self.convertStringToPulls(stringset[i])
                pullInches.append(numInches)
                pullDim.append(strDim)
                pullCount += 1
                i += 1
            elif i+1 < len(stringset):
                if self.fixtureRegexesFiveSet[1].match(stringset[i]) and self.fixtureRegexesFiveSet[2].match(stringset[i+1]):
                    numInches, strDim = self.convertStringToPulls(stringset[i:i+2])
                    pullInches.append(numInches)
                    pullDim.append(strDim)
                    pullCount += 1
                    i += 2
                else:
                    isFixture = False
                    break
            else:
                isFixture = False
                break
        if isFixture:
            return isFixture, Fixture(fixtureTitle, pullInches[0], pullDim[0], pullInches[1], pullDim[1])
        return False, None

    # Detects if a string set is a fixture
    def fixtureDetector(self, stringSet):
        isFixture = True
        setSize = 5
        if self.fixtureRegexesThreeSet[0].match(stringSet[0]):
            isFixture = False
        for i in range(1, 3):
            if not self.fixtureRegexesThreeSet[i].match(stringSet[i]):
                isFixture = False
                break
        if isFixture:
            setSize = 3
            return isFixture, setSize
        if (len(stringSet) > 4):
            isFixture = self.fixtureDetectorFiveString(stringSet)
        return isFixture, setSize

    def readPullShort(self, pullString):
        pullSet = re.compile(self.pullShortRegex).match(pullString)
        pullInches = 12*int(pullSet[1]) + int(pullSet[2])
        pullDim = pullSet[3]
        return pullInches, pullDim

    def convertThreeStringSetToPulls(self, stringSet):
        downpullInches, downpullDim = self.readPullShort(stringSet[1])
        sidepullInches, sidepullDim = self.readPullShort(stringSet[2])
        return stringSet[0], downpullInches, downpullDim, sidepullInches, sidepullDim

    def readPullLong(self, pullStringPair):
        pullSet = re.compile(self.pullLongRegex).match(pullStringPair[0])
        pullInches = 12*int(pullSet[1]) + int(pullSet[2])
        pullDim = pullStringPair[1]
        return pullInches, pullDim

    def convertFiveStringSetToPulls(self, stringSet):
        downpullInches, downpullDim = self.readPullLong(stringSet[1:3])
        sidepullInches, sidepullDim = self.readPullLong(stringSet[3:5])
        return stringSet[0], downpullInches, downpullDim, sidepullInches, sidepullDim

    def convertStringSetToPulls(self, setSize, stringSet):
        if setSize == 3:
            return self.convertThreeStringSetToPulls(stringSet)
        elif setSize == 5:
            return self.convertFiveStringSetToPulls(stringSet)
        else:
            return "", 0, "", 0, ""

    def inchesAsFtInString(self, totalInches):
        feet = int(totalInches/12)
        inches = int(totalInches%12)
        return str(feet) + "\'-" + str(inches) + "\""
    
    def pullPresentation(self, fixture):
        presentationString = self.inchesAsFtInString(fixture.downpullInches) + fixture.downpullDim + " downpull and " + \
                             self.inchesAsFtInString(fixture.sidepullInches) + fixture.sidepullDim + " sidepull"
        return presentationString

    def isColumnTitle(self, stringSet):
        return stringSet == self.columnTitle

    # Verifies 3" stack is actually part of a table
    def verifyStack(self, stringSet):
        startIndex = len(stringSet)-3
        if (self.longTextRegex.search(stringSet[-1])):
            startIndex -= 1
            if startIndex < 0:
                startIndex = 0
        if self.fixtureDetector(stringSet[startIndex:startIndex+3]) or self.isColumnTitle(stringSet[startIndex:startIndex+3]):
            return True
        if len(stringSet) > 4:
            startIndex -= 2
            if startIndex < 0:
                startIndex = 0
            if self.fixtureDetectorFiveString(stringSet[startIndex:startIndex+5]):
                return True
        return False

    # Detects if string is a valid table title
    def detectTableHeader(self, myString):
        for regex in self.tableTitleRegexes:
            if regex.search(myString):
                return True
        return False

    def checkPDF(self, pdfToCheck):
        pdfFileObj = open(pdfToCheck, 'rb')
        filename = pdfToCheck.split('/')[-1]
        viewer = SimplePDFViewer(pdfFileObj)
        stackCounter = StackCounter()

        streetAddress = re.compile(self.streetAddressRegex).search(filename)[1]
        
        # The mandatory room types require minimum one of each type, but any one of a given type will do
        kitchen = ["KITCHEN"]
        bath = ["BATH", "POWDER", "UTILITY"]
        mandatoryRoomTypes = [kitchen, bath]

        # Convert mandatoryRoomTypes to a regex list
        mandatoryRoomRegexes = []
        # Add list of rooms successfully verified in tables
        roomVerification = []
        for roomType in mandatoryRoomTypes:
            # This looks like r"(?=(ROOM1|ROOM2|ROOM3))"
            roomTypeRegex = r"("+'|'.join(roomType)+r")"
            mandatoryRoomRegexes.append(roomTypeRegex)
            roomVerification.append(False)

        # Starts in a "pass" state. Failing at any point changes this to failTest = True
        failTest = False

        # Whenever any event would cause failTest = True, a relevant string is added to the failLog
        failLog = []

        # Dictionary of fixtures generated by above function, fixtureDetector()
        fixtureDict = {}

        # Dictionary of tables generated by items proceeding columnTitle string sets
        tableDict = {}

        # counts total number of strings in document
        strings_count = 0

        # canvases are pages in a pdf, I think? Regardless, iterate over these
        for canvas in viewer:
            # Get the list of strings in the canvas. These are ordered by the method the pdf was written, not how it is viewed.
            page_strings = canvas.strings
            # print(page_strings)

            # Generate the dictionary of table titles, with cumulative page_strings indices as keys
            for regex in self.tableTitleRegexes:
                if len(page_strings) > 1:
                    for j in range(len(page_strings)-1):
                        if (regex.search(page_strings[j]) and page_strings[j+1] == "FIXTURE"):
                            tableDict[strings_count + j]=page_strings[j]

            # This should generate the list of all the detected fixtures, with cumulative page_strings indices as keys
            if len(page_strings) > 2:
                if len(page_strings) > 4:
                    for j in range(len(page_strings)-4):
                        isFixture, setSize = self.fixtureDetector(page_strings[j:j+5])
                        if(isFixture):
                            if(j > 1 and (page_strings[j].upper() == "3\" STACK" or page_strings[j].upper() == "2\" STACK")):
                                isFixture = self.verifyStack(page_strings[max(j-6, 0):j])
                            elif (j <= 1 and (page_strings[j].upper() == "3\" STACK" or page_strings[j].upper() == "2\" STACK")):
                                isFixture = False
                            if isFixture:
                                # print(setSize, page_strings[j:j+5])
                                fixtureDict[strings_count + j]= Fixture(*self.convertStringSetToPulls(setSize, page_strings[j:j+5]))
                                # fixtureDict[strings_count + j]=page_strings[j]
                        elif self.checkAddress(page_strings[j], streetAddress):
                            addressMatch = True
                        stackCounter.addStack(page_strings[j], isFixture)
                for j in range(max(0,len(page_strings)-4),len(page_strings)-2):
                    isFixture, setSize = self.fixtureDetector(page_strings[j:j+3])
                    if(isFixture):
                        if(page_strings[j].upper() == "3\" STACK" or page_strings[j].upper() == "2\" STACK"):
                            isFixture = self.verifyStack(page_strings[max(j-6, 0):j])
                        if isFixture:
                            # fixtureDict[strings_count + j]=page_strings[-4+j]
                            fixtureDict[strings_count + j]=Fixture(*self.convertStringSetToPulls(setSize, page_strings[j:]))
                            # print(page_strings[-4+j:])
                    elif self.checkAddress(page_strings[j], streetAddress):
                        addressMatch = True
                    stackCounter.addStack(page_strings[j], isFixture)
            strings_count += len(page_strings)

        # Verify the address
        if not addressMatch:
            failTest = True
            failLog.append("Address does not appear to match")

        # Verify that the mandatory rooms have tables
        for i in range(len(mandatoryRoomRegexes)):
            roomTypeRegex = mandatoryRoomRegexes[i]
            r = re.compile(roomTypeRegex)
            for key in tableDict:
                if (r.search(tableDict[key])):
                    roomVerification[i] = True

        # If any room hasn't been verified, fail the test. Append the failLog for each.
        for i in range(len(roomVerification)):
            if not roomVerification[i]:
                failTest = True
                failLog.append(mandatoryRoomRegexes[i])

        wallFixtureRegex = r'(LAV)|(SINK)|(VENT)|(W\/?B)|(W\/?S)|(W\/?H)'
        centerFixtureRegex = r'(W\/?C)|(TUB)|(SHWR)'
        for key in fixtureDict.keys():
            numCenters = 0
            if fixtureDict[key].downpullDim == 'c':
                numCenters += 1
            if fixtureDict[key].sidepullDim == 'c':
                numCenters += 1
            if numCenters == 0:
                failTest = True
                failLog.append(fixtureDict[key].name + " at " + self.pullPresentation(fixtureDict[key]) + " has too many pulls on a wall\n")
            elif re.compile(centerFixtureRegex).match(fixtureDict[key].name) and numCenters == 1:
                failTest = True
                failLog.append(fixtureDict[key].name + " at " + self.pullPresentation(fixtureDict[key]) + " should not be on a wall\n")
            elif re.compile(wallFixtureRegex).match(fixtureDict[key].name) and numCenters == 2:
                failTest = True
                failLog.append(fixtureDict[key].name + " at " + self.pullPresentation(fixtureDict[key]) + " should have one pull on a wall\n")

        for key in fixtureDict.keys():
            if fixtureDict[key].downpullInches < 12 and fixtureDict[key].downpullDim == 'tw':
                failTest = True
                failLog.append(self.pullPresentation(fixtureDict[key]) + " has a \'tw\' very close to an exterior wall\n")
            if fixtureDict[key].sidepullInches < 12 and fixtureDict[key].sidepullDim == 'tw':
                failTest = True
                failLog.append(self.pullPresentation(fixtureDict[key]) + " has a \'tw\' very close to an exterior wall\n")
                

        brickRegex = r'(\d)BRK'
        numBricks = int(re.compile(brickRegex).search(filename)[1])
        if numBricks > 1:
            for key in fixtureDict.keys():
                if fixtureDict[key].sidepullInches < 7:
                    failTest = True
                    failLog.append(fixtureDict[key].name + " at " + self.pullPresentation(fixtureDict[key]) + " might not be accounting for brick in the sidepull\n")
                if numBricks == 4 and fixtureDict[key].downpullInches < 7:
                    failTest = True
                    failLog.append(fixtureDict[key].name + " at " + self.pullPresentation(fixtureDict[key]) + " might not be accounting for brick in the downpull\n")
        
        # Test to see if the stacks in tables matches the stacks in the drawing
        stackFailString = stackCounter.verify()
        stackFail = False
        if stackFailString != "":
            stackFail = True
            # failLog.append(stackFailString)
        if stackCounter.isOdd():
            failTest = True
            failLog.append('Uneven count of stacks. Please verify that all stacks have table entries and vice versa\n')

        # Test to see if tables are empty
        emptyTable = False
        for key in range(strings_count):
            if key in fixtureDict.keys():
                emptyTable = False
            if key in tableDict.keys():
                if emptyTable:
                    failTest = True
                    failLog.append("Empty table: " + tableDict[key] + '\n')
                emptyTable = True

        # Save output to a file
        outFile = "!SCRIPT CHECK RESULTS.txt"
        outFilePath = pdfToCheck.removesuffix(filename) + outFile
        with open(outFilePath, "w") as f:

            # Finish the program based on test results.
            if failTest:
                # add code to print failLog lines to a file
                f.write("Test failed, see log.")
                f.write("\n")
                f.write("\n")
                f.write("Fail Log:")
                f.write("\n")
                for logEntry in failLog:
                    f.write(str(logEntry))
                f.write("\n")
            else:
                f.write("Good job")
                f.write("\n")

            f.write("\n")
            f.write("Fixture Summary:")
            numWHs = 0
            for val in fixtureDict.values():
                if (val.name.upper() == 'WH' or val.name.upper() == 'W/H' or val.name.upper() == 'WTRHTR' or val.name.upper() == 'WTR HTR'):
                    numWHs += 1
            if numWHs == 0:
                f.write("There were " + str(len(tableDict.values())) + " tables and " + str(len(fixtureDict.values())) + " rough fixtures detected.\n")
            else:
                f.write("There were " + str(len(tableDict.values())) + " tables, " + str(len(fixtureDict.values()) - numWHs) + " rough fixtures, and " + str(numWHs) + " WH(s) detected.\n")
            if stackFail:
                f.write(stackFailString)
                f.write("If the stack discrepancy is a scripting mislabel, there should be " + str(len(fixtureDict.values()) - numWHs - stackCounter.discrepancy()) + " rough fixtures.\n")
            # Keys are indices, which saves us the trouble of ordering our values
            f.write("They are organized in the pdf as follows:\n")
            for key in range(strings_count):
                if key in tableDict.keys():
                    f.write("\n" + tableDict[key] + ":\n")
                if key in fixtureDict.keys():
                    f.write("    " + fixtureDict[key].name + " at " + self.pullPresentation(fixtureDict[key]) + "\n")
        pdfFileObj.close()
        print("finished checking?")
        return not(failTest)
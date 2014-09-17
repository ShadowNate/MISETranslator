#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Created by Praetorian (ShadowNate) for Classic Adventures in Greek
# classic.adventures.in.greek@gmail.com
#
import os, sys, shutil
from struct import *
from string import *


company_email = "classic.adventures.in.greek@gmail.com"
app_version = "1.00"
app_name = "monkeySERepaker"
app_name_spaced = "Monkey SE repaker"

#
# Get the original file. Backup it.
# Copy the header in new modded file. Update fields where needed (e.g. total size of data)
# ASSUMPTION: the file indexes (1 DWORD per file) are unaffected by the modded file size changes, and the new pak file will operate correctly if we keep them unaltered.
#               OTHERWISE we need to figure the connection, if there is one, and I can't find out what it is so far. They are sequentially incremented but not by some constant or something related to file size so...?
# Then get the list of files, and get them from the extracted folders.
# Get each file size, dump it in the file, update its size in the file header (file entry)
#
# We want to pak all extracted files from a .pak (for MI SE for a start) back into the pak (including any changed ones, but not any additional ones)
# Should be fairly easy:
# Take as input the original pak file (rb)
#
# - MAKE BACKUP
# START WRITING THE MODED PAK FILE
# Follow the index of the original, update the file sizes where necessary and the indexes that follow them of course (cascade effect).
# Dump the files as
#
#
class pakFile:
    _version = 0
    _lpak_or_pak = ""
    _littleEndianess = False
    _pakHeader = None
    _calcNumOfContainedFiles = 0
    _lstOfFileEntries = []
    _lstOfFileIndexes = []
    _lstOfFileNames = []
    _pakFileName = ""

    def __init__(self, porigPakFilename):
        """ Attempt to parse the original file
            and update the member vars of the class
        """
        errorFound = False;
        if os.path.exists(porigPakFilename) and os.access(porigPakFilename, os.F_OK) :
            self._pakFileName = porigPakFilename
            try:
                tmpPakFile = open(self._pakFileName, 'rb')
                try:
                    tmpPakFile.seek(0)
                    tmpCharListForEndianess = []
                    del tmpCharListForEndianess[:]
                    for i in range(0,4):
                        newChar = unpack('B', tmpPakFile.read(1))
                        if chr(newChar[0]) <> '\x00':
                            tmpCharListForEndianess.append(chr(newChar[0]))
                        else:
                            break
                    self._lpak_or_pak = "".join(tmpCharListForEndianess)

                    self._littleEndianess = self.decideEndianess(self._lpak_or_pak)
        #            print "LPAK = %s \n" % (_lpak_or_pak)
                    # TODO: the direction of the comparison sign is determined by the endianess. Here it is hardcoded. Ideally it should be customised!
                    tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple # TODO: is it two bytes for the version? what is the significance?
                    self._version =  tmpIntReadTuple[0]
                    tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                    tmpStartOfIndex =  tmpIntReadTuple[0]
                    tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                    tmpStartOfFileEntries =  tmpIntReadTuple[0]
                    tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                    tmpStartOfFileNames =  tmpIntReadTuple[0]
                    tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                    tmpStartOfData =  tmpIntReadTuple[0]
                    tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                    tmpSizeOfIndex =  tmpIntReadTuple[0]
                    tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                    tmpSizeOfFileEntries =  tmpIntReadTuple[0]
                    tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                    tmpSizeOfFileNames =  tmpIntReadTuple[0]
                    tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                    tmpSizeOfData =  tmpIntReadTuple[0]

                    self._pakHeader = pakHeader(self._lpak_or_pak, self._version, tmpStartOfIndex, tmpStartOfFileEntries, tmpStartOfFileNames, tmpStartOfData, tmpSizeOfIndex, tmpSizeOfFileEntries, tmpSizeOfFileNames, tmpSizeOfData)
                    ##print "SIZE OF FILE ENTRIES %d \nStart of data: %d\nSize Of Index:  %d\nStart Of File Entries:%d \n" % (self._pakHeader._sizeOfFileEntries, self._pakHeader._startOfData, self._pakHeader._sizeOfIndex,  self._pakHeader._startOfFileEntries)
                    self._calcNumOfContainedFiles = self._pakHeader._sizeOfFileEntries/ (5 * 4)  # 5 *4 bytes per file entry
                    print "Number of contained files is: %d " % (self._calcNumOfContainedFiles)

                    # file indexes list population. TODO: this is currently retained unchanged to the modded file.
                    tmpPakFile.seek(self._pakHeader._startOfIndex )
                    for i1 in range(0, self._calcNumOfContainedFiles):
                        tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                        tmpIntIndexForFile =  tmpIntReadTuple[0]
                        self._lstOfFileIndexes.append(tmpIntIndexForFile)
                    ##print "Indexes list length %d\n" % ( len(self._lstOfFileIndexes))
                    #
                    # file entries list population.
                    tmpPakFile.seek(self._pakHeader._startOfFileEntries)
                    for i1 in range(0, self._calcNumOfContainedFiles):
                        tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                        tmpfileDataPos =  tmpIntReadTuple[0]
                        tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                        tmpFileNamePos =  tmpIntReadTuple[0]
                        tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                        tmpDataSize =  tmpIntReadTuple[0]
                        tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                        tmpDataSize2 =  tmpIntReadTuple[0]
                        tmpIntReadTuple = unpack('<L',tmpPakFile.read(4))    # unpack always returns a tuple
                        tmpCompressed =  tmpIntReadTuple[0]
                        tmpFileEntry = pakFileEntry(tmpfileDataPos, tmpFileNamePos, tmpDataSize, tmpDataSize2, tmpCompressed, i1)
                        self._lstOfFileEntries.append(tmpFileEntry)
                    ##print "Entries list length %d\n" % ( len(self._lstOfFileEntries))
                    #
                    # Filenames list population.
                    #
                    tmpPakFile.seek(self._pakHeader._startOfFileNames)
                    tmpListOfCharsForFileName = []

                    for i1 in range(0, self._calcNumOfContainedFiles):
                        del tmpListOfCharsForFileName[:]
                        inTmpWord = True
                        while inTmpWord == True:
                            newChar = unpack('B', tmpPakFile.read(1))
                            if chr(newChar[0]) <> '\x00':
                                tmpListOfCharsForFileName.append(chr(newChar[0]))
                            else:
                                inTmpWord = False

                        tmpFileName = "".join(tmpListOfCharsForFileName)
                        self._lstOfFileNames.append(tmpFileName)
                    ##print "FileNames list length %d\n" % ( len(self._lstOfFileNames))

        ##            for i1 in range(0, len(self._lstOfFileNames)):
        ##                print "Name: %s" % (self._lstOfFileNames[i1])
                finally:
                    tmpPakFile.close()
            except IOError:
                errorFound = True
                if tmpPakFile!=None:
                    tmpPakFile.close()
        else:
            print "Error! Source original file was not found!"
            # pak header will be none here then.

        return

    #
    # It seems that endianess is different for the XBOX version (bigEndian)
    #
    def decideEndianess(self, headerfourBytes):
        retVal = None
        if headerfourBytes == 'LPAK':
            retVal = False
        elif headerfourBytes == 'KAPL':
            retVal = True
        return retVal


    def produceModdedPak(self, rootFolder = "./", parseMode = 1):
        # TODO: get current directory from original pak file and write the new file there?
        errorFound = False;
        tmpTargetPakFile = None
        try:
            tmpTargetPakFile = open("modded.pak", 'wb')
            try:
                # TODO: ideally here we should have a writeHeader method!
                for tmChar in list(self._pakHeader._lilEndianMagic):
                    tmpTargetPakFile.write(pack('B', ord(tmChar)))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._version))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._startOfIndex))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._startOfFileEntries))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._startOfFileNames))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._startOfData))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._sizeOfIndex))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._sizeOfFileEntries))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._sizeOfFileNames))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._sizeOfData))

                # then follows the file index list (unchanged)
                #print "File Index List from address: %s " % ( hex(tmpTargetPakFile.tell()))
                for i1 in range (0, len(self._lstOfFileIndexes)):
                    tmpTargetPakFile.write(pack('<L',self._lstOfFileIndexes[i1]))
                    ##OLD ##print "%d. %s " % (i1, hex(self._lstOfFileIndexes[i1]+ tmpTargetPakFile.tell() - 4))
                    #print "%d. %s " % (i1, hex(self._lstOfFileIndexes[i1]))

                # then follows the file entries
                # TODO: ideally here we should have a writeFileEntry ???
                # we will revisit this file entries space to update offsets for data pos and size!
                #print "#################################################"
                #print "File Entries Init List (before update) from address: %s " % ( hex(tmpTargetPakFile.tell()))
                for i1 in range (0, len(self._lstOfFileEntries)):
                    tmpFileEntry = self._lstOfFileEntries[i1]
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._fileDataPos))
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._fileNamePos))
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._dataSize))
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._dataSize2))
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._compressed))
                    ##OLD ##print "%d. %s %s %s %s %s" % (i1, hex(tmpFileEntry._fileDataPos + tmpTargetPakFile.tell() - 20), hex(tmpFileEntry._fileNamePos + tmpTargetPakFile.tell() - 16), hex(tmpFileEntry._dataSize), hex(tmpFileEntry._dataSize2), hex(tmpFileEntry._compressed))
                    #print "%d. %d %s %s %s %s %s" % (i1, tmpFileEntry._orderInTheOrigFile, hex(tmpFileEntry._fileDataPos), hex(tmpFileEntry._fileNamePos), hex(tmpFileEntry._dataSize), hex(tmpFileEntry._dataSize2), hex(tmpFileEntry._compressed))

                # then follows the filename catalogue
                #print "#################################################"
                #print "File Name catalogue from address: %s " % ( hex(tmpTargetPakFile.tell()))
                for i1 in range (0, len(self._lstOfFileNames)):
                    tmpFileName = self._lstOfFileNames[i1]
                    for tmChar in list(tmpFileName):
                        tmpTargetPakFile.write(pack('B', ord(tmChar)))
                    tmpTargetPakFile.write(pack('B', ord('\x00')))
                    #print "%d. %s" % (i1, tmpFileName)

                # then we follow the filenames catalogue and retrieve the extracted files, open them and dump them in the modded file. (for MI:SE)
                # TODO: for MI2:SE we need to follow another order as specified in the offsets of the file entries list.
                mi2seFileNameOrderList = []
                if parseMode == 2:
                    mi2seFileNameOrderList = sorted(self._lstOfFileEntries, key=lambda pakFileEntry: pakFileEntry._fileDataPos)
                    #print "#################################################"
                    #print "SORTED MI2SE File Name catalogue "
                    for i1 in range (0, len(mi2seFileNameOrderList)):
                        tmpFileEntry = mi2seFileNameOrderList[i1]
                        #print "%d. %s" % (i1, self._lstOfFileNames[tmpFileEntry._orderInTheOrigFile])

                # We also get the new size of the files and make changes accordingly in the file entries list
                modPakTotalSizeOfContainedFilesData = 0
                accumulatedOffset = 0
                for i1 in range (0, len(self._lstOfFileNames)):
                    tmpFileName = self._lstOfFileNames[i1]
                    # MI2:SE specific!
                    tmpMI2SEFileEntry = None
                    if parseMode == 2:
                        tmpMI2SEFileEntry = mi2seFileNameOrderList[i1]
                        tmpFileName = self._lstOfFileNames[tmpMI2SEFileEntry._orderInTheOrigFile]
                    # <scx>
                    #newFixedTmpFileName = replace(tmpFileName, "/" , "\\")
                    #fullpathNewFixedTmpFileName =  rootFolder + '\\' +  newFixedTmpFileName
                    newFixedTmpFileName = tmpFileName
                    if os.sep <> "/":
                        newFixedTmpFileName = replace(tmpFileName, "/" , os.sep)
                    fullpathNewFixedTmpFileName = os.path.join(rootFolder, newFixedTmpFileName)
                    # </scx>
                    if not os.path.exists(fullpathNewFixedTmpFileName):
                        print "ERROR! No such file found: %s !" % (fullpathNewFixedTmpFileName)
                        pass
                    else:
                        #print "File found: %s " % (newFixedTmpFileName)
                        extrFileSize = os.path.getsize(fullpathNewFixedTmpFileName)
                        try:
                            tmpContainedFileOpen = open( fullpathNewFixedTmpFileName, 'rb')
                            try:
                                openedFileContents = tmpContainedFileOpen.read(extrFileSize)
                                if tmpContainedFileOpen.read() <> "":
                                    print "Error: This file has more bytes: %s !!! " % (newFixedTmpFileName) # should never happen
                            finally:
                                tmpContainedFileOpen.close()
                        except IOError:
                            if tmpContainedFileOpen!=None:
                                tmpContainedFileOpen.close()

                        #write file contents byte -to- byte into the new modded file!
                        # TODO: a faster way to dump binary data?
        #                for tmChar in list(openedFileContents):
        #                    tmpTargetPakFile.write(pack('B', ord(tmChar)))
                        tmpTargetPakFile.write(openedFileContents)
                        #print "Extr file size = %d, Opened file data size = %d " % (extrFileSize, len(openedFileContents))
                        tmpFileOrigPos = 0
                        if parseMode == 1:
                            tmpFileOrigPos = self._lstOfFileEntries[i1]._fileDataPos
                            self._lstOfFileEntries[i1]._fileDataPos = tmpFileOrigPos + accumulatedOffset
                            if extrFileSize <> self._lstOfFileEntries[i1]._dataSize:
                                accumulatedOffset +=  (extrFileSize -  self._lstOfFileEntries[i1]._dataSize)
                                print "(Info) File size modified: %s" % (newFixedTmpFileName)
##                                print "(Info) File size modified: %s  Offset accum is now %d!!! " % (newFixedTmpFileName, accumulatedOffset)
                                self._lstOfFileEntries[i1]._dataSize = extrFileSize
                                self._lstOfFileEntries[i1]._dataSize2 = extrFileSize
                        else: #mi2se
                            tmpFileOrigPos = tmpMI2SEFileEntry._fileDataPos
                            i1_mi2se = tmpMI2SEFileEntry._orderInTheOrigFile
                            self._lstOfFileEntries[i1_mi2se]._fileDataPos = tmpFileOrigPos + accumulatedOffset
                            if extrFileSize <> self._lstOfFileEntries[i1_mi2se]._dataSize:
                                accumulatedOffset +=  (extrFileSize -  self._lstOfFileEntries[i1_mi2se]._dataSize)
                                print "(Info) File size modified: %s" % (newFixedTmpFileName)
##                               print "(Info) File size modified: %s  Offset accum is now %d!!! " % (newFixedTmpFileName, accumulatedOffset)
                                self._lstOfFileEntries[i1_mi2se]._dataSize = extrFileSize
                                self._lstOfFileEntries[i1_mi2se]._dataSize2 = extrFileSize

                        modPakTotalSizeOfContainedFilesData += extrFileSize

                if modPakTotalSizeOfContainedFilesData <> self._pakHeader._sizeOfData:
                    print "(INFO) Total size of contained files data differs from original (%d  vs  %d)! This is normal for mods." % (modPakTotalSizeOfContainedFilesData,self._pakHeader._sizeOfData)# is expected to occur
                    self._pakHeader._sizeOfData = modPakTotalSizeOfContainedFilesData

                # in the end we rewrite the header and the file entries catalogue!
                tmpTargetPakFile.seek(0)
                for tmChar in list(self._pakHeader._lilEndianMagic):
                    tmpTargetPakFile.write(pack('B', ord(tmChar)))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._version))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._startOfIndex))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._startOfFileEntries))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._startOfFileNames))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._startOfData))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._sizeOfIndex))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._sizeOfFileEntries))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._sizeOfFileNames))
                tmpTargetPakFile.write(pack('<L',self._pakHeader._sizeOfData))

                tmpTargetPakFile.seek(self._pakHeader._startOfFileEntries)
                for i1 in range (0, len(self._lstOfFileEntries)):
                    tmpFileEntry = self._lstOfFileEntries[i1]
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._fileDataPos))
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._fileNamePos))
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._dataSize))
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._dataSize2))
                    tmpTargetPakFile.write(pack('<L',tmpFileEntry._compressed))

            finally:
                tmpTargetPakFile.close()
        except IOError:
            errorFound = True
            if tmpTargetPakFile != None:
                tmpTargetPakFile.close()
        return errorFound

class pakFileEntry:
    """ Manages the fields of each contained file entry in the pak file
        there are five (5) fields describing a file entry
        From BgBennyBoy's MI Explorer code (thanks!) :
        DWORD fileDataPos;          (* + startOfData *)              Offsets are from the start of the file data section. MISE and MI2:SE
        DWORD fileNamePos;          (* + startOfFileNames *)         (????) In MI2:SE this is not correct. The offset is
        DWORD dataSize;
        DWORD dataSize2;            (* real size? (always =dataSize) *)
        DWORD compressed;           (* compressed? (always 0) *)
    """
    _orderInTheOrigFile = 0
    _fileDataPos = 0
    _fileNamePos = 0
    _dataSize = 0
    _dataSize2 = 0
    _compressed = 0

    def __init__(self, pFileDataPos, pFileNamePos, pDataSize, pDataSize2, pCompressed, pOrderInOrigFile = 0):
        self._orderInTheOrigFile = pOrderInOrigFile
        self._fileDataPos = pFileDataPos
        self._fileNamePos = pFileNamePos
        self._dataSize = pDataSize
        self._dataSize2 = pDataSize2
        self._compressed = pCompressed
        return


class pakHeader:
    """ From BgBennyBoy's MI Explorer code (thanks!) :
    DWORD magic;                (* KAPL -> "LPAK" *)
    Single version;
    DWORD startOfIndex;         (* -> 1 DWORD per file *)           // what do they mean?
    DWORD startOfFileEntries;   (* -> 5 DWORD per file *)
    DWORD startOfFileNames;     (* zero-terminated string *)
    DWORD startOfData;
    DWORD sizeOfIndex;
    DWORD sizeOfFileEntries;
    DWORD sizeOfFileNames;
    DWORD sizeOfData;
    """
    _lilEndianMagic = ""
    _version = 0
    _startOfIndex = 0
    _startOfFileEntries = 0
    _startOfFileNames = 0
    _startOfData =0
    _sizeOfIndex = 0
    _sizeOfFileEntries = 0
    _sizeOfFileNames = 0
    _sizeOfData = 0

    def __init__(self, pMagic, pVersion, pStartOfIndex, pStartOfFileEntries, pStartOfFileNames, pStartOfData, pSizeOfIndex, pSizeOfFileEntries, pSizeOfFileNames, pSizeOfData):
        self._lilEndianMagic = pMagic
        self._version = pVersion
        self._startOfIndex = pStartOfIndex
        self._startOfFileEntries = pStartOfFileEntries
        self._startOfFileNames = pStartOfFileNames
        self._startOfData = pStartOfData
        self._sizeOfIndex = pSizeOfIndex
        self._sizeOfFileEntries = pSizeOfFileEntries
        self._sizeOfFileNames = pSizeOfFileNames
        self._sizeOfData = pSizeOfData


#
#
# ########################
# main
# sys.argv[1] filename of original PAK file
# sys.argv[2] root folder of extracted (and modified files)
# eg. MI2:SE for validation:   monkeySERepaker "mi2se" "O:\Program Files (x86)\Steam\steamapps\common\monkey2\monkey2.pak" "O:\Program Files (x86)\Steam\steamapps\common\monkey2\extractedAllOrig"
# eg. MI2:SE for import repak: monkeySERepaker "mi2se" "O:\Program Files (x86)\Steam\steamapps\common\monkey2\monkey2.pak" "O:\Program Files (x86)\Steam\steamapps\common\monkey2\extractedAllOrigWithModifications"
# eg. MI:SE for validation:
# eg. MI:SE for import repak: monkeySERepaker "mise" "O:\Program Files (x86)\Steam\steamapps\common\the secret of monkey island special edition\monkey1.pak" "O:\Program Files (x86)\Steam\steamapps\common\the secret of monkey island special edition\extractedAllOrig"
# eg. MI:SE for import repak: monkeySERepaker "mise" "O:\Program Files (x86)\Steam\steamapps\common\the secret of monkey island special edition\monkey1.pak" "O:\Program Files (x86)\Steam\steamapps\common\the secret of monkey island special edition\extractedAllOrigWithModifications"
# #########################
#
if __name__ == "__main__":
    invalidSyntax = False
    if len(sys.argv) == 2:
        if(sys.argv[1] == '--help'or sys.argv[1] == '-h'):
            print "%s %s supports SoMI:SE and MI2:SE. (Tested with Steam version)." % (app_name_spaced, app_version)
            print "Created by Praetorian of the classic adventures in greek team for the purposes of the greek translation for the Special Editions of Monkey Island."
            print "Based on bgbennyboy's MISE Explorer."
            print "Always keep backups!"
            print "--------------------"
            print "Preparatory steps:"
            print "1. Use bgbennyboy's MISE Explorer to extract all files (raw) from the ORIGINAL monkey1.pak or monkey2.pak resource files in a \"extractedAllOrigWithModifications\" folder."
            print "2. Overwrite any resource files with modified ones as needed."
            print "--------------------"
            print "%s takes 3 mandatory arguments:" % (app_name_spaced)
            print "Valid syntax: %s [mise|mi2se] [original_PAK_filepath] [folderpath_for_extracted_and_modified_Files]" % (app_name)
            print "1rst argument is the game mode. Valid values are 'mise' or 'mi2se'"
            print "2nd argument is the path to the ORIGINAL pak file. Do not point to a modified pak file here."
            print "3rd argument is the path to the folder of extracted files."
            print "If the repaker finishes successfully a modded.pak file will be created in the same folder with the repaker tool."
            print "Copy this file to the game's installation directory and rename it appropriately (monkey1.pak or monkey2.pak)."
            print "Keep a backup of the original pak file, just in case."
            print "--------------------"
            print "Sample calls:"
            print "%s \"mise\" \"C:\\Program Files (x86)\\Steam\\steamapps\\common\\the secret of monkey island special edition\\monkey1.pak\" \"C:\\Program Files (x86)\\Steam\\steamapps\\common\\the secret of monkey island special edition\\extractedAllOrigWithModifications\"" % (app_name)
            print ""
            print "%s \"mi2se\" \"C:\\Program Files (x86)\\Steam\\steamapps\\common\\monkey2\\monkey2.pak\" \"C:\\Program Files (x86)\\Steam\\steamapps\\common\\monkey2\\extractedAllOrigWithModifications\"" % (app_name)
            print "Thank you for using this app."
            print "Please provide any feedback to: %s " % (company_email)
        elif(sys.argv[1] == '--version' or sys.argv[1] == '-v'):
            print "%s %s supports SoMI:SE and MI2:SE. (Tested with Steam version)." % (app_name_spaced, app_version)
            print "Please provide any feedback to: %s " % (company_email)
    elif len(sys.argv) ==  4:
#        TMPminSpaceBetweenLettersInRowLeftToLeft = int(sys.argv[4])
        if(sys.argv[1] == 'mise'):
            parseMode = 1
        elif((sys.argv[1] == 'mi2se')):
            parseMode = 2
        else:
            parseMode = -1
            invalidSyntax = True

        if not invalidSyntax:
            TMPoriginalPakFilename = sys.argv[2]
            TMProotFolderWithExtractedFiles = sys.argv[3]

            myOriginalPakInstance = pakFile(TMPoriginalPakFilename)

            if(myOriginalPakInstance._pakHeader != None):
                errorFound = myOriginalPakInstance.produceModdedPak(TMProotFolderWithExtractedFiles, parseMode)
                if errorFound :
                    print "Process was halted by unexpected errors during the re-packing! Failed to produce a valid pak."
            else:
                print "Process was halted by unexpected errors while attempting to read from the original pak file! Process Failed."
    #        myOriginalPakInstance.generateModFiles(TMPcustomBaseLineOffset)
    else:
        invalidSyntax = True

    if invalidSyntax == True:
        print "Invalid syntax\n Insufficient number of arguments (%d detected, 3 needed)\n Try: \n %s [mise|mi2se] [original_PAK_filepath] [folderpath_for_extracted_and_modified_Files] \n %s --help for more info \n %s --version for version info " % (len(sys.argv)-1 , app_name, app_name, app_name)
        tmpi = 0
        for tmpArg in sys.argv:
            if tmpi==0: #skip first argument
                tmpi+=1
                continue
            print "\nArgument: %s" % (tmpArg)
            tmpi+=1
else:
    ## debug
	#print '%s was imported from another module' % (app_name_spaced,)
    pass

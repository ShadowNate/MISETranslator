#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Created by Praetorian (ShadowNate) for Classic Adventures in Greek
# classic.adventures.in.greek@gmail.com
#
import os, sys, shutil
import Image
from struct import *
import re
import sqlite3

#
# Let's assume an Input image with only a row of letters (no double rows...)
#
#
# TO DO: make this adjustable!!!!
# TODO: Report the error when no more new letters fit !!!!
# TODO: Evaluate if we should keep greek hacks or do something more before 1rst public release

#v014:
## DONE check for existence of files opened (do we do this always?)
#v012:
## DONE: Make compatible with both games MI and MI2:SE! Get input from DB!

#
class grabberFromPNG:
    origEncoding = 'windows-1252'
    defaultTargetLang = "greek"
    defaultTargetEncoding = 'windows-1253' #greek
    defaultTargetEncodingUnicode = unicode(defaultTargetEncoding, 'utf-8')
    allOfGreekChars = "ΆΈΉΊΌΎΏΐΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΪΫάέήίΰαβγδεζηθικλμνξοπρςστυφχψωϊϋόύώ"
    targetEncoding = 'windows-1253'
    targetEncodingUnicode = unicode(targetEncoding, 'utf-8')
    overrideEncodingTextFile = u'overrideEncoding.txt'
    DBFileName = u'trampol.sqlite'
    relPath = u'.'
    DBFileNameAndRelPath = os.path.join(relPath,DBFileName)
    overrideEncodingFileRelPath = os.path.join(relPath,overrideEncodingTextFile)
    PNG_TABLE_STARTLINE_OFFSET = 0x4260 #both for MI:SE and MI2:SE # offset 0x4260 = decimal 16992
    SOMISE_GameID = 1
    MISE2_GameID = 2
    SOMISE_Desc= 'The Secret of the Monkey Island:SE'
    SOMISE_CodeName = 'SoMISE'
    MISE2_Desc= 'Monkey Island 2:SE'
    MISE2_CodeName= 'MI2SE'
    lettersInOriginalFontFileDict = {1: 0x9a, 2:0x9b}

    minSpaceBetweenLettersInRowLeftToLeft =0
    minSpaceBetweenLettersInColumnTopToTop = 0
    origFontFilename=""
    origFontPropertiesTxt = ""
    imageOriginalPNG=""
    imageRowFilePNG=""
    copyFontFileName=""
    copyFontPropertiesTxt = ""
    copyPNGFileName=""

    lettersFound = 0
    listOfBaselines = []
    listOfWidths = []
    listOfLetterBoxes = []
    ##
    ## FOR DB INIT PURPOSES!!!!
    ##
    overrideFailed = True
    targetLangOrderAndListOfForeignLettersStrUnicode = None
    targetLangOrderAndListOfForeignLettersStr = None
    # TODO: read from an override file if it exists. Filename should be overrideEncoding.txt (overrideEncodingTextFile)
    if os.access(overrideEncodingFileRelPath, os.F_OK) :
        ## debug
        #print "Override encoding file found: {0}.".format(overrideEncodingFileRelPath)
        overEncodFile = open(overrideEncodingFileRelPath, 'r')
        linesLst = overEncodFile.readlines()
        overEncodFile.close()
        if linesLst is None or len(linesLst) == 0:
            overrideFailed = True
        else:
            involvedTokensLst =[]
            for readEncodLine in linesLst:
                del involvedTokensLst[:]
                involvedTokensLst = re.findall("[^\t\n]+",readEncodLine )
                if len(involvedTokensLst) == 2:
                    try:
                        targetEncodingUnicode = unicode(involvedTokensLst[0], 'utf-8')
                        targetEncoding = unicode.encode("%s" % targetEncodingUnicode, origEncoding)
                        targetLangOrderAndListOfForeignLettersStrUnicode = unicode(involvedTokensLst[1], 'utf-8')
                        print targetLangOrderAndListOfForeignLettersStrUnicode
                        overrideFailed = False
                    except:
                        overrideFailed = True
                else:
                    overrideFailed = True
                break #only read first line
    else:
        ## debug
        #print "Override encoding file not found: {0}.".format(overrideEncodingFileRelPath)
        #print "To override the default encoding {0} use an override encoding file with two tab separated entries: encoding (ascii) and characters-list. Convert to UTF-8 without BOM and save. For example:".format(defaultTargetEncoding)
        #print "windows-1252\tABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        pass

    if overrideFailed:
        ## debug
        #print "Override encoding file FAILED. Initializing for {0}...".format(defaultTargetLang)
        targetEncoding = defaultTargetEncoding
        targetEncodingUnicode = defaultTargetEncodingUnicode
        targetLangOrderAndListOfForeignLettersStrUnicode = unicode(allOfGreekChars, 'utf-8')
        #print targetLangOrderAndListOfForeignLettersStrUnicode

    try:
        targetLangOrderAndListOfForeignLettersStr = unicode.encode("%s" % targetLangOrderAndListOfForeignLettersStrUnicode, targetEncoding)
    except:
        ## debug
        #print "Override encoding file FAILED. Initializing for {0}...".format(defaultTargetLang)
        targetEncoding = defaultTargetEncoding
        targetEncodingUnicode = defaultTargetEncodingUnicode
        targetLangOrderAndListOfForeignLettersStrUnicode = unicode(allOfGreekChars, 'utf-8')
        targetLangOrderAndListOfForeignLettersStr = unicode.encode("%s" % targetLangOrderAndListOfForeignLettersStrUnicode, targetEncoding)
        #print targetLangOrderAndListOfForeignLettersStrUnicode

    targetLangOrderAndListOfForeignLetters = list(targetLangOrderAndListOfForeignLettersStr)

    # this list could be loaded from an original file (or be preloaded for each game in the DB)
    # The empty slots assume that we can have only up to '0xFF' character (so only 1C0 total slots (empty and reserved) are avail in the file since it starts from 0x20 character)
    # up to (and not including) the 0x214 position
    GENERIC_listOfEmptySlotsForLetters = [  0x118,
                                    0x11A,
                                    0x11C,
                                    0x11E,
                                    0x120,
                                    0x122,
                                    0x126,
                                    0x128,
                                    0x12A,
                                    0x12C,
                                    0x12E,
                                    0x130,
                                    0x132,
                                    0x134,
                                    0x136,
                                    0x138,
                                    0x13A,
                                    0x13C,
                                    0x13E,
                                    0x140,
                                    0x142,
                                    0x144,
                                    0x146,
                                    0x14A,
                                    0x14E,
                                    0x150,
                                    0x152,
                                    0x154,
                                    0x156,
                                    0x158,
                                    0x15A,
                                    0x15E,
                                    0x160,
                                    0x162,
                                    0x164,
                                    0x166,
                                    0x168,
                                    0x16A,
                                    0x172,
                                    0x174,
                                    0x178,
                                    0x17A,
                                    0x17C,
                                    0x17E,
                                    0x180,
                                    0x182,
                                    0x184,
                                    0x186,
                                    0x188,
                                    0x18A,
                                    0x18C,
                                    0x192,
                                    0x194,
                                    0x196,
                                    0x19E,
                                    0x1A0,
                                    0x1B0,
                                    0x1B8,
                                    0x1BA,
                                    0x1C2,
                                    0x1C4,
                                    0x1C8,
                                    0x1CA,
                                    0x1D0,
                                    0x1D4,
                                    0x1D6,
                                    0x1E0,
                                    0x1FA,
                                    0x204,
                                    0x208,
                                    0x20A,
                                    0x214,
                                    0x216]

    # SOMI_SE support.
    SOMISE_listOfEmptySlotsForLetters = list(GENERIC_listOfEmptySlotsForLetters)
    # TODO: add a flage to only do this for greek (?) - double check for needed parts for other languages!
    # Hack(for greek) for resolving the bug for 173 pieces of eight untranslated line used directly from classic, we need to remove reserved letters for α, ά and ώ, (which were formelly as 93 96 and fe )
    # - or better yet put them in last empty positions (this is adopted here)
    idxTmp000 = SOMISE_listOfEmptySlotsForLetters.index(0x140)
    idxTmp001 = SOMISE_listOfEmptySlotsForLetters.index(0x184)
    SOMISE_listOfEmptySlotsForLetters.remove(0x184)
    SOMISE_listOfEmptySlotsForLetters.insert(idxTmp000, 0x184)
    SOMISE_listOfEmptySlotsForLetters.remove(0x140)
##    SOMISE_listOfEmptySlotsForLetters.insert(idxTmp001, 0x140)

    idxTmp000 = SOMISE_listOfEmptySlotsForLetters.index(0x146)
    idxTmp001 = SOMISE_listOfEmptySlotsForLetters.index(0x186)
    SOMISE_listOfEmptySlotsForLetters.remove(0x186)
    SOMISE_listOfEmptySlotsForLetters.insert(idxTmp000, 0x186)
    SOMISE_listOfEmptySlotsForLetters.remove(0x146)
##    SOMISE_listOfEmptySlotsForLetters.insert(idxTmp001, 0x146)

    ##idxTmp001 = SOMISE_listOfEmptySlotsForLetters.index(0x188)
    ##SOMISE_listOfEmptySlotsForLetters.insert(idxTmp001, 0x216)
    SOMISE_listOfEmptySlotsForLetters.remove(0x188)
    SOMISE_listOfEmptySlotsForLetters.remove(0x216)
    SOMISE_listOfEmptySlotsForLetters.append(0x188)  #because 0x216 was in the end

    # MISE2 support. It is essentially the same minus 2 slots that are now used (0x132 and 0x152)
    # TODO: rather than hardconding this, it could be (more safely) detected based on an original font file input!
    MISE2_listOfEmptySlotsForLetters = []
    for tmpI in range(0, len(GENERIC_listOfEmptySlotsForLetters)):
        MISE2_listOfEmptySlotsForLetters.append(GENERIC_listOfEmptySlotsForLetters[tmpI])
        #
        # remove(x).Removes the first item from the list whose value is x. It is an error if there is no such item
        # MI 2: SE has one additional character at PNG index 0x95 (and thus a total of 0x9B characters). This character is chr(0x8C)
        # Also the 'A0' Ascii char seems to be reserved for a blank char in MISE:2 so its spot (addr 0x15A) will be marked as reserved!
        # new: the '80' Ascii char  its spot (addr 0x11A
        # new: the 'C3' Ascii char  its spot (addr  0x1A0
        # new: the 'AA' Ascii char  its spot (addr 0x16E  # not in empty anyway
        # new: the 'A9' Ascii char  its spot (addr  0x16C # not in empty anyway
        # new: the 'E2' Ascii char  its spot (addr 0x1DE
        # new: the '9C' Ascii char  its spot (addr 0x152
        # new: the '8C' Ascii char  its spot (addr 0x132
        # new: the '94' Ascii char  its spot (addr 0x142
        # new: the '9D' Ascii char  its spot (addr 0x154

    MISE2_listOfEmptySlotsForLetters.remove(0x132)
    MISE2_listOfEmptySlotsForLetters.remove(0x15A)
    MISE2_listOfEmptySlotsForLetters.remove(0x152)
    #new
   # MISE2_listOfEmptySlotsForLetters.remove(0x11A) # not cut for now  -> euro sign to Ω τονος
   # MISE2_listOfEmptySlotsForLetters.remove(0x1A0) # not cut for now  ->  Γ
   # MISE2_listOfEmptySlotsForLetters.remove(0x16E) # not in empty anyway
   # MISE2_listOfEmptySlotsForLetters.remove(0x16C) # not in empty anyway
   # MISE2_listOfEmptySlotsForLetters.remove(0x1DE) # not in empty anyway
   # MISE2_listOfEmptySlotsForLetters.remove(0x152) # done
   # MISE2_listOfEmptySlotsForLetters.remove(0x132) # done
   # MISE2_listOfEmptySlotsForLetters.remove(0x142) # not cut for now   ->  ά
   # MISE2_listOfEmptySlotsForLetters.remove(0x154) # ->  ε tried to cut but then " appeared as ά in translation


    #
    # Only for png table indexes 0x00 <= x <= 0x99 (for MISE:2 it is for 0x00 <= x <= 0x9A)
    #
    replacePngIndexForOrigChars = []
    replacePngIndexForOrigChars.append(chr(0x7F)) # the special character in the start
    for i in range(0x01, 0x60):
        replacePngIndexForOrigChars.append(chr(i+0x1F))
    replacePngIndexForOrigChars.append(chr(0xA1)) # Png index 0x60 .other special characters following. Need latin encoding (Windows-1252) these ones!
    replacePngIndexForOrigChars.append(chr(0xA9)) # Png index 0x61 .
    replacePngIndexForOrigChars.append(chr(0xAA)) # Png index 0x62 .
    replacePngIndexForOrigChars.append(chr(0xAB)) # Png index 0x63 .
    replacePngIndexForOrigChars.append(chr(0xAE)) # Png index 0x64 .
    replacePngIndexForOrigChars.append(chr(0xB0)) # Png index 0x65 .
    replacePngIndexForOrigChars.append(chr(0xBB)) # Png index 0x66 .
    replacePngIndexForOrigChars.append(chr(0xBF)) # Png index 0x67 .
    replacePngIndexForOrigChars.append(chr(0xC0)) # Png index 0x68 .
    replacePngIndexForOrigChars.append(chr(0xC1)) # Png index 0x69 .
    replacePngIndexForOrigChars.append(chr(0xC4)) # Png index 0x6A .
    replacePngIndexForOrigChars.append(chr(0xC5)) # Png index 0x6B .
    replacePngIndexForOrigChars.append(chr(0xC6)) # Png index 0x6C .
    replacePngIndexForOrigChars.append(chr(0xC7)) # Png index 0x6D .
    replacePngIndexForOrigChars.append(chr(0xC8)) # Png index 0x6E .
    replacePngIndexForOrigChars.append(chr(0xC9)) # Png index 0x6F .
    replacePngIndexForOrigChars.append(chr(0xCA)) # Png index 0x70 .
    replacePngIndexForOrigChars.append(chr(0xCC)) # Png index 0x71 .
    replacePngIndexForOrigChars.append(chr(0xCD)) # Png index 0x72 .
    replacePngIndexForOrigChars.append(chr(0xCE)) # Png index 0x73 .
    replacePngIndexForOrigChars.append(chr(0xD1)) # Png index 0x74 .
    replacePngIndexForOrigChars.append(chr(0xD2)) # Png index 0x75 .
    replacePngIndexForOrigChars.append(chr(0xD3)) # Png index 0x76 .
    replacePngIndexForOrigChars.append(chr(0xD6)) # Png index 0x77 .
    replacePngIndexForOrigChars.append(chr(0xD9)) # Png index 0x78 .
    replacePngIndexForOrigChars.append(chr(0xDA)) # Png index 0x79 .
    replacePngIndexForOrigChars.append(chr(0xDC)) # Png index 0x7A .
    replacePngIndexForOrigChars.append(chr(0xDF)) # Png index 0x7B .
    replacePngIndexForOrigChars.append(chr(0xE0)) # Png index 0x7C .
    replacePngIndexForOrigChars.append(chr(0xE1)) # Png index 0x7D .
    replacePngIndexForOrigChars.append(chr(0xE2)) # Png index 0x7E .
    replacePngIndexForOrigChars.append(chr(0xE4)) # Png index 0x7F .
    replacePngIndexForOrigChars.append(chr(0xE5)) # Png index 0x80 .
    replacePngIndexForOrigChars.append(chr(0xE6)) # Png index 0x81 .
    replacePngIndexForOrigChars.append(chr(0xE7)) # Png index 0x82 .
    replacePngIndexForOrigChars.append(chr(0xE8)) # Png index 0x83 .
    replacePngIndexForOrigChars.append(chr(0xE9)) # Png index 0x84 .
    replacePngIndexForOrigChars.append(chr(0xEA)) # Png index 0x85 .
    replacePngIndexForOrigChars.append(chr(0xEB)) # Png index 0x86 .
    replacePngIndexForOrigChars.append(chr(0xEC)) # Png index 0x87 .
    replacePngIndexForOrigChars.append(chr(0xED)) # Png index 0x88 .
    replacePngIndexForOrigChars.append(chr(0xEE)) # Png index 0x89 .
    replacePngIndexForOrigChars.append(chr(0xEF)) # Png index 0x8A .
    replacePngIndexForOrigChars.append(chr(0xF1)) # Png index 0x8B .
    replacePngIndexForOrigChars.append(chr(0xF2)) # Png index 0x8C .
    replacePngIndexForOrigChars.append(chr(0xF3)) # Png index 0x8D .
    replacePngIndexForOrigChars.append(chr(0xF4)) # Png index 0x8E .
    replacePngIndexForOrigChars.append(chr(0xF6)) # Png index 0x8F .
    replacePngIndexForOrigChars.append(chr(0xF9)) # Png index 0x90 .
    replacePngIndexForOrigChars.append(chr(0xFA)) # Png index 0x91 .
    replacePngIndexForOrigChars.append(chr(0xFB)) # Png index 0x92 .
    replacePngIndexForOrigChars.append(chr(0xFC)) # Png index 0x93 .
    replacePngIndexForOrigChars.append(chr(0xFF)) # Png index 0x94 .
    #
    # MI 2: SE. See bellow note about additional character
    #
    replacePngIndexForOrigChars.append(chr(0x9C)) # Png index 0x95 .
    replacePngIndexForOrigChars.append(chr(0x83)) # Png index 0x96 .
    replacePngIndexForOrigChars.append(chr(0x97)) # Png index 0x97 .
    replacePngIndexForOrigChars.append(chr(0x85)) # Png index 0x98 .
    replacePngIndexForOrigChars.append(chr(0x99)) # Png index 0x99 .

    SOMISE_replacePngIndexForOrigChars = list(replacePngIndexForOrigChars)
    MISE2_replacePngIndexForOrigChars = []
    for tmpI in range(0, len(replacePngIndexForOrigChars)):
        MISE2_replacePngIndexForOrigChars.append(replacePngIndexForOrigChars[tmpI])
    # insert(i, x). The first argument is the index of the element before which to insert
    #
    # MI 2: SE has one additional character at PNG index 0x95 (and thus a total of 0x9B characters). This character is chr(0x8C)
    #
    MISE2_replacePngIndexForOrigChars.insert(0x95, chr(0x8C))
    ##
    ## END OF DB INIT CODE
    ##

##
## static function to get the tryEncoding (The suggested in the overrideEncoding or  the used encoding (after the suggested failed))
##
    def getTryEncoding(self):
        return self.targetEncoding

#
# TODO: warning: assumes that there is a margin on top and bellow the letters (especially on top; if a letter starts from the first pixel row, it might not detect it!) <---to fix
#
    def __init__(self, pselectedEncoding=None, pselectedGameID=None, porigFontFilename=None,  pimageOriginalPNG=None):
        self.minSpaceBetweenLettersInRowLeftToLeft = 0
        self.minSpaceBetweenLettersInColumnTopToTop = 0
        self.origFontFilename=porigFontFilename
        self.copyFontFileName=""
        self.copyPNGFileName=""
        self.imageOriginalPNG=pimageOriginalPNG
        self.imageRowFilePNG = ""
        self.baselineOffset = 0

        self.lettersFound = 0
        self.origFontPropertiesTxt = ""
        self.copyFontPropertiesTxt = ""
        self.cleanup() # for good practice (this should not be here, but it's here too due to quick/sloppy :) coding (TODO: fix it)
        #debug
        self.DBinit()

        if pselectedEncoding == None:
            pselectedEncoding = self.targetEncoding
        if pselectedGameID == None:
            pselectedGameID = self.SOMISE_GameID
        self.selectedGameID=pselectedGameID
        self.activeEncoding = pselectedEncoding
        self.lettersInOriginalFontFile = 0 #initialization

        # TODO: we should get from the DB the encoding and lettersString and the Empty slots for the selected Game and Calculcate the rest of the lists/dictionaries on the fly.
        # IF no lettersString or encoding has been defined... then issue error? or continue with hardcoded (insert to db as well and inform the GUI?)
        self.calcFromDB()
        return

    def calcFromDB(self):
        #
        # TODO: Inform of CRITICAL Error if not found! THEN EXIT????
        # TODO: DB initialization (Should happen once, not every time!)
        if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
            #debug
            print "CRITICAL ERROR: The database file %s could not be found!!" % (self.DBFileNameAndRelPath)
        else:
            conn = sqlite3.connect(self.DBFileNameAndRelPath)
            c = conn.cursor()

            # retrieval of the required values from the DB!
            c.execute('''select encoding, charString from langSettings''')
            foundSelectedEncoding = False
            retrievedEncoding= ""
            retrievedOrderAndListOfForeignLettersStr = ""
            for row in c:
                retrievedEncoding=unicode.encode("%s" % row[0],self.origEncoding)
                if self.activeEncoding == retrievedEncoding:
                    foundSelectedEncoding = True
                    break
            #TODO: prompt with ERROR. Revert to first found?
            if foundSelectedEncoding == False:
                #debug
                print "CRITICAL ERROR: No encoding was found in the DB, matching the selected one! Reverting to {0} encoding and {0} string".format(self.defaultTargetLang)
                self.activeEncoding = self.defaultTargetEncoding
                self.activeOrderAndListOfForeignLettersStr = self.targetLangOrderAndListOfForeignLettersStr
            else:
                self.activeEncoding = retrievedEncoding # reduntand but included for readability
                retrievedOrderAndListOfForeignLettersStr= unicode.encode("%s" % row[1], self.activeEncoding)
                if retrievedOrderAndListOfForeignLettersStr is None or retrievedOrderAndListOfForeignLettersStr.strip() == "":
                    #debug
                    print "CRITICAL ERROR: No valid string of characters was found in the DB for the selected encoding: {1}! Reverting to {0} encoding and {0} string!".format(self.defaultTargetLang, self.activeEncoding)
                    self.activeEncoding = self.defaultTargetEncoding
                    self.activeOrderAndListOfForeignLettersStr = self.targetLangOrderAndListOfForeignLettersStr
                else:
                    self.activeOrderAndListOfForeignLettersStr = retrievedOrderAndListOfForeignLettersStr
            # if there are any duplicate characters they should be removed!
            tmpListOfForeignLettersStrNew = ''.join([tmpC for i, tmpC in enumerate(self.activeOrderAndListOfForeignLettersStr) if not tmpC in self.activeOrderAndListOfForeignLettersStr[:i]])
            if len(list(tmpListOfForeignLettersStrNew)) != len(list(self.activeOrderAndListOfForeignLettersStr)):
                #debug
                print "CRITICAL ERROR: Duplicate Characters Found in the imported foreign char string! Duplicate characters were removed! Please use the new string now: %s!" % (tmpListOfForeignLettersStrNew)
            self.activeOrderAndListOfForeignLettersStr = tmpListOfForeignLettersStrNew
            #debug
            #print "Using encoding: %s and string: %s " % (self.activeEncoding, self.activeOrderAndListOfForeignLettersStr) #success!

            self.orderAndListOfForeignLetters = list(self.activeOrderAndListOfForeignLettersStr)

            foundSelectedGame = False
            self.supportedGames = {}
            c.execute("select ID, Name from supportedGames")
            for row in c:
                self.supportedGames[int(row[0])]=unicode.encode("%s" % row[1],self.origEncoding)
                if self.selectedGameID == int(row[0]):
                    foundSelectedGame = True
                    self.lettersInOriginalFontFile = int(self.lettersInOriginalFontFileDict[self.selectedGameID])
                    break
            if foundSelectedGame == False:
                #debug
                print "CRITICAL ERROR: The selected game was not found in the DB! Reverting to SoMI:SE!"
                self.selectedGameID = self.SOMISE_GameID
                self.lettersInOriginalFontFile = int(self.lettersInOriginalFontFileDict[self.SOMISE_GameID])
            #debug
            #print "Selected GameID: %d, Desc: %s, Letters in orig file: %d " % (self.selectedGameID, self.supportedGames[self.selectedGameID], self.lettersInOriginalFontFile)

            self.listOfEmptySlotsForLetters = []
            del self.listOfEmptySlotsForLetters[:]
            c.execute("select GameID, AuksonID, AddressDecimal from emptySlotsInFontInfoForLetters where GameID=? order by AuksonID", ("%d" % (self.selectedGameID),))
            for row in c:
                self.listOfEmptySlotsForLetters.append(int(row[2]))
            #debug
            #print "List of Empty Slots For Letters:"
            #print self.listOfEmptySlotsForLetters
            #print "Empty Slots: %d" % len(self.listOfEmptySlotsForLetters)

            #print "Total foreign letters: %d" % (len(self.orderAndListOfForeignLetters))
            #print "Total new letters that can be added are %d for %s!" % (len(self.listOfEmptySlotsForLetters), self.supportedGames[self.selectedGameID])
            if len(self.listOfEmptySlotsForLetters) < len(self.orderAndListOfForeignLetters) :
                #debug
                print "CRITICAL ERROR: There are not enough slots to support all of the imported foreign characters! The list of new characters will be truncated to %d characters" % (len(self.listOfEmptySlotsForLetters))
                self.orderAndListOfForeignLetters = self.orderAndListOfForeignLetters[:len(self.listOfEmptySlotsForLetters)]
                #debug
                print "Please use the new string now: %s" % ''.join(self.orderAndListOfForeignLetters)

            self.replacePngIndexForOrigChars = []
            del self.replacePngIndexForOrigChars[:]
            c.execute("select GameID, IndxPngCharTable, OrigAsciiCharWin1252 from pngIndexForOriginalChars where GameID=? order by IndxPngCharTable", ("%d" % (self.selectedGameID) , ))
            for row in c:
                self.replacePngIndexForOrigChars.append(chr(int(row[2])))
##                print chr(int(row[2]))

            self.bringPngIndexForOrigChar = dict(zip(self.replacePngIndexForOrigChars, range(0, len(self.replacePngIndexForOrigChars) -1)) )
            ##print "bringPnhIndexForOrigchar"
            ##print self.bringPngIndexForOrigChar
            #debug
            #print "List of PNG Index Chars:"
            #print self.replacePngIndexForOrigChars
            #print "PNG Index items: %d" % len(self.replacePngIndexForOrigChars)

            #
            # Calculate expected positions of the foreign added chars, based on their ascii value. If conflict with existing character, then assign an empty slot from elsewhere (from available ones).
            #
            # Ordered list with the addresses where the FOREIGN letters will be put in the info file (this is used bellow in the creation of the dictionary dictOfOffsetsToValuesForForeignLettersToWrite)
            #
            self.listOfOffsetsForForeignLetters = []
            del self.listOfOffsetsForForeignLetters[:]
            expectedAddrInFontFile = 0
            for tmpI in range (0, len(self.orderAndListOfForeignLetters)):
                expectedAddrInFontFile = ((ord(self.orderAndListOfForeignLetters[tmpI]) - 0x20 ) * 2 + 0x5A)
                if (expectedAddrInFontFile in self.listOfEmptySlotsForLetters) and (expectedAddrInFontFile not in self.listOfOffsetsForForeignLetters):
                    self.listOfOffsetsForForeignLetters.append(expectedAddrInFontFile)
                else:
                    newAddrDueToConflict = 0
                    for tmpJ in range(0, len(self.listOfEmptySlotsForLetters)):
                        if self.listOfEmptySlotsForLetters[tmpJ] not in self.listOfOffsetsForForeignLetters:
                            newAddrDueToConflict = self.listOfEmptySlotsForLetters[tmpJ]
                            self.listOfOffsetsForForeignLetters.append(newAddrDueToConflict)
                            break
                    if newAddrDueToConflict==0:
                        # TODO: Report this critical error in the GUI!!!
                        print "Error! Sorry, could not fit any more letters in the font file! Total letters that can be added are %d!" % len(self.listOfEmptySlotsForLetters)


        #   from: decimal address in font file for the greek chars (addresses for the table of pointers to the png table) To -> hex index of PNG records table,  (int(dec) to int (hex))
        #   A "Should have been" address can be calculated by the [greek letter ascii hex value, (A) minus the starting ascii char (0x20) ] * 2 + 0x54 (the absolute position of the 0x20 char in the file).
        #   But: the "should have been" address MAY (often) collide with an existing foreign language or special char that was set in the original font file.
        #   In those cases the sould have been address switches to the first available address (there is a number of those in the file). (they can be found automatically, but an original file should be always supplied).
        #   (or supplied once and then the info is saved and restored from the DB for the whole game (!)
            self.dictOfOffsetsToValuesForForeignLettersToWrite = dict(zip(self.listOfOffsetsForForeignLetters, range(self.lettersInOriginalFontFile, self.lettersInOriginalFontFile + len(self.listOfOffsetsForForeignLetters))))

            #Not Used here but necessary for translation (from greek char (ASCII Hex) to special replacement char order (hex int).):
            # automatically calculated
            self.replaceAsciiIndexWithValForTranslation = dict(zip(self.orderAndListOfForeignLetters, (list (( (k - 0x1C)/2)+1 for k in self.listOfOffsetsForForeignLetters))))
            #
            # The reverse is ALSO needed (auxiliary):
            #
            self.rev_replaceAsciiIndexWithValForTranslation = dict((v, k) for k,v in self.replaceAsciiIndexWithValForTranslation.iteritems())

            self.rev_replaceAsciiIndexWithValForTranslation_FOR_DIALOGUE_FILE = dict((pack('B',v), ord(k)) for k,v in self.replaceAsciiIndexWithValForTranslation.iteritems())

            #
            # The sort-of reverse is ALSO needed. A dictionary from index of table (for png positioning) to corresponding ascii letter. Needs rev_replaceAsciiIndexWithValForTranslation to be applied to the value!!!
            # Only for png table indexes > 0x9A
            self.rev_replacePngIndexWithCorrAsciiChar = dict((v ,  ((k - 0x1C)/2)+1)  for k,v in self.dictOfOffsetsToValuesForForeignLettersToWrite.iteritems())
            for myIterKey, corrValue in self.rev_replacePngIndexWithCorrAsciiChar.iteritems():
        #        print "key: %d value: %d" % (myIterKey, corrValue)
                self.rev_replacePngIndexWithCorrAsciiChar[myIterKey] = self.rev_replaceAsciiIndexWithValForTranslation[corrValue]


            # Save (commit) any changes # probably select queries do not need commit.
            conn.commit()
            # Close the cursor
            c.close()
        return

    # TODO: The code here is mainly for test purposes. Should be cleaned up and keep what is needed if anything.
    def DBinit(self):
        #
        # TODO: Inform of Error if not found!
        ## DEBUG
        #print "Initializing DB..."
        if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
            #debug
            print "CRITICAL ERROR: The database file %s could not be found!!" % (self.DBFileNameAndRelPath)
        else:
            # TODO: DB initialization (Should happen once, not every time!)
            conn = sqlite3.connect(self.DBFileNameAndRelPath)
            c = conn.cursor()

            #
            # Fill in the supportedGames table in the DB
            #
            c.execute('''delete from supportedGames''')
            # put both MI SE games
            c.execute("""insert into supportedGames(ID, Name, CodeName) values(?,?,?)""", (self.SOMISE_GameID, self.SOMISE_Desc, self.SOMISE_CodeName))
            c.execute("""insert into supportedGames(ID, Name, CodeName) values(?,?,?)""", (self.MISE2_GameID, self.MISE2_Desc, self.MISE2_CodeName))
            conn.commit()
            #
            # Fill in the encoding and language string in the DB
            #
            c.execute('''delete from langSettings''')
            # put at least the greek encoding and string in the table
#            print self.targetLangOrderAndListOfForeignLettersStrUnicode
            c.execute("""insert into langSettings(encoding, charString) values(?,?)""", (self.targetEncodingUnicode, self.targetLangOrderAndListOfForeignLettersStrUnicode))
            conn.commit()
            #
            # Copy empty slots into the DB for SoMI:SE  and MI2:SE
            # clear the table first
            # Then insert the values in order
            ## debug
            #print "MI:SE empty slots: %d, MI2:SE empty slots: %d," % (len(self.SOMISE_listOfEmptySlotsForLetters), len(self.MISE2_listOfEmptySlotsForLetters))
            c.execute('''delete from emptySlotsInFontInfoForLetters''')
            for tmpL in range(0, len(self.SOMISE_listOfEmptySlotsForLetters)):
                c.execute("""insert into emptySlotsInFontInfoForLetters(GameID, AuksonID, AddressDecimal) values(?,?,?)""", (self.SOMISE_GameID,tmpL,self.SOMISE_listOfEmptySlotsForLetters[tmpL]))
            for tmpL in range(0, len(self.MISE2_listOfEmptySlotsForLetters)):
                c.execute("""insert into emptySlotsInFontInfoForLetters(GameID, AuksonID, AddressDecimal) values(?,?,?)""", (self.MISE2_GameID,tmpL,self.MISE2_listOfEmptySlotsForLetters[tmpL]))
            # Save (commit) the changes
            conn.commit()

            #
            # TODO: Fill in the tables that connect the original characters (ascii values) to the PNG table indexes
            # For Somi:SE and MI2:SE
            c.execute('''delete from pngIndexForOriginalChars''')
            for tmpL in range(0, len(self.SOMISE_replacePngIndexForOrigChars)):
                c.execute("""insert into pngIndexForOriginalChars(GameID, IndxPngCharTable, OrigAsciiCharWin1252) values(?,?,?)""", (self.SOMISE_GameID,tmpL,ord(self.SOMISE_replacePngIndexForOrigChars[tmpL])))
            for tmpL in range(0, len(self.MISE2_replacePngIndexForOrigChars)):
                c.execute("""insert into pngIndexForOriginalChars(GameID, IndxPngCharTable, OrigAsciiCharWin1252) values(?,?,?)""", (self.MISE2_GameID,tmpL,ord(self.MISE2_replacePngIndexForOrigChars[tmpL])))
            # Save (commit) the changes
            conn.commit()
            # Close the cursor
            c.close()
        return
##    def resetMe(self,  pminSpaceBetweenLettersInRowLeftToLeft,  pminSpaceBetweenLettersInColumnTopToTop,  porigFontFilename,  pimageOriginalPNG,  pimageRowFilePNG):
##        self.minSpaceBetweenLettersInRowLeftToLeft =pminSpaceBetweenLettersInRowLeftToLeft
##        self.minSpaceBetweenLettersInColumnTopToTop = pminSpaceBetweenLettersInColumnTopToTop
##        self.origFontFilename=porigFontFilename
##        self.copyFontFileName=""
##        self.copyPNGFileName=""
##        self.origFontPropertiesTxt = ""
##        self.copyFontPropertiesTxt = ""
##        self.imageOriginalPNG=pimageOriginalPNG
##        self.imageRowFilePNG = pimageRowFilePNG
##        self.cleanup()

    def cleanup(self):
        self.lettersFound = 0
        del self.listOfBaselines[:]
        del self.listOfWidths[:]
        del self.listOfLetterBoxes[:]
        self.origFontPropertiesTxt = ""
        self.copyFontPropertiesTxt = ""
        return

##
## SETTERS
##
    def setDasOrigFontFilename(self, pOrigFontFilename):
        self.origFontFilename=pOrigFontFilename
        return
    def setImageOriginalPNG(self, pimageOriginalPNG):
        self.imageOriginalPNG=pimageOriginalPNG
        return
    def setImageRowFilePNG(self, pimageRowFilePNG):
        self.imageRowFilePNG = pimageRowFilePNG
        return
    def setMinSpaceBetweenLettersInRowLeftToLeft(self, pminSpaceBetweenLettersInRowLeftToLeft):
        self.minSpaceBetweenLettersInRowLeftToLeft = pminSpaceBetweenLettersInRowLeftToLeft
        return
    def setMinSpaceBetweenLettersInColumnTopToTop(self, pminSpaceBetweenLettersInColumnTopToTop):
        self.minSpaceBetweenLettersInColumnTopToTop = pminSpaceBetweenLettersInColumnTopToTop
        return
##    def setBaseLineOffset(self, pcustomBaseLineOffset):
##        self.baselineOffset = pcustomBaseLineOffset
##        return
    def setCopyFontFileName(self, pcopyFontFileName):
        ##
        ## TODO: check if it IS derived as it should from the original file name that SHOULD also be defined!!!
        ##
        self.copyFontFileName = pcopyFontFileName
        return
    def setCopyPNGFileName(self, pcopyPNGFileName):
        ##
        ## TODO: check if it IS derived as it should from the original file name that SHOULD also be defined!!!
        ##
        self.copyPNGFileName = pcopyPNGFileName
        return

    def setGameID(self, pselGameID):
        self.selectedGameID= pselGameID
        return

    def setActiveEncoding(self, ptryEncoding):
        self.activeEncoding = ptryEncoding
        return
##
## END OF SETTERS
##
    def getImagePropertiesInfo(self, boolOrigFile):
        activeImageFile = None
        retText = ""
        if boolOrigFile == True:
            ## open the original file
            if os.access(self.imageOriginalPNG, os.F_OK) :
                try:
                    activeImageFile = Image.open(self.imageOriginalPNG)
                    self.origFontPropertiesTxt = "%dx%dx%s" % (activeImageFile.size[0],activeImageFile.size[1], activeImageFile.mode)
                    retText = self.origFontPropertiesTxt
                except:
                    errorFound = True
            else:
                errorFound = True
        else:
            ## open the created extended file
            if os.access(self.copyPNGFileName, os.F_OK) :
                try:
                    activeImageFile = Image.open(self.copyPNGFileName)
                    self.copyFontPropertiesTxt = "%dx%dx%s" % (activeImageFile.size[0],activeImageFile.size[1], activeImageFile.mode)
                    retText = self.copyFontPropertiesTxt
                except:
                    errorFound = True
            else:
                errorFound = True
        return retText

    def parseImage(self,  loadedImag, imwidth, imheight, trimTopPixels=0, trimBottomPixels =0):
        """ parsing image and deleting letters (we are not writing back)
        """
        prevColStartForLetter = 0
        prevRowStartForLetter = 0
        startCol = 0
        startRow = 0
        endCol = 0
        endRow = 0
        for x in range(0, imwidth):
            if startCol != 0:
                break
            for y in range(0, imheight):
                r1,g1,b1,a1 = loadedImag[x, y]
                if a1 != 0:
    #                print loadedImag[x, y]
                    if prevColStartForLetter == 0:
                        prevColStartForLetter = x
                        prevRowStartForLetter = y
                        startCol = x
    #                    print "Letter found"
    #                    print "start col:%d" % startCol
    # #                    print "hypothe row:%d" % y
    #                    # ksekinwntas apo to prwto row ths eikonas (to do optimize), kanoume parse kata rows gia na broume to top shmeio tou grammatos (row)
     #                   for y2 in range(0, y+1):
                        tmpSum = y + self.minSpaceBetweenLettersInColumnTopToTop
                        scanToRow = imheight
                        if scanToRow < imheight:
                            scanToRow = tmpSum
                        for y2 in range(0, scanToRow):
                            if startRow != 0:
                                break
                            tmpSum = startCol + self.minSpaceBetweenLettersInRowLeftToLeft
                            scanToCol = imwidth
                            if tmpSum < imwidth:
                                scanToCol = tmpSum
                            #print (startCol, scanToCol)
                            for x2 in range(startCol, scanToCol):
                                #print loadedImag[x2, y2]
                                r2,g2,b2,a2 = loadedImag[x2, y2]
                                if a2 != 0 and startRow == 0:
                                    startRow = y2 + trimTopPixels
    #                                print "start row: %d" % startRow
                                    break
        if startCol > 0 and startRow > 0:
            tmpSum = startRow + self.minSpaceBetweenLettersInColumnTopToTop
            scanToRow = imheight
            if tmpSum < imheight:
               scanToRow = tmpSum
            tmpSum = startCol + self.minSpaceBetweenLettersInRowLeftToLeft
            scanToCol = imwidth
            if tmpSum < imwidth:
               scanToCol = tmpSum
            for y in range(startRow, scanToRow):
                for x in range(startCol, scanToCol):
                    r1,g1,b1,a1 = loadedImag[x, y]
                    if a1 != 0:
                        endRow = y
            if endRow > 0:
                endRow = endRow - trimBottomPixels
    #        print "end row:% d" %endRow

        if startCol > 0 and startRow > 0 and endRow > 0:
            tmpSum = startCol + self.minSpaceBetweenLettersInRowLeftToLeft
            scanToCol = imwidth
            if tmpSum < imwidth:
               scanToCol = tmpSum
            for x in range(startCol, scanToCol):
                for y in range(startRow, endRow+1):
                    r1,g1,b1,a1 = loadedImag[x, y]
                    #print  loadedImag[x, y]
                    if a1 != 0:
                        endCol = x
    #        print "end col:% d" %endCol
        if startCol > 0 and startRow > 0 and endRow > 0 and endCol > 0:
            # append deducted baseline
            self.listOfBaselines.append(endRow)
            self.listOfWidths.append(endCol-startCol)
            self.listOfLetterBoxes.append((startCol, startRow, endCol, endRow))
            #delete the letter
            for x in range(startCol, endCol+1):
                for y in range(startRow - trimTopPixels, endRow+1 + trimBottomPixels):
                   loadedImag[x, y] = 0, 0, 0, 0
            return 0
        else: return -1
#
#
#
    def getExpectedFileNameForOutputPNG(self):
        strRet = ""
        if self.imageOriginalPNG <> "":
            file, ext = os.path.splitext(self.imageOriginalPNG)
            strRet = file + "Expanded"+ext
        return strRet
#
#
#
    def getExpectedFileNameForOutputINFO(self):
        strRet = ""
        if self.origFontFilename <> "":
            origFontFilenameParts = str.rpartition(str(self.origFontFilename), '.')
            strRet= origFontFilenameParts[0] + "_1" + origFontFilenameParts[1] + origFontFilenameParts[2]
        return strRet
#
#   CAREFUL: this method needs properties  minSpaceBetweenLettersInRowLeftToLeft and minSpaceBetweenLettersInColumnTopToTop to be set,in order to detect the baseline!
#
    def findDetectedBaseline(self):

        pDetectedBaseline = 0
        firstTableLineOffset = self.PNG_TABLE_STARTLINE_OFFSET
        #
        # ANOIGMA TOU .FONT ARXEIOU GIA NA BRW TO pDetectedBaseline
        #
        if os.access(self.origFontFilename, os.F_OK) :
            try:
                origFontFile = open(self.origFontFilename, 'rb')
                origFontFile.seek(firstTableLineOffset)
                tmpIntReadTuple = unpack('h',origFontFile.read(2))    # unpack always returns a tuple
                getFirstOrigLetterBox_LeftCol = tmpIntReadTuple[0]-1
                tmpIntReadTuple = unpack('h',origFontFile.read(2))    # unpack always returns a tuple
                getFirstOrigLetterBox_TopRow =  tmpIntReadTuple[0]-1
                tmpIntReadTuple = unpack('h',origFontFile.read(2))    # unpack always returns a tuple
                getFirstOrigLetterBox_RightCol =  tmpIntReadTuple[0]-1
                tmpIntReadTuple = unpack('h',origFontFile.read(2))    # unpack always returns a tuple
                getFirstOrigLetterBox_BottRow =  tmpIntReadTuple[0]-1
                origFontFile.close()
            except:
                errorFound = True
                return pDetectedBaseline
        else:
            errorFound = True
            return pDetectedBaseline
        ##debug
        #print getFirstOrigLetterBox_LeftCol, getFirstOrigLetterBox_TopRow, getFirstOrigLetterBox_RightCol, getFirstOrigLetterBox_BottRow
        # open original png image to figure the baseline from the first character
        if os.access(self.imageOriginalPNG, os.F_OK) :
            try:
                im = Image.open(self.imageOriginalPNG)
                w1, h1 = im.size
                pix = im.load()
                if self.parseImage(pix, getFirstOrigLetterBox_RightCol,  getFirstOrigLetterBox_BottRow) == 0:
                    pDetectedBaseline =  self.listOfBaselines[0] + 1
            except:
                errorFound = True
                return pDetectedBaseline
        else:
            errorFound = True
            return pDetectedBaseline
        return pDetectedBaseline

    def getActiveEncoding(self):
        return self.activeEncoding

    def getSelectedGameID(self):
        return self.selectedGameID

#
#   This method is independent from properties of the object.
#
    def findTotalAndImportedChars(self, pFontFilename):
        lettersInOriginalFontFile = self.lettersInOriginalFontFile
        totalCharactersInInfoFile = 0
        importedCharactersInInfoFile = 0

        if os.access(pFontFilename, os.F_OK) :
            try:
                tmpFontFile = open(pFontFilename, 'rb')
                # read the 4rth byte with the number of entries in the table indexing the png (starting from offset PNG_TABLE_STARTLINE_OFFSET)
                tmpFontFile.seek(4)
                tmpSizeOfTableWithFontsIndexedToImage = unpack('B',tmpFontFile.read(1))
                totalCharactersInInfoFile =  tmpSizeOfTableWithFontsIndexedToImage[0]
                tmpFontFile.close()
                importedCharactersInInfoFile = totalCharactersInInfoFile - lettersInOriginalFontFile
                return (totalCharactersInInfoFile, importedCharactersInInfoFile)
            except:
                errorFound = True
                return (0,0)
        else:
            errorFound = True
            return (0,0)

#
#
#
    def generateModFiles(self, customBaselineOffs):
        """ Generate extended png and font files (work on copies, not the originals). Return values: 0 no errors, -1 output font file has alrady new letters, -2 no fonts found in png (TODO: more error cases)
        """
        #
        # When a customBaselineOffs is set, we should expand the space for the letter (otherwise it will be overflown in the next line or truncated (outside the png)
        # We can't expand the space for the letter downwards, because the engine will (com)press the new height to fit its expected and it will look bad.
        # NO THAT WON'T WORK--> The font will remain in the wrong place: Should we  CUT from the top and hope that we don't trunctate!? Keeping the resulting height equal to the expected one?
        # MAYBE: Do not alter the baseline of the original file, but the detected (popular) one of the line file!!!
        retVal = 0
        totalFontLetters = 0
        importedNumOfLetters = 0
        errMsg = ""
        errorFound = False
        im = None
        #
        # CONSTANTS
        #
        origGameFontDiakenoHeight = 0
        interLetterSpacingInPNG = 4
        origGameFontSizeEqBaseLine = 0
        # offset for start of PNG index table
        firstTableLineOffset = self.PNG_TABLE_STARTLINE_OFFSET
        lettersInOriginalFontFile = self.lettersInOriginalFontFile
        #
        # detection of origGameFontSizeEqBaseLine
        #
        origGameFontSizeEqBaseLine = self.findDetectedBaseline()
        self.cleanup() # necessary after detection of baseline, because it fills up some of the  lists used in the following!

        self.origFontPropertiesTxt = self.getImagePropertiesInfo(True) # "%dx%dx%s" % (im.size[0],im.size[1], im.mode)
#        print "WEEEE::: ", self.imageOriginalPNG, im.format, "%dx%d" % im.size, im.mode        print "BASELINE DETECTED:%d " % origGameFontSizeEqBaseLine

        #
        # ANOIGMA THS EIKONAS ME TH GRAMMH TWN XARAKTHRWN PROS IMPORT
        #
        if os.access(self.imageRowFilePNG, os.F_OK) :
            try:
                im = Image.open(self.imageRowFilePNG)
            except:
                errMsg = "No letters were found in input png!"
                print errMsg
                retVal = -2
                errorFound = True
        else:
            errMsg = "No letters were found in input png!"
            print errMsg
            retVal = -2
            errorFound = True
        if not errorFound:
            #debug
            #print self.imageRowFilePNG, im.format, "%dx%d" % im.size, im.mode
            w1, h1 = im.size
            trimTopPixels = 0
            trimBottomPixels = 0
            italicsMode = False   # will be set to true only if the prefic of the row file is itcrp_ or it_ in order to activate some extra settings for kerning and letter width!

            filepathSplitTbl = os.path.split(self.imageRowFilePNG)
            sFilenameOnlyImageRowFilePNG = filepathSplitTbl[1]

            if sFilenameOnlyImageRowFilePNG.startswith("itcrp_") or sFilenameOnlyImageRowFilePNG.startswith("it_"):
                italicsMode = True

            if sFilenameOnlyImageRowFilePNG.startswith("itcrp_"):
                trimTopPixels = 1
                trimBottomPixels = 1
                print "Will trim upper line by %d pixels and bottom line by %d pixels" % (trimTopPixels, trimBottomPixels)
            pix = im.load()
            while self.parseImage(pix, w1, h1, trimTopPixels, trimBottomPixels) == 0:
                self.lettersFound=  self.lettersFound+1
        #    print self.listOfBaselines
            #debug
            #print "%d" % self.lettersFound
            if self.lettersFound > 0 :

                #
                # open file binary mode and read: number of entries original in table, then read final line and get value of endingrow pixel (-1 of what is written in the .font)
                #
                origFontFile = None
                if os.access(self.origFontFilename, os.F_OK) :
                    try:
                        origFontFile = open(self.origFontFilename, 'rb')
                    except:
                        errorFound = True
                else:
                    errorFound = True
                if not errorFound:
                    # read the 4rth byte with the number of entries in the table indexing the png (starting from offset self.PNG_TABLE_STARTLINE_OFFSET)
                    origFontFile.seek(4)
                    tmpSizeOfTableWithFontsIndexedToImage = unpack('B',origFontFile.read(1))
                    existingSizeOfTableInOrigImage =  tmpSizeOfTableWithFontsIndexedToImage[0]
                    if existingSizeOfTableInOrigImage == lettersInOriginalFontFile : # 0x9a or 0x9b
        ##                # offset self.PNG_TABLE_STARTLINE_OFFSET
        ##                firstTableLineOffset = 16992
                        origFontFile.seek(firstTableLineOffset + 6)
                        tmpFirstRowEnd = unpack('h',origFontFile.read(2))    # unpack always returns a tuple
                        origGameFontDiakenoHeight = tmpFirstRowEnd[0]
                        lastTableLineOffset = firstTableLineOffset +  (existingSizeOfTableInOrigImage -1 )* 16      #teleutaia grammi
                        origFontFile.seek(lastTableLineOffset + 6)
                        tmpLastPixelRowOfOrigImage = unpack('h',origFontFile.read(2))    # unpack always returns a tuple
                        pixHeightToBeginAppend = tmpLastPixelRowOfOrigImage[0]           # this is actually the next line pixel after the end of the previous line (but the font file indexes pixels with a +1 as it starts from 1,1 not 0,0)
                #        print origGameFontDiakenoHeight, pixHeightToBeginAppend
                        #
                        # FOR ITALICS MODE, GET SOME FEATURES OF SPECIFIC LETTERS
                        #
                        specificLetterPrototypes = ('y', 'i', 'u', 'B', 'O', 'I', 'T', 'o', 't', 'p', 'g')
                        specificLetterPrototypesToFeaturesDict = dict((k, (0,0,0)) for k in specificLetterPrototypes)
                        print specificLetterPrototypesToFeaturesDict

                        for idxe in range(0,len(specificLetterPrototypes)):
                            orderInPNG = self.bringPngIndexForOrigChar[ specificLetterPrototypes[idxe] ]  # works only for original letters
                            jOrigIndent = 0
                            jOrigWidth = 0
                            jOrigKern = 0
                            # Get features of j (which is in PNG TABLE order 76 -1 = 75)
                            #
                            origFontFile.seek(firstTableLineOffset + orderInPNG * 0x10 + 8 )
                            tmpPixelsWithinLetterBoxFromLeftToLetter = unpack('h',origFontFile.read(2))    # unpack always returns a tuple
                            tmpWidthLetter = unpack('h',origFontFile.read(2))    # unpack always returns a tuple
                            tmpKerningLetter = unpack('h',origFontFile.read(2))    # unpack always returns a tuple
                            jOrigIndent = tmpPixelsWithinLetterBoxFromLeftToLetter[0]
                            jOrigWidth = tmpWidthLetter[0]
                            jOrigKern = tmpKerningLetter[0]
                            tmpMyList = (jOrigIndent, jOrigWidth, jOrigKern)
                            specificLetterPrototypesToFeaturesDict.update({ specificLetterPrototypes[idxe]: tmpMyList});
                        print specificLetterPrototypesToFeaturesDict


                        origFontFile.close()
                        #
                        # open original font image (We won't write on it. but in a copy with an Expanded string at the end of the filename
                        imOrigGameFont = None
                        if os.access(self.imageOriginalPNG, os.F_OK) :
                            try:
                                imOrigGameFont = Image.open(self.imageOriginalPNG)
                            except:
                                errorFound = True
                        else:
                            errorFound = True
                        if not errorFound:

                            # calculate newHeight if need change
                            extra_neededRows = 1 #at least one!
                            tmpWidthMeasurement = interLetterSpacingInPNG
                            minRowTop = max(self.listOfBaselines)
                            for (c_startCol, c_startRow, c_endCol, c_endRow) in self.listOfLetterBoxes[0:]:
                                tmpWidthMeasurement += (c_endCol-c_startCol + 1) + interLetterSpacingInPNG
            ##                    print "tmpWidthMeasurement: %d " % (tmpWidthMeasurement)
                                if tmpWidthMeasurement >= imOrigGameFont.size[0]:
                                    extra_neededRows += 1
                                    tmpWidthMeasurement = interLetterSpacingInPNG + (c_endCol-c_startCol + 1) + interLetterSpacingInPNG #begin with the current letter
                                if minRowTop > c_startRow : minRowTop = c_startRow
                            tmpListOfDistinctBaselines = []
                            #
                            # find most popular baseline and adopt it
                            #
                            for i in self.listOfBaselines[0:]:
                                try:
                                    if tmpListOfDistinctBaselines.count(i) == 0:
                                        tmpListOfDistinctBaselines.append(i)
                                except:
                                    pass
                    #        print tmpListOfDistinctBaselines
                            popularBaselineCount = 0
                            popularBaseline = 0
                            for i in tmpListOfDistinctBaselines[0:]:
                                if self.listOfBaselines.count(i) > popularBaselineCount:
                                    popularBaselineCount = self.listOfBaselines.count(i)
                                    popularBaseline = i
                            #debug
                            #print "Baseline Index Popular: %d by count: %d" % (popularBaseline,popularBaselineCount)
                            customPopularBaseline = popularBaseline + customBaselineOffs ##new
            #                normalizedPopularBaseLine = popularBaseline - minRowTop ##old
                            normalizedPopularBaseLine = customPopularBaseline - minRowTop ##new

                            # TO DO: handle case where the png file already HAS space for extra letters and does not need CANVAS expansion, or needs less expansion than greedily calculated
                            #       we need to consult the .font file for this. (see until which row it is filled with letters, compare with the size[1] (height), calculate how many rows can be afforded without canvas expansion
                            #       and add (if necessary) remainder of rows.

                            # yparxoun arxeia me mono to TM char sthn teleutaia grammi opote kanoun perikopi sto ypsos. DEN TO 8ELOUME AUTO!
                            norm_OrigGameFontHeight = 0
                            if int(imOrigGameFont.size[1]) % int(origGameFontDiakenoHeight) > 0 :
                                norm_OrigGameFontHeight = int(origGameFontDiakenoHeight) * (int( int(imOrigGameFont.size[1])/ int(origGameFontDiakenoHeight)) +1)
                            else:
                                norm_OrigGameFontHeight = imOrigGameFont.size[1]

                            freeLinesInOriginalFile = int((norm_OrigGameFontHeight - pixHeightToBeginAppend) / origGameFontDiakenoHeight)  ## old
                            if freeLinesInOriginalFile < 0 :
                                print "freeLinesInOriginalFile before zeroing: %d" % freeLinesInOriginalFile
                                extra_neededRows += (-1)* freeLinesInOriginalFile # for case of the missing letters in Mi2:SE () TODO: if the problem is only this file, we could specifically set the filename in the condition to increase the extra_needed_rows.
                                freeLinesInOriginalFile = 0 # was here before
                            #debug
                            print "freeLinesInOriginalFile: %d" % freeLinesInOriginalFile
                            print "extra_neededRows: %d" % extra_neededRows
                            if freeLinesInOriginalFile <= extra_neededRows:
                                extra_neededRows = extra_neededRows - freeLinesInOriginalFile
                                newHeight = norm_OrigGameFontHeight + (extra_neededRows * origGameFontDiakenoHeight) ## old
                            elif freeLinesInOriginalFile > 0:
                                newHeight = imOrigGameFont.size[1]
                            else:
                                newHeight = norm_OrigGameFontHeight
                            # to kanoume zygo ari8mo
                            if newHeight % 2 > 0 : newHeight += 1

                            imTargetGameFont = Image.new(imOrigGameFont.mode,(imOrigGameFont.size[0], newHeight), (0,0,0,0))
                            imTargetGameFont.paste(imOrigGameFont, (0,0, imOrigGameFont.size[0], imOrigGameFont.size[1]))
                            importedNumOfLetters = 0
                            previousLetterFinishCol = 0
                            # open the copy .font file to  modify it
                            # First look for copy file and create it if it does not exist and open it
                            transSpeechInfoFile = None
                            #
                            # create and set the filename for the produced font file
                            #
                            self.copyFontFileName= self.getExpectedFileNameForOutputINFO()
            ##                origFontFilenameParts = str.rpartition(str(self.origFontFilename), '.')
            ##                self.copyFontFileName= origFontFilenameParts[0] + "_1" + origFontFilenameParts[1] + origFontFilenameParts[2]
            ##                if not os.access(self.copyFontFileName, os.F_OK) :
                            if os.access(self.origFontFilename, os.F_OK) :
                                try:
                                    shutil.copyfile(self.origFontFilename, self.copyFontFileName) #always overwrite in this method
                                except:
                                    errorFound = True
                            else:
                                errorFound = True
                            if not errorFound:
                                copyFontFile = None
                                if os.access(self.copyFontFileName, os.F_OK) :
                                    try:
                                        copyFontFile = open(self.copyFontFileName, 'r+b')
                                    except:
                                        errorFound = True
                                else:
                                    errorFound = True
                                if not errorFound:
                                    # reopen the image with our Fonts because we deleted the letters in the in-mem copy
                                    im = None
                                    if os.access(self.imageRowFilePNG, os.F_OK) :
                                        try:
                                            im = Image.open(self.imageRowFilePNG)
                                        except:
                                            errorFound = True
                                    else:
                                        errorFound = True
                                    if not errorFound:

                                        curHeightForNextAppend = pixHeightToBeginAppend
                                        for (c_startCol, c_startRow, c_endCol, c_endRow) in self.listOfLetterBoxes[0:]:
                                            currLetterFinishCol  = previousLetterFinishCol + interLetterSpacingInPNG + (c_endCol-c_startCol) + 1
                                            if currLetterFinishCol >= imOrigGameFont.size[0]:
                                                curHeightForNextAppend += origGameFontDiakenoHeight   ## old
                                                previousLetterFinishCol = 0
                                                currLetterFinishCol  = previousLetterFinishCol + interLetterSpacingInPNG + (c_endCol-c_startCol) + 1
                                            # TO DO: handle lines change and right height calculation (vertical positioning of letter)

                                            newLetterLeftCol = previousLetterFinishCol+interLetterSpacingInPNG
                                            newLetterTopRow = curHeightForNextAppend+ (c_startRow - minRowTop) + origGameFontSizeEqBaseLine - normalizedPopularBaseLine -1   # double -1 works right
                                            newLetterRightCol = currLetterFinishCol
                                            newLetterBottRow = curHeightForNextAppend + (c_endRow-c_startRow) + ( c_startRow - minRowTop)+ origGameFontSizeEqBaseLine - normalizedPopularBaseLine
                                            rowTruncatedPixels = 0
                                            if newLetterBottRow > curHeightForNextAppend + origGameFontDiakenoHeight:
                                                rowTruncatedPixels = newLetterBottRow - (curHeightForNextAppend + origGameFontDiakenoHeight)
                                                newLetterBottRow = curHeightForNextAppend + origGameFontDiakenoHeight  # TODO: or is it -1 ?


                                            imTargetGameFont.paste(im.crop((c_startCol,c_startRow, c_endCol+1, c_endRow+1 - rowTruncatedPixels)),
                                                                            (newLetterLeftCol,
                                                                            newLetterTopRow,
                                                                            newLetterRightCol,
                                                                            newLetterBottRow))
                                            importedNumOfLetters += 1
                                            copyFontFile.seek(firstTableLineOffset +  (existingSizeOfTableInOrigImage + importedNumOfLetters -1 )* 16 )     #nea grammi
                                            # # adding +1 in all coords for letter box because there is a +1 difference (png has 0,0 start and .font has 1,1)
                                            newLetterLeftColToWrite = pack('h',newLetterLeftCol+1-1) # -1 because the engine seems to be want the pixel column before the start of the letter, otherwise it purges its first column
                                            copyFontFile.write(newLetterLeftColToWrite)
                                            newBOX_LetterTopRowToWrite = pack('h', curHeightForNextAppend+1 )
                                            copyFontFile.write(newBOX_LetterTopRowToWrite)
                                            newLetterRightColToWrite = pack('h', newLetterRightCol+1) #-1 testing to see if the engine wants the last column or the column after it.
                                            copyFontFile.write(newLetterRightColToWrite)
                                            newBOX_LetterBottRowToWrite = pack('h', curHeightForNextAppend + origGameFontDiakenoHeight ) ##old
                                            copyFontFile.write(newBOX_LetterBottRowToWrite)

                                            pixelsWithinLetterBoxFromLeftToLetterInt = 0
                                            kerningLetterInt = 0
                                            widthTargetLangInt = (c_endCol-c_startCol) + 1
                                            #
                                            # ITALICS MODE!
                                            # keep indent the same as the original font (engish char, copy)
                                            # set kerning to be analogous to width, so eg. if the original width was Wo 13 and kerning Ko is 8 (and 13-8 = 5) then the kerning Kg for the greek letter with width Wg we will be: Kg = Wg - (int)( Wg * (Wo-Ko) ) /Wo
                                            #
                                            # For greek letters:
                                            # ήβγζημξρςφχψ
                                            # Should behave like:
                                            # j
                                            #
                                            # For greek letters:
                                            # ΐιίϊ
                                            # Should behave like:
                                            # i
                                            #
                                            # For greek letters:
                                            # ΰυϋύ
                                            # Should behave like:
                                            # u
                                            #
                                            # For greek letters:
                                            # ΈΉΌΏΒΓΕΖΗΙΚΜΝΞΠΡΣΤΧΨ
                                            # Should behave like:
                                            # B
                                            #
                                            # For greek letters:
                                            # ΌΘΟΦΩ
                                            # Should behave like:
                                            # O
                                            #
                                            # For greek letters:
                                            # ΊΙΪ
                                            # Should behave like:
                                            # Ι
                                            # TODO: ADD Greek flag to only use them for greek
                                            if italicsMode == True:
                                                currPngIndex = importedNumOfLetters-1
                                                currLett = self.orderAndListOfForeignLetters[currPngIndex];
                                                print "Current letter is %s"  % (currLett)
                                                if (currPngIndex == self.pngIndexOfForeignLetter(u"β") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"γ") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"ζ") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"η") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"ή") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"μ") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"ξ") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"ρ") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"ς") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"φ") or \
                                                    currPngIndex == self.pngIndexOfForeignLetter(u"ψ") \
                                                ):
                                                    letterPrototype = 'y'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)
                                                elif ( currPngIndex == self.pngIndexOfForeignLetter(u"ΐ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"ι") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"ί") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"ϊ") \
                                                ):
                                                    letterPrototype = 'i'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)
                                                elif ( currPngIndex == self.pngIndexOfForeignLetter(u"ΰ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"υ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"ϋ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"ύ") \
                                                ):
                                                    letterPrototype = 'u'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)
                                                elif ( currPngIndex == self.pngIndexOfForeignLetter(u"Έ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ή") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ό") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ώ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Β") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Γ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ε") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ζ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Η") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Κ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Μ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ν") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ξ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Π") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ρ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Σ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Χ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ψ") \
                                                ):
                                                    letterPrototype = 'B'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)

                                                elif ( currPngIndex == self.pngIndexOfForeignLetter(u"Ό") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Θ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ο") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Φ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ω") \
                                                ):
                                                    letterPrototype = 'O'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)
                                                elif ( currPngIndex == self.pngIndexOfForeignLetter(u"Ί") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ι") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"Ϊ") \
                                                ):
                                                    letterPrototype = 'I'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)
                                                elif ( currPngIndex == self.pngIndexOfForeignLetter(u"Τ")\
                                                ):
                                                    letterPrototype = 'T'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)
                                                elif ( currPngIndex == self.pngIndexOfForeignLetter(u"χ")\
                                                ):
                                                    letterPrototype = 'p'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)
                                                elif ( currPngIndex == self.pngIndexOfForeignLetter(u"ο") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"ό") \
                                                ):
                                                    letterPrototype = 'o'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)
                                                elif ( currPngIndex == self.pngIndexOfForeignLetter(u"τ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"κ") or \
                                                        currPngIndex == self.pngIndexOfForeignLetter(u"π") \
                                                ):
                                                    letterPrototype = 'g'
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= self.indentAndKernForItalicsWithProtoLetter(specificLetterPrototypesToFeaturesDict,letterPrototype,widthTargetLangInt)
                                                else:
                                                    (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt )= (0,(widthTargetLangInt-1))


                                            pixelsWithinLetterBoxFromLeftToLetterToWrite = pack('h', pixelsWithinLetterBoxFromLeftToLetterInt)
                                            copyFontFile.write(pixelsWithinLetterBoxFromLeftToLetterToWrite)

                                            widthLetterToWrite = pack('h', widthTargetLangInt)
                                            copyFontFile.write(widthLetterToWrite)

                                            if italicsMode == False:
                                                kerningLetterInt = (widthTargetLangInt-1)

                                            kerningLetterToWrite = pack('h', kerningLetterInt )
                                            copyFontFile.write(kerningLetterToWrite)
                                            dummyZerosToWrite = pack('h', 0)
                                            copyFontFile.write(dummyZerosToWrite)

                                            previousLetterFinishCol = previousLetterFinishCol+interLetterSpacingInPNG + (c_endCol-c_startCol) + 1

                        ##                    print importedNumOfLetters, c_startCol,c_startRow, c_endCol, c_endRow
                                        totalFontLetters = existingSizeOfTableInOrigImage + importedNumOfLetters
                                        # update the size of the table in the .font file 4rth byte:
                                        copyFontFile.seek(4)
                                        print "totalFontLetters %d" % (totalFontLetters)
                                        if (totalFontLetters < 0):
                                            errMsg = 'An error occurred while detecting the number of font letters!'
                                            retVal = -1
                                            print errMsg
                                        elif (totalFontLetters == 0):
                                            errMsg = 'No font letters were detected! Please adjust the fields for top-top and left-left margins!'
                                            retVal = -1
                                            print errMsg
                                        elif (totalFontLetters > 255):
                                            errMsg = 'Too many font letters were detected (%d)! Please adjust the fields for top-top and left-left margins!'%(totalFontLetters,)
                                            retVal = -1
                                            print errMsg
                                        else:
                                            totalFontLettersByteToWrite = pack('B',totalFontLetters)
                                            copyFontFile.write(totalFontLettersByteToWrite)

                                            # update the ASCII table indexes to the PNG table entries:
                                            for tmpX in self.dictOfOffsetsToValuesForForeignLettersToWrite.keys():
                                                copyFontFile.seek(tmpX)
                            ##                    print self.dictOfOffsetsToValuesForForeignLettersToWrite[tmpX]
                                                tmpByteToWrite = pack('B',self.dictOfOffsetsToValuesForForeignLettersToWrite[tmpX])
                                                copyFontFile.write(tmpByteToWrite)

                                            # SAVE the expanded image PNG file with the added fonts
                                            self.copyPNGFileName=self.getExpectedFileNameForOutputPNG()
                                            imTargetGameFont.save(self.copyPNGFileName, "PNG")
                            ##                file, ext = os.path.splitext(self.imageOriginalPNG)
                            ##                self.copyPNGFileName=file + "Expanded"+ext
                            ##                imTargetGameFont.save(self.copyPNGFileName, "PNG")
                                            self.copyFontPropertiesTxt =  self.getImagePropertiesInfo(False) # "%dx%dx%s" % (imTargetGameFont.size[0],imTargetGameFont.size[1], imTargetGameFont.mode)
                                            # close the final updated .font file
                                            # TO DO: backup the original before proceeding (or write to another file always).
                                            copyFontFile.close()
                                            retVal = 0
                                            errMsg = "Process completed successfully!"
                                            print errMsg
                    else: ## if existingSizeOfTableInOrigImage <> lettersInOriginalFontFile
        #                copyFontFile.close()
                        errMsg = "Font file %s already has appended letters or is incompatible with the selected game. Quiting...." % self.copyFontFileName
                        print errMsg
                        retVal = -1

            else: ## if self.lettersFound <= 0
                errMsg = "No letters were found in input png!"
                print errMsg
                retVal = -2
        return (retVal, errMsg, origGameFontSizeEqBaseLine, totalFontLetters, importedNumOfLetters)

    def pngIndexOfForeignLetter(self, letterUprefixed):
        return (self.targetLangOrderAndListOfForeignLettersStrUnicode.find(letterUprefixed))

    def indentAndKernForItalicsWithProtoLetter(self, specificLetterPrototypesToFeaturesDict, letterPrototype, widthTargetLangInt):
        jOrigIndent = specificLetterPrototypesToFeaturesDict[letterPrototype][0]
        jOrigWidth = specificLetterPrototypesToFeaturesDict[letterPrototype][1]
        jOrigKern = specificLetterPrototypesToFeaturesDict[letterPrototype][2]
        pixelsWithinLetterBoxFromLeftToLetterInt = jOrigIndent
        kerningLetterInt = 0
        if letterPrototype == 'i' or letterPrototype == 'u' or letterPrototype =='o' :
            kerningLetterInt = jOrigKern + 2
        else:
            kerningLetterInt = widthTargetLangInt - ((widthTargetLangInt * (jOrigWidth-jOrigKern)) / jOrigWidth)
        print "Adopting Indent and Kerning of: %s. Orig Indent=%d Width=%d Kern=%d. Target language Indent=%d Width=%d Kern=%d. " % (letterPrototype, jOrigIndent, jOrigWidth, jOrigKern, pixelsWithinLetterBoxFromLeftToLetterInt, widthTargetLangInt, kerningLetterInt )
        return (pixelsWithinLetterBoxFromLeftToLetterInt, kerningLetterInt)



    def getLetterOutlines(self, boolOrigFile):
        """ Return a list of the outlines for the letters (add info about the spacing, that could be useful for other fuctions)
        """
        # offset for PNG table index start
        firstTableLineOffset = self.PNG_TABLE_STARTLINE_OFFSET
        retList =[]
        activeFontFile = None
        ioErrorFound = False
        if boolOrigFile == True:
            ## open the original font file
            if os.access(self.origFontFilename, os.F_OK):
                try:
                    activeFontFile = open(self.origFontFilename, 'rb')
                except:
                    ioErrorFound = True
            else:
                ioErrorFound = True
        else:
            ## open the created extended font file
            if os.access(self.copyFontFileName, os.F_OK):
                try:
                    activeFontFile = open(self.copyFontFileName, 'rb')
                except:
                    ioErrorFound = True
            else:
                ioErrorFound = True
        if ioErrorFound:
            errorFound = True
        else: # file opened
        # read the 4rth byte with the number of entries in the table indexing the png (starting from offset self.PNG_TABLE_STARTLINE_OFFSET)
            activeFontFile.seek(4)
            tmpSizeOfTableWithFontsIndexedToImage = unpack('B',activeFontFile.read(1))
            existingSizeOfTableInActiveImage =  tmpSizeOfTableWithFontsIndexedToImage[0]
            for i in range(0,existingSizeOfTableInActiveImage):
                activeFontFile.seek(firstTableLineOffset + i* 0x10)
                tmpColStart = unpack('h',activeFontFile.read(2))    # unpack always returns a tuple
                tmpRowStart = unpack('h',activeFontFile.read(2))    # unpack always returns a tuple
                tmpColEnd = unpack('h',activeFontFile.read(2))    # unpack always returns a tuple
                tmpRowEnd = unpack('h',activeFontFile.read(2))    # unpack always returns a tuple
                tmpPixelsWithinLetterBoxFromLeftToLetter = unpack('h',activeFontFile.read(2))    # unpack always returns a tuple
                tmpWidthLetter = unpack('h',activeFontFile.read(2))    # unpack always returns a tuple
                tmpKerningLetter = unpack('h',activeFontFile.read(2))    # unpack always returns a tuple
                tmpChar = '0'
                if(i >= 0x0 and i <= (self.lettersInOriginalFontFile - 1) ):
                    tmpChar = self.replacePngIndexForOrigChars[i]
                if(i >= self.lettersInOriginalFontFile):
                    tmpChar = self.rev_replacePngIndexWithCorrAsciiChar[i]
                retList.append((tmpColStart[0], tmpRowStart[0], tmpColEnd[0], tmpRowEnd[0], tmpPixelsWithinLetterBoxFromLeftToLetter[0], tmpWidthLetter[0], tmpKerningLetter[0], tmpChar))
            activeFontFile.close()
        return retList

    def writeBackCharProperties(self, pCustomCharAttributesLst):
        """ Take a list with every new imported char and its indent and kening attributes and update the produced font file
        """
        # offset for start of PNG index table
        tableStartLineOffset = self.PNG_TABLE_STARTLINE_OFFSET
        activeFontFile = None
        if os.access(self.copyFontFileName, os.F_OK):
            try:
                activeFontFile = open(self.copyFontFileName, 'r+b')
                for i in range(0,len(pCustomCharAttributesLst)):
                    (tmpImportedCharIndex, tmpIndent, tmpKerning) = pCustomCharAttributesLst[i]
                    activeFontFile.seek(tableStartLineOffset + tmpImportedCharIndex* 0x10 + 0x08)
                    pixelsWithinLetterBoxFromLeftToLetterToWrite = pack('h', tmpIndent)
                    activeFontFile.write(pixelsWithinLetterBoxFromLeftToLetterToWrite)
                    activeFontFile.seek(tableStartLineOffset + tmpImportedCharIndex* 0x10 + 0x0C)
                    kerningLetterToWrite = pack('h', tmpKerning)
                    activeFontFile.write(kerningLetterToWrite)
                activeFontFile.close()
            except:
                errorFound = True
        else:
            errorFound = True
#
#
# ########################
# main
# sys.argv[1] filename of our png with row of fonts in same directory
# sys.argv[2] filename of original png to be expanded   ->>-
# sys.argv[3] filename of corresponding .font file      ->>-
# sys.argv[4] spacebetweenLetterFromLeftToLeft
# sys.argv[5] spacebetweenLetterFromTopToTop
# #########################
#
if __name__ == "__main__":

    if len(sys.argv) == 6:
        TMPminSpaceBetweenLettersInRowLeftToLeft = int(sys.argv[4])
        TMPminSpaceBetweenLettersInColumnTopToTop = int(sys.argv[5])
        TMPorigFontFilename = sys.argv[3]
        TMPimageOriginalPNG = sys.argv[2]
        TMPimageRowFilePNG = sys.argv[1]
        TMPcustomBaseLineOffset = 0
        myGrabInstance = grabberFromPNG('windows-1253', 1, TMPorigFontFilename,   TMPimageOriginalPNG)
        myGrabInstance.setImageRowFilePNG(TMPimageRowFilePNG)
        myGrabInstance.setMinSpaceBetweenLettersInRowLeftToLeft(TMPminSpaceBetweenLettersInRowLeftToLeft)
        myGrabInstance.setMinSpaceBetweenLettersInColumnTopToTop(TMPminSpaceBetweenLettersInColumnTopToTop)
#        myGrabInstance.setBaseLineOffset(TMPcustomBaseLineOffset)
        myGrabInstance.generateModFiles(TMPcustomBaseLineOffset)
    else:
        print "Invalid syntax! ..."
        myGrabInstance = grabberFromPNG('windows-extra', 1)
else:
    #debug
	#print 'font grabber imported from another module'
    pass

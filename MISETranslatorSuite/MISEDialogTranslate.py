#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Created by Praetorian (ShadowNate) for Classic Adventures in Greek
# classic.adventures.in.greek@gmail.com
#
import os, sys, shutil
import array
from struct import *
import time
import re
import hashlib
import sqlite3
from math import trunc

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)
import imagesrsc
import highlightRulesGlobal


import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QCloseEvent
from grabberFromPNG014 import grabberFromPNG
from tableViewCheckBoxDelegate import CheckBoxDelegate
from tableViewTextDocDelegate import TextDocDelegate
from MISEFontsTranslate25 import MyMainFontDLGWindow
from monkeySERepakGUI import MyMainRepackerDLGWindow
import json

######
# TODO: if search for a keyword that exists in the "pre-existing" highlight rules, then one of the two supercedes the other! (so we should just keep the highlighting of the search word.
       # "fixed", the search keyword overrides the others (it seems at least in practice)
# DONE: Fixed searching with case insensitive for greek letters (column 1 UNICODE flag set)
# TODO: Replace should create a report of how many instances were replaced!
# TODO: Bind Ctrl+H to replace (when it's implemented)
# TODO: Remember the width of columns of last session before closing app. Remember screen resolution. Keep connection with FILE MD5?
# TODO: During a merge make OPTIONAL the merging of pending lines (prompt a dialogue to the user)
# TODO: During a LOAD do a CLEAN LOAD of the pending lines . (or make it OPTIONAL? a) If file exists, and b) if the translator wants to load those and c) option to merge.
# TODO: "Replace" functionality. Replace should take into account that a word can be found more than once in the same quote. "Find" does not do that.
# TODO: export to excel ?
# TODO: import from excel ?
# TODO: spell-check (aspell? hunspell?)
# TODO: Bug: Searching for greek is always case sensitive
# TODO: Sorting books (library catalogue cards MI2:SE) uses system locale. It should use a locale associated with the selected encoding!

######
# TODO: use errMsg to show message Errors that were previously printed in console.
# TODO: use search for "TODO: debug and error"  find the Errors that were previously printed in console.

# TODO: Show uncomitted lines in report (needs update of saved lines with every submit!)
# TODO: show an animated icon while opening/loading something/merging/etc
# TODO: Check OPENED files as well for validity (valid headers, if they are what their extension states) (based on the check in the getQuoteNumberInFile method!)
# TODO: Check if uiText and speech.info MI:Se and MI2:SE have the same issue (with open file detecting fewer lines now!). FIXED more tests pending

# TODO: load file in session could restrict filter wildcard to the active session's related/allowed types only!
# TODO: for now, make the encoding field read-only!
# REVERTED (the removal of ε from grabber SO NOT NEEDED ANYMORE !! IMPORTANT NOTE: line 8610 fr.speech.info 0x94 -> ά. This should be explicitly set as a normal quote symbol " in the translation, by the translator
# TODO:  test load into session for credit files

# TODO: bug? sessions store absolute paths... Could be alleviated with force loading a backup file into a session!
# TODO: 3a. maKe exe
# TODO: 3c. Cleanup my sqlite dbase before redistribution
# TODO: 4b. Ability to have multiple sessions for the same original file (by default load the most updated) ??
# TODO: Locate and copy to destination folder
# TODO: un/mark multiple lines

# TODO: Delete a session and let it be recreated to see if the auto-inc works!

# TODO: Produce fonts for all fonts MI2:SE
# TODO: SPECIAL HANDLE NEEDED! sto MISE2 to A0 sta en.xxx kai fr.xxx (alla oxi sto geniko speech.info) xrhsimopoieitai san keno, pi8anotata keno pou den mporei na diaspastei apo new line!!!. Done?
# TODO: find out exactly which characters get changed after just loading and storing the speech.info (or the fr.speech.info). Are they all unneeded or are there special chars there? (MI2:SE). Done?

# TODO: ADD: Search ANY Column option

# TODO: Dirty bit (save before quit or before open other file)
# TODO: Support for other languages.
# TODO: Add menu, with Open, About and Another Open to import the configuration for the letter matchings. (the setting of matchings should be done in the FontsTranslation -Module or -GUI)
# TODO: Configuration tab. Table for making additions of new characters (and their correspondances to characters in the font files...)
# TODO: use md5 to recognize the original files. Make it configurable (to add md5 checksums for files if they are ever updated)
# TODO: Upon errors encountered, print where they were encountered (no prints to the console, append them in a log or in the messagebox with new-line separators)
# TODO: online updates!
# TODO: Additional search options: Find next Marked, Find previous Marked, Total marked
# TODO: Additional search options: Find next Changed, Find previous Changed,
# TODO: Additional text field: Report Total Changed
# TODO: Additional search options: Find next Pending, Find previous Pending, Report Total Pending
# TODO: Find(Match Case) does not work for local language. Maybe convert keys to UTF-8 before comparing ???
# TODO: Additional text field: Report Total Pending
# TODO: Remove all explicit references to myEncoding and Windows-1253 and 69 and 0x9a and 0x99 and the dictionariues with greek letters and FRENCH
## DONE: CHECK: Support all Formats of files for MONKEY ISLAND 2! Check if it breaks compatibility with SoMI:SE

# TODO: Autosave feature?
# TODO: Note about the SoMI bugs that were "fixed" by changing the classic version (and a how-to). This could be integrated in the interface also (produce the text required in the classic version for the bug cases (lens, The Sea Monkey, 173 piece of eight or sth)

#v 4.92
## Re-assign the show report dialogue to Ctrl+R
## Bind Ctrl+L to go to line dialogue
## Searching for [~TEMP] in translated text does not match the literal due to using regular expressions. Resolved: The case for [~temp] is resolved. The re are not removed. But search for [~temp] now works and other special characters have been supressed (eg '.', '$','^','(',')','[',']')
## Bug: Searching for '.' produces ANY character! (supressed dot special character)
## Export the pending lines to a meta file.
## During a merge or a load... merge the pending lines too.

#v 4.9
## Changed encoding of source file (MISEDialogueTranslate to UTF-8
## tryEncoding is now retrieved via grabberFromPNG module (first looks in overrideEncoding, then uses greek by default)

#v 4.8
## Add tools in menu.
## Integrate fonts mod tool
## Integrate re-packer tool
## Early work to allow override of encoding (other languages support) with overrideEncoding.txt file
## session encoding and gameid are now stored in sessions.txt (utf-8 without BOM) for font mod tool
## session delete implemented for font mod tool
## font mod tool now prompts for game selection.


#v 4.7
## DONE
## Library re-ordering. (MI2:SE) fr.uitext.info
##        # 1. Find the addresses within the classic game files. (SCRP_0063, SCRP_0064, LSCR_0207) where these scripts start
##        # 2. check for original MD5? (NOT IN 4.7), make backup copy.
##        # 3. parse commands, create new commands in place, same length!!!! Parse commands (print out their "high level version", print-out their count). Edit/update with new indexes, check the length of each result (compared to original length. Should be the same!)
##        # 4. Find related lines in fr.speech.info and fr.uiText.info. Find which ones are the names to be translated/re-ordered. In fr.uiText.info the lines get repeated. (seem identical). Order the first batch (711 - 950) and it will be similar for (1026 - 1265). (240 entries).
##        #    for each entry get the old position (index) and the new position after ordering based on name. Order first the greek ones, then the latin ones (if some remain untranslated).
##        #    Report where the 'big whoop' entry ended up (original and new). Original should be 192 (for 1-based counting, not 0-based).
##        #    Insert the big-whoop entry in the original position (it should remain unchanged) and shift all the entries to its right by one increment.
##        #    Also 719 entry has Big-whoop See Treasure reference that should be fixed (?) -probably won't be needed any change (only the category name in greek). Should it be under greek B?
##        #    ??? How do we order mixed latin and greek names? We order only categories. Categories will be in greek!
##        #
##        # 5. Go to the classic game files. Change the scripts to reflect the new order.
##        # 6. Test in-game ordering!
##        # +++. Since some ranges of categories are identical -> offer (dilaogue box) to overwrite the second range with the values of the first range.
##        # +++. Playtest with the re-ordered books and a walkthrough to see if it works 100%.
##        # Big whoop, Pirate quotes and Joy of HEx, ALL must maintain their IDs!!! (DONE)
##        # [] Offer to overwrite identical ranges in fr.uitext.info (MI2:SE)
##


# v4.23
## DONE: Bugfix: MI2:SE fr.speech.info line 6385 shows a β (0xE2) for Papier Mache. Probably needs fixin (if we don't completely translate it in greek). Also fixed sequences for classic credits (tm and b(c)  )

# v4.22
## DONE: Support for having unicode letters in file paths. tested with greek. The sqlite db stores in unicode so that helped a lot.


# v4.21
## DONE: Nasty Bug. Hitting Load in existing session and YES to the question AND THEN CANCEL, makes buttons disables, and removes the translation file from the top field!

# v4.2
## DONE: Handle ALL pure reads (rb) in memory with buffers. More importantly in open (parseQuoteFile) and load/merge (getQuoteNumberInFile)
## DONE: Check if trampol.sqlite does not exist, then check in "cleandb" folder and IF it is there then copy it in the active dir and open it. Otherwise print messagebox and quit?
## DONE: bug. after load the window becomes unfoced and shortcuts don't work before clicking on the window
## DONE: Show Report window (total pending, total marked, total conflicting, total lines, changed lines)
## DONE: Do not merge with another file if lines are conflicting from previous merge
## DONE: Go To next marked (up, down) Ctrl+P. Ctrl_Shift_P
## DONE: Go To next conflicted (up, down) Ctrl+E. Ctrl_Shift_E
## DONE: Go To next changed (up, down) Ctrl+G. Ctrl_Shift_G
## DONE: Go To next unchanged (up, down) Ctrl+U. Ctrl_Shift_U
## DONE; disable new buttons and menus when no active session

# v4.1
## bugfix: backup was having trouble with unicode encoding of certain file names
## DONE: Do not allow submit if conflicted lines!
## Set ecnoding text field as read-only (for greek translations we only need it fixed)
## Changed lines functionality now works!
## DONE: get the text from speech and uiText files for merge !!!
## DONE: Set color for conflicted. Reset it on false, and test precedence over MARKED as Pending
## DONE: Hints load (normal) bug. MI:SE 511 are detected from 517. Load file in session detects all of them (probably)!
## DONE: Add another column for resolving conflicts! Careful with too big lines (because of conlicted quoted concatenation!
## DONE: merge functionlatiy: Print warning, markers from the imported file won't be imported (the original markers will be kept)!
##                            a) Keep a list of the original french/lang-to-be-translated quotes in-memory, keep a list of the active translation (show changed lines)
##                            b) Extract the quotes list from the imported file. Compare with two lists above quote by quote. For each quote:
##                                   If same as first list then do not import
##                                   If changed as compared to first list and
##                                       if the second list is also changed as compared to first, then keep both SEPARATED BY NEW LINE? and MARK THE LINE!
##                                       if the second list is the same as the first for that quote, then import the quote from the 3rd list
##                           Print report: Imported file contained XX changed quotes. Imported FF quotes, of which CC were merged with existing translation (marked lines) and DD were cleanly imported.
## DONE: Update Tick box for "translated text" by comparing to the original file (upon load, upon save, or button press. Online? (without button pushing ?)

# v4.0
## DONE: Bind Ctrl+F to focus in search field,
## DONE: 5. support for credit files (plus one extra of MI2SE)
## Maybe not worth it: TODO: fix credit files'apparent trouble errors for 0xaa and 0x9d characters and the connected β€ appearances that are translated to βΏ
## ctrl+f shortcut focuses on find textbox
## f3 finds next match.
## DONE: 4. 	Ability to force load a previous (backuped) target fileand updtae the relevant session with its MD5 or create a new one (fits with multiple sessioons case)
## DONE: More error safe-proofing for loading a backup file (line number check)
## DONE: Somehow within the loadquotes function we should check if the translation file has less or more quotes than the original!!!
## DONE: import from text should state the number of lines imported

# v3.9
## TODO: submitting with zero lines and nothing opened /imported produces no error message!
## TODO: Fixed enabling disabling session related actions and buttons

# v3.8
## ERROR: Load translated Session in menu is wrong. (it loads a file in the translated field ?)
## DONE: MI2:SE support for speech!!!!!
## DONE: MI2:SE font files may differ from MI:SE (additional chars to be considered)
## DONE: Do the special characters appear in the original text of MI2:SE ?? Why do i only see them in the french text? Are they the same? Are they treated correctly?
## DONE: in MISE2 in en.speech.info there's a quote: I'd like to buy Indy's whip™  with the tm special character that does not exist in the speech.info:: They are different. Speech.info does nothave to be edited
## DONE: remove crashes when opeing a MI2:SE translation with a SoMI selected game set and vice-versa!
## DONE: Update Tick box for "check back again text" by loading from a sessions xml file (lines indicated as CSV) OR from sqlite db!
## DONE: extract to text file to be able to spell check (replace special characters as needed)
## DONE: import from text file (after spell check) (replace special characters as needed)
## DONE: Based on MD5 of original file, load the appropriate game ID (and keep it locked!)
## DONE: fr.speech.info support.
## DONE: fr.speech.info shuld be allowed only for MI2:SE
## DONE: fr.speech.info update should update the main speech.info? :: NO
## DONE: check for fr.speech.info AND main speech.info to be available. :: NOT NEEDED
## DONE: write to a copy fr.speech.info file?
## DONE: test with new fonts, and MI2:SE!!!
## DONE: store marked lines per session or file load?! ::: PER SESSION
## DONE: SomI:SE check bug with "The sea Monkey"(can it be fixed by changing the text in the classic game files? YES!
## DONE: Somi:SE check bug with "Oh... no more than 173 pieces of eight." and the false quote that guybrush says when selected. No speech file. used directly from classic version. Had to support direct greek in classic subtitle.s
## FIXED: o MD5 ypologismos gia to classic.credits dinei diaforetiko apotelesma apo to HxD (gia to original KAI tin metafrash)
## FIXED: after opening a credits file, opening speech.info keeps the translation file field with the credits copy file!!!
## DONE: Tick box for check back again the translation
## DONE: Tick box for "translated text" by comparing to the original file
## DONE: English text in UI: done
## DONE: Automatic Load of selected file
## DONE: pressing enter should not by default submit the text! Because the search does not work good like that! : DONE
## DONE: Ok messagebox at the end (or with error message)!
## DONE: Find Next
## DONE: Find Wrapping
## DONE: Implement upwards search
## DONE: Set find direction from GUI.
## DONE: Set find wrapping from GUI
## DONE: in the db or sessions file, store the md5 of the "original" set file to prevent wrong associations (if e.g. the original file changes due to an patch/update or is replaced by another  by the same name)
## DONE: Additional search options: Find(Match Case)
## DONE: 5. Make read-only the game id selection
## DONE: 0. test and see that the quotes are changed in-game
## DONE: 8. Put a larger text in a quote. test in-game
## DONE: 9. Put a smaller text in a quote. test in-game
## DONE:  6. Use sessions
## DONE: 7. save marked lines and load marked lines for sessions.**
## DONE: 13. what happens to session markers if I import translated text from a file? :: DONE. They are kept intact!
## DONE: ** 11. Load translation from copy file of session!
## DONE: ** 14. mAKE SURE THAT THE COPY IS ALWAYS LOADED IN THE RIGHT COLUMN and IT IS UPDATED IN THE END (NOT THE ORIGINAL FILE) IN ALL CASES
## DONE: ** New lines in quotes should be exported and imported correctly!!! 0A character is used for new line! (different than the A0 character!
## DONE: 14. Help About does not work
## DONE: 0. open translation file, or session have different wildcards for file types! dONE : NMAE UNVISIBLE AND UNLINKED ACTIONS
## DONE: 17. backup button from GUI:This will create a copy of the target file named ""  in your target directory. Warning: This will not backup any unsubmitted changes! YES_NO
## DONE: 88. Cancelling open disables backup button!
## DONE: 11. App icon
## DONE: 12. Disable or rename the menu function about loading translated file
## DONE: 0. remove support and provide warnings for files speech.info AND uiText for MI2:SE, also for the credits for now, and the actual uiText and hints csv!!!
## DONE: 0. provide warning if trying to open a speech.info file for MI2:SE (open the fr.speech.info file from your extracted MI2)
## DONE: 3c. Support for hints csv
## DONE: 3b. Support uiText!
## DONE: 10. Provide font files archive. bo_24 for 1366x768 for now. Only plain text. Not italics.
## DONE: 10a. Provide font files for ui.text for 1366x768. bo_24 does not seem to work
## DONE: 0. remove debug messages!
## DONE: 3b. test exe in a pc without python!
## DONE: 4c. Send progress on last iteration of translation project
## DONE: 4d. Provide instructions, (where to copy fonts, what to have in the installation folder (files to use). How to get the source files
## DONE: 4e. E-mail (or dropbox): To keep backup from trampol.sqlite, to put files in a workingFactory folder.
## DONE:	Sessions are saved in absolute
## DONE:	Columns and functions that don't work yet.
## DONE:	Unsupported files
## DONE:	Required resolution. Squares evrywhere else
## DONE:	Where to copy the produced files, and how to rename them!
## DONE:	Choose French from steam menu!
## DONE:	orth0grafikos elegxos!!
## DONE:	regular backjup of cpy file
## DONE:	About 0x0A in exported files
## DONE:	SPECIAL CHARS


#
fullcopyFileName = ""
#
# Input is expected from speech.info (in the audio folder), uiText.info and monkey1.hints.cvs
# The names of the original files should be kept unchanged for valid input and proper pattern (inner structure) recognition / processing
#
filenameHintsMI1CSV = "monkey1.hints.csv"
filenameHintsMI2CSV = "monkey2.hints.csv"
filenameUIText = "uiText.info"
filenameFrUIText = "fr.uitext.info"
filenameEnUIText = "en.uitext.info"
filenameEnClassicMonkey2001 = "monkey2.001"

filenameSpeechInfo = "speech.info"
filenameFrSpeechInfo = "fr.speech.info"
filenameEnSpeechInfo = "en.speech.info"
filenameInfoWildCard = "*.info"

filenameCreditsList = ["classicgame.credits.xml","endgame.credits.xml","endgamepc.credits.xml","remonkeyedgame.credits.xml","remonkeyedgamepc.credits.xml","title.credits.xml","title_sd.credits.xml", "title_windows.credits.xml"]
filenameCreditsStartMatrxAddrList  = [ 0xF4, 0x5A4, 0x5A4, 0x444, 0x444, 0x3C4, 0x3C4, 0x3C4] # this could be calculated from the files (there is an indicative offset at addr 0x1C, but the exact wherabouts of the first word do not seem to be easy to calculate)

filenameCreditsListMISE2 = ["classicgame.credits.xml","endgame.credits.xml","endgamepc.credits.xml","remonkeyedgame.credits.xml","remonkeyedgame_ingame.credits.xml","remonkeyedgamepc.credits.xml","title.credits.xml","title_sd.credits.xml", "title_windows.credits.xml"]
filenameCreditsStartMISE2MatrxAddrList  = [ 0xF4, 0x5A4, 0x5A4,  0x494, 0x254, 0x494, 0x3C4, 0x3C4, 0x3C4]

plithosOfDifferentLanguages = 5 #supported within the game (this is from MI:SE, TODO: to be confirmed as the same for the MI2:SE
selectedLanguageOffset = 1 # TODO: could vary, as a parameter? 1 is for french.

listOfEnglishLinesSpeechInfo = [] #triplet: start offset, untranslated text in English,  length
listOfForeignLinesOrigSpeechInfo = [] #triplet: start offset, untranslated text in English,  length // or it could be just the quote and length maybe...
listOfUntranslatedLinesSpeechInfo = [] #triplet: start offset, to be translated text in non-English (Selected language), start offset, length
listOfAllLinesHintsCSV = [] #triplet
listOflistsOfAllQuotesHintsCSV = [] # a list of lists with at most 4 elements that are subsequent hints (3 at most) within a "primary hint" (the first element)

listOfAllUntouchedLinesCredits = [] # triplet: start address, text, length
listOfIndexOfAllLinesCreds = [] # two values for original credits: start address, value (offset)
listOfIndexOfAllTransLinesCreds = [] # two values for translated credits: start address, value (offset)

listOfLabelsSpeechInfo = [] #used in MI2 (for fr.speech.info labels). Aux
listOfEnglishLinesSpeechInfoOrig = [] # for MI2
listOfLabelsSpeechInfoOrig = [] # for MI2
###############################
##############################
### MAIN WINDOW CLASS
###############################
###################################

class MISEQuoteTableView(QtGui.QTableView):
    """
    A QTableView for displaying the quotes and editing the translation
    """
    _autoresize = True
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent)
#        self.init_variables()
#        self.setShowGrid(False)
#        self.verticalHeader().hide()
#        self.verticalHeader().setDefaultSectionSize(20)
#        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
#        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        self.setGeometry(27, 130, 1095, 626)
        self.setFont(QtGui.QFont('Arial', 10))
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setCascadingSectionResizes(True)
        self.horizontalHeader().setDefaultSectionSize(400)
        self.horizontalHeader().setHighlightSections(True)
        self.horizontalHeader().setMinimumSectionSize(30)
        self.horizontalHeader().setStretchLastSection(False)
        self.verticalHeader().setCascadingSectionResizes(False)
        self.verticalHeader().setDefaultSectionSize(40)
        self.verticalHeader().setMinimumSectionSize(40)
        self.verticalHeader().setStretchLastSection(False)
#        connect(self, SIGNAL('doubleClicked (const QModelIndex &)'), self.revisionActivated)
        self._autoresize = True
#        connect(self.horizontalHeader(), SIGNAL('sectionResized(int, int, int)'), self.disableAutoResize)

    def resizeEvent(self, event):
        # we catch this event to resize smartly tables' columns
        QtGui.QTableView.resizeEvent(self, event)
        if self._autoresize:
            self.resizeColumns(event.oldSize(), event.size())

    def resizeColumns(self, oldSize, newSize):
        # resize columns handling
        model = self.model()
        if not model:
            ##print "DEBUG: no resize no model"
            return
        elif self._autoresize:
            ##print "DEBUG: resizing columns because table was resized from (%d, %d) to (%d, %d)" % (oldSize.width(), oldSize.height() ,newSize.width(), newSize.height() )
            self.emit(SIGNAL("resize(int, int)"), oldSize.width(), newSize.width()) # to be handled in the main class
        return
#
# END OF SUBCLASSING QTABLEVIEW
#
# TODO: validate the selected encoding?

#class for handling the GUI
class MyMainWindow(QtGui.QMainWindow):
    #
    # TODO: need a more centralised access control to the DB
    #
    origEncoding = 'windows-1252'
    currentPath = u"" # for open or save files
    relPath = u'.'
    DBFileName = u'trampol.sqlite'
    uiFolderName = u'ui'
    uiFileName = u'MISEDialogTranslateUIWin.ui'
    uiFontsToolFileName = u'MISEFontsTranslateUIDlg.ui'
    uiRepackerToolFileName = u'MISERepackUIWin.ui'
    jSettingsInMemDict = None

    DBFileNameAndRelPath = ""
    defGameID = 1 # SomiSE
    basedir = u"."
    icon = None
    ui = None
    windowFontDLG = None
    #
    # TODO: THESE SHOULD BE parameters for the GUI!!
    #
    ##tryEncoding = 'windows-1253'
    selGameID = 1 # SomiSE
    activeSessionID = -1
    ##activeEnc = tryEncoding

    localGrabInstance = grabberFromPNG() # just for init purposes and getting the tryEncoding.
    tryEncoding = localGrabInstance.getTryEncoding()
    activeEnc = tryEncoding
    localGrabInstance = None


    statusLoadingAFile = False
    ignoreQuoteTableResizeEventFlg = False


    MESSAGE = "<p>This is a sample info message! " \
        "One.</p>" \
        "<p>Two " \
        "Three.</p>"

    def eventFilter(self, object, event):
        #print "EVENT TYPE: %s VS %s " % (event.__class__.__name__, QtGui.QCloseEvent.__name__)
        #print "OBJECT: %s VS %s " % (object.__class__.__name__, self.ui.__class__.__name__)
        if self.ui.closingFlag  == False and event.__class__ == QtGui.QCloseEvent:
        ## HANDLE EVENT....
            self.closeEvent(event)
            return True
        else:
            return False


    def __init__(self, parent = None):
        self.statusLoadingAFile = False
        self.jSettingsInMemDict = dict()
        self.initHighlightRules()
        self.ignoreQuoteTableResizeEventFlg = False
        if getattr(sys, 'frozen', None):
            self.basedir = sys._MEIPASS
        else:
            self.basedir = os.path.dirname(__file__)

        self.DBFileNameAndRelPath = os.path.join(self.relPath,self.DBFileName)
        #print self.DBFileNameAndRelPath
        #qtWindow init was here...
        ##uiFilePath = os.path.join(self.relPath, self.uiFileName)
        uiFilePath = os.path.join(self.relPath, self.uiFolderName, self.uiFileName)
        #print uiFilePath
        if not os.access(uiFilePath, os.F_OK) :
            print "Could not find the required ui file %s for the application. Quiting..." % (self.uiFileName)
            sys.exit(0)




        if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
            #check in cleandb subdir too!
            cleanDBRelPath= os.path.join(self.relPath, "cleandb",self.DBFileName)
            #print cleanDBRelPath
            # removed attempts to set the (str.decode(encoding) or unicode(.. ,encoding) ) encoding here for cleanDBRelPath since it;s already a unicode object

            if os.access(cleanDBRelPath, os.F_OK) :
                reply = QtGui.QMessageBox.question(self, 'Clean DB copy',
                    "No existing DB was detected in the same folder with the translator app, but a clean DB was detected in the cleandb subdirectory. Do you want to adopt this as your active DB?", QtGui.QMessageBox.Yes |
                    QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    shutil.copyfile(cleanDBRelPath, self.DBFileNameAndRelPath)
                else:
                    QtGui.QMessageBox.critical(self, "Database file missing!",
                    "The database file %s could not be found. Cannot proceed without a database file. Quiting..." % (self.DBFileNameAndRelPath))
                    self.tryToCloseWin()
                    sys.exit(0)
            else:
                QtGui.QMessageBox.critical(self, "Database file missing!",
                "The database file %s could not be found. Cannot proceed without a database file. Quiting..." % (self.DBFileNameAndRelPath))
                self.tryToCloseWin()
                sys.exit(0)


        #
        # retrieve DB stored settings if any
        #
        conn = sqlite3.connect(self.DBFileNameAndRelPath)
        c = conn.cursor()
        ##print "checking for JSON"
        c.execute("""select jsonsettings from settings where id = 1""")
        row = c.fetchone()
        conn.commit()
        c.close()
        if (row is not None and row[0]!= ""):
            self.jSettingsInMemDict = json.loads(row[0])

        # TODO: check if the desired screen number exists.
        # TODO: get resolution of target screen check if similar. Else, show in the center? (or show always in the center?)
        screen_number = 0 #2 is an example, this is 3th screen, because screens are numbered from 0
        parentScreen = QtGui.QApplication.desktop().screen(0x00) # QWidget *
        is_virtual_desktop = QtGui.QApplication.desktop().isVirtualDesktop()  # bool
        screenCount =  QtGui.QApplication.desktop().screenCount()
        primaryScreen =  QtGui.QApplication.desktop().primaryScreen()
        top_left = QtGui.QApplication.desktop().screenGeometry(0).topLeft() #QPoint
        #
        #print "is virtual desktop: ", is_virtual_desktop, screenCount,
        if(self.jSettingsInMemDict is not None and self.jSettingsInMemDict.has_key('lastDesktopScreenNumber')):
        #
            screen_number = self.jSettingsInMemDict['lastDesktopScreenNumber']
            if(screen_number >= screenCount or screen_number < 0):
                screen_number = primaryScreen

            if is_virtual_desktop:
                top_left = QtGui.QApplication.desktop().screenGeometry(screen_number).topLeft()
            else:
                parentScreen = QtGui.QApplication.desktop().screen(screen_number)
        try:
            QtGui.QMainWindow.__init__(self, parentScreen)
        except:
            parentScreen = QtGui.QApplication.desktop().screen(0x00)
            QtGui.QMainWindow.__init__(self, parentScreen)

        # Set up the user interface from Designer.
        self.ui = uic.loadUi(uiFilePath)
#        if is_virtual_desktop :
#            self.ui.move( top_left )

        self.ui.closingFlag = False
        self.ui.installEventFilter(self)
        self.icon = QIcon(":/icons/iconsimple.ico")
        self.ui.setWindowIcon( self.icon )

        self.setWindowIcon(self.icon ) # adds icons in dialog boxes

#        self.initAppMenu(self)

        self.ui.numOfEntriesOrigTxtBx.setText(u"0")
        self.native = True #can be used to control some native-to-OS or not dialogs beiing utilised (should be a checkbox)

#		self.openFilesPath = ''
        ## Connect up the buttons.
        self.ui.BrowseQuoteFilesBtn.clicked.connect(self.setOpenFileName)
##          self.ui.BrowseTranslatedQuoteFilesBtn.clicked.connect(self.setLoadTranslatedFileName)
##        self.ui.LoadQuoteFileBtn.clicked.connect(self.loadQuoteFileinTable)
        self.ui.SubmitChangesBtn.clicked.connect(self.saveToLoadedQuoteFile)
        self.ui.FindInQuotesBtn.clicked.connect(self.findNextMatchFromClickedButton)
        self.ui.replaceInQuotesBtn.clicked.connect(self.replaceOnceMatchClickedButton)
        self.ui.replaceAllInQuotesBtn.clicked.connect(self.replaceAllMatchClickedButton)
        self.currentSearchKeyword = ""
        self.ui.findStrTxtBx.setText("")
        self.ui.findSearchUpChBx.setChecked(False)
        self.ui.findWrapAroundChBx.setChecked(True)
        self.ui.findMatchCaseChBx.setChecked(False)

        # working shortcuts but overriden by menu actions -so commented out.
#        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+F"), self.ui, self.focusOnFindBox)
#        QtGui.QShortcut(QtGui.QKeySequence("F3"), self.ui, self.findNextMatchingStrLineInTable)
        self.SearcHReplaceModesRadioGroup = QButtonGroup()
        self.SearcHReplaceModesRadioGroup.addButton(self.ui.searchModeRB)
        self.SearcHReplaceModesRadioGroup.addButton(self.ui.replaceModeRB)

        self.ui.searchModeRB.connect(self.ui.searchModeRB, QtCore.SIGNAL('toggled(bool)'), self.searchModeToggled)
        self.ui.replaceModeRB.connect(self.ui.replaceModeRB, QtCore.SIGNAL('toggled(bool)'), self.replaceModeToggled)
        self.ui.searchModeRB.toggle()

        # todo: Match Case initialise!
        QtCore.QObject.connect(self.ui.selGameCmBx, QtCore.SIGNAL("currentIndexChanged(const QString)"), self.loadSelectedGameID)
        #
        # MenuActions
        #
        self.ui.actionOpen_Original_File.triggered.connect(self.setOpenFileName)
        self.ui.actionOpen_Original_File.setShortcut('Ctrl+O')

        self.ui.actionLoad_Translation_File.triggered.connect(self.setLoadTranslatedFileName)
        self.ui.actionLoad_Translation_File.setShortcut('Ctrl+T')
        self.ui.actionLoad_Translation_File.setVisible(True)

        self.ui.actionMerge_Active_Translation_with.triggered.connect(self.setMergeWithTranslatedFileName)
        self.ui.actionMerge_Active_Translation_with.setShortcut('Ctrl+M')
#        self.ui.actionSave_Translation.setShortcut('Ctrl+S')
#        self.ui.actionSave_Translation.setEnabled(False)
        self.ui.actionSave_Translation.setVisible(False)

#        self.ui.actionSave_Translation_As.setShortcut('F12')
#        self.ui.actionSave_Translation_As.setEnabled(False)
#        self.ui.actionSave_Translation_As.triggered.connect(self.setSaveTranslatedFileName)
        self.ui.actionSave_Translation_As.setVisible(False)

        self.ui.actionExtract_Original_to_txt.setShortcut('Ctrl+Alt+X')
        self.ui.actionExtract_Original_to_txt.triggered.connect(self.setExportOriginalToTxtFileName)

        self.ui.actionExtract_Translation_to_txt.setShortcut('Ctrl+X')
        self.ui.actionExtract_Translation_to_txt.triggered.connect(self.setExportToTxtFileName)

        self.ui.actionImport_Translation_from_txt.setShortcut('Ctrl+I')
        self.ui.actionImport_Translation_from_txt.triggered.connect(self.setImportFromTxtFileName)

        self.ui.actionQuit_3.triggered.connect(self.tryToCloseWin)   ## Should check for dirty bit
        self.ui.actionQuit_3.setShortcut('Ctrl+Q')

        # Show Report window Ctrl+R (total pending, total marked, total conflicting, total lines, changed lines)
        self.ui.actionReport.triggered.connect(self.showReportLog)
        self.ui.actionReport.setShortcut('Ctrl+R')

        self.ui.actionGotoLine.triggered.connect(self.showGotoToLineDlg)
        self.ui.actionGotoLine.setShortcut('Ctrl+L')

        self.ui.actionFind.triggered.connect(self.focusOnFindBox)
        self.ui.actionFind.setShortcut('Ctrl+F')
        self.ui.actionFind_Next.triggered.connect(self.findNextMatchFromClickedButton)
        self.ui.actionFind_Next.setShortcut('F3')

        # TODO: Go To next marked (up, down) Ctrl+P. Ctrl_Shift_P
        self.ui.actionFind_Next_Marked.triggered.connect(self.findNextMarkedQuote)
        self.ui.actionFind_Next_Marked.setShortcut('Ctrl+P')

        self.ui.actionFind_Previous_Marked.triggered.connect(self.findPrevMarkedQuote)
        self.ui.actionFind_Previous_Marked.setShortcut('Ctrl+Shift+P')
        # TODO: Go To next conflicted (up, down) Ctrl+E. Ctrl_Shift_E
        self.ui.actionFind_Next_Conflicted.triggered.connect(self.findNextConflictingQuote)
        self.ui.actionFind_Next_Conflicted.setShortcut('Ctrl+E')

        self.ui.actionFind_Previous_Conflicted.triggered.connect(self.findPrevConflictingQuote)
        self.ui.actionFind_Previous_Conflicted.setShortcut('Ctrl+Shift+E')

        # TODO: Go To next changed (up, down) Ctrl+G. Ctrl_Shift_G
        self.ui.actionFind_Next_Changed.triggered.connect(self.findNextChangedQuote)
        self.ui.actionFind_Next_Changed.setShortcut('Ctrl+G')

        self.ui.actionFind_Previous_Changed.triggered.connect(self.findPrevChangedQuote)
        self.ui.actionFind_Previous_Changed.setShortcut('Ctrl+Shift+G')

        # TODO: Go To next unchanged (up, down) Ctrl+U. Ctrl_Shift_U
        self.ui.actionFind_Next_Unchanged.triggered.connect(self.findNextUnchangedQuote)
        self.ui.actionFind_Next_Unchanged.setShortcut('Ctrl+U')

        self.ui.actionFind_Previous_Unchanged.triggered.connect(self.findPrevUnchangedQuote)
        self.ui.actionFind_Previous_Unchanged.setShortcut('Ctrl+Shift+U')

        self.ui.actionAbout.triggered.connect(self.showAbout)

        self.ui.backupBtn.clicked.connect(self.backupTranslationFile)

        self.ui.actionFont_crafting.triggered.connect(self.showFontsModToolDialogue)
        self.ui.actionRepacker.triggered.connect(self.showRepackerToolDialogue)

        self.enableActionsAndButtonsForAvalidSession(False)

        #
        #
        self.fillCmBxWithSupportedGames()
        self.ui.selectedEncodingTxtBx.setText(self.tryEncoding)
        self.ui.selectedEncodingTxtBx.setReadOnly(True)

        #self.ui.quoteTableViewPlcHldr.hide()
        self.ui.gridLayout_2.removeWidget(self.ui.quoteTableViewPlcHldr)
        self.ui.quoteTableViewPlcHldr.setParent(None)
        self.ui.quoteTableViewPlcHldr = None

        self.quoteTableView = MISEQuoteTableView(self.ui)
        self.ui.gridLayout_2.addWidget(self.quoteTableView, 4, 1, 1, 8)
        self.quoteTableView.show()
        tableHeaderViewInst = self.quoteTableView.horizontalHeader();
        tableHeaderViewInst.setStretchLastSection(False)
        tableHeaderViewInst.connect(tableHeaderViewInst, QtCore.SIGNAL('sectionResized(int , int , int )'),  self.handleColumnsResized)
        self.quoteTableView.connect(self.quoteTableView, QtCore.SIGNAL('resize(int, int)'),  self.tableViewResizeEvent)



        # in the end show the UI
        self.ui.show()


#        self.ui.connect(self, QtCore.SIGNAL('triggered()'), self.closeEvent)

    #
    # TODO: should check for dirty bit
    # todo: savesettings qt method?
    #           look-up QSettings Class Reference [QtCore module]
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Quit application',
            "Are you sure you want to quit?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            self.ui.closingFlag = True
            ##print "Saving Session"
            # store session settings
            if self.jSettingsInMemDict is not None:
                try:
                    self.jSettingsInMemDict['lastDesktopScreenNumber'] = QtGui.QApplication.desktop().screenNumber(self)
                except:
                    #print "Exception in detecing display"
                    self.jSettingsInMemDict['lastDesktopScreenNumber'] = 0

            if self.jSettingsInMemDict is not None and len(self.jSettingsInMemDict) > 0:
                ##print "Session has something to save"
                jSettingsDictJSONed = json.dumps(self.jSettingsInMemDict)
                if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
                    #debug
                    print "CRITICAL ERROR: The database file %s could not be found!!" % (self.DBFileNameAndRelPath)
                else:
                    conn = sqlite3.connect(self.DBFileNameAndRelPath)
                    c = conn.cursor()
                    ##print "checking for JSON"
                    c.execute("""update settings set jsonsettings=? where id = 1""", (jSettingsDictJSONed,) )
                    conn.commit()
                    c.close()
            ##print "Session Saved"
        else:
            event.ignore()
            self.ui.closingFlag = False


    #
    ## DONE: the close event should be called when [X] is clicked also!
    def tryToCloseWin(self):
        if self.ui is not None:
            self.ui.close()
        #if __name__ == '__main__':
        #    sys.exit(0)
        return

    # serves the ctrl+f shortcut
    def focusOnFindBox(self):
        self.ui.findStrTxtBx.setFocus()
        return

    # about info box:
    def showAbout(self):
        QtGui.QMessageBox.about(self, "About MISE Series Translator",
                "This application was built for the fan translation purposes of LucasArt's SoMI:SE and MI2:SE. "
                "It was made by the Classic Adventures in Greek group and is distributed freely.")
##
##
##
    def showFontsModToolDialogue(self):
        uiFontDlgFilePath = os.path.join(self.relPath, self.uiFolderName, self.uiFontsToolFileName)
        #print uiFontDlgFilePath
        if not os.access(uiFontDlgFilePath, os.F_OK) :
            print "Could not find the required ui file %s for the Font Tool application. Quiting..." % (self.uiFontsToolFileName)

        self.windowFontDLG = MyMainFontDLGWindow(self.tryEncoding, self.selGameID)
        # Set up the user interface from Designer.
        #self.uiFontsTool = uic.loadUi(uiFontDlgFilePath)
        #self.uiFontsTool.show()
        #self.uiFontsTool.setWindowIcon( self.icon )
##
##
##
    def showRepackerToolDialogue(self):
        uiRepackerToolFilePath = os.path.join(self.relPath, self.uiFolderName, self.uiRepackerToolFileName)
        #print uiRepackerToolFilePath
        if not os.access(uiRepackerToolFilePath, os.F_OK) :
            print "Could not find the required ui file %s for the Repacker Tool application. Quiting..." % (self.uiRepackerToolFileName)

        self.windowRepackerDLG = MyMainRepackerDLGWindow(self.tryEncoding, self.selGameID)
##        QtGui.QMessageBox.information(self, "Gui connection not yet implemented...",
##                "The Gui for the repacked tool is not yet implemented!")

    def showGotoToLineDlg(self):
        global listOfEnglishLinesSpeechInfo
        plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)
        if plithosOfQuotes == 0:
            QtGui.QMessageBox.critical(self, "Go to line...", "No lines were detected. Please load a file first")
            return

        text, ok = QtGui.QInputDialog.getText(self, 'Go to...',
            'Go to Line:')
        if ok and (self.parseInt(text) <> None):
            rowToGo = self.parseInt(text) - 1
            if(rowToGo < 0 or rowToGo > plithosOfQuotes - 1 ):
                QtGui.QMessageBox.critical(self, "Go to line...", "Not a valid line number")
                return
            else:
                indexToSelect = self.quoteTableView.model().index(rowToGo, 1, QModelIndex())
                self.quoteTableView.setCurrentIndex(indexToSelect)
                self.quoteTableView.setFocus()
        elif ok and self.parseInt(text) == None:
            QtGui.QMessageBox.critical(self, "Go to line...", "Not a valid line number")
            return
        return


    def showReportLog(self):
        global listOfEnglishLinesSpeechInfo
        plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)

        plithosOfQuotesConflicts = 0
        plithosOfQuotesChanged = 0
        plithosOfQuotesMarked = 0

        lm = self.quoteTableView.model()
        lmRows = lm.rowCount()
        lmCols = lm.columnCount()
        for rowi in range(0,lmRows):
            for columni in range (2,lmCols):
                indexChkBx = lm.index(rowi, columni, QModelIndex())
                itemChkBx = lm.itemFromIndex(indexChkBx)
                datoTmp = self.quoteTableView.model().data(indexChkBx).toPyObject()
                if datoTmp == True:
                    if columni == 2: # pending
                        plithosOfQuotesMarked +=1
                    elif columni == 3: # changed
                        plithosOfQuotesChanged +=1
                    elif columni == 4: # conflict
                        plithosOfQuotesConflicts +=1

        # todo: add uncomitted lines calculation
        QtGui.QMessageBox.information(self, "Translation Session Report",
                "Total Lines: %d \n" % (plithosOfQuotes) + \
                "In conflict: %d \n" % (plithosOfQuotesConflicts) + \
                "Changed: %d \n" % (plithosOfQuotesChanged) + \
                "Marked as pending: %d " % (plithosOfQuotesMarked))

    def findNextMarkedQuote(self):
        #QtGui.QMessageBox.information(self, "Find next marked quote", "not yet implemented")
        self.findNextMatchingStrLineInTable(pFindSpecialLinesMode="marked", pSearchDirection="down", pWrapAround=True )

    def findPrevMarkedQuote(self):
        #QtGui.QMessageBox.information(self, "Find previous marked quote", "not yet implemented")
        self.findNextMatchingStrLineInTable(pFindSpecialLinesMode="marked", pSearchDirection="up", pWrapAround=True )

    def findNextConflictingQuote(self):
        #QtGui.QMessageBox.information(self, "Find next conflicted quote", "not yet implemented")
        self.findNextMatchingStrLineInTable(pFindSpecialLinesMode="conflicted", pSearchDirection="down", pWrapAround=True )

    def findPrevConflictingQuote(self):
        #QtGui.QMessageBox.information(self, "Find previous conflicted quote", "not yet implemented")
        self.findNextMatchingStrLineInTable(pFindSpecialLinesMode="conflicted", pSearchDirection="up", pWrapAround=True )

    def findNextChangedQuote(self):
        #QtGui.QMessageBox.information(self, "Find next changed quote", "not yet implemented")
        self.findNextMatchingStrLineInTable(pFindSpecialLinesMode="changed", pSearchDirection="down", pWrapAround=True )


    def findPrevChangedQuote(self):
        #QtGui.QMessageBox.information(self, "Find previous changed quote", "not yet implemented")
        self.findNextMatchingStrLineInTable(pFindSpecialLinesMode="changed", pSearchDirection="up", pWrapAround=True )

    def findNextUnchangedQuote(self):
        #QtGui.QMessageBox.information(self, "Find next unchanged quote", "not yet implemented")
        self.findNextMatchingStrLineInTable(pFindSpecialLinesMode="unchanged", pSearchDirection="down", pWrapAround=True )

    def findPrevUnchangedQuote(self):
        #QtGui.QMessageBox.information(self, "Find previous unchanged quote", "not yet implemented")
        self.findNextMatchingStrLineInTable(pFindSpecialLinesMode="unchanged", pSearchDirection="up", pWrapAround=True )

    # backups the current translation file. Just a copy and a text export!
    def backupTranslationFile(self):
        global listOfEnglishLinesSpeechInfo
        plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)

        if(self.ui.openTranslatedFileNameTxtBx.text().strip() == "" ) or (not os.access(self.ui.openTranslatedFileNameTxtBx.text().strip(), os.F_OK)) :
            reply = QtGui.QMessageBox.information(self, "Backup Info", "No file to backup or file not found. Nothing to do.")
            return
        filenameTransOrig = self.ui.openTranslatedFileNameTxtBx.text().strip()
        continueToBackup = True
        #1 Confirm with info about what's gonna happen
        reply = QtGui.QMessageBox.question(self, "Backup info message", "This action will backup the active translation file and export its text to a separate .txt file.\nNote that any unsubmitted changes won't be saved in the backup native game file, but will be available in the exported text file!\nDo you want to continue?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.No:
            continueToBackup = False
        if continueToBackup == True:
            #1b export text
            #1b copy target file
            # get current timestamp, append it to translation filename before the extension, and also create a txt file with the same name for the exported text
            fileNameForCopyNative = ""
            fileNameForExportTxt = ""
            (fileNameForCopyNative, fileNameForExportTxt) = self.createAndGetBkpFilenames(filenameTransOrig)
            self._exportToFileName( fileNameForExportTxt,1,plithosOfQuotes, suppressFinalMsgbox = True)
            shutil.copyfile(filenameTransOrig, fileNameForCopyNative)
            #2 Produce success message
            reply = QtGui.QMessageBox.information(self, "Backup Info", "Backup process was completed.")
        return

    # TODO: construct a filename (or another filename) for the translation file.
    def calcTranslationFilename(self, nextVersion = False):
        return newTranslationFilename

    def fillCmBxWithSupportedGames(self):
        #
        # TODO: Inform of CRITICAL Error if not found! THEN EXIT????
        # TODO: DB initialization (Should happen once, not every time!)
        if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
            #TODO: debug and error message. Show in message box or SessionsErors and quit?
            #print "CRITICAL ERROR: The database file %s could not be found!!" % (self.DBFileNameAndRelPath)
            pass
        else:
            conn = sqlite3.connect(self.DBFileNameAndRelPath)
            c = conn.cursor()

            self.supportedGames = {}
            c.execute("select ID, Name from supportedGames order by ID")
            for row in c:
                self.supportedGames[int(row[0])]=unicode.encode("%s" % row[1],self.origEncoding)
                self.ui.selGameCmBx.addItem(self.supportedGames[int(row[0])], int(row[0]))
            # Close the cursor
            c.close()
            # TODO: Set selected game to last used (get it from db!). NOT THE DEFAULT ONE NECESSARILY!
            #
            self.setSelectedGameByGameId(self.defGameID)
        return

    #
    #
    # will return (None, None) if no match is found in the DB!
    def getFileNameAndGameIdFromMD5(self, pFullFilePath):
        foundGameId = 0
        unicodFileName = u''
        calcMD5 = self.md5_for_file(pFullFilePath)
        if calcMD5 == "":
            return (None, None)
        #debug
        #print calcMD5.upper()
        conn = sqlite3.connect(self.DBFileNameAndRelPath)
        c = conn.cursor()
        c.execute("""select GameID, origfilename, validMD5 from """ +
                            """supportedFiles WHERE validMD5 = ?""" , (calcMD5.upper(), ))
        row = c.fetchone()
        if (row is not None):
            foundGameId = int(row[0])
            unicodFileName = row[1]
        conn.commit()
        c.close()
        #debug
        #print ("%d" % foundGameId).decode(self.origEncoding) + u" :: " + unicodFileName
        return (unicodFileName, foundGameId)

    #
    # sets gameId and loads any pertinent required settings
    #
    def setSelectedGameByGameId(self, pGameId):
        index = self.ui.selGameCmBx.findData(pGameId)
        if index < 0:
            #TODO: debug and error message. Show in message box or SessionsErors and quit?
            #print "Error: Game Id index not found in combobox!"
            index = 0
        self.ui.selGameCmBx.setCurrentIndex(index)
        self.loadSelectedGameID(self.ui.selGameCmBx.currentText())
        return

    def loadSelectedGameID(self, selGameName):
        #debug
        #print "Loading game id for: %s " % selGameName
        gameIDFound = False
        for dictKey in self.supportedGames.keys():
            if self.supportedGames[dictKey] == selGameName:
                self.selGameID = dictKey
                gameIDFound = True
                #debug
                #print "Loaded %s ID: %d " %(self.supportedGames[dictKey], self.selGameID)
                break
        if gameIDFound == False:
            # TODO: Error dialog message
            #TODO: debug and error message. Show in message box or SessionsErors and quit?
            #print "Error! The selected game is not supported! Reverting to %s" % (self.supportedGames[self.defGameID])
            self.selGameID = self.defGameID
        return

    #
    # function for exporting the original Text to file
    ## DONE: Show a sucess popu at the end!
    #
    def setExportOriginalToTxtFileName(self):
        continueToExport = True
        global listOfEnglishLinesSpeechInfo
        options = QtGui.QFileDialog.Options()
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
        filename = QtGui.QFileDialog.getSaveFileName(self, self.tr('Set the output text file to export the original text into'), self.currentPath, self.tr("Text File (*.txt);;All Files (*)"), options)
        if filename:
            filename = self.fixFileNameWithOsSep(filename)
            filename = filename.strip()
            filepathSplitTbl = os.path.split(filename)
            self.currentPath = filepathSplitTbl[0]

            extension = os.path.splitext(filename)[1][1:].strip()
            if extension != 'txt':
                filename = "%s.txt" % (filename)

            plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)
            if plithosOfQuotes == 0 or self.ui.openFileNameTxtBx.text().strip() == '':
                #debug
                #print "%d %s" % (plithosOfQuotes,self.ui.openFileNameTxtBx.text().strip())
                reply = QtGui.QMessageBox.critical(self, "Information message", "No lines to export were found! Export failed!")
                continueToExport = False

            if continueToExport == True:
                #--------
                self._exportToFileName(filename, 0, plithosOfQuotes)

        return


    #
    # TODO: be disabled if no translation file is opened.
    # TODO: be disabled if no original file is opened.
    # TODO: or display warning and do nothing (if enabled by some weird chance)
    # TODO: Show a sucess popup at the end!
    # TODO: Auto save before export ? Ask the user ?
    # TODO: ti ginetai me tis kenes grammes ?
    # TODO: ti ginetai me tin telikh grammh pou mpainei kenh? (gia to import meta)
    ## DONE: meta th grammh 1886 (Oh, joy ), sthn ellhnikh metafrash bazei mia kenh grammh GIATI? = HTAN error sth metafrash (eixe mpei kai ena new line sto ellhniko quote)
    ## DONE: If file exists, prompt for overwrite: DONE
    ## DONE: save to selected txt file
    ## DONE: BUG: to A kefalaio tonomeno XANETAI!!! px: ?κουσα ότι ήσουν ένα τιποτένιο δουλικό.: SOLUTION was to export to utf-8 encoding
    def setExportToTxtFileName(self):
        continueToExport = True
        global listOfEnglishLinesSpeechInfo
        options = QtGui.QFileDialog.Options()
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
        filename = QtGui.QFileDialog.getSaveFileName(self, self.tr('Set the output text file to export the translation into'), self.currentPath, self.tr("Text File (*.txt);;All Files (*)"), options)
        if filename:
            filename = self.fixFileNameWithOsSep(filename)
            filename = filename.strip()
            filepathSplitTbl = os.path.split(filename)
            self.currentPath = filepathSplitTbl[0]

            extension = os.path.splitext(filename)[1][1:].strip()
            if extension != 'txt':
                filename = "%s.txt" % (filename)

            plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)
            if plithosOfQuotes == 0: # or self.ui.openTranslatedFileNameTxtBx.text().strip() == '':  # TODO: Restore second clause if required!
                #debug
                #print "%d %s" % (plithosOfQuotes,self.ui.openTranslatedFileNameTxtBx.text().strip())
                reply = QtGui.QMessageBox.critical(self, "Information message", "No lines to export were found! Export failed!")
                continueToExport = False
                # the overwrite case is auto handled by the dialogue
#            elif os.access(filename, os.F_OK) :
#                reply = QtGui.QMessageBox.question(self, "Information message", "This text file already exists. Do you want to overwrite it?", QtGui.QMessageBox.No | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
#                if reply == QtGui.QMessageBox.No:
#                    continueToExport = False

            if continueToExport == True:
                #--------
                self._exportToFileName(filename, 1, plithosOfQuotes)
        return

    # interval private function
    def _exportToFileName(self, pFullPathfileName, pColumnId, pPlithosOfQuotes, suppressFinalMsgbox = False):
        exportedLines = 0
        errorFound = False;
        try:
            tmpOpenFile = open(pFullPathfileName, "wb")
            try:
                for rowi in range(0,pPlithosOfQuotes):
                    index =  self.quoteTableView.model().index(rowi, pColumnId, QModelIndex())
                    datoTmp = self.quoteTableView.model().data(index).toPyObject()
                    myASCIIString = unicode.encode("%s" % datoTmp, 'utf-8')
                    myASCIIString=myASCIIString.replace("\n", "0x0A")
                    tmpOpenFile.write("%s\n" % (myASCIIString))
                    exportedLines +=1
        ##                    if rowi >= 1880 and rowi <= 1890:
        ##                        print "(%d) \'%s\'" % (rowi, myASCIIString)
            finally:
                tmpOpenFile.close()
        except IOError:
            errorFound = True

        if(not suppressFinalMsgbox):
            if not errorFound:
                if(exportedLines==pPlithosOfQuotes):
                    reply = QtGui.QMessageBox.information(self, "Export Translation Text", "Process completed successfully! Exported %d lines." % (exportedLines))
                elif(exportedLines<>pPlithosOfQuotes):
                    reply = QtGui.QMessageBox.warning(self, "Partial Export Translation Text", "Only a partial export was completed! Exported %d lines." % (exportedLines))
            else:
                reply = QtGui.QMessageBox.critical(self, "Error in Export Translation Text", "Process did not complete successfully! Exported %d lines." % (exportedLines))
        return

    # Import from selected txt file. A translation must be selected.
    # TODO: The dirty bit should be set.
    ## DONE: be disabled if no original file is opened.
    def setImportFromTxtFileName(self):
        global listOfEnglishLinesSpeechInfo
        linesToImport = 0
        numOfimportedLines = 0
        numOfimportedErrorLines = 0
        numOfimportedEmptyPaddingLines = 0 # lines after the end of a shorter than the original text file
        plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)
        if(plithosOfQuotes == 0 or self.ui.openFileNameTxtBx.text().strip()==''):
            reply = QtGui.QMessageBox.information(self, "information message", "You cannot import a translation text with no original file loaded!")
            return

        options = QtGui.QFileDialog.Options()
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
        filename = QtGui.QFileDialog.getOpenFileName(self, "Import from text file ", self.currentPath, self.tr("Text File (*.txt);;All Files (*)"), options)
        if filename:
            filename = self.fixFileNameWithOsSep(filename)
            filename = filename.strip()
            filepathSplitTbl = os.path.split(filename)
            self.currentPath = filepathSplitTbl[0]

            linesToImport = self._file_len(filename)
            tmpOpenFile = open(filename, 'rb')
            for rowi in range(0,plithosOfQuotes):
                index =  self.quoteTableView.model().index(rowi, 1, QModelIndex())
                if(rowi < linesToImport):
                    try:
                        nextline = tmpOpenFile.readline()
                        nextline = nextline.rstrip('\r\n')
                        nextline=nextline.replace("0x0A", "\n" )
                        numOfimportedLines +=1
                    except:
                        nextline = ""
                        numOfimportedErrorLines +=1
                else:
                    nextline = ""
                    numOfimportedEmptyPaddingLines +=1
                ##print "%s" s% (nextline)
                self.quoteTableView.model().setData(index, str.decode("%s" % nextline, 'utf-8'), Qt.EditRole)  # unicode(nextline, self.localGrabInstance.getActiveEncoding()))


            tmpOpenFile.close()
            reply = QtGui.QMessageBox.information(self, "Imported Translation Text", "Process completed! \n%d lines were imported out of %d. \nOf which: \nValid lines: %d \nError lines: %d (imported empty) \nEmpty padding lines: %d" % (numOfimportedLines+numOfimportedErrorLines, linesToImport, numOfimportedLines, numOfimportedErrorLines, numOfimportedEmptyPaddingLines))
            pass
        return

    #returns number of lines in file
    def _file_len(self, fname):
        i = -1
        with open(fname, 'rb') as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    #
    # Export pending lines in meta file
    #
    def exportPendingLines(self, relFullFilePath, relFileMD5):
        objListOfPending = []
        objListOfPending = self._getPendingLinesList()
        # get name of related file, get MD5 of related file,

        filepathSplitTbl = os.path.split(relFullFilePath)
        pathTosFile = filepathSplitTbl[0]
        relFileSimpleName = filepathSplitTbl[1]
        metaFileName = relFileSimpleName + ".meta"
        fullPathMetaFileName= os.path.join( pathTosFile ,  metaFileName)
        objListOfPending.insert(0, relFileMD5)
        objListOfPending.insert(0, relFileSimpleName)
        encodedList = json.dumps(objListOfPending)

        tmpOpenFile = open(fullPathMetaFileName, "wb")
        tmpOpenFile.write(encodedList)
        tmpOpenFile.flush()
        tmpOpenFile.close()
        #print "Export Pending lines: Exported %d lines to %s " % (len(objListOfPending) - 2, metaFileName)
        return


    # retrieves a list with the pending lines
    def _getPendingLinesList(self):
        global listOfEnglishLinesSpeechInfo
        plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)
        listOfLinesForPendingMarked = []
        del listOfLinesForPendingMarked[:]

        plithosOfQuotesMarked = 0

        lm = self.quoteTableView.model()
        lmRows = lm.rowCount()
        lmCols = lm.columnCount()
        for rowi in range(0,lmRows):
            indexChkBx = lm.index(rowi, 2, QModelIndex()) # column 2: pending
            itemChkBx = lm.itemFromIndex(indexChkBx)
            datoTmp = self.quoteTableView.model().data(indexChkBx).toPyObject()
            if datoTmp == True:
                plithosOfQuotesMarked +=1
                listOfLinesForPendingMarked.append(rowi)

        return listOfLinesForPendingMarked


    #
    # Import pending lines from meta file (if one exists and if a filename is given the pending lines must correspond to that files MD5!)
    # mode can be "merge" or "load"
    # WARNING: Importing the pending lines will NOT save them in the session. The user will need to press Submit first)
    def importPendingLines(self, pendFullMetaFilename, mode):
        objList = []
        if not os.access(pendFullMetaFilename, os.F_OK) :
            return objList ##silent return if no file is found
        tmpOpenFile = open(pendFullMetaFilename, "rb")
        encodedData = tmpOpenFile.read()
        tmpOpenFile.close()
        objList = json.loads(encodedData)
        if mode == "merge":
            pass
            #print "Merge mode. For file: %s, MD5 %s, Number of lines %d" % (objList[0], objList[1], len(objList) - 2)
        elif mode == "load":
            pass
            #print "Load mode. For file: %s, MD5 %s, Number of lines %d" % (objList[0], objList[1], len(objList) - 2)
        return objList


    #
    # TODO: If there is no associated original file AND the loaded original file does not match (line number at least), then prompt error.
    # TODO: Should add an association to the original file in the SQLite db or sessions xml file. And store the pending lines.
    def setSaveTranslatedFileName(self):
        options = QtGui.QFileDialog.Options()
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
        filename = QtGui.QFileDialog.getSaveFileName(self, self.tr('Set the file for the translated dialogue'), self.currentPath, self.tr("Speech, GUI, Hints File ("+filenameInfoWildCard+");;Credits File (*.credits.xml);;All Files (*)"), options)
        if filename:
            filename = self.fixFileNameWithOsSep(filename)
            filename = filename.strip()
            filepathSplitTbl = os.path.split(filename)
            self.currentPath = filepathSplitTbl[0]
            reply = QtGui.QMessageBox.information(self, "Save to Translation File", "Process NOT YET IMPLEMENTED!")
            pass
        return

    #
    # TODO: what happens if no extension is given
    # TODO: what happens if the file has more that one dots?
    def _getExtensionOfFilefullPath(self, filenamefullPath):
        extension = ""
        extension = os.path.splitext(filenamefullPath)[1][1:].strip()
##        print "extension 2: " + extension
        return extension

    def _checkConditionsForLoadOrMerge(self, mode, filenNameGiv, pGrabberForTranslationDicts):
        global listOfEnglishLinesSpeechInfo
        continueToOpen = True
        plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)
        parsedQuotesList = []

        interimStr  = ""
        parseQuotesFlag = False
        if(mode == "merge"):
            interimStr  = "merge with"
            del parsedQuotesList[:]
            parseQuotesFlag = True
        elif(mode == "open"):
            interimStr  = "load"
            parseQuotesFlag = False
        else:
            continueToOpen = False
            return continueToOpen

        if filenNameGiv:
            fileNameOrig = self.ui.openFileNameTxtBx.text().strip()
            filenNameGiv = self.fixFileNameWithOsSep(filenNameGiv)
            filenNameGiv = filenNameGiv.strip()
            # Translated file can't be the same with the original!!!!
            #debug
            #print "%s == %s" % (filenNameGiv, self.ui.openFileNameTxtBx.text().strip())
            if filenNameGiv == fileNameOrig:
                reply = QtGui.QMessageBox.critical(self, "Error message", "You cannot set the translated file to be the same file with the original!")
                continueToOpen = False
            else:
                # check extension
                filenameGivExt = self._getExtensionOfFilefullPath(filenNameGiv)
                filenaOrigExt = self._getExtensionOfFilefullPath(fileNameOrig)
                if(filenameGivExt <> filenaOrigExt):
                    reply = QtGui.QMessageBox.critical(self, "Error message", "You cannot "+interimStr+" a translation file that has a different extension than the original!")
                    continueToOpen = False
                else:
                    # check header (4 first bytes)
                    if os.access(filenNameGiv, os.F_OK) :
                        f = open(filenNameGiv, 'rb')
                        dataGiv = f.read(4)
                        if not dataGiv:
                            dataGiv = None
                        f.close()
                    if os.access(fileNameOrig, os.F_OK) :
                        # orig file
                        f = open(fileNameOrig, 'rb')
                        dataOrig = f.read(4)
                        if not dataOrig:
                            dataOrig = None
                        f.close()
                    if dataGiv == None or dataOrig == None or dataGiv <> dataOrig:
                        reply = QtGui.QMessageBox.critical(self, "Error message", "You cannot "+interimStr+" a translation file that is of a different type than the original!")
                        continueToOpen = False
                    else:
                        (quotesInLoadFile, detectedGID, parsedQuotesList) = self.getQuoteNumberInFile(filenNameGiv, parseQuotesFlag, pGrabberForTranslationDicts)
                        #debug
                        #print "load file: %d quotes, %d gameId" % (quotesInLoadFile,detectedGID)
                        if detectedGID <> self.selGameID:
                            reply = QtGui.QMessageBox.critical(self, "Error message", "You cannot "+interimStr+" a translation file that's for a different game from the original!")
                            continueToOpen = False
                        if quotesInLoadFile <> plithosOfQuotes:
                            reply = QtGui.QMessageBox.critical(self, "Error message", "You cannot "+interimStr+" a translation file that has a different number of lines from the original!")
                            continueToOpen = False
        else:
            continueToOpen = False
        return (continueToOpen, parsedQuotesList)

    #
    #  Should merge an external file with the active one. And mark any conflicting lines
    # Similar functionality with setLoadTranslatedFileName() but it won't load a new file!
    # merge functionlatiy: Print warning, markers from the imported file won't be imported (the original markers will be kept)!
    #                          a) Keep a list of the original french/lang-to-be-translated quotes in-memory, keep a list of the active translation (show changed lines)
    #                            b) Extract the quotes list from the imported file. Compare with two lists above quote by quote. For each quote:
    #                                   If same as first list then do not import
    #                                   If changed as compared to first list and
    #                                       if the second list is also changed as compared to first, then keep both SEPARATED BY NEW LINE? and MARK THE LINE AS CONFLICTED!
    #                                       if the second list is the same as the first for that quote, then import the quote from the 3rd list
    #                           Print report: Imported file contained XX changed quotes. Imported FF quotes, of which CC were merged with existing translation (marked lines) and DD were cleanly imported.
    #                       Submit should not be allowed for files with conflicted lines!
    def setMergeWithTranslatedFileName(self):
        global listOfEnglishLinesSpeechInfo
        global listOfForeignLinesOrigSpeechInfo

        foundConflicts = self._checkforConflicts()
        if foundConflicts == True:
            QtGui.QMessageBox.critical(self, "Warning message - Merge not allowed", "You cannot merge with a translation file when unresolved conflicts are pending! \nPlease, check all detected conflicts and resolve them manually, before attempting to merge with another file!")
            return

        #localGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID)
        #activeEnc = localGrabInstance.getActiveEncoding()
        continueToOpen = True

        reply = QtGui.QMessageBox.question(self, 'Merge with translation file',
            "This action will merge a translation file with the one in the active session. \nThe resulting changes won't be saved until you click on the Submit button. \nFor any conflicting lines, all translations will be listed separated by new lines, \nand the quote will be marked as conflicted for manual resolution. \nDo you want to proceed?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.No:
            return

        plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)
        if(plithosOfQuotes == 0 or self.ui.openFileNameTxtBx.text().strip()==''):
            reply = QtGui.QMessageBox.information(self, "information message", "You cannot merge with a translation file, with no original file loaded!")
            continueToOpen = False
            return
        options = QtGui.QFileDialog.Options()
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
            "Merge with Translated Dialog File ", self.currentPath,
            self.tr("Speech, GUI File ("+filenameInfoWildCard+");;Hints File (*.csv);;Credits File (*.xml);;All Files (*)"), options)
        if(filenNameGiv):
            filenNameGiv= self.fixFileNameWithOsSep(filenNameGiv)
            filenNameGiv = filenNameGiv.strip()
            filepathSplitTbl = os.path.split(filenNameGiv)
            self.currentPath = filepathSplitTbl[0]

        myParsedQuotesList = []
        del myParsedQuotesList[:]
        (continueToOpen, myParsedQuotesList) = self._checkConditionsForLoadOrMerge("merge", filenNameGiv, self.localGrabInstance)
        if continueToOpen == True:
            if (self.activeSessionID > 0) :
            #
            # The lists that we have available to compare ARE:
            # myParsedQuotesList from the imported file
            # listOfForeignLinesOrigSpeechInfo for the original FOREIGN quotes from the original file
            # and the list of quotes that are diplayed in the item model 2nd column in the table view
                numOfQuotesInImportedFile = len(myParsedQuotesList)
                numOfQuotesChangedInImportedFile= 0
                numOfQuotesChangedButIdenticalInBothFiles = 0
                numOfQuotesNotImported = 0
                numOfQuotesImported = 0
                numOfConflicts = 0
                numOfCleanImports = 0

                for rowi in range(0,numOfQuotesInImportedFile):
                    if unicode(myParsedQuotesList[rowi][0], self.activeEnc) == unicode(listOfForeignLinesOrigSpeechInfo[rowi][0], self.activeEnc) :
                        numOfQuotesNotImported +=1
                    else:
                        lm = self.quoteTableView.model()
                        numOfQuotesChangedInImportedFile+=1
                        indexOfQuoteInTable =  self.quoteTableView.model().index(rowi, 1, QModelIndex())
                        datoTmp = lm.data(indexOfQuoteInTable).toPyObject()
                        if "%s" % (datoTmp) <> unicode(listOfForeignLinesOrigSpeechInfo[rowi][0], self.activeEnc):
                            #both lines (existing and imported are changed so there may be conflict.
                            # but they could be changed and the same between them so check that too
                            if "%s" % (datoTmp) == unicode(myParsedQuotesList[rowi][0], self.activeEnc):
                                #no conflict, no import
                                numOfQuotesNotImported +=1
                                numOfQuotesChangedButIdenticalInBothFiles +=1
                                pass
                            else:
                                # Conflict!!! concatenate
                                # AND mark conflict.
                                numOfConflicts+=1
                                numOfQuotesImported +=1
                                myASCIIString = unicode.encode("%s" % datoTmp, self.activeEnc)
                                concatStr = "<<<: " + myASCIIString + "\n" + ">>>: " + myParsedQuotesList[rowi][0]
                                lm.setData(indexOfQuoteInTable,  unicode(concatStr, self.activeEnc), Qt.EditRole)
                                self.setConflictedItem(indexOfQuoteInTable)
                                pass
                        else:
                            # TODO: clean import case
                            numOfCleanImports +=1
                            numOfQuotesImported +=1
                            lm.setData(indexOfQuoteInTable, unicode(myParsedQuotesList[rowi][0], self.activeEnc), Qt.EditRole)

                if(numOfQuotesInImportedFile>0):
                    pendLinesList =[]
                    pendLinesList = self.importPendingLines(filenNameGiv +".meta" , "merge")
                    if(pendLinesList <> None and len(pendLinesList) > 2):
                        # essentially go through all lines in list and mark them
                        for rownum in pendLinesList[2:]:
                            indexOfQuoteInTable =  self.quoteTableView.model().index(rownum, 1, QModelIndex())
                            self.setPendingItem(indexOfQuoteInTable)


                    reply = QtGui.QMessageBox.information(self, "information message", "The translation file was merged sucessfully! \n"+ \
                                                            "The imported file contained: \n%d total quotes, \nof which: \n%d were changed \nand %d were uniquely changed. \n" % (numOfQuotesInImportedFile, numOfQuotesChangedInImportedFile, numOfQuotesChangedInImportedFile - numOfQuotesChangedButIdenticalInBothFiles)  + \
                                                            "Imported Lines: %d \nCleanly imported: %d \nMerged (in conflict) Lines: %d\n" % ( numOfQuotesImported, numOfCleanImports, numOfConflicts) )
                else:
                    reply = QtGui.QMessageBox.information(self, "information message", "Nothing to import!")
            else:
                reply = QtGui.QMessageBox.critical(self, "Error message", "Could not detect the active session!")
        return


    #
    #
    # This should load a native file in an existing session
    #               1. The file type should match (extension check)
    #               2. The file header should match (4 first bytes check)
    #               3. update the db for this session with the name and MD5 of the loaded file
    #               4. load that session now.
    #               The loadquotes function we checks if the translation file has less or more quotes than the original!!!
    def setLoadTranslatedFileName(self):
        global listOfEnglishLinesSpeechInfo
        #self.localGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID)
        continueToOpen = True
        plithosOfQuotes = len(listOfEnglishLinesSpeechInfo)

        reply = QtGui.QMessageBox.question(self, 'Load translation file',
            "This action will load a translation file in the active session,\nreplacing the translation file that is currently used. \nDo you want to proceed?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.No:
            return

        if(plithosOfQuotes == 0 or self.ui.openFileNameTxtBx.text().strip()==''):
            reply = QtGui.QMessageBox.information(self, "information message", "You cannot load a translation file, with no original file loaded!")
            continueToOpen = False
            return
        options = QtGui.QFileDialog.Options()
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
            "Open Translated Dialog File ", self.currentPath,
            self.tr("Speech, GUI File ("+filenameInfoWildCard+");;Hints File (*.csv);;Credits File (*.xml);;All Files (*)"), options)
        if filenNameGiv:
            filenNameGiv = self.fixFileNameWithOsSep(filenNameGiv)
            filenNameGiv = filenNameGiv.strip()
            filepathSplitTbl = os.path.split(filenNameGiv)
            self.currentPath = filepathSplitTbl[0]


        (continueToOpen, dummy0001)  = self._checkConditionsForLoadOrMerge("open", filenNameGiv, self.localGrabInstance)

        if continueToOpen == True:
            self.ui.openTranslatedFileNameTxtBx.setText(filenNameGiv)
            if(self.ui.openTranslatedFileNameTxtBx.text().strip() != ""):
                self.enableActionsAndButtonsForAvalidSession(True)
                #
                # Update the loaded session to redirect to the loaded file. Update the timestamp as well
                # Load the newly updated session again
                #
                if(self.activeSessionID > 0):
                    currSelGameID = self.selGameID
                    fileNameOrig = self.ui.openFileNameTxtBx.text().strip()
                    md5ForpOriginalfullPathsFilename = self.md5_for_file(fileNameOrig)
                    md5ForpfullcopyFileName = self.md5_for_file(filenNameGiv)
                    conn = sqlite3.connect(self.DBFileNameAndRelPath)
                    c = conn.cursor()
                    c.execute("""update translationSessions set fullPathToTransFile=?, transFileMD5=?, DateUpdated=strftime('%s','now') WHERE ID = ? and fullPathToOrigFile = ? and origFileMD5 = ? and gameID = ?""", ( filenNameGiv, md5ForpfullcopyFileName, str(self.activeSessionID), fileNameOrig, md5ForpOriginalfullPathsFilename, str(currSelGameID) ))
                    conn.commit()
                    c.close()
                    self.enableActionsAndButtonsForAvalidSession(False)
                    self.loadQuoteFileinTable()
                    pendLinesList =[]
                    pendLinesList = self.importPendingLines(filenNameGiv +".meta" , "load")
                    if(pendLinesList <> None and len(pendLinesList) > 2):
                        # essentially go through all lines in list and mark them
                        for rownum in pendLinesList[2:]:
                            indexOfQuoteInTable =  self.quoteTableView.model().index(rownum, 1, QModelIndex())
                            self.setPendingItem(indexOfQuoteInTable)


                    ##self.loadASession(pSessionName = None, pOriginalfullPathsFilename = fileNameOrig)
                    reply = QtGui.QMessageBox.information(self, "information message", "The translation file was loaded sucessfully!")
                else:
                    reply = QtGui.QMessageBox.critical(self, "Error message", "Could not detect the active session!")
            else:
                self.enableActionsAndButtonsForAvalidSession(False)
            pass
        return

    #
    # Open one of the supported Original Files.
    #
    def setOpenFileName(self):
        options = QtGui.QFileDialog.Options()
#        self.native = True
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
            "Open Original Dialog File ",
            #self.ui.openFileNameTxtBx.text(),
            self.currentPath,
            ## $4$4
##            "Speech File (*."+filenameSpeechInfo+");;GUI File (*."+filenameUIText+ ");;Hints File (*.hints.csv);;Credits File (*.credits.xml);;All Files (*)", options)
            "Speech File MI1 ("+filenameSpeechInfo+");;Speech File MI2 ("+filenameFrSpeechInfo+");;GUI File MI1 ("+filenameUIText+ ");;GUI File MI2 ("+filenameFrUIText+ ");;Hints File (*.hints.csv);;Credits File (*.credits.xml);;All Files (*)", options)

        if filenNameGiv:
            filenNameGiv= self.fixFileNameWithOsSep(filenNameGiv)
            filenNameGiv = filenNameGiv.strip()
            filepathSplitTbl = os.path.split(filenNameGiv)
            self.currentPath = filepathSplitTbl[0]

            self.ui.openFileNameTxtBx.setText(filenNameGiv)
            self.ui.openTranslatedFileNameTxtBx.setText("")
            self.enableActionsAndButtonsForAvalidSession(False)
            self.loadQuoteFileinTable()
            # we don't import pending lines in this case. It is a simple Load (from an original)
            self.currentSearchKeyword = ""

            self.ui.actionSave_Translation.setEnabled(False)
            self.ui.actionSave_Translation_As.setEnabled(False)

#			self.openFilesPath = files[0]
#			self.ui.openFileNameTxtBx.setText("[%s]" % ', '.join(files))

		## Make some local modifications.
		#self.ui.colorDepthCombo.addItem("2 colors (1 bit per pixel)")

    def fixFileNameWithOsSep(self,filename):
        p = re.compile('[/]|(\\\\)')
        sep = ''
        if os.sep == '\\':
            sep = '\\\\'
        else:
            sep = os.sep
        retFileName = p.sub(sep, filename)
        return retFileName


    def loadQuoteFileinTable(self):
        # localVar for getting the right encodings and dictionaries
        self.localGrabInstance = None

        global listOfEnglishLinesSpeechInfo
        global listOfForeignLinesOrigSpeechInfo
        global listOfUntranslatedLinesSpeechInfo
        global listOfAllLinesHintsCSV
        global listOflistsOfAllQuotesHintsCSV
        global listOfAllUntouchedLinesCredits
        global listOfIndexOfAllLinesCreds
        global listOfIndexOfAllTransLinesCreds
        global listOfLabelsSpeechInfo # for MI2
        global listOfEnglishLinesSpeechInfoOrig # for MI2
        global listOfLabelsSpeechInfoOrig # for MI2

        #Reset all tables and textboxes because if a false file is loaded nothing should appear from a possible previous loaded file.
        del listOfEnglishLinesSpeechInfo[:]
        del listOfForeignLinesOrigSpeechInfo[:]
        del listOfUntranslatedLinesSpeechInfo[:]
        del listOfAllLinesHintsCSV[:]
        del listOflistsOfAllQuotesHintsCSV[:]
        del listOfAllUntouchedLinesCredits[:]
        del listOfIndexOfAllLinesCreds[:]
        del listOfIndexOfAllTransLinesCreds[:]
        del listOfLabelsSpeechInfo[:]
        del listOfEnglishLinesSpeechInfoOrig[:]
        del listOfLabelsSpeechInfoOrig[:]

        self.ui.numOfEntriesOrigTxtBx.setText(u"0")
        if self.quoteTableView.model() <> None:
            self.quoteTableView.model().clear()
        self.quoteTableView.clearSpans()
##		MyMainWindow.MESSAGE = "<p>This will load the selected PNG file in : " \
##					"One.</p>" \
##					"<p>Two " \
##					"Three.</p>"
##		self.informationMessage()
        fullPathsFilename = self.ui.openFileNameTxtBx.text()
        ( foundOfficialFileName, foundgameid) = self.getFileNameAndGameIdFromMD5(fullPathsFilename)
        if not (foundOfficialFileName is None or foundgameid is None):
            #debug
            #print "Setting game id"
            self.setSelectedGameByGameId(foundgameid)
            self.localGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID)
            #debug
            #print "Game id was set"
            self.parseQuoteFile(fullPathsFilename, selectedLanguageOffset, self.localGrabInstance)
        else:
            self.localGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID)
        self.activeEnc = self.localGrabInstance.getActiveEncoding()
        plithosOfQuotes =len(listOfEnglishLinesSpeechInfo)
        plithosOfUntransQuotes =len(listOfUntranslatedLinesSpeechInfo)
        self.ui.numOfEntriesOrigTxtBx.setText(str(plithosOfQuotes))
        # create table
        lm = QStandardItemModel(plithosOfQuotes, 5, self)

        lm.setHeaderData(0,Qt.Horizontal, u"Original Text")
        lm.setHeaderData(1,Qt.Horizontal, u"Text to Translate")
        lm.setHeaderData(2,Qt.Horizontal, u"Pending")
        lm.setHeaderData(3,Qt.Horizontal, u"Changed")
        lm.setHeaderData(4,Qt.Horizontal, u"Conflicted")

        self.custDelegate = CheckBoxDelegate()
        self.custTextDocDelegate = TextDocDelegate()
        #
        # retrieve markers for this session!!!
        #
        rowSQLList = []
        del rowSQLList[:]
        linesToMarkList = []
        del linesToMarkList[:]
        guiLineNum = -1
        conn = sqlite3.connect(self.DBFileNameAndRelPath)
        c = conn.cursor()
        c.execute("""select LineNum from toDoLinesForSession where IDSession = ?""", (str(self.activeSessionID), ))
        rowSQLList = c.fetchall()
        if (rowSQLList is not None):
            for rowSQL in rowSQLList:
                guiLineNum = int(rowSQL[0]) # to set checked
                linesToMarkList.append(guiLineNum)
        conn.commit()
        c.close()
        ##print "LINES TO MARK: "
        ##print linesToMarkList
        ##print "active session %s" % (str(self.activeSessionID))
        #
        # end of retrieving markers
        #
        for rowi in range(0,plithosOfQuotes):
            for columni in range(0,lm.columnCount()):
                index = lm.index(rowi, columni, QModelIndex())
                tmpItem = lm.itemFromIndex(index)
#                tmpItem = QStandardItem()
                index = lm.index(rowi, columni, QModelIndex())
                if columni == 0:
#                    print listOfEnglishLinesSpeechInfo[rowi][1]
                    lm.setData(index, unicode(listOfEnglishLinesSpeechInfo[rowi][1], self.activeEnc), Qt.EditRole)
                elif columni == 1:
##                    print localGrabInstance.getActiveEncoding()
##                    print listOfEnglishLinesSpeechInfo[rowi][1]
##                    print listOfUntranslatedLinesSpeechInfo[rowi][1]
##                    print unicode(listOfUntranslatedLinesSpeechInfo[rowi][1], localGrabInstance.getActiveEncoding())
##                    lm.setData(index, unicode("", activeEnc))
                    ##print "uh oh! %d: %s" % (rowi, listOfUntranslatedLinesSpeechInfo[rowi][1])
                    if(rowi < plithosOfUntransQuotes):
                        lm.setData(index, unicode(listOfUntranslatedLinesSpeechInfo[rowi][1], self.activeEnc), Qt.EditRole)
                    else:
                        lm.setData(index, unicode("", self.activeEnc), Qt.EditRole)
                elif columni == 2:
                    tmpItem.setEditable(True)
#                    tmpItem.setCheckable(True)
                    tmpItem.setEnabled(True)
                    try:
                        i = linesToMarkList.index(rowi)
                        index.model().setData(index, True, Qt.EditRole)
                    except ValueError:
                        ##print "exception"
                        index.model().setData(index, False, Qt.EditRole) # no match
                elif columni == 3:
                    #
                    # set if changed
                    #
                    tmpItem.setEditable(False)
#                    tmpItem.setCheckable(False)
                    tmpItem.setEnabled(False)
                    if unicode(listOfUntranslatedLinesSpeechInfo[rowi][1], self.activeEnc) <> unicode(listOfForeignLinesOrigSpeechInfo[rowi][0], self.activeEnc):
                        index.model().setData(index, True, Qt.EditRole) # TODO: fill in from saved file (comparisn with original file)
                    else:
                        index.model().setData(index, False, Qt.EditRole)
                elif columni == 4:
                    tmpItem.setEditable(False)
                    tmpItem.setEnabled(False)
                    index.model().setData(index, False, Qt.EditRole)
                    pass # conflicting are only set for merge


##        for rowi in range(0,plithosOfQuotes):
##            for columni in range(2,4):
##
##                if columni == 3:
##                    tmpItem.setEditable(False)
###                    tmpItem.setCheckable(False)
##                    tmpItem.setEnabled(False)
##                    index.model().setData(index, False, Qt.EditRole) # TODO: fill in from saved file (comparisn with original file)
##                else:
##                    ##print "LALAL"
##                    tmpItem.setEditable(True)
###                    tmpItem.setCheckable(True)
##                    tmpItem.setEnabled(True)
##                    try:
##                        i = linesToMarkList.index(rowi)
##                        index.model().setData(index, True, Qt.EditRole)
##                    except ValueError:
##                        ##print "exception"
##                        index.model().setData(index, False, Qt.EditRole) # no match
###                    print "uh oh! %s " % index.model().data(index).toBool() #
###                lm.setItem(rowi,columni,tmpItem)
        self.quoteTableView.setItemDelegateForColumn(0,self.custTextDocDelegate )
        self.quoteTableView.setItemDelegateForColumn(1,self.custTextDocDelegate )
        self.quoteTableView.setItemDelegateForColumn(2,self.custDelegate )
        self.quoteTableView.setItemDelegateForColumn(3,self.custDelegate )
        self.quoteTableView.setItemDelegateForColumn(4,self.custDelegate )

##
##        for rowi in range(0,plithosOfQuotes):
##            for columni in range(2,4):
##                __tmpItem = QStandardItem()
##                __tmpItem.setCheckable(True)
##                __tmpItem.setEditable(False)
##                __tmpItem.setSelectable(False)
##                __tmpItem.setText("")
##                __tmpItem.setCheckState(Qt.Unchecked)
###                index = lm.index(rowi, columni, QModelIndex())
###                lm.setData(index, ???)
##                if columni == 3:
##                    __tmpItem.setEnabled(False)
##                lm.setItem(rowi,columni,__tmpItem)
        lm.connect(lm, QtCore.SIGNAL('itemChanged( QStandardItem *)'),  self.handleChangedItem)


       # QtCore.QObject.connect(lm, QtCore.SIGNAL("itemChanged(const QModelIndex)"), self.handleChangedItem)
        self.statusLoadingAFile = True
        highlightRulesGlobal.clearWatchers()
        self.quoteTableView.setModel(lm)
        self.restoreSessionSavedColumSizes() # this will do something only if something was saved from a last session.
        self.statusLoadingAFile = False



#   Saves the edited quotes to a copy file
#   Distinct cases for the various file types and games
#
    def handleChangedItem(self, item = None):
        #localGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID)
        #activeEnc = localGrabInstance.getActiveEncoding()
        if item == None or item.column() <> 1:
            return
        ##print "column: %d and row:  %d" % (item.column(), item.row())
        indexChangedChkbx = item.index().model().index(item.row(), 3, QModelIndex())
        datoTmp = self.quoteTableView.model().data(item.index()).toPyObject()

        if "%s" % (datoTmp) <> unicode(listOfForeignLinesOrigSpeechInfo[item.row()][0], self.activeEnc):
            indexChangedChkbx.model().setData(indexChangedChkbx, True, Qt.EditRole)
        else:
            indexChangedChkbx.model().setData(indexChangedChkbx, False, Qt.EditRole)

    #
    # TODO handleColumnsResized introduces lag when resizing columns, due to the connects to the DB.
    # TODO we don't need to constantly save in the DB! Only when closing the app (maintain a jsonsettings self variable), but we should recall settings when needed from the in-mem jsonsettings when loading files etc....
    #
    def handleColumnsResized(self, columnIndex, oldSize, newSize):
        lm = self.quoteTableView.model()
        ##scrollMargin = self.quoteTableView.autoScrollMargin()
        lmCols = lm.columnCount()
        if not self.statusLoadingAFile and not self.ignoreQuoteTableResizeEventFlg and columnIndex < lmCols -1: ## we try not to ignore last column resizes (maximize/restore case fix)
            #print "%d %d %d" % (columnIndex, oldSize, newSize)
            totalColumnWidth = 0.0
            #totalColumnWidth = self.quoteTableView.width() #0.0
            totalColumnPercentMinusLast = 0.0
            tableVertHeaderViewInst = self.quoteTableView.verticalHeader()
            vertHeaderPixels = tableVertHeaderViewInst.width()

            listOfColumnWidths = []
            del listOfColumnWidths[:]
            for coli in range(0, lmCols):
                totalColumnWidth += self.quoteTableView.columnWidth(coli)
            ##totalColumnWidth -= (vertHeaderPixels + scrollMargin)
            for coli in range(0, lmCols - 1):
                totalColumnPercentMinusLast += trunc(100*1000000* self.quoteTableView.columnWidth(coli)/totalColumnWidth)/1000000.0
                listOfColumnWidths.append( ( coli ,trunc(100*1000000* self.quoteTableView.columnWidth(coli)/totalColumnWidth)/1000000.0)  )
                #print "getting width %i: %f (%f)" % (coli, self.quoteTableView.columnWidth(coli) , trunc(100*1000000* self.quoteTableView.columnWidth(coli)/totalColumnWidth)/1000000.0)

##            listOfColumnWidths.append( ( lmCols-1 ,trunc(100*100* self.quoteTableView.columnWidth(lmCols-1)/totalColumnWidth)/100.0)  )
            #print "getting width %i: %f (%f)" % (lmCols-1, self.quoteTableView.columnWidth(lmCols-1) , trunc(100*1000000* self.quoteTableView.columnWidth(lmCols-1)/totalColumnWidth)/1000000.0)
            #print "Total width : %f" % (totalColumnWidth,)

##                    print "col: %d width: %d percent: %f" % (coli, self.quoteTableView.columnWidth(coli), trunc(100*100* self.quoteTableView.columnWidth(coli)/totalColumnWidth)/100.0 )
##                else:
##                    print "col: %d width: %d percent: %f" % (coli, self.quoteTableView.columnWidth(coli), 100 - totalColumnPercentMinusLast)


            #
            #
            # store in the jsonsettings table of the dbase the new values:
            # jSettingsDict('columnsSizes') = list()   <--- ((index, percent ), (), (), ())
            #
            #
            # TODO: this code will be called from auto-resize in the beginning, and we don't want to reset the stored values!
            #       how can we skip this?
            # TODO: on resize(from edges)/restore/maximize or on minimize are the columns also resized? We don't want to store values then. We need to set the widths to the percentages (if needed).
            # ???????????????????????????????????????????????????????????
            # UPDATE COLUMN WIDTHS IN MEM
            if(self.jSettingsInMemDict is None):
                self.jSettingsInMemDict= dict
            self.jSettingsInMemDict['columnsSizes'] = listOfColumnWidths
##                tableHeaderViewInst = self.quoteTableView.horizontalHeader();
##                tableHeaderViewInst.setStretchLastSection(False)
##                tableHeaderViewInst.setStretchLastSection(True)
##        elif self.statusLoadingAFile:
##            print "resized while loading. Ignored..."
##        else:
##            print "resized last column. Ignored..."
        return

    # TODO: consider delegate?
    def tableViewResizeEvent(self, oldWidth, newWidth):
        if not self.statusLoadingAFile and not self.ignoreQuoteTableResizeEventFlg and oldWidth!=newWidth:
            #print "tableViewResizeEvent old:%d new:%d" %(oldWidth, newWidth)
            self.restoreSessionSavedColumSizes(True)
##        elif self.statusLoadingAFile:
##            print "Ignored LOADING FILE resize  old:%d new:%d" %(oldWidth, newWidth)
##        elif self.statusLoadingAFile:
##            print "IGNORED ignore table resiz  old:%d new:%d" %(oldWidth, newWidth)
##        elif oldWidth==newWidth:
##            print "IGNORED equal width old:%d new:%d" %(oldWidth, newWidth)


    # TODO: resizing the last column causes a horizontal bar to appear. WHY?!
    #       maximizing or resizing a window the columns are not resized analogously!
    def restoreSessionSavedColumSizes(self, fromTableResizeEventCalled = False):
        noRestoreInfo = True
        scrollMargin = self.quoteTableView.autoScrollMargin()
        if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
            #debug
            print "CRITICAL ERROR: The database file %s could not be found!!" % (self.DBFileNameAndRelPath)
        else:
            #
            if self.jSettingsInMemDict.has_key('columnsSizes'):
                noRestoreInfo = False
                listOfColumnWidths = self.jSettingsInMemDict['columnsSizes']
                # ((index, percent ), (), (), ()) for all columns minus the last one
                lm = self.quoteTableView.model()
                lmCols = lm.columnCount()
                #totalColumnWidth = 0.0
                totalColumnWidth = self.quoteTableView.width() #0.0
                totalColumnWidthMinusLast = 0.0
                # get total width (we could probably get it directly from the qTableView widget
#                for coli in range(0, lmCols):
#                    totalColumnWidth += self.quoteTableView.columnWidth(coli)
#                totalColumnWidth -= scrollMargin # which is not considered in the first case (?)
                # set column widths according to the restored values from DB
                tableHeaderViewInst = self.quoteTableView.horizontalHeader()
                tableVertHeaderViewInst = self.quoteTableView.verticalHeader()
                vertHeaderPixels = tableVertHeaderViewInst.width()
                totalColumnWidth -= (vertHeaderPixels + scrollMargin)
                #print "verhead %d, scrollMarg %d" % (vertHeaderPixels, scrollMargin)
                ##tableHeaderViewInst.setStretchLastSection(False)
                self.ignoreQuoteTableResizeEventFlg = True
                for coli in range(0, lmCols-1):
                    for itemLst in listOfColumnWidths:
                        if(itemLst[0] == coli):
                            self.quoteTableView.setColumnWidth (itemLst[0], (itemLst[1] * totalColumnWidth ) / 100.0)
                            #print "setting width %i: %f " % (itemLst[0], (itemLst[1] * totalColumnWidth ) / 100.0)
                            totalColumnWidthMinusLast += (itemLst[1] * totalColumnWidth ) / 100.0
                            break
                self.quoteTableView.setColumnWidth(lmCols-1, totalColumnWidth - totalColumnWidthMinusLast -2 ) # minus 2 seems to be helping not show the bottom horizontal scroll.
                self.ignoreQuoteTableResizeEventFlg = False
                #print "setting width %i: %f " % (lmCols-1, totalColumnWidth - totalColumnWidthMinusLast -2  )
                #print "Total width : %f, table %f table minor %f " % (totalColumnWidth, self.quoteTableView.width(), self.quoteTableView.width() - (vertHeaderPixels + scrollMargin))
                ##tableHeaderViewInst.setStretchLastSection(True)
        if noRestoreInfo:
            ##print "No restore info start"
            lm = self.quoteTableView.model()
            lmCols = lm.columnCount()
#            tableHeaderViewInst.setStretchLastSection(True)
            self.ignoreQuoteTableResizeEventFlg = True
            widthForCheckboxColumns = 55
            totalColumnWidthMinusLast = 0.0
            totalColumnWidth = self.quoteTableView.width()

            tableVertHeaderViewInst = self.quoteTableView.verticalHeader()
            vertHeaderPixels = tableVertHeaderViewInst.width()
            totalColumnWidth  -= (vertHeaderPixels + scrollMargin)
            remainingColumnWidthToSplit = totalColumnWidth
            for coli in range(2, lmCols):
                remainingColumnWidthToSplit -= widthForCheckboxColumns
            halfRemainingColumnWidth = remainingColumnWidthToSplit/2.0
            self.quoteTableView.setColumnWidth(0, halfRemainingColumnWidth)
            self.quoteTableView.setColumnWidth(1, halfRemainingColumnWidth)
            totalColumnWidthMinusLast += 2*halfRemainingColumnWidth
            for coli in range(2, lmCols-1):
                ##self.quoteTableView.resizeColumnToContents(coli)
                self.quoteTableView.setColumnWidth(coli, widthForCheckboxColumns)
                totalColumnWidthMinusLast += widthForCheckboxColumns
            self.quoteTableView.setColumnWidth(lmCols - 1, totalColumnWidth - totalColumnWidthMinusLast - 3)
            self.ignoreQuoteTableResizeEventFlg = False
            ##print "No restore info end"

#            tableHeaderViewInst.setStretchLastSection(False)
        return

    def setPendingItem(self, index = None):
        if index == None or index.column() <> 1:
            return
        indexChkBx = index.model().index(index.row(), 2, QModelIndex())
        itemChkBx = index.model().itemFromIndex(indexChkBx)
        #itemChkBx.setEditable(True)
        #itemChkBx.setEnabled(True)
        indexChkBx.model().setData(indexChkBx, True, Qt.EditRole)

    def setConflictedItem(self, index = None):
        if index == None or index.column() <> 1:
            return
        indexChkBx = index.model().index(index.row(), 4, QModelIndex())
        itemChkBx = index.model().itemFromIndex(indexChkBx)
        itemChkBx.setEditable(True)
        itemChkBx.setEnabled(True)
        indexChkBx.model().setData(indexChkBx, True, Qt.EditRole)


    def _checkforConflicts(self):
        foundConflicts = False
        lm = self.quoteTableView.model()
        lmRows = lm.rowCount()
        for rowi in range(0,lmRows):
            indexChkBx = lm.index(rowi, 4, QModelIndex())
            itemChkBx = lm.itemFromIndex(indexChkBx)
            datoTmp = self.quoteTableView.model().data(indexChkBx).toPyObject()
            if datoTmp == True:
                foundConflicts = True
                break
        return foundConflicts

    #
    # Handles the submit event
    #
    def saveToLoadedQuoteFile(self):

        # TODO: Do not submit if there are CONFLICTING LINES!:
        # loop through rows, check for set conflicts!
        foundConflicts = self._checkforConflicts()
        if foundConflicts == True:
            QtGui.QMessageBox.critical(self, "Warning message - Failed to Submit", "You cannot submit a translation file with unresolved conflicts! \nPlease, check all detected conflicts and resolve them manually, before re-submitting!")
            return



        # localVar for getting the right encodings and dictionaries
        #self.localGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID)

        global listOfEnglishLinesSpeechInfo
        global listOfForeignLinesOrigSpeechInfo
        global listOfUntranslatedLinesSpeechInfo
        global listOfAllLinesHintsCSV
        global listOflistsOfAllQuotesHintsCSV

        global listOfIndexOfAllTransLinesCreds

        global listOfLabelsSpeechInfo # for MI2
        global listOfEnglishLinesSpeechInfoOrig # for MI2
        global listOfLabelsSpeechInfoOrig # for MI2

        global fullcopyFileName # we will only change this one

        plithosOfQuotes =len(listOfEnglishLinesSpeechInfo)
        if plithosOfQuotes == 0 or self.ui.openTranslatedFileNameTxtBx.text().strip() == '':
            QtGui.QMessageBox.information(self, "Information message", "Nothing to do!")
            return

        errorsEncountered = 0
        specialFlag_LIBRARY_WAS_RESORTED = False # needs to be here
        errMsg = ""
        fullPathsFilename = self.ui.openFileNameTxtBx.text()
        filepathSplitTbl = os.path.split(fullPathsFilename)
        sFilenameOnly = filepathSplitTbl[1]
        pathTosFile = filepathSplitTbl[0]

        """ parsing one of the three quote files. Putting quotes in lists.
        """
        ##########################################################################
        #  CREDITS.XML CASE
        #
        ##########################################################################
        if (sFilenameOnly in filenameCreditsList and self.selGameID==1) or (sFilenameOnly in  filenameCreditsListMISE2 and self.selGameID==2) :
            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()
            copyOFlistOfUntranslatedLinesSpeechInfo = []
            copyOFlistOfIndexOfAllTransLinesCreds = []
            del copyOFlistOfUntranslatedLinesSpeechInfo[:]
            del copyOFlistOfIndexOfAllTransLinesCreds[:]
            for tmpIt in range (0, len(listOfUntranslatedLinesSpeechInfo)):
                copyOFlistOfUntranslatedLinesSpeechInfo.append(list(listOfUntranslatedLinesSpeechInfo[tmpIt]))
            for tmpIt in range (0, len(listOfIndexOfAllTransLinesCreds)):
                copyOFlistOfIndexOfAllTransLinesCreds.append(list(listOfIndexOfAllTransLinesCreds[tmpIt]))

            beginAddrOfIndexMatrix = 0
            if self.selGameID==1:
                beginAddrOfIndexMatrix =filenameCreditsStartMatrxAddrList[filenameCreditsList.index(sFilenameOnly)]
            else:
                beginAddrOfIndexMatrix =filenameCreditsStartMISE2MatrxAddrList[filenameCreditsListMISE2.index(sFilenameOnly)]
            deviationOffset = 0 # this is multiples of 0x10 and shows how much we should add or subtract from indexes because of changes in quotes lenght (increases or reductions)
            tmpOpenFile = open(fullcopyFileName, 'r+b')
            for rowi in range(0,plithosOfQuotes):
                index =  self.quoteTableView.model().index(rowi, 1, QModelIndex())
                datoTmp = self.quoteTableView.model().data(index).toPyObject()
#                print "Line: %d. Translated text: %s" % ( rowi, datoTmp)
                myASCIIString = unicode.encode("%s" % datoTmp, self.activeEnc)
                translatedTextAsCharsListToWriteWithZeroTerm = self.makeStringIntoModifiedAsciiCharlistToBeWritten(myASCIIString, self.localGrabInstance)
                origLengthAsMultiSixteen = listOfUntranslatedLinesSpeechInfo[rowi][2] +1 # The file counts the first 0x00 after the end as a character. orig length means length of untrans text before the (any) change
                newLengthAsMultiSixteen = len(translatedTextAsCharsListToWriteWithZeroTerm)  # The file counts the first 0x00 after the end as a character.
                if origLengthAsMultiSixteen % 16 > 0:
                    origLengthAsMultiSixteen = origLengthAsMultiSixteen - (origLengthAsMultiSixteen % 16) + 0x10
                if newLengthAsMultiSixteen % 16 > 0:
                    newLengthAsMultiSixteen = newLengthAsMultiSixteen - (newLengthAsMultiSixteen % 16) + 0x10
                    while(len(translatedTextAsCharsListToWriteWithZeroTerm) < newLengthAsMultiSixteen):
                        translatedTextAsCharsListToWriteWithZeroTerm.append('\x00') # we have already appended a 0x00 in the makeStringIntoModifiedAsciiCharlistToBeWritten function
                deviationOffset = newLengthAsMultiSixteen - origLengthAsMultiSixteen

                copyOFlistOfUntranslatedLinesSpeechInfo[rowi][1] = "".join(translatedTextAsCharsListToWriteWithZeroTerm)
                if deviationOffset <> 0 :
                    #debug
                    #print "ONE SUCH CASE offset = %d for row %d " % (deviationOffset,rowi)
                    # fix the copyOFlistOfUntranslatedLinesSpeechInfo addresses
                    for myiter2 in range(0, len(copyOFlistOfUntranslatedLinesSpeechInfo)):
                        if copyOFlistOfUntranslatedLinesSpeechInfo[myiter2][0] > copyOFlistOfUntranslatedLinesSpeechInfo[rowi][0]:  #because the addresses are not stored strictly monotonously we check from the beginning and change those greater than the current one
                            copyOFlistOfUntranslatedLinesSpeechInfo[myiter2][0] += deviationOffset  # dior8wsh twn die8ynsewn enarkshs twn quotes pou epontai
                            copyOFlistOfIndexOfAllTransLinesCreds[myiter2][1] += deviationOffset
            #
            # TO DO eventually write to the file the whole structure from start address (the copyOFlistOfIndexOfAllTransLinesCreds matrix) and continue with the quotes dump
            #
            endAddress = 0
            tmpOpenFile.seek(beginAddrOfIndexMatrix)
            startpos = tmpOpenFile.tell()
##            print "%X" % startpos
            tmpWord = tmpOpenFile.read(4)
            if tmpWord == "":
                endOfFileReached = True
            else:
                readNdxEntry = unpack('<L', tmpWord)
                readNdx = readNdxEntry[0]
                quoteStartAddr = readNdx + startpos
                endAddress = quoteStartAddr
            #
            # write first indexes and hints sequences as per copyOFlistOfIndexOfAllTransLinesCreds
            #
            for myOuterIter2 in range(0, len(copyOFlistOfIndexOfAllTransLinesCreds)):
                tmpOpenFile.seek(copyOFlistOfIndexOfAllTransLinesCreds[myOuterIter2][0])
                tmpPackedIndex = pack('<L', copyOFlistOfIndexOfAllTransLinesCreds[myOuterIter2][1])
                tmpOpenFile.write(tmpPackedIndex)
            #
            # write then the dump of the quotes in the translated language as per copyOFlistOfUntranslatedLinesSpeechInfo
            #
            tmpOpenFile.seek(endAddress)
            for myiter2 in range(0, len(copyOFlistOfUntranslatedLinesSpeechInfo)):
                tmpOpenFile.seek(copyOFlistOfUntranslatedLinesSpeechInfo[myiter2][0])
                tmpOpenFile.write(copyOFlistOfUntranslatedLinesSpeechInfo[myiter2][1])
            tmpOpenFile.truncate()

            tmpOpenFile.close()
            (savedFlag, mySessionName, myFullPathToOrigFile, myFullPathToTransFile, myGameID, myID, myOrigFileMD5, myTransFileMD5) = self.createAndSaveSession(fullPathsFilename, fullcopyFileName)
            self.exportPendingLines(myFullPathToTransFile, myTransFileMD5)

#            print "Process Completed. Errors encountered %d." % errorsEncountered

        ##########################################################################
        #  CSV HINTS CASE
        # Monkey Island 1
        ##########################################################################
        elif (sFilenameOnly == filenameHintsMI1CSV  and self.selGameID==1) or (sFilenameOnly == filenameHintsMI2CSV  and self.selGameID==2):
            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()
            copyOFlistOfAllLinesHintsCSV = []
            copyOFlistOflistsOfAllQuotesHintsCSV = []
            del copyOFlistOfAllLinesHintsCSV[:]
            del copyOFlistOflistsOfAllQuotesHintsCSV[:]
            for tmpIt in range (0, len(listOfAllLinesHintsCSV)):
                copyOFlistOfAllLinesHintsCSV.append(list(listOfAllLinesHintsCSV[tmpIt]))
            for tmpIt in range (0, len(listOflistsOfAllQuotesHintsCSV)):
                copyOFlistOflistsOfAllQuotesHintsCSV.append(list(listOflistsOfAllQuotesHintsCSV[tmpIt]))

            beginAddrOfIndexMatrix = 0x76B0 # MI:SE
            if  self.selGameID==2:
                beginAddrOfIndexMatrix = 0xC6C0 # MI2:SE
            maxNumOfHintsInSeries = 4
  #          print "EECHOO EECHOO"
  #          print copyOFlistOfAllLinesHintsCSV
  #          print "EECHOO EECHOO"
            deviationOffset = 0 # this is multiples of 0x10 and shows how much we should add or subtract from indexes because of changes in quotes lenght (increases or reductions)
            tmpOpenFile = open(fullcopyFileName, 'r+b')
            for rowi in range(0,plithosOfQuotes):
                index =  self.quoteTableView.model().index(rowi, 1, QModelIndex())
                datoTmp = self.quoteTableView.model().data(index).toPyObject()
#                print "Line: %d. Translated text: %s" % ( rowi, datoTmp)
                myASCIIString = unicode.encode("%s" % datoTmp, self.activeEnc)
                translatedTextAsCharsListToWriteWithZeroTerm = self.makeStringIntoModifiedAsciiCharlistToBeWritten(myASCIIString, self.localGrabInstance)
                origLengthAsMultiSixteen = listOfUntranslatedLinesSpeechInfo[rowi][2] +1 # The file counts the first 0x00 after the end as a character.
                newLengthAsMultiSixteen = len(translatedTextAsCharsListToWriteWithZeroTerm)  # The file counts the first 0x00 after the end as a character.
                if origLengthAsMultiSixteen % 16 > 0:
                    origLengthAsMultiSixteen = origLengthAsMultiSixteen - (origLengthAsMultiSixteen % 16) + 0x10
                if newLengthAsMultiSixteen % 16 > 0:
                    newLengthAsMultiSixteen = newLengthAsMultiSixteen - (newLengthAsMultiSixteen % 16) + 0x10
                    while(len(translatedTextAsCharsListToWriteWithZeroTerm) < newLengthAsMultiSixteen):
                        translatedTextAsCharsListToWriteWithZeroTerm.append('\x00') # we have already appended a 0x00 in the makeStringIntoModifiedAsciiCharlistToBeWritten function
                deviationOffset = newLengthAsMultiSixteen - origLengthAsMultiSixteen
#                deviationOffset += diffBetweenLengths
                # find the index in the list of all quotes copyOFlistOflistsOfAllQuotesHintsCSV
                transRowMetritis = 0
                idxOfTransQuoteInWholeList = 0
                foundIdx = False
                for tmpOuterIt in range(0, len(copyOFlistOflistsOfAllQuotesHintsCSV)):
                    for tmpInnerIt in range(0, len(copyOFlistOflistsOfAllQuotesHintsCSV[tmpOuterIt])):
                        if (transRowMetritis) == rowi and (tmpOuterIt % plithosOfDifferentLanguages == selectedLanguageOffset):
                            foundIdx = True
                        if foundIdx == False:
                            if tmpOuterIt % plithosOfDifferentLanguages == selectedLanguageOffset:
                                transRowMetritis+=1
                            idxOfTransQuoteInWholeList+=1

                copyOFlistOfAllLinesHintsCSV[idxOfTransQuoteInWholeList][1] = "".join(translatedTextAsCharsListToWriteWithZeroTerm)
#                print "Line: %d. Translated text to write: %s" % (rowi, "".join(translatedTextAsCharsListToWriteWithZeroTerm))
                # shift of the rest quotes
                if deviationOffset <> 0 :
                    #debug
                    #print "ONE SUCH CASE offset = %d for row %d " % (deviationOffset,rowi)
                    # fix the copyOFlistOfAllLinesHintsCSV addresses
                    for myiter2 in range(idxOfTransQuoteInWholeList+1, len(copyOFlistOfAllLinesHintsCSV)):
                        copyOFlistOfAllLinesHintsCSV[myiter2][0] += deviationOffset  # dior8wsh twn die8ynsewn enarkshs twn quotes pou epontai
                    # also find the position of next quote within the copy of listOflistsOfAllQuotesHintsCSV
                    auksonMetritis = 0
                    for tmpOuterIt in range(0, len(copyOFlistOflistsOfAllQuotesHintsCSV)):
                        for tmpInnerIt in range(0, len(copyOFlistOflistsOfAllQuotesHintsCSV[tmpOuterIt])):
                            if(auksonMetritis > idxOfTransQuoteInWholeList):
                                copyOFlistOflistsOfAllQuotesHintsCSV[tmpOuterIt][tmpInnerIt] += deviationOffset
##                                print "Changed"
                            auksonMetritis+=1
##                    # and fix the copyOFlistOflistsOfAllQuotesHintsCSV addresses
##                    for myOuterIter2 in range(tmpOuterIt, len(copyOFlistOflistsOfAllQuotesHintsCSV)):
##                        for myInnerIter2 in range(0, len(copyOFlistOflistsOfAllQuotesHintsCSV[myOuterIter2])):
##                            if not (myOuterIter2 == tmpOuterIt and myInnerIter2 < tmpInnerIt):

            #
            # TO DO eventually write to the file the whole structure from start address 0x76B0 (the copyOFlistOflistsOfAllQuotesHintsCSV matrix) and continue with the quotes dump
            #
            tmpOpenFile.seek(beginAddrOfIndexMatrix)
            #
            # write first indexes and hints sequences as per copyOFlistOflistsOfAllQuotesHintsCSV
            #
            for myOuterIter2 in range(0, len(copyOFlistOflistsOfAllQuotesHintsCSV)):
                for myInnerIter2 in range(0, len(copyOFlistOflistsOfAllQuotesHintsCSV[myOuterIter2])):
                    tmpOpenFile.seek(beginAddrOfIndexMatrix + 0x10 * myOuterIter2 + 4*myInnerIter2)
                    tmpPackedIndex = pack('<L', copyOFlistOflistsOfAllQuotesHintsCSV[myOuterIter2][myInnerIter2] - beginAddrOfIndexMatrix - 0x10 * myOuterIter2 - 4*myInnerIter2)
                    tmpOpenFile.write(tmpPackedIndex)
            #
            # write then the dump of the quotes in all languages as per copyOFlistOfAllLinesHintsCSV
            #
#            print "EECHOO EECHOO"
 #           print copyOFlistOfAllLinesHintsCSV
#            print "EECHOO EECHOO"

            tmpOpenFile.seek(beginAddrOfIndexMatrix + 0x10 * len(copyOFlistOflistsOfAllQuotesHintsCSV))
            for myiter2 in range(0, len(copyOFlistOfAllLinesHintsCSV)):
                tmpOpenFile.seek(copyOFlistOfAllLinesHintsCSV[myiter2][0])
                tmpOpenFile.write(copyOFlistOfAllLinesHintsCSV[myiter2][1])
            tmpOpenFile.truncate()
            tmpOpenFile.close()
            (savedFlag, mySessionName, myFullPathToOrigFile, myFullPathToTransFile, myGameID, myID, myOrigFileMD5, myTransFileMD5) = self.createAndSaveSession(fullPathsFilename, fullcopyFileName)
            self.exportPendingLines(myFullPathToTransFile, myTransFileMD5)
#            print "Process Completed. Errors encountered %d." % errorsEncountered

        #
        #
        # SPEECH INFO OR UI TEXT (SoMI)
        #
        elif (sFilenameOnly == filenameSpeechInfo or sFilenameOnly == filenameUIText) and self.selGameID == 1:
            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()
            tmpOpenFile = open(fullcopyFileName, 'r+b')
            for rowi in range(0,plithosOfQuotes):
                index =  self.quoteTableView.model().index(rowi, 1, QModelIndex())
                datoTmp = self.quoteTableView.model().data(index).toPyObject()
                #print "Line: %d. Translated text: %s" % ( rowi, datoTmp)
                myASCIIString = unicode.encode("%s" % datoTmp, self.activeEnc)
                translatedTextAsCharsListToWriteWithZeroTerm = self.makeStringIntoModifiedAsciiCharlistToBeWritten(myASCIIString, self.localGrabInstance)
                #
                # H diadikasia grapsimatos se block twn 0x100 chars einai idia gia speech.info kai gia uiText.info
                # TODO: modify for hints.csv file
                # O length elegxos autos prepei na ginetai sto telika char list kai oxi auto pou metrai san 4 xarakthres ta 0xXX special escape sequences.
                if len(translatedTextAsCharsListToWriteWithZeroTerm) > 0x100: # to teliko keno yparxei hdh apo th makeStringIntoModifiedAsciiCharlistToBeWritten  0x00
                    # DEBUG
                    #print "Line: %d. Error: Cannot have more than 255 chars in translated sentence for uitext.info file"  % rowi
                    errorsEncountered +=1
                    del translatedTextAsCharsListToWriteWithZeroTerm[:]
                else:
                    while(len(translatedTextAsCharsListToWriteWithZeroTerm) < 0x100):
                        translatedTextAsCharsListToWriteWithZeroTerm.append('\x20') # we have already appended a 0x00 in the makeStringIntoModifiedAsciiCharlistToBeWritten function
                    tmpOpenFile.seek(listOfUntranslatedLinesSpeechInfo[rowi][0])
                    tmpOpenFile.write("".join(translatedTextAsCharsListToWriteWithZeroTerm))
##                    print "Line: %d. Translated text to write: %s" % (rowi, "".join(translatedTextAsCharsListToWriteWithZeroTerm))

            tmpOpenFile.close()
#            print "Process Completed. Errors encountered %d." % errorsEncountered
            (savedFlag, mySessionName, myFullPathToOrigFile, myFullPathToTransFile, myGameID, myID, myOrigFileMD5, myTransFileMD5) = self.createAndSaveSession(fullPathsFilename, fullcopyFileName)
            self.exportPendingLines(myFullPathToTransFile, myTransFileMD5)
        #
        # SPEECH INFO (MI2:SE) or textUI (MI2:SE)
        #
        elif (sFilenameOnly == filenameFrSpeechInfo and self.selGameID==2) or (sFilenameOnly == filenameFrUIText and self.selGameID == 2):
            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()
            copyOFlistOfUntranslatedLinesSpeechInfo = []
            copyOFlistOfLabelsSpeechInfo = []
            copyOFlistOfEnglishLinesSpeechInfo = []
            specialFlag_frUiText_overwriteLibraryCategRanges = False
            enClassicMonkey2FullExpectedPath = ''
            specialFlag_enClassicMonkey2FullExpectedPath_NotFound = False
            specialFlag_continueWithNoSortofLibraryClassic = False
            specialFlag_LIBRARY_WAS_RESORTED = False

            del copyOFlistOfUntranslatedLinesSpeechInfo[:]
            del copyOFlistOfLabelsSpeechInfo[:]
            del copyOFlistOfEnglishLinesSpeechInfo[:]
            for tmpIt in range (0, len(listOfUntranslatedLinesSpeechInfo)):
                copyOFlistOfUntranslatedLinesSpeechInfo.append(list(listOfUntranslatedLinesSpeechInfo[tmpIt]))
            for tmpIt in range (0, len(listOfLabelsSpeechInfo)):
                copyOFlistOfLabelsSpeechInfo.append(list(listOfLabelsSpeechInfo[tmpIt]))
            if(sFilenameOnly == filenameFrSpeechInfo):
                for tmpIt in range (0, len(listOfEnglishLinesSpeechInfo)):
                    copyOFlistOfEnglishLinesSpeechInfo.append(list(listOfEnglishLinesSpeechInfo[tmpIt]))


            if (sFilenameOnly == filenameFrUIText and self.selGameID == 2):
                # Extra snippet to compare ranges of lines (for library items) for being exactly identical or not. Applies to Ranges (711, 950) and (1026-1265) (1-based indexing) for uiText.info monkey island 2.
                # Since they are identical in the original SE, Offer to auto overwrite from 711-950 OVER the 1026-1265.
                # This is before saving!!!!
                # The GUI should be updated too
                ## DEBUG 4.7
                #print "Comparing ranges of Book categories (711, 950)  and (1026-1265) in original file..."
                nomatchCounterTmp = 0
                totalEntriesInRange = 0 # could be derived from the subtraction
                for lineFirst in range(710, 950):
                    #print "Comparing %s" % (listOfEnglishLinesSpeechInfoOrig[lineFirst],)
                    #print " with %s " % (listOfEnglishLinesSpeechInfoOrig[1025+(lineFirst-710)], )
                    #print "(%d, %d)" % (lineFirst, 1025+(lineFirst-710) )
                    if(listOfEnglishLinesSpeechInfoOrig[lineFirst] <> listOfEnglishLinesSpeechInfoOrig[1025+(lineFirst-710)]):
                        print "NO MATCH"
                        nomatchCounterTmp +=1
                    totalEntriesInRange +=1
                ## DEBUG 4.7
                #print "Final Tally. Total: %d. Unmatched: %d." % (totalEntriesInRange,nomatchCounterTmp,)
                if(nomatchCounterTmp == 0):
                    ## DEBUG
                    #print "Ranges were identical!"
                    nomatchCounterTmp = 0 # no-op


                reply = QtGui.QMessageBox.question(self, 'Library Categories: Overwrite lines 1026-1265?', \
                            "The lines (711 to 950) and (1026-1265) contain identical values in the original file. Do you want to overwrite the translated values (lines 1026-1265) with the translated values from lines 711-950?", \
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    specialFlag_frUiText_overwriteLibraryCategRanges = True
                #
                # Also ask about the classic file if not found (for library sorting)
                #
                enClassicMonkey2FullExpectedPath = os.path.join( pathTosFile ,  filenameEnClassicMonkey2001)
                if not os.access(enClassicMonkey2FullExpectedPath, os.F_OK) :
                    specialFlag_enClassicMonkey2FullExpectedPath_NotFound = True
                    reply = QtGui.QMessageBox.question(self, 'Unable to resort the library',
                    "No classic file ({0}) was detected in the same folder with the {1} file. Do you want to proceed without resorting the library?".format(filenameEnClassicMonkey2001,filenameFrUIText), QtGui.QMessageBox.Yes |
                    QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.No:
                        # prompt to copy the original classic file to the right path
                        # and return.
                        QtGui.QMessageBox.information(self, "Information message", "Process Aborted by user request! Please place the original {0} classic file in the same path with the {1} file if you want to resort the library cards.".format(filenameEnClassicMonkey2001,filenameFrUIText))
                        specialFlag_continueWithNoSortofLibraryClassic = False # for verbosity
                        return
                    else:
                        specialFlag_continueWithNoSortofLibraryClassic = True # for verbosity
                else:
                    specialFlag_enClassicMonkey2FullExpectedPath_NotFound = False  # file was found!
                    reply = QtGui.QMessageBox.question(self, 'Resort the library option',
                    "A classic file ({0}) was detected in the same folder with the {1} file. A resorted library copy can be created there. Do you want to resort the library?".format(filenameEnClassicMonkey2001,filenameFrUIText), QtGui.QMessageBox.Yes |
                    QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                    if reply == QtGui.QMessageBox.No:
                        specialFlag_continueWithNoSortofLibraryClassic = True
                    else:
                        specialFlag_continueWithNoSortofLibraryClassic = False # for verbosity


            beginAddrOfIndexMatrix = 0x4
            deviationOffset = 0 # this shows how much we should add or subtract from indexes because of changes in quotes length (increases or reductions)
            tmpOpenFile = open(fullcopyFileName, 'r+b')
            #
            for rowi in range(0,plithosOfQuotes):
                index = None
                if specialFlag_frUiText_overwriteLibraryCategRanges == True and rowi >= 1025 and rowi <= 1264:
                    index =  self.quoteTableView.model().index(710 + (rowi - 1025), 1, QModelIndex())
                    indexOverWrite = self.quoteTableView.model().index(rowi, 1, QModelIndex())
                    # TODO: update the GUI TOO (---)
                    self.quoteTableView.model().setData(indexOverWrite, unicode(listOfUntranslatedLinesSpeechInfo[710 + (rowi - 1025)][1], self.activeEnc))

                else:
                    index =  self.quoteTableView.model().index(rowi, 1, QModelIndex())
                datoTmp = self.quoteTableView.model().data(index).toPyObject()
                # print "Line: %d. Translated text: %s" % ( rowi, datoTmp)
                myASCIIString = unicode.encode("%s" % datoTmp, self.activeEnc)
                translatedTextAsCharsListToWriteWithZeroTerm = self.makeStringIntoModifiedAsciiCharlistToBeWritten(myASCIIString, self.localGrabInstance)
                # original length of foreign quote before (potentially having been edited)
                origLength = listOfUntranslatedLinesSpeechInfo[rowi][2] +1 # The file counts the first 0x00 after the end as a character. orig length means length of untrans text before the (any) change
                # new length of the same quote after potential edit
                newLength = len(translatedTextAsCharsListToWriteWithZeroTerm)  # The file counts the first 0x00 after the end as a character.
                deviationOffset = newLength - origLength

                copyOFlistOfUntranslatedLinesSpeechInfo[rowi][1] = "".join(translatedTextAsCharsListToWriteWithZeroTerm)
                if deviationOffset <> 0 :
                    # print "ONE SUCH CASE offset = %d for row %d " % (deviationOffset,rowi)
                    # fix the copyOFlistOfUntranslatedLinesSpeechInfo addresses
                    for myiter2 in range(0, len(copyOFlistOfUntranslatedLinesSpeechInfo)):
                        # [0] has the address in the file, [1] is the string and [2] is the length
                        if copyOFlistOfUntranslatedLinesSpeechInfo[myiter2][0] > copyOFlistOfUntranslatedLinesSpeechInfo[rowi][0]:  #in fr.speech.info the addresses are stored strictly monotonously. but we still check from the beginning and change those greater than the current one (similar to credits files)
                            copyOFlistOfUntranslatedLinesSpeechInfo[myiter2][0] += deviationOffset  # dior8wsh twn die8ynsewn enarkshs twn quotes pou epontai
                        if copyOFlistOfLabelsSpeechInfo[myiter2][0] > copyOFlistOfUntranslatedLinesSpeechInfo[rowi][0]:
                            copyOFlistOfLabelsSpeechInfo[myiter2][0] += deviationOffset  # dior8wsh twn die8ynsewn enarkshs twn quotes pou epontai
                        if(sFilenameOnly == filenameFrSpeechInfo):
                            if copyOFlistOfEnglishLinesSpeechInfo[myiter2][0] > copyOFlistOfUntranslatedLinesSpeechInfo[rowi][0]:
                                copyOFlistOfEnglishLinesSpeechInfo[myiter2][0] += deviationOffset  # dior8wsh twn die8ynsewn enarkshs twn quotes pou epontai
            #
            # TO DO eventually write to the file the whole structure from start address and continue with the quotes dump
            #
            endAddress = 0
            if(sFilenameOnly == filenameFrSpeechInfo):
                tmpOpenFile.seek(beginAddrOfIndexMatrix+8+12)
            else:
                tmpOpenFile.seek(beginAddrOfIndexMatrix)
            startpos = tmpOpenFile.tell()
##            print "%X" % startpos
            tmpWord = tmpOpenFile.read(4)
            if tmpWord == "":
                endOfFileReached = True
            else:
                readNdxEntry = unpack('<L', tmpWord)
                readNdx = readNdxEntry[0]
                quoteStartAddr = readNdx + startpos
                endAddress = quoteStartAddr
            #
            # write first indexes and hints sequences as per copyOFlistOfIndexOfAllTransLinesCreds
            #
            for myOuterIter2 in range(0, plithosOfQuotes):
                if(sFilenameOnly == filenameFrSpeechInfo):
                    startOfNewMatrixEnrty = beginAddrOfIndexMatrix + myOuterIter2 * 0x20
                    startOfNewEnglishLabelIndex = startOfNewMatrixEnrty + 8 +12
                    startOfNewEnglishQuoteIndex = startOfNewEnglishLabelIndex + 4
                    startOfNewFrenchQuoteIndex = startOfNewEnglishQuoteIndex + 4
                else:
                    startOfNewMatrixEnrty = beginAddrOfIndexMatrix + myOuterIter2 * 0x8  #uitext case mi2:se
                    startOfNewEnglishLabelIndex = startOfNewMatrixEnrty
                    startOfNewFrenchQuoteIndex = startOfNewEnglishLabelIndex + 4
                tmpOpenFile.seek(startOfNewEnglishLabelIndex)
                tmpPackedIndex = pack('<L', copyOFlistOfLabelsSpeechInfo[myOuterIter2][0] - startOfNewEnglishLabelIndex)
                tmpOpenFile.write(tmpPackedIndex)
                if(sFilenameOnly == filenameFrSpeechInfo):
                    tmpOpenFile.seek(startOfNewEnglishQuoteIndex)
                    tmpPackedIndex = pack('<L', copyOFlistOfEnglishLinesSpeechInfo[myOuterIter2][0] - startOfNewEnglishQuoteIndex)
                    tmpOpenFile.write(tmpPackedIndex)
                tmpOpenFile.seek(startOfNewFrenchQuoteIndex)
                tmpPackedIndex = pack('<L', copyOFlistOfUntranslatedLinesSpeechInfo[myOuterIter2][0] - startOfNewFrenchQuoteIndex)
                tmpOpenFile.write(tmpPackedIndex)
            #
            # write then the dump of the quotes in the translated language as per copyOFlistOfUntranslatedLinesSpeechInfo
            #
            ##origFile = open(fullPathsFilename, 'rb')

            tmpOpenFile.seek(endAddress)
            for myiter2 in range(0, len(copyOFlistOfUntranslatedLinesSpeechInfo)):
                # dump the original label
                ##origFile.seek(listOfLabelsSpeechInfoOrig[myiter2][0])
                ##origLabel = origFile.read(listOfLabelsSpeechInfoOrig[myiter2][2]+1)
                origLabelRaw = listOfLabelsSpeechInfoOrig[myiter2]
                tmpOpenFile.seek(copyOFlistOfLabelsSpeechInfo[myiter2][0])
                tmpOpenFile.write(origLabelRaw)
                ##tmpOpenFile.write(origLabel)
                if(sFilenameOnly == filenameFrSpeechInfo):
                    # dump the original english text
                    ##origFile.seek(listOfEnglishLinesSpeechInfoOrig[myiter2][0])
                    ##origEnglishQuote = origFile.read(listOfEnglishLinesSpeechInfoOrig[myiter2][2]+1)
                    origEnglishQuoteRaw = listOfEnglishLinesSpeechInfoOrig[myiter2]
                    tmpOpenFile.seek(copyOFlistOfEnglishLinesSpeechInfo[myiter2][0])
                    tmpOpenFile.write(origEnglishQuoteRaw)
                ##tmpOpenFile.write(origEnglishQuote)
                # and finally dump the translated text
                tmpOpenFile.seek(copyOFlistOfUntranslatedLinesSpeechInfo[myiter2][0])
                tmpOpenFile.write(copyOFlistOfUntranslatedLinesSpeechInfo[myiter2][1])
            #
            ##origFile.close()
            tmpOpenFile.truncate()
            tmpOpenFile.close()

            #
            # --------------------- RE-ORDER LIBRARY CODE ------------------------------
            #
            #
            #
            listWithUntransQuotes = []
            listWithUntransQuotesSorted = []
            listWithNewIndexesOfQuotes = []
            listWithNewIndexesOfQuotesRestoredWhoop = []

            if (sFilenameOnly == filenameFrUIText and self.selGameID == 2):
                #
                #
                # PROCEED TO SORTING!
                # TODO: maybe not such a good idea to rely on the system locale but rather set it manually?
                # TODO: question for not proceeding should be placed earlier than here!
                if not specialFlag_enClassicMonkey2FullExpectedPath_NotFound and not specialFlag_continueWithNoSortofLibraryClassic:
                    ## DEBUG 4.7
                    # print "RE-SORTING LIBRARIE - arrrrr!"
                    #
                    # classic file was found!!
                    #

                    totalEntriesInRange = 0 # could be derived from the subtraction
                    for lineFirst in range(710, 950):
                        totalEntriesInRange +=1
                        listWithUntransQuotes.append(unicode(listOfUntranslatedLinesSpeechInfo[lineFirst][1], self.activeEnc)+"__%d" % (totalEntriesInRange-1,) )

                    import locale
                    locale.setlocale(locale.LC_ALL, '')
                    listWithUntransQuotesSorted = sorted(listWithUntransQuotes, cmp=locale.strcoll)
                    ## DEBUG 4.7
                    #print listWithUntransQuotesSorted;
                    for tmpitit in range(0, len(listWithUntransQuotesSorted)):
                        tokensOfSortedQuote = unicode.rpartition(listWithUntransQuotesSorted[tmpitit], '__')
                        listWithNewIndexesOfQuotes.append(int(tokensOfSortedQuote[2]))
                    ## debug 4.7
                    #print listWithNewIndexesOfQuotes # includes a 0 index, and goes up to 239



                    # CAREFUL WE HAVE SOME SPECIAL CASES FOR THE SE VERSION!!!!!!!!!!!!!!!!!!!!
                    # Mountains \n`The Majesty of the Sierras`				 	                    MOVED FROM 114 (original) to  237 (SE) ==> (zero based)  113 -> 236
                    # Obscenity \n`&$*#!` \nSymbolic equivalents \nof obscene words \nand phrases.  MOVED FROM 133 (original) to  238 (SE) ==> (zero based)  132 -> 237
                    # Noises \n`A Definitive Guide to \nCartoon Noises`			                    MOVED FROM 125 (original) to  239 (SE) ==> (zero based)  124 -> 238
                    # Noogies \n`How to Give \nGreat Noogies`						                MOVED FROM 126 (original) to  240 (SE) ==> (zero based)  125 -> 239
                    # --> So.. the last one (240 original) is in 236 index place of SE
                    # We build a mapping list. listMapOrigIndexToSE[indexInOriginalSE] = indexInOriginalClassic
                    # by usind the index() we can find where an SE index corresponds to in the classic version!
                    listMapOrigIndexToSE = []
                    del listMapOrigIndexToSE[:]
                    listMapOrigIndexToSE = range(0,240);
                    troglOffset = 0
                    for troglIdx in range(0,240):
                        if troglIdx == 113:
                            listMapOrigIndexToSE[troglIdx] = 236
                            troglOffset -= 1
                        elif troglIdx == 124:
                            listMapOrigIndexToSE[troglIdx] = 238
                            troglOffset -= 1
                        elif troglIdx == 125:
                            listMapOrigIndexToSE[troglIdx] = 239
                            troglOffset -= 1
                        elif troglIdx == 132:
                            listMapOrigIndexToSE[troglIdx] = 237
                            troglOffset -= 1
                        else:
                            listMapOrigIndexToSE[troglIdx] = troglIdx + troglOffset
                    # use the index to get the SE to Orig Index map
                    listMapSEIndexToOrig = []
                    del listMapSEIndexToOrig[:]
                    listMapSEIndexToOrig = range(0,240);
                    for troglIdx in range(0,240):
                        listMapSEIndexToOrig[troglIdx] = listMapOrigIndexToSE.index(troglIdx)
                    ## DEBUG 4.7
                    #print listMapSEIndexToOrig

                    #
                    # Due to changes in SE, the position o big whoop in SE (zero based is 187! - see above).id in original is 191 (zero based)
                    #
                     # Also the "Famous Pirate Quotations should remain with the same id? (the one on the governors belly on Phatt)
                    # id in SE (zero-based) is 142. id in original is (zero-based) 146
                    #
                    # Also the "Joy of Hex" should remain with the same id? (the one you have to give to the voodoo lady)
                    # id in SE (zero-based) is 145. id in original is (zero-based) 149
                    origPirateQuotsPosInSEZerobased = 142
                    origPirateQuotsPosInClassicZeroBased = 146
                    origJoyOfHexPosInSEZerobased = 145
                    origJoyOfHexPosInClassicZeroBased = 149
                    origWhoopPosInSEZerobased = 187
                    origWhoopPosInClassicZeroBased = 191


                    if listWithNewIndexesOfQuotes[origWhoopPosInClassicZeroBased] != origWhoopPosInSEZerobased \
                        or listWithNewIndexesOfQuotes[origPirateQuotsPosInClassicZeroBased] != origPirateQuotsPosInSEZerobased \
                        or listWithNewIndexesOfQuotes[origJoyOfHexPosInClassicZeroBased] != origJoyOfHexPosInSEZerobased:
                        ## DEBUG 4.7
##                        newWhoopPosInSEZeroBased = 0
##                        newPirateQuotsPosInSEZeroBased = 0
##                        newJoyOfHexPosInSEZeroBased = 0
##                        for ikid in range(0,len(listWithNewIndexesOfQuotes)):
##                            if listWithNewIndexesOfQuotes[ikid] == origWhoopPosInSEZerobased:
##                                newWhoopPosInSEZeroBased = ikid
##                                break
##                        print "New whoop Pos {0}".format(newWhoopPosInSEZeroBased)
##                        for ikid in range(0,len(listWithNewIndexesOfQuotes)):
##                            if listWithNewIndexesOfQuotes[ikid] == origPirateQuotsPosInSEZerobased:
##                                newPirateQuotsPosInSEZeroBased = ikid
##                                break
##
##                        print "New pirate quotes Pos {0}".format(newPirateQuotsPosInSEZeroBased)
##                        for ikid in range(0,len(listWithNewIndexesOfQuotes)):
##                            if listWithNewIndexesOfQuotes[ikid] == origJoyOfHexPosInSEZerobased:
##                                newJoyOfHexPosInSEZeroBased = ikid
##                                break
##
##                        print "New joy of Hex Pos {0}".format(newJoyOfHexPosInSEZeroBased)
                        ## END DEBUG
                        listWithNewIndexesOfQuotesRestoredWhoop = listWithNewIndexesOfQuotes[:]
                        listWithNewIndexesOfQuotesRestoredWhoop.remove(origWhoopPosInSEZerobased)
                        listWithNewIndexesOfQuotesRestoredWhoop.remove(origJoyOfHexPosInSEZerobased)
                        listWithNewIndexesOfQuotesRestoredWhoop.remove(origPirateQuotsPosInSEZerobased)
                        # order of insert matters
                        listWithNewIndexesOfQuotesRestoredWhoop.insert(origPirateQuotsPosInClassicZeroBased,origPirateQuotsPosInSEZerobased)
                        listWithNewIndexesOfQuotesRestoredWhoop.insert(origJoyOfHexPosInClassicZeroBased,origJoyOfHexPosInSEZerobased)
                        listWithNewIndexesOfQuotesRestoredWhoop.insert(origWhoopPosInClassicZeroBased,origWhoopPosInSEZerobased)


                    else:
                        listWithNewIndexesOfQuotesRestoredWhoop = listWithNewIndexesOfQuotes[:]



                    ## DEBUG 4.7
                    #print listWithNewIndexesOfQuotesRestoredWhoop # includes a 0 index, and goes up to 239

                    #
                    # continuing tmp snippet
                    #
                    # Find the addresses within the classic game files. (SCRP_0063, SCRP_0064, LSCR_0207) where these scripts start
                    # (INFO:)
                    # TODO: the command should ask for the location of the classic files.
                    #       For now, it assumes that they are in the same folder as the loaded filenameFrUIText file.
                    #       We should only need the 'monkey2.001'. Files are assumed xored with 0x69
                    #       Also for opCodes reference: http://wiki.scummvm.org/index.php/SCUMM/V5_opcodes
                    #
                    # 1. create decoding function for read buffer (xor every byte)
                    # 2. create encoding function for preparing buffer to write back (to copy file) (xor every byte)
                    # 3. create function to replace (in-place) a new value for index/orders of books in read buffer.
                    # 4. test test
                    # Titles:
                    # SCRP in monkey2.001 at 2425324 (0x002501EC)
                    #	size 8616 (0x000021A8)
                    #
                    # SPEECHES ANA BIBLIO:
                    # SCRP in monkey2.001 at 2479437 (0x0025D54D)
                    #	size 15401 (0x00003C29)
                    #
                    # Categories and "by " and "see ":
                    # LSCR in monkey2.001 at 2557091 (0x002704A3)
                    #	size 9326 (0x0000246E)

                    if os.access(enClassicMonkey2FullExpectedPath, os.F_OK) :
                        f = open(enClassicMonkey2FullExpectedPath, 'rb')
                        wholeDataClassicEnM2Giv = f.read()
                        if not wholeDataClassicEnM2Giv:
                            wholeDataClassicEnM2Giv = None
                        f.close()

                    ## ^^^+++
                    ## Header (4 bytes, big endian)
                    tmpHeaderWord = ""
                    startAddrOfM2Class_SCRP_0063 = 0x002501EC;
                    tmpHeaderWord = self.myFileBuffRead(wholeDataClassicEnM2Giv, startAddrOfM2Class_SCRP_0063, 4)

                    if tmpHeaderWord == "":
                        print "Debug: End of Classic File"
                    else:
                        datumUnpacked = unpack('>L', tmpHeaderWord)  # little endianess - read with the order given
                        datumHex = datumUnpacked[0]
                        datumHexUnCode = datumHex ^ 0x69696969
                        ## DEBUG 4.7
                        #print "datumHexUnCode is {0}".format(datumHexUnCode)
                        #print "datumHexCode (hex): %X" % datumHex
                        #print "datumHexUnCode (hex): %08X" % datumHexUnCode
                    ## Length (4 bytes, big endian)
                    scrp063Length = 0
                    tmpLengthWord = ""
                    tmpLengthWord = self.myFileBuffRead(wholeDataClassicEnM2Giv, startAddrOfM2Class_SCRP_0063+4, 4)

                    if tmpLengthWord == "":
                        print "Debug: End of Classic File"
                    else:
                        datumUnpacked = unpack('>L', tmpLengthWord)  # little endianess - read with the order given
                        datumHex = datumUnpacked[0]
                        datumHexUnCode = datumHex ^ 0x69696969
                        scrp063Length = datumHexUnCode
                        ## DEBUG 4.7
                        #print "Size is {0}".format(datumHexUnCode)
                    #
                    #
                    # decode classic file in buffer
                    wholeDataClassic_SCRP_0063 = self.scummDecodeIndexFile(wholeDataClassicEnM2Giv, startAddrOfM2Class_SCRP_0063, scrp063Length)

                    ## DEBUG
                    ##print "Decoding complete"  # print first 32 decoded chars
                    ##for yiyi in wholeDataClassic_SCRP_0063[0:32]:
                    ##    datumUnpacked = unpack('B', yiyi)  # little endianess - read with the order given
                    ##    datumHex = datumUnpacked[0]
                    ##    print "datumHexUnCode (hex): %02X" % datumHex
                    ## END OF DEBUG

                    #
                    # call handling function to parse commands, store the interesting in a table, count the unknown commands.
                    #
                    listIndexToAddresses_0063 = []
                    del listIndexToAddresses_0063[:]
                    listIndexToAddresses_0064 = []
                    del listIndexToAddresses_0064[:]
                    listIndexToAddresses_0207= []
                    del listIndexToAddresses_0207[:]

                    # list index contains items (x,y) where x is the index of the book, and y is the starting address where the index is stored in the buffer. Indexes are 2-bytes. (unsigned short 'H')
                    listIndexToAddresses_0063 = self.parseDecodedFileBuffer(wholeDataClassic_SCRP_0063[:], 'SCRP_0063')

                    ###
                    # FOR SCRP_0064 REPEAT
                    ###
                    tmpHeaderWord = ""
                    startAddrOfM2Class_SCRP_0064 = 0x0025D54D;
                    tmpHeaderWord = self.myFileBuffRead(wholeDataClassicEnM2Giv, startAddrOfM2Class_SCRP_0064, 4)

                    if tmpHeaderWord == "":
                        print "Debug: End of Classic File"
                    else:
                        datumUnpacked = unpack('>L', tmpHeaderWord)  # little endianess - read with the order given
                        datumHex = datumUnpacked[0]
                        datumHexUnCode = datumHex ^ 0x69696969
                        ## DEBUG 4.7
                        #print "datumHexUnCode is {0}".format(datumHexUnCode)
                        #print "datumHexCode (hex): %X" % datumHex
                        #print "datumHexUnCode (hex): %08X" % datumHexUnCode
                    ## Length (4 bytes, big endian)
                    scrp064Length = 0
                    tmpLengthWord = ""
                    tmpLengthWord = self.myFileBuffRead(wholeDataClassicEnM2Giv, startAddrOfM2Class_SCRP_0064+4, 4)

                    if tmpLengthWord == "":
                        print "Debug: End of Classic File"
                    else:
                        datumUnpacked = unpack('>L', tmpLengthWord)  # little endianess - read with the order given
                        datumHex = datumUnpacked[0]
                        datumHexUnCode = datumHex ^ 0x69696969
                        scrp064Length = datumHexUnCode
                        ## DEBUG 4.7
                        #print "Size is {0}".format(datumHexUnCode)
                    #
                    #
                    # decode classic file in buffer
                    wholeDataClassic_SCRP_0064 = self.scummDecodeIndexFile(wholeDataClassicEnM2Giv, startAddrOfM2Class_SCRP_0064, scrp064Length)
                    # list index contains items (x,y) where x is the index of the book, and y is the starting address where the index is stored in the buffer. Indexes are 2-bytes. (unsigned short 'H')
                    listIndexToAddresses_0064 = self.parseDecodedFileBuffer(wholeDataClassic_SCRP_0064[:], 'SCRP_0064')


                    #####
                    # FOR LSCR_0207 REPEAT
                    #######
                    tmpHeaderWord = ""
                    startAddrOfM2Class_LSCR_0207 = 0x002704A3;
                    tmpHeaderWord = self.myFileBuffRead(wholeDataClassicEnM2Giv, startAddrOfM2Class_LSCR_0207, 4)

                    if tmpHeaderWord == "":
                        print "Debug: End of Classic File"
                    else:
                        datumUnpacked = unpack('>L', tmpHeaderWord)  # little endianess - read with the order given
                        datumHex = datumUnpacked[0]
                        datumHexUnCode = datumHex ^ 0x69696969
                        #print "datumHexUnCode is {0}".format(datumHexUnCode)
                        #print "datumHexCode (hex): %X" % datumHex
                        ## DEBUG 4.7
                        #print "datumHexUnCode (hex): %08X" % datumHexUnCode
                    ## Length (4 bytes, big endian)
                    lscr0207Length = 0
                    tmpLengthWord = ""
                    tmpLengthWord = self.myFileBuffRead(wholeDataClassicEnM2Giv, startAddrOfM2Class_LSCR_0207+4, 4)

                    if tmpLengthWord == "":
                        print "Debug: End of Classic File"
                    else:
                        datumUnpacked = unpack('>L', tmpLengthWord)  # little endianess - read with the order given
                        datumHex = datumUnpacked[0]
                        datumHexUnCode = datumHex ^ 0x69696969
                        lscr0207Length = datumHexUnCode
                        ## DEBUG 4.7
                        #print "Size is {0}".format(datumHexUnCode)
                    #
                    #
                    # decode classic file in buffer
                    wholeDataClassic_LSCR_0207 = self.scummDecodeIndexFile(wholeDataClassicEnM2Giv, startAddrOfM2Class_LSCR_0207, lscr0207Length)
                    # list index contains items (x,y) where x is the index of the book, and y is the starting address where the index is stored in the buffer. Indexes are 2-bytes. (unsigned short 'H')
                    listIndexToAddresses_0207 = self.parseDecodedFileBuffer(wholeDataClassic_LSCR_0207[:], 'LSCR_0207')


                    for bizit in range(0, len(listWithNewIndexesOfQuotesRestoredWhoop)):
                        # bizit counts the new index in the original classic files. (object ids)
                        # since object 191 (zero based) should not be changed (directions from hungarian team)
                        # we must verify what happens for this special case!
                        # we assume/know that the indexes are incremental in the ORIGINAL classic files (we don't open modified ones - otherwise we need more loops here!)
                        # TODO: cater for modified classic files!!! (Actually i think that this would work anyway, since we always rewrite all positions.
                        newIndex = bizit+1
                        indexOfOrigToBeReplacedZB = listMapSEIndexToOrig[listWithNewIndexesOfQuotesRestoredWhoop[bizit]]
                        (oldindex, indx_addres) = listIndexToAddresses_0063[indexOfOrigToBeReplacedZB]
                        #print "bizzit == {0}. indexOfOrigToBeReplacedZB == {1}".format(bizit, indexOfOrigToBeReplacedZB)
                        ## DEBUG 4.7 - big whoop and pirate quotes and joy of hex
##                        if indexOfOrigToBeReplacedZB == 191: # big whoop id (zero based)
##                            print "Old big whoop id -zb-: {0}, new big whoop id -zb- {1}".format(indexOfOrigToBeReplacedZB, newIndex-1)
##                            if indexOfOrigToBeReplacedZB == newIndex-1:
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                                print " WHOOP IS SAME"
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                            else:
##                                print "***************************************************"
##                                print "..................................................."
##                                print " WHOOP IS DIFFERENT"
##                                print "..................................................."
##                                print "***************************************************"
##
##                        if indexOfOrigToBeReplacedZB == 146: # pirate quotes id (zero based)
##                            print "Old pirate quotes id -zb-: {0}, new pirate quotes id -zb- {1}".format(indexOfOrigToBeReplacedZB, newIndex-1)
##                            if indexOfOrigToBeReplacedZB == newIndex-1:
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                                print " PIRATE QUOTES IS SAME"
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                            else:
##                                print "***************************************************"
##                                print "..................................................."
##                                print " PIRATE QUOTES IS DIFFERENT"
##                                print "..................................................."
##                                print "***************************************************"
##                        if indexOfOrigToBeReplacedZB == 149: # Joy of HEX id (zero based)
##                            print "Old pirate quotes id -zb-: {0}, new pirate quotes id -zb- {1}".format(indexOfOrigToBeReplacedZB, newIndex-1)
##                            if indexOfOrigToBeReplacedZB == newIndex-1:
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                                print " Joy of HEX IS SAME"
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
##                            else:
##                                print "***************************************************"
##                                print "..................................................."
##                                print " Joy of HEX IS DIFFERENT"
##                                print "..................................................."
##                                print "***************************************************"
                        ## END OF DEBUG 4.7
                        listIndexToAddresses_0063[indexOfOrigToBeReplacedZB] = (newIndex, indx_addres)
                        self.myFileBuffWriteShort(wholeDataClassic_SCRP_0063,indx_addres, pack('<H', newIndex))
                        (oldindex, indx_addres) = listIndexToAddresses_0064[indexOfOrigToBeReplacedZB]
                        listIndexToAddresses_0064[indexOfOrigToBeReplacedZB] = (newIndex, indx_addres)
                        self.myFileBuffWriteShort(wholeDataClassic_SCRP_0064,indx_addres, pack('<H', newIndex))
                        (oldindex, indx_addres) = listIndexToAddresses_0207[indexOfOrigToBeReplacedZB]
                        listIndexToAddresses_0207[indexOfOrigToBeReplacedZB] = (newIndex, indx_addres)
                        self.myFileBuffWriteShort(wholeDataClassic_LSCR_0207,indx_addres, pack('<H', newIndex))

                    # here we have the separate DECODED buffers with the files and the new indexes.
                    # we neeed to
                    # 1. Encode the separate files
                    # 2. Place them in-place in the original (a copy) classic file.
                    grCopyClassicMonkey2FullExpectedPath = os.path.join( pathTosFile ,  "{0}-copy".format(filenameEnClassicMonkey2001))
                    shutil.copyfile(enClassicMonkey2FullExpectedPath, grCopyClassicMonkey2FullExpectedPath)
                    file_grM2Cl = open(grCopyClassicMonkey2FullExpectedPath, 'r+b')
                    file_grM2Cl.seek(startAddrOfM2Class_SCRP_0063) #SCRP_0063
                    file_grM2Cl.write("".join(  self.scummEncodeIndexFile(wholeDataClassic_SCRP_0063) ) )
                    file_grM2Cl.seek(startAddrOfM2Class_SCRP_0064) #SCRP_0064
                    file_grM2Cl.write("".join(  self.scummEncodeIndexFile(wholeDataClassic_SCRP_0064) ) )
                    file_grM2Cl.seek(startAddrOfM2Class_LSCR_0207) #LSCR_0207
                    file_grM2Cl.write("".join(  self.scummEncodeIndexFile(wholeDataClassic_LSCR_0207) ) )
                    file_grM2Cl.close()

                    specialFlag_LIBRARY_WAS_RESORTED = True # set the flag, for adding info in the final report.

                    ## DEBUG 4.7
                    #print listIndexToAddresses_0063
                    #print listIndexToAddresses_0064
                    #print listIndexToAddresses_0207
##                    self.parseDecodedFileBuffer(wholeDataClassic_SCRP_0063[:], 'SCRP_0063')
##                    self.parseDecodedFileBuffer(wholeDataClassic_SCRP_0064[:], 'SCRP_0064')
##                    self.parseDecodedFileBuffer(wholeDataClassic_LSCR_0207[:], 'LSCR_0207')
                    ## END OF DEBUG

            #
            # --------------------- END OF RE-ORDER LIBRARY CODE ------------------------
            #
            (savedFlag, mySessionName, myFullPathToOrigFile, myFullPathToTransFile, myGameID, myID, myOrigFileMD5, myTransFileMD5) = self.createAndSaveSession(fullPathsFilename, fullcopyFileName)
            self.exportPendingLines(myFullPathToTransFile, myTransFileMD5)

        #
        # Result status messageBox:
        #
        if errorsEncountered == 0:
            if specialFlag_LIBRARY_WAS_RESORTED:
                QtGui.QMessageBox.information(self, "Information message", "Process Completed. No errors encountered! Additionally, the library was resorted. Please copy the {0}-copy file to the classic/en folder of the game and rename it to {0}.".format(filenameEnClassicMonkey2001))
            else:
                QtGui.QMessageBox.information(self, "Information message", "Process Completed. No errors encountered!")
        else:
            QtGui.QMessageBox.information(self, "Warning message", "Process Completed, but %d errors were encountered!" % (errorsEncountered))
        return
    ####################################
    # SEARCH FIND REPLACE HIGHLIGHT
    #
    ####################################

    def initHighlightRules(self):
        highlightRulesGlobal.clearConstantRules()
        ##return
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkBlue)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)

        keywordPatterns = ["\\bBig Whoop\\b",
                "\\bPhatt\\b", "\\bDinky\\b", "\\bScabb\\b", "\\bBooty\\b",
                 "\\bDread\\b", "\\bKate\\b", "\\bCapsize\\b", "\\bToothrot\\b", "\\bHerman\\b",
                 "\\bElaine\\b", "\\bMarley\\b", "\\bAugustus\\b", "\\bDeWaat\\b", "\\bWally\\b", "\\bMarty\\b",
                  "\\bLargo\\b", "\\bLaGrande\\b", "\\bRapp\\b", "\\bScallion\\b",  "\\bJojo\\b", "\\bStan\\b",
                  "\\bMonkey Island\\b", "\\bMonkey 1\\b", "\\bMad Monkey\\b", "\\bLong John Silver\\b",
                  "\\bFink\\b" , "\\bBart\\b",
                  "\\bJean\\b","\\bLouise\\b","\\bCarrie\\b","\\bJim\\b", "\\bMcDow\\b", "\\bNibbles\\b", "\\bButtonhead\\b", "\\bHank\\b", "\\bPlank\\b", "\\bBill\\b",
                  "\\bBarney\\b","\\bGout\\b", "\\bFester\\b","\\bLeach\\b", "\\bGordo\\b", "\\bSkunk[-]Eye\\b",
                  "\\bRICKETTS\\b", "\\bQUAGMYRES\\b", "\\bGROUTS\\b"]

        for patternExpStr in keywordPatterns:
            highlightRulesGlobal.addHighlightRule(patternExpStr, keywordFormat, caseSensitivity = True)

        keywordPatternsIS = ["\\bguybrush\\b", "\\bthreepwood\\b", "\\blechuck\\b", "\\bchuckie\\b"]
        for patternExpStr in keywordPatternsIS:
            highlightRulesGlobal.addHighlightRule(patternExpStr, keywordFormat, caseSensitivity = False)

##        classFormat = QtGui.QTextCharFormat()
##        classFormat.setFontWeight(QtGui.QFont.Bold)
##        classFormat.setForeground(QtCore.Qt.darkMagenta)
##        highlightRulesGlobal.addHighlightRule("\\bQ[A-Za-z]+\\b", classFormat)

##        singleLineCommentFormat = QtGui.QTextCharFormat()
##        singleLineCommentFormat.setForeground(QtCore.Qt.red)
##        highlightRulesGlobal.addHighlightRule("//[^\n]*", singleLineCommentFormat)

        quotationFormat = QtGui.QTextCharFormat()
        quotationFormat.setForeground(QtCore.Qt.darkGreen)
        #highlightRulesGlobal.addHighlightRule("\"(.*)\"", quotationFormat)
        highlightRulesGlobal.addHighlightRule( r'[\s]("([^\\"]|\\.)*")|(^"([^\\"]|\\.)*")', quotationFormat)
        highlightRulesGlobal.addHighlightRule( r"[\s](`([^\\`]|\\.)*`)|(^`([^\\`]|\\.)*`)", quotationFormat)
        highlightRulesGlobal.addHighlightRule( r"\\n(`([^\\`]|\\.)*`)|(^`([^\\`]|\\.)*`)", quotationFormat)
        highlightRulesGlobal.addHighlightRule( r"[\s]('([^\\']|\\.)*')|(^'([^\\']|\\.)*')", quotationFormat)
        highlightRulesGlobal.addHighlightRule( r"([\sA-Za-z0-9]+)0x94", quotationFormat)

        specialCharsFormat = QtGui.QTextCharFormat()
        specialCharsFormat.setFontItalic(True)
        specialCharsFormat.setForeground(QtCore.Qt.blue)
#        highlightRulesGlobal.addHighlightRule(r"(0x[A-Fa-f0-9]{2})|(\\n)", specialCharsFormat)
        highlightRulesGlobal.addHighlightRule(r"(0x[A-F0-9]{2})|(\\n)", specialCharsFormat)

# {var:global_269} {string:global_39} {var:local_1}
        ingameVariablesFormat = QtGui.QTextCharFormat()
        ingameVariablesFormat.setForeground(QtCore.Qt.red)
        highlightRulesGlobal.addHighlightRule(r"{var:[^}]*}", ingameVariablesFormat)
        highlightRulesGlobal.addHighlightRule(r"\{verb:[^\}]*\}", ingameVariablesFormat)
        highlightRulesGlobal.addHighlightRule(r"\{string:[^\}]*\}", ingameVariablesFormat)

##        functionFormat = QtGui.QTextCharFormat()
##        functionFormat.setFontItalic(True)
##        functionFormat.setForeground(QtCore.Qt.blue)
##        highlightRulesGlobal.addHighlightRule("\\b[A-Za-z0-9_]+(?=\\()", functionFormat)

    def searchModeToggled(self, stateChecked):
        if(stateChecked):
            ##print "search Mode enabled", self.ui.searchModeRB.isChecked()
            self.ui.replaceAllInQuotesBtn.hide()
            self.ui.replaceInQuotesBtn.hide()
            self.ui.replaceWithStrTxtBx.hide()
            self.ui.replaceWithLbl.hide()
            self.ui.findReplaceLbl.setText("Find:")
        return

    def replaceModeToggled(self, stateChecked):
        if(stateChecked):
            ##print "replace Mode enabled", self.ui.replaceModeRB.isChecked()
            self.ui.replaceAllInQuotesBtn.show()
            self.ui.replaceInQuotesBtn.show()
            self.ui.replaceWithStrTxtBx.show()
            self.ui.replaceWithLbl.show()
            self.ui.findReplaceLbl.setText("Replace:")
        return

    def replaceOnceMatchClickedButton(self, checked):
        ##print "replaceOnceMatch clicked"
        return

    def replaceAllMatchClickedButton(self, checked):
        ##print "replaceAllMatch clicked"
        return


    # we needed to separate this from findNextMatchingStrLineInTable, because python passed a checked argument (bool) that overrides the value of pFindSpecialLinesMode
    def findNextMatchFromClickedButton(self, checked):
        self.findNextMatchingStrLineInTable(pFindSpecialLinesMode=None, pSearchDirection=None, pWrapAround=None, pMatchCase = None )
        return
#
#   Internal function for searching for matching strings (inline find)
#   pFindSpecialLinesMode = "marked", "changed", "unchanged", "conflicted"
#
    def findNextMatchingStrLineInTable(self, pFindSpecialLinesMode=None, pSearchDirection=None, pWrapAround=None, pMatchCase = None ):
        global listOfEnglishLinesSpeechInfo
        global listOfUntranslatedLinesSpeechInfo
        search_mode = "start"
        search_direction = "down"
        search_wrap = True
        match_case = False
        if pSearchDirection <> None:
            search_direction = pSearchDirection
        elif self.ui.findSearchUpChBx.isChecked() == True:
            search_direction = "up"
        if pWrapAround <> None:
            search_wrap = pWrapAround
        elif self.ui.findWrapAroundChBx.isChecked()== False:
            search_wrap = False
        if pMatchCase <> None:
            match_case = pMatchCase
        if self.ui.findMatchCaseChBx.isChecked()== True:
            match_case = True

        if pFindSpecialLinesMode == None:
            if self.currentSearchKeyword == self.ui.findStrTxtBx.text().strip():
                search_mode = "next"

        plithosOfQuotes =len(listOfEnglishLinesSpeechInfo)
        wrap_start = 0
        if search_direction == "up":
            wrap_start = plithosOfQuotes - 1

        searchInColumnNumber = 0
        weHadAMatch = False
        keySearchStr = ""
        if pFindSpecialLinesMode == None:
            keySearchStr = self.ui.findStrTxtBx.text().strip()
            #print "keySearchStr"+ keySearchStr
            if keySearchStr == "" or plithosOfQuotes==0:
                highlightRulesGlobal.clearSearchRule()
                if(plithosOfQuotes>0):
                    self.quoteTableView.clearSelection()
                return

            if len(keySearchStr) < 2:
                reply = QtGui.QMessageBox.information(self, "Information message", "Cannot allow string search with less than 2 characters!")
                return

            # after validity checks, we set the member var to remember the last valid search
            self.currentSearchKeyword = keySearchStr

            if self.ui.OriginalOrTransCmbBx.currentText() <> "Original Text":
                 searchInColumnNumber = 1

        elif pFindSpecialLinesMode == "marked":
            searchInColumnNumber = 2
        elif pFindSpecialLinesMode == "conflicted":
            searchInColumnNumber = 4
        elif pFindSpecialLinesMode == "unchanged":
            searchInColumnNumber = 3
        elif pFindSpecialLinesMode == "changed":
            searchInColumnNumber = 3

        startRowOfSearch = 0
        startRowOfSearchIndex = self.quoteTableView.currentIndex()
        if (search_mode == "next" or search_mode == "start") and search_direction == "down":
            if (startRowOfSearchIndex is not None) :
                startRowOfSearch = startRowOfSearchIndex.row() + 1
            elif (startRowOfSearchIndex is None):
                startRowOfSearch = 0
        elif (search_mode == "next" or search_mode == "start") and search_direction == "up":
            if (startRowOfSearchIndex is not None):
                startRowOfSearch = startRowOfSearchIndex.row() - 1
            elif (startRowOfSearchIndex is  None):
                startRowOfSearch = plithosOfQuotes - 1

        if (startRowOfSearch >= plithosOfQuotes and search_direction == "down" and search_wrap == True):
            startRowOfSearch = 0
        elif (startRowOfSearch < 0 and search_direction == "up" and search_wrap == True):
            startRowOfSearch = plithosOfQuotes - 1

##        for rowi in range(startRowOfSearch,plithosOfQuotes):
##            index =  self.quoteTableView.model().index(rowi, searchInColumnNumber, QModelIndex())
##            datoTmp = self.quoteTableView.model().data(index).toPyObject()
##            if(re.search(keySearchStr, datoTmp)) <> None:
##                self.quoteTableView.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
##                self.quoteTableView.setCurrentIndex(index)
##                self.quoteTableView.setFocus()
##                weHadAMatch = True
##                break
        untilButWithoutRow = plithosOfQuotes
        if  search_direction == "up":
            untilButWithoutRow = -1

        weHadAMatch = self.matchKeyWord(pFindSpecialLinesMode, keySearchStr,startRowOfSearch,untilButWithoutRow, searchInColumnNumber,search_direction, match_case)
        if weHadAMatch == False: #search from startRow to the end (or the top) and found nothing. Check if wrapping is set to continue searching)
            if search_wrap == True  and ( (search_direction == "down"  and startRowOfSearch > 0  ) or (search_direction == "up" and startRowOfSearch < plithosOfQuotes -1 ) ):
                weHadAMatch = self.matchKeyWord(pFindSpecialLinesMode, keySearchStr,wrap_start,startRowOfSearch, searchInColumnNumber, search_direction, match_case)
        # if still is false then print message!
        if search_wrap == True and weHadAMatch == False:
            reply = QtGui.QMessageBox.information(self, "Information message", "No matches were found!")
        elif search_wrap == False and weHadAMatch == False and search_direction == "up" and startRowOfSearch == plithosOfQuotes -1:
            reply = QtGui.QMessageBox.information(self, "Information message", "No matches were found!")
        elif search_wrap == False and weHadAMatch == False and search_direction == "down" and startRowOfSearch == 0:
            reply = QtGui.QMessageBox.information(self, "Information message", "No matches were found!")
        elif search_wrap == False and weHadAMatch == False and ( (search_direction == "down" and startRowOfSearch > 0) or (search_direction == "up" and startRowOfSearch < plithosOfQuotes -1) ) :
            reply = QtGui.QMessageBox.question(self, "Information message", "End of file reached. No matches were found! Do you want to continue search from the begining of the file?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.Yes:
                weHadAMatch = self.matchKeyWord(pFindSpecialLinesMode, keySearchStr,wrap_start,startRowOfSearch, searchInColumnNumber, search_direction, match_case)
                if weHadAMatch == False:
                    reply = QtGui.QMessageBox.information(self, "Information message", "No matches were found!")

        return

#   Internal method for matching keywords, used by the find (findNextMatchingStrLineInTable) method.
#
#
    def matchKeyWord(self, pFindSpecialLinesMode, keyStr, fromRow, untilButWithoutRow, columnNumber, search_direction, match_caseFlg):
        #print keyStr
        #print pFindSpecialLinesMode == None
        #print search_direction
        retBool = False
        dasSearchStep  = 1
        if search_direction == "up":
            dasSearchStep  = -1
        searchRange = range(fromRow, untilButWithoutRow, dasSearchStep)

        myReFlags = 0
        if pFindSpecialLinesMode== None:
            if match_caseFlg == False:
                myReFlags |= re.IGNORECASE

            if columnNumber > 0:
                myReFlags |= re.UNICODE #fixes ignorecase state for greek letters!
            # to override the error when the re contains or ends in \
            #keyStr = keyStr.replace('\\','\\\\')
            keyStr = keyStr.replace("\\", r"\\")
            keyStr = keyStr.replace('[',r'\[')
            keyStr = keyStr.replace(']',r'\]')
            keyStr = keyStr.replace('?',r'\?')
            keyStr = keyStr.replace('.',r'\.')
            keyStr = keyStr.replace('+',r'\+')
            keyStr = keyStr.replace('*',r'\*')
            keyStr = keyStr.replace('|',r'\|')
            keyStr = keyStr.replace('(',r'\(')
            keyStr = keyStr.replace(')',r'\)')
            keyStr = keyStr.replace('{',r'\{')
            keyStr = keyStr.replace('}',r'\}')
            keyStr = keyStr.replace('^',r'\^')
            keyStr = keyStr.replace('$',r'\$')

            matchKeyFormat = QtGui.QTextCharFormat()
            matchKeyFormat.setBackground(QtCore.Qt.green)
            highlightRulesGlobal.setSearchHighlightRule(keyStr, matchKeyFormat, match_caseFlg, columnNumber)
#        print "%s" % keyStr
        for rowi in searchRange:
            index =  self.quoteTableView.model().index(rowi, columnNumber, QModelIndex())
            datoTmp = self.quoteTableView.model().data(index).toPyObject()
            if pFindSpecialLinesMode == None:
                if(re.search(keyStr, datoTmp, flags=myReFlags)) <> None:
                    self.quoteTableView.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
                    self.quoteTableView.setCurrentIndex(index)
                    self.quoteTableView.setFocus()
                    retBool = True
                    break
            elif pFindSpecialLinesMode == "marked" or  pFindSpecialLinesMode == "conflicted" or pFindSpecialLinesMode == "changed":
                if datoTmp == True:
                    indexToSelect = self.quoteTableView.model().index(rowi, 1, QModelIndex())
                    self.quoteTableView.selectionModel().select(indexToSelect, QItemSelectionModel.ClearAndSelect)
                    self.quoteTableView.setCurrentIndex(indexToSelect)
                    self.quoteTableView.setFocus()
                    retBool = True
                    break
            elif pFindSpecialLinesMode == "unchanged":
                if datoTmp == False:
                    indexToSelect = self.quoteTableView.model().index(rowi, 1, QModelIndex())
                    self.quoteTableView.selectionModel().select(indexToSelect, QItemSelectionModel.ClearAndSelect)
                    self.quoteTableView.setCurrentIndex(indexToSelect)
                    self.quoteTableView.setFocus()
                    retBool = True
                    break

        return retBool

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # TODO: TO ORIO THS PROTASHS DEN EINAI TO IDIO GIA OLA TA ARXEIA. FIX PER CASE!!!
    #       Gia uiText kai gia speech.info einai 0xFF (+1 gia to keno xarakthra)
    #       EPISHS prin klh8ei ayth h synarthsh PREPEI na klh8ei h remakeCharlistWithNoEscapeSequences()
    #       ALLA PROSOXH: h remakeCharlist den 8a mporei na ksexwrisei metaksy twn ascii ellhnikwn kai twn eidikwn xarakthrwn pou exoun 8esh ascii ellhnikou (px ΞΊ).
    #       Ara prepei PALI na enswmatwsoume th routina edw.
    # TODO: this method should probably be moved in the grabber module.
    #
    def makeStringIntoModifiedAsciiCharlistToBeWritten(self, inputStringFromGUI, GrabberForTranslationDicts):
        local_replaceAsciiIndexWithValForTranslation = GrabberForTranslationDicts.replaceAsciiIndexWithValForTranslation.copy()
        translatedTextAsCharsList2 = []
        # first locate the `escape sequences` and switch them with placeholder characters maintaining their position and the corresponding special char (integration of the function from method remakeCharlistWithNoEscapeSequences)
        remadeQuoteString = inputStringFromGUI
        posOfSpecialChars = []
        listOfSpecialChars = []
        remadeCharList = []

        atLeastOneSpecialCharWasDetected = False
        while not ( re.search("0x[0-9A-F][0-9A-F]", remadeQuoteString)) == None:
            atLeastOneSpecialCharWasDetected = True
            aMatchObj =  re.search("0x[0-9A-F][0-9A-F]", remadeQuoteString)
            posOfSpecialChars.append(aMatchObj.start())
            listOfSpecialChars.append(pack('B',int(remadeQuoteString[aMatchObj.start():aMatchObj.end()], 16)))
            remadeQuoteString = remadeQuoteString[:aMatchObj.start()] + "_" + remadeQuoteString[aMatchObj.end():]  # _ is a place holder and will be replaced in the Remade charList!

        #paremboli routinas pou metafrazei tous ellhnikous xarakthres se proper hex values to be written. PREPEI NA APOFYGEI THN APOPEIRA METAFRASHS TWN PLACEHOLDER (kalou kakou
        # ta kanw skip ta '_' ekei pou ta exw markarei, an kai den anhkoun sto translation table)
        translatedTextAsCharsList2 = list(remadeQuoteString)
        for itmp in range(0,len(translatedTextAsCharsList2)):
            if not itmp in posOfSpecialChars:
                if translatedTextAsCharsList2[itmp] in local_replaceAsciiIndexWithValForTranslation:
                    tmpkey = translatedTextAsCharsList2[itmp]
                    translatedTextAsCharsList2[itmp] = pack('B', local_replaceAsciiIndexWithValForTranslation[tmpkey])
                else:
                    translatedTextAsCharsList2[itmp] = chr(ord(translatedTextAsCharsList2[itmp]))

        # epistrofi sth routina pou bazei tous pragmatika special xarakthres pali sto string
        if atLeastOneSpecialCharWasDetected:
    #        print "listOfSpecialChars %s" % listOfSpecialChars
    #        print "listOfpos %s" % posOfSpecialChars
    #            remadeCharList = list(remadeQuoteString)
            for littleI in range(0, len(posOfSpecialChars)):
                translatedTextAsCharsList2[posOfSpecialChars[littleI]] = listOfSpecialChars[littleI]
    #        print "remadeCharList %s" % remadeCharList
    #            translatedTextAsCharsList2 = remadeCharList
        translatedTextAsCharsList2.append('\x00')
        return translatedTextAsCharsList2

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #
    # TODO: TO ORIO THS PROTASHS DEN EINAI TO IDIO GIA OLA TA ARXEIA. FIX PER CASE!!!
    # Epeidh exoume antallages sta grammata, to string pou grafetai sto arxeio einai UNREADABLE kai prepei na metafer8ei sth lista se anagnwsimh morfh
    # meta 8a allaksei pali pisw me thn makeCharlistInModifiedAsciiCharlistToBeWritten()
    # Gia ta translation Strings einai enswmatwmenh h leitourgia ths "make String With Escape Sequences"
    #
    def makeStringInReadableExtAsciiCharlistToBeListed(self, inputCharlist, GrabberForTranslationDicts):
        local_rev_replaceAsciiIndexWithValForTranslation = GrabberForTranslationDicts.rev_replaceAsciiIndexWithValForTranslation_FOR_DIALOGUE_FILE.copy()
        ##print local_rev_replaceAsciiIndexWithValForTranslation
        translatedTextAsCharsList2 = inputCharlist
        lgntOList = len(translatedTextAsCharsList2)
        itmp = 0
        while itmp < lgntOList:
            if translatedTextAsCharsList2[itmp] in local_rev_replaceAsciiIndexWithValForTranslation:
                tmpkey = translatedTextAsCharsList2[itmp]
                translatedTextAsCharsList2[itmp] = pack('B', local_rev_replaceAsciiIndexWithValForTranslation[tmpkey])
            else:
                # \x94 used in a dev's comentary as a closing quote symbol. line 8610 fr.speech.info This should be explicitly set as a normal quote symbol " in the translation, by the translator
                #\a9 and c3 are in all title credits of MI2: The island of mmmdsffs (does this even appera anywhere?)
                if(self.selGameID==2 and translatedTextAsCharsList2[itmp] == '\x9c') or \
                    (self.selGameID==2 and translatedTextAsCharsList2[itmp] == '\xa0') or \
                    (self.selGameID==2 and translatedTextAsCharsList2[itmp] == '\x8c') or \
                    (self.selGameID==2 and translatedTextAsCharsList2[itmp] == '\x94') or \
                    (self.selGameID==2 and translatedTextAsCharsList2[itmp] == '\x9d') or \
                    (self.selGameID==2 and translatedTextAsCharsList2[itmp] == '\xaa') or \
                    (self.selGameID==2 and translatedTextAsCharsList2[itmp] == '\xa9') or \
                    (self.selGameID==2 and translatedTextAsCharsList2[itmp] == '\xc3') or \
                    translatedTextAsCharsList2[itmp] == '\x97' or \
                    translatedTextAsCharsList2[itmp] == '\xea' or \
                    translatedTextAsCharsList2[itmp] == '\xe9' or \
                    translatedTextAsCharsList2[itmp] == '\x99' or \
                    translatedTextAsCharsList2[itmp] == '\x85' \
                    : translatedTextAsCharsList2[itmp] =  "0x%2X" % ord(translatedTextAsCharsList2[itmp])
                elif (self.selGameID==2 and (itmp+1 < lgntOList) and translatedTextAsCharsList2[itmp] == '\xe2' and translatedTextAsCharsList2[itmp+1] == '\x80'):
                    translatedTextAsCharsList2[itmp] = "0x%2X" % ord(translatedTextAsCharsList2[itmp])
                    translatedTextAsCharsList2[itmp+1] = "0x%2X" % ord(translatedTextAsCharsList2[itmp+1])
                    itmp +=1 # skip a step
                elif (self.selGameID==2 and (itmp+2 < lgntOList) and translatedTextAsCharsList2[itmp] == '\xe2' and translatedTextAsCharsList2[itmp+1] == '\x84' and translatedTextAsCharsList2[itmp+2] == '\xa2'):
                    translatedTextAsCharsList2[itmp] = "0x%2X" % ord(translatedTextAsCharsList2[itmp])
                    translatedTextAsCharsList2[itmp+1] = "0x%2X" % ord(translatedTextAsCharsList2[itmp+1])
                    translatedTextAsCharsList2[itmp+2] = "0x%2X" % ord(translatedTextAsCharsList2[itmp+2])
                    itmp +=2 # skip two steps (classic game credits tm symbol for seagul or loom)
                elif (self.selGameID==2 and (itmp+1 < lgntOList) and translatedTextAsCharsList2[itmp] == '\xc2' and translatedTextAsCharsList2[itmp+1] == '\xa9'):
                    translatedTextAsCharsList2[itmp] = "0x%2X" % ord(translatedTextAsCharsList2[itmp])
                    translatedTextAsCharsList2[itmp+1] = "0x%2X" % ord(translatedTextAsCharsList2[itmp+1])
                    itmp +=1 # skip a step (classic game credits B(c) symbol at the end)
                elif (self.selGameID==2 and translatedTextAsCharsList2[itmp] == '\xe2'):
                    translatedTextAsCharsList2[itmp] =  "0x%2X" % ord(translatedTextAsCharsList2[itmp])
                else :
                    translatedTextAsCharsList2[itmp] = chr(ord(translatedTextAsCharsList2[itmp]))
            itmp +=1 # end of loop


        return "".join(translatedTextAsCharsList2)

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #
    # This is for viewing and editing purposes from the GUI ONLY FOR ORIGINAL STRING
    #
    def makeOriginalStringWithEscapeSequences(self, quoteCharList):
        specialCharQuoteList = []
        lgntOList = len(quoteCharList)
        secondIt = 0
        while secondIt < lgntOList:
            if (self.selGameID==2 and quoteCharList[secondIt] == '\x9c') or \
                (self.selGameID==2 and quoteCharList[secondIt] == '\xa0') or \
                (self.selGameID==2 and quoteCharList[secondIt] == '\x8c') or \
                (self.selGameID==2 and quoteCharList[secondIt] == '\x94') or \
                (self.selGameID==2 and quoteCharList[secondIt] == '\x9d') or \
                (self.selGameID==2 and quoteCharList[secondIt] == '\xaa') or \
                (self.selGameID==2 and quoteCharList[secondIt] == '\xa9') or \
                (self.selGameID==2 and quoteCharList[secondIt] == '\xc3') or \
                quoteCharList[secondIt] == '\x97' or \
                quoteCharList[secondIt] == '\xea' or \
                quoteCharList[secondIt] == '\xe9' or \
                quoteCharList[secondIt] == '\x99' or \
                quoteCharList[secondIt] == '\x85' \
                : specialCharQuoteList.append( "0x%2X" % ord(quoteCharList[secondIt]))
            elif (self.selGameID==2 and (secondIt+1 < lgntOList) and quoteCharList[secondIt] == '\xe2' and quoteCharList[secondIt+1] == '\x80'):
                specialCharQuoteList.append( "0x%2X" % ord(quoteCharList[secondIt]))
                specialCharQuoteList.append( "0x%2X" % ord(quoteCharList[secondIt+1]))
                secondIt +=1 #skip a step
            elif (self.selGameID==2 and (secondIt+2 < lgntOList) and quoteCharList[secondIt] == '\xe2' and quoteCharList[secondIt+1] == '\x84' and quoteCharList[secondIt+2] == '\xa2'):
                specialCharQuoteList.append( "0x%2X" % ord(quoteCharList[secondIt]))
                specialCharQuoteList.append( "0x%2X" % ord(quoteCharList[secondIt+1]))
                specialCharQuoteList.append( "0x%2X" % ord(quoteCharList[secondIt+2]))
                secondIt +=2 # skip two steps (classic game credits tm symbol for seagul or loom)
            elif (self.selGameID==2 and (secondIt+1 < lgntOList) and quoteCharList[secondIt] == '\xc2' and quoteCharList[secondIt+1] == '\xa9'):
                specialCharQuoteList.append( "0x%2X" % ord(quoteCharList[secondIt]))
                specialCharQuoteList.append( "0x%2X" % ord(quoteCharList[secondIt+1]))
                secondIt +=1 #skip a step (classic game credits B(c) symbol at the end)
            elif (self.selGameID==2 and quoteCharList[secondIt] == '\xe2'):
                specialCharQuoteList.append( "0x%2X" % ord(quoteCharList[secondIt]))
            else :
                specialCharQuoteList.append(  quoteCharList[secondIt])
            secondIt +=1 # end of loop

        return "".join(specialCharQuoteList)

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # Is now used only for debug purposes!
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def remakeCharlistWithNoEscapeSequences(self, newQuoteString):
        remadeQuoteString = newQuoteString
        posOfSpecialChars = []
        listOfSpecialChars = []
        remadeCharList = []

        atLeastOneSpecialCharWasDetected = False
        while not ( re.search("0x[0-9A-F][0-9A-F]", remadeQuoteString)) == None:
            atLeastOneSpecialCharWasDetected = True
            aMatchObj =  re.search("0x[0-9A-F][0-9A-F]", remadeQuoteString)
            posOfSpecialChars.append(aMatchObj.start())
            listOfSpecialChars.append(pack('B',int(remadeQuoteString[aMatchObj.start():aMatchObj.end()], 16)))
            remadeQuoteString = remadeQuoteString[:aMatchObj.start()] + "_" + remadeQuoteString[aMatchObj.end():]  # _ is a place holder and will be replaced in the Remade charList!

        if atLeastOneSpecialCharWasDetected:
    #        print "listOfSpecialChars %s" % listOfSpecialChars
    #        print "listOfpos %s" % posOfSpecialChars
            remadeCharList = list(remadeQuoteString)
            for littleI in range(0, len(posOfSpecialChars)):
                remadeCharList[posOfSpecialChars[littleI]] = listOfSpecialChars[littleI]
    #        print "remadeCharList %s" % remadeCharList
        return remadeCharList


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #
    # Create a unique filename for a new copy file, and create the file itself as a copy of the original passed as argument.
    # Returns the filename of the copy file.
    # TODO: do we need a check that the original file exists?
    def createAndGetNewCopyFile(self, originalfullPathsFilename):
        retVal = ""
        filepathSplitTbl = os.path.split(originalfullPathsFilename)
        sFilename = filepathSplitTbl[1]
        pathTosFile = filepathSplitTbl[0]
        transSpeechInfoFile = None
        sFilenameParts = []
        sFilenameUn = ""
        # Removed attempts to unicode encode sFilename with the origEncoding or tryEncoding (similar to str.decode(origEncoding) ) since it's already unicode object
        sFilenameParts = unicode.rpartition(sFilename, '.')

        appendixIndex= 0
        candidateFullCopyValid = False;
        while not candidateFullCopyValid:
            appendixIndex += 1
            candidateFullcopyFileName= os.path.join( pathTosFile ,  sFilenameParts[0] + u'_' + ("%04d" % (appendixIndex)) + sFilenameParts[1] + sFilenameParts[2])
##            print repr(candidateFullcopyFileName)
##            print repr(originalfullPathsFilename)
##            print repr(sFilename)
            if not os.access(candidateFullcopyFileName, os.F_OK) :
                shutil.copyfile(originalfullPathsFilename, candidateFullcopyFileName)
                candidateFullCopyValid = True
                retVal = candidateFullcopyFileName
                # Removed attempts to unicode encode candidateFullcopyFileName with the origEncoding or tryEncoding (similar to str.decode(origEncoding) ) since it's already joined unicode object parts
        return retVal

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #
    # Create a unique filename for a new backup file and return with the original extension AND with the txt extension.
    # Returns the filename of the backup file with original and txt extension.
    # TODO: do we need a check that the original file exists?
    def createAndGetBkpFilenames(self, originalfullPathsFilename):
        candidateFullcopyFileName = ""
        candidateTxtFileName = ""
        filepathSplitTbl = os.path.split(originalfullPathsFilename)
        sFilename = filepathSplitTbl[1]
        pathTosFile = filepathSplitTbl[0]
        transSpeechInfoFile = None
        sFilenameParts = []
        # removed attempts to encode unicode (received from sqlite db or open file messagebox)
        sFilenameParts = unicode.rpartition(sFilename, '.')
        currTimeStampInt = int(time.time())
        candidateFullcopyFileName= os.path.join( pathTosFile ,  sFilenameParts[0] + u'_' + ("%014d" % (currTimeStampInt)) + sFilenameParts[1] + sFilenameParts[2])
        candidateTxtFileName = os.path.join( pathTosFile ,  sFilenameParts[0] + u'_' + ("%014d" % (currTimeStampInt)) + sFilenameParts[1] + "txt")

        candidateFullcopyFileNameRes = ""
        candidateTxtFileNameRes  = ""
        candidateFullcopyFileNameRes = candidateFullcopyFileName
        candidateTxtFileNameRes  = candidateTxtFileName

        # removed attempts to encode unicode since the parts we join already are unicode objects

        return (candidateFullcopyFileNameRes,candidateTxtFileNameRes)

    # TODO: maybe sessions should save relative paths and NOT full paths?
    def loadASession(self, pSessionName, pOriginalfullPathsFilename):
        # check if there is an entry in the sessions table.
        # check if original file exists
        # check if copy file exists
        # check if original file on Disk has same MD5 as in the DB entry
        # check if copy file on Disk same MD5 as in the DB entry
        self.activeSessionID = -1 #invalid id
        myID = -1 #invalid id
        foundSessionErrors = False
        aSessionWasFound = False
        currSelGameID = self.selGameID

        if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
            foundSessionErrors = True
            # TODO: debug and error message. Show in message box and quit?
#            print "CRITICAL ERROR: The database file %s could not be found!!" % (self.DBFileNameAndRelPath)
        else:
            # TODO: DB initialization (Should happen once, not every time!)
            conn = sqlite3.connect(self.DBFileNameAndRelPath)
            c = conn.cursor()
            if (pSessionName is None) and (pOriginalfullPathsFilename is not None):
                #select most recent of the possible sessions
                if not os.access(pOriginalfullPathsFilename, os.F_OK) :
                    foundSessionErrors = True
                    #TODO: debug and error message. Show in message box and quit?
                    #print "CRITICAL ERROR: The original file %s could not be found on the disk!!" % (pOriginalfullPathsFilename)
                else:
                    origFileMD5 = self.md5_for_file(pOriginalfullPathsFilename)
                    # todo: the search here is strict. we could relax it after a warning (that e.g. the original file was found in a session but not with the same MD5, do you want to continue loading that session?)
                    c.execute("""select sessionName, fullPathToOrigFile, fullPathToTransFile, origFileMD5, transFileMD5, gameID, datetime(DateUpdated,'unixepoch', 'localtime' ),DateUpdated, ID from """ +
                            """translationSessions WHERE gameID = ? AND fullPathToOrigFile = ? AND origFileMD5 = ? AND DateUpdated = """ +
                            """ (select max(DateUpdated) from translationSessions where fullPathToOrigFile = ? AND origFileMD5 = ?)""", (str(currSelGameID), pOriginalfullPathsFilename, origFileMD5, pOriginalfullPathsFilename, origFileMD5))
            elif pSessionName is not None:
                c.execute("""select sessionName, fullPathToOrigFile, fullPathToTransFile, origFileMD5, transFileMD5, gameID, datetime(DateUpdated,'unixepoch', 'localtime' ),DateUpdated, ID from """ +
                            """translationSessions WHERE sessionName = ?""" , (pSessionName, ))
            else:
                #TODO: debug and error message. Show in message box or SessionsErors and quit?
                #print "CRITICAL ERROR: The loadASession method cannot have both of its parameters null!"
                foundSessionErrors = True
            if (not foundSessionErrors):
                row = c.fetchone()
                if (row is not None):
                    mySessionName = unicode.encode("%s" % row[0],self.origEncoding)
                    myFullPathToOrigFile = row[1]        # unicode.encode("%s" % row[1],self.origEncoding)
                    myFullPathToTransFile = row[2]       # unicode.encode("%s" % row[2],self.origEncoding)
                    myOrigFileMD5 = unicode.encode("%s" % row[3],self.origEncoding)
                    myTransFileMD5 = unicode.encode("%s" % row[4],self.origEncoding)
                    myGameID = int(row[5])
                    myDateUpdatedStr = unicode.encode("%s" % row[6],self.origEncoding)
                    myID = int(row[8])

                    if not os.access(myFullPathToOrigFile, os.F_OK) :
                        foundSessionErrors = True
                        #TODO: debug and error message. Show in message box or SessionsErors and quit?
                        #print "CRITICAL ERROR: The original file %s for the session could not be found on the disk!!" % (myFullPathToOrigFile)
                    if not os.access(myFullPathToTransFile, os.F_OK) :
                        foundSessionErrors = True
                        #TODO: debug and error message. Show in message box or SessionsErors and quit?
                        #print "CRITICAL ERROR: The translation file %s for the session could not be found on the disk!!" % (myFullPathToTransFile)
                    if myOrigFileMD5 != self.md5_for_file(myFullPathToOrigFile):
                        foundSessionErrors = True
                        #TODO: debug and error message. Show in message box or SessionsErors and quit?
                        #print "CRITICAL ERROR: The original file %s in the session has a different checksum %s from the file %s found on the disk!!" % (myFullPathToOrigFile,myOrigFileMD5, self.md5_for_file(myFullPathToOrigFile))
                    if myTransFileMD5 != self.md5_for_file(myFullPathToTransFile):
                        foundSessionErrors = True
                        #TODO: debug and error message. Show in message box or SessionsErors and quit?
                        #print "CRITICAL ERROR: The translation file %s in the session has a different checksum %s from the file %s found on the disk!!" % (myFullPathToTransFile, myTransFileMD5, self.md5_for_file(myFullPathToTransFile))
#                   ####
                    if (not foundSessionErrors):
                        # Load the session! Set gameId, and textfields.
                        aSessionWasFound = True
                        # TODO: fill in text fields
                        #debug
                        #print "LOADING EXISTING SESSION"
                        self.ui.openFileNameTxtBx.setText(myFullPathToOrigFile)
                        self.ui.openTranslatedFileNameTxtBx.setText(myFullPathToTransFile)
                if (not aSessionWasFound) and (pOriginalfullPathsFilename is not None) and (os.access(pOriginalfullPathsFilename, os.F_OK) ):
                        # TODO: do we display a warning here?
                        # ONLY for the case that a fullPathToOrigFile was passed as a parameter: create (and save) a new session
                        localfullcopyFileName = self.createAndGetNewCopyFile(pOriginalfullPathsFilename)
                        #debug
                        #print "CREATING NEW SESSION"
                        # clear session errors
                        foundSessionErrors = False
                        (savedFlag, mySessionName, myFullPathToOrigFile, myFullPathToTransFile, myGameID, myID, myOrigFileMD5, myTransFileMD5) = self.createAndSaveSession(pOriginalfullPathsFilename, localfullcopyFileName, pSaveMarkers = False)
                        if savedFlag == True:
                            # TODO: fill in text fields
##                            self.ui.openFileNameTxtBx.setText()
                            self.ui.openTranslatedFileNameTxtBx.setText(myFullPathToTransFile)
            conn.commit()
            c.close()
        if(self.ui.openTranslatedFileNameTxtBx.text().strip() != ""):
            self.enableActionsAndButtonsForAvalidSession(True)

        else:
            self.enableActionsAndButtonsForAvalidSession(False)

        if (foundSessionErrors or myID <= 0 ):
            self.activeSessionID = -1
            return False
        else:
            ##print "loaded session %s"% str(myID)
            self.activeSessionID = myID
            return True

    def enableActionsAndButtonsForAvalidSession(self, pFlagEnable=True):
        self.ui.backupBtn.setEnabled(pFlagEnable)
        self.ui.SubmitChangesBtn.setEnabled(pFlagEnable)
        self.ui.actionImport_Translation_from_txt.setEnabled(pFlagEnable)
        self.ui.actionExtract_Translation_to_txt.setEnabled(pFlagEnable)
        self.ui.actionExtract_Original_to_txt.setEnabled(pFlagEnable)
        self.ui.actionLoad_Translation_File.setEnabled(pFlagEnable)
        self.ui.actionMerge_Active_Translation_with.setEnabled(pFlagEnable)

        self.ui.menuView.setEnabled(pFlagEnable)
        self.ui.menuSearch.setEnabled(pFlagEnable)
        self.ui.actionReport.setEnabled(pFlagEnable)
        self.ui.actionGotoLine.setEnabled(pFlagEnable)
        self.ui.actionFind.setEnabled(pFlagEnable)
        self.ui.actionFind_Next.setEnabled(pFlagEnable)
        self.ui.actionFind_Next_Marked.setEnabled(pFlagEnable)
        self.ui.actionFind_Previous_Marked.setEnabled(pFlagEnable)
        self.ui.actionFind_Next_Unchanged.setEnabled(pFlagEnable)
        self.ui.actionFind_Previous_Unchanged.setEnabled(pFlagEnable)

        self.ui.actionFind_Next_Conflicted.setEnabled(pFlagEnable)
        self.ui.actionFind_Previous_Conflicted.setEnabled(pFlagEnable)

        self.ui.actionFind_Next_Changed.setEnabled(pFlagEnable)
        self.ui.actionFind_Previous_Changed.setEnabled(pFlagEnable)
#        self.ui.setActiveWindow()
        self.ui.setFocus()
        self.ui.activateWindow()

        return
    #
    # Create a session connecting the original file and the copy file (translation file)
    # TODO: do we need a check that the original file exists?
    # TODO: do we need a check that the copy file exists?
    #
    def createAndSaveSession(self, pOriginalfullPathsFilename, pfullcopyFileName, pSaveMarkers = True):
        sessionID = -1 #invalid session ID
        retStatus = False
        retSessionName = ""
        currSelGameID = self.selGameID
        md5ForpOriginalfullPathsFilename = self.md5_for_file(pOriginalfullPathsFilename)
        md5ForpfullcopyFileName = self.md5_for_file(pfullcopyFileName)
        #debug
        #print "MD5 orig: %s , MD5 copy: %s" % (md5ForpOriginalfullPathsFilename, md5ForpfullcopyFileName)
        if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
            #TODO: debug and error message. Show in message box or SessionsErors and quit?
            #print "CRITICAL ERROR: The database file %s could not be found!!" % (self.DBFileNameAndRelPath)
            pass
        else:
            conn = sqlite3.connect(self.DBFileNameAndRelPath)
            c = conn.cursor()
            if self.activeSessionID > 0:
                md5ForpOriginalfullPathsFilename = self.md5_for_file(pOriginalfullPathsFilename)
                md5ForpfullcopyFileName = self.md5_for_file(pfullcopyFileName)

                c.execute("""select sessionName from translationSessions WHERE ID = ? and fullPathToOrigFile = ? and origFileMD5 = ? and gameID = ?""", ( str(self.activeSessionID), pOriginalfullPathsFilename, md5ForpOriginalfullPathsFilename, str(currSelGameID) ))
                row = c.fetchone()
                if (row is not None):
                    retSessionName = unicode.encode("%s" % row[0],self.origEncoding)

            else: #which case is this, when no session exist to be loaded: set the session name automatically from the relative filename of the copy file
                # create session in DB
                filepathSplitTbl = os.path.split(pfullcopyFileName)
                retSessionName = filepathSplitTbl[1]

                foundSelectedGame = False
                sessionPrefix = "foo"
                c.execute("""select ID, CodeName from supportedGames WHERE ID = ?""" , (str(currSelGameID),) )
                for row in c:
                    foundSelectedGame = True
                    sessionPrefix =unicode.encode("%s_" % row[1],self.origEncoding)
                    break
                if foundSelectedGame == False:
                    #TODO: debug and error message. Show in message box or SessionsErors and quit?
                    #print "CRITICAL ERROR: The selected game was not found in the DB!"
                    pass
                retSessionName = "%s%s" % (sessionPrefix,retSessionName)

            sessionNameExists= False
#            print "RetSessionName %s" % (retSessionName)
            # needs an extra comma to evaluate as one parameter (and not multiple characters). Alternatively [retSessionName]
#            c.execute("""select count(ID) from translationSessions WHERE sessionName = ?""" , (retSessionName,))
            c.execute("""select ID from translationSessions WHERE sessionName = ?""" , (retSessionName,))
            row = c.fetchone()
            if (row is not None) and ( int(row[0]) > 0):
                sessionNameExists = True
                sessionID = int(row[0])
                # add a new line in the sessions table
                # TODO: warning here?
                # TODO: do we always update the date here?
                # print "UPDATING SESSION: %s" % (retSessionName)
                c.execute("""update translationSessions set fullPathToOrigFile=?, fullPathToTransFile=?, origFileMD5=?, transFileMD5=?, gameID=?, DateUpdated=strftime('%s','now') WHERE sessionName = ?""", (pOriginalfullPathsFilename, pfullcopyFileName, md5ForpOriginalfullPathsFilename, md5ForpfullcopyFileName, str(currSelGameID), retSessionName ))
            else:
                sessionNameExists = False
                # add a new line in the sessions table
                c.execute("""insert into translationSessions(sessionName, fullPathToOrigFile, fullPathToTransFile, origFileMD5, transFileMD5, gameID, DateUpdated) values(?,?,?,?,?,?, strftime('%s','now'))""", (retSessionName, pOriginalfullPathsFilename, pfullcopyFileName, md5ForpOriginalfullPathsFilename, md5ForpfullcopyFileName, str(currSelGameID) ))
                sessionID = c.lastrowid
            # to recover date in readable format I should do : SELECT datetime(DateUpdated,'unixepoch', 'localtime' ) FROM translationSessions
            retStatus = True
            # TODO: make a select to confirm writing to db?
            if(pSaveMarkers==True and sessionID>0):
                # get the row ids that have checked marker checkboxes
                # delete every marker for this session from the DB
                linenum = 0
                c.execute("""delete from toDoLinesForSession where IDSession = ?""", (str(sessionID), ))
                # insert into the db for this active sessionID
                #
                # go through all lines of the GUI
                #
                global listOfEnglishLinesSpeechInfo
                plithosOfQuotes =len(listOfEnglishLinesSpeechInfo)
                for rowi in range(0,plithosOfQuotes):
                    index =  self.quoteTableView.model().index(rowi, 2, QModelIndex())
                    if(index.model().data(index, Qt.DisplayRole).toBool() == True):
                        linenum = index.row()
                        c.execute("""insert into toDoLinesForSession(IDSession, LineNum) values(?,?)""", (str(sessionID), str(linenum) ))
            conn.commit()
            c.close()
        return (retStatus, retSessionName, pOriginalfullPathsFilename, pfullcopyFileName, currSelGameID, sessionID, md5ForpOriginalfullPathsFilename, md5ForpfullcopyFileName)


    def parseInt(self, sin):
      import re
      m = re.search(r'^(\d+)[.,]?\d*?', str(sin))
      return int(m.groups()[-1]) if m and not callable(sin) else None

    #
    # For private use: Calculate the MD5 for  given file (splitting it in chunks of block_size while digesting it, to avoid memory hogging) (chuink size 2^7 = 128 bytes)
    #
    def md5_for_file(self, pFileName, block_size=2**7):
        md5 = hashlib.md5()
        if os.access(pFileName, os.F_OK) :
            f = open(pFileName, 'rb')
            while True:
                data = f.read(block_size)
                if not data:
                    break
                md5.update(data)
            f.close()
            return md5.hexdigest()
    #        return md5.digest()
        else:
            return ""

    def md5_for_file_alter(self, fname, blocksize=65536):
        hasher = hashlib.md5()
        if os.access(pFileName, os.F_OK) :
            afile = open(fname, 'rb')
            buf = afile.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(blocksize)
            afile.close()
            return hasher.hexdigest()
        else:
            return ""

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #
    # This method gets the number of quotes for a file.
    # It is essentially a short version of parseQuoteFile
    #
    def getQuoteNumberInFile(self, fullPathOfFilename, retrieveQuotesFlag = False, pGrabberForTranslationDicts=None):
        detectedNumOfQuotes = 0
        endOfFileReached = False
        sFilename = ""
        detectedGameId = -1
        retrievedQuotesList = []    #should contain quote and length
        del retrievedQuotesList[:]
        # A credits file only has the english language so we need to create a copy to work on (for the translated credits!)
        wholeOrigSpeechInfoFile = None
        origSpeechInfoFile = open(fullPathOfFilename, 'rb')
        wholeOrigSpeechInfoFile = origSpeechInfoFile.read()
        origSpeechInfoFile.close()
        ## detect file type and game id!
        #origSpeechInfoFile.seek(0)
        #the first 4 bytes usually are indicative of file type and game id
        #tmpWord = origSpeechInfoFile.read(4)
        tmpWord = self.myFileBuffRead(wholeOrigSpeechInfoFile, 0, 4)
        if tmpWord == "":
            endOfFileReached = True
        else:
            headerUnpacked = unpack('<L', tmpWord)
            headerHex = headerUnpacked[0]
            if headerHex == 0xe1794:
                sFilename = filenameSpeechInfo
                detectedGameId = 1
            elif headerHex == 0x554e454d:
                sFilename = filenameUIText
                detectedGameId = 1
            elif headerHex == 0xf2:
                sFilename = filenameHintsMI1CSV
                detectedGameId = 1
            elif headerHex == 0x2215:
                sFilename = filenameFrSpeechInfo
                detectedGameId = 2
            elif headerHex == 0x4f2:
                sFilename = filenameFrUIText
                detectedGameId = 2
            elif headerHex == 0x13e:
                sFilename = filenameHintsMI2CSV
                detectedGameId = 2
            elif headerHex == 0x2:
                sFilename = "classicgame.credits.xml"
                #origSpeechInfoFile.seek(0x70)
                #tmpWord02 = origSpeechInfoFile.read(4)
                tmpWord02 = self.myFileBuffRead(wholeOrigSpeechInfoFile, 0x70, 4)

                if tmpWord02 == "":
                    endOfFileReached = True
                else:
                    datumUnpacked = unpack('<L', tmpWord02)
                    datumHex = datumUnpacked[0]
                    if datumHex == 0x7f:
                        detectedGameId = 1
                    elif datumHex == 0x8e:
                        detectedGameId = 2

            elif headerHex == 0x8:
                sFilename = "remonkeyedgame_ingame.credits.xml"
                detectedGameId = 2
            elif headerHex == 0x13:
                #origSpeechInfoFile.seek(0x24)
                #tmpWord02 = origSpeechInfoFile.read(4)
                tmpWord02 = self.myFileBuffRead(wholeOrigSpeechInfoFile, 0x24, 4)
                if tmpWord02 == "":
                    endOfFileReached = True
                else:
                    datumUnpacked = unpack('<L', tmpWord02)
                    datumHex = datumUnpacked[0]
                    if datumHex == 0x3f000000:
                        #origSpeechInfoFile.seek(0x120)
                        #tmpWord03 = origSpeechInfoFile.read(4)
                        tmpWord03 = self.myFileBuffRead(wholeOrigSpeechInfoFile, 0x120, 4)
                        if tmpWord03 == "":
                            endOfFileReached = True
                        else:
                            datumUnpacked = unpack('<L', tmpWord03)
                            datumHex = datumUnpacked[0]
                            if datumHex == 0x5:
                                sFilename = "remonkeyedgame.credits.xml"
                                detectedGameId = 1
                            elif datumHex == 0x6:
                                sFilename = "remonkeyedgamepc.credits.xml"
                                detectedGameId = 1 #again
                    elif datumHex == 0x40800000 or datumHex == 0x40600000:
                        # treat them all as the same (they essentially are, but little different).
                        # We can't know for sure from which game they are, or what file, so we can get the detectedGame from the activeGame!!!
                        # (only for line count - could work for quote parsing)
                        # could be : title_windows.credits.xml, title_sd.credits.xml, title.credits.xml
                        sFilename = "title.credits.xml"
                        detectedGameId = self.selGameID


            elif headerHex == 0x15:
                #origSpeechInfoFile.seek(0x18)
                #tmpWord02 = origSpeechInfoFile.read(4)
                tmpWord02 = self.myFileBuffRead(wholeOrigSpeechInfoFile, 0x18, 4)
                if tmpWord02 == "":
                    endOfFileReached = True
                else:
                    datumUnpacked = unpack('<L', tmpWord02)
                    datumHex = datumUnpacked[0]
                    if datumHex == 0x3:
                        sFilename = "remonkeyedgame.credits.xml"
                    elif datumHex == 0x2:
                        sFilename = "remonkeyedgamepc.credits.xml"
                detectedGameId = 2
            elif headerHex == 0x1b:
                #origSpeechInfoFile.seek(0x5A4)
                #tmpWord02 = origSpeechInfoFile.read(4)
                tmpWord02 = self.myFileBuffRead(wholeOrigSpeechInfoFile, 0x5A4, 4)
                if tmpWord02 == "":
                    endOfFileReached = True
                else:
                    datumUnpacked = unpack('<L', tmpWord02)
                    datumHex = datumUnpacked[0]
                    if datumHex == 0x557c:
                        #origSpeechInfoFile.seek(0x2dd0)
                        #tmpWord03 = origSpeechInfoFile.read(4)
                        tmpWord03 = self.myFileBuffRead(wholeOrigSpeechInfoFile, 0x2dd0, 4)
                        if tmpWord03 == "":
                            endOfFileReached = True
                        else:
                            datumUnpacked = unpack('<L', tmpWord03)
                            datumHex = datumUnpacked[0]
                            if datumHex == 0x4270:
                                sFilename = "endgamepc.credits.xml"
                                detectedGameId = 1
                            elif datumHex == 0x4280:
                                sFilename = "endgamepc.credits.xml"
                                detectedGameId = 2
                    elif datumHex == 0x532c:
                        #origSpeechInfoFile.seek(0x2ce8)
                        #tmpWord03 = origSpeechInfoFile.read(4)
                        tmpWord03 = self.myFileBuffRead(wholeOrigSpeechInfoFile, 0x2ce8, 4)
                        if tmpWord03 == "":
                            endOfFileReached = True
                        else:
                            datumUnpacked = unpack('<L', tmpWord03)
                            datumHex = datumUnpacked[0]
                            if datumHex == 0x4098:
                                sFilename = "endgame.credits.xml"
                                detectedGameId = 1
                            elif datumHex == 0x40a8:
                                sFilename = "endgame.credits.xml"
                                detectedGameId = 2

        #
        # TODO: we could return here, if the activeGameId does not match the detected one!
        #

        if(self.selGameID <> detectedGameId):
            detectedNumOfQuotes =0
            #origSpeechInfoFile.close()
            return (detectedNumOfQuotes, detectedGameId, None)

        elif (sFilename in filenameCreditsList and detectedGameId==1) or (sFilename in  filenameCreditsListMISE2 and detectedGameId==2) :
            locallistOfIndexOfAllLinesCreds = []
            del locallistOfIndexOfAllLinesCreds[:]
            beginAddrOfIndexMatrix = 0
            if detectedGameId==1:
                beginAddrOfIndexMatrix =filenameCreditsStartMatrxAddrList[filenameCreditsList.index(sFilename)]
            else:
                beginAddrOfIndexMatrix =filenameCreditsStartMISE2MatrxAddrList[filenameCreditsListMISE2.index(sFilename)]
            detectedNumOfQuotes = 0
            previousValidreadNdx = 0
            endOfFileReached = False
            firstPass = True
            #origSpeechInfoFile.seek(-1, 2)
            #endAddress = origSpeechInfoFile.tell() # temporary put it somewhere near the end of file. Will be updated in the first pass of the while loop to the right value
            endAddress = len(wholeOrigSpeechInfoFile) -2 # temporary put it somewhere near the end of file. Will be updated in the first pass of the while loop to the right value
            #origSpeechInfoFile.seek(beginAddrOfIndexMatrix)
            it00 = 0
            #while endOfFileReached == False and origSpeechInfoFile.tell() < endAddress:
            while endOfFileReached == False and (beginAddrOfIndexMatrix + it00*4) < endAddress:
                #startpos = origSpeechInfoFile.tell()
                startpos = beginAddrOfIndexMatrix + it00*4
    ##            print "%X" % startpos
                #tmpWord = origSpeechInfoFile.read(4)
                tmpWord = self.myFileBuffRead(wholeOrigSpeechInfoFile, startpos, 4)
                it00 += 1
                if tmpWord == "":
                    endOfFileReached = True
                else:
                    readNdxEntry = unpack('<L', tmpWord)
                    readNdx = readNdxEntry[0]
                    quoteStartAddr = readNdx + startpos
                    if firstPass == True:
                        firstPass = False
                        endAddress = quoteStartAddr
                        previousValidreadNdx = readNdx

                    if readNdx <> 0 and quoteStartAddr % 0x10 == 0 and abs(previousValidreadNdx - readNdx ) <= 0x100:
    ##                    print "Another one %X" % startpos
                        previousValidreadNdx = readNdx
                        if retrieveQuotesFlag == True:
                            tmpListForOneCredit = []
                            del tmpListForOneCredit[:]
                            tmpListForOneCredit.append(startpos)
                            tmpListForOneCredit.append(readNdx)
                            locallistOfIndexOfAllLinesCreds.append(tmpListForOneCredit)
                        detectedNumOfQuotes += 1
            if retrieveQuotesFlag == True:
                endOfFileReached = False
                quoteCharList =[]
                quoteCharListCopy=[]
                for ndx in range (0, detectedNumOfQuotes):
                    newQuotelength = 0
                    newUntransQuotelength = 0
                    newQuoteString = ""
                    newQuoteStringThroughGUIPresentFilter =""
                    newUntouchedQuoteString = ""
                    newUntransQuoteString = ""
                    beginAddrOfEnglishQuote = 0
                    beginAddrOfUntransQuote = 0

                    del quoteCharList[:]
                    del quoteCharListCopy[:]
                    beginAddrOfEnglishQuote = locallistOfIndexOfAllLinesCreds[ndx][0] + locallistOfIndexOfAllLinesCreds[ndx][1]
                    #origSpeechInfoFile.seek(beginAddrOfEnglishQuote)
                    it01 = 0
                    while True:
                        #tmpChar = origSpeechInfoFile.read(1)
                        tmpChar = self.myFileBuffRead(wholeOrigSpeechInfoFile, beginAddrOfEnglishQuote+it01, 1)
                        it01 += 1
                        if tmpChar == "":
                            endOfFileReached = True
                            break
                        newChar = unpack('B', tmpChar)
                        if chr(newChar[0]) <> '\x00':
                            newQuotelength += 1
#                            quoteCharList.append(chr(newChar[0]))
                            quoteCharListCopy.append(chr(newChar[0]))
                        else:
                            break

                    if endOfFileReached == False:
#                        newQuoteString = self.makeOriginalStringWithEscapeSequences(quoteCharList)
                        newQuoteStringThroughGUIPresentFilter = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteCharListCopy, pGrabberForTranslationDicts)
                        retrievedQuotesList.append((newQuoteStringThroughGUIPresentFilter, newQuotelength))
#                        print newQuoteStringThroughGUIPresentFilter

        #
        # Hints CSV
        #
        elif ( sFilename == filenameHintsMI1CSV  and detectedGameId==1) or (sFilename == filenameHintsMI2CSV and detectedGameId==2):
            # read from hex addr: 0x76B0. (MISE) there is an matrix of indexes to the start addresse of the quotes.
            # for MI2:SE it seesm to be 0xC6C0
            # Each entry 4 words (4x4 bytes) for as many as 4 hints of the same language id). (little endian -reverse order in bytes)
            # Each word points to the address that is the sum of its value and its own start address
            endOfFileReached = False
            beginAddrOfIndexMatrix = 0x76B0 # MI:SE
            if  detectedGameId==2:
                beginAddrOfIndexMatrix = 0xC6C0 # MI2:SE
            listOflistsOfAllQuotesHintsCSV = []
            del listOflistsOfAllQuotesHintsCSV[:]

            maxNumOfHintsInSeries = 4
            #origSpeechInfoFile.seek(beginAddrOfIndexMatrix)
            #the first value actually also represents (divided by 0x10) how many entries the index has.
            numofEntries = 0
            detectedNumOfQuotes = 0
            #tmpWord = origSpeechInfoFile.read(4)
            tmpWord = self.myFileBuffRead(wholeOrigSpeechInfoFile, beginAddrOfIndexMatrix, 4)
            if tmpWord == "":
                endOfFileReached = True
            else:
                numofEntriesUnpacked = unpack('<L', tmpWord)
                numofEntries = numofEntriesUnpacked[0]
                numofEntries = numofEntries / 0x10
                if endOfFileReached == False:
                    # find the english quotes
                    detectedHintSetEntries = 0
                    while detectedHintSetEntries < numofEntries and endOfFileReached == False:
                        tmpListForOneHintSeries = []
                        del tmpListForOneHintSeries[:]
                        readNdx = -1
                        myiter = 0
                        startOfNewMatrixEnrty = beginAddrOfIndexMatrix + detectedHintSetEntries * 0x10
                        #origSpeechInfoFile.seek(startOfNewMatrixEnrty)
                        #it01 = 0
                        while endOfFileReached  == False and myiter < maxNumOfHintsInSeries:
                            #tmpWord = origSpeechInfoFile.read(4)
                            tmpWord = self.myFileBuffRead(wholeOrigSpeechInfoFile, startOfNewMatrixEnrty+myiter*4, 4)
                            if tmpWord == "":
                                endOfFileReached = True
                                break
                            else:
                                readNdxEntry = unpack('<L', tmpWord)
                                readNdx = readNdxEntry[0]
                                quoteStartAddr = readNdx + startOfNewMatrixEnrty + myiter*4
                                if readNdx <> 0:
                                    tmpListForOneHintSeries.append(quoteStartAddr)
                                if readNdx == 0 or myiter == (maxNumOfHintsInSeries -1):
                                    listOflistsOfAllQuotesHintsCSV.append(tmpListForOneHintSeries)
                                    detectedHintSetEntries += 1
                                    break
                            myiter+=1
                    #debug
                    #print "Total Entries found %d" % detectedHintSetEntries
                    ndx = 0
                    quoteUntransCharList = []
                    for ndx in range (0, numofEntries):
                        if ndx % plithosOfDifferentLanguages == 0:
                            for innerNdx in range(0, len(listOflistsOfAllQuotesHintsCSV[ndx])):
                                newUntransQuotelength = 0
                                newQuoteStringThroughGUIPresentFilter = ""
                                beginAddrOfUntransQuote = 0
                                del quoteUntransCharList[:]

##                                beginAddrOfEnglishQuote = listOflistsOfAllQuotesHintsCSV[ndx][innerNdx]
##                                origSpeechInfoFile.seek(beginAddrOfEnglishQuote)
##                                while True:
##                                    tmpChar = origSpeechInfoFile.read(1)
##                                    if tmpChar == "":
##                                        endOfFileReached = True
##                                        break
##                                    newChar = unpack('B', tmpChar)
##                                    if chr(newChar[0]) == '\x00':
##                                        detectedNumOfQuotes += 1
##                                        break

                                # read the untranslated quote bytes of the selected language.
                                # the begin addr is calcualted similarly for both uiText and Speech.info
                                beginAddrOfUntransQuote = listOflistsOfAllQuotesHintsCSV[ndx+selectedLanguageOffset][innerNdx]
                                #origSpeechInfoFile.seek(beginAddrOfUntransQuote)
                                it02 = 0
                                while True:
                                    #tmpChar = origSpeechInfoFile.read(1)
                                    tmpChar = self.myFileBuffRead(wholeOrigSpeechInfoFile, beginAddrOfUntransQuote+it02, 1)
                                    it02 += 1
                                    if tmpChar == "":
                                        endOfFileReached = True
                                        break
                                    newChar = unpack('B', tmpChar)
                                    if chr(newChar[0]) <> '\x00':
                                        if retrieveQuotesFlag == True:
                                            newUntransQuotelength += 1
                                            quoteUntransCharList.append(chr(newChar[0]))
                                    else:
                                        detectedNumOfQuotes += 1
                                        break
                                if endOfFileReached == False and retrieveQuotesFlag == True:
    ##                            print quoteUntransCharList
                                    newQuoteStringThroughGUIPresentFilter = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteUntransCharList, pGrabberForTranslationDicts)
                                    retrievedQuotesList.append((newQuoteStringThroughGUIPresentFilter, newUntransQuotelength))

        #
        # Speech info - ui text: this case is for SoMI (monkey island 1, selGameId ==1)
        #
        elif (sFilename == filenameSpeechInfo or sFilename == filenameUIText) and detectedGameId==1:
            quoteUntransCharList = []
            detectedNumOfQuotes = 0

            currentline = 1
            endOfFileReached = False
            # read the english quote bytes after the header (which is 0x10 bytes).
            while endOfFileReached == False:
                newUntransQuotelength = 0
                del quoteUntransCharList[:]
                newQuoteStringThroughGUIPresentFilter = ""

                beginAddrOfEnglishQuote = 0
                if sFilename == filenameSpeechInfo:
                    beginAddrOfEnglishQuote = 0x10 * currentline + (currentline-1)* (plithosOfDifferentLanguages * 0x100 + 0x20) # 0x20 are the two last 0x20 byte chunk that show which character speaks a line.
                elif sFilename == filenameUIText:
                    beginAddrOfEnglishQuote = 0x100 * currentline + (currentline-1)* (plithosOfDifferentLanguages * 0x100) # 0x100 are the first header system descriptive menu sting for each quote

                beginAddrOfUntransQuote = beginAddrOfEnglishQuote + selectedLanguageOffset*0x100
                ##origSpeechInfoFile.seek(beginAddrOfEnglishQuote)
                #origSpeechInfoFile.seek(beginAddrOfUntransQuote)
                for i in range(0, 0x100):
                    #tmpChar = origSpeechInfoFile.read(1)
                    tmpChar = self.myFileBuffRead(wholeOrigSpeechInfoFile, beginAddrOfUntransQuote+i, 1)
                    if tmpChar == "":
                        endOfFileReached = True
                        break
                    newChar = unpack('B', tmpChar)
                    if chr(newChar[0]) <> '\x00':
                        if retrieveQuotesFlag == True:
                            newUntransQuotelength += 1
                            quoteUntransCharList.append(chr(newChar[0]))
                    else:
                        detectedNumOfQuotes +=1
                        break
                if endOfFileReached == False and retrieveQuotesFlag == True:
                    newQuoteStringThroughGUIPresentFilter = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteUntransCharList, pGrabberForTranslationDicts)
                    retrievedQuotesList.append((newQuoteStringThroughGUIPresentFilter, newUntransQuotelength))

                currentline +=1
        #
        # this case is for MI2:SE (monkey island 2, selGameId ==2)
        #
        elif (sFilename == filenameFrSpeechInfo or sFilename == filenameFrUIText)  and detectedGameId==2:
            quoteUntransCharList = []
            beginAddrOfIndexMatrix = 0x4
            endOfFileReached = False
            begaddr = 0
            if sFilename == filenameFrSpeechInfo:
                #origSpeechInfoFile.seek(beginAddrOfIndexMatrix + 8 +12 )
                begaddr = beginAddrOfIndexMatrix + 8 +12
            else:
                #origSpeechInfoFile.seek(beginAddrOfIndexMatrix)
                begaddr = beginAddrOfIndexMatrix

            detectedNumOfQuotes = 0
            #tmpWord = origSpeechInfoFile.read(4)
            tmpWord = self.myFileBuffRead(wholeOrigSpeechInfoFile, begaddr, 4)
            if tmpWord == "":
                endOfFileReached = True
            else:
                numofEntriesUnpacked = unpack('<L', tmpWord)
                detectedNumOfQuotes = numofEntriesUnpacked[0]
                if sFilename == filenameFrSpeechInfo:
                    detectedNumOfQuotes = (detectedNumOfQuotes + beginAddrOfIndexMatrix + 8 + 12 - beginAddrOfIndexMatrix)/ 0x20
                else:
                    detectedNumOfQuotes = (detectedNumOfQuotes + beginAddrOfIndexMatrix - beginAddrOfIndexMatrix)/ 0x8
                #debug
                #print "number Of entries %d" % detectedNumOfQuotes
                if retrieveQuotesFlag == True and endOfFileReached == False:
                    # find the foreign quotes
                    ndx = 0
                    detectedQuoteEntries = 0
                    tmpListForFrQuotesAddrs = []
                    del tmpListForFrQuotesAddrs[:]

                    while detectedQuoteEntries < detectedNumOfQuotes and endOfFileReached == False:
                        readNdx = -1
                        startOfNewMatrixEnrty = 0
                        startOfNewFrenchQuoteIndex = 0
                        if sFilename == filenameFrSpeechInfo:
                            startOfNewMatrixEnrty = beginAddrOfIndexMatrix + detectedQuoteEntries * 0x20
                            startOfNewFrenchQuoteIndex = startOfNewMatrixEnrty + 8 +12 + 4 + 4
                        else:
                            startOfNewMatrixEnrty = beginAddrOfIndexMatrix + detectedQuoteEntries * 0x8
                            startOfNewFrenchQuoteIndex = startOfNewMatrixEnrty + 4
                        #origSpeechInfoFile.seek(startOfNewFrenchQuoteIndex)
                        #tmpWordLbl = origSpeechInfoFile.read(4)
                        tmpWordLbl = self.myFileBuffRead(wholeOrigSpeechInfoFile, startOfNewFrenchQuoteIndex, 4)
                        if tmpWordLbl == "":
                            endOfOrigFileReached = True
                            break
                        else:
                            readNdxEntryLbl = unpack('<L', tmpWordLbl)
                            readNdxLbl = readNdxEntryLbl[0]
                            quoteStartAddrLbl = readNdxLbl + startOfNewFrenchQuoteIndex
                            if readNdxLbl <> 0:
                                tmpListForFrQuotesAddrs.append(quoteStartAddrLbl)
                                detectedQuoteEntries +=1
                            elif readNdx == 0:
                                endOfOrigFileReached = True
                                break
                    #
                    # we continue to parse the actual quotes
                    #
                    ndx = 0
                    for ndx in range (0, detectedQuoteEntries):
                        newUntransQuotelength = 0
                        newQuoteStringThroughGUIPresentFilter = ""
                        beginAddrOfUntransQuote = 0
                        del quoteUntransCharList[:]

                        if endOfFileReached == False:
                            # read the untranslated quote bytes of the french/foreign language of the speech.info file.
                            # the begin addr is calcualted similarly for both uiText and Speech.info
                            beginAddrOfUntransQuote = tmpListForFrQuotesAddrs[ndx]
                            #origSpeechInfoFile.seek(beginAddrOfUntransQuote)
                            it00 = 0
                            while True:
                                #tmpChar = origSpeechInfoFile.read(1)
                                tmpChar = self.myFileBuffRead(wholeOrigSpeechInfoFile, beginAddrOfUntransQuote+it00, 1)
                                it00 += 1
                                if tmpChar == "":
                                    endOfFileReached = True
                                    break
                                newChar = unpack('B', tmpChar)
                                if chr(newChar[0]) <> '\x00':
                                    newUntransQuotelength += 1
                                    quoteUntransCharList.append(chr(newChar[0]))
                                else:
                                    break
                            if endOfFileReached == False:
    ##                            print quoteUntransCharList
                                newQuoteStringThroughGUIPresentFilter = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteUntransCharList, pGrabberForTranslationDicts)
                                retrievedQuotesList.append((newQuoteStringThroughGUIPresentFilter, newUntransQuotelength))

        # all else is unsupported
        else:
            #TODO: debug and error message. Show in message box or SessionsErors and quit?
            #print "Error - unsupported type of file. Cannot calculate quote entries"
            detectedNumOfQuotes = 0

        #origSpeechInfoFile.close()
#        print "Detected %d quotes in file. For Game ID: %d." % (detectedNumOfQuotes, detectedGameId)
        return (detectedNumOfQuotes, detectedGameId, retrievedQuotesList)

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #
    # This method loads a quotes' file in the gui columns.
    #
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def parseQuoteFile(self, fullPathsFilename, pSelectedLanguageOffset, pGrabberForTranslationDicts, isTheOriginalFile = True):
        global listOfEnglishLinesSpeechInfo
        global listOfForeignLinesOrigSpeechInfo
        global listOfUntranslatedLinesSpeechInfo
        global fullcopyFileName

        filepathSplitTbl = os.path.split(fullPathsFilename)
        sFilename = filepathSplitTbl[1]
        pathTosFile = filepathSplitTbl[0]

        #
        # TODO: For the translation file we need the ID of the associated original file to find the "sFilename" (or replace that with another variable) and chose the right action.
        #       we don't work with the name of the associated original file, because it could be renamed. Do we do need its MD5, here?
        if isTheOriginalFile == False:
            pass

        """ parsing one of the three quote files. Putting quotes in lists.
        """
        #
        # A credits file only has the english language so we need to create a copy to work on (for the translated credits!)
        #
        if (sFilename in filenameCreditsList and self.selGameID==1) or (sFilename in  filenameCreditsListMISE2 and self.selGameID==2) :
            global listOfAllUntouchedLinesCredits
            global listOfIndexOfAllLinesCreds
            global listOfIndexOfAllTransLinesCreds

            del listOfEnglishLinesSpeechInfo[:]
            del listOfForeignLinesOrigSpeechInfo[:]
            del listOfAllUntouchedLinesCredits[:]
            del listOfIndexOfAllLinesCreds[:]
            del listOfIndexOfAllTransLinesCreds[:]

            quoteCharList = []
            quoteCharListCopy = []
            quoteUntransCharList = []

            #  look for copy file and create it if it does not exist and open it
            #  Also save a new session for the original file and copy file in the DB
            transSpeechInfoFile = None
#            fullcopyFileName = self.createAndGetNewCopyFile(fullPathsFilename)
#            self.createAndSaveSession(fullPathsFilename, fullcopyFileName)
            self.loadASession(pSessionName = None, pOriginalfullPathsFilename = fullPathsFilename)
            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()

            beginAddrOfIndexMatrix = 0
            if self.selGameID==1:
                beginAddrOfIndexMatrix =filenameCreditsStartMatrxAddrList[filenameCreditsList.index(sFilename)]
            else:
                beginAddrOfIndexMatrix =filenameCreditsStartMISE2MatrxAddrList[filenameCreditsListMISE2.index(sFilename)]
    #        print "start address %X" % beginAddrOfIndexMatrix
            origSpeechInfoFile = open(fullPathsFilename, 'rb')
            wholeOrigSpeechInfoFile = origSpeechInfoFile.read()
            origSpeechInfoFile.close()
            detectedCreditsEntries = 0

            previousValidreadNdx = 0
            endOfFileReached = False
            firstPass = True
            #origSpeechInfoFile.seek(-1, 2)
            #endAddress = origSpeechInfoFile.tell() # temporary put it somewhere near the end of file. Will be updated in the first pass of the while loop to the right value
            endAddress = len(wholeOrigSpeechInfoFile) -2
            #origSpeechInfoFile.seek(beginAddrOfIndexMatrix)
            #while endOfFileReached == False and origSpeechInfoFile.tell() < endAddress:
            it00 = 0
            while endOfFileReached == False and (beginAddrOfIndexMatrix + it00*4) < endAddress:
                #startpos = origSpeechInfoFile.tell()
                startpos = beginAddrOfIndexMatrix + it00*4
    ##            print "%X" % startpos
                #tmpWord = origSpeechInfoFile.read(4)
                tmpWord = self.myFileBuffRead(wholeOrigSpeechInfoFile, startpos, 4)
                it00 += 1
                if tmpWord == "":
                    endOfFileReached = True
                else:
                    readNdxEntry = unpack('<L', tmpWord)
                    readNdx = readNdxEntry[0]
                    quoteStartAddr = readNdx + startpos
                    if firstPass == True:
                        firstPass = False
                        endAddress = quoteStartAddr
                        previousValidreadNdx = readNdx

                    if readNdx <> 0 and quoteStartAddr % 0x10 == 0 and abs(previousValidreadNdx - readNdx ) <= 0x100:
    ##                    print "Another one %X" % startpos
                        previousValidreadNdx = readNdx
                        tmpListForOneCredit = []
                        del tmpListForOneCredit[:]
                        tmpListForOneCredit.append(startpos)
                        tmpListForOneCredit.append(readNdx)
                        listOfIndexOfAllLinesCreds.append(tmpListForOneCredit)
                        detectedCreditsEntries += 1
            #debug
            #print "Total Credits Index Entries Found: %d" % detectedCreditsEntries
            #print "and list length is %d " % len(listOfIndexOfAllLinesCreds)
    ##
    ## TODO: make into a function. Process repeated BUT MORE LITE this time, for the translated file
    ##
            transSpeechInfoFile =  open(fullcopyFileName, 'rb')
            wholeTransSpeechInfoFile = transSpeechInfoFile.read()
            transSpeechInfoFile.close()
            detectedTransCreditsEntries = 0
            endOfFileReached = False
    #
    #       Careful. We get the addr of the indexes from the list made from the original file. No need to search them again. We only need the new values!
    #
            for ndx1 in range(0, len(listOfIndexOfAllLinesCreds) ):
                startpos = listOfIndexOfAllLinesCreds[ndx1][0]
                #transSpeechInfoFile.seek(listOfIndexOfAllLinesCreds[ndx1][0])
                #tmpWord = transSpeechInfoFile.read(4)
                tmpWord = self.myFileBuffRead(wholeTransSpeechInfoFile, startpos, 4)
                if tmpWord == "":
                    endOfFileReached = True
                    break
                else:
                    readNdxEntry = unpack('<L', tmpWord)
                    readNdx = readNdxEntry[0]
                    quoteStartAddr = readNdx + startpos
                    tmpListForOneCredit = []
                    del tmpListForOneCredit[:]
                    tmpListForOneCredit.append(startpos)
                    tmpListForOneCredit.append(readNdx)
                    listOfIndexOfAllTransLinesCreds.append(tmpListForOneCredit)
                    detectedTransCreditsEntries += 1
            #debug
            #print "Total Translated Credits Index Entries Found: %d" % detectedTransCreditsEntries
            #print "and trans list length is %d " % len(listOfIndexOfAllTransLinesCreds)

    #
    # Back to the original file
    #
            endOfFileReached = False
            for ndx in range (0, detectedCreditsEntries):
                newQuotelength = 0
                newUntransQuotelength = 0
                newQuoteString = ""
                newQuoteStringThroughGUIPresentFilter =""
                newUntouchedQuoteString = ""
                newUntransQuoteString = ""
                beginAddrOfEnglishQuote = 0
                beginAddrOfUntransQuote = 0

                del quoteCharList[:]
                del quoteCharListCopy[:]
                beginAddrOfEnglishQuote = listOfIndexOfAllLinesCreds[ndx][0] + listOfIndexOfAllLinesCreds[ndx][1]
                #origSpeechInfoFile.seek(beginAddrOfEnglishQuote)
                it01 = 0
                while True:
                    #tmpChar = origSpeechInfoFile.read(1)
                    tmpChar = self.myFileBuffRead(wholeOrigSpeechInfoFile, beginAddrOfEnglishQuote+it01, 1)
                    it01 += 1
                    if tmpChar == "":
                        endOfFileReached = True
                        break
                    newChar = unpack('B', tmpChar)
                    if chr(newChar[0]) <> '\x00':
                        newQuotelength += 1
        #                print newChar[0]
                        quoteCharList.append(chr(newChar[0]))
                        quoteCharListCopy.append(chr(newChar[0]))
                    else:
                        break

                if endOfFileReached == False:
                    newQuoteString = self.makeOriginalStringWithEscapeSequences(quoteCharList)
                    newQuoteStringThroughGUIPresentFilter = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteCharListCopy, pGrabberForTranslationDicts)

                    #
                    # SPECIAL FOR CREDITS the original quote is stored untouched and with the padded 0x10!
                    #
                    quoteCharList.append('\x00')
                    origLengthAsMultiSixteen = newQuotelength + 1 # The file counts the first 0x00 after the end as a character.
                    if origLengthAsMultiSixteen % 16 > 0:
                        origLengthAsMultiSixteen = origLengthAsMultiSixteen - (origLengthAsMultiSixteen % 16) + 0x10
                        while(len(quoteCharList) < origLengthAsMultiSixteen):
                            quoteCharList.append('\x00')
                    newUntouchedQuoteString = "".join(quoteCharList)
                    if endOfFileReached == False:
    ##                  print quoteUntransCharList
                        newUntransQuoteString = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteCharList, pGrabberForTranslationDicts)
        #               # DEBUG
        #                print "Translating: %s length: %d" % (newQuoteString, newQuotelength)
        #                print "Translated to: %s length: %d" %  (newUntransQuoteString, newUntransQuotelength)
                        listOfEnglishLinesSpeechInfo.append((beginAddrOfEnglishQuote,newQuoteString,newQuotelength))
                        listOfForeignLinesOrigSpeechInfo.append((newQuoteStringThroughGUIPresentFilter,newQuotelength)) # new for detecting changed lines and for merging function
                        listOfAllUntouchedLinesCredits.append((beginAddrOfEnglishQuote,newUntouchedQuoteString,newQuotelength)) # ONLY for the original quote we append in the WHOLE list. For the untranslated this is done in the else statement with the other languages in its proper turn
    #
    # TODO: Back to the translation file. Process is somewhat repeated. PUT IT IN FUNCTION!
    #
            endOfFileReached = False
            for ndx in range (0, detectedTransCreditsEntries):
                newUntransQuotelength = 0
                newUntransQuoteString = ""
                beginAddrOfUntransQuote = 0

                del quoteUntransCharList[:]
                beginAddrOfEnglishQuote = listOfIndexOfAllTransLinesCreds[ndx][0] + listOfIndexOfAllTransLinesCreds[ndx][1]
                #transSpeechInfoFile.seek(beginAddrOfEnglishQuote)
                it00 = 0
                while True:
                    #tmpChar = transSpeechInfoFile.read(1)
                    tmpChar = self.myFileBuffRead(wholeTransSpeechInfoFile, beginAddrOfEnglishQuote+it00, 1)
                    it00 += 1
                    if tmpChar == "":
                        endOfFileReached = True
                        break
                    newChar = unpack('B', tmpChar)
                    if chr(newChar[0]) <> '\x00':
                        newUntransQuotelength += 1
        #                print newChar[0]
                        quoteUntransCharList.append(chr(newChar[0]))
                    else:
                        break

                if endOfFileReached == False:
    #                            print quoteUntransCharList
                    newUntransQuoteString = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteUntransCharList, pGrabberForTranslationDicts)
                    listOfUntranslatedLinesSpeechInfo.append((beginAddrOfEnglishQuote,newUntransQuoteString,newUntransQuotelength))

            #transSpeechInfoFile.close()
            #origSpeechInfoFile.close()
            #debug
            #print("orig foreign quote found: %d" % (len(listOfForeignLinesOrigSpeechInfo)))
            return (listOfEnglishLinesSpeechInfo, listOfUntranslatedLinesSpeechInfo)
        ##########################################################################
        #  CSV HINTS CASE
        # MONKEY ISLAND 1 & MI 2
        ##########################################################################
        elif ( sFilename == filenameHintsMI1CSV  and self.selGameID==1) or (sFilename == filenameHintsMI2CSV and self.selGameID==2):

            global listOfAllLinesHintsCSV
            global listOflistsOfAllQuotesHintsCSV
            localListOflistsOfAllQuotesHintsCSVOrigFile = []

            del listOfEnglishLinesSpeechInfo[:]
            del listOfForeignLinesOrigSpeechInfo[:]
            del listOfUntranslatedLinesSpeechInfo[:]
            del listOfAllLinesHintsCSV[:]
            del listOflistsOfAllQuotesHintsCSV[:]
            del localListOflistsOfAllQuotesHintsCSVOrigFile[:]
            self.loadASession(pSessionName = None, pOriginalfullPathsFilename = fullPathsFilename)

            # from the original file we need the original untranslated foreign language quotes!
            origSpeechInfoFile = open(fullPathsFilename, 'rb')
            wholeOrigSpeechInfoFile = origSpeechInfoFile.read()
            origSpeechInfoFile.close()

            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()
            copySpeechInfoFile = open(fullcopyFileName, 'rb')
            wholeCopySpeechInfoFile = copySpeechInfoFile.read()
            copySpeechInfoFile.close()

            # read from hex addr: 0x76B0. (MISE) there is an matrix of indexes to the start addresse of the quotes.
            # for MI2:SE it seesm to be 0xC6C0
            # Each entry 4 words (4x4 bytes) for as many as 4 hints of the same language id). (little endian -reverse order in bytes)
            # Each word points to the address that is the sum of its value and its own start address
            matrixOfIndexesForHints = [] # a list with entries lists of at most 4 integers (indexes)
            quoteCharList = []
            quoteUntransCharList = []
            origQuoteUntransCharList = []
            endOfFileReached = False
            endOfOrigFileReached = False
            countOfZeroLengthOrigQuotes = 0
            countOfZeroLengthTransQuotes = 0
            countOfZeroLengthRestQuotes = 0
            beginAddrOfIndexMatrix = 0x76B0 # MI:SE
            if  self.selGameID==2:
                beginAddrOfIndexMatrix = 0xC6C0 # MI2:SE

            maxNumOfHintsInSeries = 4
            #copySpeechInfoFile.seek(beginAddrOfIndexMatrix)
            #the first value actually also represents (divided by 0x10) how many entries the index has.
            numofEntries = 0
            #tmpWord = copySpeechInfoFile.read(4)
            tmpWord = self.myFileBuffRead(wholeCopySpeechInfoFile, beginAddrOfIndexMatrix, 4)
            if tmpWord == "":
                endOfFileReached = True
            else:
    #            unpack('hhl', '\x00\x01\x00\x02\x00\x00\x00\x03')
                numofEntriesUnpacked = unpack('<L', tmpWord)
                numofEntries = numofEntriesUnpacked[0]
                numofEntries = numofEntries / 0x10
                #debug
                #print "number Of entries %d" % numofEntries

            if endOfFileReached == False:
                # find the english quotes

                detectedHintSetEntries = 0
                while detectedHintSetEntries < numofEntries and endOfFileReached == False:
                    tmpListForOneHintSeries = []
                    tmpListForOneHintSeriesOrig = []
                    del tmpListForOneHintSeries[:]
                    del tmpListForOneHintSeriesOrig[:]
                    readNdx = -1
                    myiter = 0
                    startOfNewMatrixEnrty = beginAddrOfIndexMatrix + detectedHintSetEntries * 0x10
    #                print startOfNewMatrixEnrty
                    #copySpeechInfoFile.seek(startOfNewMatrixEnrty)
                    while endOfFileReached  == False and myiter < maxNumOfHintsInSeries:
                        #tmpWord = copySpeechInfoFile.read(4)
                        tmpWord = self.myFileBuffRead(wholeCopySpeechInfoFile, startOfNewMatrixEnrty+myiter*4, 4)
                        if tmpWord == "":
                            endOfFileReached = True
                            break
                        else:
                            readNdxEntry = unpack('<L', tmpWord)
                            readNdx = readNdxEntry[0]
                            quoteStartAddr = readNdx + startOfNewMatrixEnrty + myiter*4
                            if readNdx <> 0:
                                tmpListForOneHintSeries.append(quoteStartAddr)
                            if readNdx == 0 or myiter == (maxNumOfHintsInSeries -1):
                                listOflistsOfAllQuotesHintsCSV.append(tmpListForOneHintSeries)
                                detectedHintSetEntries += 1
                                break
                        myiter+=1
                    #
                    # identical for populating localListOflistsOfAllQuotesHintsCSVOrigFile for the original file
                    #
                    myiterOrig = 0
                    #origSpeechInfoFile.seek(startOfNewMatrixEnrty)
                    while endOfOrigFileReached  == False and myiterOrig < maxNumOfHintsInSeries:
                        #tmpWord = origSpeechInfoFile.read(4)
                        tmpWord = self.myFileBuffRead(wholeOrigSpeechInfoFile, startOfNewMatrixEnrty+myiterOrig*4, 4)
                        if tmpWord == "":
                            endOfOrigFileReached = True
                            break
                        else:
                            readNdxEntry = unpack('<L', tmpWord)
                            readNdx = readNdxEntry[0]
                            quoteStartAddr = readNdx + startOfNewMatrixEnrty + myiterOrig*4
                            if readNdx <> 0:
                                tmpListForOneHintSeriesOrig.append(quoteStartAddr)
                            if readNdx == 0 or myiterOrig == (maxNumOfHintsInSeries -1):
                                localListOflistsOfAllQuotesHintsCSVOrigFile.append(tmpListForOneHintSeriesOrig)
                                #detectedHintSetEntries += 1
                                break
                        myiterOrig+=1
                #debug
                #print "Total Entries found %d" % detectedHintSetEntries
                ndx = 0
                for ndx in range (0, numofEntries):
    #            while ndx < len(listOflistsOfAllQuotesHintsCSV):
    #                print "list of lists entry %d: %s" % (ndx+1,listOflistsOfAllQuotesHintsCSV[ndx])
                    if ndx % plithosOfDifferentLanguages == 0:
                        for innerNdx in range(0, len(listOflistsOfAllQuotesHintsCSV[ndx])):
                            newQuotelength = 0
                            newUntransQuotelength = 0
                            origNewUntransQuotelength = 0
                            newQuoteString = ""
                            newQuoteStringThroughGUIPresentFilter = ""
                            newUntouchedQuoteString = ""
                            newUntransQuoteString = ""
                            beginAddrOfEnglishQuote = 0
                            beginAddrOfUntransQuote = 0

                            del quoteCharList[:]
                            del quoteUntransCharList[:]
                            del origQuoteUntransCharList[:]
                            beginAddrOfEnglishQuote = listOflistsOfAllQuotesHintsCSV[ndx][innerNdx]
                            #copySpeechInfoFile.seek(beginAddrOfEnglishQuote)
                            it00 = 0
                            while True:
                                #tmpChar = copySpeechInfoFile.read(1)
                                tmpChar = self.myFileBuffRead(wholeCopySpeechInfoFile, beginAddrOfEnglishQuote+it00, 1)
                                it00 += 1
                                if tmpChar == "":
                                    endOfFileReached = True
                                    break
                                newChar = unpack('B', tmpChar)
                                if chr(newChar[0]) <> '\x00':
                                    newQuotelength += 1
                    #                print newChar[0]
                                    quoteCharList.append(chr(newChar[0]))
                                else:
                                    break

                            if endOfFileReached == False:
    #                            print quoteCharList
                                newQuoteString = self.makeOriginalStringWithEscapeSequences(quoteCharList)
                                #
                                # SPECIAL FOR HINTS CSV the original quote is stored untouched and with the padded 0x10!
                                #
                                quoteCharList.append('\x00')
                                origLengthAsMultiSixteen = newQuotelength + 1 # The file counts the first 0x00 after the end as a character.
                                if origLengthAsMultiSixteen % 16 > 0:
                                    origLengthAsMultiSixteen = origLengthAsMultiSixteen - (origLengthAsMultiSixteen % 16) + 0x10
                                    while(len(quoteCharList) < origLengthAsMultiSixteen):
                                        quoteCharList.append('\x00')
                                newUntouchedQuoteString = "".join(quoteCharList)
                #               # DEBUG!
                #                print "Remade char list: %s" % self.remakeCharlistWithNoEscapeSequences(newQuoteString)

                                # read the untranslated quote bytes of the selected language.
                                # the begin addr is calcualted similarly for both uiText and Speech.info
                                beginAddrOfUntransQuote = listOflistsOfAllQuotesHintsCSV[ndx+pSelectedLanguageOffset][innerNdx]
                                #copySpeechInfoFile.seek(beginAddrOfUntransQuote)
                                it01 = 0
                                while True:
                                    #tmpChar = copySpeechInfoFile.read(1)
                                    tmpChar = self.myFileBuffRead(wholeCopySpeechInfoFile, beginAddrOfUntransQuote+it01, 1)
                                    it01 += 1
                                    if tmpChar == "":
                                        endOfFileReached = True
                                        break
                                    newChar = unpack('B', tmpChar)
                                    if chr(newChar[0]) <> '\x00':
                                        newUntransQuotelength += 1
                                        quoteUntransCharList.append(chr(newChar[0]))
                                    else:
                                        break
                                #
                                # the original foreign quote is in the same position in the original file. OR IS IT?
                                beginAddrOfUntransQuoteOrig = localListOflistsOfAllQuotesHintsCSVOrigFile[ndx+pSelectedLanguageOffset][innerNdx]
                                #origSpeechInfoFile.seek(beginAddrOfUntransQuoteOrig)
                                it02 = 0
                                while True:
                                    #tmpChar = origSpeechInfoFile.read(1)
                                    tmpChar = self.myFileBuffRead(wholeOrigSpeechInfoFile, beginAddrOfUntransQuoteOrig+it02, 1)
                                    it02 += 1
                                    if tmpChar == "":
                                        endOfOrigFileReached = True
                                        break
                                    newChar = unpack('B', tmpChar)
                                    if chr(newChar[0]) <> '\x00':
                                        origNewUntransQuotelength += 1
                                        origQuoteUntransCharList.append(chr(newChar[0]))
                                    else:
                                        break


                            #
                            if endOfFileReached == False:
    ##                            print quoteUntransCharList
                                newUntransQuoteString = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteUntransCharList, pGrabberForTranslationDicts)
                                newQuoteStringThroughGUIPresentFilter = self.makeStringInReadableExtAsciiCharlistToBeListed(origQuoteUntransCharList, pGrabberForTranslationDicts)
                                #if newQuotelength == 0 or newUntransQuotelength == 0:
                #               # DEBUG
                #                print "Translating: %s length: %d" % (newQuoteString, newQuotelength)
                #                print "Translated to: %s length: %d" %  (newUntransQuoteString, newUntransQuotelength)
                                listOfEnglishLinesSpeechInfo.append((beginAddrOfEnglishQuote,newQuoteString,newQuotelength))
                                listOfUntranslatedLinesSpeechInfo.append((beginAddrOfUntransQuote,newUntransQuoteString,newUntransQuotelength))
                                listOfForeignLinesOrigSpeechInfo.append((newQuoteStringThroughGUIPresentFilter,origNewUntransQuotelength)) # new for detecting changed lines and for merging function

                                listOfAllLinesHintsCSV.append((beginAddrOfEnglishQuote,newUntouchedQuoteString,newQuotelength)) # ONLY for the original quote we append in the WHOLE list. For the untranslated this is done in the else statement with the other languages in its proper turn
                #                print specialCharQuoteList
                #                print quoteUntransCharList

                                if newQuotelength == 0:
                                    countOfZeroLengthOrigQuotes += 1
                                if newUntransQuotelength == 0:
                                    countOfZeroLengthTransQuotes += 1
                        #end inner for loop
                    else: #if we are in one of the rest languages quotes (including the one we are translating into.HERE WE APPEND IN THE FULL LIST OF QUOTES)
                        for innerNdx in range(0, len(listOflistsOfAllQuotesHintsCSV[ndx])):
                            newRestQuoteString = ""
                            newRestQuotelength = 0
                            beginAddrOfRestQuote = 0
                            del quoteCharList[:]
                            del quoteUntransCharList[:]
                            beginAddrOfRestQuote = listOflistsOfAllQuotesHintsCSV[ndx][innerNdx]
                            #copySpeechInfoFile.seek(beginAddrOfRestQuote)
                            it00 = 0
                            while True:
                                #tmpChar = copySpeechInfoFile.read(1)
                                tmpChar = self.myFileBuffRead(wholeCopySpeechInfoFile, beginAddrOfRestQuote+it00, 1)
                                it00 += 1
                                if tmpChar == "":
                                    endOfFileReached = True
                                    break
                                newChar = unpack('B', tmpChar)
                                if chr(newChar[0]) <> '\x00':
                                    newRestQuotelength += 1
                    #                print newChar[0]
                                    quoteCharList.append(chr(newChar[0]))
                                else:
                                    break
                            if endOfFileReached == False:
                                origLengthAsMultiSixteen = newRestQuotelength + 1 # The file counts the first 0x00 after the end as a character.
                                if origLengthAsMultiSixteen % 16 > 0:
                                    origLengthAsMultiSixteen = origLengthAsMultiSixteen - (origLengthAsMultiSixteen % 16) + 0x10
                                    while(len(quoteCharList) < origLengthAsMultiSixteen):
                                        quoteCharList.append('\x00')

                                newRestQuoteString = "".join(quoteCharList)
                                listOfAllLinesHintsCSV.append((beginAddrOfRestQuote,newRestQuoteString,newRestQuotelength))
                                # not really needed this check.
                                if newRestQuotelength == 0:
                                    countOfZeroLengthRestQuotes += 1

                    #end if indx % 5 ==0 or else
                #end outer for loop
    #        print "ECHO ECHO ECHO"
    #        print listOfAllLinesHintsCSV
    #        print "ECHO ECHO ECHO"
            #copySpeechInfoFile.close()
            #origSpeechInfoFile.close()
            #debug
            #print("orig foreign quote found: %d" % (len(listOfForeignLinesOrigSpeechInfo)))
            return (listOfEnglishLinesSpeechInfo, listOfUntranslatedLinesSpeechInfo)

        ##########################################################################
        #  UI TEXT CASE
        #  AND SPEECH INFO CASE WITH SLIGHT VARIATIONS
        # Text UI has for each UI string sequence:
        #                           a 0x100 chars block for descriptive "header quote" or "system UI string"
        #                           a 0x100 chars block for the original english quote
        #                           and the rest of the quote sequence (for the other 4 languages) follows in 0x100 char blocks
        # Speech info has for each quote sequence:
        #                            one header of 0x10 bytes,
        #                            then 0x100 char block for the original quote,
        #                            then the rest of the quote sequence (for the other 4 languages) in 0x100 char blocks
        #                            AND finally a 0x20 block with info about who/where it is spoken
        ##########################################################################
        # this case is for SoMI (monkey island 1, selGameId ==1)
        elif (sFilename == filenameSpeechInfo or sFilename == filenameUIText) and self.selGameID==1:
            self.loadASession(pSessionName = None, pOriginalfullPathsFilename = fullPathsFilename)
            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()

            del listOfEnglishLinesSpeechInfo[:]
            del listOfForeignLinesOrigSpeechInfo[:]
            del listOfUntranslatedLinesSpeechInfo[:]
            origSpeechInfoFile = open(fullPathsFilename, 'rb')
            wholeOrigSpeechInfoFile = origSpeechInfoFile.read()
            origSpeechInfoFile.close()

            copySpeechInfoFile = open(fullcopyFileName, 'rb')
            wholeCopySpeechInfoFile = copySpeechInfoFile.read()
            copySpeechInfoFile.close()

            currentline = 1
            quoteCharList = []
            quoteUntransCharList = []
            origQuoteUntransCharList = []

            endOfFileReached = False
            endOfOrigFileReached = False
            countOfZeroLengthOrigQuotes = 0
            countOfZeroLengthTransQuotes = 0
            # read the english quote bytes after the header (which is 0x10 bytes).
            while endOfFileReached == False:

                newQuotelength = 0
                newUntransQuotelength = 0
                origNewUntransQuotelength = 0
                newQuoteString = ""
                newQuoteStringThroughGUIPresentFilter = ""
                newUntransQuoteString = ""
                beginAddrOfEnglishQuote = 0
                beginAddrOfUntransQuote = 0
                del quoteCharList[:]
                del quoteUntransCharList[:]
                del origQuoteUntransCharList[:]

                beginAddrOfEnglishQuote = 0
                if sFilename == filenameSpeechInfo:
                    beginAddrOfEnglishQuote = 0x10 * currentline + (currentline-1)* (plithosOfDifferentLanguages * 0x100 + 0x20) # 0x20 are the two last 0x20 byte chunk that show which character speaks a line.
                elif sFilename == filenameUIText:
                    beginAddrOfEnglishQuote = 0x100 * currentline + (currentline-1)* (plithosOfDifferentLanguages * 0x100) # 0x100 are the first header system descriptive menu sting for each quote
                #copySpeechInfoFile.seek(beginAddrOfEnglishQuote)
                for i in range(0, 0x100):
                    #tmpChar = copySpeechInfoFile.read(1)
                    tmpChar = self.myFileBuffRead(wholeCopySpeechInfoFile, beginAddrOfEnglishQuote+i, 1)
                    if tmpChar == "":
                        endOfFileReached = True
                        break
                    newChar = unpack('B', tmpChar)
                    if chr(newChar[0]) <> '\x00':
                        newQuotelength += 1
        #                print newChar[0]
                        quoteCharList.append(chr(newChar[0]))
                    else:
                        break

                if endOfFileReached == False:
    #                print quoteCharList
                    newQuoteString = self.makeOriginalStringWithEscapeSequences(quoteCharList)
    #               # DEBUG!
    #                print "Remade char list: %s" % self.remakeCharlistWithNoEscapeSequences(newQuoteString)

                    # read the untranslated quote bytes of the selected language.
                    # the begin addr is calcualted similarly for both uiText and Speech.info
                    beginAddrOfUntransQuote = beginAddrOfEnglishQuote + pSelectedLanguageOffset*0x100
                    #copySpeechInfoFile.seek(beginAddrOfUntransQuote)
                    for i in range(0, 0x100):
                        #tmpChar = copySpeechInfoFile.read(1)
                        tmpChar = self.myFileBuffRead(wholeCopySpeechInfoFile, beginAddrOfUntransQuote+i, 1)
                        if tmpChar == "":
                            endOfFileReached = True
                            break
                        newChar = unpack('B', tmpChar)
                        if chr(newChar[0]) <> '\x00':
                            newUntransQuotelength += 1
                            quoteUntransCharList.append(chr(newChar[0]))
                        else:
                            break
                    #
                    # the original foreign quote is in the same position in the original file (DEFINITELY)):
                    beginAddrOfUntransQuoteOrig = beginAddrOfUntransQuote
                    #origSpeechInfoFile.seek(beginAddrOfUntransQuoteOrig)
                    for i in range(0, 0x100):
                        #tmpChar = origSpeechInfoFile.read(1)
                        tmpChar = self.myFileBuffRead(wholeOrigSpeechInfoFile, beginAddrOfUntransQuoteOrig+i, 1)
                        if tmpChar == "":
                            endOfOrigFileReached = True
                            break
                        newChar = unpack('B', tmpChar)
                        if chr(newChar[0]) <> '\x00':
                            origNewUntransQuotelength += 1
                            origQuoteUntransCharList.append(chr(newChar[0]))
                        else:
                            break

                # TODO: while writing we should be careful to pad with '0x20' if a translated quote is smaller than the previous (original) one of the target language we are replacing.
                if endOfFileReached == False:
                    newUntransQuoteString = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteUntransCharList, pGrabberForTranslationDicts)
                    newQuoteStringThroughGUIPresentFilter = self.makeStringInReadableExtAsciiCharlistToBeListed(origQuoteUntransCharList, pGrabberForTranslationDicts)
                    #if newQuotelength == 0 or newUntransQuotelength == 0:
    #               # DEBUG
#                    print "Line: %d. Translating: %s length: %d" % (currentline, newQuoteString, newQuotelength)
#                    print "Translated to: %s length: %d" %  (newUntransQuoteString, newUntransQuotelength)
                    listOfEnglishLinesSpeechInfo.append((beginAddrOfEnglishQuote,newQuoteString,newQuotelength))
                    listOfUntranslatedLinesSpeechInfo.append((beginAddrOfUntransQuote,newUntransQuoteString,newUntransQuotelength))
                    listOfForeignLinesOrigSpeechInfo.append((newQuoteStringThroughGUIPresentFilter,origNewUntransQuotelength)) # new for detecting changed lines and for merging function

    #                print specialCharQuoteList
    #                print quoteUntransCharList

                    if newQuotelength == 0:
                        countOfZeroLengthOrigQuotes += 1
                    if newUntransQuotelength == 0:
                        countOfZeroLengthTransQuotes += 1
                currentline += 1
            #end of while loop
            #copySpeechInfoFile.close()
            #origSpeechInfoFile.close()
    #               # DEBUG
    #        print "Total original quotes of zero length: %d" % countOfZeroLengthOrigQuotes
    #        print "Total translated quotes of zero length: %d" % countOfZeroLengthTransQuotes
    #        print listOfUntranslatedLinesSpeechInfo
            #debug
            #print("orig foreign quote found: %d" % (len(listOfForeignLinesOrigSpeechInfo)))
            return (listOfEnglishLinesSpeechInfo, listOfUntranslatedLinesSpeechInfo)
##########################################################################
        # this case is for MI2:SE (monkey island 2, selGameId ==2)
        elif (sFilename == filenameFrSpeechInfo or sFilename == filenameFrUIText)  and self.selGameID==2:
            # for MI2:SE we need to find also the fr. files
            # 1. check for the fr. files if given the speech.info, or the speech.info if given the fr.
            # 2. Load the fr. file in the column, check in parallel if there are quotes in the fr. file not present in the speech.info or vice versa
            # 3. create and save session, create copies as with the previous cases!
            # or better: always open the speech.info but in the end, update the fr.speech (copy). Also, check for quote inconsistencies, missing or not identical!
            # also, check sessioning
            global listOfLabelsSpeechInfo
            global listOfEnglishLinesSpeechInfoOrig
            global listOfLabelsSpeechInfoOrig
            self.loadASession(pSessionName = None, pOriginalfullPathsFilename = fullPathsFilename)
            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()

            del listOfEnglishLinesSpeechInfo[:]
            del listOfForeignLinesOrigSpeechInfo[:]
            del listOfUntranslatedLinesSpeechInfo[:]
            del listOfLabelsSpeechInfo[:]
            del listOfEnglishLinesSpeechInfoOrig[:]
            del listOfLabelsSpeechInfoOrig[:]

            endOfFileReached = False
            endOfOrigFileReached = False
            countOfZeroLengthOrigQuotes = 0
            countOfZeroLengthTransQuotes = 0
            currentline = 1
            labelCharList = []
            quoteCharList = []
            quoteUntransCharList = []
            origQuoteUntransCharList= []

            proceedToLoad = False
            # check if all 3 files exist in the same path
            # for now, check only for fr!!
            enUITextInfoFullExpectedPath = os.path.join( pathTosFile ,  filenameEnUIText)
            criticalCommonMsg = " file not found. "
            if not os.access(fullPathsFilename, os.F_OK):
                reply = QtGui.QMessageBox.critical(self, "Information message", sFilename + criticalCommonMsg)
            elif(sFilename == filenameFrUIText and not os.access(enUITextInfoFullExpectedPath, os.F_OK)):
                reply = QtGui.QMessageBox.critical(self, "Information message", filenameEnUIText + criticalCommonMsg + "Please place the "+filenameEnUIText+" file in the same directory with " +filenameFrUIText)
            else:
                proceedToLoad = True

            if proceedToLoad == True:
                # we mainly work with the copy as "original" since translation and original text are both there
                # but we do use the ORIGINAL quotes file to get the addresses and lengths for the original english labels and texts to be used in the save process.
                wholeOrigFrSpeechInfoFile = None
                wholeCopyFrSpeechInfoFile = None
                wholeEnUiTextInfoFile = None
                origFrSpeechInfoFile = open(fullPathsFilename, 'rb')
                wholeOrigFrSpeechInfoFile = origFrSpeechInfoFile.read()
                origFrSpeechInfoFile.close()
                copyFrSpeechInfoFile = open(fullcopyFileName, 'rb')
                wholeCopyFrSpeechInfoFile = copyFrSpeechInfoFile.read()
                copyFrSpeechInfoFile.close()

                enUiTextInfoFile = None
                if sFilename == filenameFrUIText:
                    enUiTextInfoFile = open(enUITextInfoFullExpectedPath, 'rb')
                    wholeEnUiTextInfoFile = enUiTextInfoFile.read()
                    enUiTextInfoFile.close()

                # read from hex addr: 0x04. there is an matrix of indexes to the start addresses of the quotes.
                # The indexes index the english label, english text and french (local) text (little endian -reverse order in bytes)
                # Each entry is 8 words (8x4 bytes) with 2x4 bytes as a quote id, 3x4 bytes to ignore (probably color, character, order in sentence)
                # and 1x4 for offset (added to its own addr) for english label. So the first one begins after 4 + (8  + 12) bytes
                # and 1x4 for offset of the english text
                # and 1x4 for offset of the frnch text
                # Each word points to the address that is the sum of its value and its own start address
                #matrixOfIndexesForQuotes = [] # a list with entries lists of  3 pointers integers (indexes)
                beginAddrOfIndexMatrix = 0x4
                ################################################
                # Main work. For the copy file
                # TODO: This largely duplicates code from above!! to make into method?!
                #
                endOfFileReached = False
                endOfOrigFileReached = False
                bgAddr = 0
                if sFilename == filenameFrSpeechInfo:
                    bgAddr = beginAddrOfIndexMatrix + 8 +12
                else:
                    bgAddr = beginAddrOfIndexMatrix
                # the first index's own address is 4 + (8  + 12). So you add this to its value to find the absolute address of the 1rst quote (label)
                # and also subtract 0x4 from it to get the start of the index table.
                # so you are left with a value to divide by 0x20, which is the length of the index blocks, to find the number of entries.
                numofEntries = 0
                tmpWord = self.myFileBuffRead(wholeCopyFrSpeechInfoFile, bgAddr, 4)
                if tmpWord == "":
                    endOfFileReached = True
                else:
                    numofEntriesUnpacked = unpack('<L', tmpWord)
                    numofEntries = numofEntriesUnpacked[0]
                    if sFilename == filenameFrSpeechInfo:
                        numofEntries = (numofEntries + beginAddrOfIndexMatrix + 8 + 12 - beginAddrOfIndexMatrix)/ 0x20
                    else:
                        numofEntries = (numofEntries + beginAddrOfIndexMatrix - beginAddrOfIndexMatrix)/ 0x8
                    #debug
                    #print "number Of entries %d" % numofEntries

                if endOfFileReached == False:
                    # find the english quotes
                    ndx = 0
                    detectedQuoteEntries = 0
                    tmpListForLblQuotesAddrs = []
                    del tmpListForLblQuotesAddrs[:]
                    tmpListForEnQuotesAddrs = []
                    del tmpListForEnQuotesAddrs[:]
                    tmpListForFrQuotesAddrs = []
                    del tmpListForFrQuotesAddrs[:]
                    tmpListForOrigForeignQuotesAddrs = []
                    del tmpListForOrigForeignQuotesAddrs[:]

                    while detectedQuoteEntries < numofEntries and endOfFileReached == False:
                        readNdx = -1
                        startOfNewMatrixEnrty = 0
                        startOfNewEnglishLabelIndex = 0
                        startOfNewEnglishQuoteIndex = 0
                        startOfNewFrenchQuoteIndex = 0
                        if sFilename == filenameFrSpeechInfo:
                            startOfNewMatrixEnrty = beginAddrOfIndexMatrix + detectedQuoteEntries * 0x20
                            startOfNewEnglishLabelIndex = startOfNewMatrixEnrty + 8 +12
                            startOfNewEnglishQuoteIndex = startOfNewEnglishLabelIndex + 4
                            startOfNewFrenchQuoteIndex = startOfNewEnglishQuoteIndex + 4
                        else:
                            startOfNewMatrixEnrty = beginAddrOfIndexMatrix + detectedQuoteEntries * 0x8
                            startOfNewEnglishLabelIndex = startOfNewMatrixEnrty
                            startOfNewEnglishQuoteIndex = startOfNewEnglishLabelIndex + 4 # which is actually the french quote for uitext
                        #
                        # startOf english label index
                        #
                        #copyFrSpeechInfoFile.seek(startOfNewEnglishLabelIndex)
                        #tmpWordLbl = copyFrSpeechInfoFile.read(4)
                        tmpWordLbl = self.myFileBuffRead(wholeCopyFrSpeechInfoFile, startOfNewEnglishLabelIndex, 4)
                        if tmpWordLbl == "":
                            endOfFileReached = True
                            break
                        else:
                            readNdxEntryLbl = unpack('<L', tmpWordLbl)
                            readNdxLbl = readNdxEntryLbl[0]
                            quoteStartAddrLbl = readNdxLbl + startOfNewEnglishLabelIndex
                            if readNdxLbl <> 0:
                                tmpListForLblQuotesAddrs.append(quoteStartAddrLbl)
                                # read for the address of the english quote (for speech.info)
                                #   or for the translated quote (for uitext)
                                #tmpWord = copyFrSpeechInfoFile.read(4)
                                tmpWord = self.myFileBuffRead(wholeCopyFrSpeechInfoFile, startOfNewEnglishLabelIndex+4, 4)
                                if tmpWord == "":
                                    endOfFileReached = True
                                    break
                                else:
                                    readNdxEntry = unpack('<L', tmpWord)
                                    readNdx = readNdxEntry[0]
                                    quoteStartAddrEn = readNdx + startOfNewEnglishQuoteIndex
                                    if readNdx <> 0:
                                        if sFilename == filenameFrSpeechInfo:
                                            tmpListForEnQuotesAddrs.append(quoteStartAddrEn)
                                        else:
                                            tmpListForFrQuotesAddrs.append(quoteStartAddrEn)
                                        # only for speech info we read the next pointer. In uitext there is no other pointer
                                        if sFilename == filenameFrSpeechInfo:
                                             # read for the address of the foreign quote
                                            #tmpWordFr = copyFrSpeechInfoFile.read(4)
                                            tmpWordFr = self.myFileBuffRead(wholeCopyFrSpeechInfoFile, startOfNewEnglishLabelIndex+4+4, 4)
                                            if tmpWordFr == "":
                                                endOfFileReached = True
                                                break
                                            else:
                                                readNdxEntryFr = unpack('<L', tmpWordFr)
                                                readNdxFr = readNdxEntryFr[0]
                                                quoteStartAddrFr = readNdxFr + startOfNewFrenchQuoteIndex
                                                if readNdxFr <> 0:
                                                    tmpListForFrQuotesAddrs.append(quoteStartAddrFr)
                                                elif readNdxFr == 0:
                                                    endOfFileReached = True
                                                    break
                                detectedQuoteEntries += 1
                            elif readNdx == 0:
                                endOfFileReached = True
                                break
                        #
                        # repeating the above almost similarily to retrieve the FOREIGN quotes from the original file
                        # TODO: could be made as function
                        #
                        startOfFrenchQuote = 0
                        if sFilename == filenameFrSpeechInfo:
                            startOfFrenchQuote= startOfNewFrenchQuoteIndex

                        else:
                            startOfFrenchQuote = startOfNewEnglishQuoteIndex # which is actually the french quote for uitext
                        #origFrSpeechInfoFile.seek(startOfFrenchQuote)
                        #tmpWordLbl = origFrSpeechInfoFile.read(4)
                        tmpWordLbl = self.myFileBuffRead(wholeOrigFrSpeechInfoFile, startOfFrenchQuote, 4)
                        if tmpWordLbl == "":
                            endOfOrigFileReached = True
                            break
                        else:
                            readNdxEntryLbl = unpack('<L', tmpWordLbl)
                            readNdxLbl = readNdxEntryLbl[0]
                            quoteStartAddrLbl = readNdxLbl + startOfFrenchQuote
                            if readNdxLbl <> 0:
                                tmpListForOrigForeignQuotesAddrs.append(quoteStartAddrLbl)
                            elif readNdx == 0:
                                endOfOrigFileReached = True
                                break
                    #debug
                    #print "Total Entries found %d" % detectedQuoteEntries
                    #
                    # For the uiText info case, we open the en. file and get the english text pointer, which we suppose to be in the same order (otherwise we need label matching!)
                    #
                    if sFilename == filenameFrUIText:
                        ndx = 0
                        tmpListForEnQuotesAddrs = []
                        del tmpListForEnQuotesAddrs[:]
                        detectedOrigQuoteEntries = 0
                        endOfFileReached = False
                        while detectedOrigQuoteEntries < numofEntries and endOfFileReached == False:
                            readNdx = -1
                            startOfNewMatrixEnrty = beginAddrOfIndexMatrix + detectedOrigQuoteEntries * 0x8
                            startOfNewEnglishQuoteIndex = startOfNewMatrixEnrty + 4 # which is actually the french quote for uitext

                            # startOf english quote index
                            #enUiTextInfoFile.seek(startOfNewEnglishQuoteIndex)
                            #tmpWordQt = enUiTextInfoFile.read(4)
                            tmpWordQt = self.myFileBuffRead(wholeEnUiTextInfoFile, startOfNewEnglishQuoteIndex, 4)
                            if tmpWordQt == "":
                                endOfFileReached = True
                                break
                            else:
                                readNdxEntryQt = unpack('<L', tmpWordQt)
                                readNdxQt = readNdxEntryQt[0]
                                quoteStartAddrQt = readNdxQt + startOfNewEnglishQuoteIndex
                                if readNdxQt <> 0:
                                    tmpListForEnQuotesAddrs.append(quoteStartAddrQt)
                                    detectedOrigQuoteEntries += 1
                                elif readNdxQt == 0:
                                    endOfFileReached = True
                                    break

                    #
                    # we continue to parse the actual quotes and labels
                    #
                    ndx = 0
                    for ndx in range (0, detectedQuoteEntries):
                        newLabellength = 0
                        newQuotelength = 0
                        newUntransQuotelength = 0
                        origNewUntransQuotelength = 0
                        newLabelString = ""
                        newQuoteString = ""
                        newQuoteStringThroughGUIPresentFilter = ""
                        newUntransQuoteString = ""
                        beginAddrOfEnglishQuote = 0
                        beginAddrOfUntransQuote = 0
                        beginAddrOfOrigUntransQuote = 0

                        del labelCharList[:]
                        del quoteCharList[:]
                        del quoteUntransCharList[:]
                        del origQuoteUntransCharList[:]

                        beginAddrOfLabel = tmpListForLblQuotesAddrs[ndx]
                        #copyFrSpeechInfoFile.seek(beginAddrOfLabel)
                        it00 = 0
                        while True:
                            #tmpChar = copyFrSpeechInfoFile.read(1)
                            tmpChar = self.myFileBuffRead(wholeCopyFrSpeechInfoFile, beginAddrOfLabel+it00, 1)
                            it00 +=1
                            if tmpChar == "":
                                endOfFileReached = True
                                break
                            newChar = unpack('B', tmpChar)
                            if chr(newChar[0]) <> '\x00':
                                newLabellength += 1
                #                print newChar[0]
                                labelCharList.append(chr(newChar[0]))
                            else:
                                break

                        if endOfFileReached == False:
                            newLabelString = self.makeOriginalStringWithEscapeSequences(labelCharList)
                            labelLengthWithNullTerm = newLabellength + 1
                            #copyFrSpeechInfoFile.seek(beginAddrOfLabel)
                            #origLabelRaw = copyFrSpeechInfoFile.read(labelLengthWithNullTerm)
                            origLabelRaw = self.myFileBuffRead(wholeCopyFrSpeechInfoFile, beginAddrOfLabel, labelLengthWithNullTerm)

                            beginAddrOfEnglishQuote = tmpListForEnQuotesAddrs[ndx]
                            if sFilename == filenameFrSpeechInfo:
                                #copyFrSpeechInfoFile.seek(beginAddrOfEnglishQuote)
                                pass
                            else:
                                #enUiTextInfoFile.seek(beginAddrOfEnglishQuote)
                                pass

                            it01 = 0
                            while True:
                                tmpChar = '\x00'
                                if sFilename == filenameFrSpeechInfo:
                                    #tmpChar = copyFrSpeechInfoFile.read(1)
                                    tmpChar = self.myFileBuffRead(wholeCopyFrSpeechInfoFile, beginAddrOfEnglishQuote+it01, 1)
                                    it01 +=1
                                else:
                                    #tmpChar = enUiTextInfoFile.read(1)
                                    tmpChar = self.myFileBuffRead(wholeEnUiTextInfoFile, beginAddrOfEnglishQuote+it01, 1)
                                    it01 +=1
                                if tmpChar == "":
                                    endOfFileReached = True
                                    break
                                newChar = unpack('B', tmpChar)
                                if chr(newChar[0]) <> '\x00':
                                    newQuotelength += 1
                    #                print newChar[0]
                                    quoteCharList.append(chr(newChar[0]))
                                else:
                                    break

                            if endOfFileReached == False:
    #                            print quoteCharList
                                newQuoteString = self.makeOriginalStringWithEscapeSequences(quoteCharList)
                                origQuoteLengthWithNullTerm = newQuotelength + 1
                                origQuoteRaw = None
                                if sFilename == filenameFrSpeechInfo:
                                    #copyFrSpeechInfoFile.seek(beginAddrOfEnglishQuote)
                                    #origQuoteRaw = copyFrSpeechInfoFile.read(origQuoteLengthWithNullTerm)
                                    origQuoteRaw = self.myFileBuffRead(wholeCopyFrSpeechInfoFile, beginAddrOfEnglishQuote, origQuoteLengthWithNullTerm)
                                else:
                                    #enUiTextInfoFile.seek(beginAddrOfEnglishQuote)
                                    #origQuoteRaw = enUiTextInfoFile.read(origQuoteLengthWithNullTerm)
                                    origQuoteRaw = self.myFileBuffRead(wholeEnUiTextInfoFile, beginAddrOfEnglishQuote, origQuoteLengthWithNullTerm)


                                # read the untranslated quote bytes of the french/foreign language of the speech.info file.
                                # the begin addr is calcualted similarly for both uiText and Speech.info
                                beginAddrOfUntransQuote = tmpListForFrQuotesAddrs[ndx]
                                #copyFrSpeechInfoFile.seek(beginAddrOfUntransQuote)
                                it02 = 0
                                while True:
                                    #tmpChar = copyFrSpeechInfoFile.read(1)
                                    tmpChar = self.myFileBuffRead(wholeCopyFrSpeechInfoFile, beginAddrOfUntransQuote+it02, 1)
                                    it02 +=1
                                    if tmpChar == "":
                                        endOfFileReached = True
                                        break
                                    newChar = unpack('B', tmpChar)
                                    if chr(newChar[0]) <> '\x00':
                                        newUntransQuotelength += 1
                                        quoteUntransCharList.append(chr(newChar[0]))
                                    else:
                                        break
                                if endOfFileReached == False:
        ##                            print quoteUntransCharList
                                    newUntransQuoteString = self.makeStringInReadableExtAsciiCharlistToBeListed(quoteUntransCharList, pGrabberForTranslationDicts)
                                #
                                # repeat for original foreign quote
                                beginAddrOfOrigUntransQuote = tmpListForOrigForeignQuotesAddrs[ndx]
                                #origFrSpeechInfoFile.seek(beginAddrOfOrigUntransQuote)
                                it02 = 0
                                while True:
                                    #tmpChar = origFrSpeechInfoFile.read(1)
                                    tmpChar = self.myFileBuffRead(wholeOrigFrSpeechInfoFile, beginAddrOfOrigUntransQuote+it02, 1)
                                    it02 +=1
                                    if tmpChar == "":
                                        endOfOrigFileReached = True
                                        break
                                    newChar = unpack('B', tmpChar)
                                    if chr(newChar[0]) <> '\x00':
                                        origNewUntransQuotelength += 1
                                        origQuoteUntransCharList.append(chr(newChar[0]))
                                    else:
                                        break
                                if endOfOrigFileReached == False:
                                    newQuoteStringThroughGUIPresentFilter = self.makeStringInReadableExtAsciiCharlistToBeListed(origQuoteUntransCharList, pGrabberForTranslationDicts)
            #               # DEBUG
            #                print "Translating: %s length: %d" % (newQuoteString, newQuotelength)
            #                print "Translated to: %s length: %d" %  (newUntransQuoteString, newUntransQuotelength)
                            listOfEnglishLinesSpeechInfo.append((beginAddrOfEnglishQuote,newQuoteString,newQuotelength))
                            listOfForeignLinesOrigSpeechInfo.append((newQuoteStringThroughGUIPresentFilter,origNewUntransQuotelength)) # new for detecting changed lines and for merging function
                            listOfUntranslatedLinesSpeechInfo.append((beginAddrOfUntransQuote,newUntransQuoteString,newUntransQuotelength))
                            listOfLabelsSpeechInfo.append((beginAddrOfLabel,newLabelString,newLabellength))
                            listOfLabelsSpeechInfoOrig.append(origLabelRaw)
                            listOfEnglishLinesSpeechInfoOrig.append(origQuoteRaw)

                            if newQuotelength == 0:
                                countOfZeroLengthOrigQuotes += 1
                            if newUntransQuotelength == 0:
                                countOfZeroLengthTransQuotes += 1
                    #end  for loop: for ndx in range (0, detectedQuoteEntries)
        #        print "ECHO ECHO ECHO"
        #        print listOfAllLinesHintsCSV
        #        print "ECHO ECHO ECHO"
        #        transSpeechInfoFile.close()
##                origFrSpeechInfoFile.close()
                #if sFilename == filenameFrUIText:
                #    enUiTextInfoFile.close()
                #copyFrSpeechInfoFile.close()
                #origFrSpeechInfoFile.close()

##                #
##                # DEBUG DEBUG. OPEN SPEECH.INFO and compare for missing quotes and different quotes
##                #
##                del listOfUntranslatedLinesSpeechInfo[:]
##                origSpeechInfoFile = open(speechInfoFileName, 'rb')
##
##                currentline = 1
##                quoteCharList = []
##
##                endOfFileReached = False
##                countOfZeroLengthOrigQuotes = 0
##                # read the english quote bytes after the header (which is 0x10 bytes).
##                while endOfFileReached == False:
##                    newQuotelength = 0
##                    newQuoteString = ""
##                    beginAddrOfEnglishQuote = 0
##                    del quoteCharList[:]
##
##                    beginAddrOfEnglishQuote = 0
##                    beginAddrOfEnglishQuote = 0x10 * currentline + (currentline-1)* (plithosOfDifferentLanguages * 0x100 + 0x20) # 0x20 are the two last 0x20 byte chunk that show which character speaks a line.
##                    origSpeechInfoFile.seek(beginAddrOfEnglishQuote)
##                    for i in range(0, 0x100):
##                        tmpChar = origSpeechInfoFile.read(1)
##                        if tmpChar == "":
##                            endOfFileReached = True
##                            break
##                        newChar = unpack('B', tmpChar)
##                        if chr(newChar[0]) <> '\x00':
##                            newQuotelength += 1
##                            quoteCharList.append(chr(newChar[0]))
##                        else:
##                            break
##
##                    # TODO: while writing we should be careful to pad with '0x20' if a translated quote is smaller than the previous (original) one of the target language we are replacing.
##                    if endOfFileReached == False:
##                        newQuoteString = self.makeOriginalStringWithEscapeSequences(quoteCharList)
##                        listOfUntranslatedLinesSpeechInfo.append((beginAddrOfEnglishQuote,newQuoteString,newQuotelength))
##
##                        if newQuotelength == 0:
##                            countOfZeroLengthOrigQuotes += 1
##                    currentline += 1
##                #end of while loop
##                origSpeechInfoFile.close()
##
##                #
##                # END OF DEBUG DEBUG. OPEN SPEECH.INFO and compare for missing quotes and different quotes
##                #
            #debug
            #print("orig foreign quote found: %d" % (len(listOfForeignLinesOrigSpeechInfo)))
            return (listOfEnglishLinesSpeechInfo, listOfUntranslatedLinesSpeechInfo)
        #
        # SPEECH.INFO, EN.SPEECH.INFO FOR MI2:SE
        #
        elif (sFilename == filenameEnSpeechInfo or sFilename == filenameSpeechInfo) and self.selGameID==2:
            reply = QtGui.QMessageBox.information(self, "Info message", "For the dialogue quotes of MI2:SE please open the %s file." % (filenameFrSpeechInfo))
            pass
            return (None, None)
        #
        # UI.TEXT FOR MI2:SE
        #
        elif (sFilename == filenameEnUIText  and self.selGameID==2):
            self.loadASession(pSessionName = None, pOriginalfullPathsFilename = fullPathsFilename)
            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()
            reply = QtGui.QMessageBox.information(self, "Info message", "For the ui text of MI2:SE please open the %s file." % (filenameFrUIText))
            pass
            return (None, None)
##        elif sFilename in filenameCreditsListMISE2 and self.selGameID==2:
##            self.loadASession(pSessionName = None, pOriginalfullPathsFilename = fullPathsFilename)
##            fullcopyFileName = self.ui.openTranslatedFileNameTxtBx.text().strip()
##            reply = QtGui.QMessageBox.information(self, "Info message", "Editing of "+sFilename+" credits file is not yet supported for MI2:SE!")
##            pass
##            return (None, None)
        else:
            reply = QtGui.QMessageBox.information(self, "Info message", "Unsupported file.")
            pass
            return (None, None)
####################################################################
##class MyTableModel(QAbstractItemModel ):
##    def __init__(self, datain, parent=None, *args):
##        """ datain: a list where each item is a row
##        """
##        QAbstractItemModel.__init__(self, parent, *args)
##        self.listdata = datain
##
##    def rowCount(self, parent=QModelIndex()):
##        return len(self.listdata)
##
##    def data(self, index, role):
##        if index.isValid() and role == Qt.DisplayRole:
##            return QVariant(self.listdata[index.row()])
##        else:
##            return QVariant()
    # return "" if end of file
    def myFileBuffRead(self, mybuff, startNdx=0, readLength=0):
        retVal = None
        if (startNdx >= len(mybuff)) or  ((startNdx + readLength) > len(mybuff)) or (readLength <=0):
            retVal = ""
        try:
            retVal = mybuff[startNdx:(startNdx+readLength)]
        except:
            retVal = ""
        return retVal

    # should return a buffer, scummV5-decoded  (xor-ed with 0x69 in every byte)
    def scummDecodeIndexFile(self, wholeDataClassicEnM2Giv, startAddrOfM2Classic=0, readLength=0):
        scummDecodeBuffToRet = []
        del scummDecodeBuffToRet[:]
        readInBuffOrig = self.myFileBuffRead(wholeDataClassicEnM2Giv, startAddrOfM2Classic, readLength)
        if not (readInBuffOrig is None or readInBuffOrig == ""):
            for i in range (0, readLength):
                datumUnpacked = unpack('<B', readInBuffOrig[i])  # read byte-byte
                datumHex = datumUnpacked[0]
                datumHexUnCode = datumHex ^ 0x69
                scummDecodeBuffToRet.append(pack('B', datumHexUnCode))
            ## DEBUG 4.7
            #print "length of decoded is {0}".format(len(scummDecodeBuffToRet))
            return scummDecodeBuffToRet
        else:
            return scummDecodeBuffToRet

    # should return a buffer, scummV5-encoded  (xor-ed with 0x69 in every byte) (TODO could also be done in place, by ref)!!
    def scummEncodeIndexFile(self, decodedBuffer):
        scummEncodeBuffToRet = []
        del scummEncodeBuffToRet[:]
        if not (decodedBuffer is None or decodedBuffer == ""):
            for i in range (0, len(decodedBuffer)):
                datumUnpacked = unpack('B', decodedBuffer[i])  # read byte-byte
                datumHex = datumUnpacked[0]
                datumHexUnCode = datumHex ^ 0x69
                scummEncodeBuffToRet.append(pack('B', datumHexUnCode))
            ## DEBUG 4.7
            #print "length of encoded is {0}".format(len(scummEncodeBuffToRet))
            return scummEncodeBuffToRet
        else:
            return scummEncodeBuffToRet


    # myFileBuffWrite()
    def myFileBuffWriteWord(self, mybuff, startNdx=0, wordPackedLongLE=[]):
        wordLength = 4
        retVal = None
        if (startNdx >= len(mybuff)) or  ((startNdx + wordLength) > len(mybuff)) :
            retVal = 0
        try:
            for iiTmp in range(startNdx, (startNdx+wordLength)):
                mybuff[iiTmp] = wordPackedLongLE[iiTmp - startNdx]
            retVal = wordLength;
        except:
            retVal = -1
        return retVal

    def myFileBuffWriteShort(self, mybuff, startNdx=0, wordPackedShortLE=[]):
        wordLength = 2
        retVal = None
        if (startNdx >= len(mybuff)) or  ((startNdx + wordLength) > len(mybuff)) :
            retVal = 0
        try:
            for iiTmp in range(startNdx, (startNdx+wordLength)):
                mybuff[iiTmp] = wordPackedShortLE[iiTmp - startNdx]
            retVal = wordLength;
        except:
            retVal = -1
        return retVal

    def parseDecodedFileBuffer(self, wholeDataClassicEnM2GivDecoded_SCRIPT=[], filename=''):
        retval = []
        unknownCommands = 0
        unlessEqCommands = 0
        otherCommands = 0
        endScriptCommands = 0
        if filename == 'SCRP_0063':
            startofCommands = 8
            opCodeCursor = startofCommands
            while opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT) :
                ##print "opCodeCursor {0}".format(opCodeCursor)
                #parse command starting from cursor
                #decode first byte
                datumUnpacked = unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[opCodeCursor])
                datumHex = datumUnpacked[0]
                if datumHex == 0xDD: #class-of local var
                    tmpStrCursor = 1
                    while tmpStrCursor + opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT):
                        if  unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[tmpStrCursor + opCodeCursor])[0] == 0xFF:
                            tmpStrCursor +=1
                            break
                        else:
                            tmpStrCursor +=1
                    opCodeCursor += tmpStrCursor
                    otherCommands +=1
                elif datumHex == 0xA0: #end of script
                    opCodeCursor += 1
                    endScriptCommands +=1
                elif datumHex == 0x48: #unless equals # we could use the jump operands to just get these, but we go the more verbose route
                    tmpShortOperand = []
                    tmpShortOperand = wholeDataClassicEnM2GivDecoded_SCRIPT[(opCodeCursor+3): (opCodeCursor+5)]
                    #print len(tmpShortOperand)
                    #print unpack('<B',tmpShortOperand[0])[0]
                    #print unpack('<B',tmpShortOperand[1])[0]
#                    U = array.array("H")
#                    U.fromstring(tmpShortOperand)
                    datumUnpacked = unpack('<H', ''.join(tmpShortOperand) )
                    #print (datumUnpacked[0], opCodeCursor+3 )
                    retval.append( (datumUnpacked[0], opCodeCursor+3 ) )
                    opCodeCursor += 7
                    unlessEqCommands +=1
                elif datumHex == 0xD4: #new name of local var
                    tmpStrCursor = 2
                    while tmpStrCursor + opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT):
                        if  unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[tmpStrCursor + opCodeCursor])[0] == 0x00:
                            tmpStrCursor +=1
                            break
                        else:
                            tmpStrCursor +=1
                    opCodeCursor += tmpStrCursor
                    otherCommands +=1
                elif datumHex == 0x18: #relative jump
                    opCodeCursor += 3
                    otherCommands +=1
                elif datumHex == 0x1A: # move var
                    opCodeCursor += 5
                    otherCommands +=1
                else:
                    print "unknown command %02X" % (datumHex, )
                    unknownCommands +=1
                    opCodeCursor += 1 # ???
        elif filename == 'SCRP_0064':
            startofCommands = 8
            opCodeCursor = startofCommands
            while opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT) :
                ##print "opCodeCursor {0}".format(opCodeCursor)
                #parse command starting from cursor
                #decode first byte
                datumUnpacked = unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[opCodeCursor])
                datumHex = datumUnpacked[0]
                if datumHex == 0xDD: #class-of local var
                    tmpStrCursor = 1
                    while tmpStrCursor + opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT):
                        if  unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[tmpStrCursor + opCodeCursor])[0] == 0xFF:
                            tmpStrCursor +=1
                            break
                        else:
                            tmpStrCursor +=1
                    opCodeCursor += tmpStrCursor
                    otherCommands +=1
                elif datumHex == 0xA0: #end of script
                    opCodeCursor += 1
                    endScriptCommands +=1
                elif datumHex == 0x48: #unless equals # we could use the jump operands to just get these, but we go the more verbose route
                    tmpShortOperand = []
                    tmpShortOperand = wholeDataClassicEnM2GivDecoded_SCRIPT[(opCodeCursor+3): (opCodeCursor+5)]
                    #print len(tmpShortOperand)
                    #print unpack('<B',tmpShortOperand[0])[0]
                    #print unpack('<B',tmpShortOperand[1])[0]
#                    U = array.array("H")
#                    U.fromstring(tmpShortOperand)
                    datumUnpacked = unpack('<H', ''.join(tmpShortOperand) )
                    #print (datumUnpacked[0], opCodeCursor+3 )
                    retval.append( (datumUnpacked[0], opCodeCursor+3 ) )
                    opCodeCursor += 7
                    unlessEqCommands +=1
                elif datumHex == 0xD4: #new name of local var
                    tmpStrCursor = 2
                    while tmpStrCursor + opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT):
                        if  unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[tmpStrCursor + opCodeCursor])[0] == 0x00:
                            tmpStrCursor +=1
                            break
                        else:
                            tmpStrCursor +=1
                    opCodeCursor += tmpStrCursor
                    otherCommands +=1
                elif datumHex == 0x18: #relative jump
                    opCodeCursor += 3
                    otherCommands +=1
                elif datumHex == 0x1A or datumHex == 0x28: # move var or "if bitvar =="
                    opCodeCursor += 5
                    otherCommands +=1
                elif datumHex == 0x40 or datumHex == 0x0A: # start cutscene or start-script
                    tmpStrCursor = 1
                    while tmpStrCursor + opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT):
                        if  unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[tmpStrCursor + opCodeCursor])[0] == 0xFF:
                            tmpStrCursor +=1
                            break
                        else:
                            tmpStrCursor +=1
                    opCodeCursor += tmpStrCursor
                    otherCommands +=1
                elif datumHex == 0xC0 or datumHex == 0xD8 or datumHex== 0x80: # end cutscene or say-line-default or breask-here
                    opCodeCursor += 1
                    otherCommands +=1
                elif datumHex == 0x58: # override on
                    opCodeCursor += 5
                    otherCommands +=1
                elif datumHex == 0xAE or datumHex == 0x62 or datumHex == 0x14: # wait for message or stop-script or print-line
                    opCodeCursor += 2
                    otherCommands +=1
                elif datumHex == 0x68: # f-script-running
                    opCodeCursor += 4
                    otherCommands +=1

                elif datumHex == 0x0F: # print string (null terminated)
                    # special case to skip because it uses formatted string with vars:
                    if opCodeCursor == 1909:
                        opCodeCursor = 1957
                        otherCommands +=1
                    else:
                        tmpStrCursor = 1
                        while tmpStrCursor + opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT):
                            if  unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[tmpStrCursor + opCodeCursor])[0] == 0x00:
                                tmpStrCursor +=1
                                break
                            else:
                                tmpStrCursor +=1
                        opCodeCursor += tmpStrCursor
                        otherCommands +=1
                else:
                    if opCodeCursor == 1828:
                        # skip intermediate block with expressions (not need to bother parsing command-by-command)
                        opCodeCursor = 1908
                        otherCommands +=35
                    else:
                        print "unknown command %02X" % (datumHex, )
                        unknownCommands +=1
                        opCodeCursor += 1 # ???
        elif  filename == 'LSCR_0207':
            startofCommands = 9
            opCodeCursor = startofCommands
            while opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT) :
                ##print "opCodeCursor {0}".format(opCodeCursor)
                #parse command starting from cursor
                #decode first byte
                datumUnpacked = unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[opCodeCursor])
                datumHex = datumUnpacked[0]
                if datumHex == 0x48: #unless equals # we could use the jump operands to just get these, but we go the more verbose route
                    tmpShortOperand = []
                    tmpShortOperand = wholeDataClassicEnM2GivDecoded_SCRIPT[(opCodeCursor+3): (opCodeCursor+5)]
                    datumUnpacked = unpack('<H', ''.join(tmpShortOperand) )
                    #print (datumUnpacked[0], opCodeCursor+3 )
                    retval.append( (datumUnpacked[0], opCodeCursor+3 ) )
                    opCodeCursor += 7
                    unlessEqCommands +=1
                elif datumHex == 0x1A: # move var
                    opCodeCursor += 5
                    otherCommands +=1
                elif datumHex == 0x27: # string-assign-literal
                    tmpStrCursor = 3
                    while tmpStrCursor + opCodeCursor < len(wholeDataClassicEnM2GivDecoded_SCRIPT):
                        if  unpack('B', wholeDataClassicEnM2GivDecoded_SCRIPT[tmpStrCursor + opCodeCursor])[0] == 0x00:
                            tmpStrCursor +=1
                            break
                        else:
                            tmpStrCursor +=1
                    opCodeCursor += tmpStrCursor
                    otherCommands +=1
                elif datumHex == 0xA0: #end of script
                    opCodeCursor += 1
                    endScriptCommands +=1
                elif datumHex == 0x18: #relative jump
                    opCodeCursor += 3
                    otherCommands +=1
                else:
                    print "unknown command %02X" % (datumHex, )
                    unknownCommands +=1
                    opCodeCursor += 1 # ???

        #endif

        #report
        ## DEBUG 4.7
        #print "File {0}. Total commands: {1}, Useful: {2}, Other: {3}, Unknown: {4}, End Script: {5}".format(filename, unknownCommands+unlessEqCommands+otherCommands+endScriptCommands, unlessEqCommands, otherCommands, unknownCommands, endScriptCommands)
        return retval

#
#
#
# ########################
# main
# #########################
#
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyMainWindow()
    sys.exit(app.exec_())


##if __name__ == "__main__":
##
###print this is a test
##    print "This is a test ######################################"
##    originalText = "The Sea Monkey"
##    translatedText = "το Sea Monkey"
##    localGrabInstance = grabberFromPNG('windows-1253', 1)
##    translatedTextAsCharsList = list(translatedText)
##    for itmp in range(0,len(translatedTextAsCharsList)):
##        if translatedTextAsCharsList[itmp] in localGrabInstance.replaceAsciiIndexWithValForTranslation:
##            tmpkey = translatedTextAsCharsList[itmp]
##            translatedTextAsCharsList[itmp] = pack('B', localGrabInstance.replaceAsciiIndexWithValForTranslation[tmpkey])
##        else:
##            translatedTextAsCharsList[itmp] = chr(ord(translatedTextAsCharsList[itmp]))
##    resultingTranslatedText = "".join(translatedTextAsCharsList)
##    if len(resultingTranslatedText) > 255:
##        print "Error: Cannot have more than 255 chars in translated sentence for uitext.info file"
##    else:
##        tmpOpenFile = open("tmpFileWithTrans", 'wb')
##        tmpOpenFile.write("".join(translatedTextAsCharsList))
##        tmpOpenFile.write('\x00')
##        tmpOpenFile.close()
##
##    print "Translating %s :" % originalText
##    print "Translated to %s: " %  translatedText
##    print translatedTextAsCharsList
##    print "This is a test ######################################"
##    originalText = "Cluuuck"
##    translatedText = "Κλααακ"
##    localGrabInstance = grabberFromPNG('windows-1253', 1)
##    translatedTextAsCharsList = list(translatedText)
##    for itmp in range(0,len(translatedTextAsCharsList)):
##        if translatedTextAsCharsList[itmp] in localGrabInstance.replaceAsciiIndexWithValForTranslation:
##            tmpkey = translatedTextAsCharsList[itmp]
##            translatedTextAsCharsList[itmp] = pack('B', localGrabInstance.replaceAsciiIndexWithValForTranslation[tmpkey])
##        else:
##            translatedTextAsCharsList[itmp] = chr(ord(translatedTextAsCharsList[itmp]))
##    resultingTranslatedText = "".join(translatedTextAsCharsList)
##    if len(resultingTranslatedText) > 255:
##        print "Error: Cannot have more than 255 chars in translated sentence for uitext.info file"
##    else:
##        tmpOpenFile = open("tmpFileWithTrans", 'wb')
##        tmpOpenFile.write("".join(translatedTextAsCharsList))
##        tmpOpenFile.write('\x00')
##        tmpOpenFile.close()
##
##    print "Translating %s :" % originalText
##    print "Translated to %s: " %  translatedText
##    print translatedTextAsCharsList
##    print "This is a test ######################################"
##    originalText = "ΚREEEEEEAK"
##    translatedText = "ΚΡΙΙΙΙΙΙΙΚ"
##    localGrabInstance = grabberFromPNG('windows-1253', 1)
##    translatedTextAsCharsList = list(translatedText)
##    for itmp in range(0,len(translatedTextAsCharsList)):
##        if translatedTextAsCharsList[itmp] in localGrabInstance.replaceAsciiIndexWithValForTranslation:
##            tmpkey = translatedTextAsCharsList[itmp]
##            translatedTextAsCharsList[itmp] = pack('B', localGrabInstance.replaceAsciiIndexWithValForTranslation[tmpkey])
##        else:
##            translatedTextAsCharsList[itmp] = chr(ord(translatedTextAsCharsList[itmp]))
##    resultingTranslatedText = "".join(translatedTextAsCharsList)
##    if len(resultingTranslatedText) > 255:
##        print "Error: Cannot have more than 255 chars in translated sentence for uitext.info file"
##    else:
##        tmpOpenFile = open("tmpFileWithTrans", 'wb')
##        tmpOpenFile.write("".join(translatedTextAsCharsList))
##        tmpOpenFile.write('\x00')
##        tmpOpenFile.close()
##
##    print "Translating %s :" % originalText
##    print "Translated to %s: " %  translatedText
##    print translatedTextAsCharsList
##    print "This is a test ######################################"
##    originalText = "Oh^ no more than \255\004\195\000 pieces of eight."
##    translatedText = "Ω^ όχι παραπάνω από ... κομμάτια των οχτώ."
##    localGrabInstance = grabberFromPNG('windows-1253', 1)
##    translatedTextAsCharsList = list(translatedText)
##    for itmp in range(0,len(translatedTextAsCharsList)):
##        if translatedTextAsCharsList[itmp] in localGrabInstance.replaceAsciiIndexWithValForTranslation:
##            tmpkey = translatedTextAsCharsList[itmp]
##            translatedTextAsCharsList[itmp] = pack('B', localGrabInstance.replaceAsciiIndexWithValForTranslation[tmpkey])
##        else:
##            translatedTextAsCharsList[itmp] = chr(ord(translatedTextAsCharsList[itmp]))
##    resultingTranslatedText = "".join(translatedTextAsCharsList)
##    if len(resultingTranslatedText) > 255:
##        print "Error: Cannot have more than 255 chars in translated sentence for uitext.info file"
##    else:
##        tmpOpenFile = open("tmpFileWithTrans", 'wb')
##        tmpOpenFile.write("".join(translatedTextAsCharsList))
##        tmpOpenFile.write('\x00')
##        tmpOpenFile.close()
##
##    print "Translating %s :" % originalText
##    print "Translated to %s: " %  translatedText
##    print translatedTextAsCharsList
##
###
### Repete :)))
###
##    originalText = "Music Volume"
##    translatedText = "Ένταση Μουσικής"
##    translatedTextAsCharsList2 = list(translatedText)
##    for itmp in range(0,len(translatedTextAsCharsList2)):
##        if translatedTextAsCharsList2[itmp] in replaceAsciiIndexWithValForTranslation:
##            tmpkey = translatedTextAsCharsList2[itmp]
##            translatedTextAsCharsList2[itmp] = pack('B', replaceAsciiIndexWithValForTranslation[tmpkey])
##        else:
##            translatedTextAsCharsList2[itmp] = chr(ord(translatedTextAsCharsList2[itmp]))
##    resultingTranslatedText = "".join(translatedTextAsCharsList2)
##    if len(resultingTranslatedText) > 256:
##        print "Error: Cannot have more than 255 chars in translated sentence for uitext.info file"
##    else:
##        tmpOpenFile = open("tmpFileWithTrans", 'wb')
##        tmpOpenFile.write("".join(translatedTextAsCharsList2))
##        tmpOpenFile.write('\x00')
##        tmpOpenFile.close()
##
##    print "Translating %s :" % originalText
##    print "Translated to %s: " %  translatedText
##    print translatedTextAsCharsList2
###    exit()
##
##    print "This ENDs the test ######################################"
##
##    parseQuoteFile(filenameSpeechInfo, 1)
##
###        except IOError:
###            pass
##else:
##	print 'Imported from another module'

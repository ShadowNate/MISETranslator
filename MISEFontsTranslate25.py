#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Created by Praetorian (ShadowNate) for Classic Adventures in Greek
# classic.adventures.in.greek@gmail.com
#

#
# TODO set tryEncoding ???<-- from langSettings? (no for now it's by overrideEncoding.txt (and settings, actually settings/lastActiveEncoding is more correct and can be used to retrieve the string of chars from the langSettings).
# TODO present somehow the string of letters in a new png image (as it would appear in a dialogue in-game, respecting the spacing/kerning/positioning settings.
#           greek pangram: Ξεσκεπάζω την ψυχοφθόρα βδελυγμία
#           english pangram: The quick brown fox jumps over the lazy dog
#           custom phraze (we need to check/preview spacing for punctuation marks, capital letters, special characters etc)
# TODO button for copy to game dir and keep backups checkbox should implement proper function
# TODO TEST IF THE CHANGES in the selected game WORK!
# TODO TEST check on consecutive MI1 sessions (the selected game combo box does not switch value, so the load game id is not called again. Is this a problem, or more efficient?)
# TODO Ability to replace the entire font file (english fonts too) to make a more consistent font.
#
## TODO when empty sessions.txt, we don't need an empty entry inserted in the combobox - WONTFIX. Let it be, we probably need the currentIndex to be 0 then anyway.
## DONE: game id SHOULD BE selected when a NEW session starts.
##        DONE: when a session is LOADED, then the right game ID must be selected (and a correct grabberInstance initialised!) :
## DONE: also, the number of valid letters should be configurable (it is different between languages) <-- numOfdetectCharsTxtBx gets its allowed values (and colors red the wrong) in recalculateProcessing, from len(self.myGrabInstance.orderAndListOfForeignLetters)
## DONE: Delete session works
## DONE: save session prompts for overwriting
## DONE check on delete of session. Should we call the "new session" code? :: NO
## DONE on new session : popup a dialogue to select game. ! Choice should be reflected in the combobox.
## DONE put a MISE2_ prefix to all sessions for MISE2. (to distinguise them visually)
## DONE fix: on switching the combo box values of sessions (auto-loads), when selecting the empty one you start a new session, but if you click Cancel (in the prompt for game id) then it remains in new session, with no new session restart!!!
## DONE fix bug with greek characters in file paths! or session name?!
## TODO save activeEncoding for each session
## DONE: if wrong parameters are set for top to top and left to left the prog crashes (many characters detected etc..)
## DONE: font builder python project (MISEFontsTranslate-111312_MISE2Selected ) should have a selection of Monkey Island game ID!
## DONE tryEncoding -> should be set from the DB? (via grabberFromPNG initialization)
## DONE TEST IF MISE2 prefix is applied in new session correctly (on save).
## DONE check for existence of files opened (do we do this always?)

import re

import sqlite3

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

import os, sys, shutil
from PyQt4 import QtCore, QtGui, uic

try:
    from PyQt4.QtCore import QString
except ImportError:
# we are using Python3 so QString is not defined
    QString = type("")
from  grabberFromPNG014 import grabberFromPNG

from MISESentencePreview import MyPreviewSentenceDLGWindow

#from PyQt4.QtGui import QPainter, QColor, QPalette, QWidget
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QCloseEvent


class MyMainFontDLGWindow(QtGui.QMainWindow):
    MESSAGE = "<p>This is a sample info message! "

    #
    # TODO: Can we make this a parameter for the GUI?
    # TODO: remove explicit references to encoding, 0x9a, and number of expected chars 69
    previousSessionActive = ""
    ##tryEncoding = 'windows-1253'
    localGrabInstance = grabberFromPNG() # just for init purposes and getting the tryEncoding.
    tryEncoding = localGrabInstance.getTryEncoding()
    ##activeEnc = tryEncoding #unused here
    localGrabInstance = None

    origEncoding = 'windows-1252'
    myGrabInstance = None

    currentPath = u"" # for open or save files
    relPath = u'.'
    DBFileName = u'trampol.sqlite'
    uiFolderName = u'ui'
    uiFontsToolFileName = u'MISEFontsTranslateUIDlg.ui'
    uiSentencePreviewFileName = u'sentencePreview.ui'
    DBFileNameAndRelPath = ""

    prevSentenceDLG = None

    defGameID = 1 # SomiSE
    MI2GameID = 2
    selGameID = MI2GameID

    basedir = u"."
    icon = None
    mysessionsFilename = u"mysessions.txt"
    sessionsList = []
    dirtyBitflag = 0
    MISE2_SessionPrefix = 'MISE2_'

    def eventFilter(self, object, event):
        #print "EVENT TYPE: %s VS %s " % (event.__class__.__name__, QtGui.QCloseEvent.__name__)
        #print "OBJECT: %s VS %s " % (object.__class__.__name__, self.ui.__class__.__name__)
        if self.ui.closingFlag  == False and event.__class__ == QtGui.QCloseEvent:
        ## HANDLE EVENT....
            self.closeEvent(event)
            return True
        else:
            return False


    def __init__(self, pselectedEncoding=None, pselectedGameID=None):
        QtGui.QMainWindow.__init__(self)
        if getattr(sys, 'frozen', None):
            self.basedir = sys._MEIPASS
        else:
            self.basedir = os.path.dirname(__file__)
        self.DBFileNameAndRelPath = os.path.join(self.relPath,self.DBFileName)

        # Set up the user interface from Designer.
        uiFontDlgFilePath = os.path.join(self.relPath, self.uiFolderName, self.uiFontsToolFileName)
        #print uiFontDlgFilePath
        if not os.access(uiFontDlgFilePath, os.F_OK) :
            print "Could not find the required ui file %s for the Font Tool application. Quiting..." % (self.uiFontsToolFileName)
            return

        self.ui = uic.loadUi(uiFontDlgFilePath)
        self.ui.show()

        if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
            QtGui.QMessageBox.critical(self, "Database file missing!",\
                "The database file %s could not be found. Cannot proceed without a database file. Quiting..." % (self.DBFileNameAndRelPath))
            self.tryToCloseWin()
            return

        self.icon = QIcon(":/icons/iconsimple.ico")
        self.ui.setWindowIcon( self.icon )
        self.setWindowIcon(self.icon ) # adds icons in dialog boxes

        self.ui.setWindowIcon( self.icon )
        self.ui.closingFlag = False
        self.ui.installEventFilter(self)

        self.native = True #can be used to control some native-to-OS or not dialogs being utilised (should be a checkbox)
        ##
        ## Startup sessions handling
        del self.sessionsList[:]

#        self.saveflag = 0
        uiSessionsFilePath = os.path.join(self.relPath, self.mysessionsFilename)

        if os.path.exists(uiSessionsFilePath ) and os.access(uiSessionsFilePath, os.F_OK):
            mysessionsFile = open(uiSessionsFilePath, 'rb')
            linesLst = mysessionsFile.readlines()
            involvedTokensLst =[]
            self.ui.sessionsCmBx.addItem("")
            self.ui.sessionsCmBx.setCurrentIndex(0)
            for readSessLine in linesLst:
                readSessLine = unicode("%s" % readSessLine, 'utf-8')
                del involvedTokensLst[:]
                involvedTokensLst = re.findall("[^\t\n]+",readSessLine )
                self.ui.sessionsCmBx.addItem(involvedTokensLst[0])
    ##        self.ui.sessionsCmBx.addItems(involvedTokensLst)
                # [1]: game id
                # [2]: encoding
                # [3]: filename PNG orig
                # [4]: filename PNG row characters
                # [5]: filename font orig
                # [6]: top-top
                # [7]: left-left
                # [8]: baselineOffsetSpinBox
                atmpLst = ( involvedTokensLst[1],  involvedTokensLst[2],  involvedTokensLst[3],  involvedTokensLst[4],  involvedTokensLst[5], involvedTokensLst[6], involvedTokensLst[7], involvedTokensLst[8])
                self.sessionsList.append((involvedTokensLst[0], atmpLst ))
            mysessionsFile.close()

        ##
        ##
        self.myGrabInstance = None
        self.dasPixMap = None
        self.scene = QtGui.QGraphicsScene()
        self.ui.graphicsViewPngFont.setScene(self.scene)
        self.ui.graphicsViewPngFont.show()
        self.ui.baselineOffsetSpinBox.setRange(-2, 2)
        self.ui.baselineOffsetSpinBox.setValue(0)

        #		self.openFilesPath = ''
        ## Connect up the buttons.
        self.ui.BrowsePNGfilesBtn.clicked.connect(self.setOpenPNGFileName)
        self.ui.LoadPNGBtn.clicked.connect(self.loadPNGFileNameinGraphixView)
        self.ui.BrowseCustRowfilesBtn.clicked.connect(self.setCustRowFileName)
        self.ui.BrowseOrigFontfileBtn.clicked.connect(self.setOrigFontFileName)
        self.ui.calculateOutputBtn.clicked.connect(self.calculateProcessing)
        self.ui.recalculateOutputBtn.clicked.connect(self.recalculateProcessing)
        self.ui.loadOutputPNGBtn.clicked.connect(self.loadOutputPNGFileNameinGraphixView)
        self.ui.drawOrigOutlinesBtn.clicked.connect(self.drawOutlinesForOriginGraphixView)
        self.ui.drawCopyOutlinesBtn.clicked.connect(self.drawOutlinesForCopyinGraphixView)
        self.ui.parametersSessionsSaveBtn.clicked.connect(self.saveCurrentSession)
        self.ui.parametersSessionNewBtn.clicked.connect(self.newSessionStart)
        self.ui.parametersSessionDeleteBtn.clicked.connect(self.deleteCurrentSession)
        self.ui.submitCharPropertiesBtn.clicked.connect(self.saveCharPropertiesInFile)
        self.ui.copyToGameDirBtn.clicked.connect(self.copyToGameDir)

        self.ui.previewSentenceBtn.clicked.connect(self.showPreviewSentence) # modal dialogue


##        self.ui.sessionsCmBx.currentIndexChanged.currentIndexChanged.connect(self.loadSelectedSession)
        QtCore.QObject.connect(self.ui.sessionsCmBx, QtCore.SIGNAL("currentIndexChanged(const QString)"), self.loadSelectedSessionFromComboChanged)
        QtCore.QObject.connect(self.ui.selGameCmBx, QtCore.SIGNAL("currentIndexChanged(const QString)"), self.loadSelectedGameID)

        self.fillCmBxWithSupportedGames()
        self.ui.selectedEncodingTxtBx.setText(self.tryEncoding)
        self.ui.selectedEncodingTxtBx.setReadOnly(True)

        return

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Quit Font Tool',
            "Are you sure you want to close this dialogue window?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            self.ui.closingFlag = True
        else:
            event.ignore()
            self.ui.closingFlag = False

    def tryToCloseWin(self):
##        reply = QtGui.QMessageBox.question(self, "Information message", "Do you really want to exit?", QtGui.QMessageBox.No | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
##        if reply == QtGui.QMessageBox.Yes:
        self.ui.close()
        if __name__ == '__main__':
            sys.exit(0)
        return


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
    # sets gameId and loads any pertinent required settings
    #
    def setSelectedGameByGameId(self, pGameId):
        index = self.ui.selGameCmBx.findData(pGameId)
        if index < 0:
            #TODO: debug and error message. Show in message box or SessionsErors and quit?
            #print "Error: Game Id index not found in combobox!"
            index = 0
        self.ui.selGameCmBx.setCurrentIndex(index) # this will trigger the signal to loadSelectedGameID
        return

    #
    # sets gameId and loads any pertinent required settings
    #
    def setSelectedGameByGameName(self, pGameName):
        index = self.ui.selGameCmBx.findText(pGameName)
        if index < 0:
            #TODO: debug and error message. Show in message box or SessionsErors and quit?
            #print "Error: Game Id index not found in combobox!"
            index = 0
        self.ui.selGameCmBx.setCurrentIndex(index)
        return

    # will update the self.selGameID. Will not load a new grabber instance (the caller should handle that)
    def loadSelectedGameID(self, selGameName):
        ##debug
        #print "Loading game id for: %s " % selGameName
        gameIDFound = False
        for dictKey in self.supportedGames.keys():
            if self.supportedGames[dictKey] == selGameName:
                self.selGameID = dictKey
                gameIDFound = True
                ##debug
                #print "Loaded %s ID: %d " %(self.supportedGames[dictKey], self.selGameID)
                break
        if gameIDFound == False:
            # TODO: Error dialog message
            #TODO: debug and error message. Show in message box or SessionsErors and quit?
            print "Error! The selected game is not supported! Reverting to %s" % (self.supportedGames[self.defGameID])
            self.selGameID = self.defGameID
        # also force start of new session!
        # self.newSessionStart()
        return

    def clearFieldsExceptSessionBox(self):
        self.ui.openFileNameTxtBx.setText("")
        self.ui.openCustRowFileTxtBx.setText("")
        self.ui.openOrigFontTxtBx.setText("")
        self.ui.OutputPngFileTxtBx.setText("")
        self.ui.OutputFontFileTxtBx.setText("")
        self.ui.innerSpaceLtoLpxTxtBx.setText("0")
        self.ui.InnerSpaceTtoTpxTxtBx.setText("0")

        self.ui.origPNGFileDimensionsTxtBx.setText("")
        self.ui.copyPNGFileDimensionsTxtBx.setText("")
        self.ui.numOfdetectCharsTxtBx.setText("0")

        # num of detected chars reset field
        mypalette = self.ui.numOfImportedCharsTxtBx.palette()  # get QPalette for the QLineEdit
        mypalette.setColor( QPalette.Normal, QPalette.Base, QColor('white') )
        self.ui.numOfImportedCharsTxtBx.setPalette(mypalette)
        self.ui.numOfImportedCharsTxtBx.setText("0")

        self.ui.detectedBaselineTxtBx.setText("0")

        self.ui.baselineOffsetSpinBox.setValue(0)

        if self.scene is not None:
            self.scene.clear()

        self.ui.graphicsViewPngFont.setScene(self.scene)
        self.ui.graphicsViewPngFont.show()
        #self.ui.graphicsViewPngFont.

        if self.ui.charsInFontFileTblView.model() is not None:
            self.ui.charsInFontFileTblView.model().clear()
        self.ui.charsInFontFileTblView.clearSpans()

        return

    #
    # TODO: begin a new session. Clear everything from the previous.
    # TODO: handle dirty bit(s), if previous session needs saving first.
    #
    def newSessionStart(self,silentNewSession = False):

        if self.ui.sessionsCmBx.currentIndex() <> 0:
            self.ui.sessionsCmBx.setCurrentIndex(0) # will cause this function to be called again due to selected item change
            return True

        if not silentNewSession:
            supportedGamesNames = list()
            for dictKey in self.supportedGames.keys():
                supportedGamesNames.append( self.supportedGames[dictKey])

            l1,ok= QInputDialog.getItem(self,self.tr("Select Game"),self.tr("Game"),supportedGamesNames,0,False)
            ## debug
            #print l1, ok
            if ok:
                ##print "OK"
                self.previousSessionActive = ""
                self.setSelectedGameByGameName(l1)
        #        self.saveflag = 0
                self.dirtyBitflag = 0
        #        print "currentIndex = %d " % self.ui.sessionsCmBx.currentIndex()

        #        print "called new. Proceeding due to selected 0 index."
                self.clearFieldsExceptSessionBox()

                # TODO: probably there is a better way to destroy any previous myGrabInstance
                self.myGrabInstance = None
                self.ui.sessionsCmBx.clearEditText()
            else:
                return False
        else:
            self.previousSessionActive =""
            self.setSelectedGameByGameId(self.defGameID) # load default game id (when returning from a delete)
    #        self.saveflag = 0
            self.dirtyBitflag = 0
    #        print "currentIndex = %d " % self.ui.sessionsCmBx.currentIndex()

    #        print "called new. Proceeding due to selected 0 index."
            self.clearFieldsExceptSessionBox()

            # TODO: probably there is a better way to destroy any previous myGrabInstance
            self.myGrabInstance = None
            self.ui.sessionsCmBx.clearEditText()

        return True

    def deleteCurrentSession(self):
        # get current session name
        # check if Null session is selected. DO nothing if so.
        # prompt for confirm
        matchFound = False
        matchedIndex = -1
        if self.ui.sessionsCmBx.currentIndex() <=0:
            #print "Cannot delete NULL session"
            MyMainFontDLGWindow.MESSAGE = "Cannot delete NULL session!"
            self.informationMessage()
            return

        selSessName = self.ui.sessionsCmBx.itemText(self.ui.sessionsCmBx.currentIndex())
        #print "current session name %s" % selSessName

        for i in range(0, len(self.sessionsList)):
                (itSessionName, itSessionParamsLst) = self.sessionsList[i]
                if itSessionName == selSessName:
                    matchFound = True
                    matchedIndex = i
                    #print "Found Match"

        MyMainFontDLGWindow.MESSAGE = "Are you sure you want to delete the current session (%s) ?"% (selSessName,)
        reply = self.questionMessageYesNo()
        if reply == QtGui.QMessageBox.Yes:
            ## debug
            #print "Removing session %s" % selSessName

            #  remove the session from the active list . Do we use the matchFound result? or write to file anyway?
            if matchFound:
                (sessionName, atmpLst) = self.sessionsList.pop(matchedIndex)

            #  remove the session from the combo box of sessions ( .removeItem (self, int index) )
            self.ui.sessionsCmBx.removeItem(self.ui.sessionsCmBx.currentIndex())

            #  remove the session from the file
            self.writeBackToSessionsFile()

            # return to empty new session for the default game id (don't prompt for new game id)
            MyMainFontDLGWindow.MESSAGE = "Session %s was removed successfully!"% (selSessName,)
            self.informationMessage()
            # TODO: do we really need to start a new session? Perhaps not. Let the user keep the fields and decide themselves.
            #self.newSessionStart(newSessionStart = True)
        return


##
##
##
    def loadSelectedSessionFromComboChanged(self, selSessName):
        if self.previousSessionActive <> "" and  self.previousSessionActive == selSessName: #ignore cases where we fallback to the previous active session, and maintain fields
            return
        elif self.previousSessionActive <> "" and selSessName == "":
            ## clear everything. Start new session.
            # TODO: new session
            status = self.newSessionStart()
            if status == False: #cancelled. Then return to previous session.
                self.ui.sessionsCmBx.lineEdit().setText(self.previousSessionActive)
                oldIndex = self.ui.sessionsCmBx.findText(self.previousSessionActive)
                if oldIndex > 0:
                    self.ui.sessionsCmBx.setCurrentIndex(oldIndex)

        elif self.previousSessionActive == "" and selSessName == "":
            self.newSessionStart()
        elif selSessName <> "":
            self.loadSelectedSession(selSessName)
        return

##
##
##
    # TODO: we need a dirt session bit to avoid resetting or load a new session over a changed session without confirmation
    def loadSelectedSession(self, selSessName):

    ##        print selSessName
        if selSessName != "":
            for i in range(0, len(self.sessionsList)):
                (itSessionName, itSessionParamsLst) = self.sessionsList[i]
                if itSessionName == selSessName:
                    matchFound = True
                    self.previousSessionActive = itSessionName

                    # clear all fields first!
                    self.clearFieldsExceptSessionBox()
                    self.myGrabInstance = None
                    self.ui.sessionsCmBx.lineEdit().setText(selSessName)
                    self.setSelectedGameByGameId( int(itSessionParamsLst[0]))
                    # TODO ignoring the tryEncoding itSessionParamsLst[1] field for now (should try to match?)

                    self.ui.openFileNameTxtBx.setText(itSessionParamsLst[2])
                    self.ui.openCustRowFileTxtBx.setText(itSessionParamsLst[3])
                    self.ui.openOrigFontTxtBx.setText(itSessionParamsLst[4])
                    self.ui.innerSpaceLtoLpxTxtBx.setText(itSessionParamsLst[5])
                    self.ui.InnerSpaceTtoTpxTxtBx.setText(itSessionParamsLst[6])
                    self.ui.baselineOffsetSpinBox.setValue(int(itSessionParamsLst[7]))
                    #
                    # TODO: maybe I can check with some checksums stored to verify that the files were not changed outside the session!
                    # For now, just check if in the same folder there are files with the expected name for the corresponding output files
                    #
                    origFontFilename = self.ui.openOrigFontTxtBx.text().strip()
                    imageOriginalPNG = self.ui.openFileNameTxtBx.text().strip()
                    if  origFontFilename <> "" and imageOriginalPNG <> "":
                        if self.myGrabInstance is not None:
                            self.myGrabInstance.setDasOrigFontFilename(origFontFilename)
                            self.myGrabInstance.setImageOriginalPNG(imageOriginalPNG)
                            self.myGrabInstance.setGameID(self.selGameID)
                            self.myGrabInstance.setActiveEncoding(self.tryEncoding)
                            self.myGrabInstance.calcFromDB() # needed because of potential changes in GameId and Encoding!
                        else:
                            self.myGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID, origFontFilename, imageOriginalPNG)
                        #
                        # get expected filenames.
                        expectedFileNameForOutputPNG = self.myGrabInstance.getExpectedFileNameForOutputPNG()
                        expectedFileNameForOutputINFO = self.myGrabInstance.getExpectedFileNameForOutputINFO()
                        #
                        #
                        # if both expected filenames exist in the same folder then put them in the textboxes.
                        if expectedFileNameForOutputPNG <> "" and os.path.exists(expectedFileNameForOutputPNG) and expectedFileNameForOutputINFO <> "" and  os.path.exists(expectedFileNameForOutputINFO):
                            self.myGrabInstance.setCopyFontFileName(expectedFileNameForOutputINFO)
                            self.myGrabInstance.setCopyPNGFileName(expectedFileNameForOutputPNG)

                            self.ui.OutputPngFileTxtBx.setText(expectedFileNameForOutputPNG)
                            self.ui.OutputFontFileTxtBx.setText(expectedFileNameForOutputINFO)
                            self.loadOutputPNGFileNameinGraphixView()
                            self.ui.origPNGFileDimensionsTxtBx.setText(self.myGrabInstance.getImagePropertiesInfo(True))
                            self.ui.copyPNGFileDimensionsTxtBx.setText(self.myGrabInstance.getImagePropertiesInfo(False))

                            if self.ui.innerSpaceLtoLpxTxtBx.text().strip <> "" and self.ui.InnerSpaceTtoTpxTxtBx.text().strip() <> "":
                                minSpaceBetweenLettersInRowLeftToLeft =   int(self.ui.innerSpaceLtoLpxTxtBx.text())
                                minSpaceBetweenLettersInColumnTopToTop =   int(self.ui.InnerSpaceTtoTpxTxtBx.text())
                                self.myGrabInstance.setMinSpaceBetweenLettersInRowLeftToLeft(minSpaceBetweenLettersInRowLeftToLeft)
                                self.myGrabInstance.setMinSpaceBetweenLettersInColumnTopToTop(minSpaceBetweenLettersInColumnTopToTop)
                                self.ui.detectedBaselineTxtBx.setText(str(self.myGrabInstance.findDetectedBaseline()))

                            (pTotalFontLetters, pImportedFontLetters) = self.myGrabInstance.findTotalAndImportedChars(expectedFileNameForOutputINFO)
                            self.ui.numOfdetectCharsTxtBx.setText(str(pTotalFontLetters))
                            self.ui.numOfImportedCharsTxtBx.setText(str(pImportedFontLetters))
                            self.loadCharPropertiesInTable(pTotalFontLetters)
                        #
                        #
                        # TODO: Otherwise, load up the image only for the original file and partial stats and return!
                        else:
                            self.loadPNGFileNameinGraphixView()
                            self.ui.origPNGFileDimensionsTxtBx.setText(self.myGrabInstance.getImagePropertiesInfo(True))
                            (pTotalFontLetters, pImportedFontLetters) = self.myGrabInstance.findTotalAndImportedChars(origFontFilename)
                            self.ui.numOfdetectCharsTxtBx.setText(str(pTotalFontLetters))
                            self.ui.numOfImportedCharsTxtBx.setText(str(pImportedFontLetters))
                    #
                    break
##        else:
##            ## clear everything. Start new session.
##            # TODO: new session
##            self.newSessionStart()
##            return
        return

##
##
##
    def saveCurrentSession(self, silentBool=False):
        ## grab filename of foriginal ont file,  the png row file, te original png file
        # TODO: ALSO (if any) the produced font and png files (?///) or other parameters?
        ## and the used parameters (
        ## and a session name
        ## write in file mysessions.txt
        if self.ui.sessionsCmBx.lineEdit().text().strip() == "" or \
                 (self.ui.openFileNameTxtBx.text().strip() =="" or \
                    self.ui.openCustRowFileTxtBx.text().strip() =="" or \
                    self.ui.openOrigFontTxtBx.text().strip() =="" or \
                    self.ui.innerSpaceLtoLpxTxtBx.text().strip() =="0" or \
                    self.ui.InnerSpaceTtoTpxTxtBx.text().strip() =="0"):
            #
            # TODO: display error message!
            #
            if silentBool == False:
                errMsg = "Insufficient fields were submitted. Session was not saved...!"
                MyMainFontDLGWindow.MESSAGE = errMsg
                self.informationMessage()
            return
        else:

            matchFound = False
            sessionName = self.ui.sessionsCmBx.lineEdit().text().strip()
            # Add prefix
            if self.selGameID == self.MI2GameID and not sessionName.startswith(self.MISE2_SessionPrefix):
                sessionName = "%s%s" % (self.MISE2_SessionPrefix, sessionName)
                self.ui.sessionsCmBx.lineEdit().setText(sessionName)
            atmpLst = ( self.selGameID, \
                        self.tryEncoding, \
                        self.ui.openFileNameTxtBx.text().strip(), \
                        self.ui.openCustRowFileTxtBx.text().strip(),  \
                        self.ui.openOrigFontTxtBx.text().strip(),  \
                        self.ui.innerSpaceLtoLpxTxtBx.text().strip(),  \
                        self.ui.InnerSpaceTtoTpxTxtBx.text().strip(), \
                        self.ui.baselineOffsetSpinBox.value())
            for i in range(0, len(self.sessionsList)):
                (itSessionName, itSessionParamsLst) = self.sessionsList[i]
                if itSessionName == sessionName:
                    matchFound = True
                    ## Debug
                    #print "Overwriting session %s" % (itSessionName,)
                    # TODO: prompt here?
                    MyMainFontDLGWindow.MESSAGE = "Session %s will be overwritten with the current session's data. Do you want to continue?"% (itSessionName,)
                    reply = self.questionMessageYesNo()
                    if reply == QtGui.QMessageBox.Yes:
                        self.sessionsList[i] = (itSessionName, atmpLst)
                    else:
                        ## Debug
                        #print "Save session %s was canceled!"% (itSessionName,)
                        return
                    break
            if matchFound == False:
                self.sessionsList.append((sessionName, atmpLst))
                # DONE: update the combo box with new session!!!
                self.ui.sessionsCmBx.addItem(sessionName)

            self.previousSessionActive = sessionName
            self.writeBackToSessionsFile()
        return
##
##
##
    def writeBackToSessionsFile(self):
        uiSessionsFilePath = os.path.join(self.relPath, self.mysessionsFilename)
        if os.path.exists(uiSessionsFilePath ) and os.access(uiSessionsFilePath, os.F_OK):
            mysessionsFile = open(uiSessionsFilePath, 'wb')
            for (itSessionName, itSessionParamsLst) in self.sessionsList:
                newEntryStr = "%s\t%d\t%s\t%s\t%s\t%s\t%d\t%d\t%d\n" % (itSessionName, \
                                                                    int(itSessionParamsLst[0]), \
                                                                    itSessionParamsLst[1], \
                                                                    itSessionParamsLst[2], \
                                                                    itSessionParamsLst[3], \
                                                                    itSessionParamsLst[4], \
                                                                    int(itSessionParamsLst[5]) , \
                                                                    int(itSessionParamsLst[6]), \
                                                                    int(itSessionParamsLst[7]) )
                newEntryStrEnc = unicode.encode("%s" % newEntryStr, 'utf-8')
                mysessionsFile.write(newEntryStrEnc) # loop writing all entries
            mysessionsFile.close()
##
##
##
    def drawOutlinesForOriginGraphixView(self):
        origFontFilename = self.ui.openOrigFontTxtBx.text().strip()
        imageOriginalPNG = self.ui.openFileNameTxtBx.text().strip()

        if  origFontFilename <> "" and imageOriginalPNG <> "":
            if self.myGrabInstance is not None:
                self.myGrabInstance.setDasOrigFontFilename(origFontFilename)
                self.myGrabInstance.setImageOriginalPNG(imageOriginalPNG)
                self.myGrabInstance.setGameID(self.selGameID)
                self.myGrabInstance.setActiveEncoding(self.tryEncoding)
                self.myGrabInstance.calcFromDB() # needed because of potential changes in GameId and Encoding!
            else:
                self.myGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID, origFontFilename, imageOriginalPNG)
        else:
            #print "Bad Arguments for outlining!"
            errMsg = "Bad Arguments for outlining!"
            MyMainFontDLGWindow.MESSAGE = errMsg
            self.informationMessage()
            return

        if self.myGrabInstance is not None:
            outlinesList = self.myGrabInstance.getLetterOutlines(True)
            ##fileName = QString(self.ui.openFileNameTxtBx.text())
            fileName = self.ui.openFileNameTxtBx.text()
            self.paintOutlines(outlinesList, fileName)
        return
##
##
##
    def drawOutlinesForCopyinGraphixView(self):
        origFontFilename =   self.ui.openOrigFontTxtBx.text().strip()
        imageOriginalPNG = self.ui.openFileNameTxtBx.text().strip()

        copyFontFileName = self.ui.OutputFontFileTxtBx.text().strip()
        copyPNGFileName =  self.ui.OutputPngFileTxtBx.text().strip()

        if  origFontFilename <> "" and  imageOriginalPNG  <> "" and copyFontFileName <> "" and copyPNGFileName <> "":
            if self.myGrabInstance is not None:
                self.myGrabInstance.setCopyFontFileName(copyFontFileName)
                self.myGrabInstance.setCopyPNGFileName(copyPNGFileName)
            else:
                self.myGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID, origFontFilename,   imageOriginalPNG)
                self.myGrabInstance.setCopyFontFileName(copyFontFileName)
                self.myGrabInstance.setCopyPNGFileName(copyPNGFileName)
        else:
            #print "Bad Arguments for outlining!"
            errMsg = "Bad Arguments for outlining!"
            MyMainFontDLGWindow.MESSAGE = errMsg
            self.informationMessage()
            return

        if self.myGrabInstance is not None:
            outlinesList = self.myGrabInstance.getLetterOutlines(False)
            ##fileName = QString(self.ui.OutputPngFileTxtBx.text())
            fileName = self.ui.OutputPngFileTxtBx.text()
            self.paintOutlines(outlinesList, fileName)
        return
##
##
##
    def paintOutlines(self, inputListmy, fileNameTxt):
##        MyMainFontDLGWindow.MESSAGE = "Ok now to paint!"
##        self.informationMessage()
        # todo: optimize to reuse existing scene!!! or at least clean up
        if self.scene is not None:
            self.scene.clear()
        self.dasPixMap = QtGui.QPixmap(fileNameTxt)
        p = QPainter(self.dasPixMap)
#        p.setBackgroundColor(QColor("white"))
#        h = self.height()
#        w = self.width()
#        for i in range(1, h, h/5):
        p.setPen(QColor("yellow"))
        for i in range(0, len(inputListmy)):
            (x1,y1, x2, y2, t1, t2, t3, chr0) = inputListmy[i]
            p.drawLine(x1-1, y1-1, x1-1, y2-1)
            p.drawLine(x1-1, y2-1, x2-1, y2-1)
            p.drawLine(x2-1, y2-1, x2-1, y1-1)
            p.drawLine(x2-1, y1-1, x1-1, y1-1)
        self.scene.addPixmap(QtGui.QPixmap(self.dasPixMap))
        self.ui.graphicsViewPngFont.setScene(self.scene)
        self.ui.graphicsViewPngFont.show()
##        if self.dasPixMap is not None:
##            del self.dasPixMap
        return
##
##
    def fixFileNameWithOsSep(self,filename):
        p = re.compile('[/]|(\\\\)')
        sep = ''
        if os.sep == '\\':
            sep = '\\\\'
        else:
            sep = os.sep
        retFileName = p.sub(sep, filename)
        return retFileName

##
##
##
    def setCustRowFileName(self):
        options = QtGui.QFileDialog.Options()
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
##        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
##            "Open Custom Row of Letters PNG Image file", self.ui.openCustRowFileTxtBx.text(),
##            "PNG Row Image Files (*.png);;All Files (*)", options)
        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
            "Open Custom Row of Letters PNG Image file", self.currentPath,
            "PNG Row Image Files (*.png);;All Files (*)", options)
        if filenNameGiv:
            filenNameGiv = self.fixFileNameWithOsSep(filenNameGiv)
            filenNameGiv = filenNameGiv.strip()
            filepathSplitTbl = os.path.split(filenNameGiv)
            self.currentPath = filepathSplitTbl[0]

            self.ui.openCustRowFileTxtBx.setText(filenNameGiv)
        return

##
##
##
    def setOrigFontFileName(self):
        options = QtGui.QFileDialog.Options()
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
##        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
##            "Open Original Font Data file", self.ui.openOrigFontTxtBx.text(),
##            "FONT MISE Files (*.font);;All Files (*)", options)
        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
            "Open Original Font Data file", self.ui.openOrigFontTxtBx.text(),
            "FONT MISE Files (*.font);;All Files (*)", options)
        if filenNameGiv:
            filenNameGiv = self.fixFileNameWithOsSep(filenNameGiv)
            filenNameGiv = filenNameGiv.strip()
            filepathSplitTbl = os.path.split(filenNameGiv)
            self.currentPath = filepathSplitTbl[0]
            self.ui.openOrigFontTxtBx.setText(filenNameGiv)
        return

##
##
##
    def setOpenPNGFileName(self):
        options = QtGui.QFileDialog.Options()
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
##        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
##            "Open Font Image file", self.ui.openFileNameTxtBx.text(),
##            "PNG Image Files (*.png);;All Files (*)", options)
        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
            "Open Font Image file", self.ui.openFileNameTxtBx.text(),
            "PNG Image Files (*.png);;All Files (*)", options)
        if filenNameGiv:
            filenNameGiv = self.fixFileNameWithOsSep(filenNameGiv)
            filenNameGiv = filenNameGiv.strip()
            filepathSplitTbl = os.path.split(filenNameGiv)
            self.currentPath = filepathSplitTbl[0]

            self.ui.openFileNameTxtBx.setText(filenNameGiv)
            self.loadPNGFileNameinGraphixView()
#			self.openFilesPath = files[0]
#			self.ui.openFileNameTxtBx.setText("[%s]" % ', '.join(files))

		## Make some local modifications.
		#self.ui.colorDepthCombo.addItem("2 colors (1 bit per pixel)")
        return
##
##
##
    def loadPngInGV(self, filenameTxt):
        # todo: code to clear an existing scene
        #
        if self.scene is not None:
            self.scene.clear()
#        self.scene = QtGui.QGraphicsScene()
        self.scene.addPixmap(QtGui.QPixmap(filenameTxt))
        self.ui.graphicsViewPngFont.setScene(self.scene)
        self.ui.graphicsViewPngFont.show()
        return
##
##
##
    def loadOutputPNGFileNameinGraphixView(self):
        ##fileName = QString(self.ui.OutputPngFileTxtBx.text())
        fileName = self.ui.OutputPngFileTxtBx.text()
        self.loadPngInGV(fileName)
        return

##
##
##
    def loadPNGFileNameinGraphixView(self):
        ##fileName = QString(self.ui.openFileNameTxtBx.text())
        fileName = self.ui.openFileNameTxtBx.text()
        self.loadPngInGV(fileName)
        return
##
##
##
    def calculateProcessing(self):
##      For the time being call the same process as recalcute.
        self.recalculateProcessing()
        return

##
##
##
    def recalculateProcessing(self):
        minSpaceBetweenLettersInRowLeftToLeft =   int(self.ui.innerSpaceLtoLpxTxtBx.text())
        minSpaceBetweenLettersInColumnTopToTop =   int(self.ui.InnerSpaceTtoTpxTxtBx.text())
        origFontFilename =   self.ui.openOrigFontTxtBx.text().strip()
        imageOriginalPNG = self.ui.openFileNameTxtBx.text().strip()
        imageRowFilePNG=   self.ui.openCustRowFileTxtBx.text().strip()
        customBaseLineOffset = self.ui.baselineOffsetSpinBox.value()

        if  origFontFilename <> "" and imageOriginalPNG <> "" and imageRowFilePNG <> "" and minSpaceBetweenLettersInRowLeftToLeft > 0 and minSpaceBetweenLettersInColumnTopToTop >0:
            if self.myGrabInstance is not None:
#                print "%s %s %s %d %d" % (origFontFilename, imageOriginalPNG, imageRowFilePNG, minSpaceBetweenLettersInRowLeftToLeft, minSpaceBetweenLettersInColumnTopToTop)
                self.myGrabInstance.setDasOrigFontFilename(origFontFilename)
                self.myGrabInstance.setImageOriginalPNG(imageOriginalPNG)
                self.myGrabInstance.setImageRowFilePNG(imageRowFilePNG)
                self.myGrabInstance.setMinSpaceBetweenLettersInRowLeftToLeft(minSpaceBetweenLettersInRowLeftToLeft)
                self.myGrabInstance.setMinSpaceBetweenLettersInColumnTopToTop(minSpaceBetweenLettersInColumnTopToTop)
##                self.myGrabInstance.setBaseLineOffset(customBaseLineOffset)
                self.myGrabInstance.setGameID(self.selGameID)
                self.myGrabInstance.setActiveEncoding(self.tryEncoding)
                self.myGrabInstance.calcFromDB() # needed because of potential changes in GameId and Encoding!
                self.myGrabInstance.cleanup() #because we re-use
            else:
                self.myGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID, origFontFilename, imageOriginalPNG)
                self.myGrabInstance.setImageRowFilePNG(imageRowFilePNG)
                self.myGrabInstance.setMinSpaceBetweenLettersInRowLeftToLeft(minSpaceBetweenLettersInRowLeftToLeft)
                self.myGrabInstance.setMinSpaceBetweenLettersInColumnTopToTop(minSpaceBetweenLettersInColumnTopToTop)
##                self.myGrabInstance.setBaseLineOffset(customBaseLineOffset)

        else:
            errMsg = "Bad Arguments for processing!"
            MyMainFontDLGWindow.MESSAGE = errMsg
            self.informationMessage()
            return

        (errStat, errMsg, detBaseline, totalFontLetters, importedNumOfLetters) = self.myGrabInstance.generateModFiles(customBaseLineOffset)
        if errStat == 0:
            self.ui.OutputFontFileTxtBx.setText(self.myGrabInstance.copyFontFileName)
            self.ui.OutputPngFileTxtBx.setText(self.myGrabInstance.copyPNGFileName)
            self.ui.detectedBaselineTxtBx.setText(str(detBaseline))
            self.ui.numOfdetectCharsTxtBx.setText(str(totalFontLetters))
            mypalette = QPalette()
#            mypalette.setColor(widget.backgroundRole(), QColor('red'))
#            numOfImportedCharsTxtBx.setPalette(palette)
            mypalette = self.ui.numOfImportedCharsTxtBx.palette()  # get QPalette for the QLineEdit
            if importedNumOfLetters != len(self.myGrabInstance.orderAndListOfForeignLetters):
                mypalette.setColor( QPalette.Normal, QPalette.Base, QColor('red') )
            else:
                mypalette.setColor( QPalette.Normal, QPalette.Base, QColor('white') )
            self.ui.numOfImportedCharsTxtBx.setPalette(mypalette)
            self.ui.numOfImportedCharsTxtBx.setText(str(importedNumOfLetters))
            self.ui.numOfImportedCharsTxtBx.setModified(True)
            self.ui.origPNGFileDimensionsTxtBx.setText(self.myGrabInstance.origFontPropertiesTxt)
            self.ui.copyPNGFileDimensionsTxtBx.setText(self.myGrabInstance.copyFontPropertiesTxt)
            self.drawOutlinesForCopyinGraphixView()
            self.loadCharPropertiesInTable(totalFontLetters)
            #
            # And save session (if one is selected -other than "" ), mainly for the offset to baseline!
            #
            self.saveCurrentSession(True)
        MyMainFontDLGWindow.MESSAGE = errMsg
        self.informationMessage()
        return
##
##
##
    def loadCharPropertiesInTable(self, pTotalFontLetters):
        if self.ui.charsInFontFileTblView.model() is not None:
            self.ui.charsInFontFileTblView.model().clear()
        self.ui.charsInFontFileTblView.clearSpans()

        if self.myGrabInstance is not None:
            outlinesList = self.myGrabInstance.getLetterOutlines(False)
            # create table
            lm = QStandardItemModel(pTotalFontLetters, 8, self)
            lm.setHeaderData(0,Qt.Horizontal, u"Chr")
            lm.setHeaderData(1,Qt.Horizontal, u"strX")
            lm.setHeaderData(2,Qt.Horizontal, u"strY")
            lm.setHeaderData(3,Qt.Horizontal, u"finX")
            lm.setHeaderData(4,Qt.Horizontal, u"finY")
            lm.setHeaderData(5,Qt.Horizontal, u"Indnt") #from left Indent in pixeld
            lm.setHeaderData(6,Qt.Horizontal, u"Wid")
            lm.setHeaderData(7,Qt.Horizontal, u"Kern")

            for rowi in range(0,pTotalFontLetters):
                index = lm.index(rowi, 0, QModelIndex())
                if rowi < self.myGrabInstance.lettersInOriginalFontFile:
                    lm.setData(index, unicode(str(outlinesList[rowi][7]),self.origEncoding))
                else:
                    lm.setData(index, unicode(str(outlinesList[rowi][7]),self.myGrabInstance.activeEncoding))
                for columni in range(0,7):
                    index = lm.index(rowi, columni+1, QModelIndex())
                    # tmpRowStart[0], tmpColStart[0], tmpRowEnd[0], tmpColEnd[0], tmpPixelsWithinLetterBoxFromLeftToLetter[0], tmpWidthLetter[0], tmpKerningLetter[0]
                    lm.setData(index, unicode(str(outlinesList[rowi][columni]),self.myGrabInstance.activeEncoding))
            self.ui.charsInFontFileTblView.setModel(lm)
        return
##
## Update only the added letter properties. Do not update for the original letters.
## Essentially just write back to the copy file with the char table. Update-able should only be the columns of kern and indnt!
##
    def saveCharPropertiesInFile(self):
        newCharAttributesLst = []
        if (self.myGrabInstance is not None) and (self.ui.OutputFontFileTxtBx.text().strip() == self.myGrabInstance.copyFontFileName) \
        and (self.ui.numOfdetectCharsTxtBx.text().strip() != "") and (self.ui.numOfImportedCharsTxtBx.text().strip() != ""):
            plithosOfAllChars = int(self.ui.numOfdetectCharsTxtBx.text().strip())
            plithosOfImportedChars = int(self.ui.numOfImportedCharsTxtBx.text().strip())
            for rowi in range(plithosOfAllChars - plithosOfImportedChars, plithosOfAllChars):
                # 5 is the index for column Indent
                indexIndnt =  self.ui.charsInFontFileTblView.model().index(rowi, 5, QModelIndex())
                datoTmpIndnt = self.ui.charsInFontFileTblView.model().data(indexIndnt).toPyObject()
                # 7 is the index for column kerning
                indexKern =  self.ui.charsInFontFileTblView.model().index(rowi, 7, QModelIndex())
                datoTmpKern = self.ui.charsInFontFileTblView.model().data(indexKern).toPyObject()
                myASCIIStringIndnt = unicode.encode("%s" % datoTmpIndnt, self.myGrabInstance.activeEncoding)
                myASCIIStringKern = unicode.encode("%s" % datoTmpKern, self.myGrabInstance.activeEncoding)
                tmpintIndnt = int(myASCIIStringIndnt)
                tmpintKern = int(myASCIIStringKern)
##                print "char id: %d - Indent= %d, Kern= %d" % (rowi+1, tmpintIndnt, tmpintKern)
                newCharAttributesLst.append((rowi, tmpintIndnt, tmpintKern))
            if len(newCharAttributesLst) == plithosOfImportedChars:
##                print "length of list = %d " % len(newCharAttributesLst)
                self.myGrabInstance.writeBackCharProperties(newCharAttributesLst)
# TODO: return error code and info alert!
        return

    def copyToGameDir(self):
        ## debug
        #print "Keep backup checkbox is {0}".format(self.ui.BkpOrigFilesInGameDirCkBx.isChecked())
        MyMainFontDLGWindow.MESSAGE = "Function not yet implemented!"
        self.informationMessage()
        return
##
##
##
    def showPreviewSentence(self):

        uiSentencePreviewFilePath = os.path.join(self.relPath, self.uiFolderName, self.uiSentencePreviewFileName)
        #print uiFontDlgFilePath
        if not os.access(uiSentencePreviewFilePath, os.F_OK) :
            print "Could not find the required ui file %s for the Sentence Preview Dialogue." % (self.uiSentencePreviewFileName)

        currentFontFile = ''

        self.prevSentenceDLG = MyPreviewSentenceDLGWindow(self.tryEncoding, self.selGameID, currentFontFile)

        ##MyMainFontDLGWindow.MESSAGE = "Function not yet implemented!"
        ##self.informationMessage()
        return


##
##
##
    def informationMessage(self):
        reply = QtGui.QMessageBox.information(self,
                "Information message", MyMainFontDLGWindow.MESSAGE)
#        if reply == QtGui.QMessageBox.Ok:
#            self.informationLabel.setText("OK")
#        else:
#            self.informationLabel.setText("Escape")
        return

##
##
##
    def questionMessageYesNoCancel(self):
        reply = QtGui.QMessageBox.question(self, "Question",
                    MyMainFontDLGWindow.MESSAGE,
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
#        if reply == QtGui.QMessageBox.Yes:
#            self.questionLabel.setText("Yes")
#        elif reply == QtGui.QMessageBox.No:
#            self.questionLabel.setText("No")
#        else:
#            self.questionLabel.setText("Cancel")
        return reply

    def questionMessageYesNo(self):
        reply = QtGui.QMessageBox.question(self, "Question",
                    MyMainFontDLGWindow.MESSAGE,
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
#        if reply == QtGui.QMessageBox.Yes:
#            self.questionLabel.setText("Yes")
#        elif reply == QtGui.QMessageBox.No:
#            self.questionLabel.setText("No")
#        else:
#            self.questionLabel.setText("Cancel")
        return reply
##
##
##
    def warningMessage(self):
        msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                    "Warning", MyMainFontDLGWindow.MESSAGE,
                    QtGui.QMessageBox.NoButton, self)
        #msgBox.addButton("Save &Again", QtGui.QMessageBox.AcceptRole)
        msgBox.addButton("&Continue", QtGui.QMessageBox.RejectRole)
        msgBox.exec_()
 #       if msgBox.exec_() == QtGui.QMessageBox.AcceptRole:
 #           self.warningLabel.setText("Save Again")
 #       else:
 #           self.warningLabel.setText("Continue")

 #	def errorMessage(self):
 #		self.errorMessageDialog.showMessage("This dialog shows and remembers "
 #              "error messages. If the checkbox is checked (as it is by "
 #              "default), the shown message will be shown again, but if the "
 #              "user unchecks the box the message will not appear again if "
 #              "QErrorMessage.showMessage() is called with the same message.")
 #       self.errorLabel.setText("If the box is unchecked, the message won't "
 #               "appear again.")
        return

##
## Load up the main window (instantiate an object of the MyMainFontDLGWindow class)
##
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyMainFontDLGWindow('windows-1253', 1)
    sys.exit(app.exec_())


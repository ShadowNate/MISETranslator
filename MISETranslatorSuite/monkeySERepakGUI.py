#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Created by Praetorian (ShadowNate) for Classic Adventures in Greek
# classic.adventures.in.greek@gmail.com
#
import re

import sqlite3

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)
import msgBoxesStub

import os, sys, shutil
from PyQt4 import QtCore, QtGui, uic

try:
    from PyQt4.QtCore import QString
except ImportError:
# we are using Python3 so QString is not defined
    QString = type("")
from  monkeySERepaker import pakFile

#from PyQt4.QtGui import QPainter, QColor, QPalette, QWidget
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QCloseEvent

#
# TODO: Use GUI file if available!
class MyMainRepackerDLGWindow(QtGui.QMainWindow):

    tryEncoding = 'windows-1253'
    origEncoding = 'windows-1252'

    currentPath = u"" # for open or save files
    relPath = u'.'
    uiFolderName = u'ui'
    uiRepackerToolFileName = u'MISERepackUIWin.ui'
    MI1GameID = 1
    MI1GameStr = 'The Secret of Monkey Island: SE'
    MI1GameShortStr = 'mise'
    MI2GameID = 2
    MI2GameStr = 'Monkey Island 2: SE'
    MI2GameShortStr = 'mi2se'
    defGameID = MI1GameID # SomiSE
    selGameID = MI2GameID


    basedir = u"."
    icon = None
    ui = None

    def eventFilter(self, object, event):
        #print "EVENT TYPE: %s VS %s " % (event.__class__.__name__, QtGui.QCloseEvent.__name__)
        #print "OBJECT: %s VS %s " % (object.__class__.__name__, self.ui.__class__.__name__)
        if self.ui.closingFlag  == False and event.__class__ == QtGui.QCloseEvent:
        ## HANDLE EVENT....
            self.closeEvent(event)
            return True
        else:
            return False
##
##
##
    def __init__(self, custParent = None, pselectedEncoding=None, pselectedGameID=None):
        self.ui = None
        if custParent == None:
            QtGui.QMainWindow.__init__(self, custParent)
        else:
            QtGui.QMainWindow.__init__(self)
        if getattr(sys, 'frozen', None):
            self.basedir = sys._MEIPASS
        else:
            self.basedir = os.path.dirname(__file__)
        # Set up the user interface from Designer.
        uiRepackerToolFilePath = os.path.join(self.relPath, self.uiFolderName, self.uiRepackerToolFileName)
        #print uiRepackerToolFilePath
        if not os.access(uiRepackerToolFilePath, os.F_OK) :
            print "Could not find the required ui file %s for the Repacker Tool application. Quiting..." % (self.uiRepackerToolFileName)
            self.tryToCloseWin()
            return

        self.ui = uic.loadUi(uiRepackerToolFilePath)
        self.ui.show()

        self.icon = QIcon(":/icons/iconsimple.ico")
        self.ui.setWindowIcon( self.icon )
        self.setWindowIcon(self.icon ) # adds icons in dialog boxes

        self.ui.setWindowIcon( self.icon )
        self.ui.closingFlag = False
        self.ui.installEventFilter(self)

        self.native = True #can be used to control some native-to-OS or not dialogs being utilised (should be a checkbox)

        self.ui.BrowseOrigPakBtn.clicked.connect(self.setOrigPakFilePath)
        self.ui.BrowseExtrFolderBtn.clicked.connect(self.setExtractedFolderPath)
        self.ui.SubmitRepackBtn.clicked.connect(self.goRepack)
        self.ui.resetBtn.clicked.connect(self.clearFields)

        self.ui.actionQuit_3.triggered.connect(self.tryToCloseWin)   ## Should check for dirty bit
        self.ui.actionQuit_3.setShortcut('Ctrl+Q')
        self.ui.actionAbout.triggered.connect(self.showAbout)

        self.ui.selGameCmBx.addItem(self.MI1GameStr, self.MI1GameID)
        self.ui.selGameCmBx.addItem(self.MI2GameStr, self.MI2GameID)

        return
##
##
##
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Quit Repacker Tool',
            "Are you sure you want to close this dialogue window?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.ui.closingFlag = True
            event.accept()
        else:
            event.ignore()
            self.ui.closingFlag = False

    def tryToCloseWin(self):
        if self.ui is not None:
            self.ui.close()
            #self.close()
##        if __name__ == '__main__':
##            sys.exit(0)
        return
##
##
##
    def setOrigPakFilePath(self):
        options = QtGui.QFileDialog.Options()
#        self.native = True
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
        filenNameGiv = QtGui.QFileDialog.getOpenFileName(self,
            "Open Original Pak File ",
            self.currentPath,
            "pak File (*.pak)", options)

        if filenNameGiv:
            filenNameGiv= self.fixFileNameWithOsSep(filenNameGiv)
            filenNameGiv = filenNameGiv.strip()
            filepathSplitTbl = os.path.split(filenNameGiv)
            self.currentPath = filepathSplitTbl[0]
            self.ui.origPakFileNameTxtBx.setText(filenNameGiv)
            #self.ui.extractedFolderNameTxtBx.setText("")
        return

##
##
##
    def setExtractedFolderPath(self):
        options = QtGui.QFileDialog.Options()
#        self.native = True
        if not self.native:
            options |= QtGui.QFileDialog.DontUseNativeDialog
        folderNameGiv = QtGui.QFileDialog. getExistingDirectory(self,
            "Select Extracted Game Folder ",
            #self.ui.openFileNameTxtBx.text(),
            self.currentPath, options)

        if folderNameGiv:
            folderNameGiv= self.fixFileNameWithOsSep(folderNameGiv)
            folderNameGiv = folderNameGiv.strip()
            filepathSplitTbl = os.path.split(folderNameGiv)
            self.currentPath = filepathSplitTbl[0]
            #self.ui.origPakFileNameTxtBx.setText("")
            self.ui.extractedFolderNameTxtBx.setText(folderNameGiv)
        #msgBoxesStub.qMsgBoxInformation(self.ui, "Not yet implemented", "Function not yet implemented!")
        return

##
##
##
    def goRepack(self):
        TMPoriginalPakFilename = ""
        TMProotFolderWithExtractedFiles = ""
        TMPoriginalPakFilename = self.ui.origPakFileNameTxtBx.text().strip()
        TMProotFolderWithExtractedFiles = self.ui.extractedFolderNameTxtBx.text().strip()
        selParseMode = 0 # TODO: Select 1 or 2, based on combobox
        selParseModeStr = self.ui.selGameCmBx.itemText(self.ui.selGameCmBx.currentIndex())
        if selParseModeStr == self.MI1GameStr:
            selParseMode = self.MI1GameID
        elif selParseModeStr == self.MI2GameStr:
            selParseMode = self.MI2GameID
        #print "parsMode %d" % (selParseMode,)

        if TMPoriginalPakFilename == '' or TMProotFolderWithExtractedFiles == '' or selParseMode <= 0 or selParseMode >2:
            msgBoxesStub.qMsgBoxWarning(self.ui, "Warning", "Arguments for process are invalid.")
        else:
            myOriginalPakInstance = pakFile(TMPoriginalPakFilename)

            if(myOriginalPakInstance._pakHeader != None):
                errorFound = myOriginalPakInstance.produceModdedPak(TMProotFolderWithExtractedFiles, selParseMode)
                #errorFound = True
                if errorFound:
                    msgBoxesStub.qMsgBoxWarning(self.ui, "Warning", "Process was halted by unexpected errors during the re-packing! Failed to produce a valid pak.")
                else:
                    msgBoxesStub.qMsgBoxInformation(self.ui, "Process completed", "Process completed with no errors!")
            else:
                msgBoxesStub.qMsgBoxWarning(self.ui, "Warning", "Process was halted by unexpected errors while attempting to read from the original pak file! Process Failed.")
        return

    def clearFields(self):
        self.ui.origPakFileNameTxtBx.setText("")
        self.ui.extractedFolderNameTxtBx.setText("")
        self.ui.selGameCmBx.setCurrentIndex(0)
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
    def showAbout(self):
        msgBoxesStub.qMsgBoxAbout(self.ui, "About MISE Series Repacker",
                "<p>This application was built for the fan translation purposes of LucasArt's SoMI:SE and MI2:SE. " \
                "<br>It was made by the Classic Adventures in Greek group and is distributed freely.</p>" \
                "<p>Special Thanks to: BgBennyBoy</p>")
        return

##
## Load up the main window (instantiate an object of the MyMainRepackerDLGWindow class)
##
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyMainRepackerDLGWindow(None, 'windows-1253', 1)
    sys.exit(app.exec_())



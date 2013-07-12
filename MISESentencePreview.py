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

import os, sys, shutil
from PyQt4 import QtCore, QtGui, uic

try:
    from PyQt4.QtCore import QString
except ImportError:
# we are using Python3 so QString is not defined
    QString = type("")
from  grabberFromPNG014 import grabberFromPNG

#from PyQt4.QtGui import QPainter, QColor, QPalette, QWidget
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QCloseEvent


class MyPreviewSentenceDLGWindow(QtGui.QMainWindow):
    MESSAGE = "<p>This is a sample info message! "

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
    uiSentencePreviewFileName = u'sentencePreview.ui'
    DBFileNameAndRelPath = ""

    prevSentenceDLG = None

    defGameID = 1 # SomiSE
    MI2GameID = 2
    selGameID = MI2GameID

    basedir = u"."
    icon = None

    def __init__(self, pselectedEncoding=None, pselectedGameID=None, pselectedFontFile=None):
        QtGui.QMainWindow.__init__(self)
        if getattr(sys, 'frozen', None):
            self.basedir = sys._MEIPASS
        else:
            self.basedir = os.path.dirname(__file__)
        self.DBFileNameAndRelPath = os.path.join(self.relPath,self.DBFileName)

        # Set up the user interface from Designer.
        uiSentencePreviewFilePath = os.path.join(self.relPath, self.uiFolderName, self.uiSentencePreviewFileName)
        #print uiFontDlgFilePath
        if not os.access(uiSentencePreviewFilePath, os.F_OK) :
            print "Could not find the required ui file %s for the Sentence Preview Dialogue." % (self.uiSentencePreviewFileName)
            return

        self.ui = uic.loadUi(uiSentencePreviewFilePath)
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
        ##self.ui.installEventFilter(self)

        self.native = True #can be used to control some native-to-OS or not dialogs being utilised (should be a checkbox)

        self.dasPixMap = None
        self.scene = QtGui.QGraphicsScene()
        self.ui.sentenceViewPngFont.setScene(self.scene)
        self.ui.sentenceViewPngFont.show()

        ## Connect up the buttons.
        self.ui.previewCustomTextBtn.clicked.connect(self.previewCustomText)
        self.ui.clearCustomTextBtn.clicked.connect(self.clearCustomText)
        return

##    def closeEvent(self, event):
##        reply = QtGui.QMessageBox.question(self, 'Quit Font Tool',
##            "Are you sure you want to close this dialogue window?", QtGui.QMessageBox.Yes |
##            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
##        if reply == QtGui.QMessageBox.Yes:
##            event.accept()
##            self.ui.closingFlag = True
##        else:
##            event.ignore()
##            self.ui.closingFlag = False

    def tryToCloseWin(self):
        self.ui.close()
        if __name__ == '__main__':
            sys.exit(0)
        return
##
##
##
    def previewCustomText(self):
        MyPreviewSentenceDLGWindow.MESSAGE = "Function not yet implemented!"
        self.informationMessage()
        return
##
##
##
    def clearCustomText(self):
        self.ui.customTextEdt.setText('')
        self.loadPngInGV()
##        MyPreviewSentenceDLGWindow.MESSAGE = "Function not yet implemented!"
##        self.informationMessage()
        return


##
##
##    def drawOutlinesForOriginGraphixView(self):
##        origFontFilename = self.ui.openOrigFontTxtBx.text().strip()
##        imageOriginalPNG = self.ui.openFileNameTxtBx.text().strip()
##
##        if  origFontFilename <> "" and imageOriginalPNG <> "":
##            if self.myGrabInstance is not None:
##                self.myGrabInstance.setDasOrigFontFilename(origFontFilename)
##                self.myGrabInstance.setImageOriginalPNG(imageOriginalPNG)
##                self.myGrabInstance.setGameID(self.selGameID)
##                self.myGrabInstance.setActiveEncoding(self.tryEncoding)
##                self.myGrabInstance.calcFromDB() # needed because of potential changes in GameId and Encoding!
##            else:
##                self.myGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID, origFontFilename, imageOriginalPNG)
##        else:
##            #print "Bad Arguments for outlining!"
##            errMsg = "Bad Arguments for outlining!"
##            MyPreviewSentenceDLGWindow.MESSAGE = errMsg
##            self.informationMessage()
##            return
##
##        if self.myGrabInstance is not None:
##            outlinesList = self.myGrabInstance.getLetterOutlines(True)
##            ##fileName = QString(self.ui.openFileNameTxtBx.text())
##            fileName = self.ui.openFileNameTxtBx.text()
##            self.paintOutlines(outlinesList, fileName)
##        return
####
####
####
##    def drawOutlinesForCopyinGraphixView(self):
##        origFontFilename =   self.ui.openOrigFontTxtBx.text().strip()
##        imageOriginalPNG = self.ui.openFileNameTxtBx.text().strip()
##
##        copyFontFileName = self.ui.OutputFontFileTxtBx.text().strip()
##        copyPNGFileName =  self.ui.OutputPngFileTxtBx.text().strip()
##
##        if  origFontFilename <> "" and  imageOriginalPNG  <> "" and copyFontFileName <> "" and copyPNGFileName <> "":
##            if self.myGrabInstance is not None:
##                self.myGrabInstance.setCopyFontFileName(copyFontFileName)
##                self.myGrabInstance.setCopyPNGFileName(copyPNGFileName)
##            else:
##                self.myGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID, origFontFilename,   imageOriginalPNG)
##                self.myGrabInstance.setCopyFontFileName(copyFontFileName)
##                self.myGrabInstance.setCopyPNGFileName(copyPNGFileName)
##        else:
##            #print "Bad Arguments for outlining!"
##            errMsg = "Bad Arguments for outlining!"
##            MyPreviewSentenceDLGWindow.MESSAGE = errMsg
##            self.informationMessage()
##            return
##
##        if self.myGrabInstance is not None:
##            outlinesList = self.myGrabInstance.getLetterOutlines(False)
##            ##fileName = QString(self.ui.OutputPngFileTxtBx.text())
##            fileName = self.ui.OutputPngFileTxtBx.text()
##            self.paintOutlines(outlinesList, fileName)
##        return
####
####
####
##    def paintOutlines(self, inputListmy, fileNameTxt):
####        MyPreviewSentenceDLGWindow.MESSAGE = "Ok now to paint!"
####        self.informationMessage()
##        # todo: optimize to reuse existing scene!!! or at least clean up
##        if self.scene is not None:
##            self.scene.clear()
##        self.dasPixMap = QtGui.QPixmap(fileNameTxt)
##        p = QPainter(self.dasPixMap)
###        p.setBackgroundColor(QColor("white"))
###        h = self.height()
###        w = self.width()
###        for i in range(1, h, h/5):
##        p.setPen(QColor("yellow"))
##        for i in range(0, len(inputListmy)):
##            (x1,y1, x2, y2, t1, t2, t3, chr0) = inputListmy[i]
##            p.drawLine(x1-1, y1-1, x1-1, y2-1)
##            p.drawLine(x1-1, y2-1, x2-1, y2-1)
##            p.drawLine(x2-1, y2-1, x2-1, y1-1)
##            p.drawLine(x2-1, y1-1, x1-1, y1-1)
##        self.scene.addPixmap(QtGui.QPixmap(self.dasPixMap))
##        self.ui.sentenceViewPngFont.setScene(self.scene)
##        self.ui.sentenceViewPngFont.show()
####        if self.dasPixMap is not None:
####            del self.dasPixMap
##        return
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
    def loadPngInGV(self, filenameTxt=None):
        # todo: code to clear an existing scene
        #
        if self.scene is not None:
            self.scene.clear()
#        self.scene = QtGui.QGraphicsScene()
        if filenameTxt is not None:
            self.scene.addPixmap(QtGui.QPixmap(filenameTxt))
        self.ui.sentenceViewPngFont.setScene(self.scene)
        self.ui.sentenceViewPngFont.show()
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
##    def loadCharPropertiesInTable(self, pTotalFontLetters):
##        if self.ui.charsInFontFileTblView.model() is not None:
##            self.ui.charsInFontFileTblView.model().clear()
##        self.ui.charsInFontFileTblView.clearSpans()
##
##        if self.myGrabInstance is not None:
##            outlinesList = self.myGrabInstance.getLetterOutlines(False)
##            # create table
##            lm = QStandardItemModel(pTotalFontLetters, 8, self)
##            lm.setHeaderData(0,Qt.Horizontal, u"Chr")
##            lm.setHeaderData(1,Qt.Horizontal, u"strX")
##            lm.setHeaderData(2,Qt.Horizontal, u"strY")
##            lm.setHeaderData(3,Qt.Horizontal, u"finX")
##            lm.setHeaderData(4,Qt.Horizontal, u"finY")
##            lm.setHeaderData(5,Qt.Horizontal, u"Indnt") #from left Indent in pixeld
##            lm.setHeaderData(6,Qt.Horizontal, u"Wid")
##            lm.setHeaderData(7,Qt.Horizontal, u"Kern")
##
##            for rowi in range(0,pTotalFontLetters):
##                index = lm.index(rowi, 0, QModelIndex())
##                if rowi < self.myGrabInstance.lettersInOriginalFontFile:
##                    lm.setData(index, unicode(str(outlinesList[rowi][7]),self.origEncoding))
##                else:
##                    lm.setData(index, unicode(str(outlinesList[rowi][7]),self.myGrabInstance.activeEncoding))
##                for columni in range(0,7):
##                    index = lm.index(rowi, columni+1, QModelIndex())
##                    # tmpRowStart[0], tmpColStart[0], tmpRowEnd[0], tmpColEnd[0], tmpPixelsWithinLetterBoxFromLeftToLetter[0], tmpWidthLetter[0], tmpKerningLetter[0]
##                    lm.setData(index, unicode(str(outlinesList[rowi][columni]),self.myGrabInstance.activeEncoding))
##            self.ui.charsInFontFileTblView.setModel(lm)
##        return

##
##
##
    def informationMessage(self):
        reply = QtGui.QMessageBox.information(self,
                "Information message", MyPreviewSentenceDLGWindow.MESSAGE)
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
                    MyPreviewSentenceDLGWindow.MESSAGE,
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
                    MyPreviewSentenceDLGWindow.MESSAGE,
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
                    "Warning", MyPreviewSentenceDLGWindow.MESSAGE,
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
## Load up the main window (instantiate an object of the MyPreviewSentenceDLGWindow class)
##
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyPreviewSentenceDLGWindow('windows-1253', 1)
    sys.exit(app.exec_())


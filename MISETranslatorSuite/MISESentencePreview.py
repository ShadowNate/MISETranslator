#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Created by Praetorian (ShadowNate) for Classic Adventures in Greek
# classic.adventures.in.greek@gmail.com
#

#
# TODO: add selection of background colors (similar to card catalogue, similar to generic MI background -> dark -blue-ish)
# TODO: background bould also be repeated images (??) <- low priority

import re
from struct import *
import sqlite3
import Image

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
from  grabberFromPNG014 import grabberFromPNG

#from PyQt4.QtGui import QPainter, QColor, QPalette, QWidget
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QCloseEvent


class MyPreviewSentenceDLGWindow(QtGui.QMainWindow):

    ##tryEncoding = 'windows-1253'
    greekEncoding = 'windows-1253'
    localGrabInstance = grabberFromPNG() # just for init purposes and getting the tryEncoding.
    tryEncoding = localGrabInstance.getTryEncoding()
    activeEnc = tryEncoding #unused here
    localGrabInstance = None

    origEncoding = 'windows-1252'
    localGrabInstance = None

    selOrigFontFile = None
    selOrigPngFile = None
    selCopyFontFile = None
    selCopyPngFile = None
    # consts
    ERROR_FONT_FILE_ARGS = -1
    ORIGINAL_FONT_FILE_ARGS = 0
    EXTENDED_FONT_FILE_ARGS =  1
    fontMode = ERROR_FONT_FILE_ARGS

    currentPath = u"" # for open or save files
    relPath = u'.'
    DBFileName = u'trampol.sqlite'
    uiFolderName = u'ui'
    uiSentencePreviewFileName = u'sentencePreview.ui'
    DBFileNameAndRelPath = ""

    prevSentenceDLG = None
    availBackgroundsLst = ( ( "Default Background", (131,166,235) ) ,\
                            ("Card Catalogue", (219,189,137))  ,\
                            ("Monkey Night Sky", (57,93,115) ) )

    englishPangramStr = u'The quick brown fox jumps over the lazy dog'
    # this will be used ONLY IF activeEnc == greekEncoding
    targetLangPangramStr = u'Τάχιστη αλώπηξ βαφής ψημένη γη, δρασκελίζει υπέρ νωθρού κυνός' # use it only if the default (greek encoding is used) (TODO: otherwise it should use a sentence from the DB or the overrideEncoding.txt file?)
    indexFromAsciiOrdToPngIndex = []
    listOfCharPngProperties = []

    defGameID = 1 # SomiSE
    MI2GameID = 2
    selGameID = MI2GameID

    basedir = u"."
    icon = None
    ui = None
    def __init__(self, custParent = None, pselectedEncoding=None, pselectedGameID=None, pselectedOrigFontFile=None, pselectedOrigPngFile = None,pselectedExtendedFontFile=None, pselectedExtendedPngFile=None):
        self.ui = None
        if custParent == None:
            QtGui.QMainWindow.__init__(self, custParent)
        else:
            QtGui.QMainWindow.__init__(self)
        if getattr(sys, 'frozen', None):
            self.basedir = sys._MEIPASS
        else:
            self.basedir = os.path.dirname(__file__)

        if pselectedEncoding is None or pselectedGameID is None or \
         ( (pselectedOrigFontFile is None or pselectedOrigFontFile == '' or pselectedOrigPngFile is None or pselectedOrigPngFile =='') \
            and \
            (pselectedExtendedFontFile is None or pselectedExtendedFontFile == '' or pselectedExtendedPngFile is None or pselectedExtendedPngFile =='') ):
            print "Invalid arguments were given for the initialization of preview Sentence dialogue"
            self.tryToCloseWin()
            return
        else:
            self.tryEncoding = pselectedEncoding
            self.selGameID = pselectedGameID
            self.selOrigFontFile = pselectedOrigFontFile
            self.selOrigPngFile = pselectedOrigPngFile
            self.selCopyFontFile = pselectedExtendedFontFile
            self.selCopyPngFile = pselectedExtendedPngFile


        self.DBFileNameAndRelPath = os.path.join(self.relPath,self.DBFileName)

        # Set up the user interface from Designer.
        uiSentencePreviewFilePath = os.path.join(self.relPath, self.uiFolderName, self.uiSentencePreviewFileName)
        #print uiFontDlgFilePath
        if not os.access(uiSentencePreviewFilePath, os.F_OK) :
            print "Could not find the required ui file %s for the Sentence Preview Dialogue." % (self.uiSentencePreviewFileName)
            self.tryToCloseWin()
            return

        self.ui = uic.loadUi(uiSentencePreviewFilePath)
        self.ui.show()

        if not os.access(self.DBFileNameAndRelPath, os.F_OK) :
            msgBoxesStub.qMsgBoxCritical(self.ui, "Database file missing!",\
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

        self.ui.backgroundSelectionCmbx.addItem(self.availBackgroundsLst[0][0])
        self.ui.backgroundSelectionCmbx.addItem(self.availBackgroundsLst[1][0])
        self.ui.backgroundSelectionCmbx.addItem(self.availBackgroundsLst[2][0])
        self.ui.backgroundSelectionCmbx.setCurrentIndex(0)

        self.dasPixMap = None
        self.scene = QtGui.QGraphicsScene()
        self.sceneBgBrush = QtGui.QBrush()
        self.sceneBgBrush.setStyle(QtCore.Qt.SolidPattern)
        #self.sceneBgBrush.setColor(QColor(self.availBackgroundsLst[0][1][0],self.availBackgroundsLst[0][1][1],self.availBackgroundsLst[0][1][2]))
        #self.scene.setBackgroundBrush(self.sceneBgBrush)
        self.ui.sentenceViewPngFont.setScene(self.scene)
        self.ui.sentenceViewPngFont.show()
        self.loadSelectedBGFromComboChanged(self.availBackgroundsLst[0][0])

        ## Connect up the buttons.
        self.ui.customTextEdt.setAcceptRichText(False)
        self.ui.previewCustomTextBtn.clicked.connect(self.previewCustomText)
        self.ui.clearCustomTextBtn.clicked.connect(self.clearCustomText)
        QtCore.QObject.connect(self.ui.backgroundSelectionCmbx, QtCore.SIGNAL("currentIndexChanged(const QString)"), self.loadSelectedBGFromComboChanged)

        self.localGrabInstance = grabberFromPNG(self.tryEncoding, self.selGameID)
        self.activeEnc = self.localGrabInstance.getActiveEncoding()

        self.fontMode = self.getFontModeFromFileParams()
        if self.fontMode == self.ERROR_FONT_FILE_ARGS:
            print "Could not detect font file status. Quiting"
            self.tryToCloseWin()
            return

        self.getIndexFromAsciiOrdToPngIndex()
        self.getListOfOutlinesInPng()


        self.showDefaultText()
        return

##    def closeEvent(self, event):
##        reply = msgBoxesStub.qMsgBoxQuestion(self.ui, 'Quit Font Tool',
##            "Are you sure you want to close this dialogue window?", QtGui.QMessageBox.Yes |
##            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
##        if reply == QtGui.QMessageBox.Yes:
##            self.ui.closingFlag = True
##            event.accept()
##        else:
##            event.ignore()
##            self.ui.closingFlag = False

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
    def loadSelectedBGFromComboChanged(self, selBgName):
        #print "lallala"
        #if self.scene is not None:
        #    self.scene.clear()
        #self.scene = QtGui.QGraphicsScene()
        foundSelBg = False
        #print selBgName
        for itemBg in self.availBackgroundsLst:
            #print itemBg[0]
            if(itemBg[0] == selBgName):
                foundSelBg = True
                break
        if foundSelBg:

            self.sceneBgBrush = QtGui.QBrush(QColor(itemBg[1][0],itemBg[1][1],itemBg[1][2]))
            #self.scene.setBackgroundBrush(self.sceneBgBrush)
            #self.ui.sentenceViewPngFont.setCacheMode(QtGui.QGraphicsView.CacheBackground)
            #self.ui.sentenceViewPngFont.setScene(self.scene)
            self.ui.sentenceViewPngFont.setBackgroundBrush(self.sceneBgBrush )
            self.ui.sentenceViewPngFont.show()
        return
##
##
##  Show the englishPangramStr and targetLangPangramStr in the image panel
    def showDefaultText(self):
        lettersToPrintLst = []
        del lettersToPrintLst[:]

        if self.listOfCharPngProperties is None or len(self.listOfCharPngProperties) <=0:
            #print "No items detected as drawn characters!"
            msgBoxesStub.qMsgBoxInformation(self.ui, "Info", "No items detected as drawn characters!")
            return
        #print "Active Encoding: %s. Game mode %d" % (self.activeEnc,self.selGameID)

        stringsList = []
        del stringsList [:]
        stringsList.append(self.englishPangramStr)
        if self.activeEnc == self.greekEncoding:
            stringsList.append(self.targetLangPangramStr)
        if self.ui.customTextEdt.toPlainText().strip() != '':
            stringsList.append(self.ui.customTextEdt.toPlainText().strip() )

        for tokenString in stringsList:
            myASCIIString = unicode.encode("%s" % tokenString, self.activeEnc)
            myLstChars = self.makeStringIntoModifiedAsciiCharlistToBeWritten(myASCIIString, self.localGrabInstance)

            for asciiChar in myLstChars:
                if asciiChar == '\x00' or asciiChar == '\x0a':
                    #print "EOS"
                    lettersToPrintLst.append((-1,-1,-1,-1,-1,-1,-1, '\x00')) ## should be used as special case to print new line in the preview screen!
                else:
                    if(self.pngIndexOfCharCode(asciiChar) < len(self.listOfCharPngProperties)):
                        #print (asciiChar, ord(asciiChar), self.pngIndexOfCharCode(asciiChar), self.listOfCharPngProperties[self.pngIndexOfCharCode(asciiChar)] )
                        lettersToPrintLst.append(self.listOfCharPngProperties[self.pngIndexOfCharCode(asciiChar)])
                    else:
                        #print (asciiChar, ord(asciiChar), 0, self.listOfCharPngProperties[0] )
                        lettersToPrintLst.append(self.listOfCharPngProperties[0] )

        self.printInPreviewScreen(lettersToPrintLst)
        return
##
##
##
    def printInPreviewScreen(self, lettersToPrintLst):
        if self.scene is not None:
            self.scene.clear()

        lineSpacingInPx = 60 # TODO should be font size dependent
        currentLineNumber = 1 # multiply by lineSpacing to get baseline (horizontal) for the current printing line
        startingTopColPerLinePx = 0
        colTopToContinuePx = startingTopColPerLinePx ## pixels
        rowTopToContinuePx = (currentLineNumber - 1)*lineSpacingInPx ## pixels
        ## get from origPNG or copyPNG (depending on detected font mode) the specified letters from the dimension/delimiters in the lettersToPrintLst list param.
        ## and present them as they should be based on Baseline and spacing/positioning characteristics.
        pngfile = ''
        if self.fontMode == self.EXTENDED_FONT_FILE_ARGS:
            pngfile = self.selCopyPngFile
        elif self.fontMode == self.ORIGINAL_FONT_FILE_ARGS:
            pngfile = self.selOrigPngFile

        im = None
        errorFound = False
        if os.access(pngfile, os.F_OK) :
            try:
                ##print pngfile
                im = Image.open(pngfile)
            except:
                errMsg = "Could not open appropriate png font file!"
                print "Unexpected error:", sys.exc_info()[0]
                print errMsg
                errorFound = True
        else:
            errMsg = "Could not access appropriate png font file!"
            print errMsg
            errorFound = True

        if not errorFound:
            ##debug
            #print pngfile, im.format, "%dx%d" % im.size, im.mode
            w1, h1 = im.size
            # we need  an in-mem image!!

            #pre-process to calculate max width
            maxWidthPx = 0
            maxHeightPx = 0
            for letterToPrintItem in lettersToPrintLst:
                tmpColStart= letterToPrintItem[0]
                tmpRowStart  = letterToPrintItem[1]
                tmpColEnd = letterToPrintItem[2]
                tmpRowEnd = letterToPrintItem[3]
                tmpPixelsWithinLetterBoxFromLeftToLetter = letterToPrintItem[4]
                tmpWidthLetter = letterToPrintItem[5]
                tmpKerningLetter = letterToPrintItem[6]
                tmpChar = letterToPrintItem[7]

                if tmpChar == '\x00': #End of String - change line
                    currentLineNumber +=1
                    colTopToContinuePx = startingTopColPerLinePx ## pixels
                    rowTopToContinuePx = (currentLineNumber - 1)*lineSpacingInPx ## pixels
                    if maxHeightPx < (rowTopToContinuePx + lineSpacingInPx):
                        maxHeightPx = (rowTopToContinuePx + lineSpacingInPx)
                else:
                    colTopToContinuePx += tmpPixelsWithinLetterBoxFromLeftToLetter
                    colTopToContinuePx += tmpKerningLetter
                    rowTopToContinuePx = (currentLineNumber - 1)*lineSpacingInPx ## pixels
                    if maxWidthPx < colTopToContinuePx:
                        maxWidthPx = colTopToContinuePx

            imPreviewSentence = Image.new(im.mode,(maxWidthPx+10, maxHeightPx+10), (0,0,0,0)) # width,height. Should be automatically optimized to (calculated) size of largest sentence!

            currentLineNumber = 1 # multiply by lineSpacing to get baseline (horizontal) for the current printing line
            colTopToContinuePx = startingTopColPerLinePx ## pixels
            rowTopToContinuePx = (currentLineNumber - 1)*lineSpacingInPx ## pixels
            for letterToPrintItem in lettersToPrintLst:
                tmpColStart= letterToPrintItem[0]
                tmpRowStart  = letterToPrintItem[1]
                tmpColEnd = letterToPrintItem[2]
                tmpRowEnd = letterToPrintItem[3]
                tmpPixelsWithinLetterBoxFromLeftToLetter = letterToPrintItem[4]
                tmpWidthLetter = letterToPrintItem[5]
                tmpKerningLetter = letterToPrintItem[6]
                tmpChar = letterToPrintItem[7]

                if tmpChar == '\x00': #End of String - change line
                    currentLineNumber +=1
                    colTopToContinuePx = startingTopColPerLinePx ## pixels
                    rowTopToContinuePx = (currentLineNumber - 1)*lineSpacingInPx ## pixels
                else:
                    # TODO to be moved in grabber module???
                    colTopToContinuePx += tmpPixelsWithinLetterBoxFromLeftToLetter
                    ##charSubImage = im.crop((tmpColStart+1, tmpRowStart+1, tmpColEnd+2, tmpRowEnd+2))
                    charSubImage = im.crop((tmpColStart, tmpRowStart, tmpColEnd + 1, tmpRowEnd+1))

                    maskSubImage = charSubImage
##                    maskW1, maskH1 = maskSubImage.size
##                    pix = maskSubImage.load()
##                    # we need to set every non completely transparent pixel of the mask to complete opaque and white.
##                    for x in range(0, maskW1):
##                        for y in range(0, maskH1):
##                            r1,g1,b1,a1 = pix[x, y]
##                            if a1 != 0: # if not completely transparent
##                                pix[x, y] = r1, g1, b1, 0xff # set it to completely opaque
##
##                    #maskSubImage.putdata(pix) # not needed. The data is altered!

                    ##print   charSubImage
                    charPositionCoords = (colTopToContinuePx,
                                            rowTopToContinuePx,
                                            colTopToContinuePx + 1 + tmpColEnd - tmpColStart,
                                            rowTopToContinuePx + 1 + tmpRowEnd - tmpRowStart )
                    #print tmpChar, (tmpColStart, tmpRowStart, tmpColEnd+1, tmpRowEnd+1), charPositionCoords
                    # 3rd paste option is a mask to keep the transparency (we use the same image as mask).
                    imPreviewSentence.paste(charSubImage, charPositionCoords, maskSubImage)
                    colTopToContinuePx += tmpKerningLetter
                    rowTopToContinuePx = (currentLineNumber - 1)*lineSpacingInPx ## pixels

            imPreviewSentenceData = imPreviewSentence.tostring('raw', 'RGBA')
            qimagePreviewSentence = QImage(imPreviewSentenceData, imPreviewSentence.size[0], imPreviewSentence.size[1], QImage.Format_ARGB32)
            self.dasPixMap = QtGui.QPixmap.fromImage(qimagePreviewSentence)

            self.scene.addPixmap(QtGui.QPixmap(self.dasPixMap))
            self.ui.sentenceViewPngFont.setScene(self.scene)
            self.ui.sentenceViewPngFont.show()

        return

##
##
##
    def previewCustomText(self):
        if self.ui.customTextEdt.toPlainText().strip() == '':
            return
        else:
            self.showDefaultText()
        return
##
##
##
    def clearCustomText(self):
        self.ui.customTextEdt.setText('')
        ##self.loadPngInGV()
        self.showDefaultText()
##        msgBoxesStub.qMsgBoxInformation(self.ui, "Not yet implemented", "Function not yet implemented!")
        return


####
####
####
##    def paintOutlines(self, inputListmy, fileNameTxt):
####        msgBoxesStub.qMsgBoxInformation(self.ui, "Debug", "Ok now to paint!")
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
##        if self.localGrabInstance is not None:
##            outlinesList = self.localGrabInstance.getLetterOutlines(False)
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
##                if rowi < self.localGrabInstance.lettersInOriginalFontFile:
##                    lm.setData(index, unicode(str(outlinesList[rowi][7]),self.origEncoding))
##                else:
##                    lm.setData(index, unicode(str(outlinesList[rowi][7]),self.localGrabInstance.activeEncoding))
##                for columni in range(0,7):
##                    index = lm.index(rowi, columni+1, QModelIndex())
##                    # tmpRowStart[0], tmpColStart[0], tmpRowEnd[0], tmpColEnd[0], tmpPixelsWithinLetterBoxFromLeftToLetter[0], tmpWidthLetter[0], tmpKerningLetter[0]
##                    lm.setData(index, unicode(str(outlinesList[rowi][columni]),self.localGrabInstance.activeEncoding))
##            self.ui.charsInFontFileTblView.setModel(lm)
##        return
##
##
##
    # should not be ran often, since this is not expected to change
    # -1 error (ERROR_FONT_FILE_ARGS)
    # 0 original (ORIGINAL_FONT_FILE_ARGS)
    # 1 extended (EXTENDED_FONT_FILE_ARGS)
    def getFontModeFromFileParams(self):
        errorFound = False
        retVal = self.ERROR_FONT_FILE_ARGS
        # by priority first get the extended files if available (then fallback to originals)
        if  self.selCopyFontFile is not None and  self.selCopyFontFile <> ""  and  self.selCopyPngFile  is not None and  self.selCopyPngFile:
            self.localGrabInstance.setCopyFontFileName(self.selCopyFontFile)
            self.localGrabInstance.setCopyPNGFileName(self.selCopyPngFile)
            retVal = self.EXTENDED_FONT_FILE_ARGS
        elif self.selOrigFontFile is not None and  self.selOrigFontFile <> ""  and  self.selOrigPngFile  is not None and  self.selOrigPngFile:
            self.localGrabInstance.setDasOrigFontFilename(self.selOrigFontFile)
            self.localGrabInstance.setImageOriginalPNG(self.selOrigPngFile)
            retVal = self.ORIGINAL_FONT_FILE_ARGS
        else:
            errorFound = True
            msgBoxesStub.qMsgBoxCritical(self.ui, "Error", "No valid file for characters drawing!")
            retVal = self.ERROR_FONT_FILE_ARGS
        return retVal

    # should not be ran often, since this is not expected to change
    def getListOfOutlinesInPng(self):
        del self.listOfCharPngProperties[:]
        if self.fontMode == self.EXTENDED_FONT_FILE_ARGS:
            self.listOfCharPngProperties = self.localGrabInstance.getLetterOutlines(False)
        elif self.fontMode == self.ORIGINAL_FONT_FILE_ARGS:
            self.listOfCharPngProperties = self.localGrabInstance.getLetterOutlines(True)
        return
##
##
##
    # should not be ran often, since this is not expected to change
    def getIndexFromAsciiOrdToPngIndex(self):
        if self.fontMode == self.EXTENDED_FONT_FILE_ARGS:
            fontfile = self.selCopyFontFile
        elif self.fontMode == self.ORIGINAL_FONT_FILE_ARGS:
            fontfile = self.selOrigFontFile
        # start from position 0x1a and read 256 words (2-bytes). (Sanity Check 0x20 char should be the space char)
        del self.indexFromAsciiOrdToPngIndex[:]
        retVal = None
        startPosOfAsciiSlotsTable = 0x1a
        if os.access(fontfile, os.F_OK) :
            try:
                openedFontFile = open(fontfile, 'rb')
                openedFontFile.seek(startPosOfAsciiSlotsTable)
                for asciiOrd in range(0,256):
                    tmpIntReadTuple = unpack('h',openedFontFile.read(2))    # unpack always returns a tuple
                    self.indexFromAsciiOrdToPngIndex.append(tmpIntReadTuple[0])
                openedFontFile.close()
                retVal = self.indexFromAsciiOrdToPngIndex
                ##print "########################\n########################\n########################"
                ##print retVal
                ##print "########################\n########################\n########################"
                return retVal
            except:
                print "Unexpected error:", sys.exc_info()[0]
                errorFound = True
                return retVal
        else:
            print "Font file not found!"
            errorFound = True
            return retVal


    # TODO This method could be moved in the grabber module!
    # This method is similar to pngIndexOfForeignLetter (from grabber module), but this one uses the actual 'char' that is written in the font file.
    # It will have to search in the given font file to find the png index of the given char code.
    # should return 0 if error or not Found
    # The png Index of '0' (first) is the [] (rectangle) character that is displayed when an unknown char is detected in the game text.
    # The png Index of '1' is the white space ' '
    def pngIndexOfCharCode(self, pByteCode):
        unkownCharFoundVal = 0
        endOfStringNullChar = -1
        errorFound = False
        if self.indexFromAsciiOrdToPngIndex is not None and ord(pByteCode) < len(self.indexFromAsciiOrdToPngIndex):
            ##print ord(pByteCode)
            if pByteCode == '\x00' or pByteCode == '\x0a':
                return endOfStringNullChar
            else:
                return self.indexFromAsciiOrdToPngIndex[ord(pByteCode)]
        else:
            errorFound = True
        if errorFound:
            return unkownCharFoundVal



    #
    # This method is copied from the MISEDialogTranslate module.
    # TODO It should probably be unified and moved in the grabber module!
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
        ##print "START OF translatedTextAsCharsList2: "
        ##print translatedTextAsCharsList2
        ##print "END OF translatedTextAsCharsList2"
        return translatedTextAsCharsList2

##
## Load up the main window (instantiate an object of the MyPreviewSentenceDLGWindow class)
##
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    fontExtendedfileRelPath= os.path.join(u'.', u'test', u'MISE_MinisterT_b_32-orig_1.font')
    pngExtendedfileRelPath= os.path.join(u'.', u'test', u'MISE_MinisterT_b_32-origExpanded.png')
    # origFontFilename, imageOriginalPNG, copyFontFileName, copyPNGFileName)
    origFontFilename = None
    imageOriginalPNG = None
    copyFontFileName = fontExtendedfileRelPath
    copyPNGFileName = pngExtendedfileRelPath
    window = MyPreviewSentenceDLGWindow(None, 'windows-1253', 1, origFontFilename, imageOriginalPNG, copyFontFileName, copyPNGFileName)
    sys.exit(app.exec_())


#-------------------------------------------------------------------------------
# Name:        tableViewTextDocDelegate
#-------------------------------------------------------------------------------
##import sip
##sip.setapi('QString', 2)
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import highlightRulesGlobal


class TextDocDelegate(QStyledItemDelegate):
    font = QtGui.QFont()
    moreFont = QtGui.QFont()
    def __init__(self):
        super(TextDocDelegate, self).__init__()
        self.font = QtGui.QFont()
        self.font.setFamily('Arial')
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)
        self.moreFont = QtGui.QFont()
        self.moreFont.setFamily('Arial')
        self.moreFont.setFixedPitch(True)
        self.moreFont.setPointSize(8)
        self.moreFont.setWeight(QFont.Bold)

    # override displayText, since otherwise we get duplicates with Paint-ed QTextDocument (which we need for the highlighting)
    def displayText(self, value, locale):
        text = ""
        return text

    def createEditor(self, parent, option, index):
        ## Just creates a plain line edit.
        #editor = QLineEdit(parent)

        ##editor.setAcceptRichText(True)
        ##editor.setReadOnly(False)
        ##editor.setGeometry(option.rect);
        ##sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        ##editor.setSizePolicy(sizePolicy);
        #font = QtGui.QFont()
        #font.setFamily('Arial')
        #font.setFixedPitch(True)
        #font.setPointSize(10)

        editor = QtGui.QTextEdit(parent)
        editor.setFont(self.font)

        self.highlighter = Highlighter(editor.document(), index.column())

        return editor

    def paint(self, painter, option, index):
        if option is None or index is None or painter is None:
            return
        else:
            painter.save()
            ##default = QStyledItemDelegate.sizeHint(self, option, index)
            ##print "painter option" , (option.rect.x(),option.rect.y(), default.width(), default.height())
            ##painter.drawRect(option.rect)
            QStyledItemDelegate.paint(self, painter, option, index)
            text = index.model().data(index, Qt.DisplayRole).toString()
            doc = QTextDocument()
            doc.setPlainText(text)
            doc.adjustSize()
            doc.setDefaultFont(self.font)
            doc.setDocumentMargin(3)

            docTextOption = QTextOption()
            docTextOption.setAlignment(Qt.AlignVCenter)

            doc.setDefaultTextOption(docTextOption)
#            FilterSyntaxHighlighter* highlighter = new FilterSyntaxHighlighter(regExp, doc);
            highlighter = Highlighter(doc, index.column())
            highlighter.rehighlight()

            #QAbstractTextDocumentLayout :: PaintContext context;
            context = QtGui.QAbstractTextDocumentLayout.PaintContext();

            doc.setPageSize(QSizeF ( option.rect.size()))
            #painter.setClipRect(option.rect);
            docuRect, hasMore = self.getTextDocumentRect(option, doc)

            painter.setClipRect(docuRect);
            painter.translate( docuRect.x(), docuRect.y() )
            doc.documentLayout().draw(painter,context)
            painter.restore()
            painter.save()
            if hasMore:
                #print "Has More", index.row(), index.column()
                docMoreNote = QTextDocument()
                docMoreNote.setPlainText("...")
                docMoreNote.adjustSize()
                docMoreNote.setDefaultFont(self.moreFont)
                docMoreNote.setDocumentMargin(1)
                docMoreNote.setPageSize(QSizeF ( docMoreNote.size()))
                docuCornerRect, hasMore = self.getCornerTextDocumentRect(option, docMoreNote)
                painter.setClipRect(docuCornerRect);
                painter.translate( docuCornerRect.x(), docuCornerRect.y() )
                docMoreNote.documentLayout().draw(painter,context)

            painter.restore()

    def getCornerTextDocumentRect(self, option, cornerDocu):
        hasMore = False
        docu_point = None
        docu_croppedSize = None
        if cornerDocu.size().toSize().height() <= option.rect.height() :
            docu_point = QPoint (option.rect.x() + option.rect.width() - cornerDocu.size().toSize().width(),
            					 option.rect.y() +
            					 (option.rect.height()  - cornerDocu.size().toSize().height()))
            docu_croppedSize= QSize(cornerDocu.size().toSize().width(), cornerDocu.size().toSize().height()  ) #width, height
        else:
            docu_point = QPoint (option.rect.x() + option.rect.width() - cornerDocu.size().toSize().width(), option.rect.y())
            docu_croppedSize = (cornerDocu.size().toSize().width(), option.rect.height() )
            hasMore = True
        return QRect(docu_point, docu_croppedSize), hasMore

    def getTextDocumentRect(self, option, textDocu):
        hasMore = False
        docu_point = None
        docu_croppedSize = None
        if textDocu.size().toSize().height() <= option.rect.height() :
            docu_point = QPoint (option.rect.x(),
            					 option.rect.y() +
            					 (option.rect.height()  - textDocu.size().toSize().height()) / 2)
            docu_croppedSize= QSize(textDocu.size().toSize().width(), (option.rect.height()  + textDocu.size().toSize().height()) / 2 ) #width, height
        else:
            docu_point = QPoint (option.rect.x(),option.rect.y())
            docu_croppedSize = QSize(option.rect.width(), option.rect.height() )
            hasMore = True
        return QRect(docu_point, docu_croppedSize), hasMore

        ##print "something"
##
##    def sizeHint(self, option, index):
##        default = QStyledItemDelegate.sizeHint(self, option, index)
##        print "size hint option" , (option.rect.x(),option.rect.y(), default.width(), default.height())
##        return QSize(default.width(), default.height())

    def setEditorData(self, editor, index):
    # Fetch current data from model.
        value = index.model().data(index, Qt.DisplayRole).toString();
        #print value
##        valueDato = index.model().data(index, Qt.EditRole).toPyObject();
##        print valueDato
        ## Set line edit text to current data.
        #editor.setText(value)
        ## Deselect text. (lineEdit)
        #editor.deselect();
        ## Move the cursor to the beginning. (lineEdit)
        #editor.setCursorPosition(0);
        editor.setPlainText(value)

    def setModelData(self, editor, model, index):
    # Set the model data with the text in line edit.
        #model.setData(index, QVariant(editor.text()), Qt.EditRole); # ;lineEdit
        if index.column() > 0:   # first column won't be edited!
            model.setData(index, QVariant(editor.toPlainText()), Qt.EditRole); # ;lineEdit


    def updateEditorGeometry(self, editor, option, index):
        #print (option.rect.x(),option.rect.y(),editor.sizeHint().width(),editor.sizeHint().height())
        editor.setGeometry(option.rect)
        return


class HighlightingRule:
    pass

class Highlighter(QtGui.QSyntaxHighlighter):

    parentColNumber = -1
    def __init__(self, parent=None, pParntColNum=-1):
        super(Highlighter, self).__init__(parent)
        highlightRulesGlobal.addHighlighterWatcher(self)
        self.parentColNumber = pParntColNum
        self.multiLineCommentFormat = QtGui.QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QtCore.Qt.red)
        self.commentStartExpression = QtCore.QRegExp("/\\*")
        self.commentEndExpression = QtCore.QRegExp("\\*/")

    def highlightBlock(self, text):
        #print "checking hight"
        for pattern, format, forColumnNum in highlightRulesGlobal.getAllHighlightRules():
            if(self.parentColNumber == forColumnNum or forColumnNum==-1 ):
                expression = QtCore.QRegExp(pattern)
                index = expression.indexIn(text)
                while index >= 0:
                    length = expression.matchedLength()
                    self.setFormat(index, length, format)
                    index = expression.indexIn(text, index + length)

##        self.setCurrentBlockState(0)
##
##        startIndex = 0
##        if self.previousBlockState() != 1:
##            startIndex = self.commentStartExpression.indexIn(text)
##
##        while startIndex >= 0:
##            endIndex = self.commentEndExpression.indexIn(text, startIndex)
##
##            if endIndex == -1:
##                self.setCurrentBlockState(1)
##                commentLength = len(text) - startIndex
##            else:
##                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
##
##            self.setFormat(startIndex, commentLength,
##                    self.multiLineCommentFormat)
##            startIndex = self.commentStartExpression.indexIn(text,
##                    startIndex + commentLength);

def main():
    pass

if __name__ == '__main__':
    main()

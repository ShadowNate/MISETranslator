#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#!/usr/bin/env python
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#
# MESSAGEBOX FUNCTIONS
#
def qMsgBoxQuestion(parentWidg, titleMsgBx, messageMsgBx, buttonFlagsMsgBxm = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, defaultBtnMsgBx = QtGui.QMessageBox.No):
    qmsgParent = None
    if(parentWidg is not None):
        qmsgParent = parentWidg
    reply = defaultBtnMsgBx
    try:
        reply = QtGui.QMessageBox.question(qmsgParent, titleMsgBx, messageMsgBx, buttonFlagsMsgBxm, defaultBtnMsgBx)
    except:
        parentScreen = QtGui.QApplication.desktop().screen(QtGui.QApplication.desktop().primaryScreen())
        qmsgParent = QtGui.QMainWindow(parentScreen)
        reply = QtGui.QMessageBox.question(qmsgParent, titleMsgBx, messageMsgBx, buttonFlagsMsgBxm, defaultBtnMsgBx)
    return reply

def qMsgBoxCritical(parentWidg, titleMsgBx, messageMsgBx, buttonFlagsMsgBxm = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default, defaultBtnMsgBx = QtGui.QMessageBox.NoButton ):
    qmsgParent = None
    if(parentWidg is not None):
        qmsgParent = parentWidg
    reply = defaultBtnMsgBx
    try:
        reply = QtGui.QMessageBox.critical(qmsgParent, titleMsgBx, messageMsgBx, buttonFlagsMsgBxm, defaultBtnMsgBx)
    except:
        parentScreen = QtGui.QApplication.desktop().screen(QtGui.QApplication.desktop().primaryScreen())
        qmsgParent = QtGui.QMainWindow(parentScreen)
        reply = QtGui.QMessageBox.critical(qmsgParent, titleMsgBx, messageMsgBx, buttonFlagsMsgBxm, defaultBtnMsgBx)
    return reply


def qMsgBoxInformation(parentWidg, titleMsgBx, messageMsgBx):
    qmsgParent = None
    if(parentWidg is not None):
        qmsgParent = parentWidg
    reply = QtGui.QMessageBox.Ok
    try:
        reply = QtGui.QMessageBox.information(qmsgParent, titleMsgBx, messageMsgBx)
    except:
        parentScreen = QtGui.QApplication.desktop().screen(QtGui.QApplication.desktop().primaryScreen())
        qmsgParent = QtGui.QMainWindow(parentScreen)
        reply = QtGui.QMessageBox.information(qmsgParent, titleMsgBx, messageMsgBx)
    return reply

def qMsgBoxAbout(parentWidg, titleMsgBx, messageMsgBx):
    qmsgParent = None
    if(parentWidg is not None):
        qmsgParent = parentWidg
    reply = QtGui.QMessageBox.Ok
    try:
        reply = QtGui.QMessageBox.about(qmsgParent, titleMsgBx, messageMsgBx)
    except:
        parentScreen = QtGui.QApplication.desktop().screen(QtGui.QApplication.desktop().primaryScreen())
        qmsgParent = QtGui.QMainWindow(parentScreen)
        reply = QtGui.QMessageBox.about(qmsgParent, titleMsgBx, messageMsgBx)
    return reply

def qMsgBoxWarning(parentWidg, titleMsgBx, messageMsgBx):
    qmsgParent = None
    if(parentWidg is not None):
        qmsgParent = parentWidg
    reply = QtGui.QMessageBox.Ok
    try:
        reply = QtGui.QMessageBox.warning(qmsgParent, titleMsgBx, messageMsgBx)
    except:
        parentScreen = QtGui.QApplication.desktop().screen(QtGui.QApplication.desktop().primaryScreen())
        qmsgParent = QtGui.QMainWindow(parentScreen)
        reply = QtGui.QMessageBox.warning(qmsgParent, titleMsgBx, messageMsgBx)
    return reply


def main():
    pass

if __name__ == '__main__':
    main()

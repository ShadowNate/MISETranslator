from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#
# For a checkbox (only and not text) in TableView columns.
#
class CheckBoxDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        '''
        Important, otherwise an editor is created if the user clicks in this cell.
        '''
        return None

    def paint(self, painter, option, index):
        '''
        Paint a checkbox without the label.
        '''
##        print "repaint!"
        ## disconnect the itemchanged signal
        ##index.model().disconnect( index.model(), QtCore.SIGNAL('itemChanged( QStandardItem *)'), None, None)

        checked = index.model().data(index, Qt.DisplayRole).toBool()
        if checked is None or option is None or index is None or painter is None:
            return

        check_box_style_option = QStyleOptionButton()
##        #print "%d %d %2x %2x" % (index.column(), index.row() ,int(index.flags()), Qt.ItemIsEditable)

        check_box_style_option.state |= QStyle.State_Enabled

        if int((index.flags()) & Qt.ItemIsEditable) > 0:
            check_box_style_option.state |= QStyle.State_Enabled
        else:
            check_box_style_option.state |= QStyle.State_ReadOnly

        if checked == True:
            check_box_style_option.state |= QStyle.State_On
        else:
            check_box_style_option.state |= QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)
##        prvBlockState = index.model().blockSignals(True)
        if checked == True:
            #QtCore.QVariant(QtGui.QBrush(QtGui.QColor(QtCore.Qt.green)))
            if index.column() == 2: #do it only for the "pending" column, not for the "changed"
                for tmpColumn in range(0, index.model().columnCount()):
    #                tmpItem = index.model().itemFromIndex(index)
                    ##print (tmpColumn, index.model().columnCount())
                    if  (index.row() % 2) > 0 :
                        index.model().item(index.row(),tmpColumn).setBackground(QBrush(QColor(230,250,137)))
    #                    index.model().setData(index,QBrush(QColor(255,0,0)), Qt.BackgroundRole)
                    else:
                        index.model().item(index.row(),tmpColumn).setBackground(QBrush(QColor(234,254,141)))
                # handle this cell
                if  (index.row() % 2) > 0 :
                    painter.fillRect(option.rect, QColor(230,250,137))
                else:
                    painter.fillRect(option.rect, QColor(234,254,141))
            elif index.column() == 4: # we need to also mark the conflicting checkbox (not the row)
                if  (index.row() % 2) > 0 :
                    painter.fillRect(option.rect, QColor(153,144,120))
                else:
                    painter.fillRect(option.rect, QColor(160,152,130))



#                    index.model().setData(index, QColor().setNamedColor("#000000"), Qt.BackgroundRole)
#        tmpBrush = painter.background()
#        painter.setBackgroundMode(Qt.OpaqueMode)
#        painter.setBackground(QBrush(QColor(255,0,0)))
##        index.model().blockSignals(prvBlockState)
        QApplication.style().drawControl(QStyle.CE_CheckBox, check_box_style_option, painter)
#        painter.setBackground (tmpBrush)
#                tmpItem = QStandardItem()
#                if columni == 3:
#                    tmpItem.setEditable(False)
#                    tmpItem.setCheckable(False)
#                    tmpItem.setEnabled(False)
#                    index.model().setData(index, False, Qt.EditRole)) # TODO: fill in from saved file (comparisn with original file)

#            for tmpColumn in range(0, index.model.columnCount()):
#                index.column(),index.row()
#                QTableWidgetItem *newItem = new QTableWidgetItem(tr("%1").arg((row+1)*(column+1)));
#                newItem->setData(Qt::BackgroundRole, (row % 2)>0 ? QtCore.Qt.yellow : QtCore.Qt.blue);
#                ui->tableWidget->setItem(row, column, newItem);


    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        '''
        if event is None or model is None or index is None or option is None:
            return

        if not (int((index.flags()) & Qt.ItemIsEditable)) > 0:
            return True

        # Do not change the checkbox-state
        if event.type() == QEvent.MouseButtonRelease: #or event.type() == QEvent.MouseButtonDblClick:
            if event.button() != Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return True
            if event.type() == QEvent.MouseButtonDblClick:
                return True
#        	   pass # CHECK IF IT WAS THE LEFT CLICK!
        elif event.type() == QEvent.KeyPress:
            if event.key() != Qt.Key_Space and event.key() != Qt.Key_Select:
                return True
        else:
            return True
        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True

    def setModelData(self, editor, model, index):
        '''
        The user wanted to change the old state in the opposite.
        '''
        newValue = not index.model().data(index, Qt.DisplayRole).toBool()

        model.setData(index, newValue, Qt.EditRole)

        #since the value has changed, clear the color for "False" value
        if newValue == False:
            origColor= index.model().parent().palette().color(QPalette.Base)
            if  (index.row() % 2) > 0:
                origColor= index.model().parent().palette().color(QPalette.AlternateBase)
            for tmpColumn in range(0, index.model().columnCount()):
                index.model().item(index.row(),tmpColumn).setBackground(origColor)
#        print "%d %d %s" % (index.column(),index.row(),  str(newValue))
#        print "%d %d %s EdDispl" % (index.column(),index.row(),  str(bool(index.model().data(index, Qt.DisplayRole))))

    def getCheckBoxRect(self, option):
        check_box_style_option = QStyleOptionButton()
        check_box_rect = QApplication.style().subElementRect(QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QPoint (option.rect.x() +
        					 option.rect.width() / 2 -
        					 check_box_rect.width() / 2,
        					 option.rect.y() +
        					 option.rect.height() / 2 -
        					 check_box_rect.height() / 2)
        return QRect(check_box_point, check_box_rect.size())
#
# END OF CLASS FOR CHECKBOX DELEGATE in TABLE VIEW
#
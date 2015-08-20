#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui
from UI_form import Ui_Form
from UI_edit import Ui_Dialog
from mysql.connector import (connection)
from mysql.connector import errorcode, Error
from settings import settings


class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.connect_db)
        self.ui.lineEdit.returnPressed.connect(self.ui.pushButton.click)
        self.ui.tableWidget.cellDoubleClicked.connect(self.edit_item)
        self.center()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    #@QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def edit_item(self, row, column):
        self.vals=[]
        email = self.ui.tableWidget.item(row,0).text()
        dtf = self.ui.tableWidget.item(row,1).text()
        serial = self.ui.tableWidget.item(row,2).text()
        date = QtCore.QDate(int(dtf[:4]), int(dtf[5:7]), int(dtf[8:10]))
        self.vals.append(str(email))
        self.vals.append(date)
        self.vals.append(serial)
        self.edit = EditDialog(self.vals)
        self.edit.show()

    def connect_db(self):
        try:
            cnx = connection.MySQLConnection(
                user=settings['user'],
                password=settings['password'],
                host=settings['host'],
                database=settings['database']
            )
            cursor = cnx.cursor()
            mail_to_search = '%' + self.ui.lineEdit.text() + '%'
            query = (
                "SELECT user_mail, license_end, serial_number FROM serials WHERE user_mail LIKE '%s' ORDER BY id"
                ) % mail_to_search
            cursor.execute(query)
            fetchall = cursor.fetchall()
            self.ui.tableWidget.setColumnCount(3)
            self.ui.tableWidget.setRowCount(cursor.rowcount)
            self.ui.tableWidget.setHorizontalHeaderLabels(["E-mail", "Licencja", "Serial"])
            self.ui.tableWidget.setColumnWidth(0, 300)
            self.ui.tableWidget.setColumnWidth(1, 151)
            self.ui.tableWidget.setColumnWidth(2, 250)
            for idx, (user_mail, license_end, serial_number) in enumerate(fetchall):
                self.ui.tableWidget.setItem(idx,0,QtGui.QTableWidgetItem(user_mail))
                self.ui.tableWidget.setItem(idx,1,QtGui.QTableWidgetItem(str(license_end)))
                self.ui.tableWidget.setItem(idx,2,QtGui.QTableWidgetItem(serial_number))
            cursor.close()

        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        finally:
            cnx.close()


class EditDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, vals, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.vals=vals
        self.setupUi(self)
        self.label.setText(self.vals[0])
        self.dateEdit_2.setDate(self.vals[1])
        self.serial_label.setText(self.vals[2])
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.ok_clicked)
        QtCore.QObject.connect(self.delButton, QtCore.SIGNAL("clicked()"), self.del_clicked)


    def ok_clicked(self):
        try:
            cny = connection.MySQLConnection(
                user=settings['user'],
                password=settings['password'],
                host=settings['host'],
                database=settings['database']
            )
            cursor = cny.cursor()
            data = '%s-%s-%s' % (
                (int(QtCore.QDate.year(self.dateEdit_2.date()))),
                (int(QtCore.QDate.month(self.dateEdit_2.date()))),
                (int(QtCore.QDate.day(self.dateEdit_2.date()))),
            )
            user_mail=self.label.text()
            query = (
                "UPDATE serials SET license_end='%s' WHERE user_mail='%s'"
                ) % (data, user_mail)
            cursor.execute(query)
            msgBox=QtGui.QMessageBox()
            msg = 'Licencja Użytkonika została pomyślnie zaktualizowana'
            msg_more = 'Użytkownik: <b>%s</b><br />Data: <b>%s</b>' % (
                user_mail, self.dateEdit_2.date().toString('d MMMM yyyy')
                )
            msgBox.setText(msg)
            msgBox.setInformativeText(msg_more)
            msgBox.exec_()
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        finally:
            cny.close()

    def del_clicked(self):
        self.close()
        try:
            cny = connection.MySQLConnection(
                user=settings['user'],
                password=settings['password'],
                host=settings['host'],
                database=settings['database']
            )
            cursor = cny.cursor()
            data = '%s-%s-%s' % (
                (int(QtCore.QDate.year(self.dateEdit_2.date()))),
                (int(QtCore.QDate.month(self.dateEdit_2.date()))),
                (int(QtCore.QDate.day(self.dateEdit_2.date()))),
            )
            user_mail=self.label.text()
            query = (
                "DELETE FROM serials WHERE user_mail='%s'"
                ) % (user_mail)
            cursor.execute(query)
            msgBox=QtGui.QMessageBox()
            msg = 'Licencja Użytkownika została pomyślnie usunięta'
            msg_more = 'Użytkownik: <b>%s</b>' % (
                user_mail
                )
            msgBox.setText(msg)
            msgBox.setInformativeText(msg_more)
            msgBox.exec_()
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        finally:
            cny.close()

    def on_rejectButton_clicked(self):
        self.close()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())
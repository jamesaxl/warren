# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'InsertFinishedDialog.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_InsertFinishedDialog(object):
    def setupUi(self, InsertFinishedDialog):
        InsertFinishedDialog.setObjectName("InsertFinishedDialog")
        InsertFinishedDialog.resize(546, 102)
        self.buttonBox = QtWidgets.QDialogButtonBox(InsertFinishedDialog)
        self.buttonBox.setGeometry(QtCore.QRect(190, 60, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(InsertFinishedDialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 521, 16))
        self.label.setObjectName("label")
        self.keyLineEdit = QtWidgets.QLineEdit(InsertFinishedDialog)
        self.keyLineEdit.setGeometry(QtCore.QRect(10, 30, 521, 26))
        self.keyLineEdit.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.keyLineEdit.setObjectName("keyLineEdit")

        self.retranslateUi(InsertFinishedDialog)
        self.buttonBox.rejected.connect(InsertFinishedDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(InsertFinishedDialog)

    def retranslateUi(self, InsertFinishedDialog):
        _translate = QtCore.QCoreApplication.translate
        InsertFinishedDialog.setWindowTitle(_translate("InsertFinishedDialog", "Insert Finished"))
        self.label.setText(_translate("InsertFinishedDialog", "The insert has finished. Copy the request key from below:"))


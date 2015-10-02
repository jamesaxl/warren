# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PasteInsert.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PasteInsertDialog(object):
    def setupUi(self, PasteInsertDialog):
        PasteInsertDialog.setObjectName("PasteInsertDialog")
        PasteInsertDialog.resize(546, 106)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PasteInsertDialog.sizePolicy().hasHeightForWidth())
        PasteInsertDialog.setSizePolicy(sizePolicy)
        PasteInsertDialog.setMaximumSize(QtCore.QSize(546, 106))
        self.buttonBox = QtWidgets.QDialogButtonBox(PasteInsertDialog)
        self.buttonBox.setGeometry(QtCore.QRect(360, 70, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.keyLineEdit = QtWidgets.QLineEdit(PasteInsertDialog)
        self.keyLineEdit.setGeometry(QtCore.QRect(10, 40, 521, 26))
        self.keyLineEdit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.keyLineEdit.setObjectName("keyLineEdit")
        self.progressBar = QtWidgets.QProgressBar(PasteInsertDialog)
        self.progressBar.setGeometry(QtCore.QRect(10, 10, 521, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.pushButton = QtWidgets.QPushButton(PasteInsertDialog)
        self.pushButton.setGeometry(QtCore.QRect(10, 70, 171, 23))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(PasteInsertDialog)
        QtCore.QMetaObject.connectSlotsByName(PasteInsertDialog)

    def retranslateUi(self, PasteInsertDialog):
        _translate = QtCore.QCoreApplication.translate
        PasteInsertDialog.setWindowTitle(_translate("PasteInsertDialog", "Inserting Pastebin"))
        self.pushButton.setText(_translate("PasteInsertDialog", "Copy key to clipboard"))


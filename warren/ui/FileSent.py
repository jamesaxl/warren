# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FileSent.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_fileDroppedDialog(object):
    def setupUi(self, fileDroppedDialog):
        fileDroppedDialog.setObjectName("fileDroppedDialog")
        fileDroppedDialog.resize(378, 151)
        self.buttonBox = QtWidgets.QDialogButtonBox(fileDroppedDialog)
        self.buttonBox.setGeometry(QtCore.QRect(290, 100, 71, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(fileDroppedDialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 371, 81))
        self.label.setObjectName("label")
        self.checkBox = QtWidgets.QCheckBox(fileDroppedDialog)
        self.checkBox.setGeometry(QtCore.QRect(10, 100, 271, 31))
        self.checkBox.setObjectName("checkBox")

        self.retranslateUi(fileDroppedDialog)
        self.buttonBox.rejected.connect(fileDroppedDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(fileDroppedDialog)

    def retranslateUi(self, fileDroppedDialog):
        _translate = QtCore.QCoreApplication.translate
        fileDroppedDialog.setWindowTitle(_translate("fileDroppedDialog", "File sent"))
        self.label.setText(_translate("fileDroppedDialog", "Warren sends the file to your freenet node now.\n"
"\n"
"Visit your node\'s Upload page to see the progress\n"
"of the insert and to change priorities."))
        self.checkBox.setText(_translate("fileDroppedDialog", "Don\'t show this message again."))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PastebinDialog.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PastebinDialog(object):
    def setupUi(self, PastebinDialog):
        PastebinDialog.setObjectName("PastebinDialog")
        PastebinDialog.resize(500, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PastebinDialog.sizePolicy().hasHeightForWidth())
        PastebinDialog.setSizePolicy(sizePolicy)
        PastebinDialog.setMinimumSize(QtCore.QSize(500, 400))
        PastebinDialog.setMaximumSize(QtCore.QSize(16777215, 16777215))
        PastebinDialog.setAcceptDrops(False)
        self.gridLayout = QtWidgets.QGridLayout(PastebinDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(PastebinDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(PastebinDialog)
        self.plainTextEdit.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 1, 0, 1, 3)
        self.shl_select = QtWidgets.QComboBox(PastebinDialog)
        self.shl_select.setObjectName("shl_select")
        self.gridLayout.addWidget(self.shl_select, 2, 0, 1, 1)
        self.linenos_checkbox = QtWidgets.QCheckBox(PastebinDialog)
        self.linenos_checkbox.setObjectName("linenos_checkbox")
        self.gridLayout.addWidget(self.linenos_checkbox, 2, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(PastebinDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 2, 1, 1)

        self.retranslateUi(PastebinDialog)
        QtCore.QMetaObject.connectSlotsByName(PastebinDialog)

    def retranslateUi(self, PastebinDialog):
        _translate = QtCore.QCoreApplication.translate
        PastebinDialog.setWindowTitle(_translate("PastebinDialog", "Pastebin"))
        self.label.setText(_translate("PastebinDialog", "Enter text to insert below"))
        self.linenos_checkbox.setText(_translate("PastebinDialog", "Add line numbers"))


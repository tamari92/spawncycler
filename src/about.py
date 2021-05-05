#  about.py
#
#  Author: Tamari (Nathan P. Ybanez)
#  Date of creation: 11/20/2020
#
#  UI code for the 'About' page


##  LICENSE INFORMATION
##  =======================================================================
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <https://www.gnu.org/licenses/>.
##  =======================================================================
##
##  © Nathan Ybanez, 2020-2021
##  All rights reserved.


from PyQt5 import QtCore, QtGui, QtWidgets
import os

class AboutDialog(object):
    def setupUi(self, Dialog):
        # Font used for all text
        font = QtGui.QFont()
        font.setFamily('Consolas')
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)

        # Main stuff
        Dialog.resize(630, 630)
        Dialog.setStyleSheet('background-color: rgb(40, 40, 40);')

        # Set up the logo image
        self.logo = QtWidgets.QLabel(Dialog)
        self.logo.setGeometry(QtCore.QRect(180, 20, 281, 271))
        self.logo.setText('')
        self.logo.setPixmap(QtGui.QPixmap('img/logo.png'))
        self.logo.setScaledContents(True)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)

        # Set up description
        self.description = QtWidgets.QTextEdit(Dialog)
        self.description.setGeometry(QtCore.QRect(30, 350, 571, 231))
        self.description.setFont(font)
        self.description.setStyleSheet('color: rgb(255, 255, 255);\nborder-color: rgba(255, 255, 255, 0);\nbackground-color: rgb(50, 50, 50);')
        self.description.setReadOnly(True)
        self.description.setFrameShape(QtWidgets.QFrame.Box)
        self.description.setFrameShadow(QtWidgets.QFrame.Plain)
        self.description.setLineWidth(1)

        # Set up author label
        self.author_label = QtWidgets.QLabel(Dialog)
        self.author_label.setGeometry(QtCore.QRect(220, 300, 191, 41))
        self.author_label.setFont(font)
        self.author_label.setStyleSheet('color: rgb(255, 255, 255);\nbackground-color: rgb(50, 50, 50);')
        self.author_label.setAlignment(QtCore.Qt.AlignCenter)
        self.author_label.setFrameShape(QtWidgets.QFrame.Box)
        self.author_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.author_label.setLineWidth(1)

        # Set up button
        self.ok_button = QtWidgets.QPushButton(Dialog)
        self.ok_button.setGeometry(QtCore.QRect(280, 590, 75, 23))
        self.ok_button.setStyleSheet('color: rgb(255, 255, 255);\nbackground-color: rgb(60, 60, 60);')

        self.retranslateUi(Dialog)
        self.ok_button.clicked.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.description.setHtml(_translate('Dialog', "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                                    "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                                    "p, li { white-space: pre-wrap; }\n"
                                                    "</style></head><body style=\" font-family:\'Consolas\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#2aed11;\">SpawnCycler</span></span><span style=\" font-size:9pt;\"> is a utility designed to help you Create, Edit, Generate, and Analyze SpawnCycles for Killing Floor 2\'s <span style=\" font-size:9pt; color:#2aed11;\">Controlled Difficulty</span> <span style=\" font-size:9pt;\">mod.</span></p>\n"
                                                    "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;\"><br /></p>\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">Through a <span style=\" font-size:9pt; color:#2aed11;\">simplistic UI</span><span style=\" font-size:9pt;\"> and intuitive <span style=\" font-size:9pt; color:#2aed11;\">drag-and-drop features</span><span style=\" font-size:9pt;\">, one can create a SpawnCycle in a much simpler (and quicker) fashion than creating it the old-fashioned way with a Text Editor.</span></p>\n"
                                                    "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;\"><br /></p>\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#2aed11;\">Quality-of-life features</span><span style=\" font-size:9pt;\"> such as a built-in parser ensure <span style=\" font-size:9pt; color:#2aed11;\">maximum ease-of-use</span><span style=\" font-size:9pt;\"> and make iterations quick and simple, with <span style=\" font-size:9pt; color:#2aed11;\">minimal errors</span><span style=\" font-size:9pt;\">.</span></p>\n"
                                                    "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;\"><br /></p>\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">If you have any feedback to give me, I can be reached at:</span></p>\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\"><br /></span><span style=\" font-size:9pt; color:#ffaa00;\">Discord:</span><span style=\" font-size:9pt;\"> Tamari#6292<br /></span><span style=\" font-size:9pt; color:#ffaa00;\">Email:</span><span style=\" font-size:9pt;\"> nate92@gmail.com<br /></span><span style=\" font-size:9pt; color:#ffaa00;\">Steam:</span><span style=\" font-size:9pt;\"> steamcommunity.com/id/tamaritm</span></p></body></html>"))
        self.author_label.setText(_translate('Dialog', 'SpawnCycler v1.1\nby Tamari'))
        self.ok_button.setText(_translate('Dialog', 'OK'))

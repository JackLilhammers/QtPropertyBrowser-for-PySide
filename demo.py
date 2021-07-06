# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2013 Digia Plc and/or its subsidiary(-ies).
## Contact: http://www.qt-project.org/legal
##
## This file is part of the Qt Solutions component.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Digia Plc and its Subsidiary(-ies) nor the names
##     of its contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,
## DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
############################################################################/
import sys
import os
filePath = os.path.dirname(os.path.abspath(__file__))
print(filePath)
sys.path.append(os.path.join(filePath,'QtProperty'))
sys.path.append(os.path.join(filePath,'libqt5'))
print(sys.path)
from PyQt5.QtWidgets import (
    QApplication, 
    QLabel, 
    QScrollArea, 
    QGridLayout, 
    QWidget,
    QFrame
    )
from PyQt5.QtCore import Qt

from pyqtcore import QMap, QList
from qtpropertymanager import (
    QtBoolPropertyManager, 
    QtIntPropertyManager, 
    QtStringPropertyManager, 
    QtSizePropertyManager, 
    QtRectPropertyManager, 
    QtSizePolicyPropertyManager, 
    QtEnumPropertyManager, 
    QtGroupPropertyManager
    )
from qteditorfactory import (
    QtCheckBoxFactory, 
    QtSpinBoxFactory, 
    QtSliderFactory, 
    QtScrollBarFactory, 
    QtLineEditFactory, 
    QtEnumEditorFactory
    )

from qttreepropertybrowser import QtTreePropertyBrowser
from qtgroupboxpropertybrowser import QtGroupBoxPropertyBrowser
from qtbuttonpropertybrowser import QtButtonPropertyBrowser

from PyQt5.QtGui import QIcon
import demo_rc

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = QWidget()

    boolManager = QtBoolPropertyManager(w)
    intManager = QtIntPropertyManager(w)
    stringManager = QtStringPropertyManager(w)
    sizeManager = QtSizePropertyManager(w)
    rectManager = QtRectPropertyManager(w)
    sizePolicyManager = QtSizePolicyPropertyManager(w)
    enumManager = QtEnumPropertyManager(w)
    groupManager = QtGroupPropertyManager(w)

    item0 = groupManager.addProperty("QObject")

    item1 = stringManager.addProperty("objectName")
    item0.addSubProperty(item1)

    item2 = boolManager.addProperty("enabled")
    item0.addSubProperty(item2)

    item3 = rectManager.addProperty("geometry")
    item0.addSubProperty(item3)

    item4 = sizePolicyManager.addProperty("sizePolicy")
    item0.addSubProperty(item4)

    item5 = sizeManager.addProperty("sizeIncrement")
    item0.addSubProperty(item5)

    item7 = boolManager.addProperty("mouseTracking")
    item0.addSubProperty(item7)

    item8 = enumManager.addProperty("direction")
    enumNames = QList()
    enumNames.append("Up")
    enumNames.append("Right")
    enumNames.append("Down")
    enumNames.append("Left")

    enumManager.setEnumNames(item8, enumNames)
    enumIcons = QMap()
    enumIcons[0] = QIcon(":/demo/images/up.png")
    enumIcons[1] = QIcon(":/demo/images/right.png")
    enumIcons[2] = QIcon(":/demo/images/down.png")
    enumIcons[3] = QIcon(":/demo/images/left.png")
    enumManager.setEnumIcons(item8, enumIcons)
    item0.addSubProperty(item8)

    item9 = intManager.addProperty("value")
    intManager.setRange(item9, -100, 100)
    item0.addSubProperty(item9)

    checkBoxFactory = QtCheckBoxFactory(w)
    spinBoxFactory = QtSpinBoxFactory(w)
    sliderFactory = QtSliderFactory(w)
    scrollBarFactory = QtScrollBarFactory(w)
    lineEditFactory = QtLineEditFactory(w)
    comboBoxFactory = QtEnumEditorFactory(w)

    editor1 = QtTreePropertyBrowser()
    editor1.setFactoryForManager(boolManager, checkBoxFactory)
    editor1.setFactoryForManager(intManager, spinBoxFactory)
    editor1.setFactoryForManager(stringManager, lineEditFactory)
    editor1.setFactoryForManager(sizeManager.subIntPropertyManager(), spinBoxFactory)
    editor1.setFactoryForManager(rectManager.subIntPropertyManager(), spinBoxFactory)
    editor1.setFactoryForManager(sizePolicyManager.subIntPropertyManager(), spinBoxFactory)
    editor1.setFactoryForManager(sizePolicyManager.subEnumPropertyManager(), comboBoxFactory)
    editor1.setFactoryForManager(enumManager, comboBoxFactory)

    editor1.addProperty(item0)

    editor2 = QtTreePropertyBrowser()
    editor2.addProperty(item0)

    editor3 = QtGroupBoxPropertyBrowser()
    editor3.setFactoryForManager(boolManager, checkBoxFactory)
    editor3.setFactoryForManager(intManager, spinBoxFactory)
    editor3.setFactoryForManager(stringManager, lineEditFactory)
    editor3.setFactoryForManager(sizeManager.subIntPropertyManager(), spinBoxFactory)
    editor3.setFactoryForManager(rectManager.subIntPropertyManager(), spinBoxFactory)
    editor3.setFactoryForManager(sizePolicyManager.subIntPropertyManager(), spinBoxFactory)
    editor3.setFactoryForManager(sizePolicyManager.subEnumPropertyManager(), comboBoxFactory)
    editor3.setFactoryForManager(enumManager, comboBoxFactory)

    editor3.addProperty(item0)

    scroll3 = QScrollArea()
    scroll3.setWidgetResizable(True)
    scroll3.setWidget(editor3)

    editor4 = QtGroupBoxPropertyBrowser()
    editor4.setFactoryForManager(boolManager, checkBoxFactory)
    editor4.setFactoryForManager(intManager, scrollBarFactory)
    editor4.setFactoryForManager(stringManager, lineEditFactory)
    editor4.setFactoryForManager(sizeManager.subIntPropertyManager(), spinBoxFactory)
    editor4.setFactoryForManager(rectManager.subIntPropertyManager(), spinBoxFactory)
    editor4.setFactoryForManager(sizePolicyManager.subIntPropertyManager(), sliderFactory)
    editor4.setFactoryForManager(sizePolicyManager.subEnumPropertyManager(), comboBoxFactory)
    editor4.setFactoryForManager(enumManager, comboBoxFactory)

    editor4.addProperty(item0)

    scroll4 = QScrollArea()
    scroll4.setWidgetResizable(True)
    scroll4.setWidget(editor4)

    editor5 = QtButtonPropertyBrowser()
    editor5.setFactoryForManager(boolManager, checkBoxFactory)
    editor5.setFactoryForManager(intManager, scrollBarFactory)
    editor5.setFactoryForManager(stringManager, lineEditFactory)
    editor5.setFactoryForManager(sizeManager.subIntPropertyManager(), spinBoxFactory)
    editor5.setFactoryForManager(rectManager.subIntPropertyManager(), spinBoxFactory)
    editor5.setFactoryForManager(sizePolicyManager.subIntPropertyManager(), sliderFactory)
    editor5.setFactoryForManager(sizePolicyManager.subEnumPropertyManager(), comboBoxFactory)
    editor5.setFactoryForManager(enumManager, comboBoxFactory)

    editor5.addProperty(item0)

    scroll5 = QScrollArea()
    scroll5.setWidgetResizable(True)
    scroll5.setWidget(editor5)

    layout = QGridLayout(w)
    label1 = QLabel("Editable Tree Property Browser")
    label2 = QLabel("Read Only Tree Property Browser, editor factories are not set")
    label3 = QLabel("Group Box Property Browser")
    label4 = QLabel("Group Box Property Browser with different editor factories")
    label5 = QLabel("Button Property Browser")
    label1.setWordWrap(True)
    label2.setWordWrap(True)
    label3.setWordWrap(True)
    label4.setWordWrap(True)
    label5.setWordWrap(True)
    label1.setFrameShadow(QFrame.Sunken)
    label2.setFrameShadow(QFrame.Sunken)
    label3.setFrameShadow(QFrame.Sunken)
    label4.setFrameShadow(QFrame.Sunken)
    label5.setFrameShadow(QFrame.Sunken)
    label1.setFrameShape(QFrame.Panel)
    label2.setFrameShape(QFrame.Panel)
    label3.setFrameShape(QFrame.Panel)
    label4.setFrameShape(QFrame.Panel)
    label5.setFrameShape(QFrame.Panel)
    label1.setAlignment(Qt.AlignCenter)
    label2.setAlignment(Qt.AlignCenter)
    label3.setAlignment(Qt.AlignCenter)
    label4.setAlignment(Qt.AlignCenter)
    label5.setAlignment(Qt.AlignCenter)

    layout.addWidget(label1, 0, 0)
    layout.addWidget(label2, 0, 1)
    layout.addWidget(label3, 0, 2)
    layout.addWidget(label4, 0, 3)
    layout.addWidget(label5, 0, 4)
    layout.addWidget(editor1, 1, 0)
    layout.addWidget(editor2, 1, 1)
    layout.addWidget(scroll3, 1, 2)
    layout.addWidget(scroll4, 1, 3)
    layout.addWidget(scroll5, 1, 4)
    w.showMaximized()
    w.show()

    ret = app.exec()

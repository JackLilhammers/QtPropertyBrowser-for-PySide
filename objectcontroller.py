# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2013 Digia Plc and/or its subsidiary(-ies).
## Contact: http:#www.qt-project.org/legal
##
## self file is part of the Qt Solutions component.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use self file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, self list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, self list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Digia Plc and its Subsidiary(-ies) nor the names
##     of its contributors may be used to endorse or promote products derived
##     from self software without specific prior written permission.
##
##
## self SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,
## DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF self SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
############################################################################/
import sys

from libqt5.compat import QVariant
from PySide2.QtCore import QTimeLine
from PySide2.QtGui import QTextDocument
from PySide2.QtWidgets import (
    QDialog,
    QComboBox,
    QToolButton,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QTreeWidget,
    QCalendarWidget,
    QAction,
    QApplication
)
from libqt5.pyqtcore import QMap, QList, QMapMap
from QtProperty.qtvariantproperty import QtVariantPropertyManager, QtVariantEditorFactory
from QtProperty.qttreepropertybrowser import QtTreePropertyBrowser

class ObjectControllerPrivate():
    def __init__(self):
        self.q_ptr = 0
        self.m_object = 0
        self.m_classToProperty = QMap()
        self.m_propertyToClass = QMap()
        self.m_propertyToIndex = QMap()
        self.m_classToIndexToProperty = QMapMap()
        self.m_propertyToExpanded = QMap()
        self.m_topLevelProperties = QList()
        self.m_browser = 0
        self.m_manager = 0
        self.m_readOnlyManager = 0

    def enumToInt(self, metaEnum, enumValue):
        valueMap = QMap() # dont show multiple enum values which have the same values
        pos = 0
        for i in range(metaEnum.keyCount()):
            value = metaEnum.value(i)
            if (not valueMap.contains(value)):
                if (value == enumValue):
                    return pos
                valueMap[value] = pos
                pos += 1

        return -1

    def intToEnum(self, metaEnum, intValue):
        valueMap = QMap() # dont show multiple enum values which have the same values
        values = QList()
        for i in range(metaEnum.keyCount()):
            value = metaEnum.value(i)
            if (not valueMap.contains(value)):
                valueMap[value] = True
                values.append(value)

        if (intValue >= values.count()):
            return -1
        return values.at(intValue)

    def isSubValue(self, value, subValue):
        if (value == subValue):
            return True
        i = 0
        while (subValue):
            if (not (value & (1 << i))):
                if (subValue & 1):
                    return False

            i += 1
            subValue = subValue >> 1

        return True

    def isPowerOf2(self, value):
        while (value):
            if (value & 1):
                return value == 1

            value = value >> 1

        return False

    def flagToInt(self, metaEnum, flagValue):
        if (not flagValue):
            return 0
        intValue = 0
        valueMap = QMap() # dont show multiple enum values which have the same values
        pos = 0
        for i in range(metaEnum.keyCount()):
            value = metaEnum.value(i)
            if (not valueMap.contains(value) and self.isPowerOf2(value)):
                if (self.isSubValue(flagValue, value)):
                    intValue |= (1 << pos)
                valueMap[value] = pos
                pos += 1

        return intValue

    def intToFlag(self, metaEnum, intValue):
        valueMap = QMap() # dont show multiple enum values which have the same values
        values = QList()
        for i in range(metaEnum.keyCount()):
            value = metaEnum.value(i)
            if (not valueMap.contains(value) and self.isPowerOf2(value)):
                valueMap[value] = True
                values.append(value)

        flagValue = 0
        temp = intValue
        i = 0
        while (temp):
            if (i >= values.count()):
                return -1
            if (temp & 1):
                flagValue |= values.at(i)
            i += 1
            temp = temp >> 1

        return flagValue

    def updateClassProperties(self, metaObject, recursive):
        if (not metaObject):
            return

        if (recursive):
            self.updateClassProperties(metaObject.superClass(), recursive)

        classProperty = self.m_classToProperty.value(metaObject)
        if (not classProperty):
            return

        for idx in range(metaObject.propertyOffset(), metaObject.propertyCount(), 1):
            metaProperty = metaObject.property(idx)
            if (metaProperty.isReadable()):
                if (self.m_classToIndexToProperty.contains(metaObject) and self.m_classToIndexToProperty[metaObject].contains(idx)):
                    subProperty = self.m_classToIndexToProperty[metaObject][idx]
                    if (metaProperty.isEnumType()):
                        if (metaProperty.isFlagType()):
                            subProperty.setValue(self.flagToInt(metaProperty.enumerator(), metaProperty.read(self.m_object)))
                        else:
                            subProperty.setValue(self.enumToInt(metaProperty.enumerator(), metaProperty.read(self.m_object)))
                    else:
                        subProperty.setValue(metaProperty.read(self.m_object))

    def addClassProperties(self, metaObject):
        if (not metaObject):
            return
        self.addClassProperties(metaObject.superClass())
        classProperty = self.m_classToProperty.value(metaObject)
        if (not classProperty):
            className = metaObject.className()
            classProperty = self.m_manager.addProperty(QtVariantPropertyManager.groupTypeId(), className)
            self.m_classToProperty[metaObject] = classProperty
            self.m_propertyToClass[classProperty] = metaObject

            for idx in range(metaObject.propertyOffset(), metaObject.propertyCount(), 1):
                metaProperty = metaObject.property(idx)
                type = metaProperty.userType()
                subProperty = 0
                if (not metaProperty.isReadable()):
                    subProperty = self.m_readOnlyManager.addProperty(QVariant.String, metaProperty.name())
                    subProperty.setValue("< Non Readable >")
                elif (metaProperty.isEnumType()):
                    if (metaProperty.isFlagType()):
                        subProperty = self.m_manager.addProperty(QtVariantPropertyManager.flagTypeId(), metaProperty.name())
                        metaEnum = metaProperty.enumerator()
                        valueMap = QMap()
                        flagNames = QList()
                        for i in range(metaEnum.keyCount()):
                            value = metaEnum.value(i)
                            if (not valueMap.contains(value) and self.isPowerOf2(value)):
                                valueMap[value] = True
                                flagNames.append(metaEnum.key(i))

                        subProperty.setAttribute("flagNames", flagNames)
                        subProperty.setValue(self.flagToInt(metaEnum, metaProperty.read(self.m_object)))

                    else:
                        subProperty = self.m_manager.addProperty(QtVariantPropertyManager.enumTypeId(), metaProperty.name())
                        metaEnum = metaProperty.enumerator()
                        valueMap = QMap() # dont show multiple enum values which have the same values
                        enumNames = QList()
                        for i in range(metaEnum.keyCount()):
                            value = metaEnum.value(i)
                            if (not valueMap.contains(value)):
                                valueMap[value] = True
                                enumNames.append(metaEnum.key(i))

                        subProperty.setAttribute("enumNames", enumNames)
                        subProperty.setValue(self.enumToInt(metaEnum, metaProperty.read(self.m_object)))

                elif (self.m_manager.isPropertyTypeSupported(type)):
                    if (not metaProperty.isWritable()):
                        subProperty = self.m_readOnlyManager.addProperty(type, metaProperty.name() + " (Non Writable)")
                    if (not metaProperty.isDesignable()):
                        subProperty = self.m_readOnlyManager.addProperty(type, metaProperty.name() + " (Non Designable)")
                    else:
                        subProperty = self.m_manager.addProperty(type, metaProperty.name())
                    subProperty.setValue(metaProperty.read(self.m_object))
                else:
                    subProperty = self.m_readOnlyManager.addProperty(QVariant.String, metaProperty.name())
                    subProperty.setValue("< Unknown Type >")
                    subProperty.setEnabled(False)

                classProperty.addSubProperty(subProperty)
                self.m_propertyToIndex[subProperty] = idx
                self.m_classToIndexToProperty[metaObject][idx] = subProperty

        else:
            self.updateClassProperties(metaObject, False)

        self.m_topLevelProperties.append(classProperty)
        self.m_browser.addProperty(classProperty)

    def saveExpandedState(self):
        pass

    def restoreExpandedState(self):
        pass

    def slotValueChanged(self, property, value):
        if (not self.m_propertyToIndex.contains(property)):
            return

        idx = self.m_propertyToIndex.value(property)

        metaObject = self.m_object.metaObject()
        metaProperty = metaObject.property(idx)
        if (metaProperty.isEnumType()):
            if (metaProperty.isFlagType()):
                metaProperty.write(self.m_object, self.intToFlag(metaProperty.enumerator(), value))
            else:
                metaProperty.write(self.m_object, self.intToEnum(metaProperty.enumerator(), value))
        else:
            metaProperty.write(self.m_object, value)

        self.updateClassProperties(metaObject, True)

##########

class ObjectController(QWidget):
    def __init__(self, parent=None):
        super(ObjectController, self).__init__(parent)
        self.d_ptr = ObjectControllerPrivate()
        self.d_ptr.q_ptr = self
        self.d_ptr.m_object = 0

        ##
        #    scroll = QScrollArea(self)
        #    scroll.setWidgetResizable(True)
        #
        #    self.d_ptr.m_browser = QtGroupBoxPropertyBrowser(self)
        #    layout = QVBoxLayout(self)
        #    layout.setMargin(0)
        #    layout.addWidget(scroll)
        #    scroll.setWidget(self.d_ptr.m_browser)
        ##
        browser = QtTreePropertyBrowser(self)
        browser.setRootIsDecorated(False)
        self.d_ptr.m_browser = browser
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.d_ptr.m_browser)

        self.d_ptr.m_readOnlyManager = QtVariantPropertyManager(self)
        self.d_ptr.m_manager = QtVariantPropertyManager(self)
        factory = QtVariantEditorFactory(self)
        self.d_ptr.m_browser.setFactoryForManager(self.d_ptr.m_manager, factory)

        self.d_ptr.m_manager.valueChangedSignal.connect(self.d_ptr.slotValueChanged)

    def __del__(self):
        del self.d_ptr

    def setObject(self, object):
        if (self.d_ptr.m_object == object):
            return

        if (self.d_ptr.m_object):
            self.d_ptr.saveExpandedState()
            for it in self.d_ptr.m_topLevelProperties:
                self.d_ptr.m_browser.removeProperty(it)

            self.d_ptr.m_topLevelProperties.clear()

        self.d_ptr.m_object = object

        if (not self.d_ptr.m_object):
            return

        self.d_ptr.addClassProperties(self.d_ptr.m_object.metaObject())

        self.d_ptr.restoreExpandedState()

    def object(self):
        return self.d_ptr.m_object

class MyController(QDialog):
    def __init__(self, parent=None):
        super(MyController, self).__init__(parent)

        self.theClassNames = QList()
        self.theClassCombo = QComboBox(self)
        self.theControlledObject = None

        button = QToolButton(self)
        self.theController = ObjectController(self)
        buttonBox = QDialogButtonBox(self)

        button.clicked.connect(self.createAndControl)
        buttonBox.rejected.connect(self.reject)

        button.setText(self.tr("Create And Control"))
        buttonBox.setStandardButtons(QDialogButtonBox.Close)

        layout = QVBoxLayout(self)
        internalLayout = QHBoxLayout()
        internalLayout.addWidget(self.theClassCombo)
        internalLayout.addWidget(button)
        layout.addLayout(internalLayout)
        layout.addWidget(self.theController)
        layout.addWidget(buttonBox)

        self.theClassNames.append("QWidget")
        self.theClassNames.append("QPushButton")
        self.theClassNames.append("QDialogButtonBox")
        self.theClassNames.append("QTreeWidget")
        self.theClassNames.append("QCalendarWidget")
        self.theClassNames.append("QAction")
        self.theClassNames.append("QTimeLine")
        self.theClassNames.append("QTextDocument")

        self.theClassCombo.addItems(self.theClassNames)

    def __del__(self):
        if (self.theControlledObject):
            del self.theControlledObject

    def createAndControl(self):
        newObject = 0
        className = self.theClassNames.at(self.theClassCombo.currentIndex())
        if (className == "QWidget"):
            newObject = QWidget()
        elif (className == "QPushButton"):
            newObject = QPushButton()
        elif (className == "QDialogButtonBox"):
            newObject = QDialogButtonBox()
        elif (className == "QTreeWidget"):
            newObject = QTreeWidget()
        elif (className == "QCalendarWidget"):
            newObject = QCalendarWidget()
        elif (className == "QAction"):
            newObject = QAction(None)
        elif (className == "QTimeLine"):
            newObject = QTimeLine()
        elif (className == "QTextDocument"):
            newObject = QTextDocument()

        if (not newObject):
            return

        newWidget = newObject
        if hasattr(newWidget, 'geometry'):
            r = newWidget.geometry()
            r.setSize(newWidget.sizeHint())
            r.setWidth(max(r.width(), 150))
            r.setHeight(max(r.height(), 50))
            r.moveCenter(QApplication.desktop().geometry().center())
            newWidget.setGeometry(r)
            newWidget.setWindowTitle(self.tr("Controlled Object: %s"%className))
            newWidget.show()

        if (self.theControlledObject):
            del self.theControlledObject

        self.theControlledObject = newObject
        self.theController.setObject(self.theControlledObject)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    controller = MyController()
    controller.show()

    ret = app.exec()
    sys.exit(ret)

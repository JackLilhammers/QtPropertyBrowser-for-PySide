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

sys.path.append('QtProperty')
sys.path.append('libqt5')
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QApplication, QDoubleSpinBox
from pyqtcore import QMap, QMapList
from qtpropertymanager import QtDoublePropertyManager
from qteditorfactory import QtAbstractEditorFactory, QtDoubleSpinBoxFactory, registerEditorFactory
from qtpropertybrowser import QtProperty
from qttreepropertybrowser import QtTreePropertyBrowser

class DecoratedDoublePropertyManager(QtDoublePropertyManager):
    prefixChangedSignal = Signal(QtProperty, str)
    suffixChangedSignal = Signal(QtProperty, str)
    class Data:
        prefix = ''
        suffix = ''

    def __init__(self, parent=None):
        super().__init__(parent)

        self.propertyToData = QMap()

    def __del__(self):
        pass

    def prefix(self, property):
        if (not self.propertyToData.contains(property)):
            return ''
        return self.propertyToData[property].prefix

    def suffix(self, property):
        if (not self.propertyToData.contains(property)):
            return ''
        return self.propertyToData[property].suffix

    def setPrefix(self, property, prefix):
        if (not self.propertyToData.contains(property)):
            return

        data = self.propertyToData[property]
        if (data.prefix == prefix):
            return

        data.prefix = prefix
        self.propertyToData[property] = data

        self.propertyChangedSignal.emit(property)
        self.suffixChangedSignal.emit(property, prefix)

    def setSuffix(self, property, suffix):
        if (not self.propertyToData.contains(property)):
            return

        data = self.propertyToData[property]
        if (data.suffix == suffix):
            return

        data.suffix = suffix
        self.propertyToData[property] = data

        self.propertyChangedSignal.emit(property)
        self.suffixChangedSignal.emit(property, suffix)

    def valueText(self, property):
        text = super().valueText(property)
        if (not self.propertyToData.contains(property)):
            return text

        data = self.propertyToData[property]
        text = data.prefix + text + data.suffix

        return text

    def initializeProperty(self, property):
        self.propertyToData[property] = DecoratedDoublePropertyManager.Data()
        super().initializeProperty(property)

    def uninitializeProperty(self, property):
        self.propertyToData.remove(property)
        super().uninitializeProperty(property)

class DecoratedDoubleSpinBoxFactory(QtAbstractEditorFactory):

    def __init__(self, parent=None):
        super(DecoratedDoubleSpinBoxFactory, self).__init__(parent)

        self.propertyToData = QMap()
        # We delegate responsibilities for QtDoublePropertyManager, which is a base class
        #   of DecoratedDoublePropertyManager to appropriate 
        self.originalFactory = QtDoubleSpinBoxFactory(self)
        self.createdEditors = QMapList()
        self.editorToProperty = QMap()

    # not need to delete editors because they will be deld by originalFactory in its destructor
    def __del__(self):
        pass

    def connectPropertyManager(self, manager):
        self.originalFactory.addPropertyManager(manager)
        manager.prefixChangedSignal.connect(self.slotPrefixChanged)
        manager.suffixChangedSignal.connect(self.slotSuffixChanged)

    def createEditor(self, manager, property, parent):
        base = self.originalFactory
        w = base.findEditor(property, parent)
        if (not w):
            return 0

        spinBox = w
        if (not spinBox):
            return 0

        spinBox.setPrefix(manager.prefix(property))
        spinBox.setSuffix(manager.suffix(property))

        self.createdEditors[property].append(spinBox)
        self.editorToProperty[spinBox] = property

        return spinBox

    def disconnectPropertyManager(self, manager):
        self.originalFactory.removePropertyManager(manager)
        manager.prefixChangedSignal.disconnect(self.slotPrefixChanged)
        manager.suffixChangedSignal.disconnect(self.slotSuffixChanged)

    def slotPrefixChanged(self, property, prefix):
        if (not self.createdEditors.contains(property)):
            return

        manager = self.propertyManager(property)
        if (not manager):
            return

        editors = self.createdEditors[property]
        for editor in editors:
            editor.setPrefix(prefix)

    def slotSuffixChanged(self, property, prefix):
        if (not self.createdEditors.contains(property)):
            return

        manager = self.propertyManager(property)
        if (not manager):
            return

        editors = self.createdEditors[property]
        for editor in editors:
            editor.setSuffix(prefix)

    def slotEditorDestroyed(self, object):
        property = self.editorToProperty.get(object)
        if property:
            editor = object
            self.editorToProperty.remove(editor)
            self.createdEditors[property].removeAll(editor)
            if (self.createdEditors[property].isEmpty()):
                self.createdEditors.remove(property)
            return

registerEditorFactory(DecoratedDoubleSpinBoxFactory, QDoubleSpinBox)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    undecoratedManager = QtDoublePropertyManager()
    undecoratedProperty = undecoratedManager.addProperty("Undecorated")
    undecoratedManager.setValue(undecoratedProperty, 123.45)

    decoratedManager = DecoratedDoublePropertyManager()
    decoratedProperty = decoratedManager.addProperty("Decorated")
    decoratedManager.setPrefix(decoratedProperty, "speed: ")
    decoratedManager.setSuffix(decoratedProperty, " km/h")
    decoratedManager.setValue(decoratedProperty, 123.45)

    undecoratedFactory = QtDoubleSpinBoxFactory()
    decoratedFactory = DecoratedDoubleSpinBoxFactory()

    editor = QtTreePropertyBrowser()
    editor.setFactoryForManager(undecoratedManager, undecoratedFactory)
    editor.setFactoryForManager(decoratedManager, decoratedFactory)
    editor.addProperty(undecoratedProperty)
    editor.addProperty(decoratedProperty)
    editor.show()

    ret = app.exec()

    del decoratedFactory
    del decoratedManager
    del undecoratedFactory
    del undecoratedManager
    del editor


# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2013 Digia Plc and/or its subsidiary(-ies).
## Contact: http://www.qt-project.org/legal
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
sys.path.append('QtProperty')
sys.path.append('libqt5')
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import QVariant, QPointF
from pyqtcore import QMap
from qtvariantproperty import QtVariantPropertyManager, QtVariantEditorFactory
from qttreepropertybrowser import QtTreePropertyBrowser

class VariantManager(QtVariantPropertyManager):
    class Data:
        value = QVariant()
        x = 0
        y = 0

    def __init__(self, parent=None):
        super(VariantManager, self).__init__(parent)
        self.propertyToData = QMap()
        self.xToProperty = QMap()
        self.yToProperty = QMap()

        self.valueChangedSignal.connect(self.slotValueChanged)
        self.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        pass

    def slotValueChanged(self, property, value):
        if (self.xToProperty.contains(property)):
            pointProperty = self.xToProperty[property]
            v = self.value(pointProperty)
            p = v.value()
            p.setX(value)
            self.setValue(pointProperty, p)
        elif (self.yToProperty.contains(property)):
            pointProperty = self.yToProperty[property]
            v = self.value(pointProperty)
            p = v.value()
            p.setY(value)
            self.setValue(pointProperty, p)

    def slotPropertyDestroyed(self, property):
        if (self.xToProperty.contains(property)):
            pointProperty = self.xToProperty[property]
            self.propertyToData[pointProperty].x = 0
            self.xToProperty.remove(property)
        elif (self.yToProperty.contains(property)):
            pointProperty = self.yToProperty[property]
            self.propertyToData[pointProperty].y = 0
            self.yToProperty.remove(property)

    def isPropertyTypeSupported(self, propertyType):
        if (propertyType == QVariant.PointF):
            return True
        return super(VariantManager, self).isPropertyTypeSupported(propertyType)

    def valueType(self, propertyType):
        if (propertyType == QVariant.PointF):
            return QVariant.PointF
        return super(VariantManager, self).valueType(propertyType)

    def value(self, property):
        if (self.propertyToData.contains(property)):
            return self.propertyToData[property].value
        return super(VariantManager, self).value(property)

    def valueText(self, property):
        if (self.propertyToData.contains(property)):
            v = self.propertyToData[property].value
            p = v.value()
            return self.tr("(%.2f, %.2f)"%(p.x(), p.y()))

        return super(VariantManager, self).valueText(property)

    def setValue(self, property, val):
        if (self.propertyToData.contains(property)):
            if type(val)!=QVariant:
                val = QVariant(val)
            if (val.type() != QVariant.PointF and not val.canConvert(QVariant.PointF)):
                return
            p = val.value()
            d = self.propertyToData[property]
            d.value = QVariant(p)
            if (d.x):
                d.x.setValue(p.x())
            if (d.y):
                d.y.setValue(p.y())
            self.propertyToData[property] = d
            self.propertyChangedSignal.emit(property)
            self.valueChangedSignal.emit(property, p)
            return

        super(VariantManager, self).setValue(property, val)

    def initializeProperty(self, property):
        if (self.propertyType(property) == QVariant.PointF):
            d = VariantManager.Data()

            d.value = QVariant(QPointF(0, 0))

            d.x = self.addProperty(QVariant.Double)
            d.x.setPropertyName(self.tr("Position X"))
            property.addSubProperty(d.x)
            self.xToProperty[d.x] = property

            d.y = self.addProperty(QVariant.Double)
            d.y.setPropertyName(self.tr("Position Y"))
            property.addSubProperty(d.y)
            self.yToProperty[d.y] = property

            self.propertyToData[property] = d

        super(VariantManager, self).initializeProperty(property)

    def uninitializeProperty(self, property):
        if (self.propertyToData.contains(property)):
            d = self.propertyToData[property]
            if (d.x):
                self.xToProperty.remove(d.x)
            if (d.y):
                self.yToProperty.remove(d.y)
            self.propertyToData.remove(property)

        super(VariantManager, self).uninitializeProperty(property)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    variantManager = VariantManager()

    item = variantManager.addProperty(QVariant.PointF, "PointF Property")
    item.setValue(QPointF(2.5, 13.13))

    variantFactory = QtVariantEditorFactory()

    ed1 = QtTreePropertyBrowser()
    ed1.setResizeMode(QtTreePropertyBrowser.Interactive)
    varMan = variantManager
    ed1.setFactoryForManager(varMan, variantFactory)
    ed1.addProperty(item)

    ed1.show()

    ret = app.exec()

    del variantFactory
    del variantManager


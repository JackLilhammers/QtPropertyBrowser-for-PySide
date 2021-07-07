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
##     notice, self list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, self list of conditions and the following disclaimer in
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
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################
import sys

sys.path.append('QtProperty')
sys.path.append('libqt5')
from qtpy.QtWidgets import QApplication, QMainWindow, QAction, QDockWidget
from qtpy.QtCore import (
    QPoint, 
    Qt, 
    QSize, 
    QVariant, 
    Signal
    )
from random import random
from qtpy.QtGui import QColor, QPen, QBrush
from pyqtcore import QMap
from qttreepropertybrowser import QtTreePropertyBrowser
from qtvariantproperty import (
    QtVariantPropertyManager, 
    QtVariantEditorFactory
)
from qtcanvas import (
    QtCanvas, 
    QtCanvasView, 
    QtCanvasRectangle, 
    QtCanvasEllipse, 
    QtCanvasLine, 
    QtCanvasText, 
    QtCanvasItem, 
    RttiValues
    )

def rand():
    return int(random()*0x7fff)

class CanvasView(QtCanvasView):
    itemClickedSignal = Signal(QtCanvasItem)
    itemMovedSignal = Signal(QtCanvasItem)
    def __init__(self, arg1=None, arg2=None):
        if type(arg1)==QtCanvas:
            super(CanvasView, self).__init__(arg1, arg2)
        else:
            super(CanvasView, self).__init__(arg1)
        self.moving = QtCanvasItem(None)
        self.moving_start = QPoint()

    def contentsMousePressEvent(self, event):
        self.handleMouseClickEvent(event)

    def contentsMouseDoubleClickEvent(self, event):
        self.handleMouseClickEvent(event)

    def handleMouseClickEvent(self, event):
        p = self.inverseWorldMatrix().map(event.pos())
        l = self.canvas().collisions(p)
        self.moving = QtCanvasItem(None)
        if (not l.isEmpty()):
            self.moving = l.first()
        self.moving_start = p
        self.itemClickedSignal.emit(self.moving)

    def contentsMouseMoveEvent(self, event):
        if (self.moving):
            p = self.inverseWorldMatrix().map(event.pos())
            self.moving.moveBy(p.x() - self.moving_start.x(), p.y() - self.moving_start.y())
            self.moving_start = p
            self.canvas().update()
            self.itemMovedSignal.emit(self.moving)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.propertyToId = QMap()
        self.idToProperty = QMap()
        self.idToExpanded = QMap()

        editMenu = self.menuBar().addMenu(self.tr("Edit"))
        newObjectMenu = editMenu.addMenu(self.tr("New Object"))

        newRectangleAction = QAction(self.tr("Rectangle"), self)
        newRectangleAction.triggered.connect(self.newRectangle)
        newObjectMenu.addAction(newRectangleAction)

        newLineAction = QAction(self.tr("Line"), self)
        newLineAction.triggered.connect(self.newLine)
        newObjectMenu.addAction(newLineAction)

        newEllipseAction = QAction(self.tr("Ellipse"), self)
        newEllipseAction.triggered.connect(self.newEllipse)
        newObjectMenu.addAction(newEllipseAction)

        newTextAction = QAction(self.tr("Text"), self)
        newTextAction.triggered.connect(self.newText)
        newObjectMenu.addAction(newTextAction)

        self.deleteAction = QAction(self.tr("Delete Object"), self)
        self.deleteAction.triggered.connect(self.deleteObject)
        editMenu.addAction(self.deleteAction)

        clearAction = QAction(self.tr("Clear All"), self)
        clearAction.triggered.connect(self.clearAll)
        editMenu.addAction(clearAction)

        fillAction = QAction(self.tr("Fill View"), self)
        fillAction.triggered.connect(self.fillView)
        editMenu.addAction(fillAction)

        self.variantManager = QtVariantPropertyManager(self)

        self.variantManager.valueChangedSignal.connect(self.valueChanged)
        variantFactory = QtVariantEditorFactory(self)

        self.canvas = QtCanvas(800, 600)
        self.canvasView = CanvasView(self.canvas, self)
        self.setCentralWidget(self.canvasView)

        dock = QDockWidget(self)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        self.propertyEditor = QtTreePropertyBrowser(dock)
        self.propertyEditor.setFactoryForManager(self.variantManager, variantFactory)
        dock.setWidget(self.propertyEditor)

        self.currentItem = QtCanvasItem(None)

        self.canvasView.itemClickedSignal.connect(self.itemClicked)
        self.canvasView.itemMovedSignal.connect(self.itemMoved)

        self.fillView()
        self.itemClicked(QtCanvasItem(None))

    def newRectangle(self):
        item = self.addRectangle()
        self.canvas.update()
        self.itemClicked(item)

    def newEllipse(self):
        item = self.addEllipse()
        self.canvas.update()
        self.itemClicked(item)

    def newLine(self):
        item = self.addLine()
        self.canvas.update()
        self.itemClicked(item)

    def newText(self):
        item = self.addText()
        self.canvas.update()
        self.itemClicked(item)

    def deleteObject(self):
        if (not self.currentItem or self.currentItem.isNone()):
            return

        self.canvas.removeItem(self.currentItem)
        self.currentItem = QtCanvasItem(None)
        self.itemClicked(self.currentItem)
        self.canvas.update()

    def clearAll(self):
        for item in self.canvas.allItems():
            self.canvas.removeItem(item)
        self.itemClicked(QtCanvasItem(None))
        self.canvas.update()

    def fillView(self):
        for i in range(10):
            self.addRectangle()
            self.addEllipse()
            self.addLine()
            self.addText()
        self.canvas.update()

    def addRectangle(self):
        item = QtCanvasRectangle(rand() % self.canvas.width(), rand() % self.canvas.height(), 50, 50, self.canvas)
        item.setBrush(QBrush(QColor(rand() % 32 * 8, rand() % 32 * 8, rand() % 32 * 8)))
        item.setPen(QPen(QColor(rand() % 32*8, rand() % 32*8, rand() % 32*8), 4))
        item.setZ(rand() % 256)
        item.show()
        return item

    def addEllipse(self):
        item = QtCanvasEllipse(50, 50, self.canvas)
        item.setBrush(QBrush(QColor(rand() % 32 * 8, rand() % 32 * 8, rand() % 32 * 8)))
        item.move(rand() % self.canvas.width(), rand() % self.canvas.height())
        item.setZ(rand() % 256)
        item.show()
        return item

    def addLine(self):
        item = QtCanvasLine(self.canvas)
        item.setPoints(0, 0, rand() % self.canvas.width() - self.canvas.width() / 2, rand() % self.canvas.height() - self.canvas.height() / 2)
        item.move(rand() % self.canvas.width(), rand() % self.canvas.height())
        item.setPen(QPen(QColor(rand() % 32*8, rand() % 32*8, rand() % 32*8), 6))
        item.setZ(rand() % 256)
        item.show()
        return item

    def addText(self):
        item = QtCanvasText(self.canvas)
        item.setText(self.tr("Text"))
        item.setColor(QColor(rand() % 32*8, rand() % 32*8, rand() % 32*8))
        item.move(rand() % self.canvas.width(), rand() % self.canvas.height())
        item.setZ(rand() % 256)
        item.show()
        return item

    def itemMoved(self, item):
        if (item != self.currentItem or self.currentItem.isNone()):
            return

        self.variantManager.setValue(self.idToProperty["xpos"], item.x())
        self.variantManager.setValue(self.idToProperty["ypos"], item.y())
        self.variantManager.setValue(self.idToProperty["zpos"], item.z())

    def updateExpandState(self):
        l = self.propertyEditor.topLevelItems()
        for item in l:
            prop = item.property()
            self.idToExpanded[self.propertyToId[prop]] = self.propertyEditor.isExpanded(item)

    def itemClicked(self, item):
        self.updateExpandState()
        for p in self.propertyToId.keys():
            p.destroy()
        self.propertyToId.clear()
        self.idToProperty.clear()

        self.currentItem = item
        if (not self.currentItem or self.currentItem.isNone()):
            self.deleteAction.setEnabled(False)
            return

        self.deleteAction.setEnabled(True)

        property = self.variantManager.addProperty(QVariant.Double, self.tr("Position X"))
        property.setAttribute("minimum", 0)
        property.setAttribute("maximum", self.canvas.width())
        property.setValue(item.x())
        self.addProperty(property, "xpos")

        property = self.variantManager.addProperty(QVariant.Double, self.tr("Position Y"))
        property.setAttribute("minimum", 0)
        property.setAttribute("maximum", self.canvas.height())
        property.setValue(item.y())
        self.addProperty(property, "ypos")

        property = self.variantManager.addProperty(QVariant.Double, self.tr("Position Z"))
        property.setAttribute("minimum", 0)
        property.setAttribute("maximum", 256)
        property.setValue(item.z())
        self.addProperty(property, "zpos")

        if (item.rtti() == RttiValues.Rtti_Rectangle):
            i = item

            property = self.variantManager.addProperty(QVariant.Color, self.tr("Brush Color"))
            property.setValue(i.brush().color())
            self.addProperty(property, "brush")

            property = self.variantManager.addProperty(QVariant.Color, self.tr("Pen Color"))
            property.setValue(i.pen().color())
            self.addProperty(property, "pen")

            property = self.variantManager.addProperty(QVariant.Size, self.tr("Size"))
            property.setValue(i.size())
            self.addProperty(property, "size")
        elif (item.rtti() == RttiValues.Rtti_Line):
            i = item

            property = self.variantManager.addProperty(QVariant.Color, self.tr("Pen Color"))
            property.setValue(i.pen().color())
            self.addProperty(property, "pen")

            property = self.variantManager.addProperty(QVariant.Point, self.tr("Vector"))
            property.setValue(i.endPoint())
            self.addProperty(property, "endpoint")
        elif (item.rtti() == RttiValues.Rtti_Ellipse):
            i = item

            property = self.variantManager.addProperty(QVariant.Color, self.tr("Brush Color"))
            property.setValue(i.brush().color())
            self.addProperty(property, "brush")

            property = self.variantManager.addProperty(QVariant.Size, self.tr("Size"))
            property.setValue(QSize(i.width(), i.height()))
            self.addProperty(property, "size")
        elif (item.rtti() == RttiValues.Rtti_Text):
            i = item

            property = self.variantManager.addProperty(QVariant.Color, self.tr("Color"))
            property.setValue(i.color())
            self.addProperty(property, "color")

            property = self.variantManager.addProperty(QVariant.String, self.tr("Text"))
            property.setValue(i.text())
            self.addProperty(property, "text")

            property = self.variantManager.addProperty(QVariant.Font, self.tr("Font"))
            property.setValue(i.font())
            self.addProperty(property, "font")

    def addProperty(self, property, id):
        self.propertyToId[property] = id
        self.idToProperty[id] = property
        item = self.propertyEditor.addProperty(property)
        if (self.idToExpanded.contains(id)):
            self.propertyEditor.setExpanded(item, self.idToExpanded[id])

    def valueChanged(self, property, value):
        if (not self.propertyToId.contains(property)):
            return

        if (not self.currentItem or self.currentItem.isNone()):
            return

        id = self.propertyToId[property]
        if (id == "xpos"):
            self.currentItem.setX(value)
        elif (id == "ypos"):
            self.currentItem.setY(value)
        elif (id == "zpos"):
            self.currentItem.setZ(value)
        elif (id == "text"):
            if (self.currentItem.rtti() == RttiValues.Rtti_Text):
                i = self.currentItem
                i.setText(value)
        elif (id == "color"):
            if (self.currentItem.rtti() == RttiValues.Rtti_Text):
                i = self.currentItem
                i.setColor(value)
        elif (id == "brush"):
            if (self.currentItem.rtti() == RttiValues.Rtti_Rectangle or self.currentItem.rtti() == RttiValues.Rtti_Ellipse):
                i = self.currentItem
                b = QBrush(i.brush())
                b.setColor(value)
                i.setBrush(b)
        elif (id == "pen"):
            if (self.currentItem.rtti() == RttiValues.Rtti_Rectangle or self.currentItem.rtti() == RttiValues.Rtti_Line):
                i = self.currentItem
                p = QPen(i.pen())
                p.setColor(value)
                i.setPen(p)
        elif (id == "font"):
            if (self.currentItem.rtti() == RttiValues.Rtti_Text):
                i = self.currentItem
                i.setFont(value)
        elif (id == "endpoint"):
            if (self.currentItem.rtti() == RttiValues.Rtti_Line):
                i = self.currentItem
                p = value
                i.setPoints(i.startPoint().x(), i.startPoint().y(), p.x(), p.y())
        elif (id == "size"):
            if (self.currentItem.rtti() == RttiValues.Rtti_Rectangle):
                i = self.currentItem
                s = value
                i.setSize(s.width(), s.height())
            elif (self.currentItem.rtti() == RttiValues.Rtti_Ellipse):
                i = self.currentItem
                s = value
                i.setSize(s.width(), s.height())
        self.canvas.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()

    sys.exit(app.exec())

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
import os
filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(filePath,'QtProperty'))
sys.path.append(os.path.join(filePath,'libqt5'))
#print(sys.path)
from qtpy.QtWidgets import QApplication, QMainWindow, QAction, QDockWidget
from qtpy.QtCore import (
    QPoint, 
    Qt, 
    QSize, 
    Signal
    )
from random import random
from qtpy.QtGui import QColor, QPen, QFont, QBrush
from pyqtcore import QMap
from qttreepropertybrowser import QtTreePropertyBrowser
from qtpropertymanager import (
    QtDoublePropertyManager, 
    QtStringPropertyManager, 
    QtColorPropertyManager, 
    QtFontPropertyManager, 
    QtPointPropertyManager,
    QtSizePropertyManager
)
from qteditorfactory import (
    QtDoubleSpinBoxFactory, 
    QtCheckBoxFactory, 
    QtSpinBoxFactory, 
    QtLineEditFactory, 
    QtEnumEditorFactory
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

        self.doubleManager = QtDoublePropertyManager(self)
        self.stringManager = QtStringPropertyManager(self)
        self.colorManager = QtColorPropertyManager(self)
        self.fontManager = QtFontPropertyManager(self)
        self.pointManager = QtPointPropertyManager(self)
        self.sizeManager = QtSizePropertyManager(self)

        self.doubleManager.valueChangedSignal.connect(self.valueChanged)
        self.stringManager.valueChangedSignal.connect(self.valueChanged)
        self.colorManager.valueChangedSignal.connect(self.valueChanged)
        self.fontManager.valueChangedSignal.connect(self.valueChanged)
        self.pointManager.valueChangedSignal.connect(self.valueChanged)
        self.sizeManager.valueChangedSignal.connect(self.valueChanged)

        doubleSpinBoxFactory = QtDoubleSpinBoxFactory(self)
        checkBoxFactory = QtCheckBoxFactory(self)
        spinBoxFactory = QtSpinBoxFactory(self)
        lineEditFactory = QtLineEditFactory(self)
        comboBoxFactory = QtEnumEditorFactory(self)

        self.canvas = QtCanvas(800, 600)
        self.canvasView = CanvasView(self.canvas, self)
        self.setCentralWidget(self.canvasView)

        dock = QDockWidget(self)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        self.propertyEditor = QtTreePropertyBrowser(dock)
        self.propertyEditor.setFactoryForManager(self.doubleManager, doubleSpinBoxFactory)
        self.propertyEditor.setFactoryForManager(self.stringManager, lineEditFactory)
        self.propertyEditor.setFactoryForManager(self.colorManager.subIntPropertyManager(), spinBoxFactory)
        self.propertyEditor.setFactoryForManager(self.fontManager.subIntPropertyManager(), spinBoxFactory)
        self.propertyEditor.setFactoryForManager(self.fontManager.subBoolPropertyManager(), checkBoxFactory)
        self.propertyEditor.setFactoryForManager(self.fontManager.subEnumPropertyManager(), comboBoxFactory)
        self.propertyEditor.setFactoryForManager(self.pointManager.subIntPropertyManager(), spinBoxFactory)
        self.propertyEditor.setFactoryForManager(self.sizeManager.subIntPropertyManager(), spinBoxFactory)
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

        self.doubleManager.setValue(self.idToProperty["xpos"], item.x())
        self.doubleManager.setValue(self.idToProperty["ypos"], item.y())
        self.doubleManager.setValue(self.idToProperty["zpos"], item.z())

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

        property = self.doubleManager.addProperty(self.tr("Position X"))
        self.doubleManager.setRange(property, 0, self.canvas.width())
        self.doubleManager.setValue(property, item.x())
        self.addProperty(property, "xpos")

        property = self.doubleManager.addProperty(self.tr("Position Y"))
        self.doubleManager.setRange(property, 0, self.canvas.height())
        self.doubleManager.setValue(property, item.y())
        self.addProperty(property, "ypos")

        property = self.doubleManager.addProperty(self.tr("Position Z"))
        self.doubleManager.setRange(property, 0, 256)
        self.doubleManager.setValue(property, item.z())
        self.addProperty(property, "zpos")

        if (item.rtti() == RttiValues.Rtti_Rectangle):
            i = item

            property = self.colorManager.addProperty(self.tr("Brush Color"))
            self.colorManager.setValue(property, i.brush().color())
            self.addProperty(property, "brush")

            property = self.colorManager.addProperty(self.tr("Pen Color"))
            self.colorManager.setValue(property, i.pen().color())
            self.addProperty(property, "pen")

            property = self.sizeManager.addProperty(self.tr("Size"))
            self.sizeManager.setValue(property, i.size())
            self.addProperty(property, "size")
        elif (item.rtti() == RttiValues.Rtti_Line):
            i = item

            property = self.colorManager.addProperty(self.tr("Pen Color"))
            self.colorManager.setValue(property, i.pen().color())
            self.addProperty(property, "pen")

            property = self.pointManager.addProperty(self.tr("Vector"))
            self.pointManager.setValue(property, i.endPoint())
            self.addProperty(property, "endpoint")
        elif (item.rtti() == RttiValues.Rtti_Ellipse):
            i = item

            property = self.colorManager.addProperty(self.tr("Brush Color"))
            self.colorManager.setValue(property, i.brush().color())
            self.addProperty(property, "brush")

            property = self.sizeManager.addProperty(self.tr("Size"))
            self.sizeManager.setValue(property, QSize(i.width(), i.height()))
            self.sizeManager.setRange(property, QSize(0, 0), QSize(1000, 1000))
            self.addProperty(property, "size")
        elif (item.rtti() == RttiValues.Rtti_Text):
            i = item

            property = self.colorManager.addProperty(self.tr("Color"))
            self.colorManager.setValue(property, i.color())
            self.addProperty(property, "color")

            property = self.stringManager.addProperty(self.tr("Text"))
            self.stringManager.setValue(property, i.text())
            self.addProperty(property, "text")

            property = self.fontManager.addProperty(self.tr("Font"))
            self.fontManager.setValue(property, i.font())
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
        tp = type(value)
        id = self.propertyToId[property]
        if tp == float:
            if (id == "xpos"):
                self.currentItem.setX(value)
            elif (id == "ypos"):
                self.currentItem.setY(value)
            elif (id == "zpos"):
                self.currentItem.setZ(value)
        elif tp == str:
            if (id == "text"):
                if (self.currentItem.rtti() == RttiValues.Rtti_Text):
                    i = self.currentItem
                    i.setText(value)
        elif tp == QColor:
            if (id == "color"):
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
        elif tp == QFont:
            if (id == "font"):
                if (self.currentItem.rtti() == RttiValues.Rtti_Text):
                    i = self.currentItem
                    i.setFont(value)
        elif tp == QPoint:
            if (self.currentItem.rtti() == RttiValues.Rtti_Line):
                i = self.currentItem
                if (id == "endpoint"):
                    i.setPoints(i.startPoint().x(), i.startPoint().y(), value.x(), value.y())
        elif tp == QSize:
            if (id == "size"):
                if (self.currentItem.rtti() == RttiValues.Rtti_Rectangle):
                    i = self.currentItem
                    i.setSize(value.width(), value.height())
                elif (self.currentItem.rtti() == RttiValues.Rtti_Ellipse):
                    i = self.currentItem
                    i.setSize(value.width(), value.height())
        self.canvas.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()

    sys.exit(app.exec())

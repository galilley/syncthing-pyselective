# -*- coding: utf-8 -*-

try:
    from PySide import QtCore
    from PySide import QtWidgets
except:
    from PyQt5.QtCore import pyqtSlot as Slot
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets

# https://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html

class TreeItem:
    def __init__(self, data = [], parent = None):
        self._parentItem = parent
        self._itemData = data
        self._childItems = []
    
    def appendChild(self, child):
        if isinstance(child, TreeItem):
            self._childItems.append(child)
        else:
            raise TypeError('Child\'s type is {0}, but must be TreeItem'.format(str(type(child))))

    def child(self, row):
        if row < 0 or row >= len(self._childItems):
            return None
        return self._childItems[row]

    def childCount(self):
        return len(self._childItems)

    def columnCount(self):
        return len(self._itemData)

    def data(self, column):
        if column < 0 or column >= len(self._itemData):
            return None
        return self._itemData[column]
    
    def row(self):
        if self._parentItem is not None:
            return self._parentItem._childItems.index(self)
        return 0
    
    def parentItem(self):
        return self._parentItem



class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data = [], parent = None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._rootItem = TreeItem(['Title', 'Summary'])
        self.setupModelData(data, self._rootItem)

    def data(self, index, role):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None
        
        item = index.internalPointer()
        return item.data(index.column())
    
    def flags(self, index):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return super().flags(index)

    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._rootItem.data(section);
        return None
    
    def index(self, row, column, parent = QtCore.QModelIndex()):
        if not isinstance(parent, QtCore.QModelIndex):
            raise TypeError('Parent\'s type is {0}, but must be QModelIndex'.format(str(type(parent))))
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
             parentItem = self._rootItem
        else:
             parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem is not None:
            return self.createIndex(row, column, childItem);
        return QtCore.QModelIndex();

    def parent(self, index):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not index.isValid():
            return QtCore.QModelIndex();

        childItem = index.internalPointer()
        parentItem = childItem.parentItem()

        if parentItem is self._rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)
    
    def rowCount(self, parent = QtCore.QModelIndex()):
        if not isinstance(parent, QtCore.QModelIndex):
            raise TypeError('Parent\'s type is {0}, but must be QModelIndex'.format(str(type(parent))))
        if parent.column() > 0:
            return 0;
        
        if not parent.isValid():
             parentItem = self._rootItem
        else:
             parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent = QtCore.QModelIndex()):
        if not isinstance(parent, QtCore.QModelIndex):
            raise TypeError('Parent\'s type is {0}, but must be QModelIndex'.format(str(type(parent))))
        if parent.isValid():
            return parent.internalPointer().columnCount()
        return self._rootItem.columnCount()
    
    def setupModelData(self, data, parent):
        parent.appendChild(TreeItem([1,2], parent))
        parent.child(0).appendChild(TreeItem([3,4], parent.child(0)))
        pass




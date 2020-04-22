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
        self.checkstate = QtCore.Qt.Unchecked
    
    def appendChild(self, child):
        if isinstance(child, TreeItem):
            self._childItems.append(child)
        else:
            raise TypeError('Child\'s type is {0}, but must be TreeItem'.format(str(type(child))))

    def child(self, row):
        if row < -len(self._childItems) or row >= len(self._childItems):
            return None
        return self._childItems[row]

    def childCount(self):
        return len(self._childItems)
    
    def columnCount(self):
        return len(self._itemData)

    def data(self, column):
        if column < -len(self._itemData) or column >= len(self._itemData):
            return None
        return self._itemData[column]
    
    def setData(self, column, value):
        if column < -len(self._itemData) or column >= len(self._itemData):
            return False
        self._itemData[column] = value
        print(type(value), value)
        return True
    
    def row(self):
        if self._parentItem is not None:
            return self._parentItem._childItems.index(self)
        return 0
    
    def parentItem(self):
        return self._parentItem



class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data = [], parent = None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._rootItem = TreeItem(['Title', 'Size', 'Modified'])
        self._setupModelData(data, self._rootItem)

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item is not None:
                return item

        return self.rootItem

    def data(self, index, role):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not index.isValid():
            return None

        item = index.internalPointer()
        
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            return item.checkstate

        if role != QtCore.Qt.DisplayRole:
            return None
        
        return item.data(index.column())
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if index.column() == 0:
            if role == QtCore.Qt.CheckStateRole:
                self.getItem(index).checkstate = value
                print(value)
                self.dataChanged.emit(index, index)
                return True
            else:
                return False

        return super().setData(index, value, role)
    
    def flags(self, index):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        rv = super().flags(index)
        if index.column() == 0:
            rv |= QtCore.Qt.ItemIsUserCheckable
            #rv |= QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable
        return rv

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
             parentItem = self.getItem(parent)

        childItem = parentItem.child(row)
        if childItem is not None:
            return self.createIndex(row, column, childItem);
        return QtCore.QModelIndex();

    def parent(self, index):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not index.isValid():
            return QtCore.QModelIndex();

        parentItem = self.getItem(index).parentItem()

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
             parentItem = self.getItem(parent)

        return parentItem.childCount()

    def columnCount(self, parent = QtCore.QModelIndex()):
        if not isinstance(parent, QtCore.QModelIndex):
            raise TypeError('Parent\'s type is {0}, but must be QModelIndex'.format(str(type(parent))))
        if parent.isValid():
            return self.getItem(parent).columnCount()
        return self._rootItem.columnCount()

    
    def _setupModelData(self, data, parent = None):
        if parent is None:
            parent = self._rootItem
        if not isinstance(parent, TreeItem):
            raise TypeError('Parent\'s type is {0}, but must be TreeItem'.format(str(type(parent))))
        if not isinstance(data, list):
            raise TypeError('data\'s type is {0}, but must be list'.format(str(type(data))))
        
        for v in data:
            ch = TreeItem([
                    v['name'], 
                    v['size'] if 'size' in v else None, 
                    QtCore.QDateTime.fromString( v['modified'], QtCore.Qt.ISODateWithMs) if 'modified' in v else None,
                ], parent)
            ignored = v['ignored'] if 'ignored' in v else True
            ch.checkstate = QtCore.Qt.Checked if not ignored else QtCore.Qt.Unchecked
            parent.appendChild(ch)

            if v['isfolder']:
                self._setupModelData(v['content'], ch)
    
    def fullItemName(self, index):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        fin = ''
        while index.isValid():
            fin = self.itemData(index)[0] + '/' + fin
            pi = self.parent(index)
            if not pi.isValid():
                break;
            index = pi

        return fin

    def rowNamesList(self, index):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        rv = []
        for ch in self.getItem(index)._childItems:
            rv.append({'name': ch._itemData[0]})
        return rv

    def updateSubSection(self, index, data):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not isinstance(data, list):
            raise TypeError('data\'s type is {0}, but must be list'.format(str(type(data))))
        
        for ch in self.getItem(index)._childItems:
            for v in data: #TODO shold be dict of dicts to avoid second for
                if ch.data(0) == v['name']:
                    ch._itemData = [
                            v['name'], 
                            v['size'] if 'size' in v else None, 
                            QtCore.QDateTime.fromString( v['modified'], QtCore.Qt.ISODateWithMs) if 'modified' in v else None,
                        ]
                    ignored = v['ignored'] if 'ignored' in v else True
                    ch.checkstate = QtCore.Qt.Checked if not ignored else QtCore.Qt.Unchecked
        
        indfirst = self.index(0, 0, index)
        indlast = self.index(self.rowCount(index), self.columnCount(index), index)
        super().dataChanged.emit(indfirst, indlast, [QtCore.Qt.DisplayRole])





    



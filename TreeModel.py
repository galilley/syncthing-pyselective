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
        self._checkedItemsCount = 0
        self._checkedPartiallyCount = 0
        self._checkstate = QtCore.Qt.Unchecked
        self._changed = False
        self._initcheckstate = None
    
    def appendChild(self, child):
        if isinstance(child, TreeItem):
            self._childItems.append(child)
            if child.getCheckState() == QtCore.Qt.Checked:
                self._checkedItemsCount += 1
            if child.getCheckState() == QtCore.Qt.PartiallyChecked:
                self._checkedPartiallyCount += 1
        else:
            raise TypeError('Child\'s type is {0}, but must be TreeItem'.format(str(type(child))))

    def child(self, row):
        if row < -len(self._childItems) or row >= len(self._childItems):
            return None
        return self._childItems[row]

    def childCount(self):
        return len(self._childItems)
    
    def childNames(self):
        rv = []
        for ch in self._childItems:
            rv.append(ch._itemData[0])
        return rv
    
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
        return True

    def setCheckState(self, st):
        if st != self._checkstate and \
                self._parentItem is not None and \
                self in self._parentItem._childItems:
            if st == QtCore.Qt.Checked:
                self._parentItem._checkedItemsCount += 1
                if self._checkstate == QtCore.Qt.PartiallyChecked:
                    self._parentItem._checkedPartiallyCount -= 1
            elif st == QtCore.Qt.PartiallyChecked:
                self._parentItem._checkedPartiallyCount += 1
                if self._checkstate == QtCore.Qt.Checked:
                    self._parentItem._checkedItemsCount -= 1
            else:
                if self._checkstate == QtCore.Qt.Checked:
                    self._parentItem._checkedItemsCount -= 1
                else:
                    self._parentItem._checkedPartiallyCount -= 1
            self._checkstate = st

    def getCheckState(self):
        return self._checkstate

    def setChanged(self):
        'In the model should be called *before* set actual state'
        if self._initcheckstate is None:
            self._initcheckstate = self._checkstate
        self._changed = True

    def isChanged(self):
        if self._changed:
            #False if changed but returned back
            return True if self._initcheckstate != self._checkstate else False 
        return False

    def updateCheckState(self):
        '''
        compare checked count with child count and return True if checkstate was changed, 
        the parent state also must be updated in this case
        '''
        if self._checkedItemsCount == 0 and self._checkedPartiallyCount == 0:
            self.setCheckState(QtCore.Qt.Unchecked)
            return True
        
        elif self.childCount() != self._checkedItemsCount:
            self.setCheckState(QtCore.Qt.PartiallyChecked)
            return True

        elif self.childCount() == self._checkedItemsCount:
            self.setCheckState(QtCore.Qt.Checked)
            return True

        return False
    
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
        self._changedList = []

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item is not None:
                return item

        return self._rootItem

    def data(self, index, role):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not index.isValid():
            return None

        item = index.internalPointer()
        
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            return item.getCheckState()

        if role != QtCore.Qt.DisplayRole:
            return None
        
        return item.data(index.column())
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if index.column() == 0:
            if role == QtCore.Qt.CheckStateRole:
                item = self.getItem(index)
                item.setChanged()
                item.setCheckState(value)
                self._addToChangedList(item)
                self.dataChanged.emit(index, index)
                # update parents
                index = self.parent(index)
                while index.isValid():
                    item = self.getItem(index)
                    if not item.updateCheckState():
                        break
                    self._addToChangedList(item)
                    self.dataChanged.emit(index, index)
                    index = self.parent(index)
                return True
            else:
                return False

        return super().setData(index, value, role)

    def _addToChangedList(self, item):
        fn = "/" + self.fullItemName(item)
        if not fn in self._changedList:
            self._changedList.append(fn)
        #elif fn in self._changedList:
        #    self._changedList.remove(fn)

    def flags(self, index):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        rv = super().flags(index)
        if index.column() == 0:
            rv |= QtCore.Qt.ItemIsUserCheckable
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
        #TODO use updateSubSection() here
        for v in data:
            if parent is self._rootItem and v['name'] == '.stignoreglobal': #additional ignore list may be needed
                continue
            ch = TreeItem([
                    v['name'], 
                    v['size'] if ('size' in v and v['size'] != 0) else None, 
                    QtCore.QDateTime.fromString( v['modified'], QtCore.Qt.ISODateWithMs) if 'modified' in v else None,
                ], parent)
            ignored = v['ignored'] if 'ignored' in v else True
            partial = v['partial'] if 'partial' in v else False
            parent.appendChild(ch)
            ch.setCheckState(QtCore.Qt.PartiallyChecked if partial else QtCore.Qt.Checked if not ignored else QtCore.Qt.Unchecked)

            if v['isfolder']:
                self._setupModelData(v['content'], ch)
    
    def fullItemName(self, item):
        if not isinstance(item, TreeItem):
            raise TypeError('Index\'s type is {0}, but must be TreeItem'.format(str(type(item))))
        fin = item.data(0)
        item = item.parentItem()
        while item is not self._rootItem:
            fin = item.data(0) + '/' + fin
            item = item.parentItem()
        return fin

    def rowNamesList(self, index):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        rv = []
        for ch in self.getItem(index)._childItems:
            rv.append({\
                    'name': ch._itemData[0], \
                    'isfolder': True if ch.childCount() > 0 else False, \
                    'content': list(map(lambda x: {'name': x} , ch.childNames()))})
        return rv

    def updateSubSection(self, index, data):
        if not isinstance(index, QtCore.QModelIndex):
            raise TypeError('Index\'s type is {0}, but must be QModelIndex'.format(str(type(index))))
        if not isinstance(data, list):
            raise TypeError('data\'s type is {0}, but must be list'.format(str(type(data))))
        
        isparentchecked = True if self.getItem(index).getCheckState() == QtCore.Qt.Checked else False
        for ch in self.getItem(index)._childItems:
            for v in data: #TODO should be dict of dicts to avoid second for
                if ch._itemData[0] == v['name']:
                    ch._itemData = [
                            v['name'], 
                            v['size'] if ('size' in v and v['size'] != 0) else None, 
                            QtCore.QDateTime.fromString( v['modified'], QtCore.Qt.ISODateWithMs) if 'modified' in v else None,
                        ]
                    ignored = v['ignored'] if 'ignored' in v else True
                    partial = v['partial'] if 'partial' in v else False
                    if isparentchecked:
                        ch.setChanged()
                        self._addToChangedList(ch)
                    ch.setCheckState( \
                            QtCore.Qt.PartiallyChecked if partial else \
                            QtCore.Qt.Checked if not ignored else \
                            QtCore.Qt.Unchecked)
        
        self.getItem(index).updateCheckState()
        super().dataChanged.emit(index, index, [QtCore.Qt.DisplayRole])
        
        indfirst = self.index(0, 0, index)
        indlast = self.index(self.rowCount(index), self.columnCount(index), index)
        super().dataChanged.emit(indfirst, indlast, [QtCore.Qt.DisplayRole])
        
    def checkedPathList(self, plist = None, parent = None, pref = '/'):
        if plist is None:
            plist = []
        if parent is None:
            parent = self._rootItem
        for item in parent._childItems:
            if pref == '/' and item.data(0) == '.stignoreglobal': #additional ignore list may be needed
                continue
            if item.getCheckState() == QtCore.Qt.Checked:
                plist.append(pref + item.data(0))
            else:
                if item.childCount() > 0:
                    self.checkedPathList(plist, item, pref + item.data(0) + '/')
        return plist
    
    def changedPathList(self, plist = None, parent = None, pref = '/'):
        return self._changedList




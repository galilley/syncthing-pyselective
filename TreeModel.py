# -*- coding: utf-8 -*-

try:
    from PySide import QtCore
    from PySide import QtWidgets
except:
    from PyQt5.QtCore import pyqtSlot as Slot
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets

class TreeItem:
    def __init__(self):
        #QList<TreeItem*> m_childItems;
        #QList<QVariant> m_itemData;
        #TreeItem *m_parentItem;
        self._childItems = []
        self._itemData = []
        self._parentItem = None

    def appendChild(self, child):
    #def appendChild(TreeItem *child):
        pass

    def child(self, row):
    #def TreeItem *child(int row):
        pass

    def childCount(self):
        return 0

    def columnCount(self):
        return 0

    def data(self, column):
        pass
    #QVariant data(int column) const;
    
    def row(self):
        return 0
    
    def parentItem(self):
        pass
    #TreeItem *parentItem();


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent = None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.rootItem = TreeItem()

    #QVariant data(const QModelIndex &index, int role) const override;
    def data(self, index, role):
        return None
    
    #Qt::ItemFlags flags(const QModelIndex &index) const override;
    def flags(self, index):
        pass

    #QVariant headerData(int section, Qt::Orientation orientation,
    #                    int role = Qt::DisplayRole) const override;
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        pass
    
    #QModelIndex index(int row, int column,
    #                  const QModelIndex &parent = QModelIndex()) const override;
    def index(self, row, column, parent = QtCore.QModelIndex()):
        return None

    #QModelIndex parent(const QModelIndex &index) const override;
    def parent(self, index):
        return None
    
    def rowCount(self, parent = QtCore.QModelIndex()):
        return 0

    def columnCount(self, parent = QtCore.QModelIndex()):
        return 0



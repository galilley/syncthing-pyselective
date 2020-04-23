# -*- coding: utf-8 -*-

try:
    from PySide import QtCore
    from PySide import QtWidgets
except:
    from PyQt5.QtCore import pyqtSlot as Slot
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets

from SyncthingAPI import SyncthingAPI
from TreeModel import TreeModel

# use helloword from https://evileg.com/ru/post/63/
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setMinimumSize(QtCore.QSize(350, 350))
        self.setWindowTitle("Syncthing PySelective")
        central_widget = QtWidgets.QWidget(self)
        self.cw = central_widget
        self.setCentralWidget(central_widget)
 
        grid_layout = QtWidgets.QGridLayout(central_widget)
 
        title = QtWidgets.QLabel("Choise the folder:", self)
        title.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(title, 0, 0)

        self.cbfolder = QtWidgets.QComboBox(central_widget)
        self.cbfolder.currentIndexChanged[int].connect(self.folderSelected)
        grid_layout.addWidget( self.cbfolder, 1, 0)

        self.tv = QtWidgets.QTreeView(central_widget)
        grid_layout.addWidget( self.tv, 2, 0)
        self.tm = TreeModel(parent = central_widget)
        self.tv.setModel(self.tm)
        self.tv.header().setSectionsMovable(True)
        self.tv.header().setFirstSectionMovable(True)
        self.tv.expanded.connect(self.updateSectionInfo)
        #TODO
        #self.tv.setSelectionModel(self.tsm)

        pb = QtWidgets.QPushButton("Get file tree", central_widget)
        pb.clicked.connect(self.btGetClicked)
        grid_layout.addWidget( pb, 3, 0)
        
        pb = QtWidgets.QPushButton("Submit changes", central_widget)
        pb.clicked.connect(self.btSubmitClicked)
        grid_layout.addWidget( pb, 4, 0)
        
        #self.te = QtWidgets.QTextEdit(central_widget)
        #grid_layout.addWidget( self.te, 5, 0)
 
        exit_action = QtWidgets.QAction("&Exit", self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QtWidgets.qApp.quit)
        file_menu = self.menuBar()
        file_menu.addAction(exit_action)

        self.syncapi = SyncthingAPI()
        self.currentfid = None

    def extendFileInfo(self, fid, l, path = ''):
        for v in l:
            extd = self.syncapi.getFileInfoExtended( fid, path+v['name'])
            v['ignored'] = extd['local']['ignored']
            v['modified'] = extd['local']['modified']
            v['size'] = extd['local']['size']

    def btGetClicked(self):
        d = self.syncapi.getFoldersDict()
        self.foldsdict = d
        self.cbfolder.clear()
        for k in d.keys():
            self.cbfolder.addItem(d[k]['label'], k)

    def btSubmitClicked(self):
        if self.currentfid is not None:
            il = self.tm.checkedPathList()
            self.syncapi.setIgnoreSelective(self.currentfid, il)

    def folderSelected(self, index):
        if index < 0: #avoid signal from empty box
            return

        fid = self.cbfolder.itemData(index)
        self.currentfid = fid
        l = self.syncapi.browseFolder(fid)
        self.extendFileInfo(fid, l)
        self.tm = TreeModel(l, self.cw)
        self.tv.setModel(self.tm)

    def updateSectionInfo(self, index):
        l = self.tm.rowNamesList(index)
        self.extendFileInfo(self.currentfid, l, self.tm.fullItemName(index))
        self.tm.updateSubSection(index, l)



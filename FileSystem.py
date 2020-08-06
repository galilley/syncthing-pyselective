# -*- coding: utf-8 -*-

try:
    from PySide2 import QtCore
except:
    from PyQt5 import QtCore

import ItemProperty as iprop

import logging
logger = logging.getLogger("PySel.FileSystem")


class FileSystem:
    def __init__(self):
        pass

    def extendByLocal(self, l, path):
        logger.debug("extendByLocal path: {}".format(path))
        d = QtCore.QDir(path)
        # d.setFilter(QtCore.QDir.NoDotAndDotDot)
        dl = d.entryList()

        # dirty hack as NoDotAndDotDot do not work in PyQt5 5.12.8
        if '.' in dl:
            dl.remove('.')
        if '..' in dl:
            dl.remove('..')

        newfiles = dl[:]

        for val in l:
            if val['name'] in dl:
                if 'syncstate' not in val or val['syncstate'] is not iprop.SyncState.unknown:
                    newfiles.remove(val['name'])

        for fn in newfiles:
            fi = QtCore.QFileInfo(d.filePath(fn))
            logger.debug("New file: {}".format(fn))
            item = {'name' : fn}
            if fi.isDir():
                item['isfolder'] = True
                cl = QtCore.QDir(d.filePath(fn)).entryList()
                cl.remove('.')
                cl.remove('..')
                cont = []
                for fnc in cl:
                    cont.append({'name' : fnc,
                                'isfolder' : QtCore.QFileInfo(d.filePath(fnc)).isDir(),
                                'syncstate' : iprop.SyncState.unknown})
                item['content'] = cont
                logger.debug("    Content: {}".format(cont))
            else:
                item['isfolder'] = False
            item['size'] = fi.size()
            item['modified'] = fi.fileTime(QtCore.QFileDevice.FileModificationTime)
            item['syncstate'] = iprop.SyncState.newlocal
            l.append(item)



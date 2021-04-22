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
                item['type'] = iprop.Type.DIRECTORY.name
                cl = QtCore.QDir(d.filePath(fn)).entryList()
                cl.remove('.')
                cl.remove('..')
                cont = []
                for fnc in cl:
                    cont.append({'name' : fnc,
                                'type' : \
                                    iprop.Type.DIRECTORY.name if QtCore.QFileInfo(d.filePath(fnc)).isDir() \
                                        else iprop.Type.FILE.name,
                                'syncstate' : iprop.SyncState.unknown})
                item['children'] = cont
                logger.debug("    Children: {}".format(cont))
            else:
                item['type'] = iprop.Type.FILE.name
            item['size'] = fi.size()
            item['modified'] = fi.lastModified()
            item['syncstate'] = iprop.SyncState.newlocal
            l.append(item)



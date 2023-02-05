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

    def extendByLocal(self, l, path, psyncstate=iprop.SyncState.unknown):
        '''
        There are four cases for extension of remote file tree:
            1. none - 'syncstate' = syncing
            2. new local - file exists locally and is missing remotely (previous state is unknown)
            3. conflict - local file differs from a remote
            4. exists -  local file is the same as remote
        Besides the function lockup the children of the each item
        '''
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

        # looking for new local files, works only for the root directory
        # as further all new files has unknown syncstats
        for val in l:
            if val['name'] in dl:
                newfiles.remove(val['name'])

        itemstoremove = []
        for item in l:
            # update existing items
            if ('syncstate' not in item or \
                    item['syncstate'] is iprop.SyncState.unknown or \
                    item['syncstate'] is iprop.SyncState.newlocal or \
                    item['syncstate'] is iprop.SyncState.partial) and \
                    item['name'] in dl:
                fi = QtCore.QFileInfo(d.filePath(item['name']))
                if fi.isDir():
                    logger.debug("Update dir: {}".format(item['name']))
                    cil = QtCore.QDir(d.filePath(item['name'])).entryInfoList()
                    if 'children' in item:
                        cont = item['children']
                    else:
                        cont = []
                    for fic in cil:
                        if fic.fileName() == '.' or fic.fileName() == '..':
                            continue

                        iscont = False
                        for ch in cont:  # TODO dict of dicts to avoid for
                            if ch['name'] == fic.fileName():
                                iscont = True
                                break
                        if iscont:
                            continue

                        cont.append({'name': fic.fileName(),
                                    'type':
                                        iprop.Type.DIRECTORY.name if fic.isDir() \
                                            else iprop.Type.FILE.name,
                                    'syncstate': iprop.SyncState.unknown})
                    item['children'] = cont
                    logger.debug("    Children: {}".format(cont))
                else:
                    logger.debug("Update file: {}".format(item['name']))
                if item['syncstate'] is iprop.SyncState.unknown:
                    item['size'] = int(fi.size())
                    item['modified'] = fi.lastModified()
                    item['syncstate'] = iprop.SyncState.newlocal

            # check files ignored remotely but exists locally
            elif 'syncstate' in item and \
                    item['syncstate'] is iprop.SyncState.ignored and \
                    item['name'] in dl:
                fi = QtCore.QFileInfo(d.filePath(item['name']))
                if iprop.Type[item['type']] is iprop.Type.DIRECTORY:
                    item['syncstate'] = iprop.SyncState.exists
                elif item['size'] == fi.size() and \
                        item['modified'].secsTo(fi.lastModified()) == 0:
                    item['syncstate'] = iprop.SyncState.exists
                else:
                    item['syncstate'] = iprop.SyncState.conflict
                    logger.debug("item {} considered as conflicted:\n\t{} != {} or {} != 0".format(item['name'], item['size'], fi.size(), item['modified'].secsTo(fi.lastModified())))

            # fill list of locally removed files
            elif 'syncstate' in item and \
                    (item['syncstate'] is iprop.SyncState.unknown or \
                    item['syncstate'] is iprop.SyncState.newlocal) and \
                    item['name'] not in dl:
                itemstoremove.append(item)

        # remove removed files from the list
        for item in itemstoremove:
            l.remove(item)
        del(itemstoremove)

        # add new files into the list
        for fn in newfiles:
            fi = QtCore.QFileInfo(d.filePath(fn))
            item = {'name': fn}
            if fi.isDir():
                logger.debug("New dir: {}".format(fn))
                item['type'] = iprop.Type.DIRECTORY.name
                cil = QtCore.QDir(d.filePath(fn)).entryInfoList()
                cont = []
                for fic in cil:
                    if fic.fileName() == '.' or fic.fileName() == '..':
                        continue
                    cont.append({'name': fic.fileName(),
                                'type':
                                    iprop.Type.DIRECTORY.name if fic.isDir() \
                                        else iprop.Type.FILE.name,
                                'syncstate': iprop.SyncState.unknown})
                item['children'] = cont
                logger.debug("    Children: {}".format(cont))
            else:
                logger.debug("New file: {}".format(fn))
                item['type'] = iprop.Type.FILE.name
            item['size'] = int(fi.size())
            item['modified'] = fi.lastModified()
            # parent checked but the file absents in the database
            # so, it is ignored globally by other patterns
            if psyncstate == iprop.SyncState.syncing:
                item['syncstate'] = iprop.SyncState.globalignore
            else: # TODO, it can also be ignored globally in other states
                item['syncstate'] = iprop.SyncState.newlocal
            l.append(item)


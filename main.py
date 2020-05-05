#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import argparse

try:
    from PySide import QtWidgets
except:
    from PyQt5 import QtWidgets

from MainWindow import MainWindow

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'print more info about actions')
    parser.add_argument('-vv', '--debug', action = 'store_true', help = 'output all messages for debug purposes')
    parser.add_argument('-l', '--logfile', nargs='?', default = '', help = 'set log file name (default: pysel.log )')
    return parser

if __name__ == "__main__":
    import sys
    parser = createParser()
    namespace = parser.parse_args()
    loglev = logging.WARNING
    if namespace.debug:
        loglev = logging.DEBUG
    elif namespace.verbose:
        loglev = logging.INFO
    
    if namespace.logfile is None:
        logfile = "pysel.log"
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=loglev, filename = logfile)
    elif namespace.logfile != '':
        logfile = namespace.logfile
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=loglev, filename = logfile)
    else:
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=loglev)

    logger = logging.getLogger("PySel")
    logger.info('PySelective started')
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())


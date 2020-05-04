#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

try:
    from PySide import QtWidgets
except:
    from PyQt5 import QtWidgets

from MainWindow import MainWindow

if __name__ == "__main__":
    import sys
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.DEBUG)
    logger = logging.getLogger("PySel")
    logger.info('PySelective started')
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())


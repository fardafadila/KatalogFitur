# -*- coding: utf-8 -*-
"""
/***************************************************************************
 katalog_fiturDialog
                                 A QGIS plugin
 Plugin untuk memudahkan pengkatalogan fitur spasial
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-05-31
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Teknik Geodesi UGM
        email                : farda.fadila@mail.ugm.ac.id
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets, QtCore
#from qgis.core import QUrl
import os
import fnmatch
from pathlib import Path
import pystac
from .modules.get_files import get_files
from .modules.get_features import get_features
from .modules.make_cat import make_cat
from .modules.add_data import add_data
from .modules.search import search_data


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'katalog_fitur_dialog_base.ui'))


class katalog_fiturDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(katalog_fiturDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        opsi_cat = ["Katalog", "Subkatalog", "Koleksi"]
        self.strukturCombo.addItems(opsi_cat)

        ###Fungsi di pencarian
        self.search = search_data(self.inputSearch, self.folderSearch, self.inputKeyword, self.runSearch, self.atributSearch, self.tableSearch )
        self.folderSearch.clicked.connect(self.search.getCat)
        self.runSearch.clicked.connect(self.search.addData)
        self.atributSearch.clicked.connect(self.search.matchedSemantic)
        self.helpSearch.clicked.connect(self.search.getProp)
        #self.helpAdd.clicked.connect(self.help)

        ###Fungsi coba coba
        self.files = get_files(self.inputKeyword)       
        self.get_features = get_features(self.inputKeyword)
        #self.runSearch.clicked.connect(self.get_features.featuresFunction)
        #self.helpSearch.clicked.connect(self.files.mongoBing)

        ####Fungsi di create catalog
        self.make_cat = make_cat(self.strukturCombo, self.nama_katalog, self.deskripsi, self.folderpath_make, self.folder_make, self.catPath_make, self.catfile_make, self.produsen_make)
        if self.strukturCombo.currentText() == "Katalog":
            self.catPath_make.setEnabled(False)
            self.produsen_make.setEnabled(False)
            self.catfile_make.setEnabled(False)
        self.strukturCombo.currentTextChanged.connect(self.enableEdit)
        self.folder_make.clicked.connect(self.make_cat.outFolder)
        self.run_make.clicked.connect(self.make_cat.saveCat)
        self.catfile_make.clicked.connect(self.make_cat.getParent)
        self.helpMake.clicked.connect(self.make_cat.buatCatalog)

        ###Fungsi di add data
        self.add = add_data(self.inputkatalogAdd, self.folderAdd, self.fileinputAdd, self.fileAdd, self.dateAdd, self.fieldAdd, self.geojsonAdd, self.fiturpathAdd)
        self.folderAdd.clicked.connect(self.add.getCat)
        self.fileAdd.clicked.connect(self.add.getAtt)
        self.runAdd.clicked.connect(self.add.addingData)
        self.geojsonAdd.clicked.connect(self.add.getPath)
        #self.helpAdd.clicked.connect(self.add.cobaFungsi)
    def enableEdit(self):
        if self.strukturCombo.currentText() == "Katalog":
            self.catPath_make.setEnabled(False)
            self.produsen_make.setEnabled(False)
            self.catfile_make.setEnabled(False)
        elif self.strukturCombo.currentText() == "Subkatalog":
            self.catPath_make.setEnabled(True)
            self.produsen_make.setEnabled(False)
            self.catfile_make.setEnabled(True)
        else:
            self.catPath_make.setEnabled(True)
            self.produsen_make.setEnabled(True)
            self.catfile_make.setEnabled(True)
    
    """def help(self):
        view = QWebEngineView(self)
        view.load(QUrl('https://stacspec.org/en/tutorials/intro-to-stac/'))"""

        
import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
import json
import pystac
import pathlib
import urllib.parse
from pystac import Catalog, Collection, Extent
from qgis.PyQt.QtWidgets import QFileDialog


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'katalog_fitur', 'katalog_fitur_dialog_base.ui'))
FORM_CLASS, _ = uic.loadUiType(ui_path)


class make_cat(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, strukturCombo, nama_katalog, deskripsi, folderpath_make, folder_make):
        """Constructor."""
        super(make_cat, self).__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.strukturCombo= strukturCombo
        self.nama_katalog = nama_katalog
        self.deskripsi = deskripsi
        self.folderpath_make = folderpath_make
        self.folder_make = folder_make

 
    def outFolder(self):
        self.tipeKatalog=self.strukturCombo.currentText()
        project = QgsProject.instance()
        cache_folder_path = QgsProject.instance().homePath()
        self.folderpath_make.clear()
        # Get the text from the QLineEdit and use it as the shapefile name
        self.catLoc=  ""        
        if self.tipeKatalog == "Katalog" :
            self.catLoc, _ = QFileDialog.getSaveFileName(self, "Pilih lokasi penyimpanan katalog baru", cache_folder_path, "JSON (*.json)")
            self.folderpath_make.insert(self.catLoc)
        elif self.tipeKatalog == "Subkatalog":
            file_dialog = QFileDialog()
            file_dialog.setWindowTitle("Pilih file katalog yang sudah ada untuk menyimpan subkatalog")
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            file_dialog.setNameFilter("JSON files (*.json)")
            file_dialog.exec_()
            selected_files = file_dialog.selectedFiles()
            file_path = ""
            if len(selected_files) > 0:
                self.catLoc = selected_files[0]
            else:
                error_dialog = QtWidgets.QMessageBox()
                error_dialog.setWindowTitle("Error")
                error_dialog.setText("Pilih katalog yang sesuai untuk menyimpan subkatalog atau ubah struktur katalog!")
                error_dialog.exec_()
            self.folderpath_make.insert(self.catLoc)

        else:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Pilih lokasi penyimpanan yang sesuai!")
            error_dialog.exec_()
    
        return (self.catLoc)

    
    def saveCat(self):
        catalog_id = self.nama_katalog.text()
        catalog_description = self.deskripsi.text()
        self.tipeKatalog = self.strukturCombo.currentText()
        if self.tipeKatalog == "Katalog":
            print ( "mau  buat katalog")
            print ("katalog id    " + catalog_id)
            print ("katalog desk     " + catalog_description)
            self.new_katalog = Catalog(id=catalog_id, description=catalog_description)
            self.new_katalog.normalize_and_save(self.catLoc)
        if self.tipeKatalog == "Subkatalog":
            catalog_path = pathlib.Path(self.catLoc)
            with open(catalog_path, "r") as f:
                catalog_json = json.load(f)
                catalog = Catalog.from_dict(catalog_json)
            
            placeholder_extent = Extent(
                spatial=None,
                temporal=None
                )
            subcatalog = Collection(id=catalog_id, description=catalog_description, extent=placeholder_extent)
            catalog.add_child(subcatalog)
            with open(catalog_path, "w") as f:
                json.dump(catalog.to_dict(), f)









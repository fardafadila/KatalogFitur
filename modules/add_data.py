import os
from pydoc import describe
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5 import QtWidgets, QtCore
from qgis.core import QgsProject, QgsVectorLayer, QgsFields
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


class add_data(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, inputkatalog_add, folder_add, fileinput_add, file_add, add_date, fieldTable ):
        """Constructor."""
        super(add_data, self).__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.inputkatalog_add= inputkatalog_add
        self.folder_add= folder_add
        self.fileinput_add = fileinput_add
        self.file_add = file_add
        self.add_date = add_date
        self.fieldTable = fieldTable


    def getCat(self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Pilih katalog yang akan digunakan")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.exec_()
        selected_files = file_dialog.selectedFiles()
        file_path = ""
        self.catLocAdd = None
        if len(selected_files) > 0:
            self.catLocAdd = selected_files[0]
        else:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Pilih katalog untuk menyimpan data!")
            error_dialog.exec_()

        if self.catLocAdd != None:
            self.inputkatalog_add.insert(self.catLocAdd)
        else:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Lokasi katalog harus diisi!")
            error_dialog.exec_()
        return (self.catLocAdd)
    
    def getFile (self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Pilih file yang akan ditambahkan")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("ESRI Shape files (*.shp)")
        file_dialog.exec_()
        selected_files = file_dialog.selectedFiles()
        file_path = ""
        self.shpLocAdd = None
        if len(selected_files) > 0:
            self.shpLocAdd = selected_files[0]
        else:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Pilih data yang akan ditambahkan!")
            error_dialog.exec_()

        if self.shpLocAdd != None:
            self.fileinput_add.insert(self.shpLocAdd)
        else:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Data yang akan dipilih harus diisi!")
            error_dialog.exec_()
        return (self.shpLocAdd)
    
    def getDate(self):
        inputDate = self.add_date.text()
        return (inputDate)
    
    def getAtt(self):
        layerPath = self.getFile()
        file_name = os.path.basename(layerPath)
        layer_name = os.path.splitext(file_name)[0]
        layer = QgsVectorLayer(layerPath, layer_name, 'ogr')
        namaField = []
        jumlah_field = 0
        if layer.isValid():
            fields = layer.fields()
            for field in fields:
                namaField.append(field.name())
                jumlah_field +=1
        else:
            print('Failed to open the layer.')

        self.fieldTable.setColumnCount(2)
        self.fieldTable.setHorizontalHeaderLabels(['Nama Kolom', 'Tambahkan sebagai properti'])
        #atur ukuran kolom terakhir supaya tabel penuh
        self.fieldTable.horizontalHeader().setStretchLastSection(True)

        #buat baris sebanyak jumlah field
        self.fieldTable.setRowCount(jumlah_field)
        for index in range(jumlah_field):
            item1 = QtWidgets.QTableWidgetItem(namaField[index])
            self.fieldTable.setItem(index,0,item1)
            opsi = QtWidgets.QCheckBox()
            opsi.setStyleSheet("margin-left:50%")
            self.fieldTable.setCellWidget(index,1,opsi)

        #atur ukuran tabel
        self.fieldTable.setColumnWidth(0,275)
        self.fieldTable.setColumnWidth(1,185)
        return(jumlah_field)
    
    def getProp(self):
        propList = []
        rowCount = self.fieldTable.rowCount()
        for index in range(rowCount):
            checkBoxItem = self.fieldTable.cellWidget(index, 1)
            if isinstance(checkBoxItem, QtWidgets.QCheckBox) and checkBoxItem.isChecked():
                fieldItem = self.fieldTable.item(index, 0)
                if fieldItem is not None:
                    fieldName = fieldItem.text()
                    propList.append(fieldName)
                    print (fieldName)
        
        file_path = self.fileinput_add.text()
        
        cat_path = self.inputkatalog_add.text()
        catalog_path = pathlib.Path(cat_path)
        catalog = Catalog.from_file(cat_path, mode = 'rw')
            
        layer = QgsVectorLayer(file_path,'ogr')
        features = []
        idxFeature = 0
        field_names = [field.name() for field in layer.fields()]
        for feature in layer.getFeatures():
            idxFeature = idxFeature+1
            features.append(feature)
            geometry = feature.geometry()
            bounding_box = geometry.boundingBox()
            footprint_wkt = geometry.convexHull()
            footprint = footprint_wkt.asWkt()
            for prop in propList:
                tile = feature.attribute(prop)         
            item = pystac.Item(
                id=str(idxFeature),
                geometry=footprint,
                bbox=bounding_box,
                datetime=20230106,
                stac_extensions=['https://stac-extensions.github.io/projection/v1.0.0/schema.json'],
                properties=tile)
            catalog.add_item(item)
        print (catalog(describe))


        
        









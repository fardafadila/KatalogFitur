from asyncio.windows_events import NULL
import os
from stat import S_IREAD
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsWkbTypes, QgsFeature, QgsFields, QgsCoordinateReferenceSystem, QgsFeatureRequest
import json
import pystac
from datetime import datetime, timezone
import pathlib
import urllib.parse
from pystac import Catalog, Collection, Extent, Link
from qgis.PyQt.QtWidgets import QFileDialog
import shapely.wkt
import fnmatch
from pathlib import Path
from urllib.parse import quote
from qgis.core import QgsVectorFileWriter
from .dialog import my_dialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'katalog_fitur', 'katalog_fitur_dialog_base.ui'))
FORM_CLASS, _ = uic.loadUiType(ui_path)


class make_cat(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, strukturCombo, nama_katalog, deskripsi, folderpath_make, folder_make, catPath_make, catfile_make, produsen_make):
        """Constructor."""
        super(make_cat, self).__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.produsen_make = produsen_make
        self.strukturCombo= strukturCombo
        self.nama_katalog = nama_katalog
        self.deskripsi = deskripsi
        self.folderpath_make = folderpath_make
        self.folder_make = folder_make
        self.catPath_make = catPath_make
        self.catfile_make = catfile_make
        self.cache_folder_path = QgsProject.instance().homePath()
        self.parentLoc = None

 
    def outFolder(self):
        self.tipeKatalog=self.strukturCombo.currentText()
        project = QgsProject.instance()
        self.folderpath_make.clear()
        self.catLoc=  ""        
        if self.tipeKatalog == "Katalog" :
            self.catLoc, _ = QFileDialog.getSaveFileName(self, "Pilih lokasi penyimpanan katalog baru", self.cache_folder_path, "All files (*)")
            self.folderpath_make.insert(self.catLoc)
        elif self.tipeKatalog == "Subkatalog" or self.tipeKatalog == "Koleksi":
            self.catLoc, _ = QFileDialog.getSaveFileName(self, "Pilih lokasi penyimpanan katalog baru", self.cache_folder_path, "JSON (*.json)")
            self.folderpath_make.insert(self.catLoc)

        else:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Pilih lokasi penyimpanan yang sesuai!")
            error_dialog.exec_()
    
        return (self.catLoc)
    
    def getParent(self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Pilih file katalog yang sudah ada untuk menyimpan subkatalog")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.exec_()
        selected_files = file_dialog.selectedFiles()
        file_path = ""
        if len(selected_files) > 0:
            self.parentLoc = selected_files[0]
        else:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Pilih katalog yang sesuai untuk menyimpan subkatalog atau ubah struktur katalog!")
            error_dialog.exec_()
        self.catPath_make.insert(self.parentLoc)
        return (self.parentLoc)

    
    def saveCat(self):            
        produsen = self.produsen_make.text()
        catalog_id = self.nama_katalog.text()
        catalog_description = self.deskripsi.text()
        self.tipeKatalog = self.strukturCombo.currentText()
        if self.tipeKatalog == "Katalog":
            self.new_katalog = Catalog(id=catalog_id, description=catalog_description)
            self.new_katalog.normalize_and_save(os.path.abspath(self.catLoc))

        if self.tipeKatalog == "Subkatalog":
            print (self.parentLoc)
            with open(self.parentLoc, 'r') as file:
                contents = file.read()
                parentCat = os.path.normpath(self.parentLoc)
                self.parentCat = pystac.Catalog.from_file(parentCat)
            
            subcatalog = Catalog (id = catalog_id, description = catalog_description)
            filename = os.path.dirname(self.catLoc)
            subcatalog.set_self_href(os.path.abspath(self.catLoc))
            self.parentCat.add_child(subcatalog)
            self.parentCat.save()
            subcatalog.save()

        if self.tipeKatalog == "Koleksi":
            print (self.parentLoc)
            with open(self.parentLoc, 'r') as file:
                contents = file.read()
                parentCat = os.path.normpath(self.parentLoc)
                self.parentCat = pystac.Catalog.from_file(parentCat)
            
            koleksi = Collection (id = catalog_id, description = catalog_description, 
                                 extent=pystac.Extent(
                spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]),
                temporal=pystac.TemporalExtent([[datetime(2023, 1, 1), None]])))
            koleksi.extra_fields['Produsen Data'] = produsen
            filename = os.path.dirname(self.catLoc)
            koleksi.set_self_href(os.path.abspath(self.catLoc))
            self.parentCat.add_child(koleksi)
            self.parentCat.save()
            koleksi.save()
        print ("sukses")
        success_dialog = QtWidgets.QMessageBox.information(
            None,
            "Katalog Fitur",
            "Pembuatan katalog berhasil",
                )
    
    def buatCatalog(self):
        mainCatalog = Catalog(id="Main catalog", description="Katalog utama untuk menyimpan semua katalog")
        mainCatalog.set_self_href(os.path.abspath('D:/skripsi/KatalogFitur/mainCatalog.json'))


        osmCollection = Collection(id = "osmCat", description = "Collection untuk menyimpan katalog fitur OSM", 
                                 extent=pystac.Extent(
                spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]),
                temporal=pystac.TemporalExtent([[datetime(2023, 1, 1), None]])))
        osmCollection.set_self_href(os.path.abspath("D:/skripsi/KatalogFitur/osmCollection.json"))

        
        rdtrCollection = Collection(id = "rdtrCat", description = "Collection untuk menyimpan katalog fitur RDTR", 
                                 extent=pystac.Extent(
                spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]),
                temporal=pystac.TemporalExtent([[datetime(2023, 1, 1), None]])))
        rdtrCollection.set_self_href(os.path.abspath('D:/skripsi/KatalogFitur/rdtrCollection.json'))

        fileFeature = "D:/featureFolder/"
        outputPath = None
        
        
        shp_OSM = []
        root_path = 'D:\skripsi\Data\OSM'
        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                if fnmatch.fnmatch(file_name, '*.shp'):
                    file_path = os.path.join(root, file_name)
                    shp_OSM.append(file_path)
        for file in shp_OSM:
            filename = os.path.basename(file)
            layer = QgsVectorLayer(file,'ogr')
            features = []
            name = str(filename)
            filename = name.replace('.shp', '')
            idx = 0
            field_names = [field.name() for field in layer.fields()]
            idFeature = []
            geomFeature = []
            crs = QgsCoordinateReferenceSystem()
            crs.createFromId(QgsProject.instance().crs().postgisSrid())
            prop = []
            featId = 0
            for feature in layer.getFeatures():
                idx= idx+1
                idxFeature = str(idx)
                idFeature.append(idxFeature)                
                output_fields = feature.fields()
                outputPath = fileFeature+str(filename)+str(idx)+'.geojson'
                print (outputPath)
                geom_type = feature.geometry().type()
                new_layer = layer.materialize(QgsFeatureRequest().setFilterFid(featId))
                writer = QgsVectorFileWriter.writeAsVectorFormat(new_layer, outputPath, "utf-8", crs, "GeoJSON")
                featId = featId+1
                features.append(feature)
                geometry = feature.geometry()
                geomFeature.append(geometry)
                wkt = geometry.asWkt()
                geojson = shapely.wkt.loads(wkt).__geo_interface__
                bounding_box = geometry.boundingBox()
                bounding_box = geometry.boundingBox().toRectF().getCoords()
                osmAtt = ['water', 'natural', 'leisure', 'landuse', 'building', 'man_made', 'amenity', 'office', 'highhway', 'tourism', 'waterway', 'place']
                tileOSM = []
                for att in osmAtt:
                    if att in field_names:
                        dataOSM = feature.attribute(att) 
                        strData = str(dataOSM) 
                        if strData!= "NULL":
                            tileOSM.append(dataOSM)
                    
                datetime_tuple = (2023, 1, 1)
                datetime_str = '{}-{}-{}T00:00:00Z'.format(datetime_tuple[0], datetime_tuple[1], datetime_tuple[2])
                datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
                prop.append(tileOSM)
                item = pystac.Item(
                    id=filename+ "_" +str(idxFeature),
                    geometry=geojson,
                    bbox=bounding_box,
                    datetime=datetime_obj,
                    properties={"tile": tileOSM, "datetime": datetime_obj.isoformat()})
                
                print (item.id)
                item_properties_dict = item.properties
                print (item_properties_dict)
                item_datetime_str = item_properties_dict["datetime"]
                item_datetime_obj = datetime.strptime(item_datetime_str, '%Y-%m-%dT%H:%M:%S')
                item.datetime = item_datetime_obj
                item.add_asset(
                    key="vectorfile", asset=pystac.Asset(href=os.path.abspath(outputPath), media_type=pystac.MediaType.GEOJSON))
                osmCollection.add_item(item)
        
        shp_RDTR = []
        root_path = 'D:\skripsi\Data\RDTR'
        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                if fnmatch.fnmatch(file_name, '*.shp'):
                    file_path = os.path.join(root, file_name)
                    shp_RDTR.append(file_path)
        for file in shp_RDTR:
            filename = os.path.basename(file)
            layer = QgsVectorLayer(file,'ogr')
            features = []
            name = str(filename)
            filename = name.replace('.shp', '')
            idx = 0
            field_names = [field.name() for field in layer.fields()]
            idFeature = []
            geomFeature = []
            crs = QgsCoordinateReferenceSystem()
            crs.createFromId(QgsProject.instance().crs().postgisSrid())
            prop = []
            featId = 0
            for feature in layer.getFeatures():
                idx= idx+1
                idxFeature = str(idx)
                idFeature.append(idxFeature)                
                output_fields = feature.fields()
                outputPath = fileFeature+str(filename)+str(idx)+'.geojson'
                print (outputPath)
                geom_type = feature.geometry().type()
                new_layer = layer.materialize(QgsFeatureRequest().setFilterFid(featId))
                writer = QgsVectorFileWriter.writeAsVectorFormat(new_layer, outputPath, "utf-8", crs, "GeoJSON")
                featId = featId+1
                features.append(feature)
                geometry = feature.geometry()
                geomFeature.append(geometry)
                wkt = geometry.asWkt()
                geojson = shapely.wkt.loads(wkt).__geo_interface__
                bounding_box = geometry.boundingBox()
                bounding_box = geometry.boundingBox().toRectF().getCoords()
                attRDTR = 'NAMOBJ'
                tileRDTR = []
                if attRDTR in field_names:
                    dataRDTR = feature.attribute(attRDTR) 
                    tileRDTR.append(dataRDTR)
                    
                datetime_tuple = (2023, 1, 1)
                datetime_str = '{}-{}-{}T00:00:00Z'.format(datetime_tuple[0], datetime_tuple[1], datetime_tuple[2])
                datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
                prop.append(tileOSM)
                item = pystac.Item(
                    id=filename+ "_" +str(idxFeature),
                    geometry=geojson,
                    bbox=bounding_box,
                    datetime=datetime_obj,
                    properties={"tile": tileRDTR, "datetime": datetime_obj.isoformat()})
                
                print (item.id)
                item_properties_dict = item.properties
                print (item_properties_dict)
                item_datetime_str = item_properties_dict["datetime"]
                item_datetime_obj = datetime.strptime(item_datetime_str, '%Y-%m-%dT%H:%M:%S')
                item.datetime = item_datetime_obj
                item.add_asset(
                    key="vectorfile", asset=pystac.Asset(href=os.path.abspath(outputPath), media_type=pystac.MediaType.GEOJSON))
                rdtrCollection.add_item(item)     
        
        mainCatalog.add_child(osmCollection)
        mainCatalog.add_child(rdtrCollection)
        mainCatalog.describe()
        mainCatalog.save('D:/skripsi/KatalogFitur/mainCatalog.json')
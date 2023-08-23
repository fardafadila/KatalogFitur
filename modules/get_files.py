from msilib.schema import ODBCAttribute
import os
from pydoc import describe
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
import os
import fnmatch
from pathlib import Path
import pystac
from pystac import Catalog, Collection, Extent, CatalogType, Item
from qgis.core import QgsProject, QgsVectorLayer
from datetime import datetime, timezone
import pymongo
from pymongo import MongoClient
import json

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'katalog_fitur', 'katalog_fitur_dialog_base.ui'))
FORM_CLASS, _ = uic.loadUiType(ui_path)


class get_files(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, inputKeyword):
        """Constructor."""
        super(get_files, self).__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.shp_files = []
        self.inpuyKeyword = inputKeyword
    
    def fungsi(self):
        root_path = 'D:\skripsi\contoh data\Data'
        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                if fnmatch.fnmatch(file_name, '*.shp'):
                    file_path = os.path.join(root, file_name)
                    self.shp_files.append(file_path)
        for shp_file in self.shp_files:
            print(shp_file)
        return (self.shp_files)

    def coba(self):
        cobaKatalog = Catalog(id="cobaKatalog", description="Coba buat katalog dan isi")
        placeholder_extent = Extent(
                spatial=None,
                temporal=None
                )
        subKatalog = Collection (id = "cobaSubkatalog", description = "Coba buat sub katalog", extent=placeholder_extent)
        
        self.fungsi()
        
        for file in self.shp_files:
            layer = QgsVectorLayer(file,'ogr')
            features = []
            idxFeature = 0
            field_names = [field.name() for field in layer.fields()]
            for feature in layer.getFeatures():
                idxFeature = idxFeature+1
                features.append(feature)
                geometry = feature.geometry()
                bounding_box = geometry.boundingBox()
                print(bounding_box)
                footprint_wkt = geometry.convexHull()
                footprint = footprint_wkt.asWkt()
                if 'NAMOBJ' in field_names:
                    tile = feature.attribute('NAMOBJ') 
                else:
                    tile = feature.attribute('Ket') 

                item = pystac.Item(
                    id=str(idxFeature),
                    geometry=footprint,
                    bbox=bounding_box,
                    datetime=20230602,
                    properties=tile)
                
                subKatalog.add_item(item)
        
        subKatalog.describe()
        cobaKatalog.add_child(subKatalog)
        cobaKatalog.describe()
        print (cobaKatalog)
        #cobaKatalog.normalize_hrefs('D:/skripsi/coba_katalog/katalog_baru.json')
        #cobaKatalog.save(catalog_type=CatalogType.RELATIVE_PUBLISHED)

    def cobaMongo(self):

        """client = pymongo.MongoClient("mongodb+srv://fardafadila:normandy@cluster.ecoyz5a.mongodb.net/")
        db = client["katalog_fitur"]
        collection = db["feature_collection"]
        print ("nyambung")"""
        cobaKatalog = Catalog(id="cobaKatalog", description="Coba buat katalog dan isi")
        placeholder_extent = Extent(
                spatial=None,
                temporal=None
                )
        subKatalog = Collection (id = "cobaSubkatalog", description = "Coba buat sub katalog", 
                                 extent=pystac.Extent(
        spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]),
        temporal=pystac.TemporalExtent([[datetime(2023, 1, 1), None]])))
        self.fungsi()
        
        for file in self.shp_files:
            layer = QgsVectorLayer(file,'ogr')
            features = []
            idxFeature = 0
            field_names = [field.name() for field in layer.fields()]
            idFeature = []
            geomFeature = []
            prop = []
            for feature in layer.getFeatures():
                idxFeature = idxFeature+1
                idFeature.append(idxFeature)
                features.append(feature)
                geometry = feature.geometry()
                geomFeature.append(geometry)
                #print (geometry)
                bounding_box = geometry.boundingBox()
                
                footprint_wkt = geometry.convexHull()
                #print ("footprintnya:     " )
                #print( footprint_wkt)
                footprint = footprint_wkt.asWkt()
                if 'NAMOBJ' in field_names:
                    tile = feature.attribute('NAMOBJ') 
                else:
                    tile = feature.attribute('Ket') 
                prop.append(tile)
                item = pystac.Item(
                    id=str(idxFeature),
                    geometry=geometry,
                    bbox=bounding_box,
                    datetime=datetime(2023, 1, 1, tzinfo=timezone.utc),
                    properties=tile)
                subKatalog.add_item(item)
                #print (item.properties)
        cobaKatalog.add_child(subKatalog)
        dict_geom = zip(idFeature, geomFeature)
        dict_prop = zip (idFeature, prop)
        items = list(subKatalog.get_items())
        if len(items) > 0:
            print ("cek")
            item = items[-1]
            """item_dict = item.to_dict()
            if 'datetime' in item_dict['properties']:
                item_dict['properties']['datetime'] = item.datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            print(json.dumps(item_dict, indent=4))
        else:
            print("Koleksi kosong")"""



    def getKeyword (self):
        keyword = self.inpuyKeyword.text()
        return (keyword)
    
    def mongoBing(self):
        """"AMBIL KEYWORD YANG DIMASUKKAN"""
        keyword = self.getKeyword()

        """BUAT KONEKSI"""
        client = pymongo.MongoClient("mongodb+srv://fardafadila:normandy@cluster.ecoyz5a.mongodb.net/" )
        db = client.test
        #collectionDB = client["katalog_fitur"]["feature_collection"]        
        """END BUAT KONEKSI"""

        """BUAT KATALOG DAN COLLECTION"""
        catalog = Catalog(id="example catalog", description="An example STAC catalog")

        collection = Collection (id = "cobaSubkatalog", description = "Coba buat sub katalog", 
                                 extent=pystac.Extent(
        spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]),
        temporal=pystac.TemporalExtent([[datetime(2023, 1, 1), None]])))
        """END BUAT KATALOG"""



        """PANGGIL FILE SHP DAN TAMBAH KE COLLECTION"""
        layer = QgsVectorLayer('D:\skripsi\contoh data\Data\RDTR_PontiTimurBarat.shx','ogr')
        features = []
        idxFeature = 0
        field_names = [field.name() for field in layer.fields()]
        idFeature = []
        geomFeature = []
        prop = []
        for feature in layer.getFeatures():
            idxFeature = idxFeature+1
            idFeature.append(idxFeature)
            features.append(feature)
            geometry = feature.geometry()
            geomFeature.append(geometry)
            bounding_box = geometry.boundingBox()
            if 'NAMOBJ' in field_names:
                tile = feature.attribute('NAMOBJ') 
            else:
                tile = feature.attribute('Ket') 
            prop.append(tile)
            item = pystac.Item(
                id=str(idxFeature),
                geometry=geometry,
                bbox=bounding_box,
                datetime=datetime(2023, 1, 1, tzinfo=timezone.utc),
                properties=tile)
            collection.add_item(item)
        collection.add_item(item)
        catalog.add_child(collection)
        db.insert_one(catalog.to_dict())

        # Insert each collection in the catalog into MongoDB
        """for collection in catalog.get_children():
            db[collection.id].insert_one(collection.to_dict())

            # Insert each item in the collection into MongoDB
            for item in collection.get_items():
                db[collection.id].insert_one(item.to_dict())"""






























        """END TAMBAH FITUR KE COLLECTION"""

        """collection_json = json.dumps(collection.to_dict(include_self_link=False))

        collectionDB.insert_one(json.loads(collection_json))"""

        """BUAT JSON DARI COLLECTION"""
        """items_json = []
        for item in collection.get_all_items():
            geometry_json = json.loads(item.geometry.asJson())
            item_json = {
                'id': item.id,
                'prop': item.properties,
                'geom': geometry_json
            }
            items_json.append(item_json)"""
       

        



        """catalog.normalize_and_save(collectionDB)"""
        #collectionJS = {'items': items_json}
        #json_string = json.dumps(collectionJS, indent=4)
        #print(json_string)
        """"END BUAT JSON"""

        """for item in collection.get_all_items():
            id = item.id
            if id == keyword:
                print (item.id)
                print (item.geometry)
                print (item.properties)
            properties = item.properties
            geometri = item.geometry
            print (properties)
            print (geometri)"""
        




        #print (collection_json)
        #catalog_json = json.dumps(catalog.to_dict(include_self_link=False))
        #catalog_json = json.dumps(catalog.to_dict())
        #catalog.describe()
        #print (keyword)

        #for item in collection.get_all_items():
            #id = item.id
            #if id == printed:
                #print (item.id)
                #print (item.geometry)
                #print (item.properties)
            #properties = item.properties
            #geometri = item.geometry
            #print (properties)
            #print (geometri) 

        #collectionDB.insert_one(json.loads(catalog_json))
        #catalog_json = json.dumps(catalog.to_dict(include_self_link=False))
        #collectionDB.insert_one(json.loads(collection_json))
    
    
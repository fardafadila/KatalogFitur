import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject, QgsVectorLayer
from osgeo import ogr
import fnmatch
import pystac
import urllib.parse
from pystac import Catalog, Collection, Extent
import geopandas as gpd
from .get_files import get_files



# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'katalog_fitur', 'katalog_fitur_dialog_base.ui'))
FORM_CLASS, _ = uic.loadUiType(ui_path)


class get_features(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, input_keyword):
        """Constructor."""
        super(get_features, self).__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.input_keyword = input_keyword
        #self.files_instance = get_files()
        #self.catalogFeature = pystac.Catalog(
            #id='Catalog Feature',
            #description='Coba katalog feature',
            #stac_extensions=['https://stac-extensions.github.io/projection/v1.0.0/schema.json'])
    
    """def files (self):
        catalog = Catalog(id="my_catalog", description="My Catalog")
        subcatalog = Collection(
            id="my_subcatalog",
            description="My Subcatalog",
            extent=Extent(spatial={}, temporal=None)
        )

        catalog.add_child(subcatalog)
        catalog.normalize_and_save("D:/skripsi/coba_katalog/catalog.json")"""

    
    def files(self):
        catalogFiles = pystac.Catalog(
            id='Catalog Files',
            description='Coba katalog files')
        print ("cek")
        root_path = 'D:\skripsi\contoh data\Coba RDTR'
        self.shp_file = []
        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                if fnmatch.fnmatch(file_name, '*.shp'):
                    file_path = os.path.join(root, file_name)
                    self.shp_files.append(file_path)
        for shp_file in self.shp_files:
            print(shp_file)
        for file in self.shp_files:
            print (file)
            data = gpd.read_file(file)
            bounding_box = data.total_bounds
            print('Bounding Box:', bounding_box)
            footprint = data.unary_union.convex_hull
            print('Footprint:', footprint)
            file_name = os.path.basename(file)
            idx = file_name
            tile = "perencanaan"
            item = pystac.Item(
                id=idx,
                geometry=footprint,
                bbox=bounding_box,
                datetime=20230106,
                stac_extensions=['https://stac-extensions.github.io/projection/v1.0.0/schema.json'],
                properties=dict(
                tile=tile))
            catalogFiles.add_item(item)
        print(len(list(catalogFiles.get_items())))
        catalogFiles.describe()
    
    def featuresFunction(self):
        
        self.files_instance.fungsi()
        self.shp_files = self.files_instance.shp_files
        
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
                    datetime=20230106,
                    stac_extensions=['https://stac-extensions.github.io/projection/v1.0.0/schema.json'],
                    properties=tile)
                self.catalogFeature.add_item(item)
            

        keyword = self.input_keyword.text()
        matched_item = []
        for item in self.catalogFeature.get_all_items():
            properties = item.properties
            if keyword.lower() in properties.lower():
                item_id = item.id
                matched_item.append(item_id)
        print (matched_item)    

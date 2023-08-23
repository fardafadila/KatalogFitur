import os
from pickle import ADDITEMS
from pydoc import describe
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5 import QtWidgets, QtCore
from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsWkbTypes, QgsFeature, QgsFields, QgsCoordinateReferenceSystem, QgsFeatureRequest
import pystac
import json
import shapely.wkt
import pathlib
import urllib.parse
from pystac import Catalog, Collection, Extent
from qgis.PyQt.QtWidgets import QFileDialog
from datetime import datetime, timezone
from qgis.core import QgsVectorFileWriter
from .dialog import my_dialog
from shapely.errors import WKTReadingError

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'katalog_fitur', 'katalog_fitur_dialog_base.ui'))
FORM_CLASS, _ = uic.loadUiType(ui_path)


class add_data(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, inputkatalogAdd, folderAdd, fileinputAdd, fileAdd, dateAdd, fieldAdd, geojsonAdd, fiturpathAdd ):
        """Constructor."""
        super(add_data, self).__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.inputkatalog_add= inputkatalogAdd
        self.folder_add= folderAdd
        self.fileinput_add = fileinputAdd
        self.file_add = fileAdd
        self.add_date = dateAdd
        self.fieldTable = fieldAdd
        self.geojsonAdd = geojsonAdd
        self.fiturpathAdd = fiturpathAdd
        self.cache_folder_path = QgsProject.instance().homePath()
        self.jsonLoc = ''

        self.dictSemantic = None
        self.lindung_gambut  = ['Lindung gambut', 
                           'wetland',
                           'Gambut']
        self.sempadan_sungai = ['Sempadan sungai', 
                           'groyne']
        self.rth = ['Ruang terbuka hijau', 'Rimba Kota', 'RTH', 'Taman kota', 'Taman RW', 'Taman RT', 'Taman kelurahan', 'Taman kecamatan' 
               'village_green', 'park', 'grass', 'grassland', 'forest']
        self.lindung_spiritual = ['Keraton', 'Museum', 
                             'castle']
        self.gudang = ['Pergudangan', 'warehouse']
        self.perumahan = ['Rumah Kepadatan Tinggi',
                     'Rumah Kepadatan Sedang',
                     'Rumah Kepadatan Rendah',
                     'Perumahan',
                     'Perumahan vertikal tinggi',
                     'Perumahan vertikal sedang',
                     'Perumahan tapak', 'Rumah',
                     'residential', 'apartment', 'house']
        self.perdagangan_jasa = ['Perdagangan dan Jasa',
                            'Perdagangan dan Jasa Skala Kota',
                            'Perdagangan dan jasa Pelayanan Lingkungan',
                            'Perdagangan dan jasa Skala Sub BWP',
                            'commercial',
                            'shop',
                            'kiosk',
                            'retail',
                            'supermarket',
                            'food court',
                            'restaurant',
                            'marketplace']
        self.perkantoran = ['Perkantoran', 'office']
        self.pelayanan_umum = ['SPU skala kota', "Sarana Pelayanan Umum",
                          'SPU skala Kecamatan',
                          'SPU skala Kelurahan',
                          'SPU skala RW',
                          'Pelayanan Umum', 'SPU Pendididikan',
                           'SPU Ekonomi', 
                           'SPU Kesehatan', 
                           'SPU Olahraga', 
                           'SPU Sosial Budaaya', 
                           'SPU Peribadatan'
                          ]
        self.kawasan_industri = ['Kawasan peruntukan industri',
                            'Sentra industri kecil dan menengah',
                            'industrial']
        self.pertanian = ['hortikultura', 
                     'farm land', 
                     'allotment', 
                     'farmyard']
        self.rtnh = ['Ruang Terbuka Non Hijau',
                'Lapangan non resapan',
                'Alun-alun',
                'fountain']
        self.pariwisata = ['Pariwisata buatan',
                      'Pariwisata budaya', 'Wisata Budaya',
                      'recreational_ground',
                      'national_park']
        self.pertahanan_keamanan = ['Pertahanan dan keamanan',
                               'Police',
                               'Barrack',
                               'Bunker',
                               'Military']
        self.badan_air = ['Badan Air', 'Sungai',
                    'waterway',
                    'water',
                    'drain', 'river', 'reservoir', 'pond',
                    'ditch',
                    'canal']
        self.persampahan = ['Tempat pemrosesan sementara', 
                       'Tempat pemrosesan akhir',
                       'landfill',
                       'waste_disposal',
                       'waste_transfer_station']
        self.jalan = ['Jalan',
                        'Sistem jaringan jalan dan jembatan',
                        'Jaringan jalan',
                        'Badan jalan',
                        'Arteri Sekunder', 'Arteri Primer',
                        'Kolektor Sekunder', 'Kolektor Primer',
                        'Lokal Sekunder', 'Lokal Primer',
                        'Jalan Lain', 'Jalan Lokal',
                        'Lingkungan Sekunder',
                        'Jalur pejalan kaki',
                        'Jalur sepeda',
                        'highway',
                        'living_street',
                        'footway',
                        'path',
                        'primary',
                        'tertiary_link', 'track', 'trunk', 'trunk_link', 'steps']
        self.transportasi = ['Jaringan transportasi darat', 'Transportasi',
                        'Terminal penumpang',
                        'Jaringan jalur kereta api',
                        'Stasiun kereta api',
                        'Jaringan penyeberangan',
                        'Pelabuhan laut',
                        'Alur pelayaran',
                        'Lintas penyeberangan',
                        'Pelabuhan utama',
                        'Jalur utama',
                        'Jalur penghubung',
                        'Pelabuhan pengumpul lokal',
                        'Terminal khusus',
                        'Pelabuhan',
                        'transportation',
                        'public_transport',
                        'bridge',
                        'bus_station',
                        'stop_area',
                        'train_station']
        self.spu_kesehatan = ['Rumah sakit', 'Puskesmas', 'Klinik',
                              'hospital', 'doctor', 'dentist', 'clinic']
        self.spu_sosbud = ['events_venue', 'social_center', 'fire_station', 'post_office',
                           'social_facilitty', 'prison']
        self.spu_peribadatan = ['Ibadah', 'Masjid', 'Gereja', 'Kuil', 'Wihara',
                                'place-of_worship', 'cathedral', 'church', 'mosque', 'religious']
        self.spu_pendidikan = ['Sekolah', 'SD', 'SMP', 'SMA', 'Universitas', 'Pendidikan',
                               'school', 'university', 'eibrary', 'education']
        self.spu_ekonomi =['Ekonomi', 'atm', 'bank']
        self.pemakaman = ['Pemakaman', 'Makam', 'cemetery', 'Kuburan']
        self.hutan = ['Hutan', 'Belukar', 'wood', 'scrub']
        self.semantic = {'AA': self.lindung_gambut, 'AB':self. sempadan_sungai, 'AC': self.rth, 'AD': self.lindung_spiritual, 'AE': self.perumahan,
                    'AF': self.perdagangan_jasa, 'AG': self.perkantoran, 'AH': self.pelayanan_umum, 'AI': self.kawasan_industri, 'AJ': self.pertanian, 
                    'AK': self.rtnh, 'AL': self.pariwisata, 'AM': self.pertahanan_keamanan, 'AN': self.gudang, 
                    'AO': self.persampahan, 'AP': self.spu_pendidikan, 'AQ': self.spu_peribadatan, 'AR': self.spu_kesehatan, 
                    'AS': self.transportasi, 'AT': self.badan_air, 'AU': self.jalan, 'AW': self.pemakaman, 'AX': self.spu_sosbud,
                    'AV': self.spu_ekonomi}
        
        self.desc ={'AA': "Peruntukan ruang yang merupakan bagian dari kawasan lindung yang mempunyai fungsi utama perlindungan dan keseimbangan tata air, penyimpan cadangan karbon, dan pelestarian keanekaragaman hayati", 
                    'AB':"peruntukan ruang yang merupakan bagian dari kawasan lindung yang mempunyai fungsi pokok sebagai perlindungan, penggunaan, dan pengendalian atas sumber daya yang ada pada sungai dapat dilaksanakan sesuai dengan tujuannya", 
                    'AC': "Area memanjang/jalur dan atau mengelompok, yang penggunaannya lebih bersifat terbuka, tempat tumbuh tanaman, baik yang tumbuh tanaman secara alamiah maupun yang sengaja ditanam", 
                    'AD': "-", 
                    'AE': "Kawasan yang merupakan bagian dari lingkungan hunian dan terdiri atas lebih dari satu satuan perumahan yang mempunyai prasarana, sarana, utilitas umum, serta mempunyai penunjang kegiatan fungsi lain di kawasan perkotaan atau perdesaan",
                    'AF': "Bagian wilayah tempat kegiatan yang terkait dengan transaksi barang dan/atau jasaberupa pasar rakyat, pertokoan, pusat perbelanjaan, toko modern, gudang, pusat distribusi, pusat perbankaan, jasa informasi, jasa keuangan, jasa perusahaan, penyediaan akomodasi, penyediaan makan minum, dan lainnya, untuk mendukung kelancaran arus distribusi barang", 
                    'AG': "Bagian wilayah dengan karakteristik sebagai tempat bekerja", 
                    'AH': "Suatu bagian wilayah dengan karakteristik kegiatan pendidikan, kesehatan, olahraga, sosial budaya, peribadatan, dan transportasi yang berfungsi untuk mendukung penyelenggaraan dan pengembangan kehidupan sosial, budaya, dan ekonomi", 
                    'AI': "Bangunan gedung dengan fungsi utama sebagai tempat manusia melakukan kegiatan usaha dalam industri kecil, sedang, dan berat", 
                    'AJ': "Wilayah pertanian", 
                    'AK': "Runang terbuka non hijau", 
                    'AL': "Bagian wilayah yang di dalamnya terdapat daya tarik wisata, fasilitas umum, fasilitas pariwisata, aksesibilitas, serta masyarakat yang saling terkait dan melengkapi terwujudnya kepariwisataan", 
                    'AM': "Wilayah pertahanan", 
                    'AN': "Bagian wilayah dengan karakteristik sebagai suatu ruangan tidak bergerak yang tertutup dan/atau terbuka dengan tujuan tidak untuk dikunjungi oleh umum, tetapi untuk dipakai khusus sebagai tempat penyimpanan barang yang dapat diperdagangkan dan tidak untuk kebutuhan sendiri", 
                    'AO': "Jaringan persampahan",
                    'AP': "Bagian pelayanan umum yang memfasilitasi kegiatan pendidikan",
                    'AQ': "Bagian pelayanan umum yang memfasilitasi kegiatan peribadatan", 
                    'AR': 'Bagian pelayanan umum yang memfasilitasi kegiatan kesehatan', 
                    'AS': 'Prasarana transportasi darat yang meliputi segala bagian jalan, termasuk bangunan pelengkap dan perlengkapannya yang diperuntukkan bagi lalu lintas, kecuali jalan kereta api, jalan lori, dan jalan kabel ', 
                    'AT': 'Badan air', 
                    'AU': 'Jalan adalah prasarana transportasi darat yang meliputi segala bagian jalan, termasuk bangunan pelengkap dan perlengkapannya yang diperuntukkan bagi lalu lintas, yang berada pada permukaan tanah, di atas permukaan tanah, di bawah permukaan tanah dan/atau air, serta di atas permukaan air, kecuali jalan kereta api, jalan lori, dan jalan kabel',
                    'AV': 'Bagian pelayanan umum yang memfasilitasi kegiatan ekonomi',
                    'AW': 'Bangunan yang difungsikan untuk pemakaman baik untuk umum maupun khusus', 
                    'AX': 'Bagian pelayanan umum yang memfasilitasi kegiatan sosial budaya'
                    }

    def getCat(self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Pilih katalog yang akan digunakan")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.exec_()
        self.inputkatalog_add.clear()
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
        self.fileinput_add.clear()
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
    
    
    def getPath (self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Pilih folder")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.exec_()
        selected_files = file_dialog.selectedFiles()
        file_path = ""
        if len(selected_files) > 0:
            self.jsonLoc = selected_files[0]
        self.fiturpathAdd.insert(self.jsonLoc)
    
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
            print('Data tidak valid')

        self.fieldTable.setColumnCount(2)
        self.fieldTable.setHorizontalHeaderLabels(['Nama Kolom', 'Tambahkan sebagai properti'])
        self.fieldTable.horizontalHeader().setStretchLastSection(True)

        self.fieldTable.setRowCount(jumlah_field)
        for index in range(jumlah_field):
            item1 = QtWidgets.QTableWidgetItem(namaField[index])
            self.fieldTable.setItem(index,0,item1)
            opsi = QtWidgets.QCheckBox()
            opsi.setStyleSheet("margin-left:50%")
            self.fieldTable.setCellWidget(index,1,opsi)

        self.fieldTable.setColumnWidth(0,275)
        self.fieldTable.setColumnWidth(1,185)
        return(jumlah_field)
    
    def addingData(self):
        dialogKategori = my_dialog()
        prog_dialog = dialogKategori.progdialog()
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
        with open(os.path.abspath(catalog_path)) as f:
            data = json.load(f)
            tipe = (data['type'])
            print(tipe)
        catalog_path = os.path.abspath(catalog_path)
        if str(tipe) == "Catalog":
            catalog = pystac.Catalog.from_file(catalog_path)
            print ("dia katalog")
        elif str(tipe) == "Collection":
            catalog = pystac.Collection.from_file(catalog_path)
            print ("dia koleksi")


        
        inputDate = self.add_date.text()
        tahun = str(inputDate)[:4]
        intTahun = int(tahun)
        bulan = str(inputDate)[4:6]
        intBulan = int(bulan)
        tanggal = str(inputDate)[6:]
        intTanggal = int(tanggal)

        print (self.jsonLoc)
        fileFeature = str(self.jsonLoc+"/")
        outputPath = None
        shp_Add = []
        shp_Add.append(file_path)

        for file in shp_Add:
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
                geom_type = feature.geometry().type()
                new_layer = layer.materialize(QgsFeatureRequest().setFilterFid(featId))
                writer = QgsVectorFileWriter.writeAsVectorFormat(new_layer, outputPath, "utf-8", crs, "GeoJSON")
                featId = featId+1
                features.append(feature)
                geometry = feature.geometry()
                geomFeature.append(geometry)
                wkt = geometry.asWkt()
                try:
                    geojson = shapely.wkt.loads(wkt).__geo_interface__
                except WKTReadingError as e:
                    print(f"Kesalahan dalam membaca geometri WKT: {e}")
                    continue
                geojson = shapely.wkt.loads(wkt).__geo_interface__
                bounding_box = geometry.boundingBox()
                bounding_box = geometry.boundingBox().toRectF().getCoords()
                tileData = []
                for att in propList:
                    if att in field_names:
                        dataOSM = feature.attribute(att) 
                        strData = str(dataOSM) 
                        if strData!= "NULL":
                            tileData.append(dataOSM)
                
                listKey = []
                for properti in tileData:
                    for key, value in self.semantic.items():
                        if properti.lower() in [x.lower() for x in value]:
                            listKey.append(key)
                propertiItem = "-------"
                for a in listKey:
                    for key, value in self.desc.items():
                        if key == a:
                            propertiItem = str(value)
                print (propertiItem)

                datetime_tuple = (int(tahun), int(bulan) , int(tanggal))
                datetime_str = '{}-{}-{}T00:00:00Z'.format(datetime_tuple[0], datetime_tuple[1], datetime_tuple[2])
                datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
                prop.append(tileData)
                item = pystac.Item(
                    id=filename+ "_" +str(idxFeature),
                    geometry=geojson,
                    bbox=bounding_box,
                    datetime=datetime_obj,
                    properties={"keyword": tileData, "datetime": datetime_obj.isoformat(), "deskripsi": propertiItem})
                
                print (item.id)
                item_properties_dict = item.properties
                print (item_properties_dict)
                item_datetime_str = item_properties_dict["datetime"]
                item_datetime_obj = datetime.strptime(item_datetime_str, '%Y-%m-%dT%H:%M:%S')
                item.datetime = item_datetime_obj
                item.add_asset(
                    key="vectorfile", asset=pystac.Asset(href=os.path.abspath(outputPath), media_type=pystac.MediaType.GEOJSON))
                catalog.add_item(item)          
        catalog.save()
        success_dialog = QtWidgets.QMessageBox.information(
            None,
            "Katalog Fitur",
            "Penambahan data berhasil!",
                )






import os
from pydoc import describe
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5 import QtWidgets, QtCore
from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsProcessingFeatureSourceDefinition, QgsCoordinateReferenceSystem
import processing
import json
import pystac
import pathlib
import urllib.parse
from pystac import Catalog, Collection, Extent
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.utils import iface
from .dialog import my_dialog
from urllib.parse import urlparse

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'katalog_fitur', 'katalog_fitur_dialog_base.ui'))
FORM_CLASS, _ = uic.loadUiType(ui_path)


class search_data(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, inputSearch, folderSearch, inputKeyword, runSearch, atributSearch, tableSearch):
        """Constructor."""
        super(search_data, self).__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.tableSearch = tableSearch
        self.atributSearch = atributSearch
        self.inputSearch = inputSearch
        self.folderSearch = folderSearch
        self.inputKeyword = inputKeyword
        self.runSearch = runSearch
        
        self.dictSemantic = None
        self.lindung_gambut  = ['Lindung gambut', 
                           'Wetland',
                           'Gambut']
        self.sempadan_sungai = ['Sempadan sungai', 
                           'Groyne']
        self.rth = ['Ruang terbuka hijau', 'RTH', 'Taman kota', 'Taman RW', 'Taman RT', 'Taman kelurahan', 'Taman kecamatan' 
               'Village green', 'Park', 'Grass', 'Forest']
        self.lindung_spiritual = ['Keraton', 'Museum', 
                             'Castle']
        self.gudang = ['Pergudangan', 'Warehouse']
        self.perumahan = ['Rumah kepadatan tinggi'
                     'Rumah kepadatan sedang',
                     'Rumah kepadatan rendah',
                     'Perumahan',
                     'Perumahan vertikal tinggi',
                     'Perumahan vertikal sedang',
                     'Perumahan tapak', 'Rumah'
                     'Residential', 'Apartment', 'House']
        self.perdagangan_jasa = ['Perdagangan dan jasa',
                            'Perdagangan dan jasa skala pelayanan kota',
                            'Perdagangan dan jasa pelayanan pelayanan lingkungan',
                            'Perdagangan dan jasa skala sub BWP',
                            'Commercial',
                            'Shop',
                            'Kiosk',
                            'Retail',
                            'Supermarket',
                            'Food court',
                            'Restaurant',
                            'Marketplace']
        self.perkantoran = ['Perkantoran', 'Office']
        self.pelayanan_umum = ['SPU skala kota', "Sarana Pelayanan Umum",
                          'SPU skala kecamatan',
                          'SPU skala kelurahan',
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
                            'Industrial']
        self.pertanian = ['hortikultura', 
                     'farm land', 
                     'allotment', 
                     'farmyard']
        self.rtnh = ['Ruang terbuka non hijau',
                'Lapangan non resapan',
                'Alun-alun',
                'Fountain']
        self.pariwisata = ['Pariwisata buatan',
                      'Pariwisata budaya',
                      'Recreational ground',
                      'National park']
        self.pertahanan_keamanan = ['Pertahanan dan keamanan',
                               'Police',
                               'Barrack',
                               'Bunker',
                               'Military']
        self.badan_air = ['Badan air', 'Perairan', 'Sungai'
                    'Waterway',
                    'Water',
                    'Drain',
                    'Ditch', 'reservoir', 'pond',
                    'Canal']
        self.persampahan = ['Tempat pemrosesan sementara', 
                       'Tempat pemrosesan akhir',
                       'Landfill',
                       'Waste disposal',
                       'Waste transfer station']
        self.jalan = ['Jalan',
                        'Sistem jaringan jalan dan jembatan',
                        'Jaringan jalan',
                        'Badan jalan',
                        'Jalan arteri sekunder',
                        'Jalan kolektor sekunder',
                        'Jalan lokal sekunder',
                        'Jalan lingkungan sekunder',
                        'Jalur pejalan kaki',
                        'Jalur sepeda',
                        'High way',
                        'Living_street',
                        'Footway',
                        'Path',
                        'Primary',
                        'Tertiary_link', 'Track', 'Trunk', 'Trunk_link', 'Steps']
        self.transportasi = ['Jaringan transportasi darat',
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
                        'Transportation',
                        'Public transport',
                        'Bridge',
                        'Bus station',
                        'Stop area',
                        'Train station',
                        'Public transport station']
        self.spu_kesehatan = ['Kesehatan', 'Rumah sakit', 'Puskesmas', 'Klinik',
                              'Hospital', 'Doctor', 'Dentist', 'Clinic']
        self.spu_sosbud = ['Sosial budaya', 'Events venue', 'Social center', 'Fire station', 'Post office',
                           'Post office', 'Social facilitty', 'Prison']
        self.spu_peribadatan = ['Ibadah', 'Masjid', 'Gereja', 'Kuil', 'Wihara',
                                'Place of worship', 'Cathedral', 'Church', 'Mosque', 'Religious']
        self.spu_pendidikan = ['Sekolah', 'SD', 'SMP', 'SMA', 'Universitas', 'Pendidikan',
                               'School', 'University', 'Library']
        self.spu_ekonomi =['Ekonomi', 'ATM', 'Bank']
        self.pemakaman = ['Pemakaman', 'Makam', 'Cemetery', 'Kuburan']
        self.semantic = {'AA': self.lindung_gambut, 'AB':self. sempadan_sungai, 'AC': self.rth, 'AD': self.lindung_spiritual, 'AE': self.perumahan,
                    'AF': self.perdagangan_jasa, 'AG': self.perkantoran, 'AH': self.pelayanan_umum, 'AI': self.kawasan_industri, 'AJ': self.pertanian, 
                    'AK': self.rtnh, 'AL': self.pariwisata, 'AM': self.pertahanan_keamanan, 'AN': self.gudang, 
                    'AO': self.persampahan, 'AP': self.spu_pendidikan, 'AQ': self.spu_peribadatan, 'AR': self.spu_kesehatan, 
                    'AS': self.transportasi, 'AT': self.badan_air, 'AU': self.jalan, 'AW': self.pemakaman, 'AX': self.spu_sosbud,
                    'AV': self.spu_ekonomi}
        
    

    def getCat(self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Pilih file katalog yang sudah ada untuk menyimpan subkatalog")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.exec_()
        self.inputSearch.clear()
        selected_files = file_dialog.selectedFiles()
        file_path = ""
        self.catLoc = ""
        if len(selected_files) > 0:
            self.catLoc = selected_files[0]
        else:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Pilih katalog yang sesuai untuk menyimpan subkatalog atau ubah struktur katalog!")
            error_dialog.exec_()
        self.inputSearch.insert(self.catLoc)

    def getData (self):
        self.strukturSTAC = self.inputSearch.text()
        return (self.strukturSTAC)

    def matchedSemantic(self):
        dialogKategori = my_dialog()
        self.getData()
        prog_dialog= dialogKategori.progdialog()
        keyword = self.inputKeyword.text()
        listKey = []
        for key, value in self.semantic.items():
            if keyword.lower() in [x.lower() for x in value]:
                listKey.append(key)
            elif any(keyword.lower() in x.lower() for x in value):
                listKey.append(key)
        atributSesuai = []
        for key in listKey:
            atributSesuai += self.semantic[key]
        with open(os.path.abspath(self.strukturSTAC)) as f:
            data = json.load(f)
            tipe = (data['type'])
            print(tipe)
        catalog_path = os.path.abspath(self.strukturSTAC)
        if str(tipe) == "Catalog":
            self.katalog = pystac.Catalog.from_file(catalog_path)
            print ("dia katalog")
        elif str(tipe) == "Collection":
            self.katalog = pystac.Collection.from_file(catalog_path)
            print ("dia koleksi") 
        propItem = []
        idItem = []
        for collect in self.katalog.get_all_items():
            prop = collect.properties
            id = collect.id
            self.atribut= prop['keyword']
            propItem.append(self.atribut)
            idItem.append(id)
        dict_fitur = dict(zip(idItem, propItem))
        pilihanAtribut = []
        keyAtribut = []
        for key, value in dict_fitur.items():
            for a in value:
                if a.lower() in [x.lower() for x in atributSesuai]:
                    pilihanAtribut.append(a)
                    keyAtribut.append(key)
                elif any(a.lower() in x.lower() for x in atributSesuai):
                    pilihanAtribut.append(a)
                    keyAtribut.append(key)
        self.dictSemantic = dict(zip(keyAtribut, pilihanAtribut))
        displayAtribut = [*set(pilihanAtribut)]
        jumlah_atribut = len(displayAtribut)
        self.tableSearch.setColumnCount(3)
        self.tableSearch.setHorizontalHeaderLabels(['Atribut yang ditemukan', 'Koleksi', 'Tambahkan layer'])
        self.tableSearch.horizontalHeader().setStretchLastSection(True)
        self.tableSearch.setRowCount(jumlah_atribut)
        for index in range(jumlah_atribut):
            item1 = QtWidgets.QTableWidgetItem(displayAtribut[index])
            self.tableSearch.setItem(index,0,item1)
            opsi = QtWidgets.QCheckBox()
            opsi.setStyleSheet("margin-left:50%")
            self.tableSearch.setCellWidget(index,2,opsi)
        self.tableSearch.setColumnWidth(0,245)
        self.tableSearch.setColumnWidth(1,190)
        if jumlah_atribut < 1:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setText("Atribut tidak ditemukan! Coba kata kunci lain!")
            error_dialog.exec_()

        return (jumlah_atribut, self.dictSemantic)

    
    def getProp(self):
        wtaList = []
        rowCount = self.tableSearch.rowCount()
        for index in range(rowCount):
            checkBoxItem = self.tableSearch.cellWidget(index, 2)
            if isinstance(checkBoxItem, QtWidgets.QCheckBox) and checkBoxItem.isChecked():
                fieldItem = self.tableSearch.item(index, 0)
                if fieldItem is not None:
                    fieldName = fieldItem.text()
                    wtaList.append(fieldName)
        return (wtaList)
    
    def addData(self):
        dialogKategori = my_dialog()
        prog_dialog = dialogKategori.progdialog()
        dialogKategori = my_dialog()
        wtaList = self.getProp()
        
        itemAdd = []
        for key, value in self.dictSemantic.items():
            for a in wtaList:
                if value == a:
                    itemAdd.append(key)
        
        project = iface.activeLayer()
        collections = {}
        for item in self.katalog.get_all_items():
            collection_id = item.collection_id
            id = item.id
            asset = item.assets["vectorfile"]
            href = asset.href
            if id in itemAdd:
                if collection_id not in collections:
                    collections[collection_id] = []
                collections[collection_id].append(item)
            
        for key, value in collections.items():
            output_layer = "key"
            fitur = []
            nama_layer = str(key)
            for item in value:
                id = item.id
                asset = item.assets["vectorfile"]
                href = asset.href
                featureObject = QgsVectorLayer(href, id, 'ogr')
                fitur.append(featureObject)
            result = processing.run("native:mergevectorlayers", {'LAYERS': fitur, 'OUTPUT': 'memory:'+nama_layer})
            merged_layer = result['OUTPUT']
            QgsProject.instance().addMapLayer(merged_layer)
        if len (wtaList) <1:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setText("Centang atribut yang akan ditambahkan!")
            error_dialog.exec_()
        else:
            success_dialog = QtWidgets.QMessageBox.information(
                None,
                "Katalog Fitur",
                "Hasil pencarian berhasil ditambahkan!",
                )
            

        """for item in self.katalog.get_all_items():
            id = item.id
            asset = item.assets["vectorfile"]
            href = asset.href            
            if id in itemAdd:
                layer = QgsVectorLayer(href, id, "ogr")
                QgsProject.instance().addMapLayer(layer)"""


        """ listsemuaLayer = []
        for a in itemAdd:
            namaLayer = a.split('_')[0]
            listsemuaLayer.append(namaLayer)
        
        listLayer = [*set(listsemuaLayer)]
        for b in listLayer:
            print (b)
        
        layerHasil = {}
        for item in listLayer:
            layerHasil[item] = []
        
        for item in self.katalog.get_all_items():
            id = item.id
            if id in itemAdd:
                for key in layerHasil.keys():
                    if key in id:
                        layerHasil[key].append(item)
    
        project = iface.activeLayer()
        for key, value in layerHasil.items():
            fiturLayer = []
            for item in value:
                id = item.id
                asset = item.assets["vectorfile"]
                href = asset.href
                layer = QgsVectorLayer(href, id, "ogr")
                fiturLayer.append(layer)
        print (fiturLayer)
        output_layer = "merged_layer"

        processing.run("qgis:mergevectorlayers", {'LAYERS': fiturLayer, 'CRS': QgsCoordinateReferenceSystem('EPSG:4326'), 'OUTPUT': output_layer})
        merged_layer = QgsVectorLayer(output_layer, "merged_layer", "ogr")

        QgsProject.instance().addMapLayer(merged_layer)"""




        


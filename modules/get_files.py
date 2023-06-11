import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
import os
import fnmatch
from pathlib import Path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'katalog_fitur', 'katalog_fitur_dialog_base.ui'))
FORM_CLASS, _ = uic.loadUiType(ui_path)


class get_files(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(get_files, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.shp_files = []
    
    def fungsi(self):
        root_path = 'D:/skripsi/contoh data'
        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                if fnmatch.fnmatch(file_name, '*.shp'):
                    file_path = os.path.join(root, file_name)
                    self.shp_files.append(file_path)
        for shp_file in self.shp_files:
            print(shp_file)



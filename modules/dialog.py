import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets, QtCore
from qgis.utils import iface
from qgis.utils import iface

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'kugi', 'kugi_dialog_base.ui'))

# Load the UI file
FORM_CLASS, _ = uic.loadUiType(ui_path)

class my_dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=iface.mainWindow()): 
        super(my_dialog, self).__init__(parent)
        self.setupUi(self)

    def progdialog(self):
        dialog = QtWidgets.QProgressDialog()
        dialog.setWindowTitle("Katalog Fitur")
        dialog.setMinimumWidth(300)        
        dialog.show()
        return dialog
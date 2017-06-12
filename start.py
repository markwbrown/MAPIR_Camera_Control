import sys
from PyQt4 import QtCore, QtGui
from MAPIR_Processing_dockwidget import MAPIR_ProcessingDockWidget, KernelModal



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MAPIR_ProcessingDockWidget()
    myapp.show()
    sys.exit(app.exec_())
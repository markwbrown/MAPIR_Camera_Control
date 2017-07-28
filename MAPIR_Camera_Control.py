import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from MAPIR_Processing_dockwidget import MAPIR_ProcessingDockWidget, KernelModal



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MAPIR_ProcessingDockWidget()
    myapp.show()
    sys.exit(app.exec_())

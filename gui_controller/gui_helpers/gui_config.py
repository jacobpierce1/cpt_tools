# global config as well as imports for the gui 


SUBTITLE_FONT = 'arial'
SUBTITLE_SIZE = 16
SUBTITLE_WEIGHT = 3

# DEFAULT_KDE_BW = 0.03

PLOTTER_WIDGET_QLINEEDIT_WIDTH = 70



from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QPixmap
# from PyQt5 import QtGui
from PyQt5 import QtCore


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

MAX_SIZE_POLICY = size_policy = QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Maximum )

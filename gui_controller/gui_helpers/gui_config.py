# global config as well as imports for the gui 


SUBTITLE_FONT = 'arial'
SUBTITLE_SIZE = 16
SUBTITLE_WEIGHT = 3

# DEFAULT_KDE_BW = 0.03

PLOTTER_WIDGET_QLINEEDIT_WIDTH = 70


DEFAULT_TACC = 0
DEFAULT_NUM_STEPS = 5

# order: w_-, w_+, w_c 
DEFAULT_TABOR_SETTINGS = [ [ 1600.0, 656252.0, 0.5 ],  # omega
                           [ -140.0, 0.0, 0.0 ],  # phase
                           [ 0.0005, 0.2, 0.5 ],  # amp 
                           [ 1, 100, 208 ],  # loops 
                           [ 3, 1, 1 ]   # length 
]


from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QPixmap
# from PyQt5 import QtGui
from PyQt5 import QtCore


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

MAX_SIZE_POLICY = size_policy = QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Maximum )

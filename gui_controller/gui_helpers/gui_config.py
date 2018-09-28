# global config as well as imports for the gui 


SUBTITLE_FONT = 'arial'
SUBTITLE_SIZE = 16
SUBTITLE_WEIGHT = 3

# DEFAULT_KDE_BW = 0.03

PLOTTER_WIDGET_QLINEEDIT_WIDTH = 70



DEFAULT_TACC = 0
DEFAULT_NUM_STEPS = 5

# order: w_-, w_+, w_c 
DEFAULT_TABOR_SETTINGS = [ [ 1571.0, 673429.0, 675000.0 ],  # omega
                           [ -160.0, 0.0, 0.0 ],  # phase
                           [ 0.0035, 0.22, 0.5 ],  # amp 
                           [ 1, 103, 228 ],  # loops 
                           [ 3, 1, 1 ]   # length 
]


DEFAULT_TOF_CUT_LOWER = 0
DEFAULT_TOF_CUT_UPPER = 40

DEFAULT_RADIUS_CUT_LOWER = 0
DEFAULT_RADIUS_CUT_UPPER = 10

DEFAULT_SUM_X_CUT_LOWER = 0
DEFAULT_SUM_X_CUT_UPPER = 100

DEFAULT_SUM_Y_CUT_LOWER = 0
DEFAULT_SUM_Y_CUT_UPPER = 100

DEFAULT_DIFF_XY_CUT_LOWER = -100
DEFAULT_DIFF_XY_CUT_UPPER = 100


from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QPixmap, QImage
# from PyQt5 import QtGui
from PyQt5 import QtCore


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

MAX_SIZE_POLICY = size_policy = QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Maximum )


# don't modify below this line

MU_UNICODE = '\u03bc'

from PyQt4 import QtCore
from PyQt4 import QtGui as qt

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

import itertools

class MultiTabNavTool(NavigationToolbar):
    #====================================================================================================
    def __init__(self, canvases, tabs, parent=None):
        self.canvases = canvases
        self.tabs = tabs

        NavigationToolbar.__init__(self, canvases[0], parent)

    #====================================================================================================
    def get_canvas(self):
        return self.canvases[self.tabs.currentIndex()]

    def set_canvas(self, canvas):
        self._canvas = canvas

    canvas = property(get_canvas, set_canvas)

class MplMultiTab(qt.QMainWindow):
    #====================================================================================================
    def __init__(self, parent=None, figures=None, labels=None):
        qt.QMainWindow.__init__(self, parent)

        self.main_frame = qt.QWidget()
        self.tabWidget = qt.QTabWidget( self.main_frame )
        self.create_tabs( figures, labels )

        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = MultiTabNavTool(self.canvases, self.tabWidget, self.main_frame)

        self.vbox = vbox = qt.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.tabWidget)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    #====================================================================================================
    def create_tabs(self, figures, labels ):

        if labels is None:      labels = []
        figures =  [Figure()] if figures is None else figures     #initialise with empty figure in first tab if no figures provided
        self.canvases = [self.add_tab(fig, lbl) 
                            for (fig, lbl) in itertools.zip_longest(figures, labels) ]

    #====================================================================================================
    def add_tab(self, fig=None, name=None):
        '''dynamically add tabs with embedded matplotlib canvas with this function.'''

        # Create the mpl Figure and FigCanvas objects. 
        if fig is None:
            fig = Figure()
            ax = fig.add_subplot(111)

        canvas = fig.canvas if fig.canvas else FigureCanvas(fig)
        canvas.setParent(self.tabWidget)
        canvas.setFocusPolicy( QtCore.Qt.ClickFocus )

        #self.tabs.append( tab )
        name = 'Tab %i'%(self.tabWidget.count()+1) if name is None else name
        self.tabWidget.addTab(canvas, name)

        return canvas


import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(1, 2*np.pi, 100)
figures = []
for i in range(1,3):
    fig, ax = plt.subplots()
    y = np.sin(np.pi*i*x)+0.1*np.random.randn(100)
    ax.plot(x,y)
    figures.append( fig )

app = qt.QApplication(sys.argv)
ui = MplMultiTab( figures=figures )
ui.show()
app.exec_()

from PyQt4 import QtGui, QtCore
import sys, os

class Dialog_01(QtGui.QMainWindow):
    def __init__(self):
        super(QtGui.QMainWindow,self).__init__()

        myTabWidget = QtGui.QTabWidget()        

        self.QGroupBoxA = QtGui.QGroupBox()        
        myTabWidget.addTab(self.QGroupBoxA,' Tab A ')        

        self.QGroupBoxB = QtGui.QGroupBox()        
        myTabWidget.addTab(self.QGroupBoxB,' Tab B ')

        self.QHBoxLayout = QtGui.QHBoxLayout()
        self.listWidget = QtGui.QListWidget()

        self.QHBoxLayout.addWidget(self.listWidget)

        myTabWidget.connect(myTabWidget, QtCore.SIGNAL("currentChanged(int)"), self.tabSelected) 

        self.setCentralWidget(myTabWidget)

    def tabSelected(self, arg=None):
        self.listWidget.clear()
        if arg==0: 
            self.QGroupBoxA.setLayout(self.QHBoxLayout)
            for i in range(12): 
                QtGui.QListWidgetItem( 'A Item '+str(i), self.listWidget )

        if arg==1: 
            self.QGroupBoxB.setLayout(self.QHBoxLayout)      
            for i in range(12): 
                QtGui.QListWidgetItem( 'B Item '+str(i), self.listWidget )


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dialog_1 = Dialog_01()
    dialog_1.show()
    dialog_1.resize(480,320)
    sys.exit(app.exec_())

import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QListWidgetItem

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from qt_for_python.uic.tst import *
#import .qt_for_python.uic.tst
import numpy as np

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MyMainWindow(QtWidgets.QMainWindow):
#class MyMainWindowUI(Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MyMainWindow, self).__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #ui.pushButton_1

        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.sc, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        self.ui.test_widget.setLayout(layout)

        self.ui.pushButton_1.clicked.connect(self.testCallback01)
        self.ui.pushButton_3.clicked.connect(self.testCallback02)
        self.ui.pushButton_2.clicked.connect(self.testCallback03)

        # Create a placeholder widget to hold our toolbar and canvas.
        #widget = QtWidgets.QWidget()
        #widget.setLayout(layout)
        #self.setCentralWidget(widget)

        self.show()


    def fillList(self):
        #self.ui.listWidget.addItem("I1...")
        #self.ui.listWidget.addItem(QListWidgetItem(tr("Oak")))
        QtWidgets.QListWidgetItem("Oak", self.ui.listWidget)
        QListWidgetItem("Fir", self.ui.listWidget)
        QListWidgetItem("Pine", self.ui.listWidget)
        self.ui.listWidget.show()

    def fillComboBox(self):
        self.ui.comboBox.addItem("It 1")
        self.ui.comboBox.addItem("It 2")
        self.ui.comboBox.addItem("It 3")
        self.ui.comboBox.addItem("It 4")

    @QtCore.Slot()
    def testCallback01(self):
        self.ui.pushButton_1.setText("Fa")
        self.ui.label.setText("aqsdfghjklö")
        self.sc.axes.cla()
        self.sc.axes.plot([0,1,2,3,4], np.random.rand(5))
        self.sc.draw()

    @QtCore.Slot()
    def testCallback02(self):
        self.ui.pushButton_3.setText("-_-")
        self.fillList()
        self.fillComboBox()

    @QtCore.Slot()
    def testCallback03(self):
        v = self.ui.doubleSpinBox.value()
        self.ui.pushButton_2.setText( str(v) )

app = QtWidgets.QApplication(sys.argv)
MainWindow = MyMainWindow()#QtWidgets.QMainWindow()
#ui = MyMainWindowUI()
#ui.setupUi(MainWindow)
MainWindow.show()
#w = MainWindow()
app.exec_()
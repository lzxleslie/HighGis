from PyQt4.QtGui import QAction, QMainWindow
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
class RectangleMapTool(QgsMapTool):
  def __init__(self, canvas):
      self.canvas = canvas

  def canvasPressEvent(self, e):
      QMessageBox.about(self.canvas,"error","fuck")    

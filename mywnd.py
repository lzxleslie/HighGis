from qgis.gui import *
from PyQt4.QtGui import QAction, QMainWindow
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4 import QtGui, uic
from qgis.core import *

class MyWnd(QtGui.QWidget):
  def __init__(self, layer,canvas,message):
    QtGui.QWidget.__init__(self)

    self.canvas = canvas
    self.message = message
    self.canvas.setCanvasColor(Qt.white)
    QgsMapLayerRegistry.instance().addMapLayer(layer,False)
    self.canvas.setExtent(layer.extent())
    self.canvas.setLayerSet([QgsMapCanvasLayer(layer)])
    #self.setCentralWidget(self.canvas)

    actionZoomIn = QAction("Zoom in", self)
    actionZoomOut = QAction("Zoom out", self)
    actionPan = QAction("Pan", self)
    
    actionZoomIn.setCheckable(True)
    actionZoomOut.setCheckable(True)
    actionPan.setCheckable(True)

    self.connect(actionZoomIn, SIGNAL("triggered()"), self.zoomIn)
    self.connect(actionZoomOut, SIGNAL("triggered()"), self.zoomOut)
    self.connect(actionPan, SIGNAL("triggered()"), self.pan)
    self.connect(self.canvas, SIGNAL("extentsChanged()"), self.extentchaged)

    # create the map tools
    self.toolPan = QgsMapToolPan(self.canvas)
    self.toolPan.setAction(actionPan)
    self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false = in
    self.toolZoomIn.setAction(actionZoomIn)
    self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
    self.toolZoomOut.setAction(actionZoomOut)
    self.pan()
  def zoomIn(self):
    self.canvas.setMapTool(self.toolZoomIn)
  def zoomOut(self):
    self.canvas.setMapTool(self.toolZoomOut)

  def pan(self):
    self.canvas.setMapTool(self.toolPan) 
  def extentchaged(self):
    extent = self.canvas.extent()
    center = self.canvas.center()
    xcenter = round(center.x(),2)
    ycenter = round(center.y(),2)
    xmin = round(extent.xMinimum(),2)
    ymin = round(extent.yMinimum(),2)
    xmax = round(extent.xMaximum(),2)
    ymax = round(extent.yMaximum(),2)
    msg1 = str(xmin)+","+str(ymin)+":"+str(xmax)+","+str(ymax)
    msg2 = str(xcenter)+","+str(ycenter)
    self.display_message(msg1,msg2)   
    
  def display_message(self, msg1,msg2):
    self.message.lineextent.setText(msg1)
    self.message.linecenter.setText(msg2)

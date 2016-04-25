# -*- coding: utf-8 -*-
"""
/***************************************************************************
 hgis
                                 A QGIS plugin
 hgis
                              -------------------
        begin                : 2016-04-15
        git sha              : $Format:%H$
        copyright            : (C) 2016 by lzx
        email                : lzx_whu@163.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from hgis_dialog import hgisDialog
import os.path
import helper
import json
import qgis.core
import uuid
class hgis:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        
        self.layer_to_export_list_item = {}
        
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self.tmp_folder_path = os.path.join(self.plugin_path, 'tmp/')        
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'hgis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = hgisDialog()
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&hgis')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'hgis')
        self.toolbar.setObjectName(u'hgis')
        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('hgis', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/hgis/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'higis'),
            callback=self.run,
            parent=self.iface.mainWindow())
        


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&hgis'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        self.dlg.tabWidget.tabid = 0;
        # Run the dialog event loop 
        self.dlg.pushButton.clicked.connect(self.clear_tmp_folder)
        self.dlg.refreshLayers.clicked.connect(self.refreshbtn_clicked)
        self.dlg.connect(self.dlg.tabWidget, SIGNAL("currentChanged(int)"),self.currenttab)
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            if self.dlg.tabWidget.tabid==0:
                self.btndownload_clicked()
            if self.dlg.tabWidget.tabid==1:
                self.json_file_generation()
            pass
    
    def currenttab(self,tabid):
        self.dlg.tabWidget.tabid=tabid;
    def btndownload_clicked(self):
        url = self.dlg.Data_Source.text()
        filename_unique = str(uuid.uuid1())
        helper.saveHttpData(url, self.tmp_folder_path+filename_unique+".json")
        layer = helper.JsonVectorLayer(self.tmp_folder_path+filename_unique+".json","lzx")
        if not layer:
            QMessageBox.about(self.dlg,"Error","Layer is invalid") 
        helper.Json2Shp(layer, self.tmp_folder_path+filename_unique+".shp")
        layer1= helper.addVectorLayer(self.dlg,self.tmp_folder_path+filename_unique+".shp", self.iface)
        if not layer1:
            QMessageBox.about(self.dlg,"Error","Layer is invalid") 
        self.dlg.close()
    def refreshbtn_clicked(self):
        self.dlg.vLayersListWidget.clear()
        vector_layers = helper.get_vector_layers(self.iface)
        for layer in vector_layers:
            self.add_layer_in_selection_list(layer)        
    def add_layer_in_selection_list(self, layer):
        layer_id = layer.id()
        layer_name = layer.name()
    
        item = QListWidgetItem()
        item.setText(layer_name)
        self.dlg.vLayersListWidget.addItem(item)
        self.layer_to_export_list_item[layer_id] = item
    def is_layer_selected_for_export(self, layer):
        """Return true if the given layer has been selected by the user in the
        selection list.
        
        Keyword arguments:
        layer -- the layer
        """
        layer_id = layer.id()
        if layer_id in self.layer_to_export_list_item:
            return self.layer_to_export_list_item[layer_id].isSelected()
        else:
            QMessageBox.about(self.dlg,"Error",'No layer with id ' + layer_id)
            return False  
    def select_layer(self, layer):
        """Set a layer as selected in the selection list (UI) for export.
    
        Keyword arguments:
        layer -- the layer
        """
        layer_id = layer.id()
        if layer_id in self.layer_to_export_list_item:
            self.layer_to_export_list_item[layer.id()].setSelected(True)
    def get_selected_layers_for_export(self):
        """Return the list of all the layers selected for the export"""
        ret = []
        for layer in helper.get_vector_layers(self.iface):
            if self.is_layer_selected_for_export(layer):
                ret.append(layer)
        return ret
    def json_file_generation(self):
        """Create the files that the user want to export and place the files in
        the tmp forlder path"""
        selected_layers = self.get_selected_layers_for_export()
        for layer in selected_layers:
            layer_name = layer.name()
            self.create_json_alias_file(
                layer,
                os.path.join(
                    self.tmp_folder_path, layer_name + '_alias.json'))
            qgis.core.QgsVectorFileWriter.writeAsVectorFormat(
                layer,
                os.path.join(self.tmp_folder_path, layer_name),
                'utf-8', None, 'GeoJSON')
        QMessageBox.about(self.dlg,"UPLOAD","Upload done!") 
    def create_json_alias_file(self, layer, filename):
        """Creates the file containing the map field name and field alias for
        a given layer.
    
        Keyword arguments:
        layer -- the layer
        filename -- the file name of the created file
        """
        layer_attibutes = {}
        fields = layer.dataProvider().fields()
        for i, f in enumerate(fields):
            layer_attibutes[f.name()] = layer.attributeAlias(i)
        f = file(filename, 'w')
        json.dump(layer_attibutes, f)
        f.close()
    def clear_tmp_folder(self):
        """Removes all the file of the folder that store temporary the json
        files"""
        try:
            for f in os.listdir(self.tmp_folder_path):
                f_path = os.path.join(self.tmp_folder_path, f)
                os.unlink(f_path)
            #self.display_message('Temporary dir has been cleared')
            return True
        except Exception as e:
            #self.display_error_message('Temporary dir has been not cleared')
            return False
          

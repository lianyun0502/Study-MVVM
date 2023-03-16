from PySide6 import QtWidgets

class PluginWidget(QtWidgets.QWidget):...

class PluginCtrl:...

class Plugin():
    def __init__(self, name, plugin_wg:PluginWidget, plugin_ctrl:PluginCtrl):
        self.name = name
        self.plugin_wg = plugin_wg
        self.plugin_ctrl = plugin_ctrl




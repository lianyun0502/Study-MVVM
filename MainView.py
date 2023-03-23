from View import BaseView, PlugInView, isFragment, PlugInViewInfo
from typing import Optional
from PySide6 import QtCore,QtGui,QtWidgets
from MainViewModel import AppViewModel, CounterModel, ViewModelEventMediator

class AppView(PlugInView):
    view_model:Optional[AppViewModel]=None
    def __init__(self, name:str, view_model:AppViewModel):
        super().__init__(name=name, view_model=view_model)

    def _connectSentinel(self):
        super()._connectSentinel()
        self.view_model.sentinel.sig_setPlugin.connect(self.getPluginNotify)
        self.view_model.sentinel.sig_message.connect(self.getMessage)
        self.view_model.sentinel.sig_selectPlugin.connect(self.getSelectPlugin)
        for name, plug_in_view in self.plugin_views.items():
            plug_in_view.view.run()

    def _disconnectSentinel(self):
        super()._disconnectSentinel()
        self.view_model.sentinel.sig_setPlugin.disconnect(self.getPluginNotify)
        self.view_model.sentinel.sig_message.disconnect(self.getMessage)

    def setupUI(self, wg:QtWidgets.QWidget) ->None:
        self.ques = QtWidgets.QMessageBox(wg)
        # self.ques.setStyleSheet(u"font: 14pt \"Yu Gothic UI \";")
        self.pb_connect = QtWidgets.QPushButton('Connect', wg)
        self.pb_set_setting = QtWidgets.QPushButton('Set Setting', wg)
        self.el_ID = QtWidgets.QLineEdit('', wg)
        self.ccb_plugin = QtWidgets.QComboBox()
        hly = QtWidgets.QHBoxLayout(wg)
        wg.setLayout(hly)
        self.stack = QtWidgets.QStackedWidget(wg)
        wg2 = QtWidgets.QWidget(wg)
        hly.addWidget(wg2)
        hly.addWidget(self.stack)
        ly = QtWidgets.QVBoxLayout()
        wg2.setLayout(ly)
        ly.addWidget(self.pb_connect)
        ly.addWidget(self.el_ID)
        ly.addWidget(self.pb_set_setting)
        ly.addWidget(self.ccb_plugin)

        self.pb_connect.clicked.connect(self.PB_clickConnect)
        self.pb_set_setting.clicked.connect(self.PB_clickSetSetting)
        self.ccb_plugin.currentTextChanged.connect(self.view_model.selectPluginPage)

    def PB_clickConnect(self):
        if self.view_model.is_connect:
            self.view_model.disconnectDevice()
        else:
            self.view_model.connectDevice()

    def PB_clickSetSetting(self):
        self.view_model.setSetting(self.ccb_plugin.currentText(), self.el_ID.text())

    @isFragment()
    def getModelState(self, view_model:AppViewModel) ->None:
        if view_model.is_connect:
            self.pb_connect.setText('Disconnect')
        else:
            self.pb_connect.setText('Connect')
            self.el_ID.clear()

        self.ccb_plugin.setEnabled(view_model.is_connect)
        self.el_ID.setEnabled(view_model.is_connect)
        self.pb_set_setting.setEnabled(view_model.is_connect)

    @isFragment()
    def getPluginNotify(self, view_model:AppViewModel)->None:
        self.ccb_plugin.clear()
        self.ccb_plugin.addItems(tuple(view_model.plugins.keys()))

    def getSelectPlugin(self, plugin:str)->None:
        self.stack.setCurrentWidget(self.plugin_views[plugin].view.wg)

    def _addPluginToLayout(self, view:BaseView):
        wg = QtWidgets.QWidget()
        self.stack.addWidget(wg)
        view.setupUI(wg=wg)

    def getMessage(self, msg:str):
        ret = QtWidgets.QMessageBox.warning(self.ques, 'Notice',
                                      msg, QtWidgets.QMessageBox.StandardButton.Ok)
        return


class Counter(BaseView):
    view_model:Optional[CounterModel]=None
    def __init__(self, name, view_model:CounterModel):
        super().__init__(name=name, view_model=view_model)

    def setupUI(self, wg:QtWidgets.QWidget) ->None:
        self.wg = wg
        self.lb_number = QtWidgets.QLabel('Current Number :',wg)
        self.pb_plus = QtWidgets.QPushButton('+1', wg)
        self.pb_minus = QtWidgets.QPushButton('-1', wg)

        vly = QtWidgets.QVBoxLayout(wg)
        wg.setLayout(vly)
        vly.addWidget(self.lb_number)
        vly.addWidget(self.pb_plus)
        vly.addWidget(self.pb_minus)

        self.pb_plus.clicked.connect(self.view_model.plusOne)
        self.pb_minus.clicked.connect(self.view_model.minusOne)

    @isFragment()
    def getModelState(self, view_model:CounterModel) ->None:
        self.lb_number.setText(f'Current Number : {view_model.current_number}')
        self.wg.setEnabled(view_model.is_enable)
        return

    def _addPluginToLayout(self, view_info: PlugInViewInfo) ->None:...









if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.resize(600,100)
    widget = QtWidgets.QWidget()

    mediator = ViewModelEventMediator()

    app_model = AppViewModel('Main', mediator)
    counter_model = CounterModel('Counter', mediator)
    counter_model2 = CounterModel('Counter2', mediator)

    AppView = AppView('Main', app_model)
    counterView = Counter('Counter', counter_model)
    counterView2 = Counter('Counter2', counter_model2)

    AppView.setupUI(widget)
    AppView.addPluginView(counterView)
    AppView.addPluginView(counterView2)

    AppView.run()

    app_model.render()

    window.setCentralWidget(widget)
    window.show()


    sys.exit(app.exec())
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import sys
import attrs
import inspect
import logging
from typing import Optional, Dict
from PySide6 import QtCore,QtGui,QtWidgets
from ViewModel.ViewModel import ViewModel, ModelSentinel, Repository, ViewModelMediator, isHandler, log
import View.View as SETTING_PROCESS


class AppModelSentinel(ModelSentinel):
    sig_setPlugin = QtCore.Signal(object)
    sig_selectPlugin = QtCore.Signal(object)

class UIState(Repository):
    def __init__(self):
        self._is_connect = False
        self._is_set = False

class AppViewModel(ViewModel):
    @property
    def is_connect(self):
        return self._state._is_connect

    @is_connect.setter
    def is_connect(self, is_connect: bool):
        self._state._is_connect = is_connect
        self.mediator.trigger('changed_Connect', is_connect)
        self.sentinel.sig_state.emit(self)

    @property
    def is_set(self):
        return self._state._is_set

    @is_set.setter
    def is_set(self, is_set: bool):
        self._state._is_set = is_set
        self.sentinel.sig_state.emit(self)

    def __init__(self, name:str, mediator:ViewModelMediator):
        super().__init__(name=name)
        self.sentinel = AppModelSentinel()
        self._state = UIState()
        self.mediator = mediator
        self.mediator.register('changed_Connect', self.ConnectState)
        # self.plugins:Dict[str,int] = {'..':0 ,'eric':1, 'wayne':2, 'harry':3}

    def render(self):
        self.mediator.trigger('changed_Connect', self.is_connect)
        self.sentinel.sig_state.emit(self)
        for name, plugin in self.plugins.items():
            plugin.render()

    def connectDevice(self)->None:
        log.info('Connect device')
        self.is_connect = True
        self.setPlugins()

    def disconnectDevice(self)->None:
        log.info('Disconnect device')
        self.is_connect = False

    def selectSetting(self)->None:
        log.info('Select Setting')

    def setSetting(self, name:str, setting:str)->None:
        if setting == '':
            self.sentinel.sig_message.emit(f'Your setting is empty!')
            return

        log.info(f'{name} set {setting}')
        self.is_set = True

    def setPlugins(self):
        log.info(f'Set Plugin')
        self.sentinel.sig_setPlugin.emit(self)

    def selectPluginPage(self, page_name:str)->None:
        if page_name == '':
            return
        log.info(f'Select Plugin Page : {page_name}')
        self.sentinel.sig_selectPlugin.emit(page_name)

    def modifySettingConfigs(self, class_name:str, attr:str, val)->None:
        log.info('Modify Setting Configs')
        components_dict = dict(inspect.getmembers(SETTING_PROCESS))
        assert components_dict.get(class_name) is not None, f"There's no class {class_name} in Setting Process"
        assert hasattr(components_dict.get(class_name), attr), f"There's no attribute {attr} in class {class_name}"
        setattr(components_dict.get(class_name), attr, val)

    @isHandler()
    def ConnectState(self, is_connect:bool):
        if is_connect != self.is_connect:
            self.is_connect = is_connect

class CounterModel(ViewModel):
    @property
    def current_number(self)->int:
        return self._current_number
    @current_number.setter
    def current_number(self, number):
        if number == 10:
            number = 0
        elif number == -1:
            number = 9
        self._current_number = number
        self.sentinel.sig_state.emit(self)

    @property
    def is_enable(self)->bool:
        return self._enable

    @is_enable.setter
    def is_enable(self, is_enable):
        self._enable = is_enable
        self.sentinel.sig_state.emit(self)

    def __init__(self, name:str, mediator:ViewModelMediator):
        super().__init__(name=name)
        self.sentinel = AppModelSentinel()
        self.mediator = mediator
        self.mediator.register('changed_Connect', self.setViewEnable)
        self._current_number=0
        self._enable = True

    def render(self):
        self.sentinel.sig_state.emit(self)

    def plusOne(self):
        log.info('plusOne')
        self.current_number = self.current_number + 1
        return

    def minusOne(self):
        log.info('minusOne')
        self.current_number = self.current_number - 1
        return

    def setViewEnable(self, is_connect:bool):
        if self.is_enable != is_connect:
            self.is_enable = is_connect






if __name__ == '__main__':
    app = AppViewModel()
    app.connectDevice()
    app.modifySettingConfigs('View', 'a', 123)








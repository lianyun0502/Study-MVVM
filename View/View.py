from __future__ import annotations
import sys
from functools import wraps
import abc
from abc import ABC
from typing import Protocol, Tuple
from PySide6 import QtCore, QtGui, QtWidgets
from ViewModel.ViewModel import ViewModel


class IActivity(ABC):
    @abc.abstractmethod
    def run(self):...

    @abc.abstractmethod
    def stop(self):...

class View(IActivity):
    '''
    View 類別
    只負責UI的規格、布局以及樣式。
    '''
    def __init__(self, name:str, view_model:ViewModel):
        super().__init__()
        self.name = name
        self.view_model:ViewModel = view_model
        self.plugin_views:dict[str, View] = {}

    @abc.abstractmethod
    def setupUI(self, wg:QtWidgets.QWidget)->None:...

    @abc.abstractmethod
    def getModelState(self, view_model:ViewModel)->None:...

    def addPluginView(self, view: View)->None:
        self.plugin_views.update({view.name:view})
        self.view_model.addPlugin(name=view.view_model.name, plugin=view.view_model)
        self._addPluginToLayout(view)

    @abc.abstractmethod
    def _addPluginToLayout(self, view: View)->None:...

    def run(self):
        self._connectSentinel()
        for name, plug_in in self.plugin_views.items():
            plug_in.run()

    def _connectSentinel(self):
        self.view_model.sentinel.sig_state.connect(self.getModelState)

    def stop(self):
        self._disconnectSentinel()

    def _disconnectSentinel(self):
        self.view_model.sentinel.sig_state.disconnect(self.getModelState)

def isTask(name=None):
    def decorator(func):
        @wraps(func)
        def wrap(self, task):
            if task.name != name:
                return
            if task.func != func.__name__:
                return
            func(self, *task.args)
            return func
        return wrap
    return decorator









if __name__ == '__main__':
   pass



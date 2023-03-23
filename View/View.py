from __future__ import annotations

from functools import wraps
import abc
from dataclasses import dataclass
from View.Logger import log
from PySide6 import QtCore, QtGui, QtWidgets
from ViewModel.ViewModel import ViewModel


@dataclass
class PlugInViewInfo:
    name: str
    view:BaseView


class IView():
    @abc.abstractmethod
    def run(self):
        ...
    @abc.abstractmethod
    def stop(self):
        ...
    @abc.abstractmethod
    def setupUI(self, wg:QtWidgets.QWidget)->None:
        ...


class BaseView(IView):
    '''
    View 類別
    只負責UI的規格、布局以及樣式。
    '''
    def __init__(self, name:str, view_model:ViewModel):
        super().__init__()
        self.name = name
        self.view_model:ViewModel = view_model

    @abc.abstractmethod
    def getModelState(self, view_model:ViewModel)->None:...

    def run(self):
        self._connectSentinel()

    def _connectSentinel(self):
        self.view_model.sentinel.sig_state.connect(self.getModelState)

    def stop(self):
        self._disconnectSentinel()

    def _disconnectSentinel(self):
        self.view_model.sentinel.sig_state.disconnect(self.getModelState)

class PlugInView(BaseView):
    '''
    View 類別
    只負責UI的規格、布局以及樣式。
    '''
    def __init__(self, name:str, view_model:ViewModel):
        super().__init__(name=name, view_model=view_model)
        self.plugin_views:dict[str, PlugInViewInfo] = {}

    def run(self):
        self._connectSentinel()
        for name, plug_in_view in self.plugin_views.items():
            plug_in_view.view.run()

    def stop(self):
        self._disconnectSentinel()
        for name, plug_in_view in self.plugin_views.items():
            plug_in_view.view.stop()

    def addPluginView(self, view: BaseView)->None:
        self.plugin_views.update({view.name:PlugInViewInfo(name=view.name, view=view)})
        self.view_model.addPlugin(name=view.view_model.name, plugin=view.view_model)
        self._addPluginToLayout(view)

    @abc.abstractmethod
    def _addPluginToLayout(self, view: BaseView)->None:...


def isFragment(name=None):
    '''定義一個的fragment物件，用於訂閱 Sentinel 類別的通知.'''
    def decorator(func):
        @wraps(func)
        def wrap(self, arg):
            log.debug(f'Trigger fragment {self.__class__} {func.__name__}')
            # if task.name != name:
            #     return
            # if task.func != func.__name__:
            #     return
            func(self, arg)
            return func
        return wrap
    return decorator

def isActivity(name=None):
    def decorator(func):
        @wraps(func)
        def wrap(self, task):
            log.info(f'Trigger activity {func.__name__}')
            # if task.name != name:
            #     return
            # if task.func != func.__name__:
            #     return
            func(self, *task.args)
            return func
        return wrap
    return decorator









if __name__ == '__main__':
   pass



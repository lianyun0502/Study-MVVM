from __future__ import annotations
import abc
import typing
from typing import List, Dict, Any, Callable, Optional
from attrs import define
from PySide6 import QtWidgets, QtCore
from functools import wraps
from ViewModel.Logger import log

from ViewModel.ViewModelMediator import ViewModelEventMediator

@define
class Task():
    name:str = None
    func:str = None
    args:typing.Tuple = None

def isHandler():
    '''定義一個的handler物件，用於訂閱 ViewModelMediator類別的通知.'''
    def decorator(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            log.debug(f'Trigger handler {func.__name__}')
            if not isinstance(self, object):
                return None
            func(self, *args, **kwargs)
            return func
        return wrap
    return decorator


class ModelSentinel(QtCore.QObject):
    '''
    哨兵類別
    負責廣播當 ViewModel 狀態或屬性改變時，負責通知 View 類別執行 fragment。
    '''
    sig_task = QtCore.Signal(Task)
    sig_notify = QtCore.Signal(object)
    sig_message = QtCore.Signal(str)
    sig_error = QtCore.Signal(str)
    sig_state = QtCore.Signal(object)

class Repository:
    '''
    資料倉庫類別
    負責在 View model 內部狀態或希望記錄的資料過多時，將狀態或資料結構存進此類別
    '''
    ...

class ViewModel():
    '''
    View model 類別
    負責紀錄 view 的狀態及顯示邏輯，以及提供 Domain model 的使用介面。
    '''
    sentinel = ModelSentinel()
    def __init__(self, name:str, mediator:ViewModelEventMediator):
        self.name = name
        self.mediator = mediator
        self.plugins:Dict[str, ViewModel] = {}

    @abc.abstractmethod
    def render(self)->None:
        '''
        渲染 View 的抽象介面
        '''
        ...

    def addPlugin(self, name:str, plugin:ViewModel)->None:
        '''加入 plugin 的view model進行管理'''
        self.plugins.update({name:plugin})
        return

class Results(typing.Protocol):
    '''Class Results's interface.'''
    ...

class FiniteReceiveMachine(typing.Protocol):
    '''Class Results's interface.'''
    def trigger(self,**kwargs)->None:...

    def pause(self)->None:...

    def stop(self)->None:...

class ViewModelUpdater(ViewModel):
    '''此類別為 ViewModel 的子類別，用於需要使用FiniteReceiveMachine的類別。'''
    def __init__(self, name: str, mediator: ViewModelEventMediator):
        super().__init__(name=name, mediator=mediator)
        self.FRM:Optional[FiniteReceiveMachine] = None
    @abc.abstractmethod
    def update(self, results:Results)->None:
        '''
        接取來自 FRM 類別的推送(Results類別)，並發起來自 Receiver 資料更新的通知。
        '''
        ...
    def startFRM(self)->None:...

    def stopFRM(self)->None:...














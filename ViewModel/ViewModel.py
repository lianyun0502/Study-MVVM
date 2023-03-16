from __future__ import annotations

import abc
import gc
import typing
from typing import List, Dict, Any, Callable
from attrs import define
from PySide6 import QtWidgets, QtCore
from functools import wraps
import logging

log = logging.getLogger('ViewModel')
log.setLevel(logging.INFO)
handler = logging.StreamHandler()

class CustomFormatter(logging.Formatter):
    normal = '\x1b[20;1m'
    white = '\x1b[49;1m'
    green = '\x1b[32;1m'
    yellow = '\x1b[33;1m'
    Magenta = '\x1b[35;1m'
    red = '\x1b[31;1m'
    reset = '\x1b[0m'
    def __init__(self, fmt="%(asctime)s | %(name)-10s| %(levelname)-8s|: %(message)s"):
        super().__init__(fmt)
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: f"{self.green} {self.fmt} {self.reset}",
            logging.INFO: f"{self.white} {self.fmt} {self.reset}",
            logging.WARNING: f"{self.yellow} {self.fmt} {self.reset}",
            logging.ERROR: f"{self.Magenta} {self.fmt} {self.reset}",
            logging.CRITICAL: f"{self.red} {self.fmt} {self.reset}"
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
handler.setFormatter(CustomFormatter())
log.addHandler(handler)

@define
class Task():
    name:str = None
    func:str = None
    args:typing.Tuple = None

# 定義一個可銷毀的handler物件
def isHandler():
    def decorator(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            log.info(f'Trigger handler {func.__name__}')
            if not isinstance(self, object):
                return None
            func(self, *args, **kwargs)
            return func
        return wrap
    return decorator

class ViewModelMediator: ## handler無法回收
    '''
    View Model 仲介類別
    負責 View Model間的通信。
    '''
    def __init__(self):
        self._events:dict[str, set[Callable[..., Any]]] = {}

    # 註冊事件
    def register(self, event_name:str, handler:Callable[..., Any]):
        if event_name not in self._events:
            self._events[event_name] = set([])
        self._events[event_name].add(handler)

    def unregister(self, event_name:str, handler:Callable[..., Any]):
        if event_name not in self._events:
            return
        self._events[event_name].remove(handler)

    # 觸發事件
    def trigger(self, event_name:str, *args, **kwargs):
        assert self._events.get(event_name) is not None
        for handler in self._events[event_name]:
            handler(*args, **kwargs)


class ModelSentinel(QtCore.QObject):
    '''
    哨兵類別
    負責廣播當 ViewModel 狀態改變時 view 上 function 的訂閱者要改變狀態。
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
    def __init__(self, name:str):
        self.name = name
        self.plugins:Dict[str, ViewModel] = {}

    @abc.abstractmethod
    def render(self):...


    def addPlugin(self, name:str, plugin:ViewModel):
        self.plugins.update({name:plugin})
        return




if __name__ == '__main__':

    m = ViewModelMediator()
    class test:
        def __init__(self, m:ViewModelMediator):
            m.register('777', self.rrr)

        @isHandler()
        def rrr(self):
            print(self)

    t1 = test(m)
    t2 = test(m)
    t3 = test(m)

    m.trigger('777')

    del t1
    print('')
    gc.collect()
    m.trigger('777')
    print('')







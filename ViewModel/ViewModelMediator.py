import weakref
from typing import List, Dict, Any, Callable
from ViewModel.Logger import log

class ViewModelEventMediator:
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
        self._events[event_name].add(weakref.WeakMethod(handler))

    def unregister(self, event_name:str, handler:Callable[..., Any]):
        if event_name not in self._events:
            return
        self._events[event_name].remove(handler)

    # 觸發事件
    def trigger(self, event_name:str, *args, **kwargs):
        assert self._events.get(event_name) is not None
        for handler_ref in self._events[event_name]:
            handler = handler_ref()
            if handler is None:
                # self._events[event_name].remove(handler_ref)
                continue
            handler(*args, **kwargs)

if __name__ == '__main__':
    m = ViewModelEventMediator()
    class test:
        def __init__(self, m:ViewModelEventMediator):
            m.register('777', self.rrr)

        # @isHandler()
        def rrr(self):
            print(self)

    t1 = test(m)
    t2 = test(m)
    t3 = test(m)

    m.trigger('777')

    del t1
    print('')
    m.trigger('777')
    print('')
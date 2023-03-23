from __future__ import annotations
import threading
import time
from typing import Protocol, Optional, Any, Union
from threading import Timer
import logging

log = logging.getLogger('FRM')
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

class Updater(Protocol):
    '''
    Interface protocol for Updater.
    不能擅自修改
    '''
    def update(self, res) -> None:
        ...

    def setConfigs(self, **kwargs)->None:
        ...


class Receiver(Protocol):
    '''
    Interface protocol for Receiver.
    不能擅自修改
    '''
    def getResults(self)->Any:...

    def setConfigs(self, **kwargs)->None:...

    def trigger(self, **kwargs)->None:...

    def stop(self)->None:...

class RepeatTimer():
    def __init__(self, interval:float, func):
        self.daemon = False
        self.interval = interval
        self.func = func
        self.thread = Timer(interval=0, function=self.handle_function)
        self.thread.daemon = self.daemon

    def handle_function(self):
        self.func()
        self.thread = Timer(self.interval, self.handle_function)
        self.thread.daemon = self.daemon
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

class ReceiveThread(threading.Thread):
    is_start = False
    def __init__(self, interval:float, func, *args, **kargs):
        super().__init__(*args, **kargs)
        self._func = func
        self.interval =interval
    def run(self) -> None:
        if self.is_start:
            return
        self.is_start = True
        while self.is_start:
            time.sleep(self.interval)
            self._func()
        self.is_start = False

    def cancel(self):
        if not self.is_start:
            return
        self.is_start = False

class FiniteReceiveMachine:
    '''
    Receive data from receiver and update to updater.
    '''
    _updater: Optional[Updater] = None
    _receiver: Optional[Receiver] = None
    _start_Thread: Union[RepeatTimer | ReceiveThread] = None
    _is_start = False
    def __init__(self, receiver:Optional[Receiver]=None):
        self._receiver = receiver

    def __del__(self):
        self.stop()
        log.info("Close Finite Receive Machine...")

    def __repr__(self):
        return f'Receiver={self._receiver}, Updater={self._updater}'

    def setFRM(self, receiver:Receiver, updater:Updater=None):
        self.setReceiver(receiver)
        self.setUpdater(updater)

    def setReceiver(self, receiver):
        if self._is_start:
            raise Exception(f'Disable to set Receiver when FRM is launching.')
        self._receiver = receiver

    def setReceiverConfigs(self, **kwargs):
        if self._is_start:
            raise Exception(f"Disable to set Receiver's configs when FRM is launching.")
        self._receiver.setConfigs(**kwargs)

    def setUpdater(self, updater):
        if self._is_start:
            raise Exception(f'Disable to set Updater when FRM is launching.')
        self._updater = updater

    def trigger(self, **trigger_arg):
        if self._receiver is None:
            raise Exception(f'Disable to trigger FRM without delegate the receiver.')

        self._receiver.trigger(**trigger_arg)

    def start(self, interval:float=0, buffer=False):
        if self._is_start:
            # log.info('Your machine is launching')
            return
        if self._receiver is None:
            raise Exception(f'Disable to launch FRM without delegate the receiver.')
        self._start_Thread = RepeatTimer(interval, self.get)
        # self._start_Thread = ReceiveThread(interval, self.get)
        self._start_Thread.start()
        log.info('start FSM')
        self._is_start = True

    def stop(self):
        if not self._is_start:
            # log.info("You can't stop the machine if it's not launching")
            return
        if self._receiver is None:
            raise Exception(f'Disable to launch FRM without delegate the receiver.')
        self._start_Thread.cancel()
        log.info('stop FRM')
        if self._receiver is not None:
            self._receiver.stop()
        self._is_start = False

    def pause(self):
        if not self._is_start:
            # log.info("You can't pause the machine if it's not launching")
            return
        log.info('pause FRM')
        self._start_Thread.cancel()
        self._is_start = False

    def get(self):
        log.debug('getting results')
        res = self._receiver.getResults()
        if res is None:
            return
        if self._updater is not None:
            self._updater.update(res)


if __name__ == '__main__':
    import sys

    class TestUpdater():
        def update(self, res) -> None:
            if res is None:
                return
            log.info(f'Receive results from FSM : {res}')

        def setConfigs(self, **kwargs) -> None:
            for k, v in kwargs.items():
                if not hasattr(self, k):
                    log.info('Attribute "{}" not in Updater.'.format(k))
                    continue
                self.__setattr__(k, v)
                log.info('Attribute "{}", set "{}"'.format(k, v))

    class TestReceiver():
        res = None
        chirps = 16
        def getResults(self) -> Any:
            res = self.res
            self.res = None
            return res

        def setConfigs(self, **kwargs) -> None:
            for k, v in kwargs.items():
                if not hasattr(self, k):
                    log.info('Attribute "{}" not in receiver.'.format(k))
                    continue
                self.__setattr__(k, v)
                log.info('Attribute "{}", set "{}"'.format(k, v))

        def trigger(self, **kwargs) -> None:
            self.setConfigs(**kwargs)
            log.info('trigger Receiver')


        def stop(self) -> None:
            log.info('stop Receiver')

    def main(r:Receiver, u:Updater):
        try:
            FRM = FiniteReceiveMachine()
            FRM.setFRM(r, u)
            FRM.trigger(chirps=32)
            while True:
                query = input('input query :')
                if query.upper() == 'PAUSE':
                    FRM.pause()
                elif query.upper() == 'RESTART':
                    FRM.start()
                elif query.upper() == 'START':
                    FRM.start()
                elif query.upper() == 'STOP':
                    FRM.stop()
                elif query.upper() == 'Q':
                    break
                else:
                    r.res = query
            sys.exit(FRM.stop())
        except Exception as e:
            log.warning(f'{e}')



    main(r=TestReceiver(), u=TestUpdater())








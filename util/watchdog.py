"""
   Copyright 2022 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from .logger import logger
import threading
import typing
import signal
import time


class Watchdog:
    __log_msg_prefix = "watchdog"
    __log_err_msg_prefix = f"{__log_msg_prefix} error"

    def __init__(self, monitor_callables: typing.Optional[typing.List[typing.Callable[..., bool]]] = None, shutdown_callables: typing.Optional[typing.List[typing.Callable]] = None, shutdown_signals: typing.Optional[typing.List[int]] = None, monitor_delay: int = 2):
        self.__monitor_callables = monitor_callables
        self.__shutdown_callables = shutdown_callables
        self.__monitor_delay = monitor_delay
        self.__shutdown_signals = list()
        self.__start_delay = None
        self.__thread = threading.Thread(target=self.__monitor, daemon=True)
        self.__event = threading.Event()
        self.__signal = None
        self.__stop = False
        if shutdown_signals:
            self.register_shutdown_signals(sig_nums=shutdown_signals)

    def __handle_shutdown(self, sig_num, stack_frame):
        if self.__signal is None:
            self.__signal = sig_num
            logger.warning(f"{Watchdog.__log_msg_prefix}: caught '{signal.Signals(sig_num).name}'")
            if self.__shutdown_callables:
                logger.info(f"{Watchdog.__log_msg_prefix}: initiating shutdown ...")
                for func in self.__shutdown_callables:
                    try:
                        func()
                    except Exception as ex:
                        logger.error(f"{Watchdog.__log_err_msg_prefix}: calling {func} failed: {ex}")
            self.__event.set()

    def __monitor(self):
        time.sleep(self.__start_delay)
        while not self.__signal:
            for func in self.__monitor_callables:
                try:
                    if not func():
                        signal.raise_signal(signal.SIGABRT)
                except Exception as ex:
                    logger.error(f"{Watchdog.__log_err_msg_prefix}: calling {func} failed: {ex}")
            time.sleep(self.__monitor_delay)
        self.__event.wait()
        logger.info(f"{Watchdog.__log_msg_prefix}: shutdown complete")

    def register_shutdown_signals(self, sig_nums: typing.List[int]):
        for num in sig_nums:
            if num not in self.__shutdown_signals:
                signal.signal(num, self.__handle_shutdown)
                self.__shutdown_signals.append(num)

    def register_shutdown_callables(self, callables: typing.List[typing.Callable]):
        if self.__shutdown_callables:
            self.__shutdown_callables += callables
        else:
            self.__shutdown_callables = callables

    def register_monitor_callables(self, callables: typing.List[typing.Callable[..., bool]]):
        if self.__monitor_callables:
            self.__monitor_callables += callables
        else:
            self.__monitor_callables = callables

    def start(self, delay=5):
        self.__start_delay = delay
        self.__thread.start()

    def join(self):
        self.__thread.join()

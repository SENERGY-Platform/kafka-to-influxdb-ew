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

__all__ = ("ShutdownHandler", )

from .logger import logger
import typing
import signal


class ShutdownHandler:
    __log_msg_prefix = "shutdown handler"
    __callables = None

    @staticmethod
    def register(sig_nums: typing.List[int], callables: typing.List[typing.Callable]):
        ShutdownHandler.__callables = callables
        for num in sig_nums:
            signal.signal(num, ShutdownHandler.__handle_signal)

    @staticmethod
    def __handle_signal(sig_num, stack_frame):
        logger.warning(f"{ShutdownHandler.__log_msg_prefix}: caught '{signal.Signals(sig_num).name}'")
        for func in ShutdownHandler.__callables:
            try:
                func()
            except Exception as ex:
                logger.error(f"{ShutdownHandler.__log_msg_prefix} error: calling {func} failed: {ex}")

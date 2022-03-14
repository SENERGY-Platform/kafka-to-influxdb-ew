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

from .config import *
from .logger import *
from .watchdog import *
import sevm


def print_init(git_info_file):
    init_txt = "kafka-to-influxdb-ew\n"
    with open(git_info_file, "r") as file:
        for line in file:
            init_txt += f"    {line.strip()}\n"
    print(init_txt.strip())


def config_to_dict(config):
    items = dict()
    for key, value in config.__dict__.items():
        if isinstance(value, sevm.Config):
            items[key] = config_to_dict(config=value)
        else:
            items[key] = value
    return items

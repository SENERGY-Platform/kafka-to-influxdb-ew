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

__all__ = ("InfluxDB",)

import ew_lib
import influxdb
import threading


class InfluxDB:
    def __init__(self, influxdb_client: influxdb.InfluxDBClient, kafka_data_client: ew_lib.clients.KafkaDataClient, filter_handler: ew_lib.filter.FilterHandler, event: threading.Event):
        self.__influxdb_client = influxdb_client
        self.__kafka_data_client = kafka_data_client
        self.__filter_handler = filter_handler
        self.__event = event
        self.__stop = False

    def stop(self):
        self.__stop = True

    def run(self):
        self.__event.wait()

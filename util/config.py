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

__all__ = ("Config", )

import sevm


class KafkaDataClient(sevm.Config):
    consumer_group_id = None
    subscribe_interval = 5


class KafkaFilterClient(sevm.Config):
    consumer_group_id = None
    consumer_group_id_postfix = None
    filter_topic = None
    poll_timeout = 1.0
    sync_delay = 30
    time_format = None
    utc = True


class InfluxDBConfig(sevm.Config):
    host = None
    port = None
    username = None
    password = None
    retries = 3
    timeout = 10


class WatchdogConfig(sevm.Config):
    monitor_delay = 2
    start_delay = 5


class Config(sevm.Config):
    logger_level = "warning"
    get_data_timeout = 5.0
    get_data_limit = 10000
    kafka_metadata_broker_list = None
    kafka_data_client = KafkaDataClient
    kafka_filter_client = KafkaFilterClient
    influxdb = InfluxDBConfig
    watchdog = WatchdogConfig

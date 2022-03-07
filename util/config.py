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


class KafkaConfig(sevm.Config):
    metadata_broker_list = None
    data_consumer_group_id = None
    filter_consumer_group_id = None
    filter_consumer_group_id_postfix = None
    filter_topic = None


class InfluxDBConfig(sevm.Config):
    influxdb_host = None
    influxdb_port = None
    influxdb_user = None
    influxdb_password = None
    time_precision = None


class Config(sevm.Config):
    logger_level = "warning"
    kafka = KafkaConfig
    influxdb = InfluxDBConfig

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

import util
import worker
import ew_lib
import confluent_kafka
import influxdb
import threading
import signal


if __name__ == '__main__':
    config = util.Config(prefix="conf", require_value=True)
    util.init_logger(config.logger_level)
    influxdb_client = influxdb.InfluxDBClient(
        host=config.influxdb.host,
        port=config.influxdb.port,
        username=config.influxdb.username,
        password=config.influxdb.password,
        retries=config.influxdb.retries,
        timeout=config.influxdb.timeout
    )
    event = threading.Event()
    filter_handler = ew_lib.filter.FilterHandler()
    kafka_filter_client = ew_lib.clients.KafkaFilterClient(
        kafka_consumer=confluent_kafka.Consumer(
            {
                "metadata.broker.list": config.kafka.metadata_broker_list,
                "group.id": f"{config.kafka.filter_consumer_group_id}_{config.kafka.filter_consumer_group_id_postfix}",
                "auto.offset.reset": "earliest",
            }
        ),
        filter_handler=filter_handler,
        filter_topic=config.kafka.filter_topic
    )
    kafka_filter_client.set_on_sync(event.set)
    kafka_data_client = ew_lib.clients.KafkaDataClient(
        kafka_consumer=confluent_kafka.Consumer(
            {
                "metadata.broker.list": config.kafka.metadata_broker_list,
                "group.id": config.kafka.data_consumer_group_id,
                "auto.offset.reset": "earliest",
                "partition.assignment.strategy": "cooperative-sticky"
            }
        ),
        filter_handler=filter_handler
    )
    influxdb_worker = worker.InfluxDB(
        influxdb_client=influxdb_client,
        kafka_data_client=kafka_data_client,
        filter_handler=filter_handler,
        event=event
    )
    util.ShutdownHandler.register(
        sig_nums=[signal.SIGTERM, signal.SIGINT],
        callables=[influxdb_worker.stop, influxdb_client.close, kafka_data_client.stop, kafka_filter_client.stop]
    )
    kafka_filter_client.start()
    kafka_data_client.start()
    influxdb_worker.run()

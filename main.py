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
import ew
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
                "metadata.broker.list": config.kafka_metadata_broker_list,
                "group.id": f"{config.kafka_filter_client.consumer_group_id}_{config.kafka_filter_client.consumer_group_id_postfix}",
                "auto.offset.reset": "earliest",
            }
        ),
        filter_handler=filter_handler,
        filter_topic=config.kafka_filter_client.filter_topic,
        poll_timeout=config.kafka_filter_client.poll_timeout,
        time_format=config.kafka_filter_client.time_format,
        utc=config.kafka_filter_client.utc
    )
    kafka_filter_client.set_on_sync(callable=event.set, sync_delay=config.kafka_filter_client.sync_delay)
    kafka_data_client = ew_lib.clients.KafkaDataClient(
        kafka_consumer=confluent_kafka.Consumer(
            {
                "metadata.broker.list": config.kafka_metadata_broker_list,
                "group.id": config.kafka_data_client.consumer_group_id,
                "auto.offset.reset": "earliest",
                "partition.assignment.strategy": "cooperative-sticky"
            }
        ),
        filter_handler=filter_handler,
        subscribe_interval=config.kafka_data_client.subscribe_interval
    )
    export_worker = ew.ExportWorker(
        influxdb_client=influxdb_client,
        kafka_data_client=kafka_data_client,
        filter_handler=filter_handler,
        event=event,
        get_data_timeout=config.get_data_timeout,
        get_data_limit=config.get_data_limit
    )
    util.ShutdownHandler.register(
        sig_nums=[signal.SIGTERM, signal.SIGINT, signal.SIGABRT],
        callables=[export_worker.stop, influxdb_client.close, kafka_data_client.stop, kafka_filter_client.stop]
    )
    kafka_filter_client.start()
    kafka_data_client.start()
    export_worker.run()
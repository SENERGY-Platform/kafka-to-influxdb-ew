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
import ew_lib
import confluent_kafka
import signal


if __name__ == '__main__':
    config = util.Config(prefix="conf", require_value=True)
    util.init_logger(config.logger_level)
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

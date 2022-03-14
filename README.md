kafka-to-influxdb-ew
================

Kafka to InfluxDB export-worker.

## Docker compose template

```yaml
version: "2"

services:
  kafka-to-influxdb-ew:
    image: ghcr.io/senergy-platform/kafka-to-influxdb-ew:prod
    environment:
      CONF_LOGGER_LEVEL: 
      CONF_GET_DATA_TIMEOUT: 
      CONF_GET_DATA_LIMIT: 
      CONF_KAFKA_METADATA_BROKER_LIST: 
      CONF_KAFKA_CONSUMER_GROUP_ID_POSTFIX: 
      CONF_KAFKA_DATA_CLIENT_CONSUMER_GROUP_ID: 
      CONF_KAFKA_DATA_CLIENT_SUBSCRIBE_INTERVAL: 
      CONF_KAFKA_FILTER_CLIENT_CONSUMER_GROUP_ID: 
      CONF_KAFKA_FILTER_CLIENT_FILTER_TOPIC: 
      CONF_KAFKA_FILTER_CLIENT_POLL_TIMEOUT: 
      CONF_KAFKA_FILTER_CLIENT_SYNC_DELAY: 
      CONF_KAFKA_FILTER_CLIENT_TIME_FORMAT: 
      CONF_KAFKA_FILTER_CLIENT_UTC: 
      CONF_INFLUXDB_HOST: 
      CONF_INFLUXDB_PORT: 
      CONF_INFLUXDB_USERNAME: 
      CONF_INFLUXDB_PASSWORD: 
      CONF_INFLUXDB_RETRIES: 
      CONF_INFLUXDB_TIMEOUT: 
      CONF_WATCHDOG_MONITOR_DELAY: 
      CONF_WATCHDOG_START_DELAY:
```
kafka-to-influxdb-ew
================

Kafka to InfluxDB export-worker.

## Docker compose template

```yaml
version: "2"

services:
  kafka-to-influxdb-ew-0:
    image: ghcr.io/senergy-platform/kafka-to-influxdb-ew:prod
    environment:
      CONF_LOGGER_LEVEL: 
      CONF_GET_DATA_TIMEOUT: 
      CONF_GET_DATA_LIMIT: 
      CONF_KAFKA_METADATA_BROKER_LIST: 
      CONF_KAFKA_CONSUMER_GROUP_ID_POSTFIX: 
      CONF_KAFKA_DATA_CLIENT_SUBSCRIBE_INTERVAL: 
      CONF_KAFKA_DATA_CLIENT_KAFKA_MSG_ERR_IGNORE: 
      CONF_KAFKA_DATA_CONSUMER_GROUP_ID: 
      CONF_KAFKA_DATA_CONSUMER_AUTO_OFFSET_RESET: 
      CONF_KAFKA_DATA_CONSUMER_PARTITION_ASSIGNMENT_STRATEGY: 
      CONF_KAFKA_FILTER_CLIENT_FILTER_TOPIC: 
      CONF_KAFKA_FILTER_CLIENT_POLL_TIMEOUT: 
      CONF_KAFKA_FILTER_CLIENT_SYNC_DELAY: 
      CONF_KAFKA_FILTER_CLIENT_TIME_FORMAT: 
      CONF_KAFKA_FILTER_CLIENT_UTC: 
      CONF_KAFKA_FILTER_CONSUMER_GROUP_ID: 'kafka-to-influxdb-ew-0'
      CONF_INFLUXDB_HOST: 
      CONF_INFLUXDB_PORT: 
      CONF_INFLUXDB_USERNAME: 
      CONF_INFLUXDB_PASSWORD: 
      CONF_INFLUXDB_RETRIES: 
      CONF_INFLUXDB_TIMEOUT: 
      CONF_WATCHDOG_MONITOR_DELAY: 
      CONF_WATCHDOG_START_DELAY:

  kafka-to-influxdb-ew-1:
    image: ghcr.io/senergy-platform/kafka-to-influxdb-ew:prod
    environment:
      CONF_LOGGER_LEVEL: 
      CONF_GET_DATA_TIMEOUT: 
      CONF_GET_DATA_LIMIT: 
      CONF_KAFKA_METADATA_BROKER_LIST: 
      CONF_KAFKA_CONSUMER_GROUP_ID_POSTFIX: 
      CONF_KAFKA_DATA_CLIENT_SUBSCRIBE_INTERVAL: 
      CONF_KAFKA_DATA_CLIENT_KAFKA_MSG_ERR_IGNORE: 
      CONF_KAFKA_DATA_CONSUMER_GROUP_ID: 
      CONF_KAFKA_DATA_CONSUMER_AUTO_OFFSET_RESET: 
      CONF_KAFKA_DATA_CONSUMER_PARTITION_ASSIGNMENT_STRATEGY: 
      CONF_KAFKA_FILTER_CLIENT_FILTER_TOPIC: 
      CONF_KAFKA_FILTER_CLIENT_POLL_TIMEOUT: 
      CONF_KAFKA_FILTER_CLIENT_SYNC_DELAY: 
      CONF_KAFKA_FILTER_CLIENT_TIME_FORMAT: 
      CONF_KAFKA_FILTER_CLIENT_UTC: 
      CONF_KAFKA_FILTER_CONSUMER_GROUP_ID: 'kafka-to-influxdb-ew-1'
      CONF_INFLUXDB_HOST: 
      CONF_INFLUXDB_PORT: 
      CONF_INFLUXDB_USERNAME: 
      CONF_INFLUXDB_PASSWORD: 
      CONF_INFLUXDB_RETRIES: 
      CONF_INFLUXDB_TIMEOUT: 
      CONF_WATCHDOG_MONITOR_DELAY: 
      CONF_WATCHDOG_START_DELAY:
```

## Kubernetes deployment template

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka-to-influxdb-ew
spec:
  selector:
    matchLabels:
      app: export-worker
  replicas: 2
  template:
    metadata:
      labels:
        app: export-worker
    spec:
      containers:
        - name: export-worker
          image: ghcr.io/senergy-platform/kafka-to-influxdb-ew:prod
          imagePullPolicy: Always
          env:
            - name: CONF_LOGGER_LEVEL
              value: 
            - name: CONF_GET_DATA_TIMEOUT
              value: 
            - name: CONF_GET_DATA_LIMIT
              value: 
            - name: CONF_KAFKA_METADATA_BROKER_LIST
              value: 
            - name: CONF_KAFKA_CONSUMER_GROUP_ID_POSTFIX
              value: 
            - name: CONF_KAFKA_DATA_CLIENT_SUBSCRIBE_INTERVAL
              value: 
            - name: CONF_KAFKA_DATA_CLIENT_KAFKA_MSG_ERR_IGNORE
              value: 
            - name: CONF_KAFKA_DATA_CONSUMER_GROUP_ID
              value: 
            - name: CONF_KAFKA_DATA_CONSUMER_AUTO_OFFSET_RESET
              value: 
            - name: CONF_KAFKA_DATA_CONSUMER_PARTITION_ASSIGNMENT_STRATEGY
              value: 
            - name: CONF_KAFKA_FILTER_CLIENT_FILTER_TOPIC
              value: 
            - name: CONF_KAFKA_FILTER_CLIENT_POLL_TIMEOUT
              value: 
            - name: CONF_KAFKA_FILTER_CLIENT_SYNC_DELAY
              value: 
            - name: CONF_KAFKA_FILTER_CLIENT_TIME_FORMAT
              value: 
            - name: CONF_KAFKA_FILTER_CLIENT_UTC
              value: 
            - name: CONF_KAFKA_FILTER_CONSUMER_GROUP_ID
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: CONF_INFLUXDB_HOST
              value: 
            - name: CONF_INFLUXDB_PORT
              value: 
            - name: CONF_INFLUXDB_USERNAME
              value: 
            - name: CONF_INFLUXDB_PASSWORD
              value: 
            - name: CONF_INFLUXDB_RETRIES
              value: 
            - name: CONF_INFLUXDB_TIMEOUT
              value: 
            - name: CONF_WATCHDOG_MONITOR_DELAY
              value: 
            - name: CONF_WATCHDOG_START_DELAY
              value: 
      restartPolicy: Always
```
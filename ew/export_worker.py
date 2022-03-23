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

__all__ = ("ExportWorker", "validate_filter")

import util
import ew_lib
import mf_lib
import influxdb
import threading
import typing
import datetime


class ExportArgs:
    db_name = "db_name"
    time_key = "time_key"
    time_format = "time_format"
    time_precision = "time_precision"
    utc = "utc"


class InfluxDBPoint:
    measurement = "measurement"
    fields = "fields"
    tags = "tags"
    time = "time"


class WritePointsError(Exception):
    def __init__(self, points, db_name, ex):
        pts = dict()
        for point in points:
            if point[InfluxDBPoint.measurement] not in pts:
                pts[point[InfluxDBPoint.measurement]] = 1
            else:
                pts[point[InfluxDBPoint.measurement]] += 1
        super().__init__(f"writing points failed: reason={util.get_exception_str(ex)} database={db_name} points={pts}")


class ValidateFilterError(Exception):
    def __init__(self, ex):
        super().__init__(util.get_exception_str(ex))


def validate_filter(filter: dict):
    try:
        if ExportArgs.db_name not in filter["args"]:
            return False
        if not filter["args"][ExportArgs.db_name]:
            return False
        if ExportArgs.time_key in filter["args"]:
            if not filter['args'][ExportArgs.time_key]:
                return False
            if f"{filter['args'][ExportArgs.time_key]}:string:extra" not in filter["mappings"]:
                return False
        return True
    except Exception as ex:
        raise ValidateFilterError(ex)


def convert_timestamp(timestamp: str, fmt: str, utc: bool):
    time_obj = datetime.datetime.strptime(timestamp, fmt)
    if utc:
        return f"{time_obj.isoformat()}Z"
    else:
        return f"{time_obj.isoformat()}"


def gen_point(export_id, export_data, export_extra, time_key: typing.Optional[str] = None, time_format: typing.Optional[str] = None, utc: typing.Optional[bool] = None) -> typing.Dict:
    point = {
        InfluxDBPoint.measurement: export_id,
        InfluxDBPoint.fields: export_data
    }
    if time_key:
        if utc is None:
            utc = True
        point[InfluxDBPoint.time] = convert_timestamp(timestamp=export_extra[time_key], fmt=time_format, utc=utc) if time_format else export_extra[time_key]
    if len(export_extra) > 1 and time_key:
        point[InfluxDBPoint.tags] = {key: val for key, val in export_extra.items() if key != time_key}
    elif export_extra and not time_key:
        point[InfluxDBPoint.tags] = export_extra
    return point


class ExportWorker:
    __log_msg_prefix = "export worker"
    __log_err_msg_prefix = f"{__log_msg_prefix} error"

    def __init__(self, influxdb_client: influxdb.InfluxDBClient, data_client: ew_lib.DataClient, filter_client: ew_lib.FilterClient, get_data_timeout: float = 5.0, get_data_limit: int = 10000):
        self.__influxdb_client = influxdb_client
        self.__data_client = data_client
        self.__filter_client = filter_client
        self.__filter_sync_event = threading.Event()
        self.__get_data_timeout = get_data_timeout
        self.__get_data_limit = get_data_limit
        self.__filter_sync_err = False
        self.__stop = False
        self.__stopped = False

    def _gen_points_batch(self, exports_batch: typing.List[mf_lib.FilterResult]):
        points_batch = dict()
        for result in exports_batch:
            for export_id in result.filter_ids:
                try:
                    export_args = self.__filter_client.handler.get_filter_args(id=export_id)
                    db_name = export_args[ExportArgs.db_name]
                    time_precision = export_args.get(ExportArgs.time_precision)
                    if db_name not in points_batch:
                        points_batch[db_name] = {time_precision: list()}
                    if time_precision not in points_batch[db_name]:
                        points_batch[db_name][time_precision] = list()
                    points_batch[db_name][time_precision].append(gen_point(
                        export_id=export_id,
                        export_data=result.data,
                        export_extra=result.extra,
                        time_key=export_args.get(ExportArgs.time_key),
                        time_format=export_args.get(ExportArgs.time_format),
                        utc=export_args.get(ExportArgs.utc)
                    ))
                except Exception as ex:
                    util.logger.error(f"{ExportWorker.__log_err_msg_prefix}: generating points failed: reason={util.get_exception_str(ex)} export_id={export_id}")
        return points_batch

    def _write_points_batch(self, points_batch: typing.Dict):
        for db_name, batch in points_batch.items():
            for time_precision, points in batch.items():
                while True:
                    try:
                        self.__influxdb_client.write_points(
                            points=points,
                            time_precision=time_precision,
                            database=db_name,
                        )
                        break
                    except influxdb.client.InfluxDBClientError as ex:
                        if ex.code == 404:
                            self.__influxdb_client.create_database(dbname=db_name)
                        else:
                            raise WritePointsError(points, db_name, ex)
                    except Exception as ex:
                        raise WritePointsError(points, db_name, ex)

    def set_filter_sync(self, err: bool):
        self.__filter_sync_err = err
        self.__filter_sync_event.set()

    def stop(self):
        self.__stop = True

    def is_alive(self):
        return not self.__stopped

    def run(self):
        util.logger.info(f"{ExportWorker.__log_msg_prefix}: waiting for filter synchronisation ...")
        self.__filter_sync_event.wait()
        if not self.__filter_sync_err:
            util.logger.info(f"{ExportWorker.__log_msg_prefix}: starting export consumption ...")
            while not self.__stop:
                try:
                    exports_batch = self.__data_client.get_exports_batch(
                        timeout=self.__get_data_timeout,
                        limit=self.__get_data_limit,
                    )
                    if exports_batch:
                        if exports_batch[1]:
                            raise RuntimeError([str(ex) for ex in exports_batch[1]])
                        if exports_batch[0]:
                            self._write_points_batch(points_batch=self._gen_points_batch(exports_batch=exports_batch[0]))
                            self.__data_client.store_offsets()
                except WritePointsError as ex:
                    util.logger.critical(f"{ExportWorker.__log_err_msg_prefix}: {ex}")
                    self.__stop = True
                except Exception as ex:
                    util.logger.critical(f"{ExportWorker.__log_err_msg_prefix}: consuming exports failed: reason={util.get_exception_str(ex)}")
                    self.__stop = True
        self.__stopped = True

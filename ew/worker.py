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

__all__ = ("ExportWorker", )

from .util import *
from .model import *
import util
import ew_lib
import mf_lib
import influxdb
import threading
import typing
import logging


class ExportWorker:
    __log_msg_prefix = "export worker"
    __log_err_msg_prefix = f"{__log_msg_prefix} error"
    __influxdb_err_status_codes = (400, 413)

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
            if result.ex:
                util.logger.error(f"{ExportWorker.__log_err_msg_prefix}: generating points failed: reason={get_exception_str(result.ex)} export_ids={result.filter_ids}")
            else:
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
                            cast_map=export_args.get(ExportArgs.type_casts),
                            time_key=export_args.get(ExportArgs.time_key),
                            time_format=export_args.get(ExportArgs.time_format),
                            utc=export_args.get(ExportArgs.utc)
                        ))
                    except Exception as ex:
                        util.logger.error(f"{ExportWorker.__log_err_msg_prefix}: generating point failed: reason={get_exception_str(ex)} export_id={export_id}")
        return points_batch

    def _write_points(self, points: typing.List[typing.Dict], db_name: str, time_precision: str, is_retry=False):
        try:
            self.__influxdb_client.write_points(points=points, time_precision=time_precision, database=db_name)
        except influxdb.client.InfluxDBClientError as ex:
            if ex.code == 404:
                if not is_retry:
                    self.__influxdb_client.create_database(dbname=db_name)
                    self._write_points(points=points, db_name=db_name, time_precision=time_precision, is_retry=True)
                else:
                    raise WritePointsError(points, ex)
            elif ex.code in ExportWorker.__influxdb_err_status_codes:
                util.logger.warning(f"{ExportWorker.__log_msg_prefix}: writing points batch failed, writing points per measurement ...")
                groups = dict()
                for point in points:
                    if point[InfluxDBPoint.measurement] not in groups:
                        groups[point[InfluxDBPoint.measurement]] = list()
                    groups[point[InfluxDBPoint.measurement]].append(point)
                for group in groups.values():
                    try:
                        self.__influxdb_client.write_points(points=group, time_precision=time_precision, database=db_name)
                    except influxdb.client.InfluxDBClientError as ex:
                        util.logger.error(f"{ExportWorker.__log_err_msg_prefix}: {WritePointsError(group, ex)}")
            else:
                raise WritePointsError(points, ex)
        except Exception as ex:
            raise WritePointsError(points, ex)

    def _write_points_batch(self, points_batch: typing.Dict):
        if util.logger.level == logging.DEBUG:
            pts_total = 0
            for b in points_batch.values():
                for pts in b.values():
                    pts_total += len(pts)
            util.logger.debug(f"{ExportWorker.__log_msg_prefix}: writing points batch: points_total={pts_total}")
        for db_name, batch in points_batch.items():
            for time_precision, points in batch.items():
                self._write_points(points=points, db_name=db_name, time_precision=time_precision)

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
                        data_ignore_missing_keys=True
                    )
                    if exports_batch:
                        if exports_batch[1]:
                            raise RuntimeError(set(str(ex) for ex in exports_batch[1]))
                        if exports_batch[0]:
                            self._write_points_batch(points_batch=self._gen_points_batch(exports_batch=exports_batch[0]))
                            self.__data_client.store_offsets()
                except WritePointsError as ex:
                    util.logger.critical(f"{ExportWorker.__log_err_msg_prefix}: {ex}")
                    self.__stop = True
                except Exception as ex:
                    util.logger.critical(f"{ExportWorker.__log_err_msg_prefix}: consuming exports failed: reason={get_exception_str(ex)}")
                    self.__stop = True
        self.__stopped = True

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

from .model import *
from .converter import *
import traceback
import datetime
import typing

influxdb_time_precision_values = ("s", "m", "ms", "u")


class WritePointsError(Exception):
    def __init__(self, points, db_name, ex):
        pts = dict()
        for point in points:
            if point[InfluxDBPoint.measurement] not in pts:
                pts[point[InfluxDBPoint.measurement]] = 1
            else:
                pts[point[InfluxDBPoint.measurement]] += 1
        super().__init__(f"writing points failed: reason={get_exception_str(ex)} database='{db_name}' points_per_measurement={pts}")


class ValidateFilterError(Exception):
    def __init__(self, ex):
        super().__init__(get_exception_str(ex))


def validate_filter(filter: dict):
    try:
        if ExportArgs.db_name not in filter["args"]:
            return False
        if not filter["args"][ExportArgs.db_name]:
            return False
        if ExportArgs.time_key in filter["args"]:
            if not filter['args'][ExportArgs.time_key]:
                return False
            if f"{filter['args'][ExportArgs.time_key]}:extra" not in filter["mappings"]:
                return False
        if ExportArgs.time_precision in filter["args"] and filter["args"][ExportArgs.time_precision] not in influxdb_time_precision_values:
            return False
        if ExportArgs.type_casts in filter["args"]:
            for val in filter["args"][ExportArgs.type_casts].values():
                if val not in type_casts:
                    return False
        return True
    except Exception as ex:
        raise ValidateFilterError(ex)


def cast_type(key, val, cast_map):
    return type_casts[cast_map[key]](val) if key in cast_map and val is not None else val


def convert_timestamp(timestamp: str, fmt: str, utc: bool):
    time_obj = datetime.datetime.strptime(timestamp, fmt)
    if utc:
        return f"{time_obj.isoformat()}Z"
    else:
        return f"{time_obj.isoformat()}"


def gen_point(export_id, export_data, export_extra, cast_map: typing.Optional[typing.Dict] = None, time_key: typing.Optional[str] = None, time_format: typing.Optional[str] = None, utc: typing.Optional[bool] = None) -> typing.Dict:
    point = {
        InfluxDBPoint.measurement: export_id,
        InfluxDBPoint.fields: {key: cast_type(key=key, val=val, cast_map=cast_map) for key, val in export_data.items()} if cast_map else export_data
    }
    if time_key:
        if utc is None:
            utc = True
        point[InfluxDBPoint.time] = convert_timestamp(timestamp=export_extra[time_key], fmt=time_format, utc=utc) if time_format else export_extra[time_key]
    if len(export_extra) > 1 and time_key:
        point[InfluxDBPoint.tags] = {key: cast_type(key=key, val=val, cast_map=cast_map) for key, val in export_extra.items() if key != time_key} if cast_map else {key: val for key, val in export_extra.items() if key != time_key}
    elif export_extra and not time_key:
        point[InfluxDBPoint.tags] = {key: cast_type(key=key, val=val, cast_map=cast_map) for key, val in export_extra.items()} if cast_map else export_extra
    return point


def get_exception_str(ex):
    return "[" + ", ".join([item.strip().replace("\n", " ") for item in traceback.format_exception_only(type(ex), ex)]) + "]"
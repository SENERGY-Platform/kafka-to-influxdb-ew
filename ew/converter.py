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

import json

bool_true_strings = {"True", "true", "1"}
bool_false_strings = {"False", "false", "0"}


def string_to_boolean(string):
    if string in bool_true_strings:
        return True
    elif string in bool_false_strings:
        return False
    else:
        raise ValueError(string)


def object_to_string(obj):
    return json.dumps(obj, separators=(',', ':'))


# https://json-schema.org/understanding-json-schema/reference/type.html
type_casts = {
    ":integer": int,
    ":number": float,
    ":string": str,
    ":boolean": bool,
    "string:boolean": string_to_boolean,
    "object:string": object_to_string,
    "array:string": object_to_string
}
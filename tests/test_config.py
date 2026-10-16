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

import os
import unittest
import unittest.mock
import util


class TestConfigKeys(unittest.TestCase):
    def test_no_values(self):
        secret = "test-secret-value-4970"
        with unittest.mock.patch.dict(os.environ, {"CONF_INFLUXDB_PASSWORD": secret}):
            config = util.Config(prefix="conf")
        self.assertIn(secret, str(config))
        keys = util.config_keys(config)
        self.assertNotIn(secret, str(keys))
        self.assertIn("influxdb.password", keys)
        self.assertIn("influxdb.host", keys)
        self.assertIn("kafka.metadata_broker_list", keys)
        self.assertIn("logger_level", keys)
        self.assertNotIn("influxdb", keys)

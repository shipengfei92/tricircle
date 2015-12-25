# Copyright (c) 2015 Huawei Technologies Co., Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from mock import patch

import pecan
from pecan.configuration import set_config
from pecan.testing import load_test_app

from oslo_config import cfg
from oslo_config import fixture as fixture_config

from tricircle.api import app
from tricircle.common import context
from tricircle.db import core
from tricircle.tests import base


OPT_GROUP_NAME = 'keystone_authtoken'
cfg.CONF.import_group(OPT_GROUP_NAME, "keystonemiddleware.auth_token")


def fake_is_admin(ctx):
    return True


class API_FunctionalTest(base.TestCase):

    def setUp(self):
        super(API_FunctionalTest, self).setUp()

        self.addCleanup(set_config, {}, overwrite=True)

        cfg.CONF.register_opts(app.common_opts)

        self.CONF = self.useFixture(fixture_config.Config()).conf

        self.CONF.set_override('auth_strategy', 'noauth')
        self.CONF.set_override('tricircle_db_connection', 'sqlite:///:memory:')

        core.initialize()
        core.ModelBase.metadata.create_all(core.get_engine())
        self.context = context.Context()

        self.app = self._make_app()

    def _make_app(self, enable_acl=False):
        self.config = {
            'app': {
                'root': 'tricircle.api.controllers.root.RootController',
                'modules': ['tricircle.api'],
                'enable_acl': enable_acl,
                'errors': {
                    400: '/error',
                    '__force_dict__': True
                }
            },
        }

        return load_test_app(self.config)

    def tearDown(self):
        super(API_FunctionalTest, self).tearDown()
        cfg.CONF.unregister_opts(app.common_opts)
        pecan.set_config({}, overwrite=True)
        core.ModelBase.metadata.drop_all(core.get_engine())


class TestPodController(API_FunctionalTest):
    """Test version listing on root URI."""

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_post_no_input(self):
        pod_maps = [
            # missing pod_map
            {
                "pod_xxx":
                {
                    "dc_name": "dc1",
                    "pod_az_name": "az1"
                },
                "expected_error": 400
            }]

        for test_pod in pod_maps:
            response = self.app.post_json(
                '/v1.0/pods',
                dict(pod_xxx=test_pod['pod_xxx']),
                expect_errors=True)

            self.assertEqual(response.status_int,
                             test_pod['expected_error'])

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_post_invalid_input(self):

        pod_maps = [

            # missing az and pod
            {
                "pod_map":
                {
                    "dc_name": "dc1",
                    "pod_az_name": "az1"
                },
                "expected_error": 422
            },

            # missing pod
            {
                "pod_map":
                {
                    "az_name": "az1",
                    "dc_name": "dc1",
                    "pod_az_name": "az1"
                },
                "expected_error": 422
            },

            # missing pod
            {
                "pod_map":
                {
                    "az_name": "",
                    "dc_name": "dc1",
                    "pod_az_name": "az1"
                },
                "expected_error": 422
            },

            # missing az
            {
                "pod_map":
                {
                    "dc_name": "dc1",
                    "pod_name": "",
                    "pod_az_name": "az1"
                },
                "expected_error": 422
            },

            # az & pod == ""
            {
                "pod_map":
                {
                    "az_name": "",
                    "dc_name": "dc1",
                    "pod_name": "",
                    "pod_az_name": "az1"
                },
                "expected_error": 422
            },

            # invalid pod
            {
                "pod_map":
                {
                    "az_name": "az1",
                    "dc_name": "dc1",
                    "pod_name": "",
                    "pod_az_name": "az1"
                },
                "expected_error": 422
            }

            ]

        self._test_and_check(pod_maps)

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_post_duplicate_top_region(self):

        pod_maps = [

            # the first time to create TopRegion
            {
                "pod_map":
                {
                    "dc_name": "dc1",
                    "pod_name": "TopRegion",
                    "pod_az_name": "az1"
                },
                "expected_error": 200
            },

            {
                "pod_map":
                {
                    "dc_name": "dc1",
                    "pod_name": "TopRegion2",
                    "pod_az_name": ""
                },
                "expected_error": 409
            },

            ]

        self._test_and_check(pod_maps)

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_post_duplicate_pod(self):

        pod_maps = [

            # the first time to create TopRegion
            {
                "pod_map":
                {
                    "az_name": "AZ1",
                    "dc_name": "dc1",
                    "pod_name": "Pod1",
                    "pod_az_name": "az1"
                },
                "expected_error": 200
            },

            {
                "pod_map":
                {
                    "az_name": "AZ1",
                    "dc_name": "dc2",
                    "pod_name": "Pod1",
                    "pod_az_name": "az2"
                },
                "expected_error": 409
            },

            ]

        self._test_and_check(pod_maps)

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_post_pod_duplicate_top_region(self):

        pod_maps = [

            # the first time to create TopRegion
            {
                "pod_map":
                {
                    "dc_name": "dc1",
                    "pod_name": "TopRegion",
                    "pod_az_name": "az1"
                },
                "expected_error": 200
            },

            {
                "pod_map":
                {
                    "az_name": "AZ1",
                    "dc_name": "dc2",
                    "pod_name": "TopRegion",
                    "pod_az_name": "az2"
                },
                "expected_error": 409
            },

            ]

        self._test_and_check(pod_maps)

    def _test_and_check(self, pod_maps):

        for test_pod in pod_maps:
            response = self.app.post_json(
                '/v1.0/pods',
                dict(pod_map=test_pod['pod_map']),
                expect_errors=True)

            self.assertEqual(response.status_int,
                             test_pod['expected_error'])

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_get_all(self):

        pod_maps = [

            # the first time to create TopRegion
            {
                "pod_map":
                {
                    "az_name": "",
                    "dc_name": "dc1",
                    "pod_name": "TopRegion",
                    "pod_az_name": ""
                },
                "expected_error": 200
            },

            {
                "pod_map":
                {
                    "az_name": "AZ1",
                    "dc_name": "dc2",
                    "pod_name": "Pod1",
                    "pod_az_name": "az1"
                },
                "expected_error": 200
            },

            {
                "pod_map":
                {
                    "az_name": "AZ1",
                    "dc_name": "dc2",
                    "pod_name": "Pod2",
                    "pod_az_name": "az1"
                },
                "expected_error": 200
            },

            ]

        self._test_and_check(pod_maps)

        response = self.app.get('/v1.0/pods')

        self.assertEqual(response.status_int, 200)
        self.assertIn('TopRegion', response)
        self.assertIn('Pod1', response)
        self.assertIn('Pod2', response)

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_get_delete_one(self):

        pod_maps = [

            {
                "pod_map":
                {
                    "az_name": "AZ1",
                    "dc_name": "dc2",
                    "pod_name": "Pod1",
                    "pod_az_name": "az1"
                },
                "expected_error": 200
            },

            {
                "pod_map":
                {
                    "az_name": "AZ1",
                    "dc_name": "dc2",
                    "pod_name": "Pod2",
                    "pod_az_name": "az1"
                },
                "expected_error": 200
            },

            ]

        self._test_and_check(pod_maps)

        response = self.app.get('/v1.0/pods')
        self.assertEqual(response.status_int, 200)

        return_pod_maps = response.json

        for ret_pod in return_pod_maps['pod_maps']:

            _id = ret_pod['id']
            single_ret = self.app.get('/v1.0/pods/' + str(_id))

            self.assertEqual(single_ret.status_int, 200)

            one_pot_ret = single_ret.json
            get_one_pod = one_pot_ret['pod_map']

            self.assertEqual(get_one_pod['id'],
                             ret_pod['id'])

            self.assertEqual(get_one_pod['az_name'],
                             ret_pod['az_name'])

            self.assertEqual(get_one_pod['dc_name'],
                             ret_pod['dc_name'])

            self.assertEqual(get_one_pod['pod_name'],
                             ret_pod['pod_name'])

            self.assertEqual(get_one_pod['pod_az_name'],
                             ret_pod['pod_az_name'])

            _id = ret_pod['id']
            single_ret = self.app.delete('/v1.0/pods/' + str(_id))
            self.assertEqual(single_ret.status_int, 200)


class TestBindingController(API_FunctionalTest):
    """Test version listing on root URI."""

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_post_no_input(self):
        pod_bindings = [
            # missing pod_binding
            {
                "pod_xxx":
                {
                    "tenant_id": "dddddd",
                    "az_pod_map_id": "0ace0db2-ef33-43a6-a150-42703ffda643"
                },
                "expected_error": 400
            }]

        for test_pod in pod_bindings:
            response = self.app.post_json(
                '/v1.0/bindings',
                dict(pod_xxx=test_pod['pod_xxx']),
                expect_errors=True)

            self.assertEqual(response.status_int,
                             test_pod['expected_error'])

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_post_invalid_input(self):

        pod_bindings = [

            # missing tenant_id and or az_pod_map_id
            {
                "pod_binding":
                {
                    "tenant_id": "dddddd",
                    "az_pod_map_id": ""
                },
                "expected_error": 422
            },

            {
                "pod_binding":
                {
                    "tenant_id": "",
                    "az_pod_map_id": "0ace0db2-ef33-43a6-a150-42703ffda643"
                },
                "expected_error": 422
            },

            {
                "pod_binding":
                {
                    "tenant_id": "dddddd",
                },
                "expected_error": 422
            },

            {
                "pod_binding":
                {
                    "az_pod_map_id": "0ace0db2-ef33-43a6-a150-42703ffda643"
                },
                "expected_error": 422
            }

            ]

        self._test_and_check(pod_bindings)

    @patch.object(context, 'is_admin_context',
                  new=fake_is_admin)
    def test_bindings(self):

        pod_maps = [
            {
                "pod_map":
                {
                    "az_name": "AZ1",
                    "dc_name": "dc2",
                    "pod_name": "Pod1",
                    "pod_az_name": "az1"
                },
                "expected_error": 200
            }
        ]

        pod_bindings = [

            {
                "pod_binding":
                {
                    "tenant_id": "dddddd",
                    "az_pod_map_id": "0ace0db2-ef33-43a6-a150-42703ffda643"
                },
                "expected_error": 200
            },

            {
                "pod_binding":
                {
                    "tenant_id": "aaaaa",
                    "az_pod_map_id": "0ace0db2-ef33-43a6-a150-42703ffda643"
                },
                "expected_error": 200
            },

            {
                "pod_binding":
                {
                    "tenant_id": "dddddd",
                    "az_pod_map_id": "0ace0db2-ef33-43a6-a150-42703ffda643"
                },
                "expected_error": 409
            }
        ]

        self._test_and_check_podmap(pod_maps)
        _id = self._get_az_pod_id()
        self._test_and_check(pod_bindings, _id)

        # get all
        response = self.app.get('/v1.0/bindings')
        self.assertEqual(response.status_int, 200)

        # get one
        return_pod_bindings = response.json

        for ret_pod in return_pod_bindings['pod_bindings']:

            _id = ret_pod['id']
            single_ret = self.app.get('/v1.0/bindings/' + str(_id))
            self.assertEqual(single_ret.status_int, 200)

            one_pot_ret = single_ret.json
            get_one_pod = one_pot_ret['pod_binding']

            self.assertEqual(get_one_pod['id'],
                             ret_pod['id'])

            self.assertEqual(get_one_pod['tenant_id'],
                             ret_pod['tenant_id'])

            self.assertEqual(get_one_pod['az_pod_map_id'],
                             ret_pod['az_pod_map_id'])

            _id = ret_pod['id']
            single_ret = self.app.delete('/v1.0/bindings/' + str(_id))
            self.assertEqual(single_ret.status_int, 200)

    def _get_az_pod_id(self):
        response = self.app.get('/v1.0/pods')
        self.assertEqual(response.status_int, 200)
        return_pod_maps = response.json
        for ret_pod in return_pod_maps['pod_maps']:
            _id = ret_pod['id']
            return _id

    def _test_and_check(self, pod_bindings, _id=None):

        for test_pod in pod_bindings:

            if _id is not None:
                test_pod['pod_binding']['az_pod_map_id'] = str(_id)

            response = self.app.post_json(
                '/v1.0/bindings',
                dict(pod_binding=test_pod['pod_binding']),
                expect_errors=True)

            self.assertEqual(response.status_int,
                             test_pod['expected_error'])

    def _test_and_check_podmap(self, pod_maps):

        for test_pod in pod_maps:
            response = self.app.post_json(
                '/v1.0/pods',
                dict(pod_map=test_pod['pod_map']),
                expect_errors=True)

            self.assertEqual(response.status_int,
                             test_pod['expected_error'])

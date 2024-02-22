import os
import logging

from spaceone.core import utils, config
from spaceone.tester import TestCase, print_json
from google.protobuf.json_format import MessageToDict
import pprint

_LOGGER = logging.getLogger(__name__)

AKI = os.environ.get("AWS_ACCESS_KEY_ID", None)
SAK = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
ROLE_ARN = os.environ.get("ROLE_ARN", None)
EXTERNAL_ID = os.environ.get("EXTERNAL_ID", None)
REGION_NAME = os.environ.get("REGION_NAME", None)


if AKI == None or SAK == None:
    print(
        """
##################################################
# ERROR 
#
# Configure your AWS credential first for test
##################################################
example)

export AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>

"""
    )
    exit


class TestCollect(TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get("SPACEONE_TEST_CONFIG_FILE", "./config.yml")
    )
    endpoints = config.get("ENDPOINTS", {})
    secret_data = {
        "aws_access_key_id": AKI,
        "aws_secret_access_key": SAK,
    }

    if ROLE_ARN is not None:
        secret_data.update({"role_arn": ROLE_ARN})

    if EXTERNAL_ID is not None:
        secret_data.update({"external_id": EXTERNAL_ID})

    if REGION_NAME is not None:
        secret_data.update({"region_name": REGION_NAME})

    def test_init(self):
        v_info = self.inventory.Collector.init({"options": {}})
        print_json(v_info)

    def test_verify(self):
        options = {"domain": "mz.co.kr"}
        v_info = self.inventory.Collector.verify(
            {"options": options, "secret_data": self.secret_data}
        )
        print_json(v_info)

    def test_collect(self):
        options = {}
        # task_options = {
        #     'resource_type': 'inventory.CloudService',
        #     'region': 'ap-northeast-1',
        #     'service': 'EC2'
        # }
        options = {
            "resource_type": "inventory.CloudService",
            "region": "ap-northeast-2",
            "service": "DynamoDB",
        }
        filter = {}

        params = {"options": options, "secret_data": self.secret_data, "filter": filter}

        res_stream = self.inventory.Collector.collect(params)
        cnt = 0
        for res in res_stream:
            print_json(res)
            # d = MessageToDict(res, preserving_proto_field_name=True)
            # m = 'no cloud svc!\n'
            # unknown = False
            # if 'cloud_service_type' in d['resource'].keys():
            #     unknown = True
            #     m = "group : " + d['resource']['cloud_service_group'] + " type : " + d['resource']['cloud_service_type'] + '\n'
            # if unknown == False:
            #     print("WOW")
            # with open('changed_unknown_output_{number}.yaml'.format(number=cnt), 'w') as f:
            #     self.assertIsNotNone(res)
            #     pprint.pprint(MessageToDict(res, preserving_proto_field_name=True), f)
            # with open('output_{number}.yaml'.format(number=cnt), 'w') as f:
            #     self.assertIsNotNone(res)
            #     pprint.pprint(MessageToDict(res, preserving_proto_field_name=True), f)
            # cnt += 1

    def test_get_tasks(self):
        print(f"=================== start get_tasks! ==========================")
        options = {"service_filter": ["EC2"], "region_filter": ["ap-northeast-1"]}
        v_info = self.inventory.Job.get_tasks(
            {"options": options, "secret_data": self.secret_data}
        )
        print_json(v_info)

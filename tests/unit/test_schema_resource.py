# -*- coding: utf-8 -*-

import json

from tornado.testing import AsyncTestCase
from tornado.ioloop import IOLoop

from brainiak import schema_resource
from tests import TornadoAsyncTestCase


class MockResponse(object):

    def __init__(self, body):
        self.body = json.dumps(body)


class QueriesTestCase(TornadoAsyncTestCase):

    def setUp(self):
        self.io_loop = self.get_new_ioloop()
        self.original_query_class_schema = schema_resource.query_class_schema
        self.original_get_predicates_and_cardinalities = schema_resource.get_predicates_and_cardinalities

    def tearDown(self):
        if (not IOLoop.initialized() or self.io_loop is not IOLoop.instance()):
            self.io_loop.close(all_fds=True)
        super(AsyncTestCase, self).tearDown()
        schema_resource.query_class_schema = self.original_query_class_schema
        schema_resource.get_predicates_and_cardinalities = self.original_get_predicates_and_cardinalities

    def test_query_get_schema(self):
        expected_response = {
            "schema": {
                'class': 'http://test.domain.com/test_context/test_class',
                'comment': False,
                'label': False,
                'predicates': None
            }
        }

        # Mocks
        def mock_query_class_schema(class_uri, remember, callback):
            class_schema = {"results": {"bindings": [{"dummy_key": "dummy_value"}]}}
            tornado_response = MockResponse(class_schema)
            callback(tornado_response, remember)
        schema_resource.query_class_schema = mock_query_class_schema

        def mock_get_predicates_and_cardinalities(class_uri, class_schema, remember, callback):
            callback(class_schema, None)
        schema_resource.get_predicates_and_cardinalities = mock_get_predicates_and_cardinalities

        # Test target function
        def handle_test_query_get_schema(response):
            schema = response["schema"]
            self.assertIn("title", schema)
            self.assertIn("type", schema)
            self.assertIn("@id", schema)
            self.assertIn("properties", schema)
            # FIXME: enhance the structure of the response
            self.stop()

        schema_resource.get_schema("test_context", "test_class", handle_test_query_get_schema)
        self.wait()

# {'title': False, 'type': 'object', '@context': {'@langauge': 'pt'}, '$schema': 'http://json-schema.org/draft-03/schema#', '@id': 'http://semantica.globo.com/test_context/test_class', 'properties': None}

    # def test_query_cardinalities(self):
    #     effecive_response = None
    #
    #     def callback(response):
    #         global effecive_response
    #         effecive_response = response
    #
    #     query_cardinalities("http://test.domain.com", callback)
    #     self.assertEquals(effecive_response, None)
    #
    # def test_query_predicates(self):
    #     effecive_response = None
    #
    #     def callback(response):
    #         global effecive_response
    #         effecive_response = response
    #
    #     query_predicates("http://test.domain.com", callback)
    #     self.assertEquals(effecive_response, None)
    #
    # def test_query_predicates_without_lang(self):
    #     effecive_response = None
    #
    #     def callback(response):
    #         global effecive_response
    #         effecive_response = response
    #
    #     query_predicates_without_lang("http://test.domain.com", callback)
    #     self.assertEquals(effecive_response, None)

from unittest import TestCase
from mock import patch

from brainiak.search.search import do_search_query, do_search, _build_items
from brainiak import settings


class SearchUnitTestCase(TestCase):

    @patch("brainiak.search.search._get_search_fields", return_value=["label"])
    @patch("brainiak.search.search.do_search_query",
           return_value={
               u'hits': {
                   u'hits': [{
                       u'_index': u'example.onto',
                       u'_type': u'http://example.onto/Country',
                       u'_id': u'http://example.onto/Brazil',
                       u'_score': 1.0,
                       u'_source': {
                           u'http://www.w3.org/2000/01/rdf-schema#label': u'Brazil'
                       },
                   }],
                   u'total': 1,
                   u'max_score': 1.0
               }}
           )
    @patch("brainiak.search.search._build_items",
           return_value=[
               {
                   "id": "http://example.onto/Brazil",
                   "title": u"Brazil"
               }]
           )
    @patch("brainiak.search.search._build_json", return_value={"fake_response": {}})
    def test_do_search(self, mock_build_json, mock_build_items, mock_do_search_query, mock_get_search_fields):
        query_params = {
            "class_uri": "http://example.onto/Country",
            "graph_uri": "http://example.onto/",
            "pattern": "bra"
        }
        expected = {"fake_response": {}}
        result = do_search(query_params)
        self.assertTrue(all([
            mock_build_json.called,
            mock_build_items.called,
            mock_do_search_query.called,
            mock_get_search_fields.called
        ]))
        self.assertEqual(expected, result)

    @patch("brainiak.search.search._get_search_fields", return_value=["label"])
    @patch("brainiak.search.search.do_search_query",
           return_value={
               u'hits': {
                   u'hits': [],
                   u'total': 0,
                   u'max_score': None
               }}
           )
    @patch("brainiak.search.search._build_json",
           return_value={"fake_response": {}, "items": []})
    def test_do_search_with_zero_items(self, mock_build_json, mock_do_search_query, mock_get_search_fields):
        query_params = {
            "class_uri": "http://example.onto/Country",
            "graph_uri": "http://example.onto/",
            "pattern": "bra"
        }
        expected = {"fake_response": {}, "items": []}
        result = do_search(query_params)
        self.assertTrue(all([
            mock_build_json.called,
            mock_do_search_query.called,
            mock_get_search_fields.called
        ]))
        self.assertEqual(expected, result)

    @patch("brainiak.search.search.uri_to_slug", return_value="example.onto")
    @patch("brainiak.search.search.run_search")
    def test_do_search_query(self, mock_run_search, mock_uri_to_slug):
        search_fields = ["http://www.w3.org/2000/01/rdf-schema#label"]
        query_params = {
            "graph_uri": "http://example.onto/",
            "class_uri": "http://example.onto/City",
            "pattern": "Yo",  # dawg
        }
        expected_query = {
            "filter": {
                "type": {
                    "value": "http://example.onto/City"
                }
            },
            "query": {
                "multi_match": {
                    "fields": ["http://www.w3.org/2000/01/rdf-schema#label"],
                    "query": "Yo",
                    "analyzer": settings.ES_ANALYZER,
                    "fuzziness": 0.7
                }
            },
            "from": 0,
            "size": 10
        }

        do_search_query(query_params, search_fields)
        mock_run_search.assert_called_with(expected_query, indexes=["semantica.example.onto"])

    def test_build_items(self):
        expected_items = [
            {
                "id": "http://example.onto/Brazil",
                "title": u"Brazil"
            }
        ]
        elasticsearch_result = {
            u'hits': {
                u'hits': [{
                    u'_index': u'example.onto',
                    u'_type': u'http://example.onto/Country',
                    u'_id': u'http://example.onto/Brazil',
                    u'_score': 1.0,
                    u'_source': {
                        u'http://www.w3.org/2000/01/rdf-schema#label': u'Brazil'
                    },
                }],
                u'total': 1,
                u'max_score': 1.0
            },
        }
        items = _build_items(elasticsearch_result)
        self.assertEqual(expected_items, items)

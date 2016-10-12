# coding: utf-8
import unittest

from scrapy.http import Request

from ..spiders.hsi import HSISpider
from .utils import fake_response_from_file as fakeit


class HSITest(unittest.TestCase):
    def setUp(self):
        self.spider = HSISpider()

    def test_parse(self):
        results = list(
            self.spider.parse(fakeit("responses/tournament_list.html")))
        self.assertEquals(len(results), 93)
        for item in results:
            self.assertIsInstance(item, Request)

    def test_parse_tournament(self):
        results = list(
            self.spider.parse_tournament(fakeit("responses/tournament.html")))
        self.assertEquals(len(results), 84)
        for item in results:
            self.assertIsInstance(item, Request)

    def test_parse_game(self):
        results = list(self.spider.parse_game(fakeit("responses/game.html")))
        self.assertEquals(len(results), 1)

        for item in results:
            self.assertIsInstance(item, dict)

# coding: utf-8
import unittest

from scrapy.http import Request

from ..spiders.hsi import HSISpider
from .utils import fake_response_from_file as fakeit, json_fixture


class HSITest(unittest.TestCase):
    maxDiff = None

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

        item = results[0]
        self.assertIsInstance(item, dict)

        # assert that the player objects look right
        self.assertEquals(item["home"]["name"], u"ÍH")
        self.assertItemsEqual(item["home"]["roster"],
                              json_fixture("ih-throttur-home-roster.json"))

        self.assertEquals(item["away"]["name"], u"Þróttur")
        self.assertItemsEqual(item["away"]["roster"],
                              json_fixture("ih-throttur-away-roster.json"))

    def test_parse_old_style(self):
        results = list(self.spider.parse_game(fakeit(
            "responses/selfoss-vikingur-1994.html",
            "http://hsi.is/motamal/0800000002_00030004.htm")))

        self.assertEquals(len(results), 1)

    def test_parse_match_with_missing_team(self):
        results = list(self.spider.parse_game(fakeit(
            "responses/selfoss-stjarnan-1994-missing-team.html",
            "http://hsi.is/motamal/0800000002_00150004.htm")))

        self.assertEquals(len(results), 1)
        match = results[0]
        self.assertEquals(match["home"]["name"], u"Selfoss")
        self.assertItemsEqual(match["home"]["roster"], [])

    def test_parse_player_with_missing_column(self):
        """
        The total ("samtals") row for KR in this match has an extra ">" after
        one of the <td> tags which messes up the XPath parser's ability to
        parse the file correctly. It reads as 9 children but should be 10 and
        modern browsers interpret it as 10.

        In this case it's the total row which we just drop anyway but it might
        be important in some other case where this could let us ignore an
        existing field and mess everything up in some player's statistics.

        For now we're not going to worry about that but in the future adding
        some kind of sanity check to find out if the "total" row and all the
        other rows match up.
        """
        results = list(self.spider.parse_game(fakeit(
            "responses/kr-throttur-missing-column.html",
            "http://hsi.is/motamal/0800002285_00190002.htm")))

        self.assertEquals(len(results), 1)
        match = results[0]

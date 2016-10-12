# coding: utf8
import locale
import logging
import threading

import scrapy

from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


LOCALE_LOCK = threading.Lock()
PLAYER_STATUS = {
    u"markverðir": "goalkeeper",
    u"útileikmenn": "outfield",
    u"starfsmenn": "official",
}


@contextmanager
def use_locale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


def _text(el):
    text = el.xpath("text()").extract_first()
    if text:
        return text.strip()
    logger.warn(u"{0} has no text node.".format(el))
    return ""


def _parse_date(date_string):
    """
    Accepts the datetime string representation used on the HSÍ result pages
    and returns a datetime with the machine readable datetime or the string
    if we weren't able to parse it.

    HSÍ splits the datetime into date and time fields. The date field looks
    approximately like:

        Mán. 30.mar.2015

    And the time field is just HH.MM like

        19.30

    This method receives these strings concatenated, separated by a single
    space.

    If parsing doesn't work either we return the string as that's better than
    nothing.
    """
    fixed_date_string = date_string.lower().encode('utf-8')
    with use_locale("is_IS.UTF-8"):
        try:
            return datetime.strptime(fixed_date_string, "%a. %d.%b.%Y %H.%M")
        except ValueError, e:
            logger.warn(e)
    return date_string


class HSISpider(scrapy.Spider):
    """
    Scrape all match data from hsi.is
    """
    name = "hsi-scraper"
    allowed_domains = ["hsi.is"]
    start_urls = [
        "http://hsi.is/motamal/",
    ]

    def parse(self, response):
        """
        Parse the response and find all the tournaments that we can parse as
        well as other years with more tournaments we can parse.

        Params:
            response (scrapy.http.Response): the response to parse
        """
        year_match = response.xpath(
            "//td[contains(@class, 'haus')]/text()").re_first(
                r"Handknattleikur\s+-\s+(\d+)")
        if year_match:
            year = int(year_match)

            season_selector = response.xpath(
                u"//td[text() = '{0}']/parent::tr/parent::table/tr/td/a".format(
                        u"\xd6nnur t\xedmabil"))
            other_seasons = [
                (
                    int(sel.xpath("text()").extract_first().strip()),
                    sel.xpath("@href").extract_first(),
                ) for sel in season_selector]

            tournament_selector = response.xpath(
                "//td[text() = 'Konur' or text() = 'Karlar']/parent::tr/parent::table/tr/td/a")
            tournaments = [
                (
                    sel.xpath("text()").extract_first().strip(),
                    sel.xpath("@href").extract_first(),
                ) for sel in tournament_selector]

            for y, url in other_seasons:
                yield scrapy.Request(response.urljoin(url))

            for title, url in tournaments:
                yield scrapy.Request(
                    response.urljoin(url),
                    callback=self.parse_tournament,
                    meta={
                        'year': year,
                        'title': title,
                        'url': response.urljoin(url),
                    })

    def parse_tournament(self, response):
        title_selector = response.xpath("//a[@class = 'timabil']")
        title = _text(title_selector.xpath("parent::td"))
        year = int(_text(title_selector))

        game_rows = response.xpath(
            "//th[text() = 'Dagur']/../following-sibling::tr[count(td) = 6]")
        for game_selector in game_rows:
            date, time, venue, teams, ft_el, ht_el = game_selector.xpath("td")
            venue_name = _text(venue)
            full_time = _text(ft_el)
            half_time = _text(ht_el)

            parsed_date = _parse_date(" ".join((_text(date), _text(time))))

            game_details_selector = teams.xpath("a")
            if game_details_selector:
                game_url = response.urljoin(
                    game_details_selector.xpath("@href").extract_first())
                game_teams = _text(game_details_selector)
            else:
                game_url = None
                game_teams = _text(teams)

            home, away = self._find_teams(game_teams, response)

            game_data = {
                "tournament": title,
                "year": year,
                "datetime": parsed_date,
                "venue": venue_name,
                "home": home,
                "away": away,
                "full-time": full_time,
                "half-time": half_time,
                "url": game_url,
            }

            if game_url:
                yield scrapy.Request(
                    game_url,
                    callback=self.parse_game,
                    meta=game_data)
            else:
                yield game_data

    def parse_game(self, response):
        """
        Parse the single game page that contains the rosters for both teams and
        the players performance.
        """
        meta = [
            (key.strip(), value.strip()) for key, value in [
                meta_str.split(":") for meta_str in response.xpath(
                    u"//p[contains(., 'Áhorfendur')]/*/text()").extract()]]

        team_tags = response.xpath("//td[@class = 'haus']/a")
        teams = []
        for team in team_tags:
            team_name = _text(team)
            rows = team.xpath("ancestor::tr/following-sibling::tr")
            header = []
            team_roster = []
            for row in rows:
                if row.xpath("th"):
                    fields = [s.strip() for s in row.xpath(
                        "th/text()").extract()]

                    player_type = fields[1]
                    header = ["number", "name"] + fields[2:]
                else:
                    player = dict(filter(
                        # remove "fields" where there is neither key nor value
                        lambda t: t[0].replace("&nbsp", ""),
                        zip(header, [s.strip() for s in row.xpath(
                            "td/text()").extract()])))
                    player["status"] = PLAYER_STATUS[player_type.lower()]

                    # special case for the "total number of goals/penalties"
                    if player.get("name", "") != "Samtals":
                        team_roster.append(player)

            teams.append({
                "name": team_name,
                "roster": team_roster
            })

        yield dict(response.meta, meta=meta, home=teams[0], away=teams[1])

    def _find_teams(self, game_teams, response):
        """
        Extract team names from "[home team] - [away team]". Keep in mind that
        some teams might have a hyphen in their name. Also handle the case
        where either the home team or away team is missing (e.g.
        "- [away team]" or "[home team] -")
        """
        teams = [team.strip() for team in game_teams.split(" - ")]
        if len(teams) == 2:
            return teams

        if game_teams[0] == "-":
            return "", game_teams[1:].strip()
        if game_teams[-1] == "-":
            return game_teams[:-1].strip(), ""

        logger.warn(
            u"Couldn't extract home/away teams from game description \"{0}\" at {1}".format(
                game_teams, response.url))
        return "", ""

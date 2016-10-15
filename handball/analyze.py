# coding: utf-8
from itertools import chain, ifilter, imap


def player_in_match(name):
    _name = name.lower()

    def get_lowercase_name(player):
        return player.get("name", "").lower()

    def wrapped(match):
        if hasattr(match["home"], "get"):
            home_roster = imap(get_lowercase_name, match["home"]["roster"])
            away_roster = imap(get_lowercase_name, match["away"]["roster"])
            if _name in home_roster or _name in away_roster:
                return True
        return False

    return wrapped


def match_in_season(year):
    def wrapped(match):
        return match["year"] == year
    return wrapped


def match_in_tournament(tournament_name):
    tournament = tournament_name.lower()

    def wrapped(match):
        return match["tournament"].lower() == tournament
    return wrapped


def count_goals(name, matches):
    _name = name.lower()

    def find_goals(match):
        if hasattr(match["home"], "get"):
            return sum(imap(lambda player: player.get("attempts", {}).get("goals", 1), ifilter(
                    lambda x: x.get("name", "").lower() == _name,
                    chain(match["home"]["roster"], match["away"]["roster"]))))

        return 0

    return sum(imap(find_goals, matches))


def count_appearances(name, matches):
    return len(filter(player_in_match(name), data))


if __name__ == "__main__":
    import code
    import json
    import sys
    data = json.load(open(sys.argv[1], "r"))

    code.interact("Play around with the data. It's in the `data` variable",
                  local=locals())

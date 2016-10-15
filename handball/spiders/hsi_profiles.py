# coding: utf-8
import logging

from ..utils import ignore_exception, just

logger = logging.getLogger(__name__)
try_int = ignore_exception(ValueError, default=0)(int)


class UnknownPlayerType(Exception):
    pass


def get_player_parser(header):
    """
    Get a function that parses the data tuple into a common format based on the
    table header that preceeds the player line.
    """
    try:
        return filter(lambda x: x[0] == header, PLAYER_PROFILES)[0][1]
    except IndexError:
        raise UnknownPlayerType("Unknown player profile {0}".format(header))


def parse_goalkeeper((num, name, goals, _, yellow, susp, red, s6m, s9m, s7m)):
    """
    """
    return {
        "type": "goalkeeper",
        "name": name,
        "number": num,
        "saves": {
            "9m": try_int(s9m),
            "6m": try_int(s6m),
            "7m": try_int(s7m),
        },
        "penalties": {
            "yellow": yellow == "G",
            "suspensions": try_int(susp),
            "red": red == "R",
        },
        "attempts": {
            "goals": try_int(goals),
            "saved": 0,
            "missed": 0,
        }
    }


def parse_outfielder(data):
    num, name, shots, _, yellow, susp, red, skr, tb, rud, _ = just(11, data)
    if shots:
        goals, saved, missed, _ = just(4, (try_int(n) for n in shots.split("/")))
    else:
        goals, saved, missed = (0, 0, 0)
    return {
        "type": "outfielder",
        "name": name,
        "number": num,
        "penalties": {
            "yellow": yellow == "G",
            "suspensions": try_int(susp),
            "red": red == "R",
        },
        "attempts": {
            "goals": goals,
            "saved": saved,
            "missed": missed,
        }
    }


def parse_basic(player_type):
    def parser(data):
        return {
            "type": player_type,
            "name": data[1],
        }
    return parser


def parse_old_style(player_type):
    backup_parser = parse_basic(player_type)

    def parser(data):
        (num, name, goals, yellow, susp, red, extra) = just(7, data)
        if red == "1":
            logger.info("Weird value for 'R': '1' - {0}".format(data))

        player_data = {
            "type": player_type,
            "name": name,
            "number": num,
            "penalties": {
                "yellow": yellow == "G",
                "suspensions": try_int(susp),
                "red": red == "R",
            },
            "attempts": {
                "goals": try_int(goals),
                "saved": 0,
                "missed": 0,
            }
        }
        if player_type == "goalkeeper":
            player_data["saves"] = {
                "9m": 0,
                "6m": 0,
                "7m": 0,
            }
        return player_data
    return parser


PLAYER_PROFILES = (
    ((
        u'',
        u'Markver\xf0ir',
        u'M',
        u'',
        u'G',
        u'2m',
        u'R',
        u'6m M/V',
        u'9m M/V',
        u'V\xedti M/V'
    ), parse_goalkeeper),

    ((
        u'',
        u'\xdatileikmenn',
        u'Skot  M/V/F',
        u'%',
        u'G',
        u'2m',
        u'R',
        u'Skr',
        u'TB',
        u'Ru\xf0'
    ), parse_outfielder),

    ((u'', u'Starfsmenn', u''), parse_basic("official")),

    ((u'', u'Markver\xf0ir', u'M', u'G', u'2m', u'R'),
        parse_old_style("goalkeeper")),
    ((u'', u'\xdatileikmenn', u'M', u'G', u'2m', u'R'),
        parse_old_style("outfielder")),
)

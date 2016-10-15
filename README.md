A Scrapy spider that downloads all data available about handball mathces in
Iceland from the local handball federation website (hsi.is)

Just a fun little project to try out Scrapy and experiment with XPath but could
also allow me to generate some interesting statistics.

## Scraping data

To run the spider run the following command from the project directory

    scrapy crawl -o output.json -t json --logfile=logfile.log hsi-scraper

The data will be stored in the *output.json* file (or whatever is specified in
the command) and is a list of all matches played (that could be scraped). Each
match has the following attributes:

* **tournament** - the tournament this match belongs to
* **year** - the tournament year
* **round** - which round of the tournament this match belongs to
* **datetime** - the start time of the match
* **home** - the name of the home team
* **away** - the name of the away team
* **half-time** - the score at half time
* **full-time** - the final score
* **teams** - the team rosters for both teams, includes scored goals and penalties

The **teams** attribute is a list (always home team first and then away team) with
an object that has the following attributes:

* **name** - the team name
* **roster** - a list of players and team officials

The **roster** is a list of *player objects* that each have the following attributes:

* **name** - the player name
* **number** - the squad number of the player
* **type** - the type of player ("goalkeeper", "outfielder", "official")
* **attempts** - an object with a count of scored goals/missed and saved shots
 * **goals** - number of goals scored (if available)
 * **saved** - number of shots that were saved by the goalkeeper
 * **missed** - number of shots that missed the goal
* **penalties** - an object with the penalties the player received in the match
 * **yellow** - did the player receive the yellow card penalty
 * **suspensions** - number of suspensions received
 * **red** - did the player receive the red card penalty
* **saves** - an object with number of saves, only for players of type "goalkeeper"
 * **9m** - shots saved from 9m or more
 * **6m** - shots saved from 6m-9m
 * **7m** - penalties saved (from the 7m line)


## Using the scraped data

There are some tools for counting appearances and goals for players by name.

Example:

    $ python -m handball.analyze output.json
    Play around with the data. It's in the `data` variable
    >>> count_appearances(u"Halldór Rúnarsson", data)
    149
    >>> count_goals(u"Halldór Rúnarsson", data)
    3

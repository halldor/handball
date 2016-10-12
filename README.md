A Scrapy spider that downloads all data available about handball mathces in
Iceland from the local handball federation website (hsi.is)

Just a fun little project to try out Scrapy and experiment with XPath but could
also allow me to generate some interesting statistics.

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
* **goals** - number of goals scored (if available)
* **yellow** - did the player receive the yellow card penalty
* **suspensions** - number of suspensions received
* **red** - did the player receive the red card penalty

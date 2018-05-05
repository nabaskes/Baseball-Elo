##############################
#
# parse data from a retrosheet into database
# All data from the nice folks at retrosheet.org, hit them up
# for a wicked impressive collection of compiled historical
# baseball data
#
###############################
import sqlite3


def parse_file(file_name):
    with open(file_name) as f:
        games = f.read().split("\n")
        for game in games:
            fields = game.split(",")
            day = fields[0].replace('"', '')
            day = day[:4]+"-"+day[4:-2]+"-"+day[-2:]
            visit_team = fields[3].replace('"', '')
            home_team = fields[6].replace('"', '')
            visit_score = fields[9].replace('"', '')
            home_score = fields[10].replace('"', '')
            year = day[:4]
            yield({
                'day': day,
                'visit_team': visit_team,
                'home_team': home_team,
                'visit_score': visit_score,
                'home_score': home_score,
                'year': year})


if __name__ == "__main__":
    db = sqlite3.connect('games.db')
    cursor = db.cursor()
    filenames = ['retrosheets/GL'+str(i)+'.TXT' for i in range(2017, 2018)]
    for filename in filenames:
        print(filename)
        try:
            for game in parse_file(filename):
                print(game)
                cursor.execute("""INSERT INTO games
                (Host, Visitor, Year, HostScore, VisitorScore, Day)
                VALUES ('{home_team}', '{visit_team}',
                '{year}', '{home_score}', '{visit_score}', '{day}');""".format(**game))
        except IndexError:
            db.commit()

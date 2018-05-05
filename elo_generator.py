import sqlite3

db = sqlite3.connect('games.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()
ELO_CONSTANT = 128


def populate_preseason_elo(year):
    cursor.execute(f"""SELECT Distinct Visitor
    from games
    WHERE Year='{year}'
    UNION Select Distinct Host as Visitor
    From games
    WHERE Year='{year}'""")
    visitors = cursor.fetchall()

    for visitor in visitors:
        cursor.execute(f"""INSERT INTO Team
        (Name, Year, Elo) VALUES ('{visitor['Visitor']}', '{year}', 1000)""")
    db.commit()


def calculate_elo(host_elo, away_elo, host_points, away_points):
    e_host = 10**(host_elo/400)
    e_away = 10**(away_elo/400)
    host_won = 1 if host_points > away_points else 0

    new_host_elo = host_elo + ELO_CONSTANT*(host_won - e_host/(e_host+e_away))
    new_away_elo = away_elo + ELO_CONSTANT*((1 - host_won) - e_away/(e_host+e_away))
    return round(new_host_elo, 0), round(new_away_elo, 0)


def generate_elo(year):
    print(year)
    populate_preseason_elo(year)
    cursor.execute(f"""SELECT Host, Visitor, HostScore, VisitorScore, Day
    FROM games
    WHERE Year='{year}'
    ORDER BY Day ASC""")
    games = cursor.fetchall()

    for game in games:

        cursor.execute(f"""SELECT Elo FROM Team
        WHERE Year='{year}' AND Name='{game['Visitor']}'""")
        visitor_elo = cursor.fetchone()['Elo']

        cursor.execute(f"""SELECT Elo FROM Team
        WHERE Year='{year}' AND Name='{game['Host']}'""")
        host_elo = cursor.fetchone()['Elo']

        cursor.execute(f"""UPDATE games
        SET HostElo='{host_elo}', VisitorElo='{visitor_elo}'
        WHERE Host='{game['Host']}'
        AND Visitor='{game['Visitor']}'
        AND Day='{game['Day']}'
        AND HostScore='{game['HostScore']}'
        AND VisitorScore='{game['VisitorScore']}'""")

        new_host_elo, new_away_elo = calculate_elo(host_elo,
                                                   visitor_elo,
                                                   game['HostScore'],
                                                   game['VisitorScore'])

        cursor.execute(f"""UPDATE Team
        SET Elo='{new_host_elo}'
        WHERE Name='{game['Host']}'
        AND Year='{year}'""")

        cursor.execute(f"""UPDATE Team
        SET Elo='{new_away_elo}'
        WHERE Name='{game['Visitor']}'
        AND Year='{year}'""")

    db.commit()

    cursor.execute(f"SELECT Name, Elo FROM Team where Year='{year}';")
    res = cursor.fetchall()
    for row in res:
        print(row['Name'])
        print(row['Elo'])


def gen_historical_elos():
    for year in range(1871, 2018):
        generate_elo(year)


if __name__ == "__main__":
    gen_historical_elos()

from requests_html import HTMLSession
from datetime import date, datetime
import sqlite3
from elo_generator import calculate_elo


db = sqlite3.connect("games.db")
sess = HTMLSession()
urlprefix = "https://www.baseball-reference.com/boxes/?date="


def get_game_scores(day, month, year):
    resp = sess.get(urlprefix+str(year)+"-"+str(month)+"-"+str(day))
    tables = resp.html.find(".teams")
    for table in tables:
        yield(list(filter(lambda x: x != 'Final', table.text.split("\n")))[:4])


def insert_game(game, day, month, year, cursor):
    host, hostscore, away, awayscore = tuple(game)
    cursor.execute(f"""SELECT Elo FROM Team
    WHERE Year='{year}' AND Name='{host}';""")
    host_elo = cursor.fetchone()[0]
    cursor.execute(f"""SELECT Elo from Team
    WHERE Year='{year}' AND Name='{away}'""")
    away_elo = cursor.fetchone()[0]
    cursor.execute(f"""INSERT INTO games
    (Host, Visitor, Year, HostScore, VisitorScore, HostElo, VisitorElo, Day)
    VALUES ('{host}', '{away}', '{year}', '{hostscore}', '{awayscore}',
    '{hostelo}', '{awayelo}', '{str(year)+'-'+str(month)+'-'+str(day)});""")


    host_elo, away_elo = calculate_elo(host_elo, away_elo, hostscore, awayscore)

    cursor.execute(f"""UPDATE Team
    SET Elo = CASE WHEN Name='{host}' THEN host_elo ELSE away_elo END
    WHERE Name in ('{host}', '{away}')
    AND Year='{year}'""")


def finish_doing_season():
    c = db.cursor()
    year = 2018
    months = [3, 4, 5]
    days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
            17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
    for month in months:
        for day in days:
            try:
                for game in get_game_scores(day, month, year):
                    insert_game(game, day, month, year, c)
                    print(game)
            except Exception as e:
                print(e)
    db.commit()



if __name__ == "__main__":
    day, month, year = date.today().day, date.today().month, date.today().year
    games = get_game_scores(day, month, year)

    for game in games:
        insert_game(game, day, month, year)
    db.commit()

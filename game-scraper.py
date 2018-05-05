import calendar
from requests_html import HTMLSession

sess = HTMLSession()
url_pre = 'https://www.baseball-reference.com/leagues/MLB/'


def parse_year(year_string):
    _, month_day, year = tuple(year_string.split(","))
    day = month_day[-2:].strip()
    year = year.strip()
    month = month_day[:-2].strip()
    month = str(list(calendar.month_name).index(month))
    return ''.join((year, "-", month, "-", day))


def scrape_games(year):
    r = sess.get(url_pre+str(year)+"-schedule.shtml")
    tags = r.html.find('div, h3')

    for tag in tags:
        try:
            cur_day = parse_year(tag.text)
            if not (len(cur_day) <= 10):
                raise ValueError("not a date field")
            day = cur_day
            print(day)
            continue
        except ValueError:
            pass
        try:
            game = tag.text.split("\n")
            if "Boxscore" not in game[1]:
                raise ValueError("not a game field")
            print(game)
        except ValueError:
            pass
        except IndexError:
            pass


def scrape_all_years():
    return [game for game in scrape_games(year) for year in range(1900, 2018)]


if __name__ == "__main__":
    scrape_games('1911')

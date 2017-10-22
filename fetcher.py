import sys
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import date
import re
import calendar

ADDRESS = 'http://data.typeracer.com/pit/race_history'

def create_races_table(conn):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS races')
    cursor.execute('''CREATE TABLE races
                        (no integer, speed integer, accuracy real, points text,
                        place text, date integer)''')
    conn.commit()

def get_race_no(td):
    return td.a.string

def get_speed(td):
    return td.string.split(' ')[0]

def get_accuracy(td):
    return td.string.strip()[:-1]

def get_points(td):
    return td.string.strip()

def get_place(td):
    return td.string.strip()

def get_date_object(text):
    if (text == 'today'):
        return date.today()

    tokens = re.split('\W+', text)
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug',
                'Sept', 'Oct', 'Nov', 'Dec']
    year = int(tokens[2])
    month = months.index(tokens[0]) + 1
    day = int(tokens[1])
    return date(year, month, day)

# Assumin the dates are in UTC timezone
def get_date(td):
    text = td.string.strip()
    d = get_date_object(text)
    return calendar.timegm(d.timetuple())

def insert_data_from_trs(trs, conn):
    races = []
    # The first row holds the column names
    for tr in trs[1:]:
        tds = tr.find_all('td')
        values = (get_race_no(tds[0]), get_speed(tds[1]), get_accuracy(tds[2]),
                get_points(tds[3]), get_place(tds[4]), get_date(tds[5]))
        races.append(values)

    c = conn.cursor()
    c.executemany('INSERT INTO races VALUES (?,?,?,?,?,?)', races)
    conn.commit()

def fetch_parse_page(url, conn):
    r = requests.get(url)
    c = r.content

    soup = BeautifulSoup(c, 'html.parser')
    scoresTable = soup.find('table', class_='scoresTable')
    if scoresTable is None:
        print('Could not find table in html page')
    else:
        trs = scoresTable.find_all('tr')
        insert_data_from_trs(trs, conn)

    next_url = None
    next_url_tag = soup.find('a', href=True,
            string=re.compile('load older results'))
    if next_url_tag is not None:
        next_url = ADDRESS + next_url_tag['href']

    return next_url

def fetch_user_data(username):
    conn = sqlite3.connect('typeracer.db')
    initial_url = ADDRESS + '?user=' + username

    create_races_table(conn)
    url = initial_url
    while url is not None:
        url = fetch_parse_page(url, conn)
    conn.close()

if __name__ == '__main__':
    username = sys.argv[1]
    fetch_user_data(username)

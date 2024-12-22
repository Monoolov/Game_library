import requests
from bs4 import BeautifulSoup
import sqlite3
import json


def create_database():
    data_base = sqlite3.connect('../../Downloads/Telegram Desktop/q/qq/build/sourse/Games.db')
    sql = data_base.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS games 
    (title text NOT NULL PRIMARY KEY, 
        year int, 
        genre text,
        developer text,
        publisher text,
        platform text,
        criticscore float,
        userscore float,
        poster text,
        verifed text)""")
    data_base.commit()


def download_titles_and_links():
    with open('../../Downloads/Telegram Desktop/q/qq/build/sourse/html/games.json') as file:
        games = json.load(file)

    headers = {
        "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42"
    }

    url = 'https://kritikanstvo.ru/top/games/best/alltime/start/'

    for i in range(0, 1001, 10):

        current_url = url + str(i) + '/'
        print(current_url)

        responce = requests.get(current_url, headers=headers)
        soup = BeautifulSoup(responce.text, 'lxml')

        best_games_1 = soup.find_all("li", class_="row_a site_rating_good clearfix")
        best_games_2 = soup.find_all("li", class_="row_c site_rating_good clearfix")

        best_games = []

        for j in range(len(best_games_1)):
            best_games.append(best_games_1[j])
            best_games.append(best_games_2[j])

        for game in best_games:
            headline = game.find_all('h2')[0]
            title = headline.text
            lnk = headline.find('a').get('href')
            games[title] = lnk
    with open('../../Downloads/Telegram Desktop/q/qq/build/sourse/html/games.json', 'w') as file:
        json.dump(games, file)


def parse_game(title, link):
    game_url = 'https://kritikanstvo.ru' + link
    game_info = {}



    headers = {
        "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42"
    }
    responce = requests.get(game_url, headers=headers)
    soup = BeautifulSoup(responce.text, 'lxml')

    if title == '':
        title = soup.find('div', class_='page_item_title').find('h1').findAll('span')[1].text
        print(title)

    # получение ссылки на фото
    try:
        poster_link = "https://kritikanstvo.ru" + soup.find('a', class_='gallery_common').get('href')
    except AttributeError:
        poster_link = 'FALSE'

    # получение инфы об игре
    try:
        info = soup.find_all('div', class_='page_item_info')[0].text.split('выхода')[1]
    except IndexError:
        info = soup.find_all('div', class_='page_item_info')[0].text
    try:
        dates = info.split('Разработчик')[0].split('года')[:-1]
        developer = info.split('Разработчик')[1].split('Издатель')[0].strip().strip('\n')
        try:
            publisher = info.split('Разработчик')[1].split('Издатель')[1].strip().strip('\n')
        except IndexError:
            publisher = developer

    except IndexError:
        try:
            dates = info.split('Издатель')[0].split('года')[:-1]
            publisher = info.split('Издатель')[1].strip().strip('\n')
            developer = publisher
        except IndexError:
            publisher = developer = '-'

    # получение рейтинг
    try:
        critic_score = soup.find('div', class_='page_item_foreign_rating foreign_rating_good').find('h4').text
        user_score = soup.find('div', class_='page_item_users_rating users_rating_good').find('h4').text
    except AttributeError:
        score = soup.find('div', class_='page_item_site_rating site_rating_good').find('h4').text
        critic_score = user_score = score

    # получение жанра и консолей
    headline = soup.find_all('div', class_='page_item_title')[0]

    # консоли
    consols = headline.find_all('a', class_='item_tag item_tag_platform')
    consols = [i.text for i in consols]

    # жанр
    try:
        genre = headline.find_all('a', class_='item_tag item_tag_genre')
        genre = [i.text for i in genre]
    except AttributeError and IndexError:
        genre = '-'

    game_info['consols'] = consols
    game_info['genre'] = genre
    game_info['critic_score'] = critic_score
    game_info['user_score'] = user_score
    game_info['dates'] = dates
    game_info['developer'] = developer
    game_info['publisher'] = publisher
    game_info['title'] = title
    game_info['poster_link'] = poster_link

    return game_info


def download_all_games_info():
    with open('../../Downloads/Telegram Desktop/q/qq/build/sourse/html/games.json') as file:
        games = json.load(file)
    data_base = sqlite3.connect('../../Downloads/Telegram Desktop/q/qq/build/sourse/Games.db')
    sql = data_base.cursor()

    for title in games.keys():
        game_info = parse_game(title, games[title])
        sql.execute("""INSERT INTO games VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        game_info['title'],
                        '|'.join(game_info['dates']),
                        '|'.join(game_info['genre']),
                        game_info['developer'],
                        game_info['publisher'],
                        '|'.join(game_info['consols']),
                        game_info['critic_score'],
                        game_info['user_score'],
                        game_info['poster_link'],
                        'TRUE'
                    ))
        data_base.commit()
    data_base.close()


def first_build():
    create_database()
    download_titles_and_links()
    download_all_games_info()
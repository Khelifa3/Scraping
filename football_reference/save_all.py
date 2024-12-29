import logging
from curl_cffi import requests
import time
from bs4 import BeautifulSoup, Comment
import os


logging.basicConfig(
    filename=f"logs_{int(time.time())}.log",
    format="%(asctime)s - %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s",
    filemode="w",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


scraper = requests.Session(impersonate="chrome")
no_block_sleep = 2  # site limit 20 requests/minute


def elementOrDefault(list, index):
    "Return list[index] or '' if index out of range"
    return list[index] if index < len(list) else ""


def makeRequest(url):
    try:
        response = scraper.get(url)
        time.sleep(no_block_sleep)  # sleep 3sec to avoid getting blocked
        if response.status_code == 200:
            return response
        elif response.status_code == 429:  # too many requests
            logger.error(f"{response.status_code}, {url}")
            ban_time = int(response.headers["Retry-After"])
            logger.error(f"Sleeping for {ban_time} seconds...")
            time.sleep(ban_time)
            return makeRequest(url)
        elif response.status_code == 502:  # bad gateway
            logger.error(f"{response.status_code}, {url}")
            return makeRequest(url)
        else:
            logger.info(f"{response.status_code}, {url}")
    except Exception as e:  # network error
        logger.error(f"{e}, {url}")
        time.sleep(10)  # sleep 10 seconds before retry
        return makeRequest(url)
    return response


def saveProgress(game):
    with open("progress.txt", "w") as f:
        f.write(f"{game}")


def loadProgress():
    try:
        with open("progress.txt", "r") as f:
            index_td_game, index_td = f.read().split(" ")
            logger.info(f"Starting scraping from {index_td_game} {index_td}")
            return [int(index_td_game), int(index_td)]
    except:
        logger.info("No save found, starting from scratch")
        return [0, 0]


def getGame(url):
    response = makeRequest(url)
    game_n = url.split("/")[-1]
    path_save = f"./save/{game_n}"
    with open(path_save, "w", encoding="utf-8") as file:
        file.write(response.text)


def getAllLinks():
    # Get all games grouped by score
    url = "https://www.pro-football-reference.com/boxscores/game-scores.htm"
    base_url = "https://www.pro-football-reference.com"
    response = makeRequest(url)
    soup = BeautifulSoup(response.text, "html.parser")
    tds_all_games = soup.find_all("td", {"data-stat": "all_games"})
    time_start = time.time()
    index_td_game, index_td = loadProgress()
    path = "./save/"
    files = os.listdir(path)
    # For each group score get all games
    for td_game in tds_all_games[index_td_game:]:
        link = td_game.find("a")["href"]
        full_link = base_url + link
        response = makeRequest(full_link)
        soup_game = BeautifulSoup(response.text, "html.parser")
        tds = soup_game.find_all("td", {"data-stat": "boxscore_word"})
        # Get game details
        for td in tds[index_td:]:
            link = td.find("a")["href"]  # ex: /boxscores/194711090chi.htm
            file_link = link.replace("/boxscores/", "")
            if file_link in files:
                continue

            full_link = base_url + link
            try:
                getGame(full_link)
            except Exception as e:  # some games with almost no data or bad formatig
                logger.error(f"{e} {full_link}")
            saveProgress(f"{tds_all_games.index(td_game)} {tds.index(td)}")

        index_td = 0  # reset game index if loaded from save
    # Reset progress
    saveProgress(f"0 0")
    time_taken = time.time() - time_start
    logger.info(f"Time taken: {time_taken}")


if __name__ == "__main__":
    try:
        getAllLinks()
    except Exception as e:
        logger.error(f"{e}")

import logging
import time
from bs4 import BeautifulSoup, Comment
import re
import traceback
import os

import parseTable
import process_excel

logging.basicConfig(
    filename=f"logs_{int(time.time())}.log",
    format="%(asctime)s - %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s",
    filemode="w",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


file_name = "nfl_full2.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)


def elementOrDefault(list, index):
    "Return list[index] or '' if index out of range"
    return list[index] if index < len(list) else ""


def getGame(soup, url):
    # Team names
    try:
        div_scorebox = soup.find("div", "scorebox")
        team_names = [
            strong for strong in div_scorebox.find_all("strong") if strong.find("a")
        ]

        team_1_name = team_names[0].text.strip()
        team_2_name = team_names[1].text.strip()
    except Exception as e:
        logger.error(traceback.format_exc())
    # Records
    try:
        scores = div_scorebox.find_all("div", "scores")
        records_team_1 = scores[0].find_next_sibling().text.strip()
        team_1_win, team_1_loss, *team_1_tie = records_team_1.split("-")
        team_1_tie = team_1_tie[0] if team_1_tie else ""
        records_team_2 = scores[1].find_next_sibling().text.strip()
        team_2_win, team_2_loss, *team_2_tie = records_team_2.split("-")
        team_2_tie = team_2_tie[0] if team_2_tie else ""
    except Exception as e:
        logger.error(traceback.format_exc())
    # Coachs
    teams_divs = div_scorebox.find_all("div", recursive=False)
    div_team_1 = teams_divs[0]
    div_team_2 = teams_divs[1]
    try:
        team_1_coach = div_team_1.find("div", "datapoint")
        if team_1_coach:
            team_1_coach = team_1_coach.find("a").text.strip()
    except:
        logger.error(traceback.format_exc())
    try:
        team_2_coach = div_team_2.find("div", "datapoint")
        if team_2_coach:
            team_2_coach = team_2_coach.find("a").text.strip()
    except Exception as e:
        logger.error(traceback.format_exc())
    # Date, stadium
    try:
        div_meta = soup.find("div", "scorebox_meta")
        date = div_meta.find("div").text.strip()
        day_name, month, day, year = date.split(" ")
        day = day.replace(",", "")
        strongs = div_meta.find_all("strong")
        for strong in strongs:
            if "Start Time" in strong.text:
                start_time = (
                    strong.find_parent().text.strip().replace("Start Time: ", "")
                )
        stadium_a = div_meta.find("a")
        if stadium_a:
            stadium = stadium_a.text.strip()
    except Exception as e:
        logger.error(traceback.format_exc())
    # Scores
    score_tab = soup.find("table", "linescore").find_all("tr")
    score_header = score_tab[1].find_all("th")[2:]
    team_1_scores = score_tab[1].find_all("td")[2:]
    team_2_scores = score_tab[2].find_all("td")[2:]
    team_1_final_score = team_1_scores[-1].text.strip()
    team_2_final_score = team_2_scores[-1].text.strip()
    team_1_scores = [score.text.strip() for score in team_1_scores[:-1]]
    team_2_scores = [score.text.strip() for score in team_2_scores[:-1]]
    # Weather, vegas line, over/under
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        try:
            commentsoup = BeautifulSoup(comment, "html.parser")
            game_info_tab = commentsoup.find("table", id="game_info")
            if game_info_tab:
                trs = game_info_tab.find_all("tr")
                temp, humidity, wind = "", "", ""
                vegas_team, vegas_number = "", ""
                over_under_number, over_under = "", ""
                for tr in trs[1:]:  # skip header
                    th = tr.find("th").text.strip()
                    td = tr.find("td").text.strip()
                    if "Weather" in th:
                        weather = td.split(",")
                        for w in weather:
                            if "degrees" in w:
                                temp = re.sub("[^0-9]", "", w)
                            elif "humidity" in w:
                                humidity = re.sub("[^0-9]", "", w)
                            elif "mph" in w:
                                wind = re.sub("[^0-9]", "", w)
                            elif "chill" in w:
                                chill = re.sub("[^0-9]", "", w)
                    elif th == "Vegas Line":
                        try:
                            vegas_team, vegas_number = td.rsplit(" ", 1)
                        except:
                            vegas_team, vegas_number = "", 0
                    elif th == "Over/Under":
                        over_under_number, over_under = td.split(" ")
                        over_under = over_under.replace("(", "").replace(")", "")

        except Exception as e:
            logger.error(traceback.format_exc())

    team_1_passing = []
    team_2_passing = []
    team_1_rushing = []
    team_2_rushing = []
    team_1_receiving = []
    team_2_receiving = []
    passing_rushing_receiving = parseTable.getStats(soup)
    if passing_rushing_receiving:
        team_1_passing = passing_rushing_receiving[0]
        team_2_passing = passing_rushing_receiving[1]
        team_1_rushing = passing_rushing_receiving[2]
        team_2_rushing = passing_rushing_receiving[3]
        team_1_receiving = passing_rushing_receiving[4]
        team_2_receiving = passing_rushing_receiving[5]

    row_data = [
        locals().get("team_1_name", ""),
        locals().get("team_2_name", ""),
        locals().get("team_1_win", ""),
        locals().get("team_1_loss", ""),
        locals().get("team_1_tie", ""),
        locals().get("team_2_win", ""),
        locals().get("team_2_loss", ""),
        locals().get("team_2_tie", ""),
        locals().get("team_1_coach", ""),
        locals().get("team_2_coach", ""),
        locals().get("day_name", ""),
        locals().get("month", ""),
        locals().get("day", ""),
        locals().get("year", ""),
        locals().get("start_time", ""),
        locals().get("stadium", ""),
        elementOrDefault(team_1_scores, 0),
        elementOrDefault(team_2_scores, 0),
        elementOrDefault(team_1_scores, 1),
        elementOrDefault(team_2_scores, 1),
        elementOrDefault(team_1_scores, 2),
        elementOrDefault(team_2_scores, 2),
        elementOrDefault(team_1_scores, 3),
        elementOrDefault(team_2_scores, 3),
        elementOrDefault(team_1_scores, 4),
        elementOrDefault(team_2_scores, 4),
        elementOrDefault(team_1_scores, 5),
        elementOrDefault(team_2_scores, 5),
        locals().get("team_1_final_score", ""),
        locals().get("team_2_final_score", ""),
        locals().get("temp", ""),
        locals().get("humidity", ""),
        locals().get("wind", ""),
        locals().get("vegas_team", ""),
        locals().get("vegas_number", ""),
        locals().get("over_under", ""),
        locals().get("over_under_number", ""),
        elementOrDefault(team_1_passing, 0),
        elementOrDefault(team_1_passing, 1),
        elementOrDefault(team_1_passing, 2),
        elementOrDefault(team_1_passing, 3),
        elementOrDefault(team_1_passing, 4),
        elementOrDefault(team_2_passing, 0),
        elementOrDefault(team_2_passing, 1),
        elementOrDefault(team_2_passing, 2),
        elementOrDefault(team_2_passing, 3),
        elementOrDefault(team_2_passing, 4),
        elementOrDefault(team_1_rushing, 0),
        elementOrDefault(team_1_rushing, 1),
        elementOrDefault(team_1_rushing, 2),
        elementOrDefault(team_1_rushing, 3),
        elementOrDefault(team_2_rushing, 0),
        elementOrDefault(team_2_rushing, 1),
        elementOrDefault(team_2_rushing, 2),
        elementOrDefault(team_2_rushing, 3),
        elementOrDefault(team_1_receiving, 0),
        elementOrDefault(team_1_receiving, 1),
        elementOrDefault(team_1_receiving, 2),
        elementOrDefault(team_1_receiving, 3),
        elementOrDefault(team_1_receiving, 4),
        elementOrDefault(team_2_receiving, 0),
        elementOrDefault(team_2_receiving, 1),
        elementOrDefault(team_2_receiving, 2),
        elementOrDefault(team_2_receiving, 3),
        elementOrDefault(team_2_receiving, 4),
        url,
    ]
    try:
        sheet_obj.append(row_data)
    except Exception as e:
        logger.error(traceback.format_exc())


def getAllLinks():
    # Get all games grouped by score
    time_start = time.time()
    path = "./save/"
    files = os.listdir(path)
    files.reverse()  # from newest to oldest game
    base_url = "https://www.pro-football-reference.com/boxscores/"

    # For each group score get all games
    for file in files:
        html_file = path + file
        with open(html_file, "r") as f:
            html_content = f.read()
        url = base_url + file
        soup = BeautifulSoup(html_content, "html.parser")
        # Get game details
        try:
            getGame(soup, url)
        except Exception as e:  # some games with almost no data or bad formatig
            logger.error(traceback.format_exc())

    # Reset progress
    time_taken = time.time() - time_start
    logger.info(f"Time taken: {time_taken}")


if __name__ == "__main__":
    try:
        getAllLinks()
    except Exception as e:
        logger.error(traceback.format_exc())
    process_excel.close(wb_obj, file_name)

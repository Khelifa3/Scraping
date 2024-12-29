from curl_cffi import requests
import time
from bs4 import BeautifulSoup, Comment
import json

scraper = requests.Session(impersonate="chrome")


def makeRequest(url):
    try:
        response = scraper.get(url)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:  # too many requests
            ban_time = int(response.headers["Retry-After"])
            time.sleep(ban_time)
            return makeRequest(url)
        elif response.status_code == 502:  # bad gateway
            return makeRequest(url)

    except Exception as e:  # network error
        time.sleep(10)  # sleep 10 seconds before retry
        return makeRequest(url)
    return response


def getTeams():
    url = "https://www.pro-football-reference.com/teams/"
    response = makeRequest(url)
    soup = BeautifulSoup(response.text, "html.parser")
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    links = [a for a in soup.find_all("a") if a["href"].startswith("/teams/")]
    print(len(links))
    list_teams = []
    for th in links:
        try:
            team_name = th.text.strip()
            link = th["href"]
            acronym = link.split("/")[-2]
            list_teams.append([team_name, acronym.upper()])
        except:
            print(th)
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        commentsoup = BeautifulSoup(comment, "html.parser")
        links = [
            a for a in commentsoup.find_all("a") if a["href"].startswith("/teams/")
        ]
        for th in links:
            try:
                team_name = th.text.strip()
                link = th["href"]
                acronym = link.split("/")[-2]
                list_teams.append([team_name, acronym.upper()])
            except:
                print(th)

    return list_teams


teams = getTeams()
with open("teams_acronyms.json", "w") as f:
    json.dump(teams, f)

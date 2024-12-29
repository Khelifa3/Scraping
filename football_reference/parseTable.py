from collections import defaultdict
import json

with open("teams.json", "r") as f:
    teams = json.load(f)


def sort_list_of_lists(data, i1, i2):
    # Custom sort key to handle empty strings and sort by the 2 indices
    def custom_sort_key(lst):
        # Replace empty strings with a placeholder value for comparison
        return (
            lst[i1] if lst[i1] != "" else float("-inf"),  # Sort by index i1
            lst[i2] if lst[i2] != "" else float("-inf"),  # Tie-breaker: index i2
        )

    # Sort the list of lists
    sorted_data = sorted(data, key=custom_sort_key)
    return sorted_data


def parseTable(soup):

    # Team names
    try:
        div_scorebox = soup.find("div", "scorebox")
        team_names = div_scorebox.find_all("strong")
        team_1_name = team_names[0].text.strip()
        team_2_name = team_names[2].text.strip()
    except Exception as e:
        pass
        # logger.error(f"{e} {url}")
    # table
    table = soup.find("table", {"id": "player_offense"})
    if table == None:
        return None
    # Extract headers
    headers = [
        th["data-stat"]
        for th in table.find("thead").find_all("th")
        if "data-stat" in th.attrs
    ]

    # Extract rows
    rows = [{"team_1": team_1_name, "team_2": team_2_name}]
    for tr in table.find("tbody").find_all("tr"):
        row = defaultdict(int)
        for th in tr.find_all("th"):
            row[th["data-stat"]] = th.get_text()
        for td in tr.find_all("td"):
            try:
                row[td["data-stat"]] = int(td.get_text())
            except:
                row[td["data-stat"]] = td.get_text()
        rows.append(row)

    return rows


def getStats(soup):
    rows = parseTable(soup)
    if rows == None:
        return None
    team_1 = rows[0]["team_1"]
    team_2 = rows[0]["team_2"]
    team_1_passing = []
    team_2_passing = []
    team_1_rushing = []
    team_2_rushing = []
    team_1_reveiving = []
    team_2_reveiving = []
    for row in rows:
        if "player" not in row or row["player"] == "Player":  # headers
            continue
        team_abr = row["team"]
        team = ""
        for t in teams:
            if t[1] == team_abr and t[0] in [team_1, team_2]:
                team = t[0]
        if team == "":
            print(f"Team not registred {team_abr} {[team_1, team_2]}")

        if team == team_1:
            team_1_passing.append(
                [
                    row["player"],
                    row["pass_cmp"],
                    row["pass_att"],
                    row["pass_yds"],
                    row["pass_sacked"],
                ],
            )
            team_1_rushing.append(
                [row["player"], row["rush_att"], row["rush_yds"], row["rush_td"]]
            )
            team_1_reveiving.append(
                [
                    row["player"],
                    row["targets"],
                    row["rec"],
                    row["rec_yds"],
                    row["rec_td"],
                ]
            )

        else:
            team_2_passing.append(
                [
                    row["player"],
                    row["pass_cmp"],
                    row["pass_att"],
                    row["pass_yds"],
                    row["pass_sacked"],
                ]
            )
            team_2_rushing.append(
                [row["player"], row["rush_att"], row["rush_yds"], row["rush_td"]]
            )
            team_2_reveiving.append(
                [
                    row["player"],
                    row["targets"],
                    row["rec"],
                    row["rec_yds"],
                    row["rec_td"],
                ]
            )

        team_1_rushing = sort_list_of_lists(team_1_rushing, 2, 3)
        team_1_reveiving = sort_list_of_lists(team_1_reveiving, 3, 2)
        team_2_rushing = sort_list_of_lists(team_2_rushing, 2, 3)
        team_2_reveiving = sort_list_of_lists(team_2_reveiving, 3, 2)

    return [
        team_1_passing[0] if len(team_1_passing) else [],
        team_2_passing[0] if len(team_2_passing) else [],
        team_1_rushing[-1] if len(team_1_rushing) else [],
        team_2_rushing[-1] if len(team_2_rushing) else [],
        team_1_reveiving[-1] if len(team_1_reveiving) else [],
        team_2_reveiving[-1] if len(team_2_reveiving) else [],
    ]

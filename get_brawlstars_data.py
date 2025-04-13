import pandas as pd
import logging
import requests
import json
from urllib.parse import quote
from tabulate import tabulate
from mysql_utils import connect_to_mysql, load_into_mysql
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

api_key = os.getenv("BRAWLSTARS_API_KEY")
base_url = "https://api.brawlstars.com/"
api_version = "v1"

headers = {"Authorization": f"Bearer {api_key}"}


def get_battle_logs(player_tag, api_key):
    path = f"{api_version}/players/{quote(player_tag)}/battlelog"
    endpoint = base_url + path
    logging.info(endpoint)
    res = requests.get(url=endpoint, headers=headers)
    res.raise_for_status()
    logging.info(res.status_code)
    res_json = json.dumps(res.json(), indent=5)
    logging.info(res_json)


def get_player_status(player_tag, api_key):
    path = f"{api_version}/players/{quote(player_tag)}"
    endpoint = base_url + path
    logging.info(endpoint)
    res = requests.get(url=endpoint, headers=headers)
    logging.info(res.status_code)
    res_json = json.dumps(res.json(), indent=5)
    logging.info(res_json)


def get_players_ranking(country_code):
    path = f"{api_version}/rankings/{country_code}/players"
    endpoint = base_url + path
    logging.info(endpoint)
    res = requests.get(endpoint, headers=headers)
    res.raise_for_status()
    logging.info(res.content)
    res_json = json.dumps(res.json(), indent=5)
    logging.info(res_json)

    return res_json, country_code


def players_ranking_to_df(all_players_json, country_code):
    all_players = json.loads(all_players_json).get("items")
    player_data_list = []
    player_data_schema = ["player_tag", "player_name", "player_rank", "player_club"]
    for player in all_players:
        player_tag = player.get("tag")
        logging.debug(f"player_tag: {player_tag}")
        player_name = player.get("name")
        logging.debug(f"player_name: {player_name}")
        player_rank = player.get("rank")
        logging.debug(f"player_rank: {player_rank}")
        player_club = player.get("club", {}).get("name")
        logging.debug(f"player_club: {player_club}")

        player_data_list.append(
            {
                "player_tag": player_tag,
                "player_name": player_name,
                "player_rank": player_rank,
                "player_club": player_club,
            }
        )

    player_data_df = pd.DataFrame(
        player_data_list, columns=player_data_schema, dtype=object
    )
    player_data_df["country"] = country_code
    logging.info(tabulate(player_data_df, headers="keys", tablefmt="psql"))
    return player_data_df


def main():
    data, country_code = get_players_ranking("global")
    df = players_ranking_to_df(data, country_code)
    conn = connect_to_mysql()
    load_into_mysql(
        df,
        conn,
        table_name="player_data",
    )


if __name__ == '__main__':
    main()

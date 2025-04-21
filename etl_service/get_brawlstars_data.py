import pandas as pd
import logging
import requests
import json
from urllib.parse import quote
from tabulate import tabulate
from mysql_utils import connect_to_mysql, load_into_mysql
from dotenv import load_dotenv
import os
import time
import subprocess
import yaml

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

api_key = os.getenv("BRAWLSTARS_API_KEY")
base_url = "https://api.brawlstars.com/"
api_version = "v1"
mysql_pw = os.getenv("MYSQL_PASSWORD")
mysql_host = os.getenv("MYSQL_HOST", "mysql")

headers = {"Authorization": f"Bearer {api_key}"}


def wait_for_mysql(
    host=mysql_host,
    port=3306,
    user="root",
    password=mysql_pw,
    max_retries=5,
    delay_seconds=5,
):
    retries = 0
    while retries < max_retries:
        try:
            # MySQL admin command to check if MySQL is ready
            command = [
                "mysqladmin",
                "-h",
                host,
                "-P",
                str(port),
                "-u",
                user,
                "-p" + str(password),
                "ping",
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            if "mysqld is alive" in result.stdout:
                logging.info("Successfully connected to MySQL!")
                return True
        except subprocess.CalledProcessError as e:
            logging.info(f"Error connecting to MySQL: {e}")
            retries += 1
            logging.info(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay_seconds)
    logging.info("Max retries reached. Exiting.")
    return False


def read_etl_config(config_filepath):
    try:
        with open(config_filepath, "r") as file:
            config = yaml.safe_load(file)
            logging.info(config)
            return config

    except Exception as err:
        logging.exception(f"An error occured: {err}, traceback:")
        return None


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
    logging.debug(res.content)
    res_json = json.dumps(res.json(), indent=5)
    logging.debug(res_json)

    return res_json, country_code


def players_ranking_to_df(all_players_json, country_code):
    try:
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
        logging.info(f"Retrieved data for {country_code}")
        return player_data_df

    except Exception as err:
        logging.exception(f"An error occured: {err}, traceback:")


def main():
    logging.info("Starting etl job")
    logging.info("Checking mysql status")
    wait_for_mysql()
    etl_config = read_etl_config("config.yml")
    country_codes = etl_config["country_codes"]
    for country_code in country_codes:
        data, etl_country_code = get_players_ranking(country_code)
        df = players_ranking_to_df(data, etl_country_code)
        conn = connect_to_mysql()
        load_into_mysql(
            df,
            conn,
            table_name="player_data",
        )
    logging.info("Ending etl job")


if __name__ == "__main__":
    main()

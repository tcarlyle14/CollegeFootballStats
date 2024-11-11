import cfbd
import pandas as pd
from matplotlib import pyplot as plt
import flatdict
import time

pd.set_option('display.max_columns', None)  # Do not truncate columns
plt.style.use('ggplot')
# personal key needed for API access
# receive your own key here: https://collegefootballdata.com/key
CFBD_API_KEY = '1m02g7gvMjVYEtY4Gx1qboEvXRB7KLhIA8CNA7nvgBrrCJFs0GT+pSRl4Ys3QnIv'

config = cfbd.Configuration()
config.api_key['Authorization'] = CFBD_API_KEY
config.api_key_prefix['Authorization'] = 'Bearer'
# API Configs. See https://github.com/CFBD/cfbd-python?tab=readme-ov-file for more
stat_api = cfbd.StatsApi(cfbd.ApiClient(config))
team_api = cfbd.TeamsApi(cfbd.ApiClient(config))

def generate_teams_df(year=2024):
    teams = team_api.get_fbs_teams(year=year)
    team_df_data = dict()

    for team in teams:
        team_dict = team.to_dict()
        flattened_team_dict = flatdict.FlatDict(team_dict, delimiter='.')

        for k, v in flattened_team_dict.items():
            if k not in team_df_data:
                team_df_data[k] = []
            team_df_data[k].append(v)

    return pd.DataFrame(team_df_data)

def validate_team():
    # Read the team name from the text file
    # Polling loop to check if team name is written to the file
    team_name = ""
    while not team_name:
        try:
            with open("team_input.txt", "r") as file:
                team_name = file.read().strip().lower()  # Read the team name
        except FileNotFoundError:
            # If the file doesn't exist yet, keep waiting
            time.sleep(1)

    time.sleep(2)

    # Clear the file content (empty the file before writing validation result)
    with open("team_input.txt", "w") as file:
        file.write("")  # Clear the file contents

    teams_df = generate_teams_df()

    is_valid = team_name.lower() in teams_df['school'].str.lower().values

    with open("team_input.txt", "w") as file:
        file.write("true" if is_valid else "false")

if __name__ == "__main__":
    validate_team()
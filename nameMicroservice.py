import time
import pandas as pd
import cfbd
import flatdict

# Assuming you have the proper CFBD_API_KEY and configurations set up
CFBD_API_KEY = '1m02g7gvMjVYEtY4Gx1qboEvXRB7KLhIA8CNA7nvgBrrCJFs0GT+pSRl4Ys3QnIv'

config = cfbd.Configuration()
config.api_key['Authorization'] = CFBD_API_KEY
config.api_key_prefix['Authorization'] = 'Bearer'
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

def write_team_name_to_file(team_name):
    """Write the team name to the text file."""
    with open("team_input.txt", "w") as file:
        file.write(team_name)

def validate_team():
    """Validate team and update the file accordingly."""
    # Wait until the team name is written to the file
    team_name = ""
    while not team_name:
        try:
            with open("team_input.txt", "r") as file:
                team_name = file.read().strip().lower()
        except FileNotFoundError:
            # If the file doesn't exist yet, wait a bit
            print("Waiting for team name input...")
            time.sleep(1)

    print(f"Team name read: {team_name}")

    # Ensure a small delay before clearing the file (simulating microservice processing time)
    time.sleep(2)

    # Clear the file content before writing the validation result
    with open("team_input.txt", "w") as file:
        file.write("")  # Clear the file contents

    # Get the list of teams from the API
    teams_df = generate_teams_df()
    print(f"Validating team against list of {len(teams_df)} teams...")

    # Check if the team is valid
    is_valid = team_name in teams_df['school'].str.lower().values
    print(f"Is the team valid? {'Yes' if is_valid else 'No'}")

    # Write the result ('true' or 'false') to the file
    with open("team_input.txt", "w") as file:
        file.write("true" if is_valid else "false")
    print(f"Validation result written: {'true' if is_valid else 'false'}")

if __name__ == "__main__":
    validate_team()
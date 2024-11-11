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


def generate_advanced_team_game_stats_df(team, year=2024):
    """get advanced stats from website, explosiveness, havoc rates etc."""
    games = stat_api.get_advanced_team_season_stats(team=team, year=year)
    games_df_data = dict()

    for game in games:
        game_dict = game.to_dict()
        flattened_game_dict = flatdict.FlatDict(game_dict, delimiter='.')

        for k, v in flattened_game_dict.items():
            if k not in games_df_data:
                games_df_data[k] = []
            games_df_data[k].append(v)

    return pd.DataFrame(games_df_data)


def generate_team_stats(team, year=2024):
    """get basic stats for the season, pass yards, total yards etc."""
    team_stats = stat_api.get_team_season_stats(team=team, year=year)
    stats_df_data = dict()

    for stat in team_stats:
        stat_dict = stat.to_dict()
        flat_stat_dict = flatdict.FlatDict(stat_dict, delimiter='.')

        for k, v in flat_stat_dict.items():
            if k not in stats_df_data:
                stats_df_data[k] = []
            stats_df_data[k].append(v)

    return pd.DataFrame(stats_df_data)


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


def write_team_to_file(team_name):
    """Write the team name to a text file."""
    with open("team_input.txt", "w") as file:
        file.write(team_name)

def read_validation_result():
    """Read the validation result (True/False) from the text file."""
    with open("team_input.txt", "r") as file:
        result = file.read().strip().lower()  # Convert to lowercase to handle any case
    if result == 'true':
        return True
    else:
        return False

def is_valid_team(team_name):
    """Check if the team is valid by calling the microservice."""
    # Write the team input to a text file
    write_team_to_file(team_name)
    
    # Sleep for a moment to allow the microservice to process the validation
    time.sleep(7)
    
    is_valid = read_validation_result()

    with open("team_input.txt", "w") as file:
        file.write("")

    # Read the validation result from the text file
    return is_valid

def get_team_input(teams_df):
    while True:
        team_name = input("Enter an FBS college football team name: ")
        if is_valid_team(team_name):
            return team_name
        else:
            print(f"'{team_name}' is not a valid team name. Please try again.")


def format_column_name(column_name):
    mapping = {
        'offense.passing_downs.explosiveness': 'Offense Passing Explosiveness:',
        'offense.rushing_plays.explosiveness': 'Offense Rushing Explosiveness:',
        'defense.havoc.total': 'Defense Havoc Percentage:',
        'defense.passing_downs.explosiveness': 'Defense Passing Explosiveness:',
        'defense.rushing_plays.explosiveness': 'Defense Rushing Explosiveness:',
        'offense.havoc.total': 'Offense Havoc Percentage:'
    }
    return mapping.get(column_name)


def display_stats(option, team_name):
    if option == '1':
        # Generate DataFrame for basic team stats
        team_df = generate_team_stats(team_name)  # Refetch data each time
        stat_order = ['Total Yards', 'Passing Yards', 'Passing Touchdowns', 'Rushing Yards', 'Rushing Touchdowns',
                      'Defensive Interceptions', 'Defensive Sacks']
        cond_stats = team_df.copy()
        cond_stats['stat_name'] = cond_stats['stat_name'].replace({
            'totalYards': 'Total Yards',
            'netPassingYards': 'Passing Yards',
            'passingTDs': 'Passing Touchdowns',
            'rushingYards': 'Rushing Yards',
            'rushingTDs': 'Rushing Touchdowns',
            'passesIntercepted': 'Defensive Interceptions',
            'sacks': 'Defensive Sacks'
        })
        cond_stats = cond_stats[cond_stats['stat_name'].isin(stat_order)]
        cond_stats['stat_name'] = pd.Categorical(cond_stats['stat_name'], categories=stat_order, ordered=True)
        cond_stats = cond_stats.sort_values('stat_name')
        cond_stats = cond_stats.rename(columns={'stat_name': 'Statistic', 'stat_value': 'Value'})

        for _, row in cond_stats[['Statistic', 'Value']].iterrows():
            print(f"{row['Statistic']:<30}{row['Value']}")
            print()
    elif option == '2':
        # Generate DataFrame for advanced team stats
        team_advanced_df = generate_advanced_team_game_stats_df(team_name)  # Refetch data each time
        for column in ['offense.havoc.total', 'offense.passing_downs.explosiveness',
                       'offense.rushing_plays.explosiveness', 'defense.havoc.total',
                       'defense.passing_downs.explosiveness', 'defense.rushing_plays.explosiveness']:
            if column in team_advanced_df.columns:
                formatted_column_name = format_column_name(column)
                if formatted_column_name:
                    value = team_advanced_df[column].iloc[0]
                    if 'offense.havoc' in column:
                        value = f"{value * 100:.2f}% of {team_name}'s offensive downs resulted in the opposing " \
                                f"defense making a big play on them."

                    elif 'defense.havoc' in column:
                        value = f"{value * 100:.2f}% of {team_name}'s defensive downs resulted in them making " \
                                f"a big play on the opposing offense"
                    else:
                        value = f"{value:.3f} average expected points per successful offensive play"
                    print(f"{formatted_column_name:<35}{value}\n")


def main():
    print("\nHello, welcome to college football live stat tracker for the 2024 season.\n")
    print("\nThis program loads a selection of the latest team statistics for any FBS college football team.\n")
    print("\nPLEASE NOTE: You will need a personal API key in order to access the online data.")

    print("You can receive one here:https://collegefootballdata.com/key\n")
    print("Paste the key in the 'CFBD_API_KEY' variable at the top of the code.\n")

    print("Choose an option:")
    print("1. Get standard team stats for the 2024 season.")
    print("2. Get advanced team stats for the 2024 season.\n")

    while True:
        option = input("Enter the number of your choice: ")
        if option in ['1', '2']:
            break
        else:
            print("Invalid option. Please enter '1' or '2'.")

    teams_df = generate_teams_df()
    team_name = get_team_input(teams_df)

    display_stats(option, team_name)

    # Track if both stats options have been exhausted
    viewed_options = {option}

    while True:
        if len(viewed_options) < 2:
            choice = input(
                "\nWould you like to see the other stats option?\nType '1' for yes, '2' to return to the main menu, "
                "or '3' to end the program: ")
            if choice == '1':
                # Determine which option hasn't been viewed yet
                other_option = '2' if option == '1' else '1'
                display_stats(other_option, team_name)
                viewed_options.add(other_option)
            elif choice == '2':
                main()
                return
            elif choice == '3':
                print("Exiting the program. Goodbye!")
                exit()
            else:
                print("Invalid choice. Please enter '1', '2', or '3'.")
        else:
            choice = input("\nTo return to main type '2', type '3' to end the program: ")
            if choice == '2':
                main()
                return
            elif choice == '3':
                print("Exiting the program. Goodbye!")
                exit()
            else:
                print("Invalid choice. Please enter '2' or '3'.")


if __name__ == "__main__":
    main()

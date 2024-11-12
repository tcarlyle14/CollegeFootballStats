import time

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

def get_team_input():
    while True:
        team_name = input("Enter an FBS college football team name: ")
        if is_valid_team(team_name):
            return team_name
        else:
            print(f"'{team_name}' is not a valid team name. Please try again.")

def main():
    team_name = get_team_input()

if __name__ == "__main__":
    main()

import pandas as pd

def refactor_excel_from_file(excel_file_path, output_file_path="refactored_data.xlsx"):
    """Refactors the Excel data from a file into two columns: Name and Project Name,
    and saves the result to a new Excel file.

    Args:
        excel_file_path: The path to the input Excel file. Can be .xlsx or .csv.
        output_file_path: The path to save the refactored data to. Defaults to "refactored_data.xlsx".

    Returns:
        True if the refactoring and saving were successful, False otherwise.
    """
    try:
        df = pd.read_excel(excel_file_path) if excel_file_path.endswith((".xlsx", ".xls")) else pd.read_csv(excel_file_path)

    except FileNotFoundError:
        print(f"Error: File not found at path: {excel_file_path}")
        return False
    except Exception as e:
        print(f"Error reading the file: {e}")  # More informative error message
        return False

    # Create an empty list to store the refactored data
    refactored_data = []

    # Iterate over each row of the DataFrame
    for index, row in df.iterrows():
        project_name = row['Project Name']
        team_leader = row['Team Leader']
        teams = row['Teams']

        # Add the team leader to the refactored data
        refactored_data.append({'Name': team_leader, 'Project Name': project_name})

        # Split the teams string into a list of team members
        if isinstance(teams, str):  # Check if teams is not NaN
            team_members = teams.split(',')

            # Add each team member to the refactored data
            for member in team_members:
                refactored_data.append({'Name': member, 'Project Name': project_name})

    # Create a new DataFrame from the refactored data
    refactored_df = pd.DataFrame(refactored_data)

    try:
        refactored_df.to_excel(output_file_path, index=False)
        print(f"Refactored data saved to: {output_file_path}")
        return True
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        return False

# Example Usage:
input_file = "participants.xlsx"  # Replace with your input file path
output_file = "refactored_data.xlsx"  # Optional:  Specify a different output file
success = refactor_excel_from_file(input_file, output_file)  # Use the optional output path

if success:
    print("Refactoring and saving completed successfully.")
else:
    print("Refactoring or saving failed. Check error messages.")
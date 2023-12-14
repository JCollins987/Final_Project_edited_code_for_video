# Jefferson Collins
# 12/6/23
# main.py

# import statements
from app.function import create_main_window, create_listbox, add_schools, add_athletes, add_races, create_race_details_for_athletes, connect_races_to_athletes, display_schools_and_athletes
from app.function import get_race_titles, display_top_25, display_school_points
import tkinter as tk # for creating the graphical interface
import sqlite3 # for database operations
import os # for working with file path

# define the main function
def main():
    # Calls the create_main_window function to create the main Tkinter window (root).
    root = create_main_window()

    # Calls the create_listbox function to create a Tkinter Listbox for displaying races.
    listbox = create_listbox(root)

    # Add buttons to the main window
    # Creates Tkinter Button widgets for various actions.
    # Associates each button with a specific command (function) to execute when clicked.

    # click this button first, upload race.csv
    add_schools_button = tk.Button(root, text="Add Schools", command=add_schools)
    add_schools_button.pack(side=tk.LEFT, padx=10) # button placement

    # click this button second and third, upload boys.csv and girls.csv
    add_athletes_button = tk.Button(root, text="Add Athletes", command=add_athletes)
    add_athletes_button.pack(side=tk.LEFT, padx=10) # button placement

    # click this button fourth, upload race.csv
    add_races_button = tk.Button(root, text="Add Races", command=add_races)
    add_races_button.pack(side=tk.LEFT, padx=10) # button placement

    # button to get race_detail_id and athlete_id in the race_detail table
    # click the button after
    create_race_details_button = tk.Button(root, text="Create Race Details", command=create_race_details_for_athletes)
    create_race_details_button.pack(side=tk.LEFT, padx=10) # button placement

    # button to get race_id for every athlete_id and race_detail_id in the race_detail_table
    # (use race.csv)
    connect_races_button = tk.Button(root, text="Connect Races to Athletes", command=connect_races_to_athletes)
    connect_races_button.pack(side=tk.LEFT, padx=10) # button placement



    # <<<<<<<<<<<<<< edit below here for specific results >>>>>>>>>>>>>
    # Set a default value for the race dropdown
    race_titles = add_races()  # Fetch race titles

    # Create a StringVar to store the selected race
    selected_race_var = tk.StringVar(root)
    selected_race_var.set(race_titles[0])  # Set the default value

    # Create a dropdown menu for selecting the race
    race_dropdown = tk.OptionMenu(root, selected_race_var, *race_titles)
    race_dropdown.pack(side=tk.LEFT, padx=10)

    # top 25 button
    top_25_button = tk.Button(root, text="Top 25", command=lambda: display_top_25(listbox, selected_race_var.get()))
    top_25_button.pack(side=tk.LEFT, padx=10)

    # Create a button for School Points Breakdown
    school_points_button = tk.Button(root, text="School Points", command=lambda: display_school_points(listbox, selected_race_var.get()))
    school_points_button.pack(side=tk.LEFT, padx=10)

    # Add the "Display Schools and Athletes" button with the updated command
    display_schools_button_with_race = tk.Button(root, text="All Info", command=lambda: display_schools_and_athletes(listbox, selected_race_var.get()))
    display_schools_button_with_race.pack(side=tk.LEFT, padx=10)

    # <<<<<<<<<<<<<<<<<<<< ensure connection to database   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # Assuming you have defined the database_path variable
    database_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Python class", "athlete_race.db")

    # Create a database connection
    conn = sqlite3.connect(database_path)

    # Create a cursor from the connection
    cursor = conn.cursor()


    # Run the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
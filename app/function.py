# app/function.py
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import csv
import sqlite3
import os
from operator import itemgetter


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<< creates the gui >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def display_instructions(listbox):
    try:
        # Clear the listbox
        listbox.delete(0, tk.END)

        # Instructions for uploading data
        listbox.insert(tk.END, "Upload Data to athlete_race.db Instructions:")
        listbox.insert(tk.END, "")
        listbox.insert(tk.END, "insert Races.csv file when you run program")
        listbox.insert(tk.END, "1. Click 'Add Schools' button, select 'race.csv' file that contains headers.")
        listbox.insert(tk.END, "2. Click 'Add Athletes' button, select 'boys.csv' file, and type 'male' in the popup window.")
        listbox.insert(tk.END, "3. Click 'Add Athletes' button, select 'girls.csv' file, and type 'female' in the popup window.")
        listbox.insert(tk.END, "4. Click 'Create Race Details' button.")
        listbox.insert(tk.END, "5. Click 'Connect Races to Athletes' button, select 'race.csv' file.")
        listbox.insert(tk.END, "")

        # Instructions for querying data
        listbox.insert(tk.END, "Query Data Inside Database on GUI Instructions:")
        listbox.insert(tk.END, "")
        listbox.insert(tk.END, "1. Select a certain race from the dropdown, e.g., 'DIV 4 CHAMPIONSHIP RACE' or 'CLUB CHAMPIONSHIPS RACE'.")
        listbox.insert(tk.END, "2. Select 'Top 25' to see the top 25 male and female runners for the selected race.")
        listbox.insert(tk.END, "3. Select 'School Points' button to see a school points breakdown for the selected race.")
        listbox.insert(tk.END, "4. Select 'All Info' button to see all athletes' info grouped by gender for the selected race.")

        # Set a larger font size
        listbox.config(font=("Helvetica", 12))

    except Exception as e:
        print(f"Exception during display instructions: {e}")

def create_main_window():
    # Function to create the main window and return the root
    root = tk.Tk()
    root.title("Middle School XC State Finals")
    root.geometry("1050x750")

    # Make the title larger and bold
    title_label = tk.Label(root, text="Middle School XC State Finals", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=20)

    return root

def create_listbox(root):
    # Function to create and return the Listbox for displaying races
    races_listbox = tk.Listbox(root)
    races_listbox.pack(pady=10, fill=tk.BOTH, expand=True)  # Make the Listbox fill both width and height

    # Create a button for displaying instructions
    instructions_button = tk.Button(root, text="Click here for Instructions", command=lambda: display_instructions(races_listbox))
    instructions_button.pack()

    # Add event binding to clear the listbox when any other button is clicked
    def clear_listbox(event):
        races_listbox.delete(0, tk.END)

    root.bind("<Button-1>", clear_listbox)

    return races_listbox

# <<<<<<<<<<<<<<<< adding in the race.csv file to upload data to the school table >>>>>>>>>>>>>>>
def add_schools():
    print("Adding Schools")
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])

    if file_path:
        try:
            update_database_from_csv(file_path)
            print("Schools added successfully.")
        except Exception as e:
            print(f"Error adding schools: {e}")

def update_database_from_csv(file_path):
    try:
        database_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Python class", "athlete_race.db")
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(schools)")
        print("Database Schema:")
        print(cursor.fetchall())

        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)

            for row in csv_reader:
                school_name = row[0].strip()  # Strip whitespaces from the school name

                # Check if the school already exists in the database
                cursor.execute("SELECT school_id FROM schools WHERE school_name = ?", (school_name,))
                existing_school = cursor.fetchone()

                if existing_school:
                    print(f"School '{school_name}' already exists in the database.")
                else:
                    # Insert the school into the schools table
                    cursor.execute("INSERT INTO schools (school_name) VALUES (?)", (school_name,))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Exception during database update: {e}")
        raise e


# <<<<<<<<<<<<<<<<< adding boys.csv and girls.csv to database to create athletes table >>>>>>>>>>.
def add_athletes():
    print("Adding Athletes")

    # Reset the processed_athletes set for each button click
    processed_athletes = set()

    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])

    if file_path:
        try:
            gender = ask_gender()
            update_database_with_athletes(file_path, gender, processed_athletes)
            print("Athletes added successfully.")
        except Exception as e:
            print(f"Error adding athletes: {e}")

def ask_gender():
    gender = simpledialog.askstring("Gender", "Enter gender (male or female):")
    return gender.lower() if gender else None


def update_database_with_athletes(file_path, gender, processed_athletes):
    try:
        database_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Python class", "athlete_race.db")
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')

            # Skip the header row
            next(csv_reader, None)

            for row in csv_reader:
                if len(row) >= 4:
                    last_name, first_name, school_name, time = [value.strip() for value in row[:4]]

                    # Check for Whitespaces
                    school_name = school_name.strip()

                    # Case Sensitivity
                    cursor.execute("SELECT school_id FROM schools WHERE LOWER(school_name) = LOWER(?)",
                                   (school_name,))
                    result = cursor.fetchone()

                    # Check if the school exists in the database
                    if result is not None:
                        school_id = result[0]

                        # Insert the athlete into the athletes table
                        cursor.execute(
                            "INSERT INTO athletes (first_name, last_name, school_id, gender, time) VALUES (?, ?, ?, ?, ?)",
                            (first_name, last_name, school_id, gender, time))
                    else:
                        print(f"School '{school_name}' not found in the database.")
                else:
                    print("Invalid row - not enough values.")
                    continue  # Skip processing this row if it's invalid

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Exception during athletes database update: {e}")
        raise e

# <<<<<<<<<<<<<<<<<<< upload race.csv into database to get races table >>>>>>>>>>>>>>>>

def add_races():
    print("Adding Races")
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])

    if file_path:
        try:
            update_races_from_csv(file_path)
            print("Races added successfully.")

            # Fetch race titles after updating races
            race_titles = get_race_titles()
            return race_titles

        except Exception as e:
            print(f"Error adding races: {e}")

    return ["No Races"]







def update_races_from_csv(file_path):
    try:
        database_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Python class", "athlete_race.db")
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(races)")
        print("Database Schema:")
        print(cursor.fetchall())

        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)

            for row in csv_reader:
                race_title = row[1].strip()  # Take the data from the second column

                # Check if the race already exists in the database
                cursor.execute("SELECT race_id FROM races WHERE race_title = ?", (race_title,))
                existing_race = cursor.fetchone()

                if existing_race:
                    print(f"Race '{race_title}' already exists in the database.")
                else:
                    # Insert the race into the races table
                    cursor.execute("INSERT INTO races (race_title) VALUES (?)", (race_title,))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Exception during database update: {e}")
        raise e




# <<<<<<<<<<<<< begin pulling data from csv's to create race_detail table >>>>>>>>>>>>>>

# get all the athlete_ids in the database
def retrieve_athlete_ids(cursor):
    # Your logic to retrieve athlete_ids from the database
    cursor.execute("SELECT athlete_id FROM athletes")
    athlete_ids = [row[0] for row in cursor.fetchall()]
    return athlete_ids

import sqlite3

# this code takes each athlete and assigns each one a race_detail_id in the race_detail table
def create_race_details_for_athletes():
    try:
        database_path = "C:/Users/roger/OneDrive/Documents/Python class/athlete_race.db"
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Get all athlete_ids from the athletes table
        cursor.execute("SELECT athlete_id FROM athletes")
        athlete_ids = [row[0] for row in cursor.fetchall()]

        # Insert race_detail entries for each athlete
        for athlete_id in athlete_ids:
            cursor.execute("INSERT INTO race_detail (athlete_id) VALUES (?)", (athlete_id,))

        conn.commit()
        print("Race details added successfully.")

    except Exception as e:
        print(f"Error adding race details: {e}")

    finally:
        conn.close()

def connect_races_to_athletes():
    print("Connecting Races to Athletes")
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])

    if file_path:
        try:
            update_race_details_from_csv(file_path)
            print("Race details connected successfully.")
        except Exception as e:
            print(f"Error connecting races to athletes: {e}")

def update_race_details_from_csv(file_path):
    try:
        database_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Python class", "athlete_race.db")
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Fetch all schools and races from the database
        cursor.execute("SELECT school_id, school_name FROM schools")
        schools = {school_id: school_name for school_id, school_name in cursor.fetchall()}

        cursor.execute("SELECT race_id, race_title FROM races")
        races = {race_id: race_title for race_id, race_title in cursor.fetchall()}

        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  # Skip header row

            for row in csv_reader:
                school_name, race_title = [value.strip() for value in row]

                # Find school_id and race_id from the database
                school_id = next((sid for sid, sname in schools.items() if sname == school_name), None)
                race_id = next((rid for rid, rtitle in races.items() if rtitle == race_title), None)

                if school_id is not None and race_id is not None:
                    # Update race_id in the race_detail table
                    cursor.execute("""
                        UPDATE race_detail
                        SET race_id = ?
                        WHERE athlete_id IN (SELECT athlete_id FROM athletes WHERE school_id = ?)
                    """, (race_id, school_id))
                else:
                    print(f"School '{school_name}' or Race '{race_title}' not found in the database.")

        conn.commit()
        print("Race details updated successfully.")

    except Exception as e:
        print(f"Exception during race detail update: {e}")

    finally:
        conn.close()





# <<<<<<<<<<<<<<<<<<<<<<<<<<<<< Top 25 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def display_top_25(listbox, selected_race):
    try:
        # Clear the listbox
        listbox.delete(0, tk.END)

        database_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Python class", "athlete_race.db")
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Fetch schools, athletes, and genders information for the selected race
        cursor.execute("""
            SELECT athletes.first_name, athletes.last_name, athletes.time, athletes.gender
            FROM schools
            LEFT JOIN athletes ON schools.school_id = athletes.school_id
            LEFT JOIN race_detail ON athletes.athlete_id = race_detail.athlete_id
            LEFT JOIN races ON race_detail.race_id = races.race_id
            WHERE races.race_title = ?
            ORDER BY athletes.gender, athletes.time
        """, (selected_race,))

        current_gender = None
        current_place = 0
        places_to_display = 25

        for row in cursor.fetchall():
            first_name, last_name, time, gender = row

            if gender != current_gender:
                # Add a separator for each gender
                listbox.insert(tk.END, f"\n[{gender}]")
                current_gender = gender
                current_place = 0

            current_place += 1

            # Display only places 1-25
            if current_place <= places_to_display:
                # Add athlete information for each gender
                listbox.insert(tk.END, f"\t[{first_name} {last_name}]\t[{time}]\t[{current_place}]")

        # Set a larger font size
        listbox.config(font=("Helvetica", 12))  # Adjust the font size as needed

    except Exception as e:
        print(f"Exception during display top 25 athletes: {e}")

    finally:
        # Close the connection in the 'finally' block to ensure it happens regardless of exceptions
        conn.close()


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< school points breakdown >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def display_school_points(listbox, selected_race):
    try:
        # Clear the listbox
        listbox.delete(0, tk.END)

        database_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Python class", "athlete_race.db")
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Initialize a dictionary to store school points
        school_points_dict = {}

        # Fetch schools, athletes, and genders information for the selected race
        cursor.execute("""
            SELECT athletes.first_name, athletes.last_name, athletes.time, schools.school_name, athletes.gender
            FROM schools
            LEFT JOIN athletes ON schools.school_id = athletes.school_id
            LEFT JOIN race_detail ON athletes.athlete_id = race_detail.athlete_id
            LEFT JOIN races ON race_detail.race_id = races.race_id
            WHERE races.race_title = ?
            ORDER BY athletes.time
        """, (selected_race,))

        current_place = 0

        for row in cursor.fetchall():
            first_name, last_name, time, school_name, gender = row

            current_place += 1
            athlete_points = 26 - current_place if current_place <= 25 else 0

            # Update school points in the dictionary
            if school_name not in school_points_dict:
                school_points_dict[school_name] = athlete_points
            else:
                school_points_dict[school_name] += athlete_points

        # Display school points
        for school_name, school_points in school_points_dict.items():
            listbox.insert(tk.END, f"\n[{school_name}]\n[school_points: {school_points}]")

        # Set a larger font size
        listbox.config(font=("Helvetica", 12))  # Adjust the font size as needed

    except Exception as e:
        print(f"Exception during school points breakdown: {e}")

    finally:
        # Close the connection in the 'finally' block to ensure it happens regardless of exceptions
        conn.close()



# <<<<<<<<<<<<<<<<<<<<<<<<<< all info button: show each school with its athlete and athlete info >>>>>>>>>>>>>>>>>>>>>
def get_race_titles():
    try:
        database_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Python class", "athlete_race.db")
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute("SELECT race_title FROM races")
        race_titles = [row[0] for row in cursor.fetchall()]

        return race_titles

    except Exception as e:
        print(f"Exception during fetching race titles: {e}")

    finally:
        conn.close()


def display_schools_and_athletes(listbox, selected_race):
    try:
        # Clear the listbox
        listbox.delete(0, tk.END)

        database_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Python class", "athlete_race.db")
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Fetch schools, athletes, and genders information for the selected race
        cursor.execute("""
            SELECT athletes.first_name, athletes.last_name, athletes.time, schools.school_name, athletes.gender
            FROM schools
            LEFT JOIN athletes ON schools.school_id = athletes.school_id
            LEFT JOIN race_detail ON athletes.athlete_id = race_detail.athlete_id
            LEFT JOIN races ON race_detail.race_id = races.race_id
            WHERE races.race_title = ?
            ORDER BY athletes.gender, athletes.time
        """, (selected_race,))

        current_gender = None
        current_place = 0

        for row in cursor.fetchall():
            first_name, last_name, time, school_name, gender = row

            if gender != current_gender:
                # Add a separator for each gender
                listbox.insert(tk.END, f"\n[{gender}]")
                current_gender = gender
                current_place = 0

            current_place += 1
            athlete_points = 26 - current_place if current_place <= 25 else 0

            # Add athlete information for each gender
            listbox.insert(tk.END, f"\t[{first_name} {last_name}]\t[{time}]\t[{school_name}][{current_place}][points: {athlete_points}]")

        # Set a larger font size
        listbox.config(font=("Helvetica", 12))  # Adjust the font size as needed

    except Exception as e:
        print(f"Exception during display schools and athletes: {e}")

    finally:
        # Close the connection in the 'finally' block to ensure it happens regardless of exceptions
        conn.close()


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< end of function.py code >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
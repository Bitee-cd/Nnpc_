import csv
import os
from datetime import datetime
import shutil
import pandas as pd
# TODO


# Function to check if a file is a valid CSV file
def isValidCSV(file_name):
    if not os.path.isfile(file_name):
        print("File not found:", file_name)
        return False
    if not file_name.lower().endswith('.csv'):
        print("Invalid CSV file:", file_name)
        return False
    return True

def isValidHeader(file_name, header_name):
    if header_name is None or not header_name.strip():
        print("Invalid header name:", header_name)
        return False

    with open(file_name, 'r') as file:
        csvreader = csv.DictReader(file)
        headers = csvreader.fieldnames
        if header_name not in headers:
            print(f"Header '{header_name}' not found in the CSV file.\n")
            print("Available headers: \n", headers)
            return False
        return True

def parse_date(date_str):
    try:
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d")
        return formatted_date
    except ValueError:
        print("Invalid start date format. Please provide the start date in the format YYYY-MM-DD.",date_str)
        return None


def parse_and_reformat_date(date_str):
    parts = date_str.split('-')

    parts[1] = parts[1][:3].upper()  # Convert to uppercase to match the format in the date string

    reformatted_date_str = '-'.join(parts)
    try:
        formatted_date = datetime.strptime(reformatted_date_str, "%d-%b-%y")
        return formatted_date
    except ValueError:
        print("Error: Invalid date format in date string:", date_str)
        return None

# Function to search for data in a CSV file under a specific header starting from a given date
def searchFileStartingFromDate(file_name, header_name, start_date,keyword):
    start_date = parse_date(start_date)
    if start_date is None:
        return []
    if not isValidCSV(file_name):
        return []

    with open(file_name, 'r') as file:
        csvreader = csv.DictReader(file)
        headers = csvreader.fieldnames
        if header_name not in headers:
            print("Header not found:", header_name)
            return []

        data = []
        for row in csvreader:
            formatted_row_date = parse_and_reformat_date(row['v'])
            if header_name in row and formatted_row_date >= start_date:
                if keyword in row[header_name]:
                    data.append(row[header_name])
    return data


def appendAsteriskToHeaderColumn(general_file_name, general_header_name, non_duplicates):
    # Create a temporary file to write modified rows
    temp_file_name = general_file_name + '.temp'

    with open(general_file_name, 'r') as general_file:
        with open(temp_file_name, 'w', newline='') as temp_file:
            csvreader = csv.DictReader(general_file)
            headers = csvreader.fieldnames
            writer = csv.DictWriter(temp_file, fieldnames=headers)
            writer.writeheader()

            for row in csvreader:
                if row[general_header_name] in non_duplicates:
                    # Append "*" to the cell in the general header column
                    row[general_header_name] += "*"
                writer.writerow(row)

    # Replace the original file with the modified file
    import shutil
    shutil.move(temp_file_name, general_file_name)

def searchForDuplicates(company_file_name, company_header_name, data):
    general_data = set(data)
    if not general_data:
        print("No data found in the provided data list.")
        return

    duplicates = set()

    with open(company_file_name, 'r') as company_file:
        csvreader = csv.DictReader(company_file)
        headers = csvreader.fieldnames
        if company_header_name not in headers:
            print("Header not found:", company_header_name)
            return

        # Temporary file to write non-duplicate rows
        temp_file_name = company_file_name + '.temp'
        with open(temp_file_name, 'w', newline='') as temp_file:
            writer = csv.DictWriter(temp_file, fieldnames=headers)
            writer.writeheader()

            for row in csvreader:
                if company_header_name in row:
                    if row[company_header_name] in general_data:
                        duplicates.add(row[company_header_name])
                    else:
                        writer.writerow(row)

    if duplicates:
        print("Duplicates found and removed from", company_file_name)
        # Write duplicates to a new file
        duplicates_file_name = "duplicates.csv"
        with open(duplicates_file_name, 'w', newline='') as duplicates_file:
            writer = csv.DictWriter(duplicates_file, fieldnames=headers)
            writer.writeheader()
            with open(company_file_name, 'r') as company_file:
                csvreader = csv.DictReader(company_file)
                for row in csvreader:
                    if row[company_header_name] in duplicates:
                        writer.writerow(row)
        print("Duplicates data written to", duplicates_file_name)
    else:
        print("No duplicates found.")

    # Replace the original company file with the temporary file
    shutil.move(temp_file_name, company_file_name)

    # Write non-duplicate items to a separate file
    non_duplicates = general_data - duplicates
    if non_duplicates:
        non_duplicates_file_name = "non_duplicates.csv"
        with open(non_duplicates_file_name, 'w', newline='') as non_duplicates_file:
            writer = csv.writer(non_duplicates_file)
            writer.writerow([company_header_name])
            for item in non_duplicates:
                writer.writerow([item])
        print("Non-duplicate data written to", non_duplicates_file_name)
        appendAsteriskToHeaderColumn(general_file_name, general_header_name, non_duplicates)

    else:
        print("All items in the data list were found in the company file.")


def get_company(keyword):
    while True:
        if keyword == 1:
            return "NNPC"
        elif keyword == 2:
            return "MOG"
        elif keyword == 3:
            return "MON"
        elif keyword == 4:
            return "BISL"
        else:
            keyword = int(input("Invalid key selected. Please select either 1, 2, 3 or 4: "))


if __name__ == '__main__':


    # general file name
    general_file_name = input("Enter the manifest file name: ")
    while not isValidCSV(general_file_name):
        print("Invalid CSV file. Please provide a valid CSV file. \n")
        general_file_name = input("Enter the manifest file name: ")

    # general header name
    general_header_name = input("Enter the manifest header name: ")
    while not isValidHeader(general_file_name,general_header_name):
        print(" Please provide a valid Header name. \n")
        general_header_name = input("Enter the manifest header name: ")

    # start date
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    formatted_start_date = parse_date(start_date)
    while formatted_start_date is None:
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        formatted_start_date = parse_date(start_date)

    # company file name
    company_file_name = input("Enter the company file name: ")
    while not isValidCSV(company_file_name):
        print("Invalid CSV file. Please provide a valid CSV file. \n")
        company_file_name = input("Enter the company file name: ")

    # company header name
    company_header_name = input("Enter the company header name: ")
    while not isValidHeader(company_file_name,company_header_name):
        print(" Please provide a valid Header name. \n")
        company_header_name = input("Enter the company header name: ")

    #keyword
    select_keyword = int(input("Select company keyword \n 1. NNPC \n 2. MOG \n 3. MON \n"))
    company_keyword = get_company(select_keyword)

    data = searchFileStartingFromDate(general_file_name,general_header_name,start_date,company_keyword)
    searchForDuplicates(company_file_name, company_header_name, data)


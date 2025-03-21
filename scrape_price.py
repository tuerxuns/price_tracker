from datetime import datetime

import csv
import os
import pytz

import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from matplotlib.ticker import FuncFormatter
import requests


def fetch_price():
    # The URL of the page you want to scrape
    URL = "https://www.g2g.com/offer/Early-Access-Standard---Exalted-Orb?service_id=lgc_service_1&brand_id=lgc_game_27013&fa=lgc_27013_platform%3Algc_27013_platform_31854%7Clgc_27013_tier%3Algc_27013_tier_54400&sort=lowest_price&include_offline=1"

    # Send a GET request to fetch the page content
    response = requests.get(URL)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        page_content = response.text

        # Print a snippet of the page content for debugging
        print(
            page_content[:500]
        )  # Print first 500 characters of the page to see structure

        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(page_content, "html.parser")

        # Use the selector to find the price element
        price_element = soup.select_one(
            "#pre_checkout_sls_offer > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(6) > div > span.offer-price-amount"
        )

        # Check if the price element is found
        if price_element:
            price = float(price_element.text.strip()) * 100  # Multiply the price by 100
            print(f"Price fetched (100 units): {price}")
            # Store the price along with the date in a CSV file
            store_price(price)
        else:
            print("Price element not found!")
    else:
        print(f"Failed to retrieve the webpage! Status code: {response.status_code}")


def store_price(price):
    # Define the timezone for PST (Pacific Standard Time)
    pst = pytz.timezone("US/Pacific")

    # Get the current time in PST
    current_time_pst = datetime.now(pst)
    today = current_time_pst.strftime("%Y-%m-%d")
    time_of_day = current_time_pst.strftime("%H:%M:%S")  # Format the time as HH:MM:SS

    price = round(price, 4)  # Round price to 4 decimal places

    # Define the file path for the CSV file
    file_path = "prices.csv"  # Use relative path since we're working within the GitHub repository

    # Read existing data from the CSV
    try:
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
    except FileNotFoundError:
        data = []  # If the file doesn't exist, start with an empty list

    # Write to CSV
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header first
        if data:
            writer.writerow(data[0])  # Write the existing header
            data = data[1:]  # Remove the header from the data list
        else:
            writer.writerow(["Date", "Time", "Price"])  # Write a new header

        # Add the new price data to the list
        data.append([today, time_of_day, price])

        # Sort the data by date and time (newest to oldest)
        data.sort(key=lambda row: (row[0], row[1]), reverse=True)

        # Write the sorted data
        writer.writerows(data)

    print(f"Price stored for {today} at {time_of_day} (100 units): {price}")


def plot_lowest_prices():
    # Read the data from the CSV file
    daily_prices = {}

    # Read prices from the CSV and find the lowest price for each day
    with open("prices.csv", "r") as csvfile:
        reader = csv.reader(csvfile)

        # Skip the header row
        next(reader)

        for row in reader:
            date = row[0]  # Date
            try:
                # Try converting the price to a float (from the third column)
                price = float(row[2])
            except ValueError:
                print(f"Invalid price data: {row[2]}")
                continue  # Skip this row if price is invalid

            # If the date is already in the dictionary, update the lowest price
            if date in daily_prices:
                daily_prices[date] = min(daily_prices[date], price)
            else:
                daily_prices[date] = price

    # Extract dates and the lowest prices for plotting
    dates = list(daily_prices.keys())
    prices = list(daily_prices.values())

    # Sort the dates in ascending order
    sorted_dates = sorted(dates)
    sorted_prices = [daily_prices[date] for date in sorted_dates]

    # Create the plot
    plt.plot(sorted_dates, sorted_prices, marker="o", color="b", label="Lowest Price")

    # Add labels and title
    plt.xlabel("Date")
    plt.ylabel("Price (100 units)")
    plt.title("Lowest Price Trend of Exalted Orb")

    # Rotate date labels for readability
    plt.xticks(rotation=45)

    # Format the y-axis to show 4 decimal places
    formatter = FuncFormatter(lambda x, _: f"{x:.4f}")
    plt.gca().yaxis.set_major_formatter(formatter)

    # Show the plot
    plt.tight_layout()
    plt.show()


# Run the function to test
if __name__ == "__main__":
    # Fetch the price and store it
    fetch_price()

    # Plot the lowest prices
    plot_lowest_prices()

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os
from flask import Flask, request

# The URL to fetch the price from
URL = "https://www.g2g.com/offer/Early-Access-Standard---Exalted-Orb?service_id=lgc_service_1&brand_id=lgc_game_27013&fa=lgc_27013_platform%3Algc_27013_platform_31854%7Clgc_27013_tier%3Algc_27013_tier_54400&sort=lowest_price&include_offline=1"

# Initialize Flask app for Google Cloud Functions
app = Flask(__name__)


def fetch_price():
    response = requests.get(URL)
    if response.status_code == 200:
        print("Request successful!")
        page_content = response.text
        soup = BeautifulSoup(page_content, "html.parser")
        price_element = soup.select_one(
            "#pre_checkout_sls_offer > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(6) > div > span.offer-price-amount"
        )

        if price_element:
            price = float(price_element.text.strip()) * 100  # Price for 100 units
            print(f"Price fetched (100 units): {price}")
            store_price(price)
        else:
            print("Price element not found!")
    else:
        print(f"Failed to retrieve the webpage! Status code: {response.status_code}")


def store_price(price):
    today = datetime.today().strftime("%Y-%m-%d")
    price = round(price, 4)  # Round price to 4 decimal places

    # Ensure the CSV file exists and write the price
    file_path = "/tmp/prices.csv"  # Using /tmp for Cloud Functions file storage
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Price"])  # Write header if the file is new

    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([today, price])
    print(f"Price stored for {today} (100 units): {price}")


def plot_lowest_prices():
    daily_prices = {}

    file_path = "/tmp/prices.csv"
    with open(file_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            date = row[0]  # Date
            price = float(row[1])  # Price

            if date in daily_prices:
                daily_prices[date] = min(daily_prices[date], price)
            else:
                daily_prices[date] = price

    dates = list(daily_prices.keys())
    prices = list(daily_prices.values())

    sorted_dates = sorted(dates)
    sorted_prices = [daily_prices[date] for date in sorted_dates]

    plt.plot(sorted_dates, sorted_prices, marker="o", color="b", label="Lowest Price")
    plt.xlabel("Date")
    plt.ylabel("Price (100 units)")
    plt.title("Lowest Price Trend of Exalted Orb")
    plt.xticks(rotation=45)

    # Format y-axis to show 4 decimal places
    formatter = FuncFormatter(lambda x, _: f"{x:.4f}")
    plt.gca().yaxis.set_major_formatter(formatter)

    plt.tight_layout()
    plt.savefig(
        "/tmp/lowest_price_plot.png"
    )  # Save plot in the /tmp folder for Cloud Functions
    print("Plot saved as 'lowest_price_plot.png'.")


@app.route("/", methods=["GET"])
def g2g_price_tracker(request):
    """HTTP-triggered function."""
    fetch_price()  # Fetch and store price
    plot_lowest_prices()  # Plot lowest prices
    return "Price tracking complete!", 200


# No need to include app.run() here for Cloud Functions

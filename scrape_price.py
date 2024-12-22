import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def fetch_price():
    # Set headers to simulate a Canadian user
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept-Language": "en-CA,en;q=0.9",  # Set to Canadian English
    }
    # The URL of the page you want to scrape
    url = "https://www.g2g.com/offer/Early-Access-Standard---Exalted-Orb?service_id=lgc_service_1&brand_id=lgc_game_27013&fa=lgc_27013_platform%3Algc_27013_platform_31854%7Clgc_27013_tier%3Algc_27013_tier_54400&sort=lowest_price&include_offline=1"

    # Send a GET request to fetch the page content
    response = requests.get(URL, headers=headers)

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
    # Get today's date
    today = datetime.today().strftime("%Y-%m-%d")

    # Round the price to 4 decimal places
    price = round(price, 4)

    # Open the CSV file and append the price with the date
    with open("prices.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([today, price])
    print(f"Price stored for {today} (100 units): {price}")


def plot_lowest_prices():
    # Read the data from the CSV file
    daily_prices = {}

    # Read prices from the CSV and find the lowest price for each day
    with open("prices.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            date = row[0]  # Date
            price = float(row[1])  # Price

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

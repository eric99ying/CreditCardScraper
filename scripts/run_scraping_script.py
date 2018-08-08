"""
run_scraping_script.py
~~~
Script to start the scraping. Calls scrape_card in scrape_card.py on each credit card. Writes the dictionary returned
back into a csv file, which will be emailed to the Starbutter business team.
"""
from scrape_to_dict.scrape_card import run_scraper
from scripts.convert_csv import convert_csv
import csv
import os

# The source csv file where we get the links to TOC, offer, and agg for each regular credit cards. (Regular as in the
# TOC html is not dynamic nor a PDF)
current_directory = os.path.dirname(os.path.realpath(__file__))
source_csv_all = os.path.join(current_directory, "csv_files/InputCreditCardsExample.csv")


def single_scrape(card_name: str, toc_link: str, offer_link, agg_link, toc_type: str):
    """
    Scrapes a single credit card. Afterwards, writes to a new csv file.

    Args:
        card_name (str): The name of the credit card.
        toc_link (str): The link of the terms and conditions.
        offer_link (str): The link of the offer page.
        agg_link (str): The link to the NerdWallet review.
        toc_type (str): The type of the terms and conditions. (regular, dynamic, or pdf)
    """
    answer_dict = run_scraper(card_name, toc_link, offer_link, agg_link, toc_type)
    convert_csv(answer_dict)


def mass_scrape(input_csv: str, start_index: int = 0):
    """
    Mass scrapes a csv file containing credit cards and links. Afterwards, writes to a new csv file.

    Args:
        input_csv (str): The path to the csv file.
        start_index (int): The integer row index to start from in csv_file.
    """
    with open(input_csv, newline='') as csv_file:
        csv_reader = list(csv.reader(csv_file))
        for row in csv_reader[start_index:]:  # First row are the attribute titles
            full_card_name = row[0]
            toc_link = row[2]
            offer_link = row[1]
            agg_link = row[3]
            toc_type = row[4]
            print("Starting scraping on " + full_card_name)
            answer_dict = run_scraper(full_card_name, toc_link, offer_link, agg_link, toc_type)
            convert_csv(answer_dict)


# Mass scrape
mass_scrape(input_csv=source_csv_all, start_index=1)

# Single scrape
test_card = "Journey Student Credit Card from Capital One"
test_toc = "https://www.capitalone.com/credit-cards/journey-student/#disclosures"
test_agg = "https://www.nerdwallet.com/card-details/card-name/Capital-One-Student-Rewards"
test_offer = "https://www.capitalone.com/credit-cards/journey-student/"
test_toc_type = "dynamic"

# single_scrape(test_card, test_toc, test_offer, test_agg, test_toc_type)

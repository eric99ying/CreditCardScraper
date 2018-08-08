"""
scrape_card.py
~~~~~~~~~~~~~~

Scrape an individual card. Main function that handles the initial scraping.
"""

from scrape_to_dict import general_scraper, agg_scraper
from scripts.short_name_dict import short_name_dict
from scripts.issuer_processor_category_dict import ipc
import copy
import traceback


def run_scraper(card_name: str, toc_link: str, offer_link: str, agg_link: str, toc_type: str) -> dict:
    """
    Scrape a card.

    Args:
        card_name (str): The name of the card to be scraped in.
        toc_link (str): The URL of the card's terms-and-conditions page.
        offer_link (str): The URL of the offer link.
        agg_link (str): The URL of the agg page.
        toc_type (str): The type of TOC webpage. (can either be "pdf", "dynamic", or "regular")

    Returns:
        dict: The final dictionary of terms and values for each attribute of the card.
    """
    # 1. Scrape from toc_link using general scraper.
    answer_dict = dict()
    if toc_link:  # then you scrape.
        try:
            answer_dict = general_scraper.general_scraper(toc_link, toc_type)
            print("This is the result of general scraper. ")
            print(answer_dict)
        except Exception as e:
            print("Error when trying scraper. Returning empty dictionary.")
            print(traceback.print_exc())
            answer_dict = dict()

    if answer_dict == -1:  # scraper erred without throwing error.
        answer_dict = dict()
        scraper_worked = False
    else:
        scraper_worked = True

    # 2. Modify some variables in answer_dict.
    answer_dict["toc_link"] = toc_link
    answer_dict["offer_link"] = offer_link
    answer_dict["full_card_name"] = card_name
    answer_dict["agg_link"] = agg_link
    # gets the short name from the dictionary in scripts/short_name_dict.py
    if card_name.lower() in short_name_dict.keys():
        answer_dict["short_card_name"] = short_name_dict[card_name.lower()]
    else:
        answer_dict["short_card_name"] = "--- MANUALLY FILL IN THE SHORT NAME ---"
    # gets the issuer, processor, and category from the dictionary in scripts/issuer_processor_category_dict.py
    if card_name.lower() in ipc.keys():
        answer_dict["issuer"] = ipc[card_name.lower()]["issuer"]
        answer_dict["processor"] = ipc[card_name.lower()]["processor"]
        answer_dict["category"] = ipc[card_name.lower()]["category"]
    else:
        answer_dict["issuer"] = "---MANUALLY FILL IN---"
        answer_dict["processor"] = "---MANUALLY FILL IN---"
        answer_dict["category"] = "---MANUALLY FILL IN---"

    if "tips_apr" in answer_dict:
        del answer_dict["tips_apr"]
    if "termination" in answer_dict:
        del answer_dict["termination"]
    if "plan_fee" in answer_dict:
        del answer_dict["plan_fee"]

    # 3. Try to scrape from agg_scraper.
    if agg_link:
        try:
            agg_dict = agg_scraper.scrape_from_agg(agg_link, answer_dict)
        except Exception as e:
            print("You entered an agg link, but scraping from agg link failed")
            print(e)
            agg_dict = dict()
    else:
        agg_dict = answer_dict

    final_dict = copy.deepcopy(agg_dict)

    if scraper_worked:
        final_dict["scraper"] = "TRUE"
    else:
        final_dict["scraper"] = "FALSE"

    # 4. Return the final dictionary of scraped sentences.
    print("Scraper response")
    print(final_dict)
    return final_dict



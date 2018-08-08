"""
agg_scraper.py
~~~
Performs the scraping on agg link (Nerdwallet in this case). It accepts a URL and returns a dictionary
describing a credit card.
"""

import copy
from scrape_to_dict.get_visible_text import scrape_visual_text_directly
import re

# All attribute headers have a _ appended to the front of it to mark it as a header
agg_attribute_mapping_dict = {
    "pros": ["_Pros", "_ Pros"],
    "cons": ["_Cons", "_ Cons"],
    "credit_score": ["_Recommended credit score"],
    "offer_details": ["_Card details"],
    "bonus_offer": ["_Bonus offer"],
    "rewards_rate": ["_Rewards rate"],
    "intro_apr_check": ["_Intro APR"],
    "variable_apr_check": ["_APR, Variable"],
    "annual_fee_check": ["_Annual fee"]
}


def scrape_from_agg(agg_url: str, card_dict_param: dict) -> dict:
    """
    Takes in an aggregator's URL. Scrapes the page. Returns a card_dict. Doesn't store anything

    Args:
        agg_url (str): The url of the agg link we scrape from.
        card_dict_param (dict): The dictionary of attributes and data scraped from the terms and conditions. We
        create a deep copy of the dict and add to it.
    Returns:
        dict: The dictionary containing scraped data from both the TOC and Nerdwallet.
    """
    card_dict = copy.deepcopy(card_dict_param)
    card_name = card_dict["full_card_name"]
    print("scraping from agg for " + card_name)
    print(agg_url)

    # (1) Get all visible text on the webpage (via script using beautiful soup).
    block = scrape_visual_text_directly(agg_url, add_new_lines=True)

    # (2) Try to get rid of unicode garbage as well as replace all "XYZABC123!!!" with new lines.
    try:
        block = block.decode('utf-8').strip()
        block = block.encode('ascii', 'ignore')
    except:
        print("Did not decode and encode.")
        pass

    # substitute all dummy strings with new lines
    block = re.sub(r"XYZABC123!!!", "\n", block)

    # (3) Condense text block to import segment.
    # There are two versions of the page. Figure out which version, then condense block accordingly.
    important_index = block.find("_Card details")
    other_index = block.find("Recommended credit score")

    if important_index < 0 or other_index < 0:
        print("important or other index less than 0")
        return

    if other_index < important_index:
        # version where credit score at the top of the page
        start_index = block.find("Recommended credit score")
        end_index = block.find("NerdWallet reviews are the result of independent research")
    else:
        # version where credit score along with other attributes
        start_index = block.find("_Card details")
        end_index = block.find("See if you may qualify")

    if start_index < 0 or end_index < 0:
        print("start or end index less than 0")
        return
    important_block = block[start_index:end_index]

    # print(important_block)

    # (4) For each agg attribute, grab its respective text in block.
    deep_copy = copy.deepcopy(agg_attribute_mapping_dict)
    agg_dict = __collect_info(deep_copy, important_block)

    # (5) Write to dict.
    for attribute, term in agg_dict.items():
        inner_dict = {"term": term, "value": ""}
        card_dict[attribute] = inner_dict

    # (6) Grab the trademark name. (should be between "Advertiser Disclosure" and "Apply Now")
    card_dict["trademark_card_name"] = block[block.find("Advertiser Disclosure") + len("Advertiser Disclosure"):
                                             block.find("Apply Now")]

    return card_dict


def __collect_info(attributes: dict, text: str) -> dict:
    """
    Used by scrape_from_agg to scrape the agg link. Collects data for each attribute and stores in a dictionary.

    Args:
        attributes: The dictionary of attributes we scrape for.
        text: The piece of text we scrape from. (In this case, it is all visible text on the Nerdwallet page)
    Returns:
        dict: The dictionary of scraped data.
    """
    # (A) Find all attributes that exist in text & location of attributes in text.
    attribute_info = []
    for attribute, aliases in attributes.items():
        alias_index = -1
        alias_length = 0
        for alias in aliases:  # each attribute has multiple aliases (ways it could be written in text)
            alias_index = text.find(alias)
            if alias_index >= 0:
                alias_length = len(alias)
                break  # can only have one alias of attribute
        if alias_index >= 0:
            attribute_info.append({'attribute_name': attribute,
                                   'alias_index': alias_index, 'alias_length': alias_length})

    # (B) Sort attributes in order that they appear in text.
    attribute_info_sorted = sorted(attribute_info, key=lambda k: k['alias_index'])

    # (C) For each attribute, grab the corresponding text.
    answer = dict()
    for index, attribute_dict in enumerate(attribute_info_sorted):
        start_index = attribute_dict['alias_index'] + attribute_dict['alias_length']
        end_index = len(text)  # assume last index
        if not index == (len(attribute_info_sorted) - 1):  # if not last index
            next_attribute_dict = attribute_info_sorted[index + 1]
            end_index = next_attribute_dict['alias_index']  # end index is start of next attribute
        answer[attribute_dict['attribute_name']] = text[start_index:end_index]

    return answer

"""
general_scraper.py
~~~
Returns dict with scraped info from url with terms and conditions for a credit card.
"""

from scrape_to_dict.get_visible_text import get_visible_text
from scrape_to_dict.card_schema import card_dict, upper_table_attribute_mapping_dict, \
    annual_fees_attribute_mapping_dict, transaction_fees_attribute_mapping_dict, penalty_fees_attribute_mapping_dict
import copy
import re


def general_scraper(url: str, toc_type: str) -> dict:
    """
    Scrapes the url. Return a dictionary of the relevant data. First extracts all visible text on the page
    before breaking the text into chunks to be scraped.

    Args:
        url (str): The url of the website being scraped.
        toc_type (str): The type of TOC webpage. (can either be "pdf", "dynamic", or "regular")
    Returns:
        dict: The dictionary with the relevant data.
    """
    print("Scraping from " + url)

    # (0) Create deep copies of card schema stuff
    answer = copy.deepcopy(card_dict)
    deep_copy_upper_table = copy.deepcopy(upper_table_attribute_mapping_dict)
    deep_copy_annual_fees = copy.deepcopy(annual_fees_attribute_mapping_dict)
    deep_copy_transaction_fees = copy.deepcopy(transaction_fees_attribute_mapping_dict)
    deep_copy_penalty_fees = copy.deepcopy(penalty_fees_attribute_mapping_dict)

    # (1) Get all visible text on the webpage (via script using beautiful soup)
    print("Getting visible text from url.")
    block = get_visible_text(url, toc_type)
    # answer["block"] = block # uncomment this if you want to store full block of text

    # # (2) Split table text and fine print((assume webpage begins with table))
    # block_lowercase = block.lower()
    # terminating_string_index = block_lowercase.find(terminating_string.lower())
    # if terminating_string_index == -1:  # ERROR with terminating_string
    #     print("Scraping Error: Problem with terminating string")
    #     return -1

    # table_text = block[:terminating_string_index]
    print("Processing visible text.")
    table_text = block
    # fine_print_text = block[terminating_string_index:]
    # answer["fine_print"] = fine_print_text # uncomment this if you want to store fine print

    # (3) Split table text into upper/lower table text (interest rates and interest charges VERSUS fees section)
    table_text_lowercase = table_text.lower()
    dividers = ["Fee Summary", "fees annual", "feesannual", "fees\nannual", "fees \nannual", "fees\nFlexPerks", "fees  transaction",
                "FeesSKYPASS", "FeesVisa", "FeesU.S. Bank", "Fees Transaction", "FeesFlexPerks", "Fees       Annual",
                "Fees     Annual", "Fees", "Fee"]
    div_index = find_div_index(dividers, table_text_lowercase)
    if div_index < 0:  # ERROR with separating tables
        print("Scraping Error: Problem with separating tables between apr and fees.")
        return -1

    upper_table_text = table_text[:div_index]
    lower_table_text = table_text[div_index:]

    # (4) Split lower table text (fees section) further, into annual fees, transaction fees, and penalty fees
    lower_table_text_lowercase = lower_table_text.lower()
    fee_div_index1 = find_div_index(["transaction fees", "transactionfees", "transaction\nfees"],
                                    lower_table_text_lowercase)
    if fee_div_index1 < 0:  # ERROR with separating fees table
        print("Scraping Error: Problem with separating fee table between annual and trans/penalty fees.")
        return -1

    annual_fees_text = lower_table_text[:fee_div_index1]
    other_lower_text = lower_table_text[fee_div_index1:]

    other_lower_text_lowercase = other_lower_text.lower()
    fee_div_index2 = find_div_index(["penalty fees", "penaltyfees", "penalty\nfees"], other_lower_text_lowercase)
    if fee_div_index2 < 0:
        print("Scraping Error: Problem with separating fee table between transaction and penalty fees.")
        return -1
    transaction_fees_text = other_lower_text[:fee_div_index2]
    penalty_fees_text = other_lower_text[fee_div_index2:]

    # (5) For each segment of table text, go through its respective attributes and grab corresponding attribute info
    upper_table_dict = collect_info(deep_copy_upper_table, upper_table_text)
    annual_fees_dict = collect_info(deep_copy_annual_fees, annual_fees_text)
    transaction_fees_dict = collect_info(deep_copy_transaction_fees, transaction_fees_text)
    penalty_fees_dict = collect_info(deep_copy_penalty_fees, penalty_fees_text)

    # (6) Use each dict to configure output matching formatting.
    answer = configure_output(upper_table_dict, answer)
    answer = configure_output(annual_fees_dict, answer)
    answer = configure_output(transaction_fees_dict, answer)
    answer = configure_output(penalty_fees_dict, answer)

    return answer


def find_div_index(dividers, text):
    """
    In text, find index of a dividing string.

    Args:
        dividers (List[str]): A list of possible divider strings.
        text (str): The text we want to search in.
    Returns:
        int: The integer index of where the divider is. Returns -1 if none of the dividers are found.
    """
    answer = -1
    for div in dividers:  # look through possible dividers
        answer = text.lower().find(div.lower())
        if answer >= 0:  # found the divider (only one--dividers contains aliases)
            break

    return answer


def collect_info(attributes: dict, text: str) -> dict:
    """
    In text, find attributes and collect the corresponding info. Returns dictionary with attribute and its
    corresponding text.

    Args:
        attributes (dict): The dictionary of attributes to look for (ie. annual_fee).
        text (str): The one line string of text to scrape.
    Returns:
        dict: The dictionary of scraped data from the text.
    """
    # (A) Find all attributes that exist in text & location of attributes in text.
    attribute_info = []
    for attribute, aliases in attributes.items():
        alias_index = -1
        alias_length = 0
        for alias in aliases:  # each attribute has multiple aliases (ways it could be written in text)
            alias_index = (text.lower()).find(alias.lower())
            if alias_index >= 0:
                alias_length = len(alias)
                break  # can only have one alias of attribute
        if alias_index >= 0:
            attribute_info.append({'attribute_name': attribute,
                                   'alias_index': alias_index, 'alias_length': alias_length})

    # (B) Sort attributes in order that they appear in text.
    attribute_info_sorted = sorted(attribute_info, key=lambda k: k['alias_index'])

    # (C) If termination attribute is in attribute_info_sorted, we want to excise all of the attributes whose
    # alias_index is after the termination alias_index, since the termination marks the end of the table. We
    # don't want to accidentally scrape anything in the terms and condition section of the page.
    temp_list = list(filter(lambda k: k["attribute_name"] == "termination", attribute_info_sorted))
    if temp_list:
        termination_index = temp_list[0]["alias_index"]
        attribute_info_sorted = list(filter(lambda k: k["alias_index"] <= termination_index, attribute_info_sorted))

    # (D) For each attribute, grab the corresponding text between the current attribute and the next attribute.
    answer = dict()
    for index, attribute_dict in enumerate(attribute_info_sorted):
        start_index = attribute_dict['alias_index'] + attribute_dict['alias_length']
        end_index = len(text)  # assume last index
        if not index == (len(attribute_info_sorted) - 1):  # if not last index
            next_attribute_dict = attribute_info_sorted[index + 1]
            end_index = next_attribute_dict['alias_index']  # end index is start of next attribute

        # we want to excise out garbage such as "This APR will vary with the market's prime rate...etc"
        temp_text = text[start_index:end_index]
        temp_text = __excise_sentence(temp_text)
        answer[attribute_dict['attribute_name']] = temp_text

    return answer


def configure_output(source_dict: dict, answer_dict: dict) -> dict:
    """
    Based on formatting in card_schema.py, configure where information stored.

    Args:
        source_dict (dict): The dictionary where we extract our data from.
        answer_dict (dict): The final dictionary where we insert our data based on the formatting in card_schema.py.
    Returns:
        dict: The modified answer_dict.
    """
    for attribute in source_dict:
        answer_dict[attribute]["term"] = source_dict[attribute]
    return answer_dict


def __excise_sentence(text: str) -> str:
    """
    Takes a string and excises out sentences with the form "These APRs will vary with the market
    based on the Prime Rate." Uses python regular expressions. If sentence is not found, nothing will happen.

    Args:
        text (str): The piece of text we want to perform regular expressions on.
    Returns:
        str: The modified sentence with any unnecessary sentences removed.
    """
    match = re.search(r"[A-Z][^\.!?]*APR[^\.!?]*Prime Rate[^\.!?]*[\.!?]", text)
    if match:
        index = match.start(0)
        return text[:index]

    return text


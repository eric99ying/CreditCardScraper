"""
term_processing_script.py
~~~
Takes in a csv file and extracts numerical values for most attributes of a credit card.
"""

import csv
from scrape_to_dict.card_schema import card_dict
from term_processor import clean_up_terms, second_clean
from scripts.convert_csv import convert_csv

from typing import List
import copy

# source_csv = "csv_filescredit_card_raw_scraped - credit_card_raw_all.csv"
source_csv = "csv_files/credit_card_raw_scraped.csv"


def __store_attribute_string_to_dict(attribute_list: List[str]) -> dict:
    """
    Takes a list of attributes of a card and stores it in a dictionary, which gets returned.

    Args:
        attribute_list (List[str]): The list of attribute data about a card.
    Returns:
        dict: The dictionary (card_dict from card_schema) of attributes and its corresponding string and value.
    """
    answer_dict = copy.deepcopy(card_dict)
    if "tips_apr" in answer_dict.keys():
        del(answer_dict["tips_apr"])
    if "termination" in answer_dict.keys():
        del(answer_dict["termination"])
    if "plan_fee" in answer_dict.keys():
        del (answer_dict["plan_fee"])

    answer_dict["full_card_name"] = attribute_list[0].strip()
    answer_dict["short_card_name"] = attribute_list[1].strip()
    answer_dict["trademark_card_name"] = attribute_list[2].strip()
    answer_dict["category"] = attribute_list[3].strip()
    answer_dict["issuer"] = attribute_list[4].strip()
    answer_dict["processor"] = attribute_list[5].strip()
    answer_dict["toc_link"] = attribute_list[6].strip()
    answer_dict["offer_link"] = attribute_list[7].strip()
    answer_dict["agg_link"] = attribute_list[8].strip()
    answer_dict["balance_transfer_apr"]["term"] = attribute_list[9].strip()
    answer_dict["cash_advance_apr"]["term"] = attribute_list[12].strip()
    answer_dict["penalty_apr"]["term"] = attribute_list[15].strip()
    answer_dict["purchase_apr"]["term"] = attribute_list[18].strip()
    answer_dict["paying_interest"]["term"] = attribute_list[21].strip()
    answer_dict["minimum_interest_charge_apr"]["term"] = attribute_list[23].strip()
    answer_dict["annual_fee"]["term"] = attribute_list[26].strip()
    answer_dict["balance_transfer_fee"]["term"] = attribute_list[29].strip()
    answer_dict["cash_advance_fee"]["term"] = attribute_list[32].strip()
    answer_dict["foreign_transaction_fee"]["term"] = attribute_list[35].strip()
    answer_dict["late_payment_fee"]["term"] = attribute_list[38].strip()
    answer_dict["returned_payment_fee"]["term"] = attribute_list[41].strip()
    answer_dict["returned_check_fee"]["term"] = attribute_list[44].strip()
    answer_dict["over_limit_fee"]["term"] = attribute_list[47].strip()
    answer_dict["pros"]["term"] = attribute_list[50].strip()
    answer_dict["cons"]["term"] = attribute_list[52].strip()
    answer_dict["credit_score"]["term"] = attribute_list[54].strip()
    answer_dict["bonus_offer"]["term"] = attribute_list[58].strip()
    answer_dict["offer_details"]["term"] = attribute_list[60].strip()
    answer_dict["rewards_rate"]["term"] = attribute_list[62].strip()
    answer_dict["intro_apr_check"]["term"] = attribute_list[64].strip()
    answer_dict["variable_apr_check"]["term"] = attribute_list[66].strip()
    answer_dict["annual_fee_check"]["term"] = attribute_list[68].strip()

    return answer_dict


def term_process(dest_csv: str, starting_index: int):
    """
    Function to term process and extract numerical values from scraped data.

    Args:
        dest_csv (str): The destination csv file.
        starting_index (int): The starting index.
    Returns:
         str: Success
    """
    with open(source_csv, 'r', newline='') as csv_f:
        csv_reader = list(csv.reader(csv_f))
        for row in csv_reader[starting_index:]:
            attribute_data = list(row)
            print([str(i) + ' ' + str(j) for i, j in enumerate(attribute_data)])
            attribute_dict = __store_attribute_string_to_dict(attribute_data)
            processed_dict = clean_up_terms.clean_up_terms(attribute_dict)
            processed_dict = second_clean.second_clean(processed_dict)
            print(processed_dict)
            convert_csv(processed_dict, dest_csv)

    return "Success"


term_process("csv_files/credit_card_raw_processed.csv", 0)


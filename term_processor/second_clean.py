"""
second_clean.py
~~~
Contains function that extracts number values from processed values. These numbers are used to compare
credit cards with one another.
"""

import re
import copy
from typing import List

# Attributes where both the monetary and percentage values exist and are used
weird_fee_attributes = [
    "balance_transfer_fee",
    "cash_advance_fee",
]

# Attributes in which the extracted value is a percentage
percent_attributes = [
    "purchase_apr",
    "cash_advance_apr",
    "balance_transfer_apr",
    "penalty_apr",
    "foreign_transaction_fee",
]

# Attributes in which the extracted value is a dollar amount
money_attributes = [
    "annual_fee",
    "late_payment_fee",
    "minimum_interest_charge_apr",
    "returned_payment_fee",
    "returned_check_fee",
    "over_limit_fee",
]

# Attributes we exclude from processing again
excluded_attributes = [
    "toc_link",
    "offer_link",
    "full_card_name",
    "agg_link",
    "issuer",
    "short_card_name",
    "trademark_card_name",
    "bonus_offer",
    "rewards_rate",
    "pros",
    "cons",
    "offer_details",
    "intro_apr_check",
    "variable_apr_check",
    "annual_fee_check",
    "paying_interest",
    "processor",
    "category",
]


def second_clean(card_dict: dict) -> dict:
    """
    Performs a second round of numerical extraction. This time, we extract only a single numerical value for each
    attribute for comparison sakes.

    Args:
        card_dict (dict): The dictionary with terms and values for each attribute.
    Returns:
        dict: Dictionary containing terms, values, and numbers for each attribute.
    """
    answer_dict = copy.deepcopy(card_dict)
    for attribute, attribute_info in card_dict.items():
        if attribute not in excluded_attributes:
            value_to_process = attribute_info["value"]

            if not value_to_process:
                number = ""
                if attribute == "credit_score":
                    answer_dict[attribute]["low_number"] = number
                    answer_dict[attribute]["high_number"] = number
                else:
                    answer_dict[attribute]["number"] = number

            elif attribute in percent_attributes:
                number = find_max_percentage(value_to_process)
                answer_dict[attribute]["number"] = number

            elif attribute in weird_fee_attributes:
                number = find_max_percentage(value_to_process)
                answer_dict[attribute]["number"] = number

            elif attribute in money_attributes:
                number = float(value_to_process[1:])
                answer_dict[attribute]["number"] = number

            elif attribute == "credit_score":
                # assume that all credit scores are three digit numbers
                scores = process_regex_multiple(r"\d\d\d", value_to_process)
                # scores should be ["{low_score}", "{high_score}"]
                low_score = scores[0]
                high_score = scores[1]
                answer_dict[attribute]["low_number"] = low_score
                answer_dict[attribute]["high_number"] = high_score

    return answer_dict


def find_max_percentage(value_to_process: str) -> (float, int):
    """
    Given a percentage value (12%, 12% to 15%...), finds and returns the maximum percentage.

    Args:
        value_to_process (str): The value to process.
    Returns:
        str: The largest percentage as just a single number. (ie. 15)
    """
    results = process_regex_multiple(r"[\d\.]+(?=%)", value_to_process)

    if not results:
        return -1

    for i in range(len(results)):
        try:
            results[i] = float(results[i])
        except Exception as e:
            print("Error during float conversion of percentage.")
            print(e)
            return -1

    return max(results)


# Helper functions for regex matching and returning

def process_regex(pattern: str, text: str) -> str:
    """
    Takes a pattern and a text and perform regex on it. Returns a single match.

    Args:
        pattern (str): The pattern to search for.
        text (str): The piece of text to perform search on.
    Returns:
        str: A string match.
    """
    regex = re.compile(pattern)
    for result in regex.findall(text):
        return result
    return None


def process_regex_multiple(pattern: str, text: str) -> List[str]:
    """
    Takes a pattern and a text and perform regex on it. Returns a list of multiple matches.

    Args:
        pattern (str): The pattern to search for.
        text (str): The piece of text to perform search on.
    Returns:
        List[str]: A list of string matches.
    """
    answer = []
    regex = re.compile(pattern)
    for result in regex.findall(text):
        answer.append(result)
    return answer

# clean_up_terms.py: contains fxn that cleans up scraped terms gets its processed value

import copy
import re
from typing import List

# Attributes in which the extracted value is a percentage
percent_attributes = [
    "purchase_apr",
    "cash_advance_apr",
    "balance_transfer_apr",
    "penalty_apr",
    "foreign_transaction_fee",
    "intro_apr_check",
    "variable_apr_check"
]

# Attributes in which the extracted value is a dollar amount
money_attributes = [
    "annual_fee",
    "late_payment_fee",
    "minimum_interest_charge_apr",
    "returned_payment_fee",
    "returned_check_fee",
    "over_limit_fee",
    "annual_fee_check"
]

# Attributes in which the extracted value is just an integer
integer_attributes = [
    "paying_interest"
]

# Attributes we exclude from processing
excluded_attributes = [
    "toc_link",
    "offer_link",
    "full_card_name",
    "agg_link",
    "issuer",
    "short_card_name",
    "trademark_card_name",
    "processor",
    "category"
]

# Attributes where both the monetary and percentage values exist and are used
weird_fee_attributes = [
    "balance_transfer_fee",
    "cash_advance_fee",
]

# Attributes scraped from the NerdWallet link that is not credit_score, offer_details, pros and cons, and
# is not contained in any of the other attribute lists
nw_attributes = [
    "rewards_rate",
    "bonus_offer",
]


def clean_up_terms(card_dict: dict) -> dict:
    """
    Takes a card_dict and processes the terms for each attribute. Returns another dictionary with values stored along
    with the string terms.

    Args:
        card_dict (dict): The dictionary of terms.
    Returns:
        dict: Another dictionary with terms and values.
    """
    card_info = copy.deepcopy(card_dict)
    print("Cleaning up terms and extracting values for " + card_info["full_card_name"])

    for attribute, attribute_info in card_info.items():
        if attribute not in excluded_attributes:
            raw_term_to_process = attribute_info["term"]
            try:
                if attribute in nw_attributes:
                    value = process_other_agg(attribute, raw_term_to_process)
                if attribute in money_attributes:
                    value = process_money_attribute(attribute, raw_term_to_process)
                if attribute in percent_attributes:
                    value = process_percent_attribute(attribute, raw_term_to_process)
                    if attribute == "balance_transfer_apr" or "purchase_apr":
                        value = combine_percent_attribute(simple_clean(raw_term_to_process), value)
                if attribute in integer_attributes:
                    value = process_integer_attribute(attribute, raw_term_to_process)
                if attribute == "pros" or attribute == "cons":
                    value = process_pros_and_cons(attribute, raw_term_to_process)
                if attribute == "credit_score":
                    value = process_credit_score(attribute, raw_term_to_process)
                if attribute == "offer_details":
                    value = process_offer_details(attribute, raw_term_to_process)
                if attribute in weird_fee_attributes:
                    value = process_weird_fees(attribute, raw_term_to_process)

            except Exception as e:
                print("Error occurred in extraction for the attribute " + attribute)
                print(e)
                value = "------ERROR------"

            card_info[attribute]["value"] = value

    return card_info


def process_money_attribute(attribute: str, raw_term: str) -> str:
    """
    Extracts a monetary value.

    Args:
        attribute (str): The attribute.
        raw_term (str): The raw term string.
    Returns:
        str: The numerical monetary value.
    """
    raw_term = raw_term.replace("Frequently Asked Questions", "")

    # Special case for minimum_interest_charge_apr attribute
    if attribute == "minimum_interest_charge_apr":
        if raw_term.lower().find("none") >= 0:
            return "$0"
        elif raw_term.find("cents") >= 0:
            cents_phrase = process_regex(r"\d+(?= cents)", raw_term)
            cents_amount = float(cents_phrase)
            cents_dollar = cents_amount / 100.0
            cents_dollar_str = "$" + str(cents_dollar)
            if len(cents_dollar_str) == 4:
                cents_dollar_str = cents_dollar_str + "0"  # need to add trailing 0
            return cents_dollar_str

    if raw_term.lower().find("none") >= 0 or raw_term.lower().find("not applicable") >= 0:
        return "$0"

    if raw_term.find("$") >= 0:
        money_occurrences = process_regex_multiple(r"\$[\d.]+", raw_term)
        # Only extract the largest dollar amount for the fee
        processed_val = max(money_occurrences)
    else:
        # Fee is not shown in terms and conditions
        processed_val = ""

    # "$.5" -> "$0.5", "$34.3." -> "$34.3"
    processed_val = re.sub(r"\$\.", "$0.", processed_val)
    processed_val = re.sub(r"\.$", "", processed_val)
    return processed_val


def process_percent_attribute(attribute: str, raw_term: str) -> str:
    """
    Extracts a percentage value.

    Args:
        attribute (str): The attribute.
        raw_term (str): The raw term string.
    Returns:
        str: The numerical percentage value.
    """
    raw_term = simple_clean(raw_term)
    if not raw_term:
        return ""

    if attribute == "intro_apr_check" or attribute == "variable_apr_check":
        if raw_term.lower().find("n/a") >= 0 or raw_term.lower().find("none") >= 0:
            return "None"

    if raw_term.lower().find("none") >= 0 or raw_term.lower().find("not applicable") >= 0 \
            or raw_term.lower().find("n/a") >= 0:
        if attribute != "intro_apr_check":
            return "0%"
        else:
            return ""

    # search for different possible combinations of percentages
    range_apr_match = re.search(r"([\d\.]+%) +to +([\d\.]+%)", raw_term)
    if not range_apr_match:
        range_apr_match = re.search(r"([\d\.]+%) +- +([\d\.]+%)", raw_term)
    if range_apr_match:
        return range_apr_match.group(1) + " to " + range_apr_match.group(2)

    multiple_apr_match = re.search(r"([\d\.]+%)\, +([\d\.]+%)\,* +or +([\d\.]+%)", raw_term)
    if multiple_apr_match:
        return multiple_apr_match.group(1) + ", " + multiple_apr_match.group(2) + ", or " + multiple_apr_match.group(3)

    double_apr_match = re.search(r"([\d\.]+%) +or +([\d\.]+%)", raw_term)
    if double_apr_match:
        return double_apr_match.group(1) + " or " + double_apr_match.group(2)

    single_apr_match = process_regex(r"[\d\.]+%", raw_term)
    if single_apr_match:
        if attribute == "intro_apr_check":
            duration_match = process_regex(r"\d+ months", raw_term)
            if not duration_match:
                duration_match = process_regex(r"\d+ billing cycles", raw_term)
                if not duration_match:
                    duration_match = process_regex(r"\d+ mos", raw_term)
                    if duration_match:
                        duration_match = duration_match[:len(duration_match) - 3] + "months"
            if duration_match:
                return single_apr_match + " for " + duration_match

        return single_apr_match

    if raw_term.find(". ") > 0:
        return

    return ""


def combine_percent_attribute(term: str, percent_string: str) -> str:
    """
    Combines the percent attribute string with the first sentence.

    Args:
        term (str): The term string.
        percent_string (str): The percent attribute string.
    Returns:
        str: The final string.
    """
    ind = term.find(". ")
    if ind > 0:
        return term[:ind] + ". After that, " + percent_string
    return percent_string


def process_integer_attribute(attribute: str, raw_term: str) -> str:
    """
    Extracts an integer value.

    Args:
        attribute (str): The attribute.
        raw_term (str): The raw term string.
    Returns:
        str: The numerical integer value.
    """
    if attribute == "paying_interest":
        match = process_regex(r"\d+(?= days)", raw_term)
        if match:
            return match + " days"

    return ""


def process_offer_details(attribute: str, raw_term: str) -> str:
    """
    Cleans up the offer details string.

    Args:
        attribute (str): The name of the attribute.
        raw_term (str): The raw term string.
    Returns:
         str: The cleaned up offer details.
    """
    if attribute == "offer_details":
        # Cleans up the raw_term string
        answer = re.sub(r"Extended Warranty Protection.*", "", raw_term)

        answer = answer.replace("U.\nS.", "U.S.")
        answer = answer.replace(".\ncom", ".com")
        answer = answer.replace("Learn More.", "")
        answer = answer.replace("Terms Apply.\n", "")
        answer = answer.replace("Terms Apply.", "")
        answer = answer.replace("View Rates and Fees_APRPurchase: N/A\n", "")
        answer = answer.replace("View Rates and Fees_APRPurchase: N/A", "")
        answer = answer.replace("View Rates and Fees\n", "")
        answer = answer.replace("View Rates and Fees", "")
        answer = answer.replace("Terms & Limitations Apply\n", "")
        answer = answer.replace("Terms and limitations apply\n", "")

        return answer

    return ""


# We don't want to extract anything from the pros and cons term.
def process_pros_and_cons(attribute: str, raw_term: str) -> str:
    return raw_term


def process_other_agg(attribute: str, raw_term: str) -> str:
    """
    Cleans up other NerdWallet attributes (reward_rate, bonus_offer, checks...).

    Args:
        attribute (str): The name of the attribute.
        raw_term (str): The raw term string.
    Returns:
         str: The cleaned up NW attribute.
    """
    value_to_process = simple_clean(raw_term)

    if attribute == "rewards_rate" or attribute == "bonus_offer":
        return value_to_process

    return ""


def process_credit_score(attribute: str, raw_term: str) -> str:
    """
    Extracts two credit score values from the credit score term. One value is the low value, the other is the high
    value. Returns "{low_value}-{high_value}."

    Args:
        attribute (str): The attribute.
        raw_term (str): The raw term string.
    Returns:
        str: The credit score range.
    """
    if attribute == "credit_score":
        # There should exist 2 three digit numbers side by side (ie. 450650)
        processed_values = process_regex_multiple(r"\d\d\d\d\d\d", raw_term)
        if len(processed_values) == 0:
            return ""
        processed_values = processed_values[0]
        processed_low_val = processed_values[:3]
        processed_high_val = processed_values[3:]

        return processed_low_val + " to " + processed_high_val

    return ""


def process_weird_fees(attribute: str, raw_term: str) -> str:
    """
    Extracts percentages and monetary values from either..or.. sentences.

    Args:
        attribute (str): The attribute name.
        raw_term (str): The raw term string.
    Returns:
        str: The processed string in the format (2% or $3)
    """
    raw_term = simple_clean(raw_term)
    if not raw_term:
        return ""

    if attribute == "balance_transfer_fee" or attribute == "cash_advance_fee":
        # Checks the existence of percentage, monetary, or both.
        percentage_match = re.search(r"[\d\.]+\%", raw_term)
        monetary_match = re.search(r"\$[\d.]+", raw_term)
        percentage_string = ""
        monetary_string = ""
        if percentage_match:
            percentage_string = percentage_match.group()
        if monetary_match:
            monetary_string = monetary_match.group()

        if percentage_string and monetary_string:
            if attribute == "balance_transfer_fee":
                return "either " + percentage_string + " of each transfer " + " or " + monetary_string \
                       + ", whichever is greater"
            if attribute == "cash_advance_fee":
                return "either " + percentage_string + " of each advance " + " or " + monetary_string \
                       + ", whichever is greater"
        elif percentage_string:
            if attribute == "balance_transfer_fee":
                return percentage_string + " of each transfer"
            if attribute == "cash_advance_fee":
                return percentage_string + " of each advance"
        elif monetary_string:
            return monetary_string

    return ""


# General Cleaning/Regex Helper Functions

def simple_clean(term: str) -> str:
    """
    Function that takes in a raw_term and fixes basic formatting issues. Only used for process_other_agg.

    Args:
        term (str): The string to fix.
    Returns:
         str: Fixed string.
    """
    answer = term

    # (0) If term is blank, return
    if term == "" or term == " ":
        return ""

    # (1) Replace remaining newlines with spaces
    answer = answer.replace("\n", " ")
    answer = answer.replace("&nbsp;", "")

    # (2) Add spaces after periods and commas
    answer = re.sub(r"\.[A-Z]", add_space, answer)
    answer = re.sub(r"\,[a-zA-Z]", add_space, answer)

    # (3) Add spaces after lowercase letter concatenated with NOT (lowercase letter or space)
    # essentially, add space between lowercase letter concatenated with uppercase letter, number, or special character
    answer = re.sub(r"[a-z][A-Z]", add_space, answer)
    answer = re.sub(r"[a-z]\d", add_space, answer)
    answer = re.sub(r"[a-z]\$", add_space, answer)
    answer = re.sub(r":\w", add_space, answer)
    answer = re.sub(r"\d[a-zA-Z]", add_space, answer)
    answer = re.sub(r"%[a-zA-Z]", add_space, answer)

    # (4) Remove periods or asterisk at the end of answer
    last_index = len(answer) - 1
    last_char = answer[last_index]
    if last_char == "." or last_char == "*":
        answer = answer[:last_index]

    # (4) Remove extra spaces
    answer = re.sub(r" +", " ", answer)

    # (5) Remove terms apply string
    answer = re.sub("Terms Apply", "", answer)
    answer = re.sub(r" introductory APR", "", answer)

    # (6) If after processing answer is blank, return not found string
    if answer == "" or answer.isspace():
        return ""

    return answer


def add_space(matchobj) -> str:
    """
    Function called by re.sub to add a space where needed.

    Args:
        matchobj (re.Match): The Match object.
    Returns:
        str: The string with space.
    """
    current_str = matchobj.group(0)
    return current_str[:1] + " " + current_str[1:]


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
    regex = re.compile(pattern)
    results = []
    for result in regex.findall(text):
        results.append(result)
    return results

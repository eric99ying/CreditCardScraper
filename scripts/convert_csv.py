"""
convert_csv.py
~~~
This module handles converting data from the dictionary returned from scrape_card.py into a csv file.
Later on, this module is also used to convert data from the output of clean_up_terms.py and second_clean.py
into a csv file, as well as converting the generated phrases in phrase_generation.
"""

import csv
import os
from scrape_to_dict.card_schema import card_dict

current_directory = os.path.dirname(os.path.realpath(__file__))
f = os.path.join(current_directory, "csv_files/credit_card_phrases.csv")
f2 = os.path.join(current_directory, "csv_files/credit_card_raw_scraped.csv")

# Order of attributes to be displayed in the csv file for CreditCardCardRaw/CreditCardRawInput (raw scraped data)
# This order is not the same as the actual spreadsheet (due to human editing)
attributes_order = ["full_card_name", "short_card_name", "trademark_card_name", "category", "issuer",
                    "processor", "toc_link", "offer_link",
                    "agg_link", "balance_transfer_apr", "cash_advance_apr", "penalty_apr", "purchase_apr",
                    "paying_interest", "minimum_interest_charge_apr", "annual_fee", "balance_transfer_fee",
                    "cash_advance_fee", "foreign_transaction_fee", "late_payment_fee", "returned_payment_fee",
                    "returned_check_fee", "over_limit_fee", "pros", "cons", "credit_score", "bonus_offer",
                    "offer_details", "rewards_rate", "intro_apr_check", "variable_apr_check", "annual_fee_check"]

# Order of attributes to be displayed in the csv file for CreditCardCard (attribute responses)
attributes_order_voice_responses = ["name", "short_card_name", "trademark_card_name", "issuer_name",
                                    "processor", "balance_transfer_apr", "balance_transfer_apr_chips",
                                    "balance_transfer_apr_followup_question",
                                    "cash_advance_apr", "cash_advance_apr_chips", "cash_advance_apr_followup_question",
                                    "penalty_apr",
                                    "penalty_apr_chips", "penalty_apr_followup_question", "purchase_apr",
                                    "purchase_apr_chips",
                                    "purchase_apr_followup_question", "minimum_interest_charge_apr",
                                    "minimum_interest_charge_apr_chips",
                                    "minimum_interest_charge_apr_followup_question", "annual_fee", "annual_fee_chips",
                                    "annual_fee_followup_question",
                                    "balance_transfer_fee", "balance_transfer_fee_chips",
                                    "balance_transfer_fee_followup_question",
                                    "cash_advance_fee", "cash_advance_fee_chips", "cash_advance_fee_followup_question",
                                    "foreign_transaction_fee", "foreign_transaction_fee_chips",
                                    "foreign_transaction_fee_followup_question",
                                    "late_payment_fee", "late_payment_fee_chips", "late_payment_fee_followup_question",
                                    "returned_payment_fee",
                                    "returned_payment_fee_chips", "returned_payment_fee_followup_question",
                                    "returned_check_fee", "returned_check_fee_chips",
                                    "returned_check_fee_followup_question",
                                    "over_limit_fee", "over_limit_fee_chips", "over_limit_fee_followup_question",
                                    "pros", "pros_chips", "pros_followup_question", "cons", "cons_chips",
                                    "cons_followup_question",
                                    "credit_score", "credit_score_chips", "credit_score_followup_question",
                                    "bonus_offer",
                                    "bonus_offer_chips", "bonus_offer_followup_question", "rewards_rate",
                                    "rewards_rate_chips", "rewards_rate_followup_question", "image_link",
                                    "fb_horizontal_link", "issuer_phrase", "score", "score_response",
                                    "score_response_chips", "score_response_followup_question",
                                    "billing_and_payment_quality", "billing_and_payment_quality_chips",
                                    "billing_and_payment_quality_followup_question", "credit_card_terms",
                                    "credit_card_terms_chips", "credit_card_terms_followup_question",
                                    "customer_service", "customer_service_chips", "customer_service_followup_question",
                                    "problem_resolution", "problem_resolution_chips",
                                    "problem_resolution_followup_question", "rewards_quality", "rewards_quality_chips",
                                    "rewards_quality_followup_question", "overall_satisfaction",
                                    "overall_satisfaction_chips", "overall_satisfaction_followup_question",
                                    "similar_cards", "category"
                                    ]


def convert_csv(data_dict: dict, dest_csv: str=f2) -> str:
    """
    Writes the data in data_dict to the dest_csv file. Formats all of the attribute data in a
    very specific way. See CreditCardCardRaw in Google sheets for output format. This is used for scraping the raw
    data and formatting that data into a spreadsheet.

    Args:
        data_dict (dict): The data to be written.
        dest_csv (str): The destination csv file to output results on.
    Returns:
        str: Success if the write is successful.
    """
    with open(dest_csv, "a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)

        # add all of the term and values into data_list
        data_list = []
        for attribute in attributes_order:
            example_data = card_dict.get(attribute)
            try:
                data = data_dict.get(attribute)
                if type(data) == dict:  # the data is a dictionary with keys "term" and "value"
                    # if the attribute is a credit score, value is instead value_low and value_high
                    term = data.get("term")
                    value = data.get("value")
                    data_list.append(term)
                    data_list.append(value)
                    if attribute == "credit_score":
                        data_list.append(data.get("low_number"))
                        data_list.append(data.get("high_number"))
                    elif "number" in data.keys():
                        # rubber band fix. for some reason, intro_apr_check has "number" in it even though
                        # it shouldn't
                        if attribute != "intro_apr_check":
                            data_list.append(data.get("number"))
                elif type(data) == str:
                    data_list.append(data)
            except KeyError:  # the given attribute could not be found during the scraping
                # insert "" empty strings in place of the data for the attribute
                if type(example_data) == dict:
                    data_list.append("")
                    data_list.append("")
                else:
                    data_list.append("")
        print(data_list)

        csv_writer.writerow(data_list)

    return "Success"


def convert_csv_voice_responses(data_dict: dict, dest_csv: str=f) -> str:
    """
    Writes the data in data_dict to the dest_csv file. The data is the generated responses from
    phrase_generation/generate_responses.

    Args:
        data_dict (dict): The data to be written.
        dest_csv (str): The destination csv file to output results on.
    Returns:
        str: Success if the write is successful.
    """
    with open(dest_csv, "a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)

        # add all of the term and values into data_list
        data_list = []
        for attribute in attributes_order_voice_responses:
            data = data_dict.get(attribute)
            data_list.append(data)
        print(data_list)

        csv_writer.writerow(data_list)

    return "Success"


def convert_csv_voice_responses_header(dest_csv: str=f) -> str:
    """
    Generates headers for the csv file for voice responses.

    Args
        dest_csv (str): The path to the dest_csv.
    Returns:
        str: Success if the write was successful
    """

    with open(dest_csv, "a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(attributes_order_voice_responses)

    return "Success"

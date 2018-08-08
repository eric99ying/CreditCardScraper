"""
generator.py
~~~~~~~~~~~~~~~~~~~~~
Generates responses based on the scraped and processed data in CreditCardCardRaw table. Uses the
category and company templates.
"""

import re
import copy
import json
import os
import boto3

current_directory = os.path.dirname(os.path.realpath(__file__))
f = os.path.join(current_directory, "category_template.json")
with open(f, "r") as rt:
    category_template = json.load(rt)

f = os.path.join(current_directory, "company_template.json")
with open(f, "r") as rt:
    company_template = json.load(rt)

# gather images from S3
s3 = boto3.client('s3')
s3_response = s3.list_objects(Bucket='static.starbutter.com')

base_url = "https://s3-us-west-2.amazonaws.com/static.starbutter.com/images/card/"
s3_images = []
for k in s3_response['Contents']:
    s3_images.append(k['Key'].replace("images/card/", ""))

# Attributes whose values might contain a "None"
supported_none_case_attributes = [
    "annual_fee",
    "foreign_transaction_fee",
    "minimum_interest_charge_apr",
    "over_limit_fee",
    "penalty_apr",
    "returned_check_fee",
    "returned_payment_fee",
]

# Attributes with no values
non_value_keys = [
    "name",
    "short_card_name",
    "trademark_card_name",
    "offer_link",
    "toc_link",
    "agg_link",
    "issuer",
    "processor",
    "category",
    "redeem",
    "our_take",
    "pros",
    "cons",
    "bonus_offer",
    "rewards_rate"
]

# Attributes with values in the key name
value_keys = {
    "balance_transfer_apr",
    "cash_advance_apr",
    "purchase_apr",
    "penalty_apr",
    "annual_fee",
    "balance_transfer_fee",
    "cash_advance_fee",
    "credit_score",
    "foreign_transaction_fee",
    "late_payment_fee",
    "minimum_interest_charge_apr",
    "over_limit_fee",
    "returned_payment_fee",
    "returned_check_fee",
}

# Attributes with a short appended to the end of the name.
short_keys = {
    "bonus_offer",
    "rewards_rate"
}

category_rank = [
    'cash_back',
    'travel',
    'rewards',
    'balance_transfer',
    'student',
    'secured',
    'business',
    'low_interest',
    'miles',
    'faux_miles',
    'dining',
    'hotel',
    'affinity',
    'military',
    'online_shopping',
    'ethical',
    'credit_union',
    'favorite',
    'service',
    'gas'
]


def generate_responses(full_card_name: str, card_scraped_info: dict, card_score_info: dict,
                       individual_card_info: dict) -> dict:
    """
    Generates responses for a specific card. Returns an output dictionary containing all of the attributes and its
    voice response.

    Args:
        full_card_name (str): The card name.
        card_scraped_info (dict): The scraped and processed info for the credit card pulled from DynamoDB
                                  table called CreditCardCardRaw.
        card_score_info (dict): The card score info pulled from the DynamoDB table called CreditCardCardScore.
        individual_card_info (dict): The individual card info pulled from the DynamoDB table
                                     CreditCardAttrbuteIndividualCard. The attributes from the table must match the
                                     intents in company templates.
    Returns:
        dict: A dictionary of all of the responses for the card.
    """
    output_dict = dict()
    copy_template = copy.deepcopy(category_template)

    print("Generating responses for " + full_card_name)

    # (1) Write values from response template
    for intent, templates in copy_template.items():
        # a. gets the scraped info for a specific card and attribute
        issuer_choice = False
        if intent == 'score_response':
            continue
        try:
            if intent in value_keys:
                value = card_scraped_info[intent + "_value"].strip()
            elif intent in short_keys:
                value = card_scraped_info[intent + "_short"].strip()
            else:
                value = card_scraped_info[intent].strip()
        except KeyError:
            print("Error trying to get the intent {} from card_scraped_info, defaulting to empty string".format(intent))
            value = str()

        # b. gets the voice template depending on the value of the attribute
        if value == "-1" or value == "None":
            # if the terms and conditions does not disclose an attribute, we direct the user to issuer website
            issuer_choice = True
            voice_template_to_use = templates['voice'][1]

        elif value == str() or value.isspace():
            print("Error! {} has a empty string for the attribute {}".format(full_card_name, intent))
            return

        elif intent in supported_none_case_attributes and (value.lower() == "$0" or value.lower() == "0%"):
            voice_template_to_use = templates['voice'][2]

        else:
            voice_template_to_use = templates['voice'][0]

        # c. configures the text response using the voice template and scraped values
        text = __configure_response_for_intent(intent, card_scraped_info, voice_template_to_use, full_card_name)

        # d. store the display text in output dictionary
        output_dict[intent] = text

        # e. get the chips for the intent
        chips = templates.get("chips")

        # f. add "see issuer site" chip if issuer does not disclose an attribute
        if issuer_choice:
            chips.insert(2, "See issuer site")

        # g. add the attribute suggestion chips and follow up questions to the output dictionary
        follow_up_q = templates["followup_question"]
        output_dict[intent + "_chips"] = chips
        output_dict[intent + "_followup_question"] = follow_up_q

    # (2) Write our_take, uses basic cards for Google and Facebook
    # a. generates the our_take string
    our_take_speech = card_scraped_info['our_take'] + ". Ask me what I like about this card?"
    if full_card_name not in card_scraped_info['our_take']:
        our_take_speech = full_card_name + ": " + our_take_speech[0].lower() + our_take_speech[1:]

    # b. store the our take in the output dictionary
    output_dict["our_take"] = our_take_speech

    # (3) Store the image url and the facebook horizontal image url
    image_url = "https://s3-us-west-2.amazonaws.com/static.starbutter.com/images/card/generic+card.jpeg"
    fb_horiz_url = "https://s3-us-west-2.amazonaws.com/static.starbutter.com/images/card/generic+card.jpeg"
    print("Getting images for this card " + full_card_name)
    for k in s3_images:
        if full_card_name.lower().replace("/", "") == k.lower().replace(".jpg", ""):
            image_url = base_url + k.replace(" ", "+")
            fb_horiz_url = base_url + "facebook_horiz/" + k.replace(" ", "+")
            break
    output_dict["image_link"] = image_url
    output_dict["fb_horizontal_link"] = fb_horiz_url

    # (4) Write score
    try:
        final_score = card_score_info["final_score"]
    except KeyError:
        # default score value is "Unknown"
        final_score = "Unknown"
    output_dict['score'] = final_score

    # (5) Write score response
    if final_score != "Unknown":
        score_response = category_template['score_response']['voice'][0].replace("{full_card_name}", full_card_name)\
            .replace("{score}", str(final_score))
    else:
        score_response = category_template['score_response']['voice'][1].replace("{full_card_name}", full_card_name)
    output_dict['score_response'] = score_response
    output_dict['score_response_chips'] = category_template['score_response']["chips"]
    output_dict['score_response_followup_question'] = category_template['score_response']["followup_question"]

    # (6) Writes the issuer phrase to the output dictionary
    company = card_score_info["issuer"]
    issuer_phrase = company_template["name"][0]
    output_dict["issuer_phrase"] = issuer_phrase.replace("{company_name}", company)\
        .replace("{full_card_name}", full_card_name)

    # (7) Write values from company response template
    for intent, templates in company_template.items():
        if intent != "name":
            try:
                # gets the score out of 5 from the score out of 100 (for indexing purposes)
                if intent == "overall_satisfaction":
                    score_100 = int(card_score_info["final_score"])
                else:
                    score_100 = int(card_score_info[intent])
                if score_100 <= 64:
                    score_5 = 0
                elif score_100 <= 74:
                    score_5 = 1
                elif score_100 <= 84:
                    score_5 = 2
                elif score_100 <= 94:
                    score_5 = 3
                else:
                    score_5 = 4
            except KeyError:
                score = 2  # score is average if company score doesn't exist
            text = templates['voice'][score_5].replace("{company_name}", full_card_name)
            follow_up_q = templates["followup_question"]
            chips = templates["chips"][score_5]
            output_dict[intent] = text
            output_dict[intent + "_chips"] = chips
            output_dict[intent + "_followup_question"] = follow_up_q

    # (8) Write similar cards, short card names, trademark card names
    # output_dict['similar_cards'] = __get_similar_cards(card)
    output_dict['short_card_name'] = card_scraped_info["short_card_name"]
    output_dict['trademark_card_name'] = card_scraped_info["trademark_card_name"]
    output_dict['name'] = card_scraped_info["name"]
    output_dict['issuer_name'] = card_scraped_info['issuer']
    output_dict['processor'] = card_scraped_info['processor']
    output_dict['category'] = card_scraped_info['category']
    output_dict['similar_cards'] = __get_similar_cards(card_score_info['similar_cards'])

    # (9) Overrides all phrases with corresponding phrases in CreditCardAttrbuteIndividualCards if they exist.
    # The phrases in CreditCardAttrbuteIndividualCards take priority.
    for key, value in individual_card_info.items():
        if key != "name":
            output_dict[key] = value

    print("OUTPUT DICTIONARY")
    print(output_dict)
    return output_dict


def __configure_response_for_intent(intent: str, scraped_info: dict, template_string: str, full_card_name: str) -> str:
    """
    Given a template string, configures the response using the scraped info.

    Args:
        intent (str): The name of the intent. (ie. balance_transfer_apr)
        scraped_info (dict): The dictionary of card data.
        template_string (str): The template string with the {} for placeholder values.
        full_card_name (str): The full card name
    Returns:
        str: The configured response.

    """
    voice_answer = template_string

    # 1. Find all variables needed for this template
    variables = __process_regex(template_string)

    # 2. Figure out what the variables are
    variable_dict = {"full_card_name": scraped_info["name"]}
    for var in variables:
        if var == "company_name":
            company_name = scraped_info["issuer"]
            variable_dict[var] = company_name
        elif var != "full_card_name":
            if intent in value_keys:
                variable_dict[var] = scraped_info[intent + "_value"]
            elif intent in short_keys:
                variable_dict[var] = scraped_info[intent + "_short"]
            else:
                variable_dict[var] = scraped_info[intent]

    # 3. Replace the variables with actual values
    for var_key, var_found in variable_dict.items():
        update_regex = r"\{" + var_key + r"\}"
        voice_answer = re.sub(update_regex, var_found, voice_answer)

    return voice_answer


def __get_similar_cards(similar_card_string: str) -> list:
    """
    Returns a list of similar cards given the similar card string.

    Args:
        similar_card_string (str): The similar card string. [{'S': 'Bank of America...'}...}
    Returns:
        list: A list of similar cards.
    """
    indices = [m.start(0) for m in re.finditer(r"'", similar_card_string)]
    i = 0
    cards = []
    while i < len(indices):
        start = indices[i] + 1
        end = indices[i + 1]
        substring = similar_card_string[start:end]
        cards.append(substring)
        i += 2
    return [c for c in cards if c != 'S']


def __process_regex(text: str) -> list:
    """
    Given a template string with {} placeholders, use regex to search for all variables in the {} placeholders
    and returns them in a list.

    Args:
        text (str): The template string.
    Returns:
        list: A list of all variables contained within the {} placeholders.
    """
    answer = list()
    regex = r"\{(.*?)\}"
    matches = re.finditer(regex, text)
    for match in matches:
        answer.append(match.group(1))
    return answer






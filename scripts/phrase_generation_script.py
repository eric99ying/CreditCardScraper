"""
phrase_generation_script.py
~~~
Phrase generation script. Builds the phrases and outputs them in a csv file called credit_card_phrases.csv.
"""
import boto3
from phrase_generation.generator import generate_responses
from scripts.convert_csv import convert_csv_voice_responses, convert_csv_voice_responses_header

# initialize dynamoDB tables
db = boto3.resource("dynamodb")
credit_card_table = db.Table("CreditCardCardRaw")
card_score_table = db.Table("CreditCardCardScore")
# the CreditCardAttrbituteIndividualCard table contains phrases that override the generated phrase
card_individual_attribute = db.Table("CreditCardAttrbituteIndividualCard")

all_credit_cards = credit_card_table.scan()["Items"]
all_scores = card_score_table.scan()["Items"]
all_individual_cards = card_individual_attribute.scan()["Items"]

# create the attribute headers for the csv file
convert_csv_voice_responses_header()

for card in all_credit_cards:
    name = card["name"]
    score_info = list(filter(lambda x: x["name"] == name, all_scores))[0]
    individual_card_info = list(filter(lambda x: x["name"] == name, all_individual_cards))
    if len(individual_card_info) == 0:
        individual_card_info = {"name": name}
    output_dict = generate_responses(name, card, score_info, individual_card_info)
    convert_csv_voice_responses(output_dict)

print("Success")


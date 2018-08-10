#CreditCardScraper
Module for scraping aggregator sites and credit card terms and conditions pages. Some of the code is adapted from
the Summer 2017 scraper in database_editor, although the majority of the code has been changed to make compatible with
Python 3 and to utilize DynamoDB tables and spreadsheets instead of Graphs.

Link to full documentation : https://docs.google.com/document/d/1XzJsX_yGMLW3sN-9yhLbUWGrSqKokMOryqzwhn0zq9Y/edit#heading=h.av6y7vamki6y .

________
SCRAPING
--------

For each credit card TOC (terms and condition) link, offer link, and Nerdwallet (if available) link, scrape for the
"full_card_name", "short_card_name", "trademark_card_name", "issuer", "toc_link", "offer_link",
"agg_link", "balance_transfer_apr", "cash_advance_apr", "penalty_apr", "purchase_apr", "paying_interest",
"minimum_interest_charge_apr", "annual_fee", "balance_transfer_fee", "cash_advance_fee", "foreign_transaction_fee",
"late_payment_fee", "returned_payment_fee", "returned_check_fee", "over_limit_fee", "pros", "cons", "credit_score",
"bonus_offer", "offer_details", "reward_rate", "intro_apr_check", "variable_apr_check",  and "annual_fee_check".

For each attribute, the scraper first scrapes for the entire sentence containing the relevant data (ie. 0% for 12 months,
then 23%-45%...). This is stored in a string version of the attribute. (ie. purchase_apr_string)
Afterwards, the scraper will use regular expressions to process the sentence and store only the relevant value
in a separate value version of the attribute. (ie. purchase_apr_value). Finally, we will process the values to extract
single numbers, which are number versions of the attribute. We use the numbers to compare different credit cards.

~~~
Before using the scraper, set the source root to CreditCardScraper.
~~~

Steps to use scraper:

    1) Put all of the credit card names and links in a csv file. The rows in the csv file should follow the format
    (card_name, offer_link, toc_link, agg_link, toc_type). Download the csv file and place it in
    CreditCardScraper/scripts/csv_files. In run_scraping_script.py, update the source_csv to point to the csv file.
    Example file: InputCreditCardsExample.csv

        - The toc_type refers to the type of webpage the terms and conditions are in. It can either be "dynamic"
        (for dynamically JS loaded pages), "pdf" (for pdf), or "regular" (standard html).

    2) If you are scraping dynamically loaded web pages, make sure to download the ChromeDriver and update the
    scrape_using_node function in get_visible_text.py to provide the path to the ChromeDriver.

    3) Run the mass_scrape on the csv file with a specified starting row index (1 in most cases).

    4) All of the scraped info is written onto credit_card_raw_scraped.csv. Import the csv file into Google sheets.

Make sure to double check all of the scraped data in Google sheets. The scraper does not work well at all for
pdf terms and condition pages, so most of the credit cards with pdf terms and conditions would probably be
manually edited.

______________________________
TERM PROCESSING AND EXTRACTION
------------------------------

After all of the scraped data is written onto credit_card_raw_scraped.csv or any other csv file, the script
term_processing_script.py iterates through the csv file (credit_card_raw_scraped.csv) and processes each string
attribute. Another csv file will be written to (credit_card_raw_processed.csv), in which all of the string, values,
and numbers are written.


Steps to process terms:

    1) Download the csv file with the scraped data. Add it to CreditCardScraper/scripts/csv_files. Provide the path
    to the csv file in term_processing_script.py. Make sure the format of the csv file and the attributes are
    in the exact same order as the output of the scraping script (credit_card_raw_scraped.csv).

    2) Update the source_csv variable in term_processing_script to provide the path to the csv file.
    Update the starting index as well (1 in most cases).

    3) Run term_processing_script.

    4) All of the scraped data and extracted values should be outputted in credit_card_raw_processed.csv.
    Import that csv file to Google sheets to view.

Guidelines for the extracted value of each attribute string:

    balance_transfer_fee, cash_advance_fee: The percentage (10%) and the monetary value ($5).

    annual_fee, late_payment_fee, over_limit_fee, returned_payment_fee, returned_check_fee: The highest monetary
                  value encountered in the string.

    paying_interest: The number of days before the payment is due.

    pros, cons: We don't extract anything from the pros and cons string.

    credit_score: The range of credit score values in the format "{low_credit_score} to {high_credit_score}".
                  (ie. "450 to 670")

    bonus_offer, rewards_rate, offer_details: Just some very minor formatting changes. Nothing is extracted.

    intro_apr_check: The percentage APR as well as the number of days it is valid for.

    All of the apr attributes and foreign_transaction_fee: Can be one of the following three cases
                   - A range of percentages (12% to 15%)
                   - A list of three percentages (12$, 14%, or 16%)
                   - A single percentage (12%)


Guidelines for the single number extracted from each attribute value:

    All of the apr attributes and foreign_transaction_fee: The highest percentage.

    balance_transfer_fee, cash_advance_fee: The percentage. (12% or $5 -> 12%)

    annual_fee, late_payment_fee, over_limit_fee, returned_payment_fee, returned_check_fee: The monetary value
            without the $ symbol.

    None of the Nerdwallet attributes have number versions.


Finally, everything (string, value, number) is  written onto a Google sheet called CreditCardCardRaw/CreditCardRawInput.
The Starbutter business team should take a look at the data and look for errors (there will be quit a few). In addition,
the business team will append their own attributes such as our_take, pros, cons, redeem, bonus_offer, and rewards_rate.

_________________
PHRASE GENERATION
-----------------

The phrase_generation_script.py handles generating the actual phrases that CreditCardHelper will serve to users.
The script takes the raw data directly from the DynamoDB table CreditCardCardRaw and CreditCardCardScore to
generate the responses. For every attribute, there is also a chips and followup_question. The templates for these
responses are located in category_template.json and company_template.json in phrase_generation folder.
Phrases that are in CreditCardAttrbuteIndividualCard take priority and override any generated phrase.

Steps to generate phrases:

    1) Make sure the CreditCardCardRaw DynamoDB table exists and all of the attributes are present. For a
    complete list of required attributes, look at the CreditCardCardRaw table in Google sheets.

    2) Run phrase_generation.py. All of the generated phrases should be outputted in
    scripts/csv_files/credit_card_phrases.csv.



Basic pipeline:

InputCreditCardsExample.csv (or any csv file with the same format) ---> run_scraping_script ---> credit_card_raw_scraped.csv
(manually edit to make sure everything is correct, especially for pdf credit cards) ---> term_processing_script.py
---> credit_card_raw_processed.csv ---> CreditCardCardRaw Google sheets (business team will manually edit the table
and append their own attributes such as our_take_value, pros_value ... etc) ---> CreditCardCardRaw DynamoDB table via
CMSv2 ---> phrase_generation.py ---> credit_card_phrases.csv ---> CreditCardCard Google sheets ---> CreditCardCard
DynamoDB table via CMSv2

Important files:

run_scraping_script ----> strings
term_processing_script ----> values and numbers
phrase_generation_script ----> phrases

All files in scrape_to_dict handle the initial scraping.
All files in term_processor handles the value and number extraction.
All files in phrase_generation handle the generation of phrases.

Scores:
50-64 Poor
65-74 Below average
75-84 Average
85-94 Good
95-100 Excellent






   
 

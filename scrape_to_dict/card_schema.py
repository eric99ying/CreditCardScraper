"""
card_schema.py:
~~~
Dictionary skeleton used in scraping process.
"""

# (1) dict with format for scraped info and processed values/numbers
card_dict = {"full_card_name": "",
             "pros": {  # from agg
                 "term": "",  # original value or original text in document
                 "value": ""  # cleaned up value
             },
             "cons": {  # from agg
                 "term": "",
                 "value": ""
             },
             "credit_score": {  # from agg
                 "term": "",
                 "value": "",
                 "low_number": "",
                 "high_number": ""
             },
             "offer_details": {  # from agg
                 "term": "",
                 "value": ""
             },
             "bonus_offer": {  # from agg
                 "term": "",
                 "value": ""
             },
             "rewards_rate": {  # from agg
                 "term": "",
                 "value": ""
             },
             "intro_apr_check": {  # from agg
                 "term": "",
                 "value": ""
             },
             "variable_apr_check": {  # from agg
                 "term": "",
                 "value": ""
             },
             "balance_transfer_apr": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "cash_advance_apr": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "penalty_apr": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "purchase_apr": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "paying_interest": {
                 "term": "",
                 "value": ""
             },
             "tips_apr": {
                 "term": "",
             },
             "termination": {
                 "term": "",
             },
             "plan_fee": {
                 "term": "",
             },
             "minimum_interest_charge_apr": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "annual_fee": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "annual_fee_check": {  # from agg
                 "term": "",
                 "value": ""
             },
             "balance_transfer_fee": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "cash_advance_fee": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "foreign_transaction_fee": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "late_payment_fee": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "returned_payment_fee": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "returned_check_fee": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "over_limit_fee": {
                 "term": "",
                 "value": "",
                 "number": ""
             },
             "toc_link": "",
             "offer_link": "",
             "agg_link": "",
             "short_card_name": "",
             "trademark_card_name": "",
             "issuer": "",
             "processor": "",
             "category": ""
             }

# (2) dicts with aliases for attributes -- ways attributes can be written on terms/conditions page
# this dictionary is used to search for dividing keywords in the terms and conditions page

# (2.1) aliases for interest rates and interest charges (upper table with apr stuff)
upper_table_attribute_mapping_dict = {
    "purchase_apr": ["Annual Percentage Rate (APR) for Purchases", "Annual percentage rates (APR) for purchases",
                     "Purchase Annual Percentage Rate (APR)", "Annual Percentage Rate  (APR) for Purchases",
                     "Annual Percentage Rate (APR) for Purchases and Transfers",
                     "Variable Annual Percentage Rate (APR)"],
    "balance_transfer_apr": ["Annual Percentage Rate (APR) for Balance Transfers", "APR for Balance Transfers",
                             "Balance Transfer APR", "APR for Transfers"],
    "cash_advance_apr": ["APR for Cash Advances", "Cash Advance APR"],
    "penalty_apr": ["Penalty APR and When it Applies", "Penalty APRand When it Applies",
                    "Penalty APR and When  It Applies", "Penalty APR and When It Applies"],
    "paying_interest": ["How to Avoid Paying Finance Charges on Purchases", "How to Avoid Paying Interest on Purchases",
                        "Paying Interest", "Grace Period"],
    "plan_fee": ["Plan Fee (Fixed Finance Charge)", "Plan Fee"],
    "minimum_interest_charge_apr": ["Minimum Interest Charge"],
    "tips_apr": ["For Credit Card Tips from the Consumer Financial Protection Bureau",
                 "Credit Card Tips from the Consumer Financial Protection Bureau"]
}

# (2.2) aliases for fees (lower table)

# (2.2.1) aliases for annual fees (lower table first section)
annual_fees_attribute_mapping_dict = {
    "annual_fee": ["Annual Fee", "Annual Membership Fee"]}

# (2.2.2) aliases for transaction fees (lower table second section)
transaction_fees_attribute_mapping_dict = {
    "balance_transfer_fee": ["Balance Transfers", "Balance Transfer", "Transfer"],
    "cash_advance_fee": ["Cash Advances and Convenience Checks", "Cash Advances", "Cash Advance", "ATM Cash Advance"],
    "foreign_transaction_fee": ["Foreign Transactions", "Foreign Currency Conversion Fee",
                                "Foreign Transaction", "Foreign Purchase Transaction"]
}

# (2.2.3) aliases for penalty fees (lower table third section)
penalty_fees_attribute_mapping_dict = {
    "late_payment_fee": ["Late Payment"],
    "returned_payment_fee": ["Returned Payment", "Return Payment"],
    "returned_check_fee": ["Returned Check", "Return Check"],
    "over_limit_fee": ["Overlimit", "Over-the-Credit-Limit", "Over the limit fee"],
    "termination": ['How We Will Calculate', 'How We Will Calculate Your Balance', 'How we will calculate your balance',
                    'HOW WE WILL CALCULATE YOUR BALANCE', 'How we will calculate',
                    'How we calculate interest', 'Note: This account may not be eligible',
                    'TERMS AND CONDITIONS', 'How Do You Calculate My Balance?', 'For more information or any questions',
                    'Details about your interest rates', 'When applicable', 'TERMS AND CONDITIONS',
                    'Information Regarding the Pay Over Time Feature', 'Details About Your Interest',
                    'Information Regarding the Pay Over Time Feature']
}

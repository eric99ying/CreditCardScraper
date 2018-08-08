"""
dynamodb.py
~~~
Script to transfer credit cards from csv file to dynamodb table CreditCardCardRaw. DO NOT USE. Use CMSv2 instead
to transfer Google sheets to DynamoDB.
"""

import boto3
import csv

dynamodb = boto3.resource('dynamodb')
credit_card_table = dynamodb.Table('CreditCardCardRaw')

source = "csv_files/CreditCardCardRaw - Main.csv"

attribute_titles = []

with open(source, "r", newline='') as csv_file:
    csv_reader = list(csv.reader(csv_file))

    # gets the attribute titles
    first_row = list(csv_reader[0])
    for attribute in first_row:
        attribute_titles.append(attribute)

    print("Finished attribute titles")
    print(attribute_titles)

    for row in csv_reader[1:]:
        key = row[0]
        row = list(row)[1:]

        print("Started transferring " + key)
        p = {}

        for i in range(len(row)):
            p[attribute_titles[1:][i]] = row[i]

        update_string = "set "
        update_values = {}
        j = 1
        for key, item in p.items():
            update_string += (key + " = :val" + str(j) + ", ")
            update_values[":val" + str(j)] = item
            j += 1
        update_string = update_string[:len(update_string) - 1]

        print(update_string)
        print(update_values)

        credit_card_table.update_item(Key={"name": key},
                                      UpdateExpression=update_string,
                                      ExpressionAttributeValues=update_values)



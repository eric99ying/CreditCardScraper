"""
helper_scripts.py
~~~
A bunch of helper scripts not related to scraping at all. Do not use.
"""

import csv


def category_script():
    source = "csv_files/Credit Card Research 2018 - Category.csv"
    dest = "csv_files/category.csv"
    p = {}
    order = []

    with open(source, "r", newline='') as source_file, open(dest, "w", newline='') as dest_file, open(source, "r", newline='') as another_file:
        source_reader = csv.reader(source_file)
        dest_writer = csv.writer(dest_file)
        for row in list(source_reader)[1:]:
            row = list(row)
            order.append(row[0])
            p[row[0]] = []

        print(p)

        source_reader = csv.reader(another_file)
        for row in list(source_reader)[1:]:
            row = list(row)
            print(row[0])

            if row[2]:
                try:
                    p[row[2]].append("low_interest")
                except:
                    pass
            if row[3]:
                try:
                    p[row[3]].append("credit_union")
                except:
                    pass
            if row[4]:
                try:
                    p[row[4]].append("ethical")
                except:
                    pass
            if row[5]:
                try:
                    p[row[5]].append("cash_back")
                except:
                    pass
            if row[6]:
                try:
                    p[row[6]].append("balance_transfer")
                except:
                    pass
            if row[7]:
                try:
                    p[row[7]].append("business")
                except:
                    pass
            if row[8]:
                try:
                    p[row[8]].append("online_shopping")
                except:
                    pass
            if row[9]:
                try:
                    p[row[9]].append("secured")
                except:
                    pass
            if row[10]:
                try:
                    p[row[10]].append("favorite")
                except:
                    pass
            if row[11]:
                try:
                    p[row[11]].append("student")
                except:
                    pass
            if row[12]:
                try:
                    p[row[12]].append("rewards")
                except:
                    pass
            if row[13]:
                try:
                    p[row[13]].append("military")
                except:
                    pass
            if row[14]:
                try:
                    p[row[14]].append("service")
                except:
                    pass
            if row[15]:
                try:
                    p[row[15]].append("travel")
                except:
                    pass
            if row[16]:
                try:
                    p[row[16]].append("affinity")
                except:
                    pass
            if row[17]:
                try:
                    p[row[17]].append("dining")
                except:
                    pass
            if row[18]:
                try:
                    p[row[18]].append("hotel")
                except:
                    pass
            if row[19]:
                try:
                    p[row[19]].append("faux_miles")
                except:
                    pass
            if row[20]:
                try:
                    p[row[20]].append("miles")
                except:
                    pass
            if row[21]:
                try:
                    p[row[21]].append("gas")
                except:
                    pass

        print(p)

        for card in order:
            cat_string = ""
            for e in p[card]:
                cat_string += (e + ", ")
            cat_string = cat_string[:len(cat_string) - 2]
            dest_writer.writerow([cat_string])

    print("Success")
    return "Success"




def attribute_2017_script():
    source = "csv_files/2017 Processed Credit Card Data (from VoiceCard_raw) - Sheet1.csv"
    order = "csv_files/CreditCardCardRaw - Main.csv"
    dest = "csv_files/2017Attributes.csv"
    p = {}
    with open(source, "r", newline='') as source_file:
        source_reader = csv.reader(source_file)
        for row in source_reader:
            row = list(row)
            name = row[0]
            inner = dict()
            inner["similar"] = row[27]
            p[name.lower()] = inner

    with open(order, "r", newline='') as order_file, open(dest, "a", newline='') as dest_file:
        order_reader = csv.reader(order_file)
        dest_writer = csv.writer(dest_file)
        for row in list(order_reader)[1:]:
            row = list(row)
            name = row[0]
            try:
                inner = p[name.lower()]
                dest_writer.writerow([inner["similar"]])
            except KeyError:
                dest_writer.writerow(["--MANUALLY FILL IN--"])

    return "Success"

attribute_2017_script()

def issuer_script():
    source = "csv_files/Credit Card Research 2018 - ComplementaryCards.csv"
    order = "csv_files/CreditCardCardRaw - Main.csv"
    dest = "csv_files/ipc.csv"
    p = {}
    with open(source, "r", newline='') as a:
        b = csv.reader(a)
        for row in b:
            r = list(row)
            name = r[0]
            inner = dict()
            inner["issuer"] = r[3]
            inner["category"] = r[4]
            inner["processor"] = r[2]
            p[name.lower()] = inner

    with open(order, "r", newline='') as a, open(dest, "a", newline='') as c:
        b = csv.reader(a)
        w = csv.writer(c)
        for row in list(b)[1:]:
            r = list(row)
            n = r[0]
            try:
                sn = p[n.lower()]
                w.writerow([sn["issuer"], sn["processor"], sn["category"]])
            except KeyError:
                w.writerow(["--MANUALLY FILL IN--", "--MANUALLY FILL IN--", "--MANUALLY FILL IN--"])

    return "Success"


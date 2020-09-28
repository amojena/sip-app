#!/usr/bin/env python3

import pandas as pd
from test.test_defaultdict import defaultdict
from sodapy import Socrata
from restaurant import Restaurant
from covid import nycHealth

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofnewyork.us", None) # ADD TOKEN FOR FULL ACCESS

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
results = client.get("pitm-atqc")

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)


# useful attributes: name, business address, zip code, sidewalk/roadway seating or both, alcohol available
openRests = defaultdict(list)
for i, row in results_df.iterrows():
    name = row['restaurant_name']
    addr = row['business_address']
    zipcode = int(row['zip'])
    sidewalk = True if row['approved_for_sidewalk_seating'] == "yes" else False
    roadway = True if row['approved_for_roadway_seating'] == "yes" else False
    alcohol = True if row['qualify_alcohol'] == "yes" else False
    restaurant = Restaurant(name, addr, zipcode, sidewalk, roadway, alcohol)
    
    if restaurant.isOpen():
        openRests[zipcode].append(restaurant)

# github COVID data, updated weekly
gitURL = "https://raw.githubusercontent.com/nychealth/coronavirus-data/master/recent/recent-4-week-by-modzcta.csv"
df = pd.read_csv(gitURL, error_bad_lines=False)


# useful features: 
# COVID_CASE_RATE_4WEEK, PCT_CHANGE_2WEEK, TESTING_RATE_4WEEK, PERCENT_POSITIVE_4WEEK

nycHealthStats = dict()
for _, row in df.iterrows():
    zipcode = int(row['MODIFIED_ZCTA'])
    caseRate = float(row['COVID_CASE_RATE_4WEEK'])
    pctChange = float(row['PCT_CHANGE_2WEEK'])/100.0
    testRate = float(row['TESTING_RATE_4WEEK'])
    pctPositive = float(row['PERCENT_POSITIVE_4WEEK'])/100.0

    if zipcode in openRests.keys():
        nycHealthStats[zipcode] = nycHealth(caseRate, pctChange, testRate, pctPositive)




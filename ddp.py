#!/usr/bin/env python3

import pandas as pd
from test.test_defaultdict import defaultdict
from sodapy import Socrata
from restaurant import Restaurant
from covid import nycHealth
from credentials import GetCredentials

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
token, user, pswd = GetCredentials()
client = Socrata("data.cityofnewyork.us", None) # ADD TOKEN FOR FULL ACCESS

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
results = client.get("pitm-atqc")

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)
results_df = results_df.dropna()
# results_df.apply(lambda x: x.astype(str).str.upper())
# print(results_df)
# results_df.drop_duplicates()

# useful attributes: name, business address, zip code, sidewalk/roadway seating or both, alcohol available
openRests = defaultdict(list)
restaurantZipcodes = dict()
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
    
    restaurantZipcodes[name] = zipcode

# github COVID data, updated weekly
gitURL = "https://raw.githubusercontent.com/nychealth/coronavirus-data/master/recent/recent-4-week-by-modzcta.csv"
df = pd.read_csv(gitURL, error_bad_lines=False)
df = df.dropna()

# useful features: 
# COVID_CASE_RATE_4WEEK, PCT_CHANGE_2WEEK, TESTING_RATE_4WEEK, PERCENT_POSITIVE_4WEEK

nycHealthStats = dict()
for _, row in df.iterrows():
    zipcode = int(row['MODIFIED_ZCTA'])
    caseRate = float(row['COVID_CASE_RATE_4WEEK'])
    pctChange = float(row['PCT_CHANGE_2WEEK'])/100.0
    testRate = float(row['TESTING_RATE_4WEEK']) / 100000.0
    pctPositive = float(row['PERCENT_POSITIVE_4WEEK'])/100.0

    if zipcode in openRests.keys() and caseRate and pctChange and testRate and pctPositive:
        nycHealthStats[zipcode] = nycHealth(caseRate, pctChange, testRate, pctPositive)

# for k,v in nycHealthStats.items():
#     print(k, v)

# scenarios 1: user knows name of restaurant, we give covid stats and risk factor
# FAIL!!!!!!!
# restName: input by user
# restName = input("Enter the restaurant name: ")
# if restName in restaurantZipcodes:
#     print(nycHealthStats[restaurantZipcodes[restName]])

# scenario 2: user knows the destination zip code, we provide a list of safe restaurants in the area.
# FAIL!!!!!
# destZipcode = int(input("Enter destination zipcode: "))
# restaurantWithScores = []
# if destZipcode in nycHealthStats:
#     # input preferences here
#     # COVID_CASE_RATE_4WEEK, PCT_CHANGE_2WEEK, TESTING_RATE_4WEEK, PERCENT_POSITIVE_4WEEK
#     print("Please answer the following questions to help us determine the safest zipcode/restaurants")
#     print("1 = Not important, 2 = Somewhat important , 3 = Important")
#     print("Rate the importance of the")
#     pref_caseRate4Week = input("COVID-19 case rate of the last month (1-3): ")
#     pref_pctChange2Week = input("Change in COVID-19 cases in the last 2 weeks (1-3): ")
#     pref_testRate4Week = input("COVID-19 tests done in the last month (1-3): ")
#     pref_positiveRate4Week = input("Rate of COVID positive results in the last month (1-3): ")

#     # score for each restaurant, and store it with it. And then sort descending to get the highest scoring ones first.
#     # top 10 restaurants (iff 10 exist within the zipcode) that satisfy the preference
#     for r in openRests[destZipcode]:
#         score = pref_caseRate4Week * nycHealthStats[destZipcode]
    
#     # need model here

# scenario 3: user provides preferences. based on that, we suggest zip codes and list of restaurants in that area.
# input preferences here
# COVID_CASE_RATE_4WEEK, PCT_CHANGE_2WEEK, TESTING_RATE_4WEEK, PERCENT_POSITIVE_4WEEK
print("Please answer the following questions to help us determine the safest zipcode/restaurants")
print("1 = Not important, 2 = Somewhat important , 3 = Important")
print("Rate the importance of the")
pref_caseRate4Week = int(input("COVID-19 case rate of the last month (1-3): "))
pref_pctChange2Week = int(input("Change in COVID-19 cases in the last 2 weeks (1-3): "))
pref_testRate4Week = int(input("COVID-19 tests done in the last month (1-3): "))
pref_positiveRate4Week = int(input("Rate of COVID positive results in the last month (1-3): "))

# calculate score for each zipcode based preferences and 
# recommend the top 3, along with their restaurants (no particular order)

zip_score = []
for zipcode, stats in nycHealthStats.items():
    score = -1 * pref_caseRate4Week * stats.covid_case_rate_4week
    score += -1 * pref_pctChange2Week * stats.pct_change_2week
    score +=  1 * pref_testRate4Week * stats.test_rate_4week
    score +=  -1 * pref_positiveRate4Week * stats.pct_positive_4week
    zip_score.append((zipcode, score))

zip_score = sorted(zip_score, key=lambda x: x[1], reverse=True)
minzipscore = zip_score[-1][1]
maxzipscore = zip_score[0][1]
normalize = lambda y: round(10*(y-minzipscore)/(maxzipscore-minzipscore),3)
zip_score = [(x, normalize(y)) for x,y in zip_score]
zip_score = sorted(zip_score, key=lambda x: x[1], reverse=True)


# zip_score = list(map(zip_score, lambda score: ((score[1] - minzipscore)/(maxzipscore-minzipscore)) * 10))
print(zip_score[:10])

# # to test, we plot a scatterplot
# import matplotlib.pyplot as plt
# # plt.plot([i for i in range(len(zip_score))], [y for _, y in zip_score])
# plt.plot([x for x,_ in zip_score], [y for _, y in zip_score], 'ob')
# plt.savefig("scores.png")

#  restaurants in the top 3 results 

# for zipcode in zip_score[:3]:
#     print("Zipcode: ", zipcode[0])
#     for rest in openRests[zipcode[0]]:
#         print(rest)
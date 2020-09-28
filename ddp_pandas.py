import pandas as pd
from scipy.sparse.construct import random
from sodapy import Socrata
from restaurant import Restaurant
from covid import nycHealth
from sklearn.cluster import KMeans
from random import seed

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofnewyork.us", None) # ADD TOKEN FOR FULL ACCESS

# First 2000 restaurant_data, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
restaurant_data = client.get("pitm-atqc", limit=15000)

# Convert to pandas DataFrame
wanted_cols = ['restaurant_name', 'borough', 'zip', 'business_address','approved_for_sidewalk_seating', 
'approved_for_roadway_seating', 'qualify_alcohol']
restaurant_df = pd.DataFrame.from_records(restaurant_data)[wanted_cols]
restaurant_df = restaurant_df.dropna()
restaurant_df.apply(lambda x: x.astype(str).str.upper())
restaurant_df = restaurant_df.drop_duplicates()
print(restaurant_df)

seed(42)

# github COVID data, updated weekly
gitURL = "https://raw.githubusercontent.com/nychealth/coronavirus-data/master/recent/recent-4-week-by-modzcta.csv"
covid_df = pd.read_csv(gitURL, error_bad_lines=False)
covid_df = covid_df.dropna()

print(covid_df)

wanted_features = ['COVID_CASE_COUNT_4WEEK', 'COVID_CASE_RATE_4WEEK', 'PCT_CHANGE_2WEEK','TESTING_RATE_4WEEK', 'PERCENT_POSITIVE_4WEEK']
kmeans = KMeans(n_clusters=3).fit(covid_df[wanted_features])

covid_df['RISK'] = kmeans.labels_
print(kmeans.labels_, len(kmeans.labels_))
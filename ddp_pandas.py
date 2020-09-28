import pandas as pd
from scipy.sparse.construct import random
from sodapy import Socrata
from restaurant import Restaurant
from covid import nycHealth
from sklearn.cluster import KMeans
from random import seed
from sklearn import preprocessing

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofnewyork.us", None) # ADD TOKEN FOR FULL ACCESS

# Restaurant_data, returned as JSON from API / converted to Python list of
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

#random seed generator
seed(42)

# github COVID data, updated weekly
gitURL = "https://raw.githubusercontent.com/nychealth/coronavirus-data/master/recent/recent-4-week-by-modzcta.csv"
covid_df = pd.read_csv(gitURL, error_bad_lines=False)
covid_df = covid_df.dropna()

print(covid_df)

wanted_features = ['COVID_CASE_RATE_4WEEK', 'PCT_CHANGE_2WEEK','TESTING_RATE_4WEEK', 'PERCENT_POSITIVE_4WEEK']

# normalize wanted features
min_max_scaler = preprocessing.MinMaxScaler()
covid_df[wanted_features] = min_max_scaler.fit_transform(covid_df[wanted_features])

# upped number of rounds and iterations per round to get more consistent answers
kmeans = KMeans(n_clusters=3, n_init=20, max_iter=500).fit(covid_df[wanted_features])
print(kmeans.labels_, len(kmeans.labels_))
print(kmeans.cluster_centers_)

# format data for csv output
covid_df['RISK'] = kmeans.labels_
output_features = ['MODIFIED_ZCTA', 'NEIGHBORHOOD_NAME'] + wanted_features + ['RISK']
covid_df[output_features].to_csv(path_or_buf="kmeans.csv")
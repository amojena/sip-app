import pandas as pd
from scipy.sparse.construct import random
from sklearn.cluster.k_means_ import _kmeans_single_elkan
from sodapy import Socrata
from restaurant import Restaurant
from covid import nycHealth
from sklearn.cluster import KMeans
from random import seed
from sklearn import preprocessing
import numpy as np
from test.test_defaultdict import defaultdict
from operator import itemgetter
import matplotlib.pyplot as plt
import folium
from folium.map import Popup
from folium.plugins import MarkerCluster

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofnewyork.us", None) # ADD TOKEN FOR FULL ACCESS

# Restaurant_data, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
restaurant_data = client.get("pitm-atqc", limit=15000)

# Convert to pandas DataFrame
wanted_cols = ['restaurant_name', 'borough', 'zip', 'business_address','approved_for_sidewalk_seating', 
'approved_for_roadway_seating', 'qualify_alcohol', 'longitude', 'latitude']
restaurant_df = pd.DataFrame.from_records(restaurant_data)[wanted_cols]
restaurant_df = restaurant_df.dropna()
restaurant_df.apply(lambda x: x.astype(str).str.upper())
restaurant_df = restaurant_df.drop_duplicates()

restaurantPerZip = defaultdict(list)
for i, row in restaurant_df.iterrows():
    name = row['restaurant_name']
    addr = row['business_address']
    zipcode = int(row['zip'])
    sidewalk = True if row['approved_for_sidewalk_seating'] == "yes" else False
    roadway = True if row['approved_for_roadway_seating'] == "yes" else False
    alcohol = True if row['qualify_alcohol'] == "yes" else False
    longitude, latitude = float(row['longitude']), float(row['latitude'])

    restaurant = Restaurant(name, addr, zipcode, sidewalk, roadway, alcohol, longitude, latitude)
    
    if restaurant.isOpen() and row['borough'] == "Manhattan":
        restaurantPerZip[zipcode].append(restaurant)

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
kmeans = KMeans(n_clusters=3, n_init=20, max_iter=400).fit(covid_df[wanted_features])
print(kmeans.labels_, len(kmeans.labels_))
print(kmeans.cluster_centers_)

kmeans_label_custom = dict()
# print(np.argmax(kmeans.cluster_centers_[:][2]), max(kmeans.cluster_centers_[:][2]))
# print(max(map(lambda x: x[2], kmeans.cluster_centers_)))
# print(min(map(lambda x: x[3], kmeans.cluster_centers_)))


# relabels the kmeans cluster label outputs to Low, Medium, and High
# we detect which cluster might be low by calc max of testing rate and min of pct_positive
# likewise, we detect high risk cluster by calc max of pct_positive

def max_value(l, index):
    return max(enumerate(x[index] for x in l), key=itemgetter(1))
def min_value(l, index):
    return min(enumerate(x[index] for x in l), key=itemgetter(1))

if max_value(kmeans.cluster_centers_, 2)[0] == min_value(kmeans.cluster_centers_, 3)[0]:
    kmeans_label_custom["LOW"] = max_value(kmeans.cluster_centers_, 2)[0]

kmeans_label_custom["HIGH"] = max_value(kmeans.cluster_centers_, 3)[0]
for i in range(3):
    if i not in kmeans_label_custom.values():
        kmeans_label_custom["MEDIUM"] = i

    
# format data for csv output
covid_df['RISK'] = kmeans.labels_
output_features = ['MODIFIED_ZCTA', 'NEIGHBORHOOD_NAME'] + wanted_features + ['RISK']
covid_df[output_features].to_csv(path_or_buf="kmeans.csv")

lowRestaurants = []
midRestaurants = []
highRestaurants = []

for _, row in covid_df[['MODIFIED_ZCTA', 'RISK']].iterrows():
    
    risk = row['RISK']
    zipcode = row['MODIFIED_ZCTA']

    if kmeans_label_custom["LOW"] == risk:
        lowRestaurants.extend(restaurantPerZip[zipcode])
    elif kmeans_label_custom["MEDIUM"] == risk:
        midRestaurants.extend(restaurantPerZip[zipcode])
    if kmeans_label_custom["HIGH"] == risk:
        highRestaurants.extend(restaurantPerZip[zipcode])


low_risk_icon_create_function = '''
    function(cluster) {
            var count = cluster.getChildCount();
            return L.divIcon({html: '<div><span>' + count + '</span></div>',
                              className: 'marker-cluster-small',
                              iconSize: new L.Point(40, 40)});
    }'''

mid_risk_icon_create_function = '''
    function(cluster) {
            var count = cluster.getChildCount();
            return L.divIcon({html: '<div><span>' + count + '</span></div>',
                              className: 'marker-cluster-medium',
                              iconSize: new L.Point(40, 40)});
    }'''

high_risk_icon_create_function = '''
    function(cluster) {
            var count = cluster.getChildCount();
            return L.divIcon({html: '<div><span>' + count + '</span></div>',
                              className: 'marker-cluster-large',
                              iconSize: new L.Point(40, 40)});
    }'''


centralParkCoords = (40.7812, -73.9665)
m = folium.Map(location=centralParkCoords, prefer_canvas=True)
low_layer = folium.FeatureGroup()
low_markercluster = MarkerCluster(icon_create_function=low_risk_icon_create_function).add_to(low_layer)
plt.title('Low')
x, y = [], []
for r in lowRestaurants:
    x += [r.longitude]
    y += [r.latitude]
    folium.Marker(location=(y[-1], x[-1]), popup=r.name, icon=folium.Icon(color='green')).add_to(low_markercluster)

plt.plot(x,y, 'og')

med_layer = folium.FeatureGroup()
med_markercluster = MarkerCluster(icon_create_function=mid_risk_icon_create_function).add_to(med_layer)
x, y = [], []
for r in midRestaurants:
    x += [r.longitude]
    y += [r.latitude]
    folium.Marker(location=(y[-1], x[-1]), popup=r.name, icon=folium.Icon(color='orange')).add_to(med_markercluster)

plt.plot(x,y, 'oy')

high_layer = folium.FeatureGroup()
high_markercluster = MarkerCluster(icon_create_function=high_risk_icon_create_function).add_to(high_layer)
x, y = [], []
for r in highRestaurants:
    x += [r.longitude]
    y += [r.latitude]
    folium.Marker(location=(y[-1], x[-1]), popup=r.name, icon=folium.Icon(color='red')).add_to(high_markercluster)

low_layer.add_to(m)
med_layer.add_to(m)
high_layer.add_to(m)

folium.LayerControl().add_to(m)

plt.plot(x, y, 'or')
plt.legend(['Low', 'Mid', 'High'])


m.save('map.html')




plt.savefig('scatter.png')






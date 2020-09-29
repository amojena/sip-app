# Safe In Place (SIP)

New York City now offers outdoor dining on the sidewalk / roadway, changes made due to COVID.

However, we don't really know how safe it is to eat outside. 

## SIP to the rescue!

SIP helps you decide which restaurants are safe to dine out with lower risk of exposure to COVID.

## How we do it

Following are the 2 data sources used:
* [Open Restaurant applications](https://data.cityofnewyork.us/Transportation/Open-Restaurant-Applications/pitm-atqc) to get a list of restaurants that are permitted to offer outdoor dining.
* [Recent Case Data by Zip Code](https://www1.nyc.gov/site/doh/covid/covid-19-data-recent.page) to get each neighborhood's weekly case rate over the past four weeks. **(Unlabeled data)**

Type: Unsupervised learning  
Model used: K-means clustering  

Performed K-means clustering to cluster COVID risk areas into LOW, MEDIUM, and HIGH risk.  
The restaurants are displayed on a map with a color coded risk profile (LOW = green, MEDIUM = orange, HIGH = red)

Find out more [here](https://docs.google.com/presentation/d/1MCzlYl0kCjre2dH0zbQYXR2yP4r4n9uzX5xizaXcv-A/edit?usp=sharing).


## Demo

[![alt text](https://img.youtube.com/vi/-cpzVMiw7d8/0.jpg)](https://www.youtube.com/watch?v=-cpzVMiw7d8)

This project is a collaboration with [Antonio Mojena](https://github.com/amojena), [Chinmay Bhat](https://github.com/chinmay-bhat), Shreya Chandrasekar and Bharat Dev Gandhi, developed for the [Designing Data Products](https://classes.cornell.edu/browse/roster/FA20/class/NBAY/6170) course at Cornell taught by Prof Lutz Finger.

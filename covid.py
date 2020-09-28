# COVID_CASE_RATE_4WEEK, PCT_CHANGE_2WEEK, TESTING_RATE_4WEEK, PERCENT_POSITIVE_4WEEK

class nycHealth:
    def __init__(self, covid_case_rate_4week, pct_change_2week, test_rate_4week, pct_positive_4week):
        self.covid_case_rate_4week = covid_case_rate_4week
        self.pct_change_2week = pct_change_2week
        self.test_rate_4week = test_rate_4week
        self.pct_positive_4week = pct_positive_4week
    
    def __str__(self):
        return "{}, {}, {}, {}".format(self.covid_case_rate_4week, self.pct_change_2week, 
                                    self.test_rate_4week, self.pct_positive_4week)
    
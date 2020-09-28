class Restaurant:
    def __init__(self, name, addr, zipcode, sidewalk, roadway, alcohol, longitude, latitude):
        self.name = name
        self.addr = addr
        self.zipcode = zipcode
        self.sidewalk = sidewalk
        self.roadway = roadway
        self.alcohol = alcohol
        self.longitude = longitude
        self.latitude = latitude
    
    def isOpen(self):
        return self.sidewalk or self.roadway
    
    def __str__(self):
        return "{}, {} {}".format(self.name, self.addr, self.zipcode)

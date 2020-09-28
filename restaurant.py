class Restaurant:
    def __init__(self, name, addr, zipcode, sidewalk, roadway, alcohol):
        self.name = name
        self.addr = addr
        self.zipcode = zipcode
        self.sidewalk = sidewalk
        self.roadway = roadway
        self.alcohol = alcohol
    
    def isOpen(self):
        return self.sidewalk or self.roadway
    
    def __str__(self):
        return "{}, {} {}".format(self.name, self.addr, self.zipcode)

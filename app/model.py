from app import my_db as db
from mongoengine.queryset.visitor import Q


class Package(db.Document):
    meta = {"collection" : "packages"}
    hotel_name = db.StringField(max_length=30)
    duration = db.IntField()
    unit_cost = db.FloatField()
    image_url = db.StringField(max_length=30)
    description = db.StringField(max_length=500)

    @property
    def packageCost(self):
        return self.unit_cost * self.duration
    
    @staticmethod
    def getPackage(hotel_name):
        return Package.objects(hotel_name=hotel_name).first()
    
    @staticmethod
    def getAllPackages():
        return Package.objects()
    
    @staticmethod
    def getPackageFromPrice(low, high):
        return Package.objects(Q(unit_cost__gte=low) & Q(unit_cost__lte=high))

    @staticmethod
    def createPackage(hotel_name, duration, unit_cost, image_url, description):
        return Package(hotel_name=hotel_name, duration=duration, unit_cost=unit_cost, image_url=image_url, description=description).save()

class Promotion(db.Document):
    meta = {'collection': "promotion"}
    check_in = db.DateTimeField()
    check_out = db.DateTimeField()
    capacity = db.IntField()

    @staticmethod
    def createPromotion(check_in, check_out, capacity):
        return Promotion(check_in=check_in, check_out=check_out, capacity=capacity).save()
    

class PromotionPackage(db.Document):
    meta = {"collection": "promotionpackage"}
    package = db.ReferenceField(Package)
    promotion = db.ListField(db.ReferenceField(Promotion))
    discount = db.FloatField()
    hotel_name = db.StringField()

    @staticmethod
    def getAllPackages():
        return PromotionPackage.objects()
    
    @staticmethod
    def getPackage(hotel_name):
        return PromotionPackage.objects(hotel_name=hotel_name).first()
    
    @staticmethod
    def createPackages(package, promotion, discount, hotel_name):
        return PromotionPackage(package=package, promotion=promotion, discount=discount, hotel_name=hotel_name).save()



from django.test import TestCase
# from .models import Address, Village, Town, State, Country

# class ModelTestCase(TestCase):

#     def setUp(self):
#         india = Country.objects.create(name='India')
#         telangana = State.objects.create(name="Telangana", country=india)
#         pitlam = Town.objects.create(name="Pitlam", state=telangana)
#         kurthi = Village.objects.create(name="Kurthi", town=pitlam)
#         school_address = Address.objects.create(street="School",village=kurthi)
    
#     def test_address(self):
#         school_address = Address.objects.get(street="School")
#         self.assertEqual(school_address.street,"School")
#         self.assertEqual(school_address.village.name,"Kurthi")
#         self.assertEqual(school_address.village.town.name,"Pitlam")
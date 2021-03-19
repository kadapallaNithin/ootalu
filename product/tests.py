from django.test import TestCase
from .models import Product, ServerKey
from home.models import Address, Village, Town, State, Country
from django.contrib.auth.models import User

class ModelTestCase(TestCase):
    def setUp(self):
        india = Country.objects.create(name='India')
        telangana = State.objects.create(name="Telangana", country=india)
        pitlam = Town.objects.create(name="Pitlam", state=telangana)
        kurthi = Village.objects.create(name="Kurthi", town=pitlam)
        school_address = Address.objects.create(street="School",village=kurthi)

        u1 = User.objects.create(username="nithin")
        p1 = Product.objects.create(owner=u1, name="nithin's product", address=school_address,count_per_unit=200)

    def test_address_of_product(self):
        p = Product.objects.first()
        school_address = Address.objects.first()
        self.assertEqual(p.address,school_address)

    def test_server_key_signal(self):
        s = ServerKey.objects.first()
        p = Product.objects.first()
        self.assertEqual(s.product,p)
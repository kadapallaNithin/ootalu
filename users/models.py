from django.db import models
from django.contrib.auth.models import User
from home.models import Address
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pic = models.ImageField(default='default.png', upload_to='profile_pics')
    address = models.ForeignKey(Address,on_delete=models.SET_NULL,null=True)
    def __str__(self):
        return f'{self.id} Profile'

    def save(self,**kwargs):
        super().save()

        img = Image.open(self.pic.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.pic.path)
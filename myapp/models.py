
# from django.db import models

# class Profile(models.Model):
#     name = models.CharField(max_length=100)
#     age = models.IntegerField()
#     email = models.EmailField()
#     bio = models.TextField()

#     def __str__(self):
#         return self.name
# Create your models here.

from django.db import models

class Profile(models.Model):
     name = models.CharField(max_length=100)
     age = models.IntegerField()
     job = models.CharField(max_length=100)
     couple = models.CharField(max_length=100)
     email = models.EmailField()
     bio = models.TextField()
     image = models.ImageField(upload_to='profile_pics/', default='default.jpg')
     def __str__(self):
         return self.name



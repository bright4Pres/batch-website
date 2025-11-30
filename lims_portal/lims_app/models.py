from django.db import models

# Create your models here.
sectionChoice = (
    ("Einstein", "Einstein"),
    ("Tesla", "Tesla"),
    ("Curie", "Curie")
)

class scholarList(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=5000)
    section = models.CharField(max_length=50, choices=sectionChoice)
    image = models.ImageField(upload_to='food_pic')

class commenter(models.Model):
    username = models.CharField(max_length=50)
    comment = models.CharField(max_length=50)
    targetScholar = models.CharField(max_length=50)

    def __str__(self):
        return self.username
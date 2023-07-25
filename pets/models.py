from django.db import models


class Pet_Sex(models.TextChoices):
    Male = "Male"
    Female = "Female"
    NOT_INFORMED = "Not Informed"

class Pet(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    sex = models.CharField(max_length=20, choices=Pet_Sex.choices, default=Pet_Sex.NOT_INFORMED, null=True)

    group = models.ForeignKey(
        "groups.Group", on_delete=models.PROTECT, related_name="pets"
    )

    traits = models.ManyToManyField(
        "traits.Trait", related_name="pets"
    )

    

from django.db import models
from django.contrib.auth.models import User

   
class Utilizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Defrag_Process(models.Model):
    user = models.ForeignKey(Utilizador, on_delete=models.CASCADE)
    generated_file_name = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    initial_simulation = models.CharField(max_length=200, null=True)
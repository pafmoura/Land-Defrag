from django.db import models
from django.contrib.auth.models import User

   
class Defrag_Process(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_file_name = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    file_path = models.CharField(max_length=200, null=True, blank=True)

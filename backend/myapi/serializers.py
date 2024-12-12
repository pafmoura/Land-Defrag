from myapi.models import Defrag_Process
from rest_framework import serializers

class Defrag_Process_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Defrag_Process
        fields = (
            "is_completed",
            "generated_file_name",
            "initial_simulation",
        )
# serializers.py

from rest_framework import serializers

class TimeTrackSerializer(serializers.Serializer):
    resource = serializers.CharField(max_length=255)
    date = serializers.DateField()
    projects = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

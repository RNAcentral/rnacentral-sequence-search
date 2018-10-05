from rest_framework import serializers
from django.conf import settings

from .models import Job, JobChunk


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


# class SubmitJobSerializer(serializers.Serializer):
#     query = serializers.CharField()
#     databases = serializers.ListField(child=serializers.ChoiceField(choices=settings.DATABASE_CHOICES))


class JobChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobChunk
        fields = ('job_id', 'database', 'result')

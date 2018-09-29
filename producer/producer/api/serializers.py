from rest_framework.serializers import ModelSerializer

from models import Job, JobChunk, Database


class JobSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


class JobChunkSerializer(ModelSerializer):
    class Meta:
        model = JobChunk
        fields = '__all__'

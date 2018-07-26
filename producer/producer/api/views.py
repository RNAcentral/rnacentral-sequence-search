# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from kafka import KafkaProducer

from serializers import JobSerializer


class SubmitJob(APIView):
    def post(self, request, format=None):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
            # produce keyed messages to enable hashed partitioning
            producer.send(settings.KAFKA_TOPICS['tRNA'], key=b'foo', value=b'bar')

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

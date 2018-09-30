# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Job
from .serializers import JobSerializer, JobChunkSerializer


class SubmitJob(APIView):
    def post(self, request, format=None):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            for database in request.data["databases"]:
                requests.post(
                    url=settings.CONSUMERS[database],
                    data={"job_id": request.data['job_id'], "sequence": request.data['sequence']}
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobDone(APIView):
    def post(self, request, format=None):
        serializer = JobChunkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class JobStatus(APIView):
    def get(self, request, job_id, format=None):
        job = Job.objects.get(id=job_id).select_related("job_chunk")
        serializer = JobSerializer(instance=job)
        return Response(serializer.data, status=status.HTTP_200_OK)

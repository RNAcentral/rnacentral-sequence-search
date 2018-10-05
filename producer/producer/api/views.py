# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import requests

from django.conf import settings
from rest_framework import views, viewsets, mixins, response, reverse, permissions, status

from .models import Job
from .serializers import JobSerializer, JobChunkSerializer


class APIRoot(views.APIView):
    """This is the root of the sequence search API."""
    # the above docstring appears on the API website
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=format):
        return response.Response({
            'submit-job': reverse.reverse('submit-job', request=request),
            'job-status': reverse.reverse('job-status', request=request),
        })


class SubmitJob(views.APIView):
    """To run a sequence search job, post it to this endpoint."""
    def post(self, request, format=None):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            for database in request.data["databases"]:
                requests.post(
                    url="http://" + settings.CONSUMERS[database] + '/' + settings.CONSUMER_SUBMIT_JOB_URL,
                    data=json.dumps({"job_id": instance.id, "sequence": instance.query, "database": database})
                )

            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobDone(views.APIView):
    """
    When consumer is done running nhmmer job,
    it posts results of respective job chunk to this endpoint.
    """
    def post(self, request, format=None):
        serializer = JobChunkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)


class JobStatusViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """Viewset that lists all jobs that were ever started."""
    serializer_class = JobSerializer
    lookup_field = 'job_id'

    def get_queryset(self):
        return Job.objects.all().order_by('-submitted')

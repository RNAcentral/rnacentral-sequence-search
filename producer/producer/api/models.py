# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


class Job(models.Model):
    STATUS_CHOICES = (
        ('started', 'started'),
        ('success', 'success'),
        ('failed', 'failed'),
    )

    id = models.AutoField(primary_key=True)
    query = models.TextField()
    databases = ArrayField(models.CharField(max_length=255, choices=settings.DATABASE_CHOICES))
    submitted = models.DateTimeField(default=timezone.now)
    finished = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='started')


class JobChunk(models.Model):
    """Part of the search job, run against a specific database and assigned to a specific consumer"""
    STATUS_CHOICES = (
        ('started', 'started'),
        ('success', 'success'),
        ('failed', 'failed'),
    )

    job_id = models.ForeignKey(Job, related_name="job_chunk")
    database = models.CharField(max_length=255, choices=settings.DATABASE_CHOICES)
    result = models.TextField(null=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='started')

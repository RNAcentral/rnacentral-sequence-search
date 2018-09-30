# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Job(models.Model):
    STATUS_CHOICES = (
        ('started', 'started'),
        ('success', 'success'),
        ('failed', 'failed'),
    )

    id = models.CharField(max_length=36, primary_key=True)
    query = models.TextField()
    submitted = models.DateTimeField(null=True)
    finished = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='started')


class Database(models.Model):
    name = models.CharField(max_length=36, primary_key=True)
    ip = models.CharField(max_length=15)


class JobChunk(models.Model):
    """Part of the search job, run against a specific database and assigned to a specific consumer"""
    STATUS_CHOICES = (
        ('started', 'started'),
        ('success', 'success'),
        ('failed', 'failed'),
    )

    database = models.ForeignKey(Database, related_name="job_chunk")
    job = models.ForeignKey(Job, related_name="job_chunk")
    result = models.TextField(null=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='started')

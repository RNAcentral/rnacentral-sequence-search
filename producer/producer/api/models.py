# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Job(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    query = models.TextField()
    submitted = models.DateTimeField(null=True)
    finished = models.DateTimeField(null=True, blank=True)

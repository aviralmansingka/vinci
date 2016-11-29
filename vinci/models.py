from __future__ import unicode_literals

from datetime import datetime
from django.db import models

# Create your models here.
class User(models.Model):
    """
    Storing individual users of the application.
    """

    uid = models.IntegerField()
    name = models.CharField(max_length=30)

    def __str__(self):
        return "%s: %s" % (self.uid, self.name)

class Message(models.Model):
    """
    Responsible for storing all of the users messages.
    """

    content = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    confidence = models.FloatField()
    intent = models.CharField(max_length=30)
    date = models.DateTimeField(default=datetime.now(), blank=True)

    def __str__(self):
        return "User: %s, Message: %s, Intent: %s, Confidence: %s" % (self.user, self.content, self.intent, self.confidence)

class Image(models.Model):
    """
    Every entry holds one user submitted image
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    filepath = models.ImageField(upload_to='images/')
    width = models.IntegerField()
    height = models.IntegerField()
    date = models.DateTimeField(default=datetime.now(), blank=True)

    def __str__(self):
        return "User: %s, Upload Path: %s" % (self.user, self.filepath,)

class Filter(models.Model):
    """
    Storing the locations of all filters in our application
    """

    name = models.CharField(max_length=30)
    url = models.ImageField(upload_to='images/')
    path = models.FileField(upload_to='filters/')
    counter = models.IntegerField(default=0);

    def __str__(self):
        return "Name: %s, URL: %s" % (self.name, self.url,)

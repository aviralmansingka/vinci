from __future__ import unicode_literals

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

    def __str__(self):
        return "User: %s, Message: %s, Intent: %s, Confidence: %s" % (self.user, self.content, self.intent, self.confidence)

class Image(models.Model):
    """
    Every entry holds one user submitted image
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    is_landscape = models.BooleanField(default=True)

    def __init__(self):
        url = models.ImageField(upload_to="./images/%s" % (Image.user.uid,))

    def __str__(self):
        return "User: %s, Upload Path: %s, URL: %s, Is Landscape: %s" % (self.user, self.upload_path, self.url, self.is_landscape,)

class Filter(models.Model):
    """
    Storing the locations of all filters in our application
    """

    name = models.CharField(max_length=30)
    url = models.ImageField(upload_to='./filters')

    def __str__(self):
        return "Name: %s, URL: %s" % (name, url,)


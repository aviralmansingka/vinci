import json, requests, subprocess, urllib
from pprint import pprint

from django.http import HttpResponse
from django.views import generic

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from PIL import Image as Img
from datetime import datetime

from . import models
from . import secrets
from .nlp import recast as nlp
from .rendering import evaluate as dl


SITE_URL=secrets.SITE_URL
VALIDATION_TOKEN = secrets.VALIDATION_TOKEN
ACCESS_TOKEN=secrets.ACCESS_TOKEN


class FacebookHandler(object):

    def send_message(self, fbid, received_message):

        send_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % ACCESS_TOKEN
        response_msg = json.dumps({"recipient": {"id":fbid}, "message":{"text":received_message}})

        status = requests.post(send_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

    def send_filters(self, fbid):

        filters = models.Filter.objects.all()

        send_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % ACCESS_TOKEN

        elements = []

        for fil in filters:

            url = "%s/%s" % (SITE_URL, fil.url.url)
            print "URL: %s" % url

            mydict = {
                    "title":fil.name,
                    "image_url":url,
                    "buttons":[
                        {
                            "type":"postback",
                            "title":"Pick me!",
                            "payload":fil.name
                            }
                        ]
                    }
            elements.append(mydict)


        response_to_send = {
                "recipient" :   {"id":str(fbid)},
                "message":{
                    "attachment":{
                        "type":"template",
                        "payload":{
                            "template_type":"generic",
                            "elements":elements
                            }
                        }
                    }
                }

        response_msg = json.dumps(response_to_send)

        status = requests.post(send_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

    def send_image(self, fbid, url):

        send_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % ACCESS_TOKEN
        response_to_send = {
                "recipient":{
                    "id":fbid
                    },
                "message":{
                    "attachment":{
                        "type":"image",
                        "payload":{
                            "url": url
                            }
                        }
                    }
                }

        response_msg = json.dumps(response_to_send)

        status = requests.post(send_message_url, headers={"Content-Type": "application/json"}, data=response_msg)



class IndexView(generic.View):
    def get(self, request, *args, **kwargs):
        """
        Returns a simple message of the index page
        """
        return HttpResponse("Hello World! You're at the vinci index")


class VinciView(generic.View):
    """
    The main webhook for our application. All messages are routed through here
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        """
        The main GET route for our webhook
        """
        if self.request.GET['hub.verify_token'] == VALIDATION_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])

        else:
            return HttpResponse("Error with request")


    def post(self, request, *args, **kwargs):
        """
        The main POST route for our webhook.
        Every single message enters here and is dispatched accordingly.
        """

        incoming_message = json.loads(self.request.body.decode('utf-8'))

        for entry in incoming_message['entry']:

            for message in entry['messaging']:

                if 'postback' in message:

                    self.postback_handler(message)

                elif 'text' in message['message']:

                    self.message_handler(message)

                elif 'attachments' in message['message']:

                    self.image_handler(message)


        return HttpResponse()

    def message_handler(self, message):
        """
        This method deals with handling all text messages sent by the user.
        It handles NLP, dispatching, and data entry.
        """

        fbid = message['sender']['id']

        try:
            text = message['message']['text']
        except KeyError:
            text = "hello"


        """
        TEXT PROCESSING CODE
        Parses text and returns intent. Handles everything based on that
        """
        nlp_handler = nlp.Recast()

        intent, intent_type, confidence = nlp_handler.understand_intent(text)
        pprint("Intent is: %s" % (intent,))
        pprint("Intent Types: %s" % (intent_type,))


        """
        DATABASE CODE
        This code will add a user if he does not exist, and save his message
        """
        user = models.User.objects.filter(uid=fbid)

        if user.count() <= 0:

            user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
            user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':ACCESS_TOKEN}
            user_details = requests.get(user_details_url, user_details_params).json()

            name = "%s %s" % (user_details['first_name'], user_details['last_name'])

            user = models.User(uid=fbid, name=name)
            user.save()

            print "\nReceived Text: \"%s\" from %s (new user)\n" % (text, user.name)

        else:

            user = user[0]

            print "\nReceived Text: \"%s\" from %s\n" % (text, user.name)

        if intent is not None:
            m = models.Message(user=user, content=text, confidence=confidence, intent=intent)
            m.save()

        """
        DISPATCH CODE
        Dispatches the calls to the various functions required to respond to a user
        """
        dispatch = FacebookHandler()

        if intent is None:
            dispatch.send_message(fbid, "Sorry I could not understand you")


        if intent_type == 'text':

            response = nlp_handler.parse_response_from_intent(intent)

            dispatch.send_message(fbid, response)


        elif intent_type == 'image':

            dispatch.send_filters(fbid)


    def postback_handler(self, message):
        """
        This method is responsible for dealing with when a user selects a filter.
        """

        fbid = message['sender']['id']
        payload = message['postback']['payload']

        print "Payload is %s" % payload

        dispatch = FacebookHandler()

        if payload == "get_started":

            dispatch.send_message(fbid, "Hey there! My name's Vinci, but maybe you can call me Leo ;-). Say hi to me or send me an image and see what happens")
            return


        text = "Okay! You've selected the filter \"%s\"" % payload

        dispatch.send_message(fbid, text)

        user = models.User.objects.filter(uid=fbid)
        user = user[0]

        print "\nRecevied postback from: %s selecting filter: %s\n" % (user.name, payload)

        image = user.image_set.all()

        fil = models.Filter.objects.filter(name=payload)
        fil = fil[0]
        print "Initial filter counter is %d" % fil.counter

        """
        Increasing the count of the selected filter and saving in DATABASE
        """

        fil.counter = fil.counter + 1;
        fil.save();

        print "Updated filter counter is %d" % fil.counter

        """
        End
        """

        if image and (DateTime.Now - image[0]).TotalDays < 1:

            image = image[0]

            dispatch.send_message(fbid, "We are now drawing your image by hand, scanning it, and sending it to you.")

            out_file = "%d.jpg" % user.uid
            img_out = models.Image(user=user, filepath=out_file)
            img_in  = models.Image(user=user, filepath="in_%s" % out_file)
            url = "%s%s" % (SITE_URL, img_out.filepath.url)

            image_size = (image.width, image.height)

            dl.render(img_in.filepath.path, img_out.filepath.path, fil.path.path)

            dispatch.send_image(fbid, url)

            dispatch.send_message(fbid, "We hope you liked it! You can simply select from the filters above if you plan on using the same image!")

        else:

            text = "You don't appear to have sent us an image yet. Do you want to send us one?"

            dispatch.send_message(fbid, text)


    def image_handler(self, message):
        """
        This method is responsible for dealing with images that the user bestows upon us
        """

        fbid = message['sender']['id']

        image_url = message['message']['attachments'][0]['payload']['url']
        pprint(image_url)

        user = models.User.objects.filter(uid=fbid)

        if user.count() <= 0:

            user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
            user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':ACCESS_TOKEN}
            user_details = requests.get(user_details_url, user_details_params).json()

            name = "%s %s" % (user_details['first_name'], user_details['last_name'])

            user = models.User(uid=fbid, name=name)
            user.save()

            print "\nReceived Image from %s (new user)\n" % (user.name)

        else:

            user = user[0]

            print "\nReceived Image from from %s\n" % (user.name)

        out_file="%d.jpg" % user.uid
        in_file = "in_%s" % out_file

        pprint(in_file)

        if user.image_set.all():
            user.image_set.all().delete()

        img_db = models.Image(user=user, filepath=in_file)

        urllib.urlretrieve(image_url, img_db.filepath.path)

        img = Img.open(img_db.filepath.path)

        img_db.width, img_db.height = img.size
        img_db.save()

        dispatch = FacebookHandler()

        dispatch.send_message(fbid, "Okay we have updated your image. Please select a filter again!")
        dispatch.send_filters(fbid)

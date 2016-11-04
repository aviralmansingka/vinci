import json, requests, subprocess
from pprint import pprint

from django.http import HttpResponse
from django.views import generic

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .nlp import recast as nlp
from . import models

# Create your views here.

SITE_URL='http://0cef449d.ngrok.io/'
VALIDATION_TOKEN = "vinci"
ACCESS_TOKEN='EAADGJe1gDtQBAMld6JsYUVC9s1UPvFpePXPQDzDoQGhPZCmJhmeRioZCGZAIF6i3Is1or5AhcGzASx88SUD7Q0AP0GmTrWGzi1mL2UAhpSDYyOiGNfGrZAAo0ZAFtQzxdZA8cbqlfh10InP3TrA528AJKF33dZAbZCOWKVQTdSvPSQZDZD'

class FacebookHandler(object):

    def send_message(self, fbid, received_message):

        send_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % ACCESS_TOKEN
        response_msg = json.dumps({"recipient": {"id":fbid}, "message":{"text":received_message}})

        status = requests.post(send_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

    def send_filters(self, fbid):

        fil = models.Filter.objects.get(pk=1)

        send_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % ACCESS_TOKEN
        url = "%s/%s" % (SITE_URL, fil.url.url)
        pprint("URL: %s" % url)
        response_to_send = {
                "recipient" :   {"id":str(fbid)},
                "message":{
                    "attachment":{
                        "type":"template",
                        "payload":{
                            "template_type":"generic",
                            "elements":[
                                {
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
                                ]
                            }
                        }
                    }
                }

        response_msg = json.dumps(response_to_send)
        pprint(response_to_send)

        status = requests.post(send_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
        pprint(status.content)


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

                if 'message' in message:

                    self.message_handler(message)

                elif 'postback' in message:

                    self.postback_handler(message)


        return HttpResponse()

    def message_handler(self, message):
        """
        This method deals with handling all text messages sent by the user.
        It handles NLP, dispatching, and data entry.
        """

        fbid = message['sender']['id']
        text = message['message']['text']


        """
        TEXT PROCESSING CODE
        Parses text and returns intent. Handles everything based on that
        """
        nlp_handler = nlp.Recast()

        intent, intent_type, confidence = nlp_handler.understand_intent(text)
        pprint("Intent is: %s" % (intent,))
        pprint("Intent Types: %s" % (intent_type,))


        """
        DISPATCH CODE
        Dispatches the calls to the various functions required to respond to a user
        """
        dispatch = FacebookHandler()
        if intent_type == 'text':

            response = nlp_handler.parse_response_from_intent(intent)

            dispatch.send_message(fbid, response)

        elif intent_type == 'image':

            dispatch.send_filters(fbid)


        """
        DATABASE CODE
        This code will add a user if he does not exist, and save his message
        """
        user = models.User.objects.filter(uid=fbid)
        user = user[0]

        if not user:
            user = models.User(uid=fbid)
            user.save()
        else:
            pprint("We have a user for this id")

        user.message_set.create(content=text, intent=intent, confidence=confidence)


    def postback_handler(self, message):
        """
        This method is responsible for dealing with when a user selects a filter.
        """

        fbid = message['sender']['id']
        payload = message['postback']['payload']

        text = "Okay! You've selected the filter \"%s\"" % payload

        dispatch = FacebookHandler()

        dispatch.send_message(fbid, text)

        user = models.User.objects.filter(uid=fbid)
        user = user[0]

        image = user.image_set.all()

        if not image:

            text = "You don't appear to have sent us an image yet. Do you want to send us one?"

            dispatch.send_message(fbid, text)

        else:

            text = "Due to the lack of skill on part of my creator, we are going to have to proceed with using your latest submission. Please wait while your image renders."

            dispatch.send_message(fbid, text)



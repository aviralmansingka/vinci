import json, requests
from pprint import pprint

from django.http import HttpResponse
from django.views import generic

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .nlp import recast as nlp
# Create your views here.

VALIDATION_TOKEN = "vinci"

def post_facebook_message(fbid, received_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAADGJe1gDtQBAMld6JsYUVC9s1UPvFpePXPQDzDoQGhPZCmJhmeRioZCGZAIF6i3Is1or5AhcGzASx88SUD7Q0AP0GmTrWGzi1mL2UAhpSDYyOiGNfGrZAAo0ZAFtQzxdZA8cbqlfh10InP3TrA528AJKF33dZAbZCOWKVQTdSvPSQZDZD'
    response_msg = json.dumps({"recipient": {"id":fbid}, "message":{"text":received_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

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

        if self.request.GET['hub.verify_token'] == VALIDATION_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])

        else:
            return HttpResponse("Error with request")


    def post(self, request, *args, **kwargs):

        incoming_message = json.loads(self.request.body.decode('utf-8'))

        for entry in incoming_message['entry']:

            for message in entry['messaging']:

                if 'message' in message:
                    pprint(message)

                    fbid = message['sender']['id']
                    text = message['message']['text']

                    nlp_handler = nlp.Recast()

                    intent, intent_type = nlp_handler.understand_intent(text)
                    pprint("Intent is: %s" % (intent,))
                    pprint("Intent Types: %s" % (intent_type,))

                    if intent_type == 'text':

                        response = nlp_handler.parse_response_from_intent(intent)

                        post_facebook_message(fbid, response)

                    elif intent_type == 'image':

                        pprint("I'm supposed to send an image here I guess")

        return HttpResponse()

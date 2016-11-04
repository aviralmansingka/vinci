import recastai
from pprint import pprint

RECAST_ACCESS_TOKEN = '95bed182f2b541ccefc1084bd76826bb'
LANG = 'en'


class Recast(object):
    """
    An object responsible for all recast related functionality
    """

    POSSIBLE_RESPONSE = {
        'greeting': 'Hi! I\'m Vinci. Really nice to meet you',
        'goodbyes': 'See you later! Stay tuned for updates',
    }

    INTENT_TYPE = {
        'greeting': 'text',
        'goodbyes': 'text',
        'showfilters': 'image',
    }

    def __init__(self):
        self.client = recastai.Client(RECAST_ACCESS_TOKEN, LANG)

    def understand_intent(self, text):
        """
        Takes as input text and return the intent.
        """

        response = self.client.text_request(text)

        pprint(response.intent())

        if response.intent() is not None:
            return response.intent().slug, Recast.INTENT_TYPE[response.intent().slug], response.intent().confidence
        else:
            return None, None, None

    def parse_response_from_intent(self, intent):
        """
        Takes as input the users' intent and return a response
        """
        try:
            return Recast.POSSIBLE_RESPONSE[intent]
        except KeyError:
            return "Sorry. Unfortunately I couldn't understand you!"


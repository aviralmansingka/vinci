from random import randint
import json
from .. import models
""" 
The class generates auto random replies,
when the user intent is identified as a greeting
or a goodbye. Replies for help intent coming up!
"""

class Replies():

  # A list of replies when the user intent is identified as greetings
  greetings = [
      "Hi! I'm Vinci, really nice to meet you!",
      "Hey! My name is Vinci, and I am your personal Artist!",
      "Hi There! Welcome to Vinci, hope you are doing well.",
      "Hey! This is Vinci, hope you're having a wonderful day!",
      "Hello! My name is Vinci, it's a pleasure to meet you!"
      ]

  # A list of replies when the user intent is identified as goodbyes		
  goodbyes = [
      "See you later! Stay tuned for new updates.", 
      "Bye! Stay tuned for new updates", 
      "Hope you enjoyed! Stay tuned for new updates",
      "Bye, take care! Do come back to check out new updates",
      "Later! Waiting to hear back from you"
      ]

  # help_message =  "As your Personal Artist, I can be used the following ways\nSee the range of artworks I have available by typing, for instance \'show filters\' or,\nYou may send me a picture on which you want the artwork to be applied on, then select a filter of your choice and then experience the piece of exclusive modern artwork created for you."
  help_message='Help'
  
  
  """	A function that generates an integer to index the lists.
    Parameters: None
    Return: a random integer
  """
  def generateIndex(self):
    return (randint(0,4))

  """	A function that generates a reply for the greeting intent
    Parameters: list greetings, int random_index 
    Return: prints an appropriate greeting
  """
  def generateGreeting(self, greetings, random_index):
      return greetings[random_index] + " Wanna see me in action? Ask for some filters or send me an image!"

  """	A function that generates a reply for the goodbyes intent
    Parameters: list greetings, int random_index 
    Return: prints an appropriate goodbye
  """
  def generateGoodbye(self, goodbyes, random_index):
    return goodbyes[random_index]

  def recommendFilter(self):
    
    filters = models.Filter.objects.all()

    maxFilter = filters[0]

    for fil in filters:
      if fil.counter > maxFilter.counter:
        maxFilter = fil
    
    return maxFilter.name    


  def handle_intent(self, intent):
    rand_index = self.generateIndex()


    if intent == 'greetings':
      return self.generateGreeting(self.greetings, rand_index)
    elif intent == 'goodbyes':
      return self.generateGoodbye(self.goodbyes, rand_index)
    elif intent == 'help-intent':
      return self.help_message
    elif intent == 'recommend':
      return self.recommendFilter()
    else:
      return "Didn't quite get that. Try greetings or goodbyes"

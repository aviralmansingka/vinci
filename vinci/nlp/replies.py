from random import randint
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
		return greetings[random_index]

	"""	A function that generates a reply for the goodbyes intent
		Parameters: list greetings, int random_index 
		Return: prints an appropriate goodbye
	"""
	def generateGoodbye(self, goodbyes, random_index):
		return goodbyes[random_index]


	def handle_intent(self, intent):
		rand_index = self.generateIndex()

		if intent == 'greetings':
			return self.generateGreeting(self.greetings, rand_index)
		elif intent == 'goodbyes':
			return self.generateGoodbye(self.goodbyes, rand_index)
		else:
			return "Didn't quite get that. Try greetings or goodbyes"

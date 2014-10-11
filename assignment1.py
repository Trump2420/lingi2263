import re

class RecipeParser():

	#Time related
	Seconds_Key_Words = set(["second", "sec", "s"])
	Minutes_Key_Words = set(["minute", "min", "m"])
	Hours_Key_Words = set(["hour", "h"])

	Time_Key_Words = Seconds_Key_Words | Minutes_Key_Words | Hours_Key_Words

	Preparation_Words = set(["stir", "prep time", "preparation time", "preptime", "preparationtime", "shake", "beat", "whisk", "roll"])
	Other_Cooking_Time_Related_Words = set(["bake", "sit", "chill", "total time", "cool", "stand", "freeze", "rest", "refrigerate", "cook"])

	#Servings
	Serving_Words = set(["serving", "serve"])

	#Quantity

	#We could add g and l, t
	Quantity_Words = set(["clove", "zest", "ounce", "cup", "teaspoon", "tsp", "tea spoon", "slice", "tablespoon", "table spoon", "spoon",
							"gram", "kg", "kilo", "mg", "mili", "ml", "liter", "jar", "can", "oz", "scoop"])

	End_Sentence_Regex = r'[^!?\n<\.]*'
	Time_Regex = r'\b([0-9]+|an|a)( *)\b({})[s]?\b'.format("|".join(Time_Key_Words))
	Cooking_Time_Regex = r'\b({})(.*)({})({})'.format("|".join(Other_Cooking_Time_Related_Words), Time_Regex, End_Sentence_Regex)
	Preparation_Time_Regex = r'({})(.*)'.format("|".join(Preparation_Words))
	Ingredient_Regex = r'([0-9]+/[0-9]+|[0-9]+)[ *]({})([s]?[\.]?)( *)([\w() ]*)(,|{})'.format("|".join(Quantity_Words), End_Sentence_Regex)
	#Watch out!!!! -> The number may be in another sentence	
	Servings_Regex = r'[0-9]+\b( *)({})[s]?({})?|serve[s]? *:?;? *[0-9]+'.format("|".join(Serving_Words), End_Sentence_Regex)

	def findIngredients(self, textLine):
		matches = re.finditer(self.Ingredient_Regex, textLine, re.IGNORECASE)

		if matches:
			ingredientName = 5
			quantityUnit = 2
			ingredientQuantity = 1
			return [(match.group(ingredientName), match.group(ingredientQuantity), match.group(quantityUnit)) for match in matches]

	def findServings(self, textLine):
		matches = re.search(self.Servings_Regex, textLine, re.IGNORECASE)
		if matches:
			sentence = matches.group()
			return self._findNumberInSentence(sentence)

	def _findNumberInSentence(self, sentence):
		matches = re.search(r'[0-9]+', sentence)
		if matches:
			return matches.group()

	def findPreparationTime(self, textLine):
		return self._findActionTime(textLine, self.Preparation_Time_Regex)

	def findCookingTime(self, textLine):
		return self._findActionTime(textLine, self.Cooking_Time_Regex)

	def _findActionTime(self, textLine, actionsTimeRegex):
		matches = re.search(actionsTimeRegex, textLine, re.IGNORECASE)
		
		if matches:
			sentence = matches.group()
			times = self.findTime(sentence)
			return times

	def findTime(self, sentence):
		# Can't find a time range (ex: 8-10, will found only 10)
		matches = re.search(self.Time_Regex, sentence, re.IGNORECASE)
		if matches:
			number = matches.group(1)
			unit = matches.group(3)
			return (number, unit)

	def stripSpan(self, line):
		return re.sub(r"</?span.*?>", "", line)

class RecipeExtractor():

	parser = RecipeParser()

	def extractRecipe(self, filePath):
		servings = None
		preparationTime = (None, None)

		with open(filePath, "r") as myfile:
			for line in myfile:
				line = self.parser.stripSpan(line)
				#If more than one serving is detected, the previous one is overided
				servingsFound = self.parser.findServings(line)
				preparationTimeFound = self.parser.findPreparationTime(line)
				if preparationTimeFound:
					preparationTime = self.addTime(preparationTime, preparationTimeFound)
				if servingsFound:
					servings = servingsFound

		recipe = "prep_time {} {}\nnb_servings {}".format(preparationTime[0], preparationTime[1], servings)

		return recipe

	def addTime(self, time1, time2):
		t1 = 0
		t2 = 0

		if time1[0]:
			t1 = self._ConvertToMinutes(time1)
		if time2[0]:
			t2 = self._ConvertToMinutes(time2)

		return t1 + t2, "min."

	def _ConvertToMinutes(self, time):
		t = int(time[0])
		if time[1] in RecipeParser.Seconds_Key_Words:
			t = time[0] / 60
		elif time[1] in RecipeParser.Hours_Key_Words:
			t = time[0] * 60
		return t

if __name__ == "__main__":
	recipeExtractor = RecipeExtractor()

	print(recipeExtractor.extractRecipe("recipe_book/main-dish_130.html"))
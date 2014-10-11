import re

class RecipeParser():

	#Time related
	Seconds_Key_Words = set(["second", "sec", "s"])
	Minutes_Key_Words = set(["minute", "min", "m"])
	Hours_Key_Words = set(["hour", "h"])

	Time_Key_Words = Seconds_Key_Words | Minutes_Key_Words | Hours_Key_Words

	Preparation_Words = set(["stir", "prep time", "preparation time", "preptime", "preparationtime", "shake", "beat", "whisk", "roll"])
	Total_Time_Words = set(["total time", "total_time", "totaltime"])
	Other_Cooking_Time_Related_Words = set(["bake", "sit", "chill", "cool", "stand", "freeze", "rest", "refrigerate", "cook", "boil", "grill"])

	#Servings
	Serving_Words = set(["serving", "serve", "portion", "portions for", "portion for"])

	#Quantity

	#We could add g and l, t
	Quantity_Words = set(["clove", "zest", "ounce", "cup", "teaspoon", "tsp", "tea spoon", "slice", "tablespoon", "table spoon", "spoon",
							"gram", "kg", "kilo", "mg", "ml", "liter", "jar", "can", "oz", "scoop", "stick", "miligram", "mililiter"])

	End_Sentence_Regex = r'[^!?\n<\.]*'
	Time_Regex = r'\b([0-9]+|an|a)( *)\b({})[s]?\b'.format("|".join(Time_Key_Words))
	Cooking_Time_Regex = r'\b({})(.*)({})({})'.format("|".join(Other_Cooking_Time_Related_Words), Time_Regex, End_Sentence_Regex)
	Preparation_Time_Regex = r'({})(.*)'.format("|".join(Preparation_Words))
	Total_Time_Regex = r'({})(.*)'.format("|".join(Total_Time_Words))
	Ingredient_Regex = r'([0-9]+/[0-9]+|[0-9]+)[ *]({})([s]?[\.]?)( *)(\(.*\))? *([-\w() ]*)(,|{})'.format("|".join(Quantity_Words), End_Sentence_Regex)
	#Watch out!!!! -> The number may be in another sentence
	Servings_Regex = r'[0-9]+\b( *)({})[s]?({})?|({})[s]? *:?;? *[0-9]+'.format("|".join(Serving_Words), End_Sentence_Regex, "|".join(Serving_Words))

	def findTotalTime(self, textLine):
		return self._findActionTime(textLine, self.Total_Time_Regex)

	def findIngredients(self, textLine):
		matches = re.finditer(self.Ingredient_Regex, textLine, re.IGNORECASE)
		if matches:
			ingredientName = 6
			quantityUnit = 2
			ingredientQuantity = 1
			return set([(match.group(ingredientName), match.group(ingredientQuantity), match.group(quantityUnit)) for match in matches if match.group(ingredientName)])

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
			if "a" in number:
				number = "1"
			unit = matches.group(3)
			return (number, unit)

	def stripSpan(self, line):
		return re.sub(r"</?span.*?>", "", line)

class RecipeExtractor():

	Conversion_Table = {"clove":("clove", 1),
						 "zest":("zest", 1), 
						 "ounce":("gram", 28.3495),
						 "cup":("ml", 236.588),
						 "teaspoon":("ml", 4.98),
						 "tsp":("ml", 4.98),
						 "tea spoon":("ml", 4.98),
					     "slice":("slice", 1),
						 "tablespoon":("ml", 14.79), 
						 "table spoon":("ml", 14.79),
						 "spoon":("ml", 14.79),
						 "gram":("gram", 1),
					     "kg":("kg", 1),
						 "kilo":("kg", 1),
						 "mg":("mg", 1),
					     "miligram":("mg", 1),
					     "mililiter":("ml", 1),
						 "ml":("ml", 1),
						 "liter":("l", 1),
					     "jar":("ml", 500), #approx. (Mason jar)
						 "can":("ml", 354.9),
						 "oz":("ml", 29.57),
						 "scoop":("ml", 70), #approx.
						 "stick":("stick", 1)}

	parser = RecipeParser()

	def extractRecipe(self, filePath):
		servings = None
		preparationTime = (None, None)
		cookingTime = (None, None)
		totalTime = (None, None)
		ingredients = set()

		with open(filePath, "r") as myfile:
			for line in myfile:
				line = self.parser.stripSpan(line)
				#If more than one serving is detected, the previous one is overiden
				servingsFound = self.parser.findServings(line)
				preparationTimeFound = self.parser.findPreparationTime(line)
				cookingTimeFound = self.parser.findCookingTime(line)
				totalTimeFound = self.parser.findTotalTime(line)
				ingredientsFound = self.parser.findIngredients(line)

				if ingredientsFound:
					ingredients |= ingredientsFound
				if cookingTimeFound:
					cookingTime = self.addTime(cookingTime, cookingTimeFound)
				if totalTimeFound:
					totalTime = (self._ConvertToMinutes(totalTimeFound), "min")
				if preparationTimeFound:
					preparationTime = self.addTime(preparationTime, preparationTimeFound)
				if servingsFound:
					servings = servingsFound

		if not totalTime[0] and preparationTime[0]:
			totalTime = self.addTime(cookingTime, preparationTime)

		recipesIngredients = " ".join([ingredient[0] for ingredient in ingredients])
		recipesIngredientsOrigQuantity = " ".join([ingredient[1] for ingredient in ingredients])
		recipesIngredientsOrigUnit = " ".join([ingredient[2] for ingredient in ingredients])

		recipesIngredientsMetricQuantity = " ".join([str(self.convertToMetric(ingredient)[1]) for ingredient in ingredients])
		recipesIngredientsMetricUnit = " ".join([self.convertToMetric(ingredient)[2] for ingredient in ingredients])
		
		recipe = "ingredients {}\norig_quantity {}\norig_unit {}\nmetric_qunatity {}\nmetric_unit {}\nnb_servings {}\nprep_time {} {}\ntotal_time {} {}".format(
			recipesIngredients, recipesIngredientsOrigQuantity, recipesIngredientsOrigUnit, recipesIngredientsMetricQuantity, recipesIngredientsMetricUnit,
			servings, preparationTime[0], preparationTime[1], totalTime[0], totalTime[1])

		return recipe

	def convertToMetric(self, ingredient):
		if ingredient[2].lower() in self.Conversion_Table:
			return (ingredient[0], eval(ingredient[1])*self.Conversion_Table[ingredient[2].lower()][1], self.Conversion_Table[ingredient[2].lower()][0])
		else:
			return ingredient

	def addTime(self, time1, time2):
		t1 = 0
		t2 = 0

		if time1[0]:
			t1 = self._ConvertToMinutes(time1)
		if time2[0]:
			t2 = self._ConvertToMinutes(time2)

		return t1 + t2, "min"

	def _ConvertToMinutes(self, time):
		t = int(time[0])
		if time[1] in RecipeParser.Seconds_Key_Words:
			t = t / 60
		elif time[1] in RecipeParser.Hours_Key_Words:
			t = t * 60
		return t

if __name__ == "__main__":
	import sys

	recipeExtractor = RecipeExtractor()
	if(len(sys.argv) == 3):
		recipe = recipeExtractor.extractRecipe(sys.argv[1])
		with open(argv[2], "w") as output:
			output.write(recipe)
	else:
		print("Expected format: digest_recipe.py input_file.txt output_file.txt")
import re

#Time related
Time_Key_Words = set(["second", "sec", "s", "minute", "min", "m", "hour", "h"])
Preparation_Words = set(["stir", "prep time", "preparation time", "preptime", "preparationtime", "shake", "beat", "whisk", "roll"])
Other_Cooking_Time_Related_Words = set(["bake", "sit", "chill", "total time"])

#Servings
Serving_Words = set(["serving"])

#Quantity

#We could add g and l, t
Quantity_Words = set(["clove", "zest", "ounce", "cup", "teaspoon", "tsp", "tea spoon", "slice", "tablespoon", "table spoon", "spoon",
						"gram", "kg", "kilo", "mg", "mili", "ml", "liter", "jar", "can", "oz"])

End_Sentence_Regex = r'[^!?\n<\.]*'
Time_Regex = r'\b([0-9]+|an|a)( *)\b({})[s]?\b'.format("|".join(Time_Key_Words))
Cooking_Time_Regex = r'\b({})(.*)({})({})'.format("|".join(Other_Cooking_Time_Related_Words), Time_Regex, End_Sentence_Regex)
Preparation_Time_Regex = r'({})(.*)'.format("|".join(Preparation_Words))
Ingredient_Regex = r'([0-9]+/[0-9]+|[0-9]+)[ *]({})([s]?[\.]?)( *)([\w() ]*)(,|{})'.format("|".join(Quantity_Words), End_Sentence_Regex)
#Watch out!!!! -> The number may be in another sentence	
Servings_Regex = r'[0-9]+(.*)({})[s]?\b(.*)({})'.format("|".join(Serving_Words), End_Sentence_Regex)

def findIngredients(textLine):
	matches = re.finditer(Ingredient_Regex, textLine, re.IGNORECASE)

	if matches:
		ingredientName = 5
		quantityUnit = 2
		ingredientQuantity = 1
		return [(match.group(ingredientName), match.group(ingredientQuantity), match.group(quantityUnit)) for match in matches]

def findServings(textLine):
	matches = re.search(Servings_Regex, textLine)

	if matches:
		sentence = matches.group()
		return _findNumberInSentence(sentence)

def _findNumberInSentence(sentence):
	matches = re.search(r'[0-9]+', sentence)
	if matches:
		return matches.group()

def findPreparationTime(textLine):
	return _findActionTime(textLine, Preparation_Time_Regex)

def findCookingTime(textLine):
	return _findActionTime(textLine, Cooking_Time_Regex)

def _findActionTime(textLine, actionsTimeRegex):
	matches = re.search(actionsTimeRegex, textLine, re.IGNORECASE)
	
	if matches:
		sentence = matches.group()
		times = findTime(sentence)
		return times

def findTime(sentence):
	# Can't find a time range (ex: 8-10, will found only 10)
	matches = re.search(Time_Regex, sentence, re.IGNORECASE)
	if matches:
		number = matches.group(1)
		unit = matches.group(3)
		return (number, unit)

def stripHTML(line):
	return re.sub(r"<[^>]*>", "", line)	

with open("recipe_book/main-dish_266.html", "r") as myfile:
	for line in myfile:
		#line = stripHTML(line)
		time = findIngredients(line)
		if time:
			print(time)
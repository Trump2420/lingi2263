import re

Time_Key_Words = set(["second", "sec", "s", "minute", "min", "m", "hour", "h"])
Actions_Words = set(["bake"])


End_Sentence_Regex = r'[^!?\n<\.]*'
Time_Regex = r'\b([0-9]+)( *)\b({})[s]?\b'.format("|".join(Time_Key_Words))
Cooking_Time_Regex = r'\b({})(.*)({})({})'.format("|".join(Actions_Words), Time_Regex, End_Sentence_Regex)


def findCookingTime(textLine):
	matches = re.search(Cooking_Time_Regex, textLine, re.IGNORECASE)
	
	if matches:
		sentence = matches.group()
		times = findTime(sentence)
		return times

def findTime(sentence):
	matches = re.search(Time_Regex, sentence, re.IGNORECASE)
	if matches:
		return matches.group()

with open ("recipe_book/dessert_204.html", "r") as myfile:
	for line in myfile:
		time = findCookingTime(line)
		if time:
			print(findCookingTime(line))
# import required module
import os
import json
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy
from spacy.matcher import Matcher


# assign directory
directory = "dataset_1"

#spacy models
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

entity1 = []
entity2 = []
entities3 = []

def main():
	
	global entity1
	global entity2
	global entities3
	out_json = []
	counter = 0

	for filename in os.listdir(directory):
		counter +=1
		p = os.path.join(directory, filename)
		with open(p, "r") as fin:
			print(filename)
			data = json.load(fin)
			#find abstract
			paper_id = data["paper_id"]
			paper_title = data["title"]
			abstract = data['pdf_parse']['abstract']
			body = data['pdf_parse']['body_text']
			body = abstract + body
			#nltk sent tokenize

			#global sentence counter ID

			sent_id = 0
			# deal with abstract
			# deal with every text in body_text

			for item in body:
				section = item["section"]
				tokens = nlp(item["text"])
				for sent in tokens.sents:
					
					doc = nlp(sent.text)
					sent_id +=1

					entity1 = {		"name": "achievement",
						"mentions": []# mention: (surface_form, start_position_in_tokens, end_position_in_tokens)
						}
					entity2 = {		"name": "self-concept",
						"mentions": []# mention: (surface_form, start_position_in_tokens, end_position_in_tokens)
						}
					entities3 = create_ent3_dict_list()
					#print(str(sent), sent_idx)
					#use spacy tokenize
					tokens = []
					for token in doc:
						tokens.append(token.text)
					tags = [w.tag_ for w in doc]
					#callbacks in the matches automatically add the found items to the arrays
					matches = matcher(doc)
					#print(entity1)
					#print(entity2)
					#print(entities3)
					# output
					#if either is not empty
					if  entity1["mentions"] and entity2["mentions"]:	
						entities3 = prune_ent3_dict_list(entities3)

						out_item = {
							"paper_id" : paper_id,
							"title" : paper_title,
							"sentence_id" : sent_id,
							"section" : section,
							"text" : sent.text,
							"tokens": tokens,
							"tags" : tags,
							"entity1": entity1,
							"entity2": entity2,
							"entities3": entities3,
						}

						out_json.append(out_item)
		#if counter > 5:
		#	break
				
		
	#write output json to file
	out_filename = "step1_output_concept.json"
	with open(out_filename, "w") as fout:
		json.dump(out_json, fout)




def add_ent1(matcher, doc, i, matches):
	match_id, start, end = matches[i]
	string_id = nlp.vocab.strings[match_id]  # Get string representation
	span = doc[start:end]  # The matched span
	#print( (span.text, start, end))
	if "grade" in span.text.lower():
		start +=1
		end -= 1
		span = doc[start:end]			
	entity1["mentions"].append((span.text, start, end) )

def add_ent2(matcher, doc, i, matches):

	match_id, start, end = matches[i]
	string_id = nlp.vocab.strings[match_id]  # Get string representation
	span = doc[start:end]  # The matched span
	#print( (span.text, start, end))
	entity2["mentions"].append( (span.text, start, end) )


def add_ent_3(matcher, doc, i, matches):
	match_id, start, end = matches[i]
	string_id = nlp.vocab.strings[match_id]  # Get string representation
	span = doc[start:end]  # The matched span
	#match from string ID to correct item in entities 3
	for group in entities3:
		for item in group["values"]:
				if item["name"] == string_id:
					item["mentions"].append( (span.text, start, end) )				
					break

#lists for country, schoolyear
subjects = ["maths", "verbal", "history"]
genders = ["female", "male", "enby"]
countries = ["germany", "china", "usa", "canada", "france", "uk", "japan", "korea", "belgium", "croatia", "estonia", "finland", "italy", "netherlands", "thailand", "australia", "israel", "new zealand"]
races = ["asian", "black", "latin", "white"]
school_years = ["first_grade", "second_grade", "third_grade", "fourth_grade", "fifth_grade", "sixth_grade", "seventh_grade", "eighth_grade"]
#list comprehensions

def create_ent3_dict_list():
	entities3= [
		{
		"name": "subject",
		"values": [ {"name": subject, "mentions":[]} for subject in subjects]
		}, 
		{
		"name": "country",
		"values": [ {"name": country, "mentions":[]} for country in countries]
		},
				{
		"name": "schoolyear",
		"values": [ {"name": year, "mentions":[]} for year in school_years]
		}, 
				{
		"name": "gender",
		"values": [ {"name": gender, "mentions":[]} for gender in genders]
		}, 
				{
		"name": "race",
		"values": [ {"name": race, "mentions":[]} for race in races]		
		},  
	]

	entities3
	return entities3

#remove empty items
def prune_ent3_dict_list(ent3):
	for group in ent3:
		group['values'] = [item for item in group['values'] if item['mentions']]
	
	ent3 = [item for item in ent3 if item['values']]
	return ent3


#ENTITY1
schoolyears = ["first","second","third","fourth","fifth","sixth","seventh","eighth","ninth", "tenth", "eleventh", "twelvth", "-", 
				"1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"]

# entities 1: patterns and callbacks to add to output.json
ent1patterns = [
	[{"LOWER": {"REGEX": "achievements?"}}],  
	[{"LOWER": {"REGEX": "GPAs?"}}],
	[ {"LOWER": {"IN": schoolyears } , "OP":"!",  },{"LOWER": {"REGEX": "grades?"}}, {"POS": "NUM", "OP":"!"}]
	]

matcher.add("Achievement", ent1patterns,  on_match=add_ent1)

# ENTITY2
ent2patterns = [
	[{"LOWER": "self"}, {"IS_PUNCT": True, "OP":"?"} ,{"LOWER": {"REGEX": "concepts?"}}] ,
	[{"LOWER": "self"}, {"IS_PUNCT": True, "OP":"?"} ,{"LOWER": {"REGEX": "perceptions?"}}] ,
	[{"LOWER": {"REGEX": "SCs?"}} ]
	]
matcher.add("self-concept", ent2patterns, on_match=add_ent2)

# SUBJECTS
mathspatterns = [
	[{"LOWER": {"REGEX": "maths?"}}]
	]
matcher.add("maths", mathspatterns, on_match=add_ent_3 )


historypatterns = [
	[{"LOWER": {"REGEX": "history"}}]
	]
matcher.add("history", historypatterns, on_match=add_ent_3 )

verbalpatterns = [
	[{"LOWER": "verbal"}],
	[{"LOWER": "language"}]
	]
matcher.add("verbal", verbalpatterns, on_match=add_ent_3)

#COUNTRIES
germanpatterns = [
	[{"LOWER": {"REGEX": "germany?"}}]
	]
matcher.add("germany", germanpatterns, on_match=add_ent_3)

koreanpatterns = [
	[{"LOWER": {"REGEX": "korean?"}}]
	]
matcher.add("korea", koreanpatterns, on_match=add_ent_3)


japanpatterns = [
	[{"LOWER": {"REGEX": "japan"}}]
	]
matcher.add("japan", japanpatterns, on_match=add_ent_3)

chinapatterns = [
	[{"LOWER": "china"}],
	[{"LOWER": "chinese"}]
	]
matcher.add("china", chinapatterns, on_match=add_ent_3)

usapatterns = [
	[{"LOWER": "usa"}],
	[{"LOWER": "united states"}]
	]
matcher.add("usa", usapatterns, on_match=add_ent_3)


canadapatterns = [
	[{"LOWER": "canada"}],
	[{"LOWER": "canadian"}]
	]
matcher.add("canada", canadapatterns, on_match=add_ent_3)

francepatterns = [
	[{"LOWER": "france"}],
	[{"LOWER": "french"}]
	]
matcher.add("france", francepatterns, on_match=add_ent_3)


ukpatterns = [
	[{"LOWER": "uk"}],
	[{"LOWER": "united kingdom"}],
	[{"LOWER": "england"}],
	[{"LOWER": "english"}],
	[{"LOWER": "british"}],
	]
matcher.add("uk", ukpatterns, on_match=add_ent_3)

belgiumpatterns = [
	[{"LOWER": "belgium"}],
	[{"LOWER": "belgian"}]
	]
matcher.add("belgium", belgiumpatterns, on_match=add_ent_3)

croatiapatterns = [
	[{"LOWER": "croatia"}],
	[{"LOWER": "croatian"}]
	]
matcher.add("croatia", croatiapatterns, on_match=add_ent_3)

estoniapatterns = [
	[{"LOWER": "estonia"}],
	[{"LOWER": "estonian"}]
	]
matcher.add("estonia", estoniapatterns, on_match=add_ent_3)

finlandpatterns = [
	[{"LOWER": "finland"}],
	[{"LOWER": "finnish"}]
	]
matcher.add("finland", finlandpatterns, on_match=add_ent_3)

italypatterns = [
	[{"LOWER": "italy"}],
	[{"LOWER": "italian"}]
	]
matcher.add("italy", italypatterns, on_match=add_ent_3)


nlpatterns = [
	[{"LOWER": "netherlands"}],
	[{"LOWER": "dutch"}]
	]
matcher.add("netherlands", nlpatterns, on_match=add_ent_3)


norwaypatterns = [
	[{"LOWER": "norway"}],
	[{"LOWER": "norwegian"}]
	]
matcher.add("norway",norwaypatterns, on_match=add_ent_3)


australiapatterns = [
	[{"LOWER": "australia"}],
	[{"LOWER": "australian"}]
	]
matcher.add("australia",australiapatterns, on_match=add_ent_3)


thailandpatterns = [
	[{"LOWER": "thailand"}],
	[{"LOWER": "thai"}]
	]
matcher.add("thailand",thailandpatterns, on_match=add_ent_3)

israelpatterns = [
	[{"LOWER": "israel"}],
	[{"LOWER": "israeli"}]
	]
matcher.add("israel",israelpatterns, on_match=add_ent_3)

newzealandpatterns = [
	[{"LOWER": "New Zealand"}],
	]
matcher.add("new zealand",newzealandpatterns, on_match=add_ent_3)

#SCHOOLYEARS
firstgradepatterns = [
	[{"LOWER": {"IN":["first", "1st"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("first_grade", firstgradepatterns, on_match=add_ent_3)

secondgradepatterns = [
	[{"LOWER": {"IN":["second", "2nd"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("second_grade", secondgradepatterns, on_match=add_ent_3)

thirdgradepatterns = [
	[{"LOWER": {"IN":["third", "3rd"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("third_grade", thirdgradepatterns, on_match=add_ent_3)

fourthgradepatterns = [
	[{"LOWER": {"IN":["fourth", "4th"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("fourth_grade", fourthgradepatterns, on_match=add_ent_3)


fifthgradepatterns = [
	[{"LOWER": {"IN":["fifth", "5th"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("fifth_grade", fifthgradepatterns, on_match=add_ent_3)

sixthgradepatterns = [
	[{"LOWER": {"IN":["sixth", "6th"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("sixth_grade", sixthgradepatterns, on_match=add_ent_3)


seventhgradepatterns = [
	[{"LOWER": {"IN":["seventh", "7th"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("seventh_grade", seventhgradepatterns, on_match=add_ent_3)

eighthgradepatterns = [
	[{"LOWER": {"IN":["eighth", "8th"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("eighth_grade", eighthgradepatterns, on_match=add_ent_3)


ninthgradepatterns = [
	[{"LOWER": {"IN":["ninth", "9th"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("ninth_grade", ninthgradepatterns, on_match=add_ent_3)

tenthgradepatterns = [
	[{"LOWER": {"IN":["tenth", "10th"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("tenth_grade", tenthgradepatterns, on_match=add_ent_3)

eleventhgradepatterns = [
	[{"LOWER": {"IN":["eleventh", "11th"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("eleventh_grade", eleventhgradepatterns, on_match=add_ent_3)

twelvthgradepatterns = [
	[{"LOWER": {"IN":["twelvth", "12th"]}}, {"IS_PUNCT": True, "OP":"?"}, {"LOWER":{"IN":["grade", "grades", "year"] } }  ],
	]
matcher.add("twelvth_grade", twelvthgradepatterns, on_match=add_ent_3)

#GENDER
femalepatterns = [
	[{"LOWER": {"REGEX": "females?"}}]
	]
matcher.add("female", femalepatterns, on_match=add_ent_3)

malepatterns = [
	[{"LOWER": {"REGEX": "males?"}}]
	]
matcher.add("male", malepatterns, on_match=add_ent_3)

enbypatterns = [
	[{"LOWER": "non"},  {"IS_PUNCT": True, "OP":"?"}, {"LOWER": "binary"}],
	[{"LOWER":"nb"}]
	]
matcher.add("enby", enbypatterns, on_match=add_ent_3)

#RACE
asianpatterns = [
	[{"LOWER": {"REGEX": "asians?"}}]
	]
matcher.add("asian", asianpatterns, on_match=add_ent_3)

blackpatterns = [
	[{"LOWER": {"REGEX": "blacks?"}}],
	[{"LOWER": {"REGEX": "caucasian?"}}]
	]
matcher.add("black", blackpatterns, on_match=add_ent_3)

latinpatterns = [
	[{"LOWER": {"REGEX": "latin[oa]s?"}}],
	[{"LOWER": {"REGEX": "hispanics?"}}]
	]
matcher.add("latin", latinpatterns, on_match=add_ent_3)

whitepatterns = [
	[{"LOWER": {"REGEX": "whites?"}}],
	[{"LOWER": {"REGEX": "caucasians?"}}]
	]
matcher.add("white", whitepatterns, on_match=add_ent_3)


if __name__ == "__main__":
	main()
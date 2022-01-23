# import required module
import os
import json
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy
from spacy.matcher import Matcher
from sklearn import metrics


# assign directory
directory = "dataset_1"

#spacy models
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

def mod_key_sent(key, op):
	keylist = key.split(" ")
	if op == "plus":
		keylist[2] = str( int(keylist[2]) + 1)
	if op == "minus":
		keylist[2] = str( int(keylist[2]) - 1)
	key = " ".join(keylist)
	return key


labeleddocs = [15, 60, 17, 10, 13, 14, 61]

def main():
	

	output = ""
	counter = -1


	#load results of algorithm
	results = {}
	with open("output_concept.json", "r") as resultfile:
		json_data = json.load(resultfile)
		for item in json_data:
			if item["paper_id"] in labeleddocs:
				predicted_label = "no relation"
				if item["type"] == "correlation":
						predicted_label = "correlation"
				else:
						predicted_label = "causation"
				key = (str(item["paper_id"])+" " + str(item["paragraph"])+" " + str(item["para_sent_id"]))
				#print(key, predicted_label, item["text"])
				results[key] = predicted_label
	#print(results)
	print("\n")
	labels = {}
	#preprocess, load annotations
	with open("dataset_1_labels.txt", "r") as labelfile:
		lines = labelfile.readlines()
		lines = [(line.strip().split("\t")) for line in lines]
		#remove empty line at the end
		for line in lines:
			if len(line) > 8:
				#filter interactions of other entities and older annotations we did with nltk tokenization
				if ( ( line[7]=="1" and line [8]=="4" ) or (line[8]=="1" and line [7]=="4") ): #and not (int(line[0] ) < 133):
					true_label = "no relation"
					if line[9] == "0" or line[9] == "1":
						true_label = "causation"
					if line[9] == "3" or line[9] == "2":
						true_label = "correlation"
					#document, paragraph,sentence
					key = str(line[1])+" " + str(int(line[2]) -1)+" " + str(line[3])
					#print(key, true_label)
					labels[key] = true_label
	#print(labels)
	tp=0
	tn = 0
	fp = 0
	fn = 0
	for key in results:
		originalkey = key
		if (key in labels and labels[key] == results[key]) :
			tp+=1
		#elif (mod_key_sent(key, "plus" ) in labels and labels[mod_key_sent(key, "plus" )] == results[key]) :
		#	tp+=1	
		#elif (mod_key_sent(key, "minus" ) in labels and labels[mod_key_sent(key, "minus" )] == results[originalkey]) :
		#	tp+=1	
		else:
			fp+=1
	for key in labels:
		if not key in results:
			fn+=1
	print("tp" , tp)
	print("fp" , fp)
	print("fn" ,fn)
	prec = tp / (tp+fp)
	rec = tp / (tp+fn)
	f1 = (2* prec*rec) / (prec+rec)
	print("precision: ", prec, "recall: ", rec, "f1: " , f1)		
		
	#write output json to file
	#output += "total " + str(total ) + "total positive " + str(total_pos) + "total negative "+ str(total_neg) + "\n true positives " + str(true_positives) + "true_negatives " + str(true_negatives)+ "false_positives "+  str(false_positives)+"false_negatives "+str(false_negatives)
	#out_filename = "results.txt"
	#with open(out_filename, "w") as fout:
	#	print(output)
	#	fout.write(output)



if __name__ == "__main__":
	main()
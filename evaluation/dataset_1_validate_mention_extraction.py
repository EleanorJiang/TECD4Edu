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

def list_of_lists_remove_duplicates(ls):
	new_ls = []
	for item in ls:
	    if item not in new_ls:
	        new_ls.append(item)
	return new_ls


labeleddocs = [15, 60, 17, 10, 13, 14, 61]

def main():
	

	output = ""
	counter = -1


	#load results of algorithm
	results = []
	with open("step1_output_concept_online_format.txt", "r") as resultfile:
		lines = resultfile.readlines()
		results = [(line.strip().split("\t"))[0:3] for line in lines]

	labels = []
	#preprocess, load annotations
	with open("dataset_1_labels.txt", "r") as labelfile:
		lines = labelfile.readlines()
		lines = [(line.strip().split("\t")) for line in lines]
		#remove empty line at the end
		for line in lines:
			if len(line) > 8:
				if ( ( line[7]=="1" and line [8]=="4" ) or (line[8]=="1" and line [7]=="4")) and not (int(line[0] ) < 133):
					print(int(line[0]))
					print(line[7], line[8])
					labels.append(line[1:4])
		labels = list_of_lists_remove_duplicates(labels)


	total = 0
	total_pos = 0
	total_neg = 0
	true_positives = 0
	false_positives = 0
	false_negatives = 0
	true_negatives = 0

	pos = 0
	for filename in os.listdir(directory):
		counter +=1

		if (counter not in labeleddocs):
			continue
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
			#global sentence counter ID
			sent_id = 0

			para_id=-1
			for item in body:
				para_sent_id = 0
				section = item["section"]
				tokens = nlp(item["text"])
				for sent in tokens.sents:
					#out_item = str(counter) + "\t" +str(para_id)+ "\t" +str(para_sent_id)+"\n"
					#print(out_item + "\t" + sent.text + "\n")
					#print([str(counter), str(para_id), str(para_sent_id)])
					predicted_pos = [str(counter), str(para_id), str(para_sent_id)] in results
					labeled_pos = [str(counter), str(para_id+1), str(para_sent_id)] in labels 
					total+=1
					if labeled_pos:
						total_pos+=1
					else:
						total_neg+=1
						#print([str(counter), str(para_id), str(para_sent_id)])
						#print("predicted positive"+ sent.text)
					#if labeled_pos:
						#print([str(counter), str(para_id), str(para_sent_id)])
						#print("labeled positive"+ sent.text)
					if predicted_pos and labeled_pos: 
						true_positives+=1
						#print([str(counter), str(para_id), str(para_sent_id)])
						#print("true positive"+ sent.text)
					if not predicted_pos and not labeled_pos: 
						true_negatives+=1
					if predicted_pos and not labeled_pos: 
						false_positives+=1
						#print([str(counter), str(para_id), str(para_sent_id)])
						#print("false positive"+ sent.text)
					if not predicted_pos and labeled_pos: 
						false_negatives+=1
						print([str(counter), str(para_id), str(para_sent_id)])
						print("false negative"+ sent.text)
					sent_id +=1
					para_sent_id +=1
				para_id+=1
		#if counter > 20:
		#	break
				
		
	#write output json to file
	output += "total " + str(total ) + "total positive " + str(total_pos) + "total negative "+ str(total_neg) + "\n true positives " + str(true_positives) + "true_negatives " + str(true_negatives)+ "false_positives "+  str(false_positives)+"false_negatives "+str(false_negatives)
	
	tp = true_positives
	tn = true_negatives
	fn = false_negatives
	fp = false_positives

	prec = tp / (tp+fp)
	rec = tp / (tp+fn)
	f1 = (2* prec*rec) / (prec+rec)
	print("precision: ", prec, "recall: ", rec, "f1: " , f1)	
	

	out_filename = "results.txt"
	with open(out_filename, "w") as fout:
	#	print(output)
		fout.write(output)



if __name__ == "__main__":
	main()
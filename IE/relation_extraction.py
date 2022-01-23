# import required module
import os
import json
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy
from spacy.matcher import Matcher
import re


directory = '../data/scherrer_json_s2orc'
directory2 = 'output'
nlp = spacy.load("en_core_web_sm")

def my_strip(sentence):
    return ''.join(sentence.split())

def str2float(string):
    return float(my_strip(string))

def search_words(word_list, text):
    for word in word_list:
        if word in text.lower():
            return True
    return False

def sub_list(lst1, lst2):
    for item in lst2:
        lst1.remove(item)
    return lst1

def identify_type(text):
    causal_word_list = ["cause", "causal", "effect"]
    correlate_word_list = ["correlate", "relate", "correlation"]
    sec_level_causal_word_list = ["lead"]
    if search_words(causal_word_list, text):
        return "causal"
    elif search_words(correlate_word_list, text):
        return "correlation"
    elif search_words(sec_level_causal_word_list, text):
        return "causal"
    else:
        return "correlation"

def list_replace(lst, a, b):
    return [b if x==a else x for x in lst]

def extract_relation(dataset):
    out_json = []
    with open(f'step1_output_{dataset}.json') as f:
        in_json = json.load(f)
    for in_item in in_json:
        #find abstract
        factors = [entity3['name'] for entity3 in in_item['entities3']]
        len_factors = [len(entity3['values']) for entity3 in in_item['entities3']]
        N = len(factors)
        # print(N)
        if N <= 1:
            new_entities3 = []
            for entity3 in in_item['entities3']:
                name = entity3['name']
                for item in entity3['values']:
                    new_entities3.append({name: item['name']})
        elif N == 2:
            new_entities3 = []
            a = {}
            for item in in_item['entities3'][0]['values']:
                a[in_item['entities3'][0]['name']] = item['name']
                for item in in_item['entities3'][1]['values']:
                    a[in_item['entities3'][1]['name']] = item['name']
                    new_entities3.append(a.copy())
                    # recover
                    del a[in_item['entities3'][1]['name']]
        elif N == 3:
            new_entities3 = []
            a = {}
            for item in in_item['entities3'][0]['values']:
                a[in_item['entities3'][0]['name']] = item['name']
                for item in in_item['entities3'][1]['values']:
                    a[in_item['entities3'][1]['name']] = item['name']
                    for item in in_item['entities3'][2]['values']:
                        a[in_item['entities3'][2]['name']] = item['name']
                        new_entities3.append(a.copy())
                        # recover
                        del a[in_item['entities3'][2]['name']]
                    # recover
                    del a[in_item['entities3'][1]['name']]
        else:
            print(N)

        #len_factors = [len(new_entities3[factor]) for factor in factors]
        #total_numbers = 1
       # for len_factor in len_factors:
       #     total_numbers *= len_factor
        text = in_item['text']
        if len(new_entities3) == 0:
            out_item_list = [
                {
                    "paper_id": in_item["paper_id"],
                    "title": in_item["title"],
                    "sentence_id": in_item["sentence_id"],
                    "section": in_item["section"],
                    "entity1": in_item['entity1']['name'],
                    "entity2": in_item['entity2']['name'],
                    "entities3": [],
                    'type': identify_type(text),
                    'coefficient': 'NA',
                    'p_value': 'NA'
                }
            ]
        else:
            out_item_list = [
                        {
                            "paper_id": in_item["paper_id"],
                            "title": in_item["title"],
                            "sentence_id": in_item["sentence_id"],
                            "section": in_item["section"],
                            "entity1": in_item['entity1']['name'],
                            "entity2": in_item['entity2']['name'],
                            "entities3": new_entity3,
                            'type': identify_type(text),
                            'coefficient': 'NA',
                            'p_value': 'NA'
                        } for new_entity3 in new_entities3
                        ]
        # for i, factor in enumerate(factors):
        #     repeat_times = total_numbers / len_factors[i]
        #     for value in new_entities3[factor]:
        #         out_item["entities3"][]

        pattern_list = {"all_num": [re.compile('\D[-]?[0]?[.][\s]*[\d]+\D'), [[], []]],
                        "range": [re.compile('\D[-]?[0]?[.][\d]+[\s]*to[\s][0]?[.][\s]*[\d]+\D'), [[], []]],
                        "p_values": [re.compile('\Dp[\s]*[\S]?[\s]*[0]?[.][\s]*[\d]+\D'), [[], []]],
                        "two_values": [re.compile('\D[-]?[0]?[.][\d]+[\s]*and[\s]*[0]?[.][\s]*[\d]+\D'), [[], []]]
                        }

        tmp = text.lower()
        # match_list = re.findall(pattern, tmp, flags=0)
        for key in pattern_list.keys():
            pattern_list[key][1][0] = re.findall(pattern_list[key][0], tmp, flags=0)
            for i, item in enumerate(pattern_list[key][1][0]):
                pattern_list[key][1][0][i] = item[1:-1]
                pos = tmp.find(item[1:-1])
                pattern_list[key][1][1].append(pos)
        all_num = [str2float(item) for i, item in enumerate(pattern_list['all_num'][1][0])]
        p_values = []
        for i, item in enumerate(pattern_list['p_values'][1][0]):
            tmp = re.findall(re.compile('[0]?[.][\s]*[\d]+'), item)
            p_values.append(float(my_strip(tmp[0])))
        # print("p_values", p_values)
        average_values = []
        for i, item in enumerate(pattern_list['range'][1][0]):
            tmp = item.split('to')
            min, max = str2float(tmp[0]), str2float(tmp[1])
            all_num.remove(max)
            all_num = list_replace(all_num, min, (min+max)/2)

        if all_num is None:
            all_num = []
        # if len(out_item_list) > 1 and len(all_num) != 0:
        #     if len(all_num) - len(p_values) == len(out_item_list):
        #         print('good')
        #     elif len(all_num) - len(p_values) != len(out_item_list):
        #         print(text)
        #         print([pattern_list[key][1][0] for key in pattern_list.keys()])
        #         print("mismatch")
        coefficients = sub_list(all_num, p_values)
        if len(all_num) == 0:
            continue
        if len(all_num) == 1 and len(p_values)==1:
            for out_item in out_item_list:
                out_item['p_value'] = p_values[0]
        elif len(all_num) == 1 and len(p_values)==0:
            for out_item in out_item_list:
                out_item['coefficient'] = all_num[0]

        # p_values:
        if len(p_values) != 0:
            if len(p_values) < len(out_item_list):
                for i in range(len(p_values),len(out_item_list)):
                    p_values.append(p_values[-1])
            for i, out_item in enumerate(out_item_list):
                out_item['p_value'] = p_values[i]
        # coefficients
        if len(coefficients) != 0:
            if len(coefficients) < len(out_item_list):
                for i in range(len(coefficients),len(out_item_list)):
                    coefficients.append(coefficients[-1])
            for i, out_item in enumerate(out_item_list):
                out_item['coefficient'] = coefficients[i]


        # if len(match_list) > 0:
        #     doc = nlp(text)
        #     item_id = 0
        #     for chunk in doc.noun_chunks:
        #         if match_list[item_id][0] in chunk.text:
        #             item_id += 1
        #             print(chunk.text)
            # match_list = []
        # m0 = re.search(pattern, text.lower())
        # while m0 is not None:
        #     match_list.append((m0.span(), m0.start(), m0.end()))
        #     tmp = text[m0.end():]
        #     m0 = re.search(pattern, tmp.lower())


        # if len(match_list) > 0:
        #     for entity3 in in_item['entities3']:
        #         if len(entity3) > 1:
        #             print(entity3)
        #             doc = nlp(text)
        #             item_id = 0
        #             for chunk in doc.noun_chunks:
        #                 if match_list[item_id][0] in chunk.text:
        #                     item_id += 1
        #                     print(chunk.text)
        #     out_item['size'] = float(match_list[0])
        #     if len(match_list) > 1:
        #         out_item['p_value'] = float(match_list[1])
        out_json.extend(out_item_list)

    #write output json to file
    with open(f"output_{dataset}.json", "w") as fout:
        json.dump(out_json, fout)

if __name__ == '__main__':
    datasets = ['concept', 'esteem'] #concept, esteem
    for dataset in datasets:
        extract_relation(dataset)
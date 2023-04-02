import json, re
from time import time
from collections import defaultdict
from numpy import log10 as lg

def solve_cloze(input, candidates, lexicon, corpus):
    print(f'starting to solve the cloze {input} with {candidates} using {lexicon} and {corpus}')
  
    with open(candidates, 'r', encoding='utf-8') as _candidates:
        candidates = _candidates.read().split('\n')
    _candidates.close()
  
    with open(input, 'r', encoding='utf-8') as _cloze:
        cloze = _cloze.read().replace(',','').split('.')
    _cloze.close()
  
    prefixes_dict, suffixes = get_relevant_prefixes_and_suffixes(cloze,candidates)    
    prefixes_dict = build_dict_by_corpus(corpus,candidates,suffixes,prefixes_dict)
  
    return get_best_matches(prefixes_dict, extract_surrounding_words(cloze), candidates)

def print_hit_percentage(solution,candidates):
    with open(candidates, 'r', encoding='utf-8') as _candidates:
        candidates = _candidates.read().split('\n')
    _candidates.close()
    
    count = len(candidates)
    hits = sum([1  if x == y else 0  for x, y in zip(solution,candidates)])
    print(f'hit percentage: {hits/count}')
    
def build_dict_by_corpus(corpus,candidates,suffixes,prefix_dict):
    """

    :param corpus: file path | str
    :param candidates: file path | str
    :param suffixes: list[str]
    :param prefix_dict:
    :return: returning a dictionary where keys = {words before blanks | candidates} from a given cloze and values are list[x,y]
             where list[x] is a dictionary where keys = {following word after candidate | words after blanks} and values (of list[x])
             are count of occurences of the sequence (key,value) in corpus.
             list[y] is the count of occurences of the key
    """

    # insert candidates to the dictionary
    for cand in candidates:
        prefix_dict[cand] = [defaultdict(int),0]

    # lower-casing keys and extracting all prefixes
    prefix_dict = {k.lower(): v for k,v in prefix_dict.items()} 
    prefixes = list(map(str.lower,prefix_dict.keys()))

    with open(corpus,'r',encoding='utf-8') as corp:
        corp_lines = corp.readlines()

    # working around the corpus with a sliding window of the size of 3 --> [prefix,blank,suffix]
    inspected_group = []
    # in case sentence is overflowing to next line
    overflow = False
    for line in corp_lines:
        line = [tok.lower() for tok in re.subn(r"[\n,.;]",'',line)[0].split()]

        next_token_to_take = 0
        while len(line)>next_token_to_take:
            if len(inspected_group) < 3:
                inspected_group.append(line[next_token_to_take])
                next_token_to_take+=1
                if next_token_to_take == len(line):
                    overflow = True
                    continue
          
            for cur_token in inspected_group:
                if cur_token in prefixes:
                    if overflow: 
                        break
                    next_token = line[next_token_to_take]# + 1
                    if (cur_token in candidates and next_token in suffixes) or \
                    ((not (cur_token in candidates)) and next_token in candidates):
              
                        prefix_dict[cur_token][0][next_token]+=1
                        prefix_dict[cur_token][1]+=1
            inspected_group.pop(0)
            if overflow:
                overflow = False
                break
    return prefix_dict

def get_relevant_prefixes_and_suffixes(cloze,candidates):
    suffixes = []
    prefixes_dict = {}
    for line in cloze:
        cur_line = line.split()
        for word_ind in range(len(cur_line)):
            if '__' in cur_line[word_ind]:
                if word_ind < len(cur_line)-1:
                    suffixes.append(cur_line[word_ind+1])
                if word_ind == 0:
                    continue
                prefixes_dict[cur_line[word_ind-1]] = [defaultdict(int),0]
          
    return prefixes_dict, suffixes

def extract_surrounding_words(cloze):
  
    cloze_sentences = [sen.split() for sen in cloze]
  
    ordered_surroundings = []
    for sentence in cloze_sentences:
        for word in range(len(sentence)):
            if '___' in sentence[word]:
                surrounding_words = []
                surrounding_words.append(sentence[word-1].lower()  if word > 0 else '<s>')
                surrounding_words.append(sentence[word+1].lower() if word < len(sentence) - 1 else '</s>')    
                ordered_surroundings.append(surrounding_words)
          
    return ordered_surroundings
  
def get_best_matches(prefixes_dict, surrounding_words,candidates):
    result = []
    big_num = 1000000
    for pref,suff in surrounding_words:#
        last_cand = ''
        last_max = 0
        for cand in candidates:
            pref_prob = 0.25
            suff_prob = 0.25
            if pref != '<s>':
                candidate_dict , occurences1 = prefixes_dict[pref]
                pref_prob = (candidate_dict[cand] + 1) / (occurences1 + big_num)
            if suff != '</s>':
                suffixes_dict , occurences2 = prefixes_dict[cand]
                suff_prob = (suffixes_dict[suff] + 1) / (occurences2 + big_num)
            
            cur_prob = suff_prob * pref_prob
            
            if last_max < cur_prob:
                last_cand = cand
                last_max = cur_prob
              
        result.append(last_cand)
        candidates.remove(last_cand)
        
    return result
      
      
              
                  
                  
                  
          
      
if __name__ == '__main__':
    with open('config.json', 'r') as json_file:
        config = json.load(json_file)
    # if not os.path.isfile('prefixes_dict.pkl'):
    #     prefixes_dict, suffixes = get_relevant_prefixes_and_suffixes(config['input_filename'],config['candidates_filename'])
    #     prefixes_dict = build_dict_by_corpus(config['corpus'],config['candidates_filename'],suffixes,prefixes_dict)
    #     pickle.dump(prefixes_dict,open('prefixes_dict.pkl','wb'))
      
    # prefixes_dict = pickle.load(open('prefixes_dict.pkl','rb'))
  
    begin = time()
    solution = solve_cloze(config['input_filename'],
                           config['candidates_filename'],
                           config['lexicon_filename'],
                           config['corpus'])
    end = time()
    print (f'time took: {(end-begin)/60} minutes')
    print('cloze solution:', solution)
    
    print_hit_percentage(solution,config['candidates_filename'])
    





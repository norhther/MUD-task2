#! /usr/bin/python3

import sys
import re
from os import listdir

from xml.dom.minidom import parse
from nltk.tokenize import word_tokenize


   
## --------- tokenize sentence ----------- 
## -- Tokenize sentence, returning tokens and span offsets

def tokenize(txt):
    offset = 0
    tks = []
    ## word_tokenize splits words, taking into account punctuations, numbers, etc.
    for t in word_tokenize(txt):
        ## keep track of the position where each token should appear, and
        ## store that information with the token
        offset = txt.find(t, offset)
        tks.append((t, offset, offset+len(t)-1))
        offset += len(t)

    ## tks is a list of triples (word,start,end)
    return tks


## --------- get tag ----------- 
##  Find out whether given token is marked as part of an entity in the XML

def get_tag(token, spans) :
   (form,start,end) = token
   for (spanS,spanE,spanT) in spans :
      if start==spanS and end<=spanE : return "B-"+spanT
      elif start>=spanS and end<=spanE : return "I-"+spanT

   return "O"
 
# custom functions to extract features
def is_abbreviation(token):
   return token.isupper() and len(token) >= 2 and len(token) <= 4


def has_common_drug_name(token):
   pref_suf = ['floxacin', 'olone', 'mycin', 'antifungal', 'caine', 'dronate', 
               'pramine', 'profen', 'onide', 'tadine', 'terol', 'tretin', 'thiazide', 
               'olol', 'triptan', 'afil', 'mab', 'parin', 'pred', 'vir', 'glitazone', 
               'tyline', 'bital', 'phylline', 'bicin', 'zolam', 'setron', 'lamide', 
               'mustine', 'asone', 'zodone', 'cillin', 'gliptin', 'sulfa', 'vudine', 
               'zepam', 'cycline', 'pril', 'oprazole', 'prefix, root, suffix', 'cort',
               'iramine', 'cef, ceph', 'sartan', 'dipine', 'ridone', 'semide', 'tinib',
               'trel', 'dazole', 'statin', 'zosin', 'nacin', 'eprazole', 'fenac']
   
   for suf in pref_suf:
      if suf in token:
         return True
   return False

def has_guion(token):
   # return if the token has a guion
   # if it has it, return first position as prefix and last as sufix
   if '-' in token:
      return True, token.split('-')[0], token.split('-')[1]
   return False, None, None

def has_numbers_with_commas(token):
   # return if the token has a number with commas
   return re.search(r'\d{1,3}(,\d{3})*', token) is not None

def hasUppercase(token):
   return any(c.isupper() for c in token)

def hasNumber(token):
   return any(c.isdigit() for c in token)


def readDrugBankToDict(path = '../DDI/resources/DrugBank.txt'):
   drugbank = {}
   with open(path, 'r') as f:
      for line in f:
         drug, type = line.split('|')
         drugbank[drug.lower()] = type
   return drugbank

def readHSDBToSet(path = '../DDI/resources/hsdb.txt'):
   hsdb = set()
   with open(path, 'r') as f:
      for line in f:
         hsdb.add(line.strip().lower())
   return hsdb

## --------- Feature extractor ----------- 
## -- Extract features for each token in given sentence

def drug_n_list(token):
   drug_n = ["ch12", "flavo", "catechin", "endoxifen", "beta-endorphin"]
   for drug in drug_n:
      if drug in token:
         return True
   return False

drug = readDrugBankToDict()
hsdb = readHSDBToSet()

def extract_features(tokens) :
   # for each token, generate list of features and add it to the result
   result = []
   for k in range(0,len(tokens)):
      tokenFeatures = []
      t = tokens[k][0]
      tokenFeatures.append("form="+t)
      tokenFeatures.append("suf3="+t[-3:])
      
      if is_abbreviation(t):
         tokenFeatures.append("abbr=T")

      if has_common_drug_name(t):
         tokenFeatures.append("commonDrugName=T")

      if has_numbers_with_commas(t):
         tokenFeatures.append("hasNumbersWithCommas=T")
      if hasUppercase(t):
         tokenFeatures.append("hasUppercase=T")
      if hasNumber(t):
         tokenFeatures.append("hasNumber=T")

      if t.lower() in drug:
         tokenFeatures.append("drugBankType="+str(drug[t.lower()]).strip())
      
      if t.lower() in hsdb:
         tokenFeatures.append("hsdb=T")

      if drug_n_list(t):
         tokenFeatures.append("drug_n="+str(drug_n_list(t)))

      if has_guion(t)[0]:
         tokenFeatures.append("prefixGuion="+has_guion(t)[1])
         tokenFeatures.append("sufixGuion="+has_guion(t)[2])


      if k>0 :
         tPrev = tokens[k-1][0]
         tokenFeatures.append("formPrev="+tPrev)
         tokenFeatures.append("suf3Prev="+tPrev[-3:])
         if is_abbreviation(tPrev):
            tokenFeatures.append("abbrPrev=T")
         else:
            tokenFeatures.append("abbrPrev=F")

      else :
         tokenFeatures.append("BoS")

      if k<len(tokens)-1 :
         tNext = tokens[k+1][0]
         tokenFeatures.append("formNext="+tNext)
         tokenFeatures.append("suf3Next="+tNext[-3:])
         if is_abbreviation(tNext):
            tokenFeatures.append("abbrNext=T")
         else:
            tokenFeatures.append("abbrNext=F")

      else:
         tokenFeatures.append("EoS")
    
      result.append(tokenFeatures)
    
   return result


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  baseline-NER.py target-dir
## --
## -- Extracts Drug NE from all XML files in target-dir, and writes
## -- them in the output format requested by the evalution programs.
## --


# directory with files to process
datadir = sys.argv[1]

# process each file in directory
for f in listdir(datadir) :
   
   # parse XML file, obtaining a DOM tree
   tree = parse(datadir+"/"+f)
   
   # process each sentence in the file
   sentences = tree.getElementsByTagName("sentence")
   for s in sentences :
      sid = s.attributes["id"].value   # get sentence id
      spans = []
      stext = s.attributes["text"].value   # get sentence text
      entities = s.getElementsByTagName("entity")
      for e in entities :
         # for discontinuous entities, we only get the first span
         # (will not work, but there are few of them)
         (start,end) = e.attributes["charOffset"].value.split(";")[0].split("-")
         typ =  e.attributes["type"].value
         spans.append((int(start),int(end),typ))
         

      # convert the sentence to a list of tokens
      tokens = tokenize(stext)
      # extract sentence features
      features = extract_features(tokens)

      # print features in format expected by crfsuite trainer
      for i in range (0,len(tokens)) :
         # see if the token is part of an entity
         tag = get_tag(tokens[i], spans) 
         print (sid, tokens[i][0], tokens[i][1], tokens[i][2], tag, "\t".join(features[i]), sep='\t')

      # blank line to separate sentences
      print()

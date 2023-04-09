#! /usr/bin/python3

import sys
import inspect
from os import listdir

from xml.dom.minidom import parse

from deptree import *
#import patterns


## ------------------- 
## -- Convert a pair of drugs and their context in a feature vector

def extract_features(tree, entities, e1, e2) :
   feats = set()

   # get head token for each gold entity
   tkE1 = tree.get_fragment_head(entities[e1]['start'],entities[e1]['end'])
   tkE2 = tree.get_fragment_head(entities[e2]['start'],entities[e2]['end'])

   if tkE1 is not None and tkE2 is not None:
      # features for tokens in between E1 and E2
      for tk in range(tkE1+1, tkE2) :
         tk=tkE1+1
         try:
            while (tree.is_stopword(tk)):
               tk += 1
         except:
            return set()
         word  = tree.get_word(tk)
         lemma = tree.get_lemma(tk).lower()
         tag = tree.get_tag(tk)
         feats.add("lib=" + lemma)
         feats.add("wib=" + word)
         feats.add("lpib=" + lemma + "_" + tag)
      

      eib = False
      for tk in range(tkE1+1, tkE2) :
         if tree.is_entity(tk, entities):
            eib = True 
      
	  # feature indicating the presence of an entity in between E1 and E2
      feats.add('eib='+ str(eib))

      # features about paths in the tree
      lcs = tree.get_LCS(tkE1,tkE2)
      
      path1 = tree.get_up_path(tkE1,lcs)
      path1 = "<".join([tree.get_lemma(x)+"_"+tree.get_rel(x) for x in path1])
      feats.add("path1="+path1)

      path2 = tree.get_down_path(lcs,tkE2)
      path2 = ">".join([tree.get_lemma(x)+"_"+tree.get_rel(x) for x in path2])
      feats.add("path2="+path2)

      path = path1+"<"+tree.get_lemma(lcs)+"_"+tree.get_rel(lcs)+">"+path2      
      feats.add("path="+path)

      # features for tokens between E1 and E2
      idx = 1
      for tk in range(tkE1+1, tkE2) :
         try:
            feats.add(f"pos_{idx}={tree.get_tag(tk)}")
            feats.add(f"lemma_{idx}={tree.get_lemma(tk)}")
            # get type attribute
            feats.add(f"relType_{idx}={tree.get_rel(tk)}")

            if tree.is_entity(tk, entities):
               feats.add(f"entityType_{idx}={entities[tree.get_entity(tk, entities)]['type']}")
            """
            if tk == tkE1+1 and tkE2-1 == tk:
                feats.add(f"siblings_{idx}=yes")
            else:

            if tree.get_lemma(tk).lower() in ["not", "n't", "no"]:
                feats.add(f"negation_{idx}=yes")
            else:
                  feats.add(f"negation_{idx}=no")

            # feature to check for modal verbs
            if tree.get_lemma(tk).lower() in ["can", "could", "may", "might", "must", "shall", "should", "will", "would"]:
                  feats.add(f"modal_verbs_{idx}=yes")
            else:
                feats.add(f"modal_verbs_{idx}=no")
            """
         except:
            continue
         idx += 1
      
      class_verbs = {
         "adverse": ["interact", "potentiate", "inhibit", "reduce", "decrease", 
                     "impair", "worsen", 
                     "block", "prevent", "decrease", "reduce", "inhibit",
                     "depress", "suppress", "negate", "counteract", "nullify"
                     "compete", "disrupt", "interfere"],

         "beneficial": ["enhance", "augment", "boost", "potentiate", 
                        "increase", "improve", "elevate", "stimulate", 
                        "facilitate", "synergize", "promote", "accelerate","elevate", 
                        "potentiate","upregulate"],

         "neutral": ["affect", "modify", "alter", "change", "influence", 
                     "impact", "induce", "produce", "result in", "cause",
                     "control", "determine", "direct", "effect","instruct"]
      }

      tkidx = 0
      for tk in range(tkE1+1, tkE2):
         if tree.get_lemma(tk) in class_verbs["adverse"]:
            feats.add(f"relation_{tkidx}=adverse")
         if tree.get_lemma(tk) in class_verbs["beneficial"]:
            feats.add(f"relation_{tkidx}=beneficial")
         if tree.get_lemma(tk) in class_verbs["neutral"]:
            feats.add(f"relation_{tkidx}=neutral")
         tkidx += 1



      
   return feats


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  extract_features targetdir
## --
## -- Extracts feature vectors for DD interaction pairs from all XML files in target-dir
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
        stext = s.attributes["text"].value   # get sentence text
        # load sentence entities
        entities = {}
        ents = s.getElementsByTagName("entity")
        for e in ents :
           id = e.attributes["id"].value
           offs = e.attributes["charOffset"].value.split("-")           
           entities[id] = {'start': int(offs[0]), 'end': int(offs[-1])}

        # there are no entity pairs, skip sentence
        if len(entities) <= 1 : continue

        # analyze sentence
        analysis = deptree(stext)

        # for each pair in the sentence, decide whether it is DDI and its type
        pairs = s.getElementsByTagName("pair")
        for p in pairs:
            # ground truth
            ddi = p.attributes["ddi"].value
            if (ddi=="true") : dditype = p.attributes["type"].value
            else : dditype = "null"
            # target entities
            id_e1 = p.attributes["e1"].value
            id_e2 = p.attributes["e2"].value
            # feature extraction

            feats = extract_features(analysis,entities,id_e1,id_e2) 
            # resulting vector
            if len(feats) != 0:
              print(sid, id_e1, id_e2, dditype, "\t".join(feats), sep="\t")


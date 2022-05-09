import pandas as pd
import pickle
import ast
from stanza.utils.conll import CoNLL

dicts = CoNLL.conll2doc('la_ittb-ud-train.conllu')
trees = {}
for id, sent in enumerate(dicts.sentences):
  trees[id] = sent
trees_df = pd.DataFrame.from_dict(trees, orient='index')

intersect_df = pd.read_csv('intersect_csv.csv')
intersect_df['0'] = intersect_df['0'].apply(lambda x: x.replace(' ', ', ')) 
intersect_df['0'] = intersect_df['0'].apply(ast.literal_eval)

with open('deprel_list.pickle','rb') as f:
  deprel_list = pickle.load(f)

def deprelDict(sentence, search):
  deprel_dict = {}
  for dep in sentence.dependencies:
    if dep[0].lemma == search or dep[2].lemma == search:
      for deprel in deprel_list:
        if (deprel == dep[1]) and (dep[1] != 'punct'):
          if deprel in deprel_dict:
            deprel_dict[deprel] += 1
          else:
            deprel_dict[deprel] = 1
  return deprel_dict

def deprelDictHeaderFooter(sentence, search):
  header_dict = {}
  footer_dict = {}
  for dep in sentence.dependencies:
    if dep[0].lemma == search:
      for deprel in deprel_list:
        if (deprel == dep[1]) and (dep[1] != 'punct'):
          if deprel in header_dict:
            header_dict[deprel] += 1
          else:
            header_dict[deprel] = 1
    elif dep[2].lemma == search:
      for deprel in deprel_list:
        if (deprel == dep[1]) and (dep[1] != 'punct'):
          if deprel in footer_dict:
            footer_dict[deprel] += 1
          else:
            footer_dict[deprel] = 1
  return header_dict, footer_dict

def generateStatDicts(search):
  from collections import Counter

  sub_df = trees_df.iloc[intersect_df.explode('0').loc[intersect_df.explode('0')['0'] == search]['index'].to_list()]
  total = sub_df[0].apply(lambda x: deprelDict(x, search))
  header = sub_df[0].apply(lambda x: deprelDictHeaderFooter(x, search)).apply(lambda x: x[0])
  footer = sub_df[0].apply(lambda x: deprelDictHeaderFooter(x, search)).apply(lambda x: x[1])

  counts = sum(map(Counter, total), Counter())
  res = pd.DataFrame.from_dict(counts, orient='index')
  res[res.columns[0]] = (res[res.columns[0]]/res[res.columns[0]].sum())*100

  h_counts = sum(map(Counter, header), Counter())
  h_res = pd.DataFrame.from_dict(h_counts, orient='index')
  h_res[h_res.columns[0]] = (h_res[h_res.columns[0]]/h_res[h_res.columns[0]].sum())*100

  f_counts = sum(map(Counter, footer), Counter())
  f_res = pd.DataFrame.from_dict(f_counts, orient='index')
  f_res[f_res.columns[0]] = (f_res[f_res.columns[0]]/f_res[f_res.columns[0]].sum())*100

  res['asheader'] = h_res[h_res.columns[0]]
  res['asfooter'] = f_res[f_res.columns[0]]
  res = res.fillna(0)
  return res.rename(columns={0:'Total', 'asheader':f'{search} as a head', 'asfooter':f'{search} as a modifier'})

def lemmaFilter(lemma, verb_search):
  return lemma.split(verb_search)[1].isnumeric() or lemma.split(verb_search)[1] == ''
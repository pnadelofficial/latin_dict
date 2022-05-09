import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st
import re
import pickle
from util import *

st.title('Latin Verb Search')
st.markdown('Enhancing the *Lewis and Short* Latin dictionary with ITTB Latin treebanks')

las_df = pd.read_csv('las_csv.csv').rename(columns={'Unnamed: 0':'lemma','0':'entry'})

with open('lemmas_nonums.pickle', 'rb') as f:
  verb_lemmas_fromdict = pickle.load(f)

stats = open('stats.xml')
stat_xml = BeautifulSoup(stats)
deprel_list = [] 
for dep in stat_xml.find_all('deps')[0].find_all('dep'):
  deprel_list.append(dep.attrs['name'])

st.markdown("Search for a verb.")
verb_search = st.text_input('Give first person, singular, indicative form of any verb.')
verb_search = verb_search.lower()
if verb_search:
  st.write(verb_search)
  st.write(generateStatDicts(verb_search))
  st.write('Guide to [deprel tags](https://universaldependencies.org/treebanks/la_ittb/index.html#relations)')

  sub_df = las_df.applymap(lambda x: re.findall(f'(^{verb_search}\d)\|(^{verb_search})',x))
  sub_lemma = las_df['lemma'].apply(lambda x: re.findall(f'(^{verb_search})',x))
  sub_idx = sub_lemma.loc[sub_lemma.str.len() > 0].index
  sub_lemma_d = las_df['lemma'].apply(lambda x: re.findall(f'(^{verb_search}\d)',x))
  sub_d_idx = sub_lemma.loc[sub_lemma.str.len() > 0].index
  final = las_df.iloc[sub_idx]
  if len(final) == 0:
    final = las_df.iloc[sub_d_idx]

  st.write(final.loc[final['lemma'].apply(lambda x: lemmaFilter(x, verb_search))]['entry'].iloc[0])
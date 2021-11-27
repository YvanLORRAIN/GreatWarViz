import streamlit as st
import logging
import requests
from html import unescape
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.express as px

st.title("Death of french soldiers during world war one")

st.write('[Go to the data on french soldiers](https://www.data.gouv.fr/en/datasets/premiere-guerre-mondiale-les-poilus-morts-pour-la-france-a-completer/)')

st.write('[Go to the data on french cities](https://www.data.gouv.fr/fr/datasets/communes-de-france-base-des-codes-postaux/)')

st.write('The Great War (also called The War To End All Wars or more commonly The First World War) is a bloody and traumatizing conflict that shook the world in the early 20th century. The horror of the soldiers had to endure would break even the most strongest of minds.')

st.write('On this website I diplay some information that might interest you as I ve display the information in a way that helps you to put what you might have learned on this conflict into perspective. The graphs that you will see do not match perfectly the reality as the data used is only an small sample (I could not get my hand on more data :/ ).')

st.write('However the graphs do paint a portrait of WWI casualties which might be interresting to keep in mind.')


st.title("Enjoy the graphs :)")

df_poilus_raw = pd.read_csv("data/tracesdesoldats-lespoilus.csv",encoding='utf8')
df_city = pd.read_csv('data/communes-departement-region.csv')

# Delete the image reference because it is not useful
df_poilus = df_poilus_raw.drop(columns=['images-href'])

# Rename 'Lieu de décès (suite)'  into a more appropriate one
df_poilus.rename(columns = {'Lieu de décès (suite)':'Cause du décès'}, inplace = True)
df_poilus["naissance"].ffill(inplace=True)


#--------------------------------------------------------------------------------------------
# Split a the "naissance" column to extract only the date of birth
# I did not want to bother with getting the place of birth too

def SplitColumn(col,sep):
  date_of_birth = []

  for line in col:
    splited_data = line.split(sep)
    
    # If the number of words is long enough it means that the data has the standard format I'm looking for
    if len(splited_data) >= 5: 
      date_of_birth.append(splited_data[2])
    # If that is not the case it's probably because there is no date of birth so I just put the one on the previous line in it's place
    else:
      date_of_birth.append(date_of_birth[-1])
  
  return date_of_birth

df_poilus["Date de naisssance"] = SplitColumn(df_poilus.naissance," ")
#--------------------------------------------------------------------------------------------

date_of_death = []
df_poilus["Date de décès"] = df_poilus["Date de décès"].astype(str)
for line in df_poilus["Date de décès"]:
    splited_data = line.split("-")
    if len(splited_data) == 3:
      date_of_death.append(int(splited_data[2]))
    else:
      date_of_death.append(np.nan)

df_poilus["Année de décès/Date of death"] = date_of_death

low = []
low2 = []
for i in range(len(df_city['nom_commune_postal'])):
  low.append(df_city['nom_commune_postal'].iloc[i].lower())

df_poilus['Lieu de décès'] = df_poilus['Lieu de décès'].astype(str)
for i in range(len(df_poilus['Lieu de décès'])):
  low2.append(df_poilus['Lieu de décès'].iloc[i].lower())

for i in range(len(low)):
  low[i] = low[i].replace(' ','-')

df_city['nom_commune_postal']=low
df_poilus['Lieu de décès'] = low2

df_death_city_france = df_city[df_city['nom_commune_postal'].isin(df_poilus['Lieu de décès'])]

df_for_map = df_poilus.set_index('Lieu de décès').join(df_city.set_index('nom_commune_postal'))

df_for_map = df_for_map[(df_for_map['Année de décès/Date of death'] >= 1914.0) & (df_for_map['Année de décès/Date of death'] <= 1918.0)]
df_for_map['Année de décès/Date of death'].astype(str)


#--------------------------------------------------------------------------------------------
#					That's the real deal
#--------------------------------------------------------------------------------------------

# Map of deaths in France
fig = px.scatter_geo(data_frame= df_for_map,lat=df_for_map.latitude, lon=df_for_map.longitude,color=df_for_map["Année de décès/Date of death"],scope='europe',title='Map of the french soldiers who died during the Great War in France',height=500,width=800)
st.plotly_chart(fig, use_container_width=True)
st.write('This map show where soldiers died between 1914 and 1918, one can clearly see the concentration of casualties neer the franco-german border as well as a change in the distribution of deaths. This is explained by the the fact that although the frontline remained static there was a great deal of troop movement to prepare assaults on ennemy lines or to repel the ennemy.')

st.write('One can even see an aggregation of points around 1916 south-west of Luxembourg which corresponds to the Battle of Verdun which lasted 9 months and 27 days and made more then 700 000 casualties including PoWs and wounded')



fig1, ax1= plt.subplots()
# Lineplot of the deaths per year
X = df_for_map["Année de décès/Date of death"].unique()
Y = df_for_map["Année de décès/Date of death"].value_counts()

DeathPerYear = sns.lineplot(y=Y, x=X,ax=ax1)
DeathPerYear.set(title='Evolution of the bumber of deaths per year')
st.pyplot(fig1)
st.write('This plot complements nicely what I just said earlier, one can observe a peak of casualties in 1916 which is not surprising at all considering the battle of Verdun is the bloodiest battle of the conflict.')



st.write('The following has been created using a subsample of the data set of 1000 lines')
fig2, ax2= plt.subplots(figsize=(7,20))
# Distribution of deaths accross ranks on the first 1000 soldiers 
CasualtiesPerRank = sns.histplot(data=df_poilus[:1000],y='Grade',ax=ax2)
CasualtiesPerRank.set(title='Distribution of the casualties per rank')
st.pyplot(fig2)
st.write('Finally I would like to remind you that the people who fought this conflict are beyond brave as most of the deads were low ranking soldiers conscripted and whos jobs were: farmers, teachers, students, fatory workers... YOU might have been one of them...')


st.title("A word from the author")
st.write('I am a huge fan of history so I wanted to share this passion with you. And I feel like this conflict is not given the credit it is due.')

st.write('As christmas is slowly approching when I write this, I leave you a song from Sabaton on what I consider to be the best moment of the war (appart from its end): the christmas truce')
st.write('[Here is the song](https://www.youtube.com/watch?v=goXDAFtkJLw)')


st.write('Thank you for reading')
st.write('Author: Yvan LORRAIN')

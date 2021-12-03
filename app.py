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

st.write('''This website is dedicated to presenting the Great war in a new light. To achieve this you will be able to: 
- see the western front through thanks to the place where some soldiers dies
- see the impact of the battle of Verdun on the death toll
- See the difference in the amount of rank''')

st.write('However the graphs do paint a portrait of WWI casualties which might be interresting to keep in mind.')


st.title("The great war seen with graphs")

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


method = df_poilus['Cause du décès'].unique()
df_test = pd.DataFrame()

df_test['Cause of death'] = method
df_test['Cause of death'] = df_test['Cause of death'].astype(str)
method = []

for d in df_test['Cause of death']:
    if (' en mer' in d):
      method.append('Died at sea')
    if ('avion' in d):
      method.append('Died flying airplane')
    if ('blessure' in d):
      method.append('Died of injuries')
    if ('ennemi' in d):
      method.append('Died to the ennemi')
    if ('nan' in d):
      method.append('Unknown causes')
    if ('maladie' in d):
      method.append('Died of illness')

df_death = pd.DataFrame()
df_death['Cause of death'] = method

#--------------------------------------------------------------------------------------------
#					That's the real deal
#--------------------------------------------------------------------------------------------

# Map of deaths in France
fig = px.scatter_geo(data_frame= df_for_map,lat=df_for_map.latitude, lon=df_for_map.longitude,color=df_for_map["Année de décès/Date of death"],scope='europe',title='1 point, 1 soul...',height=500,width=800,hover_name='nom')
st.plotly_chart(fig, use_container_width=True)
st.write('This map show where soldiers died between 1914 and 1918, one can clearly see the concentration of casualties neer the franco-german border as well as a change in the distribution of deaths. This is explained by the the fact that although the frontline remained static there was a great deal of troop movement to prepare assaults on ennemy lines or to repel the ennemy.')

st.write('One can even see an aggregation of points around 1916 south-west of Luxembourg which corresponds to the Battle of Verdun which lasted 9 months and 27 days and made more then 700 000 casualties including PoWs and wounded')



fig1, ax1= plt.subplots()
# Lineplot of the deaths per year
X = df_for_map["Année de décès/Date of death"].unique()
Y = df_for_map["Année de décès/Date of death"].value_counts()

DeathPerYear = sns.lineplot(y=Y, x=X,ax=ax1)
DeathPerYear.set(title='1916, the battle year')
st.pyplot(fig1)
st.write('This plot complements nicely the previous information, one can observe a peak of casualties in 1916 which is not sur$$prising at all considering the battle of Verdun is the bloodiest battle of the conflict.')



st.write('The following has been created using a subsample of the data set for lisibility concerns')
fig2, ax2= plt.subplots(figsize=(6,10))
# Distribution of deaths accross ranks on the first 1000 soldiers 
Casualties = sns.histplot(data=df_death,y='Cause of death',ax=ax2)
Casualties.set(title='Death has many shapes')
st.pyplot(fig2)
st.write('Finally, it is always a good thing to remind people that the men who fought in this conflict were beyond brave as they had to live every day surounded by death. Soldier or not none of them had been prepared for the kind of horrors that awaited them: the smell of rotting corpses, the diseases, the thunderous noise of cannons and shells, the first tanks, ...')


st.title("A word from the author")
st.write('I am a huge fan of history so I wanted to share this passion with you. And I feel like this conflict is not given the credit it is due so I decided to show you this conflict in an way you might not be used to: graphs.')

st.write('As christmas is slowly approching when I write this, I leave you a song from Sabaton on what I consider to be the best moment of the war (appart from its end): the christmas truce')
st.write('[Here is the song](https://www.youtube.com/watch?v=goXDAFtkJLw)')


st.write('Thank you for reading')
st.write('Author: Yvan LORRAIN')

import sys
sys.path.append('../code/')
import pandas as pd


#from data_handling.handle_data import *
from data_handling.handle_data import get_anime,get_users_ratings
from data_handling.handle_data import get_virgin_data, drop_users_with_too_many_items
from data_handling.handle_data import replace_rating_with_0_and_1
from data_handling.handle_data import get_titles,get_my_ratings
from data_handling.handle_data import drop_users_with_high_proportion_of_ratings



df_anime = get_anime().set_index('anime_id')



df_anime


df_anime.loc[10757]


ratings = get_users_ratings()
anime_titles = get_titles()
my_ratings = get_my_ratings()


df_anime.columns


df_anime


df_anime.index.name = 'item'


no_episodes_info = df_anime[df_anime['episodes'] == 0].index # 0 episodes?
#df_anime = df_anime.drop(index=no_episodes_info)
no_data_info = df_anime[df_anime['aired_string'] == 'Not available'].index # no date?
not_exist = df_anime[df_anime['status'] == 'Not yet aired'].index # does no exist?
indicies_to_drop = no_episodes_info.union(no_data_info.union(not_exist))


columns = ['type', 'source', 'episodes', 'status', 'aired_string','duration','rating', 'score','producer','licensor','studio','genre']


#pd.set_option('display.max_columns', None)
anime_info = df_anime[columns].copy()
anime_info = anime_info.drop(index=indicies_to_drop)
anime_info


anime_info.loc[10757]


anime_info[columns].nunique()


pd.get_dummies(anime_info['type'])


# Delete source


episodes = pd.cut(anime_info['episodes'],bins=[0,1,6,11,14,26,56, 2000],include_lowest=True)
episodes.value_counts()


# delete status


date = anime_info['aired_string']
date


all_date = list(date.values)
result = []
for dat in all_date:
    res = dat.split(',')
    if len(res) > 1:
    #print(res[1][1:5])
        result.append(res[1][1:5])
    else:
        result.append(res[0])


problematic_indicies = []
for i,v in enumerate(result):
    if len(v) get_ipython().getoutput("= 4:")
        problematic_indicies.append(i)


for i in problematic_indicies:
    result[i] = result[i][:4]


years_started = pd.Series(result,dtype=int, name='Year')
years_started


years_started.index = anime_info.index
years_started


len(['old`s','60`s','70`s','80`s','90-95`s','95-99`s','99-02`s','02-05`s','05-07`s','07-10`s','10-12`s','12-14`s','14-16`s','newest'])


len([1910,1960,1970,1980,1990,1995,1999,2002,2005,2007,2010,2012,2014,2016,2021])


years_binarized = pd.cut(years_started, bins=[1910,1960,1970,1980,1990,1995,1999,2002,2005,2007,2010,2012,2014,2016,2021],
                        labels=['old`s','60`s','70`s','80`s','90-95`s','95-99`s','99-02`s','02-05`s','05-07`s','07-10`s','10-12`s','12-14`s','14-16`s','newest'])
years_binarized.value_counts()


years_binarized.index =anime_info.index


years_binarized


pd.get_dummies(years_binarized)


df_anime['duration'].value_counts()


df_anime['duration'].str[:6].unique()


df_anime['duration'] = df_anime['duration'].replace('Unknown', '0 unknown')


duration_df = pd.DataFrame(df_anime['duration'].str[:6].str.split(' ',1).to_list(), columns=['dur','time_type'])
duration_df.dur = duration_df.dur.astype(int)
duration_df.time_type = duration_df.time_type.str.replace('.','')
duration_df.time_type = duration_df.time_type.str.strip()


duration_df = duration_df.loc[duration_df.dur get_ipython().getoutput("= 0]")
duration_df


minutes = duration_df.loc[duration_df.time_type == 'min']
minutes = pd.cut(minutes.dur, bins=[0,2,10,20,35,59])
minutes


pd.get_dummies(anime_info['rating'])


scores = pd.cut(anime_info['score'], bins=[0,4,5,6,7,8,10], include_lowest=True,
               labels=['low_rate','low_middle_rate','middle_rate','mean_rate','high_rate','highest_rate'])
scores.value_counts()


genres = anime_info['genre'].str.lower()
genres


genres = genres.dropna()


genres.loc[10757]


unique_genres = []
for genre in genres.values:
    res = genre.split(',')
    #print(res)
    for g in res:
        if g.strip() not in unique_genres:
            unique_genres.append(g.strip())


len(unique_genres)


genres_df = pd.DataFrame(columns=unique_genres, index=genres.index)


for i,genre in enumerate(genres):
    res = genre.split(',')
    for g in res:
        s=g.strip()
        genres_df.iloc[i][s] = 1


genres_df


genres_df = genres_df.dropna(how='all').fillna(0)


ep_df = pd.get_dummies(episodes)
ep_df.columns = ['1','1_6','6_11','11_14','14_26','26_56','56+']
ep_df


years_df = pd.get_dummies(years_binarized)


df_anime.columns


scores


scores_dummy = pd.get_dummies(scores) # added this line, will crash everything?


#anime_info = df_anime[['title','title_english','title_japanese','title_synonyms']].loc[anime_info.index].join(pd.get_dummies(anime_info['type']).join(ep_df).join(years_binarized).join(scores)).join(genres_df)
anime_info = df_anime[['title','title_english','title_japanese','title_synonyms']].loc[anime_info.index].join(anime_info['type'].to_frame().join(anime_info['episodes'].to_frame()).join(years_started).join(anime_info['score'])).join(genres_df)
anime_info


idx=anime_info.iloc[:,5:].dropna().index


anime_info.loc[idx].shape


anime_info.loc[idx].to_csv('../data/anime/anime_info.csv')




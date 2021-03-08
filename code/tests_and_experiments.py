#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 09:02:59 2021

@author: leo
"""
import pandas as pd
import numpy as np
import time
import seaborn as sns
from Recommender.Algorithm import Recommender

PATH_MY_CORR = '../../anime_recommendation/animeData/my_correlation.csv'

PATH_MY_RATINGS = '../data/my_ratings.csv'

PATH_movies = '../data/ml-latest-small/movies.csv'
PATH_ratings = '../data/ml-latest-small/ratings.csv'

PATH_movies = '../data/ml-latest/movies.csv'
PATH_ratings = '../data/ml-latest/ratings.csv'

#anime
#PATH_ratings = '../../anime_recommendation/animeData/ratings.csv'
#PATH_MY_RATINGS = '../../anime_recommendation/animeData/my_rating.xlsx'


movies = pd.read_csv(PATH_movies).set_index('movieId')

columns = ['userId', 'movieId', 'rating']
#anime
#columns = ['user', 'item', 'rating']
ratings = pd.read_csv(PATH_ratings, usecols=columns)
ratings.columns = ['user', 'item', 'rating']


#weights = pd.read_csv(PATH_MY_CORR ,index_col=0,squeeze = True).iloc[1:]

my_ratings = pd.read_csv(PATH_MY_RATINGS).dropna()
#anime
#my_ratings = pd.read_excel(PATH_MY_RATINGS, usecols=['anime_id', 'title', 'rating'])
my_ratings.columns = ['item', 'title', 'rating']

#TOTAL_WATCHED_ITEMS = 25
#drop users watched few anime
#counts = ratings.user.value_counts()
#ratings[~ratings.user.isin(counts[counts < TOTAL_WATCHED_ITEMS ].index)]

# 2 anime
#titles_id_df = my_ratings.drop(columns=['rating'])
#my_ratings =my_ratings.dropna()

my_ratings.drop(columns=['title'], inplace=True)
# -1 is me, Mario!
MY_USER_ID = -1
my_ratings = my_ratings.sample(frac=1)
test=my_ratings.iloc[20:]
valid=my_ratings.iloc[:20]
#ratings_with_me = ratings.append(test).fillna(MY_USER_ID )
ratings_with_me = ratings.append(my_ratings).fillna(MY_USER_ID )


item = 1
user = -1
data = ratings_with_me
min_items = 30
#alg = Recommender(data, user, weights=weights)
alg = Recommender(data, user, min_items=min_items)
# P = '../data/1.xls'
# rate = pd.read_excel(P)
# # get code for rates
# code = {}
# for item in rate.item.values:
#     cod = item.split(':')[0]
#     code[item] = cod
    
# rate.item = rate.item.map(lambda x: code[x])
# users = list(rate.columns[1:])
# rate = rate.set_index('item')
# test_date = pd.DataFrame(columns=['user','item','rating'])
# for user in users:
#     ser = rate[user]
#     ser.name = 'rating'
#     df = ser.to_frame().reset_index().join(pd.Series(name='user'))
#     df.user = df.user.apply(lambda x: user)
#     test_date = test_date.append(df[['user','item','rating']])
    
# test_date.item = test_date.item.astype(int)
# user = 3712
# item = 641
# weights = rate.corrwith(rate[user]).sort_values().iloc[-6:-1]
# alg = Recommender(test_date,user,weights=weights)

#t1 = time.time()
#rec = alg.score_item(item,k_users=30)
#t2=time.time()

#print('Total Time:', abs(t2-t1))
#print(rec)
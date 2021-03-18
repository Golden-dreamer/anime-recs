#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 09:30:59 2021

@author: leo
"""
import pandas as pd
from Recommender.Algorithm import Recommender

PATH_MY_CORR = '../../anime_recommendation/animeData/my_correlation.csv'

PATH_ratings = '../data/ratings.csv'
PATH_MY_RATINGS = '../data/my_rating.xlsx'

columns = ['user', 'item', 'rating']
ratings = pd.read_csv(PATH_ratings, usecols=columns)
ratings.columns = ['user', 'item', 'rating']


#weights = pd.read_csv(PATH_MY_CORR ,index_col=0,squeeze = True)

my_ratings = pd.read_excel(PATH_MY_RATINGS, usecols=['anime_id', 'title', 'rating'])
my_ratings.columns = ['item', 'title', 'rating']

TOTAL_WATCHED_ITEMS = 25
#drop users watched few anime
counts = ratings.user.value_counts()
ratings[~ratings.user.isin(counts[counts < TOTAL_WATCHED_ITEMS ].index)]

titles_id_df = my_ratings.drop(columns=['rating'])
my_ratings =my_ratings.dropna()

my_ratings.drop(columns=['title'], inplace=True)
# -1 is me, Mario!
MY_USER_ID = -1
my_ratings = my_ratings.sample(frac=1)
#test=my_ratings.iloc[10:]
#valid=my_ratings.iloc[:10]
#ratings_with_me = ratings.append(test).fillna(MY_USER_ID )
ratings_with_me = ratings.append(my_ratings).fillna(MY_USER_ID )


item = 1
user = -1
data = ratings_with_me
min_items = 25
alg = Recommender(data, user, min_items=min_items)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 09:02:59 2021

@author: leo
"""
import pandas as pd
import numpy as np
from Recommender.Algorithm import Recommender


PATH_MY_RATINGS = '..//data/films/my_ratings.csv'

#PATH_movies = '../data/ml-latest-small/movies.csv'
#PATH_ratings = '../data/ml-latest-small/ratings.csv'

PATH_movies = '../data/films/ml-latest/movies.csv'
PATH_ratings = '../data/films/ml-latest/ratings.csv'

movies = pd.read_csv(PATH_movies).set_index('movieId')

columns = ['userId', 'movieId', 'rating']
ratings = pd.read_csv(PATH_ratings, usecols=columns)
ratings.columns = ['user', 'item', 'rating']

my_ratings = pd.read_csv(PATH_MY_RATINGS).dropna()
my_ratings.columns = ['item', 'title', 'rating']

my_ratings.drop(columns=['title'], inplace=True)

# -1 is me, Mario!
MY_USER_ID = -1

my_ratings = my_ratings.sample(frac=1.0)
#test = my_ratings.iloc[20:]
#valid = my_ratings.iloc[:20]
ratings_with_me = ratings.append(my_ratings).fillna(MY_USER_ID )
#ratings_with_me = ratings.append(test).fillna(MY_USER_ID )

item = 1
user = -1
min_items = 40
data = ratings_with_me

#alg = Recommender(data, user,min_items=min_items)
recs = {}
items = ratings.item.unique()
count = 0 

# x_valid = []
# for item in valid.item:
#     recs = alg.score_item(item)
#     x_valid.append(recs)
# x_valid = pd.Series(x_valid)
# y_valid = valid.rating
# y_valid = y_valid.reset_index().rating
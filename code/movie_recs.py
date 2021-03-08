#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 09:02:59 2021

@author: leo
"""
import pandas as pd
from Recommender.Algorithm import Recommender


PATH_MY_RATINGS = '../data/my_ratings.csv'

#PATH_movies = '../data/ml-latest-small/movies.csv'
#PATH_ratings = '../data/ml-latest-small/ratings.csv'

PATH_movies = '../data/ml-latest/movies.csv'
PATH_ratings = '../data/ml-latest/ratings.csv'

movies = pd.read_csv(PATH_movies).set_index('movieId')

columns = ['userId', 'movieId', 'rating']
ratings = pd.read_csv(PATH_ratings, usecols=columns)
ratings.columns = ['user', 'item', 'rating']

my_ratings = pd.read_csv(PATH_MY_RATINGS).dropna()
my_ratings.columns = ['item', 'title', 'rating']

my_ratings.drop(columns=['title'], inplace=True)

# -1 is me, Mario!
MY_USER_ID = -1
ratings_with_me = ratings.append(my_ratings).fillna(MY_USER_ID )

item = 1
user = -1
min_items = 30
data = ratings_with_me

alg = Recommender(data, user,min_items=min_items)

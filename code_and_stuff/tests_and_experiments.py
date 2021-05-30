#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 09:30:59 2021

@author: leo
"""
from Recommender.Algorithm import Recommender

#from data_handling.handle_data import *
from data_handling.handle_data import get_anime,get_users_ratings
from data_handling.handle_data import get_virgin_data, drop_users_with_too_many_items
from data_handling.handle_data import replace_rating_with_0_and_1, transform_ratings
from data_handling.handle_data import get_titles, get_my_ratings
from data_handling.handle_data import drop_users_with_high_proportion_of_ratings

import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity

# -1 is me, Mario!
MY_USER_ID = -1

df_anime = get_anime()

ratings = get_users_ratings()

my_ratings = get_my_ratings()

#ratings_with_me = ratings.append(my_ratings).fillna(MY_USER_ID )

data_virgin = get_virgin_data(ratings, df_anime, 5,5,7)

ITEMS_THRESHOLD = 1500
data_too_many_watched = drop_users_with_too_many_items(data_virgin, ITEMS_THRESHOLD)

data_without_happy_users = drop_users_with_high_proportion_of_ratings(data_too_many_watched,
                                                                        threshold=0.9)
#data_extreme_like_or_not = replace_rating_with_0_and_1(data_without_happy_users)
data = data_without_happy_users
#data_final = data_extreme_like_or_not
#pivot = data_final.loc[data_final.item.isin(my_ratings.item)].pivot(index='user',
#                                                                    columns='item').rating
sheet_name = 'NormRatings'
rate = pd.read_excel('/home/leo/ML/Assignment 5.xlsx')
rate=rate.drop(columns=['Mean'])
rate=rate.iloc[:20]
rate=rate.set_index('User')
film='1: Toy Story (1995)'
sw='1210: Star Wars: Episode VI - Return of the Jedi (1983)'
rate = rate.fillna(0)
x1 = rate[film].to_numpy().reshape(1,-1)
x2 = rate[sw].to_numpy().reshape(1,-1)


cosine_similarity(x1,x2)

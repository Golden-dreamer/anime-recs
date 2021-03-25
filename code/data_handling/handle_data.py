#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 08:31:55 2021

@author: leo
"""
import pandas as pd
import numpy as np

PATH_MY_CORR = '../data/anime/my_corr.csv'
PATH_RATINGS = '../data/anime/ratings.csv'
PATH_MY_RATINGS = '../data/anime/my_rating.xlsx'
PATH_REPLACED_RATINGS = '../data/anime/replaced_ratings.csv'
PATH_TO_ANIME_TITLES_INFO = '../data/anime/AnimeList.csv'


def get_users_ratings(drop_few_watches=True, min_watched=25):
    columns = ['user', 'item', 'rating']
    ratings = pd.read_csv(PATH_RATINGS, usecols=columns)
    ratings.columns = ['user', 'item', 'rating']    
    if not drop_few_watches:
        return ratings
    #drop users watched  too few anime
    TOTAL_WATCHED_ITEMS = min_watched
    user_counts = ratings.user.value_counts()
    ratings = ratings[~ratings.user.isin(
        user_counts[user_counts < TOTAL_WATCHED_ITEMS].index)]

    return ratings

def get_my_ratings():    
    cols = ['anime_id', 'rating']
    my_ratings = pd.read_excel(PATH_MY_RATINGS, usecols=cols)
    my_ratings.columns = ['item', 'rating']
    
    my_ratings.dropna(inplace=True)
    #my_ratings = my_ratings.loc[~(my_ratings.rating == 1)]    
    return my_ratings

def get_titles():
    cols = ['anime_id','title']
    titles = pd.read_excel(PATH_MY_RATINGS, usecols=cols)
    titles.columns = ['item','title']
    return titles


def drop_users_with_too_many_items(data,too_many_items=500):
    items_count_by_user = data.groupby('user',as_index=False)['item'].count()
    heavy_users = items_count_by_user [items_count_by_user .item > too_many_items].user
    data_refined = data.loc[~data.user.isin(heavy_users)]
    return data_refined


def drop_users_with_high_proportion_of_ratings(data,threshold=0.9,
                                               positive_idx=[7,8,9,10]):
    user_rate_count = data.groupby('user')['rating'].value_counts()
    user_rate_count.name = 'rate_count'
    items_total_count = data.groupby('user')['item'].count()
    
    users_rate_proportion = user_rate_count / items_total_count
    positive_rate_per_user_proportion = users_rate_proportion.loc[:,positive_idx].groupby('user').sum()
    users_think_every_item_is_good = positive_rate_per_user_proportion[positive_rate_per_user_proportion > threshold].index
    data_without_happy_users = data[~data.user.isin(users_think_every_item_is_good )]
    return data_without_happy_users 

def get_anime():
    return pd.read_csv(PATH_TO_ANIME_TITLES_INFO)


def replace_rating_with_0_and_1(data):
    new_data = data.copy(deep=True)
    new_data.loc[new_data['rating'] < 6, 'rating'] = 0
    new_data.loc[new_data['rating'] > 5, 'rating'] = 1
    return new_data

def get_virgin_data(data, df_anime, n_ecchi=10, n_hentai=10,rate_threshold=5):
    #df_anime.genre = df_anime.genre.str.lower()
    #df_anime.genre = df_anime.genre.str.strip()
    items_e  = df_anime.ecchi[df_anime.ecchi == 1].index
    items_h  = df_anime.hentai[df_anime.hentai == 1].index
    #items_e = df_anime[(df_anime.genre.str.contains('ecchi')) > 0]['anime_id']
    #items_h = df_anime[(df_anime.genre.str.contains('hentai')) > 0]['anime_id']
    ecchi_df = data[data.item.isin(items_e)]
    count_pos_rate_for_ecchi = ecchi_df[ecchi_df.rating > rate_threshold].groupby('user')['item'].count()
    guilty = count_pos_rate_for_ecchi[count_pos_rate_for_ecchi > n_ecchi]
    guilty_users_e = guilty.index
    
    #virginity = data[~data.user.isin(guilty_users_e)]

    hentai = data[data.item.isin(items_h)]
    count_pos_rate_for_hentai = hentai[hentai.rating > rate_threshold].groupby('user')['item'].count()
    guilty_h = count_pos_rate_for_hentai[count_pos_rate_for_hentai > n_hentai]
    guilty_users_h = guilty_h.index
    
    #return  virginity[~virginity.user.isin(guilty_users_h)]
    return data[~data.user.isin(guilty_users_e.union(guilty_users_h))]
    


def split_df(df, test_samples=6, seed=42):
    np.random.seed(seed)
    data = df.sample(frac=1.0)
    test = data.groupby('user',as_index=False).nth([range(test_samples)])
    train = data.loc[data.index.difference(test.index)]
    return train, test

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 07:55:12 2021

@author: leo
"""
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
def get_user_rating( user,data):
        return data.loc[data['user'] == user].set_index('item')['rating']
    
class Recommender:
    def __init__(self, data, user_id, min_items=0,  weights=None,titles=None,
                 cos=False):
        self.data = data
        self.users_mean = data.groupby(['user'])['rating'].mean()
        self.user_id = user_id
        self.user_ratings = get_user_rating(user_id,data)

        self.user_mean = data[data['user'] == user_id]['rating'].mean()
        self.titles = titles
        self.cos = cos
        
        if weights is None:
            print('Calculating correlation')
            self.weights = self.calculate_sim(min_items)
        else:
            self.weights = weights
        
    def calculate_sim(self, min_items):
        my_items = list(self.user_ratings.index)
        assert(len(my_items) >= min_items) , f'''min_items({min_items}) must be not greater then users_watched items!
        users total watched items: {len(my_items)}'''
        data = self.data
        # calclulate corr is make sense with items me, user, already watched
        common_items = data[data.item.isin(my_items)].groupby(['user'], as_index=False)['item'].count()
        common_items = common_items.sort_values('item', ascending=False)
        # users watched with me at least min_items
        users_common_items_me = list(common_items[common_items.item > min_items].user)
        new_data = data.loc[(data.item.isin(my_items)) & (data.user.isin(users_common_items_me))]
        
        pivot = new_data.pivot(columns='user',index='item')
        pivot.dropna(how='all', inplace=True)
        pivot.columns = pivot.columns.droplevel(0)
        if self.cos: # calculate cosine similarity for user_id
            v1 = pivot[self.user_id].to_numpy().reshape(1,-1)
            cos_sim = cosine_similarity(v1,pivot.fillna(0).T)
            weights = pd.DataFrame(cos_sim).T[0]
            weights.index = pivot.columns
            weights = weights.sort_values(ascending=False)
            weights.name = 'weights'
            return weights.iloc[1:] # skip myself
        my_corr = pivot.corrwith(pivot[self.user_id]).sort_values(ascending=False).dropna()
        my_corr.name = 'weights'
        return my_corr.iloc[1:] # skip myself
    
    def score_items(self, items, k_users=50):
        raise NotImplementedError
        data = self.data
        pass
        
    def score_item(self, item, k_users=50):
        data = self.data                    
        users = self.weights.iloc[:k_users].index   
        # V - all who watched this item
        V = data[data.item == item]
        # select important users(with whom I have good enough corr)
        rv = V.set_index('user').reindex(users).dropna()['rating'] # pick users I need
        rv_mean = self.users_mean.loc[users]        
        W = self.weights.iloc[:k_users]
        index_to_sum = rv.index
        if len(index_to_sum) == 0: # not enough users watched this item
            return 0
        rate = ((rv-rv_mean) * W).sum() / W[index_to_sum].sum() + self.user_mean
        return rate
    
    def recs(self, items, k=50, threshold=5, return3list=False):
        total_recs = []
        positive_recs = []
        negative_recs = []
        for item in items:
            if self.titles is None:
                anime_title = item 
            else:
                anime_title = self.titles[self.titles.item == item].title.iloc[0]
            rec = self.score_item(item,k)
            total_recs.append((anime_title , rec))
            if not return3list:
                continue
            if rec > threshold:
                positive_recs.append(anime_title )
            else:
                negative_recs.append(anime_title )
        if return3list:
            return total_recs, positive_recs, negative_recs
        else:
            return total_recs
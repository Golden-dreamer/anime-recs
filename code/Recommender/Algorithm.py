#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 07:55:12 2021

@author: leo
"""

def get_user_rating( user,data):
        return data.loc[data['user'] == user].set_index('item')['rating']
    
class Recommender:
    def __init__(self, data, user, min_items=0,  weights=None,titles=None):
        self.data = data
        self.users_mean = data.groupby(['user'])['rating'].mean()
        self.user = user
        self.user_ratings = get_user_rating(user,data)

        self.user_mean = data[data['user'] == user]['rating'].mean()
        self.titles = titles
        
        if weights is None:
            print('Calculating correlation')
            self.weights = self.calculate_corr(min_items)
        else:
            self.weights = weights
        
    def calculate_corr(self, min_items):
        my_items = list(self.user_ratings.index)
        assert(len(my_items) >= min_items) , f'''min_items({min_items}) must be not greater then users_watched items!
        users total watched items: {len(my_items)}'''
        data = self.data
        common_items = data[data.item.isin(my_items)].groupby(['user'], as_index=False)['item'].count()
        common_items = common_items.sort_values('item', ascending=False)
        # users watched with me at least min_items
        users_common_items_me = list(common_items[common_items.item > min_items].user)
        new_data = data.loc[(data.item.isin(my_items)) & (data.user.isin(users_common_items_me))]
        
        pivot = new_data.pivot(columns='user',index='item')
        pivot.dropna(how='all', inplace=True)
        pivot.columns = pivot.columns.droplevel(0)
        my_corr = pivot.corrwith(pivot[self.user]).sort_values(ascending=False).dropna()
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
    
    def recs(self, items, k=50, threshold=5):
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
            if rec > threshold:
                positive_recs.append(anime_title )
            else:
                negative_recs.append(anime_title )
        return total_recs, positive_recs, negative_recs
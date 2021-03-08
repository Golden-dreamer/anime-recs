#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 07:55:12 2021

@author: leo
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 07:43:09 2021

@author: leo
"""

def get_user_rating( user,data):
        return data.loc[data['user'] == user].set_index('item')['rating']
    
class Recommender:
    def __init__(self, data, user, min_items=0, threshold=0, weights=None):
        self.data = data
        self.users_mean = data.groupby(['user'], as_index=False)['rating'].mean()
        self.user = user
        self.user_ratings = get_user_rating(user,data)

        self.user_mean = data[data['user'] == user]['rating'].mean()
        self.threshold = threshold
        
        if weights is None:
            print('Calculating correlation')
            self.weights = self.calculate_corr(min_items)
        else:
            self.weights = weights
        
    def calculate_corr(self, min_items):
        my_items = list(self.user_ratings.index)
        data = self.data
        common_items = data[data.item.isin(my_items)].groupby(['user'], as_index=False)['item'].count()
        common_items = common_items.sort_values('item', ascending=False)
        # users watched with me at least min_items
        users_common_items_me = list(common_items[common_items.item > min_items].user)
        new_data = data.loc[(data.item.isin(my_items)) & (data.user.isin(users_common_items_me))]
        
        pivot = new_data.pivot(columns='user',index='item')
        pivot.dropna(how='all', inplace=True)
        pivot.columns = pivot.columns.droplevel(0)
        my_corr = pivot.corrwith(pivot[self.user]).sort_values(ascending=False)
        return my_corr.iloc[1:] # skip myself
        
    def score_item(self, item, k_users=50):
        data = self.data    
        #deprecated
        def calc_W(k_users, users,min_items=10):            
            items = self.user_ratings.index
            #drop item if I watched this, try to predict like I have never seen this
            if item in items:
                items = items.drop(item)
            #choose only data that I watched
            pivot = data.loc[data['user'].isin(users) & 
                             data['item'].isin(items)].pivot(
                                 columns='user',
                                 index='item')
            pivot.columns = pivot.columns.droplevel(0)
            self.pivot = pivot
            
            counts = pivot.count()
            columns_to_drop = counts[counts < min_items].index
            pivot = pivot.drop(columns=columns_to_drop)
            
            W = pivot.corrwith(self.user_ratings).dropna().sort_values(ascending=False)
#            self.neg_W = W[W < -self.threshold].copy(deep=True)
            W = W[(W > self.threshold)]
            return W.iloc[:k_users]
 
        user = self.user
        V = data[data['item'] == item] # neighbour V
        # delete myself
        V = V.loc[~(V['user'] == user)]
        self.V =  V
        self.users = self.V.user.unique()
        self.users_v_ratings = self.V[['user','rating']].set_index('user')['rating']
        #users_V_mean = users_mean.loc[V['user']]['rating']
        users_V_mean  = self.users_mean[self.users_mean['user'].isin(self.V['user'])]
        self.users_V_mean = users_V_mean.set_index('user')['rating']
            
        
        users = self.users
        #if self.weights is None:
            #self.weights = calc_W(k_users,users)
            
        #W = self.weights.iloc[:k_users]
            #W = calc_W(k_users, users)
            
        W = self.weights.iloc[:k_users]
        rv = self.users_v_ratings.reindex(W.index) # rating user V
        self.rv = rv
        rv_mean = self.users_V_mean.reindex(W.index)
        self.rv_mean = rv_mean
        index_to_sum = rv[~rv.isna()].index
        self.i = index_to_sum
        rate = ((rv-rv_mean) * W).sum() / W[index_to_sum].sum() + self.user_mean
        return rate
        '''
        print('Fuck')
        W = self.weights.iloc[:k_users]
        rv = self.users_v_ratings.reindex(W.index) # rating user V
        rv_mean = self.users_V_mean.reindex(W.index)
        index_to_sum = rv[~rv.isna()].index
        rate = ((rv-rv_mean) * W).sum() / W[index_to_sum].sum() + self.user_mean
        return rate
        ##self.users_v_ratings.loc[s.index.intersection(labels)]
        self.W = W
        users = W.index
        self.check = users        
        user_mean = self.user_mean
        #pick same users that exists in W

        users_v_ratings = self.users_v_ratings.loc[users]
        users_V_mean = self.users_V_mean.loc[users]
        self.item_rec = (( users_v_ratings - users_V_mean ) * W).sum() / W.sum() + user_mean
        
        return self.item_rec
        '''    
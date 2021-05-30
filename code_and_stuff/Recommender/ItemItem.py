#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 18:59:08 2021

@author: leo
"""
from scipy.spatial.distance import cosine

def get_user_rating( user,data):
        return data.loc[data['user'] == user].set_index('item')['rating']
  
class ItemItem():
    def __init__(self, data, user_id, min_items=0,  weights=None,titles=None):
        #norm = (data.T - data.T.mean()).T
        self.data = data
        self.users_mean = data.groupby(['user'])['rating'].mean()
        self.user_id = user_id
        self.user_ratings = get_user_rating(user_id,data)

        self.user_mean = data[data['user'] == user_id]['rating'].mean()
        self.titles = titles
        
        if weights is None:
            print('Calculating correlation')
            self.weights = self.calculate_corr(min_items)
        else:
            self.weights = weights
    
    def calculate_corr(self, min_items):
        data = self.data
        
        
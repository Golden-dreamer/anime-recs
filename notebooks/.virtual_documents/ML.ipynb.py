import sys
sys.path.append('../code/')


from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.model_selection import ShuffleSplit, GridSearchCV, train_test_split

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.linear_model import LinearRegression, LogisticRegression, SGDClassifier

from sklearn.metrics import confusion_matrix
from sklearn.metrics import mean_absolute_error, mean_squared_error

import matplotlib.pyplot as plt
import seaborn as sns


#from data_handling.handle_data import *
from data_handling.handle_data import get_anime,get_users_ratings
from data_handling.handle_data import get_virgin_data, drop_users_with_too_many_items
from data_handling.handle_data import replace_rating_with_0_and_1
from data_handling.handle_data import get_titles,get_my_ratings
from data_handling.handle_data import drop_users_with_high_proportion_of_ratings
from data_handling.handle_data import transform_ratings



from sklearn.tree import export_graphviz
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, MinMaxScaler, RobustScaler


'''
def transform_ratings(ratings_got):
    ratings = ratings_got.copy(deep=True)
    ratings = ratings.replace([1,2],1)
    #ratings = ratings.replace([3,4],2)
    ratings = ratings.replace([3,4],1)
    #ratings = ratings.replace([5,6],3)
    ratings = ratings.replace([5,6,7],3)
    ratings = ratings.replace([8,9,10],5)
    #ratings = ratings.replace([7,8],4)
    #ratings = ratings.replace([9,10],5)
    return ratings'''


import pandas as pd
from sklearn.neighbors import KNeighborsClassifier


from Recommender.Algorithm import Recommender


K_ECCHI = 3 #best 3 ?15
K_HENTAI = 3 #best 3 ?15

MIN_WACTHED = 14

K_BIG_ITEMS = 1500 # best 1000 ?1500

POSITIVE_RATE_PROPORTION_THRESHOLD = 0.89 #best 0.9 ?1
POSITIVE_IDX=[5] # best 5
# THOUGHT: maybe use 3 classes?

MIN_ITEMS = 15 # best 15
CORRELATION_THRESHOLD = 0.5 #best 0.5
K_USERS_POS = 10# best 20 ?22
K_USERS_NEG = 4# best 15
#best RandomForestClassifier


#PATH_TO_ANIME_DATA = "../data/anime/anime_info.csv"
#anime = pd.read_csv(PATH_TO_ANIME_DATA,index_col=0)
anime = get_anime()


my_ratings = get_my_ratings()


data = get_users_ratings(min_watched=MIN_WACTHED)



data = get_virgin_data(data,anime,K_ECCHI,K_HENTAI)


data.rating = transform_ratings(data.rating)
my_ratings.rating = transform_ratings(my_ratings.rating)


data = drop_users_with_too_many_items(data,K_BIG_ITEMS)



#data = drop_users_with_high_proportion_of_ratings(data,POSITIVE_RATE_PROPORTION_THRESHOLD, POSITIVE_IDX)
data


anime.score.unique()


categories = ['low_rate','low_middle_rate', 'middle_rate','mean_rate','high_rate','highest_rate']


anime_dropped = anime.drop(columns=['Year','score'])


my_rate_anime_combine = my_ratings.set_index('item').join(anime_dropped.iloc[:,4:])
my_rate_anime_combine


NA_indicies = my_rate_anime_combine.iloc[:,1:].isna().all(axis=1)[my_rate_anime_combine.iloc[:,1:].isna().all(axis=1) > 0].index


my_rate_anime_combine = my_rate_anime_combine.drop(index=NA_indicies)
#Full_train


idx = my_ratings.set_index('item').index



pivot = data.loc[data.item.isin(idx)].pivot(columns='user',index='item').rating


#corr_piv = pivot.loc[pivot.index.isin(my_ratings.set_index('item').index)].dropna(how='all')
corr_piv = pivot


users = corr_piv.count()[corr_piv.count() > MIN_ITEMS].index


corr = pivot[users].corrwith(my_ratings.set_index('item').rating)


corr = corr.dropna().sort_values(ascending=False)
#corr


corr


def find_besk_k_users(df, model, corr, k_pos, k_neg, users_only=False):
    mse = float('inf')
    best_pos = 0
    best_neg = 0
    pos_cor = corr[corr > CORRELATION_THRESHOLD]
    neg_cor = corr[corr < -CORRELATION_THRESHOLD].sort_values()
    
    y = df.iloc[:,0]
    for i in range(0,k_pos+1):
        print(i)
        for j in range(0, k_neg+1):
            users_pos = pos_cor.iloc[:i].index
            users_neg =  neg_cor.iloc[:j].index
            users = users_neg.union(users_pos)
            if len(users) == 0 and users_only:
                continue
            X_users_only = df.iloc[:, 57:][users]
            if users_only:
                y_preds = cross_val_predict(model, X_users_only, y, cv=5)
            else:
                X_full = df.iloc[:,1:57].join(X_users_only) #  1 is skip rating
                y_preds = cross_val_predict(model, X_full, y, cv=5)
                
            mse_new = mean_squared_error(y_preds, y)
            if mse > mse_new:
                mse = mse_new
                best_pos = i
                best_neg = j
    print(mse)
    return mse, best_pos, best_neg


df = my_rate_anime_combine.join(pivot.fillna(0))
drop_idx = df.iloc[:,58:].isna().all(axis=1)[df.iloc[:,58:].isna().all(axis=1) > 0].index
df = df.drop(index=drop_idx)


#mse, bp, bn = find_besk_k_users(df, RandomForestClassifier(random_state=42),corr,25,25,True)


users_pos = corr[corr > CORRELATION_THRESHOLD].iloc[:K_USERS_POS].index
users_neg =  corr[corr < -CORRELATION_THRESHOLD].sort_values().iloc[:K_USERS_NEG].index
users = users_neg.union(users_pos)


len(users)


#Full_train = Full_train.join(pivot.fillna(-1))
Full_train = my_rate_anime_combine.join(pivot[users].fillna(0))


Full_train.shape


drop_idx = Full_train.iloc[:,58:].isna().all(axis=1)[Full_train.iloc[:,58:].isna().all(axis=1) > 0].index


Full_train = Full_train.drop(index=drop_idx)


y_full = Full_train.rating
X_full = Full_train.iloc[:,1:]


X_users_only = X_full.iloc[:,56:] # not bad with best


x_train, x_valid, y_train, y_valid = train_test_split(X_full, y_full, test_size=7,random_state=1)


model = KNeighborsClassifier(n_neighbors=3)


total_preds = cross_val_predict(model, X_users_only, y_full, cv=5) # X_full


confusion_matrix(total_preds, y_full).T


model.fit(x_train, y_train)


model.score(x_train, y_train)


preds=model.predict(x_valid)


y_valid


le = LinearRegression()
le.fit(x_train, y_train)
le.score(x_train, y_train)


preds = le.predict(x_valid)
preds


le.score(x_valid, y_valid)


score = cross_val_score(le, X_users_only, y_full, cv=5) # X_full
score.mean()


y_preds = cross_val_predict(le, X_users_only, y_full, cv=5) # X_users_only
y_preds


mean_squared_error(y_preds, y_full)


y_full.values


res = y_full.to_frame().reset_index().join(pd.Series(y_preds, name='le'))


res.tail(11)


for i, preds in enumerate(y_preds):
    if preds > 10:
        y_preds[i] = 10
    elif preds < 1:
        y_preds[i] = 1


y_preds


clf = RandomForestClassifier(random_state=42)
clf.fit(x_train, y_train)
clf.score(x_train,y_train)


clf.score(x_valid,y_valid)


preds = clf.predict(x_valid)
preds


y_valid.values


score = cross_val_score(clf, X_users_only, y_full, cv=5) # X_full
score.mean()


score


y_preds = cross_val_predict(clf, X_users_only, y_full, cv=5) # X_users_only


matrix = confusion_matrix(y_full, y_preds)
matrix


model = LogisticRegression(C=0.7, random_state=42,max_iter=500, class_weight={1:10, 3:1,4:1,5:1})
#model = clf
y_preds = cross_val_predict(model, X_full, y_full, cv=5) # X_users_only
matrix = confusion_matrix(y_full, y_preds)
matrix


for i in range(len(matrix)):
    print(matrix[i].sum())


model.fit(X_full, y_full)


bad_rates_count_as_good = matrix[0][2] + matrix[0][3] + matrix[1][2] + matrix[1][3]
good_rates_count_as_bad = matrix[2][0] + matrix[2][1] + matrix[3][0] + matrix[3][1]
bad_rates_true = matrix[0][0] + matrix[0][1] + matrix[1][0] + matrix[1][1]
good_rates_true = matrix[2][2] + matrix[2][3] + matrix[3][2] + matrix[3][3]
print(bad_rates_count_as_good) # 5
print(good_rates_count_as_bad) # 9
print(bad_rates_true) # 36
print(good_rates_true) # 11


#for i, val in enumerate(y_preds):
#    print(y_preds[i],' ; ',y_full.values[i])


from sklearn.dummy import DummyClassifier


dummy = DummyClassifier(strategy='most_frequent')


dummy_score = cross_val_score(dummy, X_full, y_full, cv=5)
dummy_score.mean()


dummy_score


dummy.fit(x_train,y_train)


dummy.predict(x_valid)


dummy.score(x_train, y_train)


dummy.score(x_valid, y_valid)


y_full.unique()


#fig, ax = plt.subplots(figsize=(50, 50))  # whatever size you want
#plot_tree(clf, filled=True,fontsize=30, ax=ax, feature_names=Full_train.columns)


#fn=X_full.columns
#cn=y_full.unique()
#fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (14,19), dpi=800)
#plot_tree(clf.estimators_[1],
#               feature_names = fn, 
#               #class_names=cn,
#               filled = True);


#fig, ax = plt.subplots(figsize=(50, 50))  # whatever size you want
#plot_tree(clf, filled=True,fontsize=30, ax=ax, feature_names=Full_train.columns)


#grid = GridSearchCV(clf, parameters)


#grid.fit(X_full, y_full)


#clf = RandomForestRegressor(max_depth=5, n_estimators=150, n_jobs=8,random_state=42)


#fig, ax = plt.subplots(figsize=(10, 30))  # whatever size you want
#plot_tree(clf, filled=True,fontsize=20, ax=ax,class_names=cn,feature_names=X_full.columns)



pivot_full = data[data.user.isin(users)].pivot(columns='user', index='item').rating


#X = anime.iloc[:,4:].join(pivot.fillna(-1))
#X = anime.iloc[:,4:].join(pivot_full[users].fillna(0))
X = anime_dropped.iloc[:,4:].join(pivot_full.fillna(0))
#X = anime.iloc[:,4:]


drop_idx = X.iloc[:,58:].isna().all(axis=1)[X.iloc[:,58:].isna().all(axis=1) > 0].index


len(drop_idx)


#preds = clf.predict(pivot_full.fillna(0))
#model = le #X_full  X_users_only
model.fit(X_users_only, y_full)
preds = model.predict(X.iloc[:,56:].drop(index=drop_idx))


recs = pd.Series(preds,index=X.drop(index=drop_idx).index, name='preds')


recs.sort_values(ascending=False)


items=recs.sort_values(ascending=False)


preds = anime[['title']].join(items).dropna().sort_values('preds', ascending=False)


clear_preds = preds.loc[~preds.index.isin(my_ratings.set_index('item').index)]


clear_preds.head(50) #578


preds[preds.title.str.contains('Re:Zero')]


#clear_preds[clear_preds.preds > 3.5].head(50)


preds[preds.title.str.contains('One')]




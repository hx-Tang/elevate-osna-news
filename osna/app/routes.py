from flask import render_template, flash, redirect, session
from scipy.sparse import hstack

from osna.clf_train import make_features
from . import app
from .forms import MyForm
from .. import credentials_path, clf_path, clf_path2, clf_path3, clf_path_
from osna.get_wordlist import get_text, get_source

import pickle
import numpy as np
import pandas as pd
import sys
import json
from TwitterAPI import TwitterAPI
from ..mytwitter import Twitter

from keras.layers import Dropout, Flatten
import keras

# clf, vec = pickle.load(open(clf_path, 'rb'))
# print('read clf %s' % str(clf))
# print('read vec %s' % str(vec))

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = MyForm()

    if form.validate_on_submit():

        input_field = form.input_field.data
        method = form.select_field.data
        flash(input_field)

        news = get_tweets(input_field)
        if method == '1':
            pred, proba, top_features, title, text = predict(news)
            return render_template('myform.html', title='', form=form, news_title=title, news=text, pred=pred,
                                   proba=max(proba * 100),
                                   top_features=top_features)
        else:
            pred, proba, title, text = predict_(news)
            return render_template('myform.html', title='', form=form, news_title=title, news=text, pred=pred,
                                   proba=max(proba * 100))
    return render_template('myform.html', title='', form=form)


def get_tweets(input_field):
    t = Twitter(credentials_path)
    # search news and get tweets
    new_tweets = t._search_news(input_field)
    return new_tweets


def predict(df):
    vec1, vec2, vec3, vecf, lr = pickle.load(open(clf_path, 'rb'))

    df = make_features(df)

    features = df.loc[:, ['avg_retweet', 'avg_favorite', 'var_time', 'var_desc']]
    features = features.to_dict('records')

    text = get_text(list(df.text))
    title = get_text(list(df.title))
    source = get_source(list(df.source))

    x1 = vec1.transform(text)
    x2 = vec2.transform(title)
    x3 = vec3.transform(source)
    xf = vecf.transform(features)

    x = hstack([x1, x2, x3, xf])

    pred = lr.predict(x)[0]
    proba = lr.predict_proba(x)[0]

    top_features = []
    features = np.array(vec1.get_feature_names() + vec2.get_feature_names() + vec3.get_feature_names() + vecf.get_feature_names())

    x = x.tocsr()

    if pred == 'fake':
        coef = -lr.coef_[0]
    else:
        coef = lr.coef_[0]

    for j in np.argsort(coef[x[0].nonzero()[1]])[::-1][:15]:  # start stop ste
        idx = x[0].nonzero()[1][j]
        top_features.append({'feature': features[idx], 'coef': coef[idx]})

    return pred, proba, top_features, list(df.title)[0], list(df.text)[0]


def predict_(df):
    keras.backend.clear_session()

    vec1, vec2, vec3, vecf, model = pickle.load(open(clf_path_, 'rb'))

    df = make_features(df)

    features = df.loc[:, ['avg_retweet', 'avg_favorite', 'var_time', 'var_desc']]
    features = features.to_dict('records')

    text = get_text(list(df.text))
    title = get_text(list(df.title))
    source = get_source(list(df.source))

    x1 = vec1.transform(text)
    x2 = vec2.transform(title)
    x3 = vec3.transform(source)
    xf = vecf.transform(features)

    x = hstack([x1, x2, x3, xf]).tocsr()

    pred = model.predict(x)

    proba = max(pred[0], 1-pred[0])

    if pred[0] < 0.5:
        pred = 'fake'
    else:
        pred = 'real'

    return pred, proba, list(df.title)[0], list(df.text)[0]

# def predict3(df):
#     vec1, vec2, vec3, lr = pickle.load(open(clf_path3, 'rb'))
#
#     text = get_text(list(df.text))
#     title = get_text(list(df.title))
#     source = get_source(list(df.source))
#
#     x1 = vec1.transform(text)
#     x2 = vec2.transform(title)
#     x3 = vec3.transform(source)
#
#     # features = make_features(df)
#
#     x = np.hstack([x1, x2, x3])
#     # x = x1
#
#     top_features = []
#
#     pred = lr.predict(x)[0]
#     proba = lr.predict_proba(x)[0]
#
#     top_features = []
#     features = vec1.get_feature_names()
#
#     coef = [-lr.coef_[0], lr.coef_[0]]
#
#     for j in np.argsort(coef[0][x[0].nonzero()[1]])[::-1][:3]:  # start stop step
#         idx = x[0].nonzero()[1][j]
#         top_features.append({'feature': features[idx], 'coef': coef[0][idx]})
#
#     return pred, proba, top_features

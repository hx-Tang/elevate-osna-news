# -*- coding: utf-8 -*-

"""Console script for elevate_osna."""
import click
import glob
import pickle
import sys
import pandas as pd

import numpy as np
import pandas as pd
import re
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, classification_report

from . import credentials_path, clf_path


@click.group()
def main(args=None):
    """Console script for osna."""
    return 0


@main.command('web')
@click.option('-t', '--twitter-credentials', required=False, type=click.Path(exists=True), show_default=True,
              default=credentials_path, help='a json file of twitter tokens')
@click.option('-p', '--port', required=False, default=5000, show_default=True, help='port of web server')
def web(twitter_credentials, port):
    from .app import app
    app.run(host='127.0.0.1', debug=True, port=port)

@main.command('stats')
@click.argument('directory', type=click.Path(exists=True))
def stats(directory):
    print('reading from %s' % directory) 
    from .stats import Mystats
    Mystats(directory)


@main.command('train')
@click.argument('directory', type=click.Path(exists=True))
def train(directory):
    """
    Train a classifier and save it.
    """
    print('reading from %s' % directory)
    # (1) Read the data...
    #
    # (2) Create classifier and vectorizer.
    clf = LogisticRegression() # set best parameters 
    vec = CountVectorizer()    # set best parameters
    
    # (3) do cross-validation and print out validation metrics
    # (classification_report)

    # (4) Finally, train on ALL data one final time and
    # train...
    # save the classifier
    pickle.dump((clf, vec), open(clf_path, 'wb'))


def make_features(df):
    ## Add your code to create features.
    pass


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

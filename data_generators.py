
import pymongo
import json
import configparser
import FAIRsoft

from pymongo import MongoClient
from datetime import datetime
from collections import Counter
import numpy as np
from FAIRsoft.indicators_evaluation import FAIR_indicators_eval


# connecting to db
config = configparser.ConfigParser()
config.read('config_db.ini')
DBHOST = config['MONGO_DETAILS']['DBHOST']
DBPORT = config['MONGO_DETAILS']['DBPORT']
DATABASE = config['MONGO_DETAILS']['DATABASE']
TOOLS = config['MONGO_DETAILS']['TOOLS']
ALAMBIQUE = config['MONGO_DETAILS']['ALAMBIQUE']
STATS = config['MONGO_DETAILS']['STATS']


connection = MongoClient(DBHOST, int(DBPORT))
tools = connection[DATABASE][TOOLS]
stats = connection[DATABASE][STATS]


def count_tools_per_source():
    count_source = {
        'variable':'tools_counts_per_source',
        'version': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'data': []
    }
    sources_lab ={'github', 'galaxy','toolshed','bioconda', 'biotools', 'bioconductor', 'sourceforge', 'bitbucket', 'opeb_metrics'}
    source_match ={'bioconda':'bioconda', 'bioconda_recipes':'bioconda', 'bioconda_conda':'bioconda',
            'galaxy_metadata':'toolshed', 'toolshed':'toolshed',
            'github':'github',
            'biotools':'biotools',
            'bioconductor':'bioconductor',
            'sourceforge':'sourceforge',
            'bitbucket':'bitbucket',
            'opeb_metrics':'opeb_metrics',
            'galaxy':'galaxy'}     
        

    counts = {}
    for lab in sources_lab:
        counts[lab] = 0

    N = 0
    for tool in tools.find():
        N = N + 1
        sources = tool['source']
        sources = list(set([source_match[s] for s in sources]))
        for label in sources:
            counts[label] += 1
    
    for source in counts.keys():
        count_source['data'].append({
            "source":source,
            "count":counts[source]
        })  
        
    stats.insert_one(count_source)

def count_tools():
    count = {
        'variable':'tools_count',
        'version': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'data': tools.count_documents({})
    }
    stats.insert_one(count)

  
#count_tools_per_source()
#count_tools()
ids = {'F':['F3','F2', 'F1'],
       'A':['A3', 'A1'],
       'I':['I3', 'I2', 'I1'],
       'R':['R4', 'R3', 'R2', 'R1']
      }

def scores_in_dict(metrics):
    '''
    From a list of scores by instance, returns a dictinary of
    scores by principle
    '''
    # initializing dict with scores
    scores = {}
    for p in ids.keys():
        scores[p]={}
        for e in ids[p]:
            scores[p][e] = []

    # populating indicators dict with scores
    for inst in metrics:
        for p in ids.keys():
            for e in ids[p]:
                scores[p][e].append(float(round(inst[e], 2)))

    return scores

def distribution_of_scores(scores):
    '''
    Compute distribution of a set of values
    '''
    for p in ids.keys():
        for e in ids[p]:
            scores[p][e] = np.array(scores[p][e])
            scores[p][e] = scores[p][e].astype(np.float)
            scores[p][e] = Counter(scores[p][e])
            scores[p][e] = {k: v for k, v in sorted(scores[p][e].items(), key=lambda item: item[0])}

    return scores


def set_from_dist(dist: 'distribution of the synthetic set', 
                       N:'number of appearances of the least frequent value'
                       ):
    '''
    Generate a set of values following a given distribution. 
    '''
    values = []
    for value in dist.keys():
        values.extend([value]*int(dist[value]*N))
 
    return values

def generate_synthetic_score_sets(scores):
    '''
    Generate synthetic sets of FAIR scores based on score distributions
    '''
    synt_scores = {}
    for p in ids.keys():
        synt_scores[p] = {}
        for e in ids[p]:
            synt_scores[p][e] = set_from_dist(scores[p][e], 1)
    return synt_scores

def compute_FAIR_scores_distributions():
    '''
    Compute FAIR score distributions by principle
    '''
    
    metrics = FAIR_indicators_eval.computeScores()
    scores = scores_in_dict(metrics[:5])
    distributions = distribution_of_scores(scores)
    synt_scores = generate_synthetic_score_sets(distributions)

    data = {
        'variable': 'FAIR_scores',
        'version': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'data': synt_scores
    }

    stats.insert_one(data)




compute_FAIR_scores_distributions()
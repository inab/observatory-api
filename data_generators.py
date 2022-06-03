
import pymongo
import json
import configparser
import FAIRsoft

from pymongo import MongoClient
from datetime import datetime
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
def compute_FAIR_scores():
    metrics = FAIR_indicators_eval.computeScores()
    ids = {'F':['F3','F2', 'F1'],
       'A':['A3', 'A1'],
       'I':['I3', 'I2', 'I1'],
       'R':['R4', 'R3', 'R2', 'R1']
      }

    # initializing dict with scores
    scores = {}
    for p in ids.keys():
        scores[p]={}
        for e in ids[p]:
            scores[p][e] = []
    print(scores)
    # populating dict with scores
    for inst in metrics:
        for p in ids.keys():
            for e in ids[p]:
                scores[p][e].append(float(round(inst[e], 2)))
    print(scores)
    for p in ids.keys():
            for e in ids[p]:
                np.random.shuffle(scores[p][e])

    data = {
        'variable': 'FAIR_scores',
        'version': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'data': scores
    }

    stats.insert_one(data)


compute_FAIR_scores()
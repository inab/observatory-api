import json 


def get_feedback(result):

    # open FAIR_indicators_feedback 
    with open('app/helpers/FAIR_indicators_feedback.json','r') as feedback_file:
        feedback_per_indicator = json.load(feedback_file) 

    feedback = {
        'F': {
            'strengths': [],
            'improvements': []
        },
        'A': {
            'strengths': [],
            'improvements': []
        },
        'I': {
            'strengths': [],
            'improvements': []
        },
        'R': {
            'strengths': [],
            'improvements': []
        },

    }


    for indicator in feedback_per_indicator.keys():
        if indicator[0] in ['F', 'A', 'I', 'R']:
            if  result.get(indicator) == True:
                feedback[indicator[0]]['strengths'].append(feedback_per_indicator[indicator]['strengths'])
            elif result.get(indicator) == False:
                feedback[indicator[0]]['improvements'].append(feedback_per_indicator[indicator]['improvements'])

    return feedback

        



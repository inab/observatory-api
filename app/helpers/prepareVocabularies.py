from app.helpers.EDAM_forFE import EDAMDict 

def prepareEDAM():
    EDAMVocabularyItems = {
        'format': [],
        'datatype': [],
        'operation': [],
        'topic': [],
    }

    for key,value in EDAMDict.items():
        # if this is an EDAM term
        if 'http://edamontology.org' in key:

            # Find out type of EDAM term it is
            if 'format' in key:
                EDAMVocabularyItems['format'].append(value) 
            elif 'data' in key:
                EDAMVocabularyItems['datatype'].append(value)
            elif 'operation' in key:
                EDAMVocabularyItems['operation'].append(value)
            elif 'topic' in key:
                EDAMVocabularyItems['topic'].append(value)
            else:
                print(f'Error: EDAM term not recognised: key: {key}, value: {value}')
    
    return EDAMVocabularyItems

if __name__ == "__main__":
    EDAMVocabularyItems = prepareEDAM()            
    print(EDAMVocabularyItems)

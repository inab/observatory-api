from functools import wraps
import os
import warnings
import time
import logging

# --------------------------------------------
# Constants 
# --------------------------------------------
global webTypes
webTypes = ['rest', 'web', 'app', 'suite', 'workbench', 'db', 'soap', 'sparql']

# environment variables containing whether sources to be transformed in .env
sources_to_transform = [
    'BIOCONDUCTOR',
    'BIOCONDA',
    'BIOTOOLS',
    'TOOLSHED',
    'GALAXY_METADATA',
    'SOURCEFORGE',
    'GALAXY_EU',
    'OPEB_METRICS',
    'BIOCONDA_RECIPES',
    'BIOCONDA_CONDA',
    'REPOSITORIES',
    'GITHUB',
    'BITBUCKET'
]

# Labels of sources accross FAIRsoft pacakage. Must be consistent!!!! 
# Present in:
# 1.- 'sources' field in `instance`` objects (and anywhere they appear in code) 
# 2.- toolGenerators in FAIRsoft.meta_transformers
# if labels change in one place, they must change in the others for everythong to keep working

sources_labels = {
    'BIOCONDUCTOR':'bioconductor',
    'BIOCONDA':'bioconda',
    'BIOTOOLS':'biotools',
    'TOOLSHED':'toolshed',
    'GALAXY_METADATA':'galaxy_metadata',
    'SOURCEFORGE': 'sourceforge',
    'GALAXY_EU': 'galaxy',
    'OPEB_METRICS':'opeb_metrics',
    'BIOCONDA_RECIPES':'bioconda_recipes',
    'BIOCONDA_CONDA':'bioconda_conda',
    'REPOSITORIES': 'repository',
    'GITHUB': 'github',
    'BITBUCKET': 'bitbucket'
}

# --------------------------------------------
# Helper functions
# --------------------------------------------

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


# --------------------------------------------
# Classes
# --------------------------------------------
class instance(object):

    def __init__(self, 
                 name='fairsoft_default_name', 
                 type_='fairsoft_default', 
                 version='fairsoft_default', 
                 dictionary=None):
        # initialize this class from a dictionary
        if dictionary != None:
            #print(dictionary)
            for key, value in dictionary.items():
                if key != '_id':
                    setattr(self,key,value)
        
        # initialize this class from name, type and version
        else:
            # Minimal initiallization of instance
            ## name is required. If not specified, a default value is assigned and a warning raised
            self.attribute_check_and_set('name', name)
            self.attribute_check_and_set('type', type_)

            ## version and type are strongly recommended. If not set, raise a warning and assign None.
            self.attribute_check_and_set('version', version)
            
            # remaining attributes are set to None/empty
            self.label : str = None
            self.links : List(str) = []
            self.publication : List() =  []
            self.download : List(str) = []
            self.inst_instr : bool = False
            self.test : bool = False
            self.src : List(str) = []
            self.os : List(str) = []
            self.input : List(dict) = [] #  {'format' : <format> , 'uri' : <uri> , 'data' : <data> , 'uri': <uri>}
            self.output : List(dict) = [] #  {'format' : <format> , 'uri' : <uri> }
            self.dependencies : List(str) = []
            self.documentation : List(list) = [] # [[type, url], [type, rul], ...]
            self.license : List(str) = []
            self.termsUse : List(str) = []
            self.contribPolicy = False
            self.authors : List(str) = []
            self.repository : List(str) = []
            self.description : List(str) = []
            self.source : List(str) = []
            self.bioschemas : bool  = False
            self.https : bool = False
            self.operational : bool = False
            self.ssl : bool = False
            self.edam_topics : List(str) = []
            self.edam_operations : List(str) = []
            self.semantics : dict = {}
            self.tags : List(str) = []
            

    def attribute_check_and_set(self, key, value):
        '''Check if the attribute is set.
        If it is not, set default attribute to the instance and raise a warning.
        '''
        if value == 'fairsoft_default':
            warnings.warn(f'Instance {key} not specified. Setting instance.{key} = None')
            setattr(self,key,None)

        elif value == 'fairsoft_default_name':
            # Default name instead of None for trackability/debugging purposes
            warnings.warn(f'Instance {key} not specified. Assigning default value "fairsoft_default_name"', Warning)
            setattr(self,key,value)

        else:
            setattr(self,key,value)


    def set_super_type(self):
        if self.type in webTypes:
            self.super_type='web'
        else:
            self.super_type='no_web'


    ##============ Findability metrics computation functions ================

    def compF1_2(self):
        '''
        Identifiability of version:
        Whether there is a scheme to uniquely and properly identify the software version.
        A version of the form X.X is considered acceptable: True. Anything else is False
        '''
        if self.version:
            vers_veredicts = []
            for v in self.version:
                if v:
                    if len(v.split('.'))==2:
                        vers_veredicts.append(True)
                    else:
                        vers_veredicts.append(False)
                # for now, a single True is enough, can be changed in the future, not allowing any False
            if True in vers_veredicts:
                return(True)
        return(False)

    global struct_meta
    # TODO this list must depend on the analyzed sources. Take from config.yaml
    struct_meta = ['biotools', 'bioconda', 'github', 'bitbucket', 'galaxy', 'toolshed', 'opeb_metrics', 'observatory']
    def compF2_1(self):
        '''
        Structured Metadata
        Metadata is adjusted to specific metdata formats
        The sources in struct_meta are structured. If these sources are among self.source: True. Otherwise: False
        '''
        if True in [a in struct_meta for a in self.source]:
            return(True)
        else:
            return(False)

    def compF2_2(self):
        '''
        Whether the software is described using ontologies or controlled vocabularies.
        Schema in observatory:
        {
            "vocabulary": "EDAM",
            "term": "Topic",
            "uri": "http://edamontology.org/topic_0003"
        }
        '''
        # collect vocabularies/ontolgies used
        def collectVeredicts(listItems, veredicts):
            if listItems:
                for t in listItems:
                    if t['vocabulary'] != '':
                        veredicts.append(True)
                    else:
                        veredicts.append(False)
            
            return(veredicts)

        veredicts = []
        veredicts = collectVeredicts(self.topics, veredicts)
        veredicts = collectVeredicts(self.operations, veredicts)

        # If at least one of the terms is described using a vocabulary/ontology: True. Otherwise: False
        if True in veredicts:
            return(True)
        else:
            return(False)

        '''
        DEPRECATED:        
        # look for EDAM terms
        if self.semantics:
            for k in self.semantics.keys():
                if self.semantics[k]:
                    return(True)
        return(False)
        '''


    global softReg
    softReg = ['biotools', 'bioconda', 'bioconductor']
    def compF3_1(self):
        '''
        Searchability in registries
        Whether software is included in the main software registries.
        If the source is among the software registries: True. Otherwise: False
        '''
        if True in [a in softReg for a in self.source]:
            return(True)
        else:
            return(False)
        


    def compF3_2(self):
        '''
        Searchabiliy in software repositories
        Whether software can be found in any of the major software repositories e.g. GitHub, GitLab, SourceForge, 
        If the instance has an associated repository uri: True. Otherwise: False
        '''
        if len(self.repository)>0:
            return(True)
        else:
            return(False)


    def compF3_3(self):
        '''
        Searchability in literature.
        Whether software can be found in specialized literatue services e.g. EuropePMC, PubMed, Journals Site, bioArxiv.
        If the instance at least one associated publication: True. Otherwise: False
        '''
        if len(self.publication)>0:
            return(True)
        else:
            return(False)

    ##============== Accessibility metrics computation functions ================

    def compA1_1(self):
        '''
        WEB
        Existance of API or web 
        Whether it is possible to access a working version of the tool through and API or web. 
        A 200 status when accessing the links provided is consired acceptable.
        '''
        return(self.operational)

    def compA1_2(self):
        '''
        NO WEB
        Existence of downloadable and buildable software working version
        If there is a download link: True ## we do not check if it is available. 
        '''
        if self.super_type == 'no_web':
            if len(self.download)>0:
                return(True)
            elif True in [s in self.source for s in ['bioconda', 'bioconductor','galaxy','toolshed','bioconda_conda','bioconda_recipes']]:
                return(True)
            else:
                return(False)
        else:
            return(False)

    def compA1_3(self):
        '''
        NO WEB
        Existence of installation instructions
        Whether there is a set of instructions and other necessary information the user can follow to build the software
        We check self.inst_instructions (already a boolean)
        '''
        #print('A1_3', end='\r')
        if self.super_type == 'no_web':
            return(self.inst_instr)
        else:
            return(False)

    def compA1_4(self):
        '''
        Existence of test data
        Whether test data is available
        We check self.test (already a boolean)
        '''
        if self.test:
            return(True)
        else:
            return(False)

    def compA1_5(self):
        '''
        NO WEB
        Existence of software source code
        Whether software source code is available 
        '''
        if self.super_type == 'no_web':
            if len(self.src)>0:
                return(True)
            else:
                return(False)
        else:
            return(False)
    
    def compA3_1(self):
        '''
        Registration not compulsory
        Whether homepage can be accessed without registration
        '''
        return(self.registration_not_mandatory)



    def compA3_2(self):
        '''
        NO WEB
        Availability of version for free OS
        Whether the software can be used in a free operative system
        '''
        if self.super_type == 'no_web':
            if 'Linux' in self.os:
                return(True)
            elif 'FreeBSD' in self.os:
                return(True)
            else:
                return(False)
        else:
            return(True)

    def compA3_3(self):
        '''
        No WEB
        Availability for several OS
        Whether there are versions of the software for several operative systems
        '''
        if self.super_type == 'no_web':
            if len(self.os)>1:
                return(True)
            else:
                return(False)
        else:
            return(False)

    def compA3_4(self):
        '''
        NO WEB
        Availability on free e-Infrastructures
        Whether the software can be used in a free e-infrastructure
        We are only considering galaxy servers and vre
        '''
        if self.super_type == 'no_web':
            eInfra = ['vre.multiscalegenomics.eu', 'galaxy.', 'usegalaxy.']
            for url in self.links:
                for e in eInfra:
                    if e in url:
                        return(True)
                else:
                    return(False)
            return(False)
        else:
            return(False)


    def compA3_5(self):
        '''
        NO WEB
        Availability on several e-Infrastructures
        Whether the software can be used in several e-infrastructure
        '''
        if self.super_type == 'no_web':
            count = 0
            eInfra = ['vre.multiscalegenomics.eu', 'galaxy.', 'usegalaxy.']
            for url in self.links:
                for e in eInfra:
                    if e in url:
                        count += 1
            if count>1:
                return(True)

            return(False)
        else:
            return(False)

    ##============== Interoperability metrics computation functions ================
    def compI1_1(self):
        '''
        Usage of standard data formats
        Whether the input and output datatypes are formally specified AND related to accepted ontologies
        Exmaple: 
        [
            {   "vocabulary": "EDAM",
                "term": "Sequence format",
                "url": "http://edamontology.org/format_1929",
                datatype: {
                    "vocabulary": "EDAM",
                    "term": "Sequence",
                    "url": "http://edamontology.org/data_0006"
                }
            },
            ...
        ]
        '''
        # collect vocabularies/ontolgies used
        def collectVeredicts(listItems, veredicts):
            if listItems:
                for t in listItems:
                    if t['vocabulary'] != '':
                        veredicts.append(True)
                    else:
                        veredicts.append(False)
            
            return(veredicts)

        veredicts = []
        veredicts = collectVeredicts(self.input, veredicts)
        veredicts = collectVeredicts(self.output, veredicts)

        # If at least one of the terms is described using a vocabulary/ontology: True. Otherwise: False
        if True in veredicts:
            return(True)
        else:
            return(False)

        '''
        DEPRECATED
        for i in self.input:
            if 'format' in i.keys():
                if i['format']['term'] in self.stdFormats:
                    return(True)

        for i in self.output:
            if 'format' in i.keys():
                if i['format']['term'] in self.stdFormats:
                    return(True)
        
        return(False)
        '''
    def compI1_2(self):
        '''
        API standard specification
        '''
        for item in self.documentation:
            if item.type == 'API specification':
                return(True)
        
        return False


    def compI1_3(self):
        '''
        Verificability of data formats
        Whether input/output data are specified using verifiable schemas (e.g. XDS, Json schema, ...)
        '''
        if self.compI1_1() == True:
            return(True)

        verifiable_formats = ['json', 'xml', 'rdf', 'xds']
        formats = self.input + self.output
        terms = set()
        for i in formats:
            if 'format' in i.keys():
                terms.add(i['format']['term'])
        
        for term in terms:
            if term in verifiable_formats:
                return(True)

        return(False)



    def compI1_4(self):
        '''
        Flexibility of data format supported
        Whether the software allows to choose among various input/output data formats, or provide the necessary tools to convert other common formats into the supported ones.
        '''
        if len(self.input)>1 and len(self.output)>1:
            return(True)
        else:
            return(False)

        '''
        DEPRECATED
        ins = []
        formats = self.input + self.output
        for i in formats:
            if 'format' in i.keys():
                ins.append(i['format']['term'])

        if len(ins)>1:
            return(True)
        else:
            return(False)
        '''
        

    def compI2_1(self):
        '''
        Existence of API/library version 
        Whether the software has API /library versions to be included in users' pipelines
        '''
        interTypes = ['Library', 'Web API']
        for t in self.type:
            if t in interTypes:
                return(True)
        else:
            return(False)


    def compI2_2(self):
        '''
        E-infrastructure compatibility
        '''
        if 'galaxy' in self.source:
            return(True)
        elif 'toolshed' in self.source:
            return(True)
        else:
            return(False)

    def compI3_1(self):
        '''
        Dependencies statement
        Whether the software includes details about dependencies
        '''
        if len(self.dependencies)>0:
            return(True)
        else:
            return(False)

    def compI3_2(self):
        '''
        Dependencies are provided
        Whether the software includes its dependencies or mechanisms to access them
        '''
        # checking source
        if 'toolshed' in self.source:
            return(True)
        elif 'bioconda' in self.source:
            return(True)
        elif 'bioconductor' in self.source:
            return(True)
        
        # registries 
        accepted_registries = ['toolshed', 'bioconductor','conda', 'PyPI', 'CRAN', 'npm', 'CPAN', 'RubyGems', 'DockerHub', 'GitHub Container Registry', 'GitLab Container Registry', 'BioContainers']
        for registry in self.registries:
            if registry in accepted_registries:
                return(True)
        
        #checking links
        sources_with_dependencies = ['bioconda', 'bioconductor', 'galaxy']
        for url in self.links:
            if True in  [a in url for a in sources_with_dependencies]:
                return(True)
        
        return(False)
    
    def compI3_3(self):
        '''
        Dependency-aware system
        '''
        # registries 
        accepted_registries = ['toolshed', 'bioconductor','conda', 'PyPI', 'CRAN', 'npm', 'CPAN', 'RubyGems']
        for registry in self.registries:
            if registry in accepted_registries:
                return(True)
        
        #checking links
        sources_with_dependencies = ['bioconda', 'bioconductor', 'galaxy']
        for url in self.links:
            if True in  [a in url for a in sources_with_dependencies]:
                return(True)
        
        return(False)

    # ===================== Reusability ==============================================================
    def compR1_1(self):
        '''
        Existence of usage guides
        Whether software user guides are provided
        Documentation format: list of dictionaries
        [
            {
                "type": "general",
                "url": "https://bio.tools/api/tool/blast2go/docs/1.0.0"
            },
            ...
        ]   
        '''
        # documentation types that are not guides for the user
        noGuide = ['license', 'terms of use', 'news', 'contribution', 'citation', 'contact', 'changelog', 'release']
        for individual_document in self.documentation:
            for string in noGuide:
                if string not in individual_document['type'].lower(): # doc[0] is the type of document
                    return(True)

        return(False)


    def compR2_1(self):
        '''
        Existence of license
        Whether license is stated
        '''
        '''
        DEPRECATED 
        # license can be part of the documentation
        for doc in self.documentation:
            if 'license' in doc[0].lower():
                print('In doc')
                return(True)
        '''
        for doc in self.documentation:
            if 'license' in doc['type'].lower():
                return(True)
            elif 'terms of use' in doc['type'].lower():
                return(True)
            elif 'conditions of use' in doc['type'].lower():
                return(True)
        
        # or it can be specified in the license field
        if self.license:
            if len(self.license)>0:
                for a in self.license:
                    # some licenses are actually a list of one license in old versions of ETL
                    license_name = a.name
                    if type(license_name) == list:
                        license_name = license_name[0]
                    if license_name.lower()=='unlicensed' or license_name.lower()=='unknown' or license_name.lower()=='unlicense':
                        continue
                    else:
                        if license_name:
                            return(True)
        return(False)
        
    
    def compR2_2(self):
        '''
        Technical conditions of use
        '''
        '''
        DEPRECATED
        for doc in self.documentation:
            if 'conditions of use' in doc[0].lower():
                return(True)
            elif 'terms of use' in doc[0].lower():
                return(True)
        if self.license:
            if len(self.license)>0:
                for a in self.license:
                    # some licenses are actually a list of one license in old versions of ETL
                    if type(a) == list:
                        a = a[0]
                    if a.lower()=='unlicensed' or a.lower()=='unknown' or a.lower()=='unlicense':
                        continue
                    else:
                        if a:
                            return(True)

        return(False)
        '''
        for doc in self.documentation:
            if 'conditions of use' in doc['type'].lower():
                return(True)
            elif 'terms of use' in doc['type'].lower():
                return(True)
        if self.license:
            if len(self.license)>0:
                for a in self.license:
                    # some licenses are actually a list of one license in old versions of ETL
                    license_name = a.name
                    if type(license_name) == list:
                        license_name = license_name[0]
                    if license_name.lower()=='unlicensed' or license_name.lower()=='unknown' or license_name.lower()=='unlicense':
                        continue
                    else:
                        if license_name:
                            return(True)
        return(False)        
    

    def compR3_1(self):
        '''
        contribution policy
        '''
        for item in self.documentation:
            if item.type == 'contribution policy':
                return(True)
        
        return False
    

    def compR3_2(self):
        '''
        Existence of credit
        Whether credit for contributions is provided
        '''
        if len(self.authors)>0:
            return(True)
        else:
            return(False)


    def compR4_1(self):
        '''
        Usage of (public) version control
        Whether the software follows a version-control system
        '''
        if self.version_control:
            return(True)
        else:
            return(False)
        
        '''
        DEPRECATED
        for repo in self.repository:
            if 'github' in repo or 'mercurial-scm' in repo:
                return(True)
        return(False)
        '''

    def compR4_2(self):
        '''
        Release Policy
        '''
        for item in self.documentation:
            if item.type == 'release policy':
                return(True)
        
        return False
    

    def FAIRscores(self):
        self.scores = FAIRscores()
        # ===================== Findability =========================
        # F1
        self.scores.F1 = (0.8*self.metrics.F1_1 
                        + 0.2*self.metrics.F1_2)
        # F2
        self.scores.F2 = 0.6*self.metrics.F2_1 + 0.4*self.metrics.F2_2
        # F3
        acc = [self.metrics.F3_1, self.metrics.F3_2, self.metrics.F3_3].count(True)
        if acc == 1:
            self.scores.F3 = 0.7
        elif acc == 2:
            self.scores.F3 = 0.85
        elif acc == 3:
            self.scores.F3 = 1
        # F
        self.scores.F = (0.4*self.scores.F1
                       + 0.2*self.scores.F2
                       + 0.4*self.scores.F3)
        # ===================== Accessibility =======================
        if self.super_type == 'web':
            # A1
            self.scores.A1 = (0.6*self.metrics.A1_1 
                            + 0.4*self.metrics.A1_4)
            # A3
            self.scores.A3 = 1.0*self.metrics.A3_1 
        else:
            # A1
            self.scores.A1 = (0.5*self.metrics.A1_2 
                            + 0.2*self.metrics.A1_3 
                            + 0.1*self.metrics.A1_4 
                            + 0.2*self.metrics.A1_5)
            # A3
            self.scores.A3 = (1/4)*(self.metrics.A3_2
                                  + self.metrics.A3_3
                                  + self.metrics.A3_4
                                  + self.metrics.A3_5)
        # A
        self.scores.A = (0.7*self.scores.A1
                       + 0.3*self.scores.A3)
        #  A_2 not computable bc we do not have the appropriate metrics.
        #  self.A += (self.metrics.A2_1*(1/3)+self.metrics.A2_2*(2/3))*0.15
        
        # ===================== Interoperability =====================

        # I1
        self.scores.I1 = (0.5*self.metrics.I1_1
                        + 0.3*self.metrics.I1_2 # I1.2 is not measured so equals 0
                        + 0.3*self.metrics.I1_3
                        + 0.2*self.metrics.I1_4)
        # I2
        self.scores.I2 = (0.5*self.metrics.I2_1
                        + 0.5*self.metrics.I2_2)
        # I3
        self.scores.I3 = (1/3)*(self.metrics.I3_1
                              + self.metrics.I3_2
                              + self.metrics.I3_3)
        # I
        self.scores.I = (0.6*self.scores.I1
                       + 0.1*self.scores.I2
                       + 0.3*self.scores.I3)
        # ===================== Reusability ===========================

        # R1
        self.scores.R1 = 1.0*self.metrics.R1_1
        # R2
        if self.metrics.R2_1:
            self.scores.R2 = 1.0
        elif self.metrics.R2_2:
            self.scores.R2 = 1.0
        else:
            self.scores.R2 = 0.0
        # R3
        self.scores.R3 = 1.0*self.metrics.R3_2
        # R4
        self.scores.R4 = 1.0*self.metrics.R4_1

        #R
        self.scores.R = (0.3*self.scores.R1
                       + 0.3*self.scores.R2
                       + 0.2*self.scores.R3
                       + 0.2*self.scores.R4)

    def generateFAIRMetrics(self, stdFormats):
        self.stdFormats = stdFormats
        # FINDABILITY
        self.metrics = FAIRmetrics()

        self.metrics.F1_1 = True # all have a name
        self.metrics.F1_2 = self.compF1_2() #
        self.metrics.F2_1 = self.compF2_1()
        self.metrics.F2_2 = self.compF2_2() 

        self.metrics.F3_1 = self.compF3_1()
        self.metrics.F3_2 = self.compF3_2()
        self.metrics.F3_3 = self.compF3_3()
        # ACCESIBILITY
        self.metrics.A1_1 = self.compA1_1() # Existance of API or web 
        self.metrics.A1_2 = self.compA1_2() # Existance of downloadable and buildable software working version
        self.metrics.A1_3 = self.compA1_3() # Existance of installation instructions
        self.metrics.A1_4 = self.compA1_4() # Existance of test data
        self.metrics.A1_5 = self.compA1_5() # Existance of software source code

        self.metrics.A2_1 = False # Metadata of previous versions at software repositories
        self.metrics.A2_2 = False # Existence of accesible previous versions of the software

        self.metrics.A3_1 = self.compA3_1() # Registration compulsory
        self.metrics.A3_2 = self.compA3_2() # Availability of version for free OS
        self.metrics.A3_3 = self.compA3_3() # Availability for several OS
        self.metrics.A3_4 = self.compA3_4() # Availability on free e-Infrastructures
        self.metrics.A3_5 = self.compA3_4() # Availability on several e-Infrastructures

        self.metrics.I1_1 = self.compI1_1()  # Usage of standard data formats
        self.metrics.I1_2 = self.compI1_2() # ONLY EVALUATOR
        self.metrics.I1_3 = self.compI1_3() # Verificability of data formats
        self.metrics.I1_4 = self.compI1_4() # Flexibility of data format supported
        self.metrics.I1_5 = False # NOT FOR NOW # Generation of provenance information

        self.metrics.I2_1 = self.compI2_1() # Existance of API/library version 
        self.metrics.I2_2 = self.compI2_2() # E-infrastructure compatibility

        self.metrics.I3_1 = self.compI3_1()
        self.metrics.I3_2 = self.compI3_2()
        self.metrics.I3_3 = self.compI3_2() # Same as I3_2, BY NOW

        self.metrics.R1_1 = self.compR1_1()
        self.metrics.R1_2 = False #NOT FOR NOW

        self.metrics.R2_1 = self.compR2_1()
        self.metrics.R2_2 = self.compR2_2()

        self.metrics.R3_1 = self.compR3_1() # ONLY EVALUATOR
        self.metrics.R3_2 = self.compR3_2()

        self.metrics.R4_1 = self.compR4_1()
        self.metrics.R4_2 = self.compR4_2() # ONLY EVALUATOR
        self.metrics.R4_3 = False # By now


class FAIRscores():
    def __init__(self):
        
        self.F = 0.0 
        self.F1 = 0.0
        self.F2 = 0.0
        self.F3 = 0.0

        self.A = 0.0
        self.A1 = 0.0
        self.A2 = 0.0
        self.A3 = 0.0

        self.I = 0.0
        self.I1 = 0.0
        self.I2 = 0.0
        self.I3 = 0.0

        self.R = 0.0
        self.R1 = 0.0
        self.R2= 0.0
        self.R3 = 0.0
        self.R4 = 0.0


class FAIRmetrics(object):

    def __init__(self):
        self.F1_1 = False # uniqueness of name
        self.F1_2 = False # idenfibiability of version

        self.F2_1 = False # structured metadata
        self.F2_2 = False # standarized metadata

        self.F3_1 = False # searchability in registries
        self.F3_2 = False # searchability in software repositories
        self.F3_3 = False # searchability in literature

        self.A1_1 = False
        self.A1_2 = False
        self.A1_3 = False
        self.A1_4 = False
        self.A1_5 = False

        self.A2_1 = False
        self.A2_2 = False

        self.A3_1 = False
        self.A3_2 = False
        self.A3_3 = False
        self.A3_4 = False
        self.A3_5 = False

        self.I1_1 = False
        self.I1_2 = False
        self.I1_3 = False
        self.I1_4 = False
        self.I1_5 = False

        self.I2_1 = False
        self.I2_2 = False

        self.I3_1 = False
        self.I3_2 = False
        self.I3_3 = False

        self.R1_1 = False
        self.R1_2 = False

        self.R2_1 = False
        self.R2_2 = False

        self.R3_1 = False
        self.R3_2 = False

        self.R4_1 = False
        self.R4_2 = False
        self.R4_3 = False

class canonicalSet(object):
    
    def __init__(self):
        self.canonicals = []

    def addCanononical(self, canon):
        self.canonicals.append(canon)

class canonicalTool(object):

    def __init__(self, name, instances, sources, types):
        self.name = name
        self.instances = instances
        self.sources = sources
        self.types = types

    def computeFAIRmetrics(self):
        self.F = max([ins.F for ins in self.instances])
        self.A = max([ins.A for ins in self.instances])
        self.I = max([ins.I for ins in self.instances])
        self.R = max([ins.R for ins in self.instances])

class setOfInstances(object):

    def __init__(self, source):
        self.source = source
        self.instances = []


from pydantic import BaseModel, AnyUrl, EmailStr, field_validator, Field, ConfigDict, HttpUrl
from urllib.parse import urlparse
from typing import List, Optional, Dict, Any, Union
from app.models.fair_metrics import FAIRmetrics, FAIRscores  # Import the necessary classes
from app.constants import WEB_TYPES

def remove_nones_empty_string(v):
    """Helper function to remove None or empty string values from a list."""
    if isinstance(v, list):
        return [i for i in v if i is not None and i != '']
    return v


class License(BaseModel):
    name: str
    url: Optional[AnyUrl] = Field(None, description="URL of the license. Can be empty.")

    @field_validator('url', mode='before')
    def allow_empty_url(cls, v):
        if v == '':
            return None
        return v

class Documentation(BaseModel):
    type: str
    url: Optional[AnyUrl] = None

class Publication(BaseModel):
    pmid: str
    cit_count: int
    doi: Optional[str] = None
    pmcid: Optional[str] = None
    pmid: Optional[str] = None
    cit_count: Optional[int] = None
    ref_count: Optional[int] = None
    refs: Optional[List[Dict[str, Any]]] = None
    title: Optional[str] = None
    year: Optional[int] = None
    citations: Optional[List[Dict[str, Any]]] = None

    @field_validator('year', mode='before')
    def convert_string_year(cls, v):
        if isinstance(v, str):
            return int(v)
        return v

class ControlledTerm(BaseModel):
    vocabulary: Optional[str] = None
    term: Optional[str] = None
    uri: Optional[AnyUrl] = None

class Person(BaseModel):
    name: str
    type: str
    email: Optional[str] = None
    maintainer: Optional[bool] = False

    @field_validator('email', mode='before')
    def allow_empty_email(cls, v):
        if v == '':
            return None
        return v

def remove_nones_empy_string(v):
    # Remove None values from the list
    if isinstance(v, list):
        new_v = [i for i in v if i is not None]
        return [i for i in new_v if i != '']
    return v



class Instance(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[List[str]] = None
    version: Optional[List[str]] = None
    authors: Optional[List[Person]] = []
    bioschemas: Optional[bool] = False
    contribPolicy: Optional[List[str]] = []
    dependencies: Optional[List[str]] = []
    description: Optional[List[str]] = []
    documentation: Optional[List[Documentation]] = []
    download: Optional[List[AnyUrl]] = []
    edam_operations: Optional[List[AnyUrl]] = []
    edam_topics: Optional[List[AnyUrl]] = []
    https: Optional[bool] = False
    input: Optional[List[ControlledTerm]] = []
    inst_instr: Optional[bool] = False
    label: Optional[List[str]] = []
    license: Optional[List[License]] = []
    links: Optional[List[AnyUrl]] = []
    operational: Optional[bool] = False
    os: Optional[List[str]] = []
    output: Optional[List[ControlledTerm]] = []
    publication: Optional[List[Publication]] = []
    repository: Optional[List[AnyUrl]] = []
    semantics: Optional[Dict[str, Any]] = {}
    source: Optional[List[str]] = []
    src: Optional[List[AnyUrl]] = []
    ssl: Optional[bool] = False
    tags: Optional[List[str]] = []
    termsUse: Optional[bool] = False
    test: Optional[List] = False
    topics: Optional[List[ControlledTerm]] = []
    operations: Optional[List[ControlledTerm]] = []
    webpage: Optional[List[AnyUrl]] = []
    registration_not_mandatory: Optional[bool] = False
    registries: Optional[List[str]] = []
    other_versions: Optional[List[str]] = []                 
    e_infrastructures: Optional[List[Any]] = []               
    version_control: Optional[bool] = False          
    super_type: Optional[str] = None 
    metrics: Optional[FAIRmetrics] = None 
    scores: Optional[FAIRscores] = None 
    logs: Optional[List[str]] = []

    # type may come as a string
    @field_validator("type", mode="before")
    @classmethod
    def coerce_str_to_list(cls, v: Any):
        if v is None:
            return None
        if isinstance(v, str):
            return [v]
        return v

    @field_validator("version", mode="before")
    @classmethod
    def coerce_str_to_list_version(cls, v: Any):
        if v is None:
            return None
        if isinstance(v, str):
            return [v]
        return v

    # Filter empty strings and non-valid entries in the publications field
    @field_validator('publication', mode='before')
    def filter_empty_publication(cls, v):
        filtered_v = remove_nones_empty_string(v)
        if filtered_v:
            return [p for p in filtered_v if p != {}]
        return filtered_v
    
    # Filter empty strings and non-valid entries in the webpage field
    @field_validator('webpage', mode='before')
    def filter_empty_webpage(cls, v):
        return remove_nones_empty_string(v)

    # Set super_type based on whether the instance is part of web_types
    def set_super_type(self, web_types: List[str]):
        web = False
        non_web = False
        for type in self.type:
            if type in web_types:
                web = True 
            else:
                non_web = True 
        
        if web and non_web:
            self.super_type = 'both'
        else:
            if web:
                self.super_type = 'web'
            else:
                self.super_type = 'non-web'

    def __init__(self, **data):
        super().__init__(**data)
        self.set_super_type(WEB_TYPES)
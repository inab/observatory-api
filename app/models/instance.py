from pydantic import BaseModel, AnyUrl, EmailStr, field_validator, Field, ConfigDict 
from typing import List, Optional, Dict, Any
from app.models.fair_metrics import FAIRmetrics, FAIRscores  # Import the necessary classes

class License(BaseModel):
    name: str
    url: Optional[AnyUrl] = Field(None, description="URL of the license. Can be empty.")

    @field_validator('url')
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
    ref_count: Optional[int] = None
    refs: Optional[List[Dict[str, Any]]] = None
    title: Optional[str] = None
    year: Optional[int] = None
    citations: Optional[List[Dict[str, Any]]] = None

class ControlledTerm(BaseModel):
    vocabulary: Optional[str] = None
    term: Optional[str] = None
    uri: Optional[AnyUrl] = None

class Person(BaseModel):
    name: str
    type: str
    email: Optional[EmailStr] = None
    maintainer: Optional[bool] = False

    @field_validator('email')
    def allow_empty_email(cls, v):
        if v == '':
            return None
        return v

class Instance(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    version: Optional[str] = None
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
    test: Optional[bool] = False
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


    def set_super_type(self, web_types: List[str]):
        if self.type in web_types:
            self.super_type = 'web'
        else:
            self.super_type = 'no_web'
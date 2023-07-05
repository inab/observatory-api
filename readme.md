# Software Observatory API 

This repository contains the source code of the Software Observatory API. This API is a Flask application that uses a local mongodb database. 

## Development 

### Ready-to-use database

To facilitate the testing of the Observatory API, a docker-compose to deploy and populate a full and ready-to-use database is available (`mongo-compose/docker-compose.yml`). 

The components necessary for this deployment are `mongodb`, `mongo-total` and `mongo-seed`. The configuration of the latter two can be found in the `mongo-compose` directory. 

To deploy the database:

```
sudo docker login registry.gitlab.bsc.es
sudo docker-compose up --remove-orphans --force-recreate --renew-anon-volumes
```

### Collections 
 
Most endpoints use the `observatory2.tools` collection. The endpoint `GET "/tools/names_type_labels"` uses the collection `observatory2.tools_discoverer_w_index`. This is due to this collection being processed to contain information of types and labels in a more convenient way. 


### Mappings 

| bioschema |  UI    |
| --------- | ------ |
| `@type`   | `type` |
| `schema:applicationSubcategory` | `topics` |
| `schema:additionalType` | `type` |
| `schema:name` | `name` |
| `schema:url` | `webpages` |
| `schema:description` | `description` |
| `schema:applicationCategory` | `type` |
| `schema:operatingSystem` | `os` |
| `schema:license` | `license` |
| `schema:author` | `authors` |
| `schema:maintainer` | `authors` |
| `schema:softwareVersion` | `version` |
| `schema:codeRepository` | `repository` 
| `schema:featureList` | `operations` |
| `schema:input` | `input` |
| `schema:output` | `output` |
| `schema:downloadURL` | `download` |
| `schema:softwareHelp` | `documentation` | 
| `schema:citation` | `publication` |
| `schema:requirements` | `dependencies` |
| `schema:isAccessibleForFree` | `registration_not_manadatory` |
| `schema:dateModified` | - |
| `@context` | - |
# Ready-to-use database

To facilitate the testing of the Observatory API, a docker-compose to deploy and populate a full and ready-to-use database is available (`mongo-compose/docker-compose.yml`). 

The components necessary for this deployment are `mongodb`, `mongo-total` and `mongo-seed`. The configuration of the latter two can be found in the `mongo-compose` directory. 

To deploy the database:

```
sudo docker login registry.gitlab.bsc.es
sudo docker-compose up --remove-orphans --force-recreate --renew-anon-volumes
```
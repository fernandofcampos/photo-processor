## photo-processor exercise

### Description

The aim of the exercise is to orchestrate the generation of thumbnails for a specific set of photos.

### Installation

Prerequisites:  
- Docker  
- Ability to run `make`.

App is bundling Postgres and RabbitMQ instances via Docker, so please stop any local related services to avoid port conflicts. Otherwise you can amend the default port mappings on the docker-compose file.

Start the app:
- `make start`

Create or reset the db schema after booting the app:  
- `make db-schema`

Fill the db with a test set:
- `make db-test-set`

Postgres PSQL can be accessed via:
- `make psql`

RabbitMQ management console can be accessed at:  
`http://localhost:15672/`  

Web app can be accessed at:  
`http://localhost:3000/`  

### Assumptions

- Consumer is always ACKing messages. Errors in processing are recorded only on the database with `failed` status.

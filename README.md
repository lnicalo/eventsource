# PoC of events based application with Nameko, Kafka and Flask

## Architecture

### Services

- API (flask):
  - Make asynchronous calls to nameko services `userevents` and `userstats`.
  - Endpoints are synchronous. 
  TODO: They should be asynchronous and return a 202. 
- `userevents`(nameko service):
  - exposes a RPC endpoint to submit event messages to kafka.
- `userstats` (nameko service):
  - consumes messages from kafka
  - insert a new record into a sqlite database for each new user event
  - periodically (every 1 hour) sends a new email with the report. Actually only logs stats every 5 seconds in debug mode

### Brokers

- Zookeeper: Required by kafka
- Kafka: Messages
- Rabbit: Async communication between services

## Run demo with docker compose

1. Change to root folder: `cd blockchain-project`
2. Run brokers with `make run-brokers`. Wait until they are ready (around 30 s).
3. In a separate terminal, run the services: `make run-services`
4. Look at the logs in userstats service. You should that the stats reported every 5 seconds are empty because there are not users in the database. ```New report generated. Fake email sent. to: ['manage@mybusiness.com'], subject: report, content: {'timestamp': '2020-12-13 17:32:42.050393', 'stats': {}}```
5. Request a new report with `curl localhost:8000/report`
6. Submit new 10 users: `curl localhost:8000/submit/10`. Number of new users can be any integer.
7. Look at the logs in `userevents`. You will see logs like:
```New user event {'id': '0905f97a-9e1b-4710-9a1a-1aeb119d2306', 'address': {'city': 'Chagrin Falls', 'state': 'Ohio', 'country': 'US', 'postCode': '44023'}, 'datetime': '2019-05-07 19:54:13.563'}```

7. Look at the logs in `userstats`:

```New user inserted: {'id': 'fc0aa1bf-804c-45d5-b26e-dfb1913d7507', 'address': {'city': 'Holland', 'state': 'Mi', 'country': 'US', 'postCode': '49424'}, 'datetime': '2019-05-07 17:11:13.828'}```

8. Look at the periodic log stats in `userstats`:

```New report generated. Fake email sent. to: ['manage@mybusiness.com'], subject: report, content: {'timestamp': '2020-12-13 17:34:47.048641', 'stats': {'Chagrin Falls': 1, 'Detroit': 1, 'Fresno': 1, 'Harpersferry ': 1, 'Holbrook': 1, 'Holland': 1, 'Mauston ': 1, 'Schenectady': 1, 'Stanley ': 1, 'baltimore': 1}}```

9. Request a new report: `curl localhost:8000/report`

## Automatic tests

Created one example of test for user event service. Run `make tests`
  
## Local development env

Developement enviroment can be created with `pipenv install`

## TODOs

- Clean input data
- Some hardcoded config values
- ...
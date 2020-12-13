app:
	docker-compose build

tests:
	docker-compose run --entrypoint=bash userevents /var/user_events/run-tests.sh

run-brokers:
	docker-compose up --build rabbit zookeeper broker

run-services:
	docker-compose up --build userevents userstats api

run-user-events-localhost:
	cd user_events && nameko run --config config.localhost.yml userevents --broker amqp://guest:guest@localhost

run-user-stats-localhost:
	cd user_stats && nameko run --config config.localhost.yml userstats --broker amqp://guest:guest@localhost


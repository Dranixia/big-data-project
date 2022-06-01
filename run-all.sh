docker network create project-network

docker run -d --name zookeeper-server --network project-network -e ALLOW_ANONYMOUS_LOGIN=yes bitnami/zookeeper:latest
docker run -d --name kafka-server --network project-network -e ALLOW_PLAINTEXT_LISTENER=yes -e KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper-server:2181 bitnami/kafka:latest
docker run -it --rm --network project-network -e KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper-server:2181 bitnami/kafka:latest kafka-topics.sh --create --bootstrap-server kafka-server:9092 --replication-factor 1 --partitions 3 --topic wiki

docker run --name cassandra-node --network project-network -p 9042:9042 -d cassandra:latest
sleep 75s
docker cp ./DDL.cql cassandra-node:/DDL.cql
docker exec cassandra-node cqlsh cassandra-node -f ./DDL.cql


docker build -t kafka-consumer-image -f ./Dockerfile-consumer .
docker build -t kafka-producer-image -f ./Dockerfile-producer .

docker run -it -d --name kafka-producer --network project-network --rm kafka-producer-image
docker run -it -d --name kafka-consumer --network project-network --rm kafka-consumer-image
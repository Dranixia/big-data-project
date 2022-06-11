docker stop kafka-server
docker stop zookeeper-server
docker stop cassandra-server
docker stop cassandra-node
docker stop kafka-producer
docker stop kafka-consumer

docker rm kafka-server
docker rm zookeeper-server
docker rm cassandra-server
docker rm cassandra-node
docker rm kafka-consumer

docker network rm project-network
# THIS PROJECT IS NOT FOR 8 Gb MEMORY MACHINES, TRUST US, WE SUFFERED A LOT AND LOST CAT A RESULTS BECAUSE OF THAT

## Team:

- Danylo Butynets
- Ihor Ramskyi

## Design 

The project uses following tool:

- Cassandra
- Kafka
- Spark

**Cassandra**: used as the primary storage for the permanent info, all the category B queries
are based on the info stored in there. We decided to use Cassandra as the base storage because
a) we are familiar with it through this course b) the B category saves all the info, so we need reliable storage (and potentially
speaking, we suppose that this project is running for days/month, so we need NoSQL DB), surely 
other DBs could be used, such as Mongo, but once again, see a)

**Kafka**: could be omitted in the project, but it stands as insurance, because despite
Python function saving the info coming in memory, instances of calling Spark sometimes stop program for a while, so we
decided to use this MQ just to be sure

**Spark**: originally I didn't want to use it, but you specified that it must be used in the project. The only proper
use we came up with was to give it a function of the storage for category A info. The info is only for the last 8 hours 
at max, which is at most 100 Mb of data, also Spark is easy to use when it comes to filtering out old data.

The project is split in:

- Stream creator: This one is a simple program that reads only necessary data from original stream and puts it
into the batching process trough Kafka, no other functions
- Batching process: basically main program for managing data. First, receives data from Kafka
, than check if the hour has changed, if it did, than we remove old data and the first entry in cat A 1st query, add new one to it,
and finally recalculate 2nd and 3rd queries. Finally, string format of the cat A queries is written into the Cassandra. Then program makes writes to
Cassandra tables and Spark DataFrame. All of this is looped, so the data is constantly being written and there is no unnecessary recalculations of
cat A queries, only when the hour changes
- Server: responsible for using SELECT from Cassandra and send it to the client, both category A and B, we used Flask because have experience with it,
there is no other purpose, this is very similar to the server-client thing I (Danylo) did for the labs.
- Client: Finally, client is just for retrieving info we want as queries, the results are both printed and saved in file.
The input is not protected from entering letters instead of int, or improper date format.

## Data Format

### Cassandra

For the 5 B queries and A query, we decided to make 5 table, 4 for the B category, and 1 for the A.

#### Category A

*Table: cat_a*

The A one is simple, it only has 3 rows with ids 1-3 and strings which are just answers for queries A.

#### Category B

*Table: domains_and_articles*

This table is used for 2 queries, first and third. The first needs only all domains, and third needs count for domains,
so domain is partition key. We also added uri in to a) provide opportunity to count b) provide uniqueness of rows (by adding it to primary key as well)

*Table: user_pages*

Only contains uri and user_id, used for second query. We select by user_id, so it is partitioning key, 
and we need a) uri to select it b) uri in primary key to provide uniqueness of rows

*Table: pages*

Completely identical to previous table, but instead of user_id now page_id and for fourth query.

*Table: user_dates*

Used for last query, each row contains user_id, user_name, datatime stamp and uri of page created. The uri once again
provides uniqueness, and dt is not a partition key because we believe it is too much different values.

### Spark

The Spark DF has the following columns:

time, domain, page_title, user_name, user_id, is_bot, interval

all of these are values from original stream that are used for cat A queries. The only exception is new column which is used to filter out hour 
(because this is time with minutes and seconds being 0, we could even potentially dont add it, and just zero out minutes and second from
time each time we used interval column, but we still decided to add it for convenience)

## Results

The result of queries made from client (both images and json files) are in their
appropriate folders.

Note after project finish: Доброго дня/вечора/ночі/ранку, наскільки ви могли б помітити, результати
для категорії А не є наявними у папках. Причина доволі проста, оригінально проект був з 2ма нодами для Касандри,
проте ми не врахували к-сть оперативної пам'яті що це потребувало. Як результат, в певний момент (після запуску 5 квері) проект зїв всю
память та крашнув убунту, в результаті дані, що зберігалися на нодах були втрачені. І хоча ми розуміємо, що це призведе 
до певної втрати балів, ми не мали бажання знову запускати систему на 8 годин, сподіваюся ви віднесетеся до цього із розумінням. 

CREATE  KEYSPACE wikidata WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE wikidata;

CREATE TABLE domains_and_articles (domain text, uri text, PRIMARY KEY (domain, uri));

CREATE TABLE user_pages (user_id int, uri text, PRIMARY KEY (user_id, uri));

CREATE TABLE pages (page_id int, uri text, PRIMARY KEY (page_id, uri));

CREATE TABLE user_dates (user_id int, user_name text, uri text, dt timestamp, PRIMARY KEY (dt, uri));
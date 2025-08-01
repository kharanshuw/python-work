--end goal

--first it is making bucket of 5 min ,identifying those rows which are inside those 5 min block based on ts column 
--as it has the timestamp  after identifing putting them inside that bucket and then after grouping based on the key ,entity_id 
--after grouping finding the avg of that buket 5 min bucket if there are some  int , double ,float  or numeric values 
--and if there is string ,bool ,json then ignore those after calculating everything merge those records as the new values will be replaced by that
--5 min bucket 



SELECT * FROM 
(
-- original full query
WITH base AS (
SELECT *,
date_trunc('hour', to_timestamp(ts / 1000.0)) +
FLOOR(EXTRACT(MINUTE FROM to_timestamp(ts / 1000.0))::int / 5) * INTERVAL '5 minutes' AS bucket_start
FROM delete_test
),
numeric_bucketed AS (
    SELECT
        key,
        entity_id,
        bucket_start,
        MAX(ts) AS ts,
        AVG(
            CASE
                WHEN long_v IS NOT NULL THEN long_v::double precision
                ELSE dbl_v
            END
        ) AS avg_val,
        NULL::boolean AS bool_v,
        NULL::text AS str_v,
        NULL::json AS json_v
    FROM base
    WHERE long_v IS NOT NULL OR dbl_v IS NOT NULL
    GROUP BY key, entity_id, bucket_start
),

non_numeric_rows AS (
    SELECT
        key,
        entity_id,
        bucket_start,
        ts,
        NULL::double precision AS avg_val,
        bool_v,
        str_v,
        json_v
    FROM base
    WHERE long_v IS NULL AND dbl_v IS NULL
)

SELECT * FROM numeric_bucketed
UNION ALL
SELECT * FROM non_numeric_rows
) final_result
ORDER BY key, entity_id, bucket_start, ts




table structure for delete_test2
CREATE TABLE delete_test (
    id INTEGER PRIMARY key,
    key INTEGER,
    entity_id text,
    ts bigint,
    long_v bigint,
    dbl_v double precision,
    bool boolean,
    str_v text,
    json_v text
);




generate query which will return the group by ts and count of id

SELECT ts, COUNT(id) AS id_count
FROM delete_test2
GROUP BY ts
ORDER BY ts;

--max and min time 
SELECT min(ts) from device_logs_1000

SELECT max(ts) FROM device_logs_1000







SELECT DISTINCT to_timestamp(ts/1000.0)
from delete_test2




--auto increment in postgressql
ALTER TABLE users
ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;

ALTER TABLE device_logs_ts_kv_2024_06
ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;



Alter table compressed_device_logs
Alter column id ADD GENERATED ALWAYS AS IDENTITY; 

  
SELECT * FROM device_logs_demo
SELECT * FROM compressed_device_logs


SELECT COUNT(DISTINCT entity_id) FROM compressed_device_logs

SELECT COUNT(DISTINCT entity_id) FROM device_logs_demo

SELECT COUNT(DISTINCT key ) FROM device_logs_demo

SELECT COUNT(DISTINCT key ) FROM compressed_device_logs

SELECT * from compressed_device_logs ORDER by ts;

SELECT * FROM device_logs where key = '57' and entity_id = 'b7c7fa20-845b-11ed-b518-433f6848ae78'

drop table if EXISTS compressed_device_logs;


select avg(dbl_v) from compressed_device_logs where entity_id = '33574000-7792-11ed-b518-433f6848ae78'
and key = '17' and ts >= '1690848000000' and ts < '1690848300000' 


select avg(dbl_v) from compressed_device_logs where entity_id = 'c6c1e680-845b-11ed-b518-433f6848ae78'
and key = '62' and ts >= '1690848000000' and ts < '1690848300000' 

select * from device_logs where entity_id = 'c6c1e680-845b-11ed-b518-433f6848ae78'
and key = 62


select avg(dbl_v) from compressed_device_logs where entity_id = 'c6c1e680-845b-11ed-b518-433f6848ae78'
and key = '62' and ts >= '1693195800000' and ts < '1693196100000' 

select * from compressed_device_logs where entity_id = '33574000-7792-11ed-b518-433f6848ae78'
and key = '17' and ts >= '1690848000000' and ts < '1690848300000' 

select avg(long_v) from compressed_device_logs where entity_id = '33574000-7792-11ed-b518-433f6848ae78'
and key = '17' and ts >= '1690848000000' and ts < '1690848300000' 


select * from compressed_device_logs where entity_id = '6046da40-9c7b-11ed-8ed6-7b49dc2e0106'
and key = '54' and ts >= '1690848000000' and ts < '1690848300000'


select * from compressed_device_logs where entity_id = 'c6c1e680-845b-11ed-b518-433f6848ae78'
and key = '62' and ts >= '1693195800000' and ts < '1693196100000' 

select * from compressed_device_logs_ts_kv_2024_06 where entity_id = '6046da40-9c7b-11ed-8ed6-7b49dc2e0106'






select entity_id,key from compressed_device_logs group by entity_id,key 

select entity_id,key from device_logs group by entity_id,key 

select * from compressed_device_logs where json_v is not null or str_v is not null or bool_v is not null 

select * from device_logs where json_v is not null or str_v is not null or bool_v is not null   

SELECT entity_id, key, json_v, str_v, bool_v
FROM your_table_name
WHERE (json_v IS NOT NULL OR str_v IS NOT NULL OR bool_v IS NOT NULL)
  AND entity_id = '7bb08550-7792-11ed-b518-433f6848ae78'
  AND key = '38';


No of lines before compression : 4,83,83,237

No of lines after compression : 64,71,579





















-- command to connect with postgressql from terminal
psql -d test  -U postgres  -W



--Different host database
psql -h my-psql-db.cloud.neon.tech -d tutorials_db -U admin -W

--SSL mode
psql "sslmode=require host=my-psql-db.cloud.neon.tech dbname=tutorials_db user=admin"

--list databases
\l


-- Switch to another database - \c
\c tutorials_db


--List database tables - \dt
\dt


--Describe a table - \d
\d device_logs_demo


--List users and their roles - \du
\du

--Retrieve a specific user - \du
\du username

--List all functions - \df
\df



--List all views - \dv
\dv

--Save query results to a file - \o
\o output.txt
SELECT * FROM users;
\o

--Quit psql - \q
\q

--drop table
DROP TABLE IF EXISTS device_logs_demo;

drop table if EXISTS compressed_device_logs;

--drop database
DROP DATABASE IF EXISTS tutorials_db;



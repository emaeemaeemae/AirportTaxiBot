drop database if exists airport_taxi_bot;
create database airport_taxi_bot;
use airport_taxi_bot;


create table main
(
    id             int(11) primary key auto_increment,
    admin_username varchar(50),
    district       varchar(50),
    class_auto     varchar(50),
    users_count    int(1),
    max_users      int(1),
    create_date    datetime default current_timestamp
);

ALTER TABLE `main`
    CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci
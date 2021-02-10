

CREATE TABLE UserTable (
 user_id SERIAL PRIMARY KEY ,
 user_name CHAR(10) NOT NULL,
 lastest_post_ts timestamp without time zone NOT NULL
);

CREATE TABLE Blog (
 blog_id SERIAL PRIMARY KEY ,
 user_id bigint NOT NULL UNIQUE,
 content text NOT NULL,
 is_deleted CHAR(1) NOT NULL,
 post_date timestamp without time zone NOT NULL,
 FOREIGN KEY(user_id) REFERENCES UserTable(user_id)
);

CREATE TABLE Follow (
 id SERIAL PRIMARY KEY ,
 user_id bigint NOT NULL,
 following_user_id bigint NOT NULL,
 FOREIGN KEY(user_id) REFERENCES UserTable(user_id),
 FOREIGN KEY(following_user_id) REFERENCES UserTable(user_id)
);


# 这种获取一次大量数据的地方，很明显可以加cache
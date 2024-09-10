CREATE TABLE IF NOT EXISTS sample_table (
    column_name_1 int,
    column_name_2 int,
    column_name_3 int,
    column_name_4 text static,
    column_name_5 int,
    column_name_6 counter,
    column_name_7 list<int>,
    column_name_8 set<int>,
    column_name_9 map<int>,
    column_name_10 custom_int,
    column_name_11 tuple<int, set<int>>,
    column_name_12 int,

    PRIMARY KEY (column_name_1, column_name_2, column_name_3)
) WITH CLUSTERING ORDER BY (column_name_3 DESC);
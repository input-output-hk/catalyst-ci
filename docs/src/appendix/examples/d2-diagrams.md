---
icon: material/draw
---

# Converting CQL to D2

This is the guide how to use the earthly target
to convert a CQL schema file into D2 diagram entity.

Following is the sample of using the target:

```earthly
VERSION 0.8

IMPORT utilities/cql-to-d2 AS cql-to-d2-utils

example:
    FROM scratch

    COPY . .

    COPY (+cql-to-d2/diagrams --input="./input") ./output

    RUN ls ./output
```

## Converting result sample

This is the sample valid CQL schema code:

```cql
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
```

Resulted in D2:

```d2
{{ include_file('src/appendix/examples/diagrams/sample_d2.d2') }}
```

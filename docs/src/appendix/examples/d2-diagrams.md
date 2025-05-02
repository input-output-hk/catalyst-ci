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
{{ include_file('./diagrams/sample_d2.cql') }}
```

Resulted in D2:

```d2
{{ include_file('./diagrams/sample_d2.d2') }}
```

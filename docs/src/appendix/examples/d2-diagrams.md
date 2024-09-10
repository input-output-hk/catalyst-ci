---
icon: material/draw
---

# D2 Diagrams

This is the guide how to use the earthly target,
to convert a CQL schema file into D2 diagram entity.

```earthly
example:
    FROM scratch

    COPY . .

    COPY (+cql-to-d2/diagrams --input="./input") ./output

    RUN ls ./output
```

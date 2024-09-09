# Cassandra Schema to D2 Diagram Converter

Converts Cassandra schemas to D2 diagram entity `sql_table`.

## How to use it

```bash
python3 main.py <input-dir> <output-dir>
```

## A valid CQL file

* Make sure that a CQL file is fundamentally syntactically correct.
* Only unquoted name is supported.
* Secondary index is not supported.
* User defined type (UDT) is not supported.
* One table per one CQL file.
* Items inside `PRIMARY KEY` must not be empty.
* In-line primary key is not supported.
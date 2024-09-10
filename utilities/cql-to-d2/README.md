# Cassandra Schema to D2 Diagram Converter

Converts Cassandra schemas to D2 diagram entity `sql_table`.
The program accepts two arguments `<src-dir>` and `<out-dir>`.
So it reads the whole directory. The files with `.cql` extension will be read.
And transform individually into the D2 diagram entity, `.d2` extension file.
If the `<out-dir>` does not exist,
then the directory will be created automatically.

## How to use it as a CLI

```bash
python3 main.py <input-dir> <output-dir>
```

## How to use it as an Earthly target

You can simply refer the target to `earthly/cassandra` in this repository.
The target is `cql-to-d2`. Make sure you include the required arguments.
After using the target,
you can save the artifact (output) according to your output path.

```earthly
COPY (+cql-to-d2/<output> --input="./<input>" --output="./<output>") ./<save-dir>
```

And include this line to your target.

## A valid CQL file and limitations

* Make sure that a CQL file is fundamentally syntactically correct.
* Only unquoted name is supported.
* Secondary index is not supported.
* User defined type (UDT) is not supported.
* One table per one CQL file.
* Items inside `PRIMARY KEY` must not be empty.
* In-line primary key is not supported.

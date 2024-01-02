# dbviz

Simple tool to create database diagrams from postgres schemas.
The diagrams themselves are just text files, and are controlled by `.jinja` templates.
The tool builds in a default template which produces `.dot` files.

## Usage

```sh
dbviz -d database_name | dot -Tpng > schema.png
```

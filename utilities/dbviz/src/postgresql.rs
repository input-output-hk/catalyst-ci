//! Loader for postgresql.

// This is not production code, so while we should get rid of these lints, its not
// worth the time it would take, for no return value.
#![allow(clippy::unwrap_used)]
#![allow(clippy::indexing_slicing)]

use std::{
    cell::RefCell,
    collections::HashMap,
    convert::{TryFrom, TryInto},
};

use anyhow::Result;
use itertools::Itertools;
use postgres::{tls::NoTls, Client, Row};

use crate::{
    opts,
    schema::{Index, Relation, Schema, Table, TableColumn},
};

/// Struct that manages the loading and implements `Loader` trait.
pub struct Conn {
    /// Postgres client
    pg_client: RefCell<Client>,
    /// Schema name
    schema: String,
    /// Options
    opts: opts::Cli,
}

/// Check if a column is a primary key
fn is_primary_key(table: &str, column: &str, indexes: &[Index]) -> bool {
    indexes
        .iter()
        .any(|idx| idx.table == table && idx.fields.contains(&column.to_string()) && idx.primary)
}

impl Conn {
    /// Make a new postgres connection
    pub(crate) fn new(opts: &opts::Cli) -> Result<Conn> {
        let pg_client = postgres::Config::new()
            .user(&opts.pg_opts.username)
            .password(&opts.pg_opts.password)
            .dbname(&opts.pg_opts.database)
            .host(&opts.pg_opts.hostname)
            .connect(NoTls)?;

        let pg_client = RefCell::new(pg_client);
        let schema = opts.pg_opts.schema.clone();
        Ok(Conn {
            pg_client,
            schema,
            opts: opts.clone(),
        })
    }

    /// Do we include this table name?
    fn include_table(&self, name: &String) -> bool {
        match &self.opts.include_tables {
            Some(inc) => inc.contains(name),
            None => true,
        }
    }

    /// Do we exclude this table name?
    fn exclude_table(&self, name: &String) -> bool {
        match &self.opts.exclude_tables {
            Some(inc) => inc.contains(name),
            None => false,
        }
    }

    /// Load the schema
    pub(crate) fn load(&self) -> Result<Schema> {
        let mut client = self.pg_client.borrow_mut();
        let tables_rows = client.query(tables_query(), &[&self.schema])?;
        let relations_rows = client.query(relations_query(), &[&self.schema])?;
        let index_rows = client.query(index_query(), &[])?;

        let mut partial_tables: HashMap<String, Vec<String>> = HashMap::new();

        let indexes: Vec<_> = index_rows
            .into_iter()
            .filter(|row| {
                let row_name: String = row.get(0);
                self.include_table(&row_name) && !self.exclude_table(&row_name)
            })
            .map(|row| {
                let idx: Index = row.try_into().unwrap();
                idx
            })
            .collect();

        let tables: Vec<_> = tables_rows
            .into_iter()
            .group_by(|row| row.get(0))
            .into_iter()
            .filter(|(name, _rows)| self.include_table(name) && !self.exclude_table(name))
            .map(|(name, rows)| {
                let fields: Vec<_> = rows
                    .into_iter()
                    .map(|row| {
                        let mut field: TableColumn = row.try_into().unwrap();
                        field.primary_key = is_primary_key(&name, &field.column, &indexes);

                        let desc = match field.description {
                            Some(desc) => {
                                match self.opts.column_description_wrap {
                                    Some(wrap) => Some(textwrap::fill(&desc, wrap)),
                                    None => Some(desc),
                                }
                            },
                            None => None,
                        };
                        field.description = desc;

                        field
                    })
                    .collect();

                let desc = match &fields[0].table_description {
                    Some(desc) => {
                        match self.opts.table_description_wrap {
                            Some(wrap) => Some(textwrap::fill(desc, wrap)),
                            None => Some(desc).cloned(),
                        }
                    },
                    None => None,
                };

                Table {
                    name,
                    description: desc,
                    fields,
                }
            })
            .collect();

        let relations: Vec<_> = relations_rows
            .into_iter()
            .map(|row| {
                let relation: Relation = row.try_into().unwrap();
                relation
            })
            .filter(|relation| {
                if self.include_table(&relation.on_table)
                    && !self.exclude_table(&relation.on_table)
                    && !self.exclude_table(&relation.to_table)
                {
                    if !self.include_table(&relation.to_table) {
                        match partial_tables.get_mut(&relation.to_table) {
                            Some(value) => {
                                if !value.contains(&relation.to_field) {
                                    value.push(relation.to_field.clone());
                                }
                            },
                            None => {
                                partial_tables.insert(relation.to_table.clone(), vec![relation
                                    .to_field
                                    .clone()]);
                            },
                        }
                    }
                    true
                } else {
                    false
                }
            })
            .collect();

        Ok(Schema {
            tables,
            relations,
            partial_tables,
        })
    }
}

impl TryFrom<Row> for Index {
    type Error = String;

    fn try_from(row: Row) -> std::result::Result<Self, String> {
        let all_fields: String = row.get(4);
        let braces: &[_] = &['{', '}'];

        let fields: Vec<_> = all_fields
            .trim_matches(braces)
            .split(',')
            .map(std::string::ToString::to_string)
            .collect();

        Ok(Self {
            table: row.get(0),
            // name: row.get(1),
            primary: row.get(2),
            // unique: row.get(3),
            fields,
        })
    }
}

impl TryFrom<Row> for Relation {
    type Error = String;

    fn try_from(row: Row) -> std::result::Result<Self, String> {
        let fields: HashMap<String, String> = row
            .columns()
            .iter()
            .enumerate()
            .map(|(i, c)| (c.name().to_string(), row.get(i)))
            .collect();

        Ok(Self {
            on_table: fetch_field(&fields, "on_table")?,
            on_field: fetch_field(&fields, "on_field")?,
            to_table: fetch_field(&fields, "to_table")?,
            to_field: fetch_field(&fields, "to_field")?,
        })
    }
}

impl TryFrom<Row> for TableColumn {
    type Error = String;

    fn try_from(row: Row) -> std::result::Result<Self, String> {
        Ok(Self {
            column: row.get(1),
            data_type: row.get(2),
            index: row.get(3),
            default: row.get(4),
            nullable: row.get(5),
            max_chars: row.get(6),
            description: row.get(7),
            table_description: row.get(8),
            primary_key: false,
        })
    }
}

/// Fetch a field from a hashmap
fn fetch_field(map: &HashMap<String, String>, key: &str) -> std::result::Result<String, String> {
    map.get(key)
        .cloned()
        .ok_or(format!("could not find field {key}"))
}

/// Query all tables and columns
fn tables_query() -> &'static str {
    "
    select table_name, column_name, data_type, ordinal_position, column_default, is_nullable, character_maximum_length, col_description(table_name::regclass, ordinal_position), obj_description(table_name::regclass)
      from information_schema.columns
     where table_schema = $1
     order by table_name, ordinal_position
    "
}

/// Query all relationships
fn relations_query() -> &'static str {
    "
    select *
      from (
        select ns.nspname AS schemaname,
               cl.relname AS on_table,
               attr.attname AS on_field,
               clf.relname AS to_table,
               attrf.attname AS to_field
          from pg_constraint con
                 join pg_class cl
                     on con.conrelid = cl.oid
                 join pg_namespace ns
                     on cl.relnamespace = ns.oid
                 join pg_class clf
                     on con.confrelid = clf.oid
                 join pg_attribute attr
                     on attr.attnum = ANY(con.conkey) and
                 attr.attrelid = con.conrelid
                 join pg_attribute attrf
                     on attrf.attnum = ANY(con.confkey) and
                 attrf.attrelid = con.confrelid
      ) as fk
     where fk.schemaname = $1
    "
}

/// Query all indexes
fn index_query() -> &'static str {
    "
SELECT
    CAST(idx.indrelid::regclass as varchar) as table_name,
    i.relname as index_name,
    idx.indisprimary as primary_key,
    idx.indisunique as unique,
    CAST(
        ARRAY(
            SELECT pg_get_indexdef(idx.indexrelid, k + 1, true)
            FROM generate_subscripts(idx.indkey, 1) as k
            ORDER BY k
        ) as varchar
    ) as columns
FROM   pg_index as idx
JOIN   pg_class as i
ON     i.oid = idx.indexrelid
JOIN   pg_am as am
ON     i.relam = am.oid
JOIN   pg_namespace as ns
ON     ns.oid = i.relnamespace
AND    ns.nspname = ANY(current_schemas(false))
ORDER BY idx.indrelid
"
}

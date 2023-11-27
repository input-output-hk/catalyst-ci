//! Core entities.
use std::collections::HashMap;

use serde::{Deserialize, Serialize};

/// All the schema information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct Schema {
    /// List of tables in the database.
    pub(crate) tables: Vec<Table>,
    /// List of relations in the database.
    pub(crate) relations: Vec<Relation>,
    /// Partial Tables
    pub(crate) partial_tables: HashMap<String, Vec<String>>,
}

/// Table information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct TableColumn {
    /// Column name.
    pub(crate) column: String,
    /// Column data type.
    pub(crate) data_type: String,
    /// Column index.
    pub(crate) index: i32,
    /// Column default.
    pub(crate) default: Option<String>,
    /// Column nullable.
    pub(crate) nullable: String,
    /// Column max chars.
    pub(crate) max_chars: Option<i32>,
    /// Column description.
    pub(crate) description: Option<String>,
    /// Table description.
    pub(crate) table_description: Option<String>, // Redundant but easiest way to get it.
    /// Column primary key.
    pub(crate) primary_key: bool,
}

/// Table information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct Table {
    /// Table name.
    pub(crate) name: String,
    /// Table Description
    pub(crate) description: Option<String>,
    /// List of fields.
    pub(crate) fields: Vec<TableColumn>,
}

/// Row description.
//#[derive(Debug)]
// pub(crate)struct Field(pub(crate)FieldName, pub(crate)FieldType);

/// Relation node.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct Relation {
    /// Table that the constraint references.
    pub(crate) on_table: TableName,
    /// Field that the constraint references.
    pub(crate) on_field: FieldName,
    /// Table which the fk references.
    pub(crate) to_table: TableName,
    /// Field which the fk references.
    pub(crate) to_field: FieldName,
}

/// Table name
pub(crate) type TableName = String;
/// Field name
pub(crate) type FieldName = String;
// pub(crate)type FieldType = String;

/// Index Definition
pub(crate) struct Index {
    /// Table name
    pub(crate) table: TableName,
    // pub(crate)name: String,
    /// Primary Key
    pub(crate) primary: bool,
    // pub(crate)unique: bool,
    /// Fields
    pub(crate) fields: Vec<String>,
}

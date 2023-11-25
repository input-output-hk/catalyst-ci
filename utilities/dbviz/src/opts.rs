//! CLI Option parsing

use std::path::PathBuf;

use clap::{Args, Parser};
use serde::{Deserialize, Serialize};

#[derive(Debug, Parser, Clone, Serialize, Deserialize)]
#[command(author, version, about, long_about = None)]
/// `DBViz` a tool for generating database diagrams.
pub(crate)struct Cli {
    #[command(flatten)]
    /// Postgres connection options
    pub(crate)pg_opts: Pg,

    #[arg(short, long)]
    /// Tables to include in the current diagram.
    pub(crate)include_tables: Option<Vec<String>>,

    #[arg(short, long)]
    /// Tables to completely exclude in the current diagram.
    pub(crate)exclude_tables: Option<Vec<String>>,

    /// Title to give the Diagram
    #[arg(short, long)]
    pub(crate)title: Option<String>,

    /// How wide is the Column Description before we wrap it?
    #[arg(long)]
    pub(crate)column_description_wrap: Option<usize>,

    /// How wide is the Table Description before we wrap it?
    #[arg(long)]
    pub(crate)table_description_wrap: Option<usize>,

    /// Do we include comments in the diagram?
    #[arg(long)]
    pub(crate)comments: bool,

    /// Input file
    pub(crate)template: Option<PathBuf>,

    /// Output file
    pub(crate)output: Option<PathBuf>,
}

#[derive(Debug, Args, Clone, Serialize, Deserialize)]
/// Postgres connection options
pub(crate)struct Pg {
    #[arg(short, long, default_value = "localhost")]
    /// Hostname to connect to 
    pub(crate)hostname: String,

    #[arg(short, long, default_value = "postgres")]
    /// Username to use when connecting
    pub(crate)username: String,

    #[arg(short, long, default_value = "postgres")]
    /// Password to use when connecting
    pub(crate)password: String,

    #[arg(short, long, default_value = "postgres")]
    /// Database name to connect to
    pub(crate)database: String,

    #[arg(short, long, default_value = "public")]
    /// Schema name to use
    pub(crate)schema: String,
}

/// Load CLI Options.
pub(crate)fn load() -> Cli {
    Cli::parse()
}

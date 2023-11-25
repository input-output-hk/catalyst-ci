//! `DBViz` - Database Diagram Generator
//!
//! `DBViz` is a tool for generating database diagrams.

mod opts;
mod postgresql;
mod schema;

use std::fs;

use anyhow::Result;
use minijinja::{context, Environment};

fn main() -> Result<()> {
    let opts = opts::load();

    let loader = postgresql::Conn::new(&opts)?;
    let schema = loader.load()?;

    let template_file = match &opts.template {
        Some(fname) => fs::read_to_string(fname)?,
        None => include_str!("default_template.jinja").to_string(),
    };

    let mut env = Environment::new();
    env.add_template("diagram", &template_file)?;
    let tmpl = env.get_template("diagram")?;

    let ctx = context!(
        opts => opts,
        schema => schema
    );

    let rendered = tmpl.render(ctx)?;

    println!("{rendered}");

    Ok(())
}

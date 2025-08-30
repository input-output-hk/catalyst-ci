//! Simple program to greet a person.
//! Used as a test of the Rust CI/CD pipeline.

use clap::Parser;
use foo::fmt_hello;

/// Simple program to greet a person
#[cfg_attr(debug_assertions, derive(Debug))]
#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Name of the person to greet
    #[arg(short, long)]
    name: String,

    /// Number of times to greet
    #[arg(short, long, default_value_t = 1)]
    count: u8,
}

/// The main entrypoint of this program.
fn main() {
    let args = Args::parse();

    #[cfg(debug_assertions)]
    println!("{args:?}");

    for cnt in 0..args.count {
        println!("{}", fmt_hello(&args.name, cnt));
    }
}

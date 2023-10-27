// src/main.rs
use clap::{App, Arg};

fn main() {
    let matches = App::new("Hello, World!")
        .version("1.0")
        .arg(
            Arg::with_name("version")
                .short('v')
                .long("version")
                .help("Print the program version"),
        )
        .get_matches();

    if matches.is_present("version") {
        println!("Hello, World! v1.0");
        return;
    }

    println!("Hello, World!");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hello_world() {
        assert_eq!(main(), ());
    }
}

//! Our simple library crate.

/// Format our hello message nicely.
#[must_use]
pub fn fmt_hello(name: &str, count: u8) -> String {
    format!("Hello #{count:>3} {name}!")
}

/// Excessive unit tests for this function.
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    /// Prove we can say hello to Dave on a 3 count.
    fn test_hello_dave_3() {
        let msg = fmt_hello("Dave", 3);
        assert_eq!(msg, "Hello #  3 Dave!");
    }

    #[test]
    /// Prove we can say hello to Sally on a 67 count.
    fn test_hello_sally_67() {
        let msg = fmt_hello("Sally", 67);
        assert_eq!(msg, "Hello # 67 Sally!");
    }

    #[test]
    /// Prove we can say hello to World on a 123 count.
    fn test_hello_world_123() {
        let msg = fmt_hello("World", 123);
        assert_eq!(msg, "Hello #123 World!");
    }
}

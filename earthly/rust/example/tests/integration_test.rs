// tests/integration_test.rs
#[cfg(test)]
mod integration_tests {
    use super::*;

    #[test]
    fn test_hello_world() {
        assert_eq!(main(), ());
    }
}

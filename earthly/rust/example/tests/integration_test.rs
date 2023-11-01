//! Simple integration tests

#[test]
/// Prove we can say hello to Dave on a 99 count.
fn test_hello_dave_99() {
    let msg = fmt_hello("Dave", 99);
    assert_eq!(msg, "Hello # 99 Dave!");
}

/// Dummy main needed because we are integration testing a binary package.
fn main() {}

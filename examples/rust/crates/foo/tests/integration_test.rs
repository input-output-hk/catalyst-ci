//! Simple integration tests

#[test]
#[ignore]
/// Prove we can say hello to Dave on a 99 count.
fn test_hello_dave_99() {
    let msg = foo::fmt_hello("Dave", 99);
    assert_eq!(msg, "Hello # 99 Dave!");
}

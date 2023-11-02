#!/usr/bin/env bash

assert_eq() {
  local expected="$1"
  local actual="$2"

  if [ "$expected" == "$actual" ]; then
    return 0
  else
    echo "assert_eq FAILED"
    echo "expected:"
    echo "$expected"
    echo "actual:"
    echo "$actual"
    echo "Diff:"
    diff  <(echo "$expected" ) <(echo "$actual")
    return 1
  fi
}
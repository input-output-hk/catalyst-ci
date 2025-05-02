#!/usr/bin/env python
"""General Utility Functions."""

import sys
import unittest


def fix_quoted_earthly_args() -> None:
    """Arguments that are quoted in Earthly need to be corrected to be parsed.

    This function does that by modifying sys.argv in-place.

    It should still work with normal argument strings from a command line.
    """
    # Fix arguments because of munging that can happen because of the
    # rust builder +EXECUTE function and the necessity to quote the arguments.
    processed_args = []
    for arg in sys.argv[1:]:
        # To fix quoting, if the previous arg has one quote, add subsequent args
        # to it with a single space until it has more than one quote.
        if len(processed_args) > 0 and processed_args[-1].count('"') == 1:
            processed_args[-1] += " " + arg
            # When we close the quotes, strip them from the argument.
            if processed_args[-1].count('"') != 1:
                processed_args[-1] = processed_args[-1].replace('"', "")
        else:
            processed_args.append(arg)

    # Replace sys.argv with the processed arguments
    sys.argv = [sys.argv[0], *processed_args]


class TestProcessListWithQuotes(unittest.TestCase):
    """Test Process List With Quotes."""

    def test_process_list_with_quotes(self) -> None:
        """Test Process List with Quotes."""
        sys.argv = [sys.argv[0], "this", 'has "quoted', "strings", 'in it"', "this", "doesn't"]
        expected_result = ["this", "has quoted strings in it", "this", "doesn't"]
        fix_quoted_earthly_args()
        self.assertEqual(sys.argv[1:], expected_result)


if __name__ == "__main__":
    unittest.main()

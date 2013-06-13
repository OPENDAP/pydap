"""Test parsing functions."""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from pydap.parsers import (
    parse_projection, parse_ce, parse_hyperslab, SimpleParser)


class TestParseProjection(unittest.TestCase):

    """Test projection parser.

    The projection is a comma separated list of variable ids (or names, if the
    client is using the shorthand notation), with optional hyperslabs and
    possibly function calls.

    """

    def test_basic(self):
        """Test a basic projection."""
        parsed = parse_projection("a,b,c")
        self.assertEqual(parsed, [[("a", ())], [("b", ())], [("c", ())]])

    def test_deep(self):
        """Test a projection with a deep id."""
        parsed = parse_projection("a.b.c,d")
        self.assertEqual(
            parsed, [[("a", ()), ("b", ()), ("c", ())], [("d", ())]])

    def test_hyperslab(self):
        """Test a projection with a hyperslab."""
        parsed = parse_projection("a,b.c[0:2:9]")
        self.assertEqual(
            parsed, [[("a", ())], [("b", ()), ("c", (slice(0, 10, 2),))]])

    def test_function_call(self):
        """Test a projection with a function call."""
        parsed = parse_projection("mean(a[0],1)")
        self.assertEqual(
            parsed, ['mean(a[0],1)'])

    def test_nested_function_call(self):
        """Test a projection with a function call."""
        parsed = parse_projection("mean(mean(a[0],1))")
        self.assertEqual(
            parsed, ['mean(mean(a[0],1))'])


class TestParseCe(unittest.TestCase):

    """Test the constraint expression parser."""

    def test_basic(self):
        """Test a basic constraint expression."""
        projection, selection = parse_ce("a,b&c>1")
        self.assertEqual(projection, [[("a", ())], [("b", ())]])
        self.assertEqual(selection, ["c>1"])

    def test_only_projection(self):
        """Test a constraint expression with only the projection."""
        projection, selection = parse_ce("a,b")
        self.assertEqual(projection, [[("a", ())], [("b", ())]])
        self.assertEqual(selection, [])

    def test_only_selection(self):
        """Test a constraint expression with only the selection."""
        projection, selection = parse_ce("c>1")
        self.assertEqual(projection, [])
        self.assertEqual(selection, ["c>1"])

    def test_complex(self):
        """Test a more complex constraint expression."""
        projection, selection = parse_ce("a,b[0:2:9],c&a>1&b<2")
        self.assertEqual(
            projection,
            [[("a", ())], [("b", (slice(0, 10, 2),))], [("c", ())]])
        self.assertEqual(selection, ["a>1", "b<2"])

    def test_function(self):
        """Test a constraint expression with a function call."""
        projection, selection = parse_ce(
            "time&bounds(0,360,-90,90,0,500,00Z01JAN1970,00Z04JAN1970)")
        self.assertEqual(projection, [[("time", ())]])
        self.assertEqual(
            selection,
            ["bounds(0,360,-90,90,0,500,00Z01JAN1970,00Z04JAN1970)"])

    def test_function_no_selection(self):
        """Test a constraint expression with a function call."""
        projection, selection = parse_ce(
            "time,bounds(0,360,-90,90,0,500,00Z01JAN1970,00Z04JAN1970)")
        self.assertEqual(
            projection,
            [[("time", ())],
                'bounds(0,360,-90,90,0,500,00Z01JAN1970,00Z04JAN1970)'])
        self.assertEqual(selection, [])


class TestParseHyperslab(unittest.TestCase):

    """Test hyperslab parser."""

    def test_point(self):
        """Test a single value selection."""
        self.assertEqual(parse_hyperslab('[0]'), (slice(0, 1, 1),))

    def test_start_stop(self):
        """Test start and stop, default step."""
        self.assertEqual(parse_hyperslab('[0:1]'), (slice(0, 2, 1),))

    def test_start_step_stop(self):
        """Test start, step and stop."""
        self.assertEqual(parse_hyperslab('[0:2:9]'), (slice(0, 10, 2),))


class TestSimpleParser(unittest.TestCase):

    """Test the base class for the DAS/DDS parsers."""

    def test_peek_existing(self):
        """Test the peek method when the token exists."""
        parser = SimpleParser("Hello, World!")
        self.assertEqual(parser.peek("\w+"), "Hello")

    def test_peek_missing(self):
        """Test the peek method when the token does not exist."""
        parser = SimpleParser("Hello, World!")
        self.assertEqual(parser.peek("\d+"), "")

    def test_consume_existing(self):
        """Test the consume method when the token exists."""
        parser = SimpleParser("Hello, World!")
        self.assertEqual(parser.consume("\w+"), "Hello")
        self.assertEqual(parser.consume(", "), ", ")
        self.assertEqual(parser.consume("\w+"), "World")
        self.assertEqual(parser.consume("!"), "!")

    def test_consume_existing(self):
        """Test the consume method when the token does not exist."""
        parser = SimpleParser("Hello, World!")
        with self.assertRaises(Exception):
            parser.consume("\d+")

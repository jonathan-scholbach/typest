from unittest import TestCase

from typest.utils.fake_type import (
    FakeGeneric,
    parse,
    parse_arg_list,
    FakeBuiltin,
    FakeUnion,
)


class TestParse(TestCase):
    def test_bare_builtin(self):
        bare = parse("int")
        self.assertEqual(bare, FakeBuiltin("int"))

    def test_verbose_builtin(self):
        verbose = parse("builtins.int")
        self.assertEqual(verbose, FakeBuiltin("int"))

    def test_traditional_optional(self):
        optional = parse("Optional[SomeType]")
        self.assertEqual(optional, FakeUnion("SomeType", "None"))

    def test_optional_builtin(self):
        optional = parse("Optional[bool]")
        self.assertEqual(optional, FakeUnion(FakeBuiltin("bool"), "None"))

    def test_union(self):
        union = parse("Union[SomeType, OtherType]")
        self.assertEqual(union, FakeUnion("SomeType", "OtherType"))

    def test_piped_union(self):
        union = parse("SomeType | OtherType")
        self.assertEqual(union, FakeUnion("SomeType", "OtherType"))

    def test_union_builtin(self):
        union = parse("Union[None, int]")
        self.assertEqual(
            union,
            FakeUnion(FakeBuiltin("None"), FakeBuiltin("int")),
        )

    def test_simple_generic(self):
        generic = parse("SomeGeneric[int]")
        self.assertEqual(generic, FakeGeneric("SomeGeneric", FakeBuiltin("int")))

    def test_nested_generic(self):
        generic = parse("SomeGeneric[Union[int, str]]")
        self.assertEqual(
            generic, FakeGeneric("SomeGeneric", FakeUnion(FakeBuiltin("int"), FakeBuiltin("str")))
        )


class TestParseArgList(TestCase):
    def test_flat_list(self):
        text = "str, int, float"
        self.assertEqual(
            parse_arg_list(text),
            (FakeBuiltin("str"), FakeBuiltin("int"), FakeBuiltin("float")),
        )

    def test_nested_list(self):
        text = "Union[str, int], str"
        self.assertEqual(parse_arg_list(text), (FakeUnion("str", "int"), FakeBuiltin("str")))


class TestEquality(TestCase):
    def test_builtins(self):
        bare = parse("int")
        verbose = parse("builtins.int")
        self.assertEqual(verbose, bare)

    def test_none_equals_none_type(self):
        none = FakeBuiltin("None")
        none_type = FakeBuiltin("NoneType")
        self.assertEqual(none, none_type)

    def test_union_order_does_not_matter(self):
        this_or_that = FakeUnion("this", "that")
        that_or_this = FakeUnion("that", "this")
        self.assertEqual(this_or_that, that_or_this)

    def test_union_multiple_occurrences_of_same_type_dont_matter(self):
        once = FakeUnion("SomeType")
        twice = FakeUnion("SomeType", "SomeType")
        self.assertEqual(once, twice)

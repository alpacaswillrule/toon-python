import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from toon import DELIMITERS, encode


class EncodeTests(unittest.TestCase):
    def test_encode_primitives(self):
        self.assertEqual(encode("hello"), "hello")
        self.assertEqual(encode("Ada_99"), "Ada_99")
        self.assertEqual(encode(""), '""')
        self.assertEqual(encode("true"), '"true"')
        self.assertEqual(encode("false"), '"false"')
        self.assertEqual(encode("null"), '"null"')
        self.assertEqual(encode("42"), '"42"')
        self.assertEqual(encode("-3.14"), '"-3.14"')
        self.assertEqual(encode("1e-6"), '"1e-6"')
        self.assertEqual(encode("05"), '"05"')
        self.assertEqual(encode("line1\nline2"), '"line1\\nline2"')
        self.assertEqual(encode("tab\there"), '"tab\\there"')
        self.assertEqual(encode("return\rcarriage"), '"return\\rcarriage"')
        self.assertEqual(encode(r"C:\Users\path"), '"C:\\\\Users\\\\path"')
        self.assertEqual(encode("[3]: x,y"), '"[3]: x,y"')
        self.assertEqual(encode("- item"), '"- item"')
        self.assertEqual(encode("[test]"), '"[test]"')
        self.assertEqual(encode("{key}"), '"{key}"')
        self.assertEqual(encode("café"), "café")
        self.assertEqual(encode("你好"), "你好")
        self.assertEqual(encode("🚀"), "🚀")
        self.assertEqual(encode("hello 👋 world"), "hello 👋 world")
        self.assertEqual(encode(42), "42")
        self.assertEqual(encode(3.14), "3.14")
        self.assertEqual(encode(-7), "-7")
        self.assertEqual(encode(0), "0")
        self.assertEqual(encode(-0.0), "0")
        self.assertEqual(encode(1_000_000), "1000000")
        self.assertEqual(encode(1e-6), "0.000001")
        self.assertEqual(encode(1e20), "100000000000000000000")
        self.assertEqual(encode(True), "true")
        self.assertEqual(encode(False), "false")
        self.assertEqual(encode(None), "null")

    def test_simple_objects(self):
        self.assertEqual(
            encode({"id": 123, "name": "Ada", "active": True}),
            "id: 123\nname: Ada\nactive: true",
        )
        self.assertEqual(
            encode({"id": 123, "value": None}),
            "id: 123\nvalue: null",
        )
        self.assertEqual(encode({}), "")
        self.assertEqual(encode({"note": "a:b"}), 'note: "a:b"')
        self.assertEqual(encode({"note": "a,b"}), 'note: "a,b"')
        self.assertEqual(encode({"text": "line1\nline2"}), 'text: "line1\\nline2"')
        self.assertEqual(encode({"text": 'say "hello"'}), 'text: "say \\"hello\\""')
        self.assertEqual(encode({"text": " padded "}), 'text: " padded "')
        self.assertEqual(encode({"text": "  "}), 'text: "  "')
        self.assertEqual(encode({"v": "true"}), 'v: "true"')
        self.assertEqual(encode({"v": "42"}), 'v: "42"')
        self.assertEqual(encode({"v": "-7.5"}), 'v: "-7.5"')

    def test_object_keys(self):
        self.assertEqual(encode({"order:id": 7}), '"order:id": 7')
        self.assertEqual(encode({"[index]": 5}), '"[index]": 5')
        self.assertEqual(encode({"{key}": 5}), '"{key}": 5')
        self.assertEqual(encode({"a,b": 1}), '"a,b": 1')
        self.assertEqual(encode({"full name": "Ada"}), '"full name": Ada')
        self.assertEqual(encode({"-lead": 1}), '"-lead": 1')
        self.assertEqual(encode({" a ": 1}), '" a ": 1')
        self.assertEqual(encode({123: "x"}), '"123": x')
        self.assertEqual(encode({"": 1}), '"": 1')
        self.assertEqual(encode({"line\nbreak": 1}), '"line\\nbreak": 1')
        self.assertEqual(encode({"tab\there": 2}), '"tab\\there": 2')
        self.assertEqual(encode({'he said "hi"': 1}), '"he said \\"hi\\"": 1')

    def test_nested_objects(self):
        self.assertEqual(
            encode({"a": {"b": {"c": "deep"}}}),
            "a:\n  b:\n    c: deep",
        )
        self.assertEqual(encode({"user": {}}), "user:")

    def test_arrays_of_primitives(self):
        self.assertEqual(encode({"tags": ["reading", "gaming"]}), "tags[2]: reading,gaming")
        self.assertEqual(encode({"nums": [1, 2, 3]}), "nums[3]: 1,2,3")
        self.assertEqual(encode({"data": ["x", "y", True, 10]}), "data[4]: x,y,true,10")
        self.assertEqual(encode({"items": []}), "items[0]:")
        self.assertEqual(encode({"items": [""]}), 'items[1]: ""')
        self.assertEqual(encode({"items": ["a", "", "b"]}), 'items[3]: a,"",b')
        self.assertEqual(encode({"items": [" ", "  "]}), 'items[2]: " ","  "')
        self.assertEqual(encode({"items": ["a", "b,c", "d:e"]}), 'items[3]: a,"b,c","d:e"')
        self.assertEqual(encode({"items": ["x", "true", "42", "-3.14"]}), 'items[4]: x,"true","42","-3.14"')
        self.assertEqual(encode({"items": ["[5]", "- item", "{key}"]}), 'items[3]: "[5]","- item","{key}"')

    def test_arrays_of_objects(self):
        self.assertEqual(
            encode({"items": [{"sku": "A1", "qty": 2, "price": 9.99}, {"sku": "B2", "qty": 1, "price": 14.5}]}),
            "items[2]{sku,qty,price}:\n  A1,2,9.99\n  B2,1,14.5",
        )
        self.assertEqual(
            encode({"items": [{"id": 1, "value": None}, {"id": 2, "value": "test"}]}),
            "items[2]{id,value}:\n  1,null\n  2,test",
        )
        self.assertEqual(
            encode({"items": [{"sku": "A,1", "desc": "cool", "qty": 2}, {"sku": "B2", "desc": "wip: test", "qty": 1}]}),
            'items[2]{sku,desc,qty}:\n  "A,1",cool,2\n  B2,"wip: test",1',
        )
        self.assertEqual(
            encode({"items": [{"id": 1, "status": "true"}, {"id": 2, "status": "false"}]}),
            'items[2]{id,status}:\n  1,"true"\n  2,"false"',
        )
        self.assertEqual(
            encode({"items": [{"order:id": 1, "full name": "Ada"}, {"order:id": 2, "full name": "Bob"}]}),
            'items[2]{"order:id","full name"}:\n  1,Ada\n  2,Bob',
        )
        self.assertEqual(
            encode({"items": [{"id": 1, "name": "First"}, {"id": 2, "name": "Second", "extra": True}]}),
            "items[2]:\n"
            "  - id: 1\n"
            "    name: First\n"
            "  - id: 2\n"
            "    name: Second\n"
            "    extra: true",
        )
        self.assertEqual(
            encode({"items": [{"id": 1, "nested": {"x": 1}}]}),
            "items[1]:\n"
            "  - id: 1\n"
            "    nested:\n"
            "      x: 1",
        )
        self.assertEqual(
            encode({"items": [{"nums": [1, 2, 3], "name": "test"}]}),
            "items[1]:\n"
            "  - nums[3]: 1,2,3\n"
            "    name: test",
        )
        self.assertEqual(
            encode({"items": [{"name": "test", "nums": [1, 2, 3]}]}),
            "items[1]:\n"
            "  - name: test\n"
            "    nums[3]: 1,2,3",
        )
        self.assertEqual(
            encode({"items": [{"matrix": [[1, 2], [3, 4]], "name": "grid"}]}),
            "items[1]:\n"
            "  - matrix[2]:\n"
            "    - [2]: 1,2\n"
            "    - [2]: 3,4\n"
            "    name: grid",
        )
        self.assertEqual(
            encode({"items": [{"users": [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Bob"}], "status": "active"}]}),
            "items[1]:\n"
            "  - users[2]{id,name}:\n"
            "    1,Ada\n"
            "    2,Bob\n"
            "    status: active",
        )
        self.assertEqual(
            encode({"items": [{"users": [{"id": 1, "name": "Ada"}, {"id": 2}], "status": "active"}]}),
            "items[1]:\n"
            "  - users[2]:\n"
            "    - id: 1\n"
            "      name: Ada\n"
            "    - id: 2\n"
            "    status: active",
        )
        self.assertEqual(
            encode({"items": [{"nums": [1, 2], "tags": ["a", "b"], "name": "test"}]}),
            "items[1]:\n"
            "  - nums[2]: 1,2\n"
            "    tags[2]: a,b\n"
            "    name: test",
        )
        self.assertEqual(
            encode({"items": [{"nums": [1, 2, 3], "tags": ["a", "b"]}]}),
            "items[1]:\n"
            "  - nums[3]: 1,2,3\n"
            "    tags[2]: a,b",
        )
        self.assertEqual(
            encode({"items": [{"name": "test", "data": []}]}),
            "items[1]:\n"
            "  - name: test\n"
            "    data[0]:",
        )
        self.assertEqual(
            encode({"items": [{"users": [{"id": 1}, {"id": 2}], "note": "x"}]}),
            "items[1]:\n"
            "  - users[2]{id}:\n"
            "    1\n"
            "    2\n"
            "    note: x",
        )
        self.assertEqual(
            encode({"items": [{"data": [], "name": "x"}]}),
            "items[1]:\n"
            "  - data[0]:\n"
            "    name: x",
        )
        self.assertEqual(
            encode({"items": [{"a": 1, "b": 2, "c": 3}, {"c": 30, "b": 20, "a": 10}]}),
            "items[2]{a,b,c}:\n  1,2,3\n  10,20,30",
        )
        self.assertEqual(
            encode({"items": [{"id": 1, "data": "string"}, {"id": 2, "data": {"nested": True}}]}),
            "items[2]:\n"
            "  - id: 1\n"
            "    data: string\n"
            "  - id: 2\n"
            "    data:\n"
            "      nested: true",
        )

    def test_arrays_of_arrays(self):
        self.assertEqual(
            encode({"pairs": [["a", "b"], ["c", "d"]]}),
            "pairs[2]:\n  - [2]: a,b\n  - [2]: c,d",
        )
        self.assertEqual(
            encode({"pairs": [["a", "b"], ["c,d", "e:f", "true"]]}),
            'pairs[2]:\n  - [2]: a,b\n  - [3]: "c,d","e:f","true"',
        )
        self.assertEqual(
            encode({"pairs": [[], []]}),
            "pairs[2]:\n  - [0]:\n  - [0]:",
        )
        self.assertEqual(
            encode({"pairs": [[1], [2, 3]]}),
            "pairs[2]:\n  - [1]: 1\n  - [2]: 2,3",
        )

    def test_root_arrays(self):
        self.assertEqual(
            encode(["x", "y", "true", True, 10]),
            '[5]: x,y,"true",true,10',
        )
        self.assertEqual(
            encode([{"id": 1}, {"id": 2}]),
            "[2]{id}:\n  1\n  2",
        )
        self.assertEqual(
            encode([{"id": 1}, {"id": 2, "name": "Ada"}]),
            "[2]:\n  - id: 1\n  - id: 2\n    name: Ada",
        )
        self.assertEqual(encode([]), "[0]:")
        self.assertEqual(
            encode([[1, 2], []]),
            "[2]:\n  - [2]: 1,2\n  - [0]:",
        )

    def test_complex_structure(self):
        self.assertEqual(
            encode(
                {
                    "user": {
                        "id": 123,
                        "name": "Ada",
                        "tags": ["reading", "gaming"],
                        "active": True,
                        "prefs": [],
                    }
                }
            ),
            "user:\n"
            "  id: 123\n"
            "  name: Ada\n"
            "  tags[2]: reading,gaming\n"
            "  active: true\n"
            "  prefs[0]:",
        )

    def test_mixed_arrays(self):
        self.assertEqual(
            encode({"items": [1, {"a": 1}, "text"]}),
            "items[3]:\n"
            "  - 1\n"
            "  - a: 1\n"
            "  - text",
        )
        self.assertEqual(
            encode({"items": [{"a": 1}, [1, 2]]}),
            "items[2]:\n"
            "  - a: 1\n"
            "  - [2]: 1,2",
        )

    def test_custom_delimiters_basic(self):
        self.assertEqual(
            encode({"items": ["a", "b"]}, {"delimiter": DELIMITERS["tab"]}),
            "items[2\t]: a\tb",
        )
        self.assertEqual(
            encode({"items": ["a", "b"]}, {"delimiter": DELIMITERS["pipe"]}),
            "items[2|]: a|b",
        )

    def test_custom_delimiters_quote_strings(self):
        self.assertEqual(
            encode({"items": ["a", "b\tc", "d"]}, {"delimiter": DELIMITERS["tab"]}),
            'items[3\t]: a\t"b\\tc"\td',
        )
        self.assertEqual(
            encode({"items": ["a", "b|c", "d"]}, {"delimiter": DELIMITERS["pipe"]}),
            'items[3|]: a|"b|c"|d',
        )

    def test_custom_delimiter_comma_handling(self):
        self.assertEqual(
            encode({"items": ["a,b", "c,d"]}, {"delimiter": DELIMITERS["tab"]}),
            "items[2\t]: a,b\tc,d",
        )
        self.assertEqual(
            encode({"items": ["a,b", "c,d"]}, {"delimiter": DELIMITERS["pipe"]}),
            "items[2|]: a,b|c,d",
        )

    def test_custom_delimiter_tabular_rows(self):
        obj = {"items": [{"id": 1, "note": "a,b"}, {"id": 2, "note": "c,d"}]}
        self.assertEqual(
            encode(obj, {"delimiter": DELIMITERS["comma"]}),
            'items[2]{id,note}:\n  1,"a,b"\n  2,"c,d"',
        )
        self.assertEqual(
            encode(obj, {"delimiter": DELIMITERS["tab"]}),
            "items[2\t]{id\tnote}:\n  1\ta,b\n  2\tc,d",
        )

    def test_custom_delimiter_invariants(self):
        obj = {"items": ["true", "42", "-3.14"]}
        self.assertEqual(
            encode(obj, {"delimiter": DELIMITERS["pipe"]}),
            'items[3|]: "true"|"42"|"-3.14"',
        )
        self.assertEqual(
            encode(obj, {"delimiter": DELIMITERS["tab"]}),
            'items[3\t]: "true"\t"42"\t"-3.14"',
        )

        obj_struct = {"items": ["[5]", "{key}", "- item"]}
        self.assertEqual(
            encode(obj_struct, {"delimiter": DELIMITERS["pipe"]}),
            'items[3|]: "[5]"|"{key}"|"- item"',
        )
        self.assertEqual(
            encode(obj_struct, {"delimiter": DELIMITERS["tab"]}),
            'items[3\t]: "[5]"\t"{key}"\t"- item"',
        )

    def test_custom_delimiter_keys_and_headers(self):
        self.assertEqual(
            encode({"a|b": 1}, {"delimiter": DELIMITERS["pipe"]}),
            '"a|b": 1',
        )
        self.assertEqual(
            encode({"a\tb": 1}, {"delimiter": DELIMITERS["tab"]}),
            '"a\\tb": 1',
        )
        self.assertEqual(
            encode({"items": [{"a|b": 1}, {"a|b": 2}]}, {"delimiter": DELIMITERS["pipe"]}),
            'items[2|]{"a|b"}:\n  1\n  2',
        )
        obj = {"items": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}
        self.assertEqual(
            encode(obj, {"delimiter": DELIMITERS["pipe"]}),
            "items[2|]{a|b}:\n  1|2\n  3|4",
        )
        self.assertEqual(
            encode(obj, {"delimiter": DELIMITERS["tab"]}),
            "items[2\t]{a\tb}:\n  1\t2\n  3\t4",
        )

    def test_length_marker(self):
        self.assertEqual(
            encode({"tags": ["reading", "gaming", "coding"]}, {"length_marker": "#"}),
            "tags[#3]: reading,gaming,coding",
        )
        self.assertEqual(
            encode({"items": []}, {"length_marker": "#"}),
            "items[#0]:",
        )
        obj = {"items": [{"sku": "A1", "qty": 2, "price": 9.99}, {"sku": "B2", "qty": 1, "price": 14.5}]}
        self.assertEqual(
            encode(obj, {"length_marker": "#"}),
            "items[#2]{sku,qty,price}:\n  A1,2,9.99\n  B2,1,14.5",
        )
        self.assertEqual(
            encode({"pairs": [["a", "b"], ["c", "d"]]}, {"length_marker": "#"}),
            "pairs[#2]:\n  - [#2]: a,b\n  - [#2]: c,d",
        )
        self.assertEqual(
            encode({"tags": ["reading", "gaming", "coding"]}, {"length_marker": "#", "delimiter": "|"}),
            "tags[#3|]: reading|gaming|coding",
        )
        self.assertEqual(
            encode({"tags": ["reading", "gaming", "coding"]}),
            "tags[3]: reading,gaming,coding",
        )


if __name__ == "__main__":
    unittest.main()

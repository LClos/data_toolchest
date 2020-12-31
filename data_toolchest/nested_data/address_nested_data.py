"""Tools to parse and index all values in nested data structures."""
import json
import sys

from pathlib import Path, PurePath
from typing  import Iterator, List, NamedTuple, Tuple, Union

Keys       = Union[int, str]
JsonValues = Union[bool, dict, float, int, list, None, str]
Address    = Tuple[Keys, ...]
Values     = Union[bool, float, int, None, str]


AddressedValue = NamedTuple('AddressedValue', [('address', Address), ('value', Values)])


# TODO: look into parsers to address other nested data structures based on input file suffix.


def address_json(jsonfile: Union[str, PurePath]) -> Iterator[AddressedValue]:
    """Obtain nesting addresses for JSON values.

    Extract the unique container index addresses (tuple of property names and/or array indicies) for each
    non-iterable JSON values (i.e. object or array).

    Args:
        jsonfile: Path to input json file.

    Yields:
        AddressedValue objectsSet of non-iterable json values with dictionary/list index address tuples.

    """
    with open(Path(jsonfile), 'r') as j:
        j_dict = json.load(j)

    for k, v in j_dict.items():
        for address, value in value_drilldown(k, v):
            yield AddressedValue(address, value)


def value_drilldown(key_address: Union[Keys, List[Keys]], value: JsonValues) \
        -> Iterator[Tuple[Address, Values]]:
    """Recursively drill down into input values, append key lists, until json non-iterable is found.

    Args:
        key_address: str, int, or list of those that
        value:       json property value or array element

    Returns:
        Tuple of json property names and/or array indices, along with json non-iterable value.

    """
    if isinstance(key_address, (int, str)):
        key_address = [key_address]
    if isinstance(value, (bool, float, int, str, type(None))):
        new_key = tuple(key_address)
        yield new_key, value
    elif isinstance(value, list):
        for cnt, sub_value in enumerate(value):
            sub_address = key_address + [cnt]
            yield from value_drilldown(sub_address, sub_value)
    elif isinstance(value, dict):
        for key, sub_value in value.items():
            sub_address = key_address + [key]
            yield from value_drilldown(sub_address, sub_value)


if __name__ == '__main__':
    user_input = sys.argv[1]
    for x in address_json(user_input):
        print(x[:])

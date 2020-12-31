"""Modue to compare json files."""

from data_toolchest.nested_data.address_nested_data import address_json, Address, AddressedValue, Keys, Values

import sys

from pathlib     import Path, PurePath
from typing      import Generic, Iterable, Iterator, Set, Tuple, TypeVar, Union

__all__ = ['AddressedValueSet']


AddressSet = Set[AddressedValue]

AVS = TypeVar('AVS', bound='AddressedValueSet')

AVS_Input_Arg = Union['AddressedValueSet', AddressSet, Path, str]


class AddressedValueSet(Generic[AVS]):
    """Generic class for a set of addressed values from nested data structure(s).

    addressed_values: Set of AddressedValue objects with address tuple of key strings or array indices, and the data value.

    """
    def __init__(self, *args: AVS_Input_Arg) -> None:
        """Ensure input data is a list of paths, and generate set of uniquely addressed values if not input."""
        self.addressed_values: AddressSet = set()
        if args:
            # if len(args)
            self.addressed_values = self._addressedvalueset_logic(args, 'union').addressed_values

    def __iter__(self) -> Iterator[Tuple[Address, Values]]:
        """Handle calls to iterate on this object.  Yields from self.addressed_values."""
        for adv in self.addressed_values:
            yield adv.address, adv.value

    def __str__(self) -> str:
        """Provide string representation of object's addressed_values."""
        adv_list = ',\n'.join([str(adv[:]) for adv in sorted(self.addressed_values)])
        return f'{{{adv_list}}}'

    def _addressedvalueset_logic(self, dataset: Iterable[AVS_Input_Arg], set_operation: str) -> 'AddressedValueSet':
        """Perform basic set operations self.addressed_values set with input dataset addressed_values sets."""
        new_addressed_datasets: list = list(self.get_addressedvalue_sets(dataset))
        addressed_values = set()
        if set_operation == 'union':
            addressed_values = self.addressed_values.union(*new_addressed_datasets)
        elif set_operation == 'intersection':
            addressed_values = self.addressed_values.intersection(*new_addressed_datasets)
        elif set_operation == 'difference':
            addressed_values = self.addressed_values.difference(*new_addressed_datasets)
        elif set_operation == 'symmetric_difference':
            union_addressed_values = self.addressed_values.union(*new_addressed_datasets)
            intersection_addressed_values = self.addressed_values.intersection(*new_addressed_datasets)
            addressed_values = union_addressed_values.difference(intersection_addressed_values)
        new_avs: AddressedValueSet = AddressedValueSet()
        new_avs.addressed_values = addressed_values
        return new_avs
        # return AddressedValueSet(addressed_values)

    @staticmethod
    def get_addressedvalue_sets(input_data: Iterable[AVS_Input_Arg]) -> Iterator[AddressSet]:
        """Convert list of inputs to AddressedValueSet objects.

        Args:
              input_data: List of input nested data structures.  Can be mixed.

        Yields:
             Set of AddressedValue namedtuple objects.

        Raises:
            TypeError is input data is not of specific type.

        """
        if not isinstance(input_data, tuple):
            input_data = tuple(input_data)
        for data in input_data:
            if isinstance(data, (PurePath, str)):
                # TODO: look into parsers to address other nested data structures based on input file suffix.
                yield set(address_json(data))
            elif isinstance(data, AddressedValueSet):
                yield data.addressed_values
            elif isinstance(data, set) and all(isinstance(d, AddressedValue) for d in data):
                yield data
            else:
                raise TypeError

    def addresses(self) -> Set[Address]:
        """Find the set of unique addresses in the addressed_value set. Like addresses with different values will be combined.

        Returns:
            Set of unique addresses.

        """
        return {nt.address for nt in self.addressed_values}

    def union(self, *args: AVS_Input_Arg) -> 'AddressedValueSet':
        """Produce the union of object addressedvalues set and input datasets. Like addresses with different values will be maintained."""
        return self._addressedvalueset_logic(args, 'union')

    def intersection(self, *args: AVS_Input_Arg) -> 'AddressedValueSet':
        """Produce the intersection of object addressedvalues set and input datasets. Like addresses with different values will be maintained."""
        return self._addressedvalueset_logic(args, 'intersection')

    def difference(self, *args: AVS_Input_Arg) -> 'AddressedValueSet':
        """Produce the difference of object addressedvalues set and input datasets. Like addresses with different values will be maintained."""
        return self._addressedvalueset_logic(args, 'difference')

    def symmetric_difference(self, *args: AVS_Input_Arg) -> 'AddressedValueSet':
        """Produce the symmetric difference of unique addressed values."""
        return self._addressedvalueset_logic(args, 'symmetric_difference')

    def find_address_with_key(self, key: Keys) -> Iterator[Tuple[Address, Values]]:
        """Find any addressed_values that contain the input key."""
        for address, value in self:
            if key in address:
                yield address, value

    def find_value(self, result: Values) -> Iterator[Tuple[Address, Values]]:
        """Find any addressed_values that contain the input key."""
        result_type = type(result)
        for address, value in self:
            if type(value) != result_type:
                continue
            elif value == result:
                yield address, value


if __name__ == '__main__':
    user_input = sys.argv[1]
    for x in address_json(user_input):
        print(x[:])
    # ex1 = '../../tests/data/input/example_1.json'
    # ex2 = '../../tests/data/input/example_2.json'
    # ex3 = '../../tests/data/input/example_3.json'

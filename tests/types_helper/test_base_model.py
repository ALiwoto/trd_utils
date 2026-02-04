# import pytest
from decimal import Decimal
from trd_utils.types_helper import (
    base_model,
    BaseModel,
    ignore_json_fields,
)

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

@ignore_json_fields(
    fields=[
        "some_field1",
        "some_field3",
    ],
)
class GroupContainer(BaseModel):
    group_name: str = None
    id: int = None
    created_at: str = None
    something: str = "default value here"

    some_field1: int = 10
    some_field2: int = 20
    some_field3: int = 100

class MultiTypeHint(BaseModel):
    cool_field1: Decimal | None = None

class MyData(BaseModel):
    groups: dict[str, GroupContainer] = None
    some_lists: list[list[list[str]]] = None
    main_group: GroupContainer = None
    some_none_value: list = None

def test_multi_type_hints():
    pos = MultiTypeHint()
    pos.cool_field1 = 1000

    result = pos.serialize()
    assert result.find("cool_field") != -1

    my_pos = MultiTypeHint.deserialize(result)

    assert my_pos.cool_field1 == pos.cool_field1

def test_my_data1():
    data = MyData()
    data.groups = {
        "a": GroupContainer(group_name="hallo1"),
        "b": GroupContainer(group_name="hallo2"),
    }
    data.some_lists = []
    data.some_lists.append([["a", "b", "c"], ["d", "e", "f"]])
    data.main_group = GroupContainer(
        group_name="main",
        id=10,
        created_at=1234,
        something=None,
        some_field3=200, # this should get ignored
    )

    result = data.serialize(omit_none=False)
    print(result)

    assert result.find("some_field1") == -1

    my_data = MyData.deserialize(result)
    print(my_data.groups)

    assert my_data is not None
    assert my_data.main_group.some_field2 == 20
    assert my_data.main_group.some_field3 == 100
    assert my_data.main_group.something is None
    assert my_data.some_lists[0][0][0] == "a"

def test_omit_none_data1():
    data = MyData()
    data.groups = {
        "a": GroupContainer(group_name="hallo1"),
        "b": GroupContainer(group_name="hallo2"),
    }
    data.some_lists = []
    data.some_lists.append([["a", "b", "c"], ["d", "e", "f"]])
    data.main_group = GroupContainer(
        group_name="main",
        id=10,
        created_at=1234,
        something=None,
    )

    result = data.serialize(omit_none=True)
    assert result.find("some_none_value") == -1

    my_data = MyData.deserialize(result)
    print(my_data.groups)

    assert my_data is not None
    assert my_data.some_lists[0][0][0] == "a"
    assert my_data.some_none_value is None

class BuildingInfo:
    name: str = None
    level: int = None

    def __init__(self, original_values: list):
        self.name = original_values[0]
        self.level = original_values[1]
    
    def to_json_obj(self):
        return [self.name, self.level]

class Buildings(BaseModel):
    buildings: list[BuildingInfo] = None

def test_list_as_obj1():
    data = Buildings()
    data.buildings = [
        BuildingInfo(["building1", 1]),
        BuildingInfo(["building2", 10]),
        BuildingInfo(["building3", 7]),
    ]

    result = data.serialize()
    assert result

    my_data = Buildings.deserialize(result)
    assert my_data.buildings[0].name == "building1"
    assert my_data.buildings[0].level == 1
    assert my_data.buildings[1].name == "building2"
    assert my_data.buildings[1].level == 10
    


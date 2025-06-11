# import pytest
from trd_utils.types_helper import (
    base_model,
    BaseModel,
)

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

class GroupContainer(BaseModel):
    group_name: str = None
    id: int = None
    created_at: str = None
    something: str = "default value here"

class MyData(BaseModel):
    groups: dict[str, GroupContainer] = None
    some_lists: list[list[list[str]]] = None
    main_group: GroupContainer = None


def test_bx_get_earning_amounts():
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

    result = data.serialize()
    print(result)

    my_data = MyData.deserialize(result)
    print(my_data.groups)

    assert my_data is not None
    assert my_data.main_group.something is None
    assert my_data.some_lists[0][0][0] == "a"

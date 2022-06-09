
import json
import uuid
from dataclasses import dataclass
from typing import Optional, Union, List
from random import randint

from faker import Faker

MAX_INTEGER = 2147483647

faker = Faker(["ru_RU"])

units = [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66a444",
      "name": "Оффер",
      "parentId": None,
      "price": 234,
      "type": "OFFER"
    },

]


@dataclass
class Unit:
    id: uuid.UUID
    name: str
    parent_id: Optional[uuid.UUID]
    price: Optional[int]
    type: str


@dataclass
class Offer(Unit):
    price: int
    type: str = "OFFER"


@dataclass
class Category(Unit):
    price = None
    type: str = "CATEGORY"


class Node:
    def __init__(self, data: Union[Category, Offer]):
        self.data = data
        self.children: List["Node"] = []

    def add_child(self, node: "Node"):
        self.children.append(node)




class Tree:
    def __init__(self, root: Category):
        self.root = root
        self.children = []
        self.nodes = []



def generate_offer(parent_id: Optional[uuid.UUID] = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": faker.name(),
        "parentId": parent_id,
        "price": randint(1, MAX_INTEGER),
        "type": "OFFER",
    }


def generate_category(parent_id: Optional[uuid.UUID] = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": faker.name(),
        "parentId": parent_id,
        "price": None,
        "type": "CATEGORY",
#        "children": [],
    }


def generate_tree(children_number: int = 0, nesting_level: int = 2):
    root = generate_category()

    parent = root
    for _ in range(nesting_level - 1):
        category = generate_category(parent_id=parent["id"])
        parent["children"].append(category)
        parent = category
        children_number -= 1

    head = root
    for _ in range(nesting_level - 1):
        for _ in range(children_number // (nesting_level)):
            head["children"].append(generate_offer(parent_id=head["id"]))
        head = head["children"][0]

    return root


def get_children(node: dict) -> list:
    l = []
    if node["type"] == "CATEGORY":
        for child in node["children"]:
            if child["type"] == "CATEGORY":
                l.append(child.copy().pop("children"))
                l += get_children(child)
            else:
                l.append(child.copy())
    return l


def flat_list(root: dict) -> list:
    return get_children(root)




# r1 = generate_offer()
# r2 = generate_category()
#
# a1 = generate_offer(parent_id=r2["id"])
# a2 = generate_offer(parent_id=r2["id"])
# a3 = generate_offer(parent_id=r2["id"])
# a4 = generate_category(parent_id=r2["id"])
# a5 = generate_category(parent_id=r2["id"])
#
# b1 = generate_offer(parent_id=a4["id"])
# b2 = generate_offer(parent_id=a4["id"])
# b3 = generate_offer(parent_id=a5["id"])
# b4 = generate_category(parent_id=a5["id"])
#
# c1 = generate_offer(parent_id=b4["id"])
# c2 = generate_offer(parent_id=b4["id"])
# c3 = generate_offer(parent_id=b4["id"])
#
# l = [r1, r2, a1, a2, a3, a4, a5, b1, b2, b3, b4, c1, c2, c3]
#
# print(json.dumps(l))
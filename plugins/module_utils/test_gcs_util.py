from gcs_util import (
    plan,
    Action
)
# test plan 

def test_plan_simple_create():
    assert plan({"attr": "value"}, None) == Action.CREATE

def test_plan_delete():
    assert plan(None, {"attr": "value"}) == Action.DELETE

def test_plan_update():
    assert plan({"attr": "value2"}, 
                    {"attr": "value1"}) == Action.UPDATE
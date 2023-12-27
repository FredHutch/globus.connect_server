from unittest.mock import Mock

from gcs_util import (
    plan,
    Action,
    read_keys
)
# test plan 

def test_plan_simple_create():
    assert plan({"k": "v"}, None) == Action.CREATE

def test_plan_delete():
    assert plan(None, {"k": "v"}) == Action.DELETE

def test_plan_update1():
    assert plan({"k": "v"}, 
                {"k": "v_updated"}) == Action.UPDATE
    
def test_plan_update2():
    assert plan({"k1": "v1", "k2": "v2"}, 
                {"k1": "v3"}) == Action.UPDATE
    
def test_plan_no_change1():
    assert plan({}, {}) == Action.NOTHING

def test_plan_no_change2():
    assert plan({"k": "v"}, {"k": "v"}) == Action.NOTHING

def test_plan_no_change3():
    assert plan(None, None) == Action.NOTHING

def test_plan_no_change4():
    assert plan({"k1": "v1"}, 
                {"k1": "v1", "k2": "v2"}) == Action.NOTHING
    
# test read_keys
# read_keys(keys, module)
    
from collections import defaultdict
    
def test_read_keys_empty():
    module = Mock()
    module.params = defaultdict(lambda: None)
    assert read_keys([], module) == {}

def test_read_keys_one():
    module = Mock()
    module.params = defaultdict(lambda: None)
    module.params["k"] = "v"
    assert read_keys(["k"], module) == {"k": "v"}

def test_read_keys_non_existent():
    module = Mock()
    module.params = defaultdict(lambda: None)
    module.params["k"] = "v"
    assert read_keys(["not_k"], module) == {}

def test_read_keys_subset1():
    module = Mock()
    module.params = defaultdict(lambda: None)
    module.params["k1"] = "v1"
    module.params["k2"] = "v2"
    assert read_keys(["k2"], module) == {"k2": "v2"}

def test_read_keys_subset2():
    module = Mock()
    module.params = defaultdict(lambda: None)
    module.params["k1"] = "v1"
    module.params["k2"] = "v2"
    module.params["k3"] = "v3"
    assert read_keys(["k1","k2","k4"], 
                     module) == {"k1":"v1", "k2": "v2"}
    

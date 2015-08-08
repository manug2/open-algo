import sys

sys.path.append('../../main')
sys.path.append('../../../../fx-oanda')
import unittest

from com.open.algo.utils import *


class TestDynamicLoader(unittest.TestCase):
    def setUp(self):
        pass

    def test_loader_can_load_module(self):
        self.assertNotEquals(DynamicLoader().load("sComponents"), None)

    def test_loader_can_load_module_with_name_value(self):
        my_mod = DynamicLoader().load("sComponents")
        self.assertEquals(my_mod.__dict__["name"], "test components 1")

    def test_loader_can_load_module_from_another_path(self):
        my_mod = DynamicLoader().loadFromPath("../test-resources", "sampleComponents", globals())
        self.assertEquals(my_mod["url"], "www.abc.xyz.com")

    def test_loader_can_load_module_from_another_path_with_var(self):
        globals()["WELCOME_MESSAGE"] = "123"
        my_mod = DynamicLoader().loadFromPath("../test-resources", "sampleComponentsVar", globals())
        self.assertEquals(my_mod["msg"], "Received : 123")


class TestTime(unittest.TestCase):
    def setUp(self):
        pass

    def test_should_give_time_zone(self):
        print(get_time())
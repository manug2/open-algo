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

    def test_should_give_time_by_adding_offset(self):
        t1 = get_time()
        t2 = get_time(1)
        age = get_age_seconds(t2, t1)
        self.assertAlmostEqual(1.0, age)

    def test_should_give_time_by_adding_offset_to_another_time(self):
        t1 = get_time()
        print(t1)
        #spend some time
        b = 0
        for i in range(1, 1000000):
            b += 1
        print(get_time())
        t2 = get_time(1, t1)
        print(t2)
        age = get_age_seconds(t2, t1)
        self.assertAlmostEqual(1.0, age)

    def test_should_add_1s_to_time(self):
        t1 = get_time_with_zero_millis()
        t2 = add_time(t1, 1.0)
        age = get_age_seconds(t2, t1)
        self.assertAlmostEqual(1.0, age)

    def test_should_add_seconds_to_time(self):
        t1 = get_time_with_zero_millis()
        t2 = add_time(t1, 1.5)
        age = get_age_seconds(t2, t1)
        self.assertAlmostEqual(1.5, age)

    def test_should_subtract_1s_from_time(self):
        t1 = get_time_with_zero_millis()
        t2 = add_time(t1, -1.0)
        age = get_age_seconds(t2, t1)
        self.assertAlmostEqual(-1.0, age)

    def test_should_subtract_seconds_from_time(self):
        t1 = get_time_with_zero_millis()
        t2 = add_time(t1, -2.0)
        age = get_age_seconds(t2, t1)
        self.assertAlmostEqual(-2.0, age)

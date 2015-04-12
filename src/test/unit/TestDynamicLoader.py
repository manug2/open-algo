import sys

sys.path.append('../../main')
sys.path.append('../../../../fx-oanda')
import unittest

from com.open.algo.utils import DynamicLoader


class TestDynamicLoader(unittest.TestCase):
    def setUp(self):
        pass

    def testLoaderClassExists(self):
        self.assertNotEquals(DynamicLoader, None)

    def testLoaderCanLoadModule(self):
        self.assertNotEquals(DynamicLoader().load("sComponents"), None)

    def testLoaderCanLoadModuleWithNameValue(self):
        myMod = DynamicLoader().load("sComponents")
        self.assertEquals(myMod.__dict__["name"], "test components 1")

    def testLoaderCanLoadModuleFromAnotherPath(self):
        myMod = DynamicLoader().loadFromPath("..", "sampleComponents", globals())
        self.assertEquals(myMod["url"], "www.abc.xyz.com")

    def testLoaderCanLoadModuleFromAnotherPathWithVar(self):
        globals()["WELCOME_MESSAGE"] = "123"
        myMod = DynamicLoader().loadFromPath("..", "sampleComponentsVar", globals())
        self.assertEquals(myMod["msg"], "Received : 123")


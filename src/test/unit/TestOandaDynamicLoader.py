import sys

sys.path.append('../../main')
sys.path.append('../../../../fx-oanda')
import unittest

from com.open.algo.utils import DynamicLoader


class TestOandaDynamicLoader(unittest.TestCase):
    def setUp(self):
        pass

    def testLoaderCanLoadOandaModules(self):
        globals()["STREAM_DOMAIN"] = "www.abc.com"
        globals()["API_DOMAIN"] = "www.abca.com"
        globals()["ACCOUNT_ID"] = "111007"
        globals()["ACCESS_TOKEN"] = "NO TOKEN"
        globals()["INSTRUMENT"] = "INR_INR"
        globals()["UNITS"] = 1000

        myMod = DynamicLoader().loadFromPath("../../../../fx-oanda", "oandaComponents", globals())
        self.assertNotEquals(myMod["prices"], None)
		


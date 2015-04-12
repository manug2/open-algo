import os
import sys

sys.path.append('../../main')
import unittest
from configparser import ConfigParser
import logging

from com.open.algo.trading.fxEvents import OrderEvent
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH
from com.open.algo.oanda.execution import OandaExecutionHandler
from com.open.algo.model import gettime

TARGET_ENV = "practice"


class TestOandaExecution(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        domain = ENVIRONMENTS["api"][TARGET_ENV]
        config = ConfigParser()
        config.read(os.path.join(CONFIG_PATH, "practice.oanda.config"))
        ACCESS_TOKEN = config.get('CONFIG', 'ACCESS_TOKEN')
        ACCOUNT_ID = config.get('CONFIG', 'ACCOUNT_ID')
        self.executor = OandaExecutionHandler(domain, ACCESS_TOKEN, ACCOUNT_ID, logEnabled=True)
        self.logger.info('Using executor : %s' % self.executor)

    def testConnect(self):
        try:
            self.executor.connect()
            self.executor.stop()
        except:
            self.fail("Error connecting to Oanda ")

    def testOrderBuy(self):
        self.executor.connect()
        side = "buy"
        event = OrderEvent("EUR_USD", 125, "market", side)
        response = self.executor.execute_order(event)
        self.executor.stop()
        self.logger.info('Response received : "%s"' % response)
        self.assertNotEqual(None, response)

        hasMessage = 'message' in response
        self.assertEqual(False, hasMessage, 'Unexpected response from broker - : %s' % response)

        self.assertEqual(response['instrument'], 'EUR_USD')
        hasTradeOpened = 'tradeOpened' in response
        self.assertEqual(True, hasTradeOpened, "trade did not open by Oanda")
        trade = response['tradeOpened']
        self.assertEqual(trade['units'], 125)
        self.assertEqual(trade['side'], side)


    def testQueryOrders(self):
        self.executor.connect()
        response = self.executor.get_orders()
        self.executor.stop()
        self.logger.info('Response received : "%s"' % response)
        self.assertNotEqual(None, response)
        hasOrders = 'orders' in response
        self.assertEqual(True, hasOrders, "orders list was NOT returned by Oanda")
        orders = response['orders']
        self.assertNotEqual(None, orders)

    def testQueryOrder(self):
        self.executor.connect()
        response = self.executor.get_order('12300')
        self.executor.stop()
        self.logger.info('Response received : "%s"' % response)
        self.assertNotEqual(None, response)
        self.assertEqual(11, response['code'])
        self.assertEqual('Order not found', response['message'])

    def testBuyLimitAndQueryOrder(self):
        self.executor.connect()
        side = "buy"
        expiry = gettime(100)
        event = OrderEvent("EUR_USD", 1000, side, order_type='limit', price=0.75, expiry=expiry)
        response = self.executor.execute_order(event)
        # self.logger.debug('response on booking : %s' % response)
        self.assertNotEqual(None, response)

        hasMessage = 'message' in response
        self.assertEqual(False, hasMessage, 'Unexpected response from broker - : %s' % response)

        self.assertEqual(response['instrument'], 'EUR_USD')

        hasOrderOpened = 'orderOpened' in response
        self.assertEqual(True, hasOrderOpened, "order did not open by Oanda")
        order = response['orderOpened']
        self.assertEqual(order['units'], 1000)
        self.assertEqual(order['side'], side)

        response = self.executor.get_order(order['id'])
        self.executor.stop()
        #self.logger.debug('Response received : "%s"'% response)
        self.assertNotEqual(None, response)
        self.assertEqual(response['id'], order['id'])
        self.assertEqual(response['instrument'], 'EUR_USD')
        self.assertEqual(response['type'], 'limit')
        self.assertEqual(response['price'], 0.75)
        self.assertEqual(response['units'], 1000)
        self.assertEqual(response['side'], side)
        self.assertEqual(response['expiry'], expiry)


if __name__ == "__main__":
    unittest.main()

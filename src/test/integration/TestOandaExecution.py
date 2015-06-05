import sys
sys.path.append('../../main')

import unittest

from com.open.algo.utils import read_settings, get_time_with_zero_millis
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_UNIT_TESTS
from com.open.algo.journal import Journaler
from com.open.algo.trading.fxEvents import OrderEvent, ExecutedOrder
from com.open.algo.oanda.execution import OandaExecutionHandler

TARGET_ENV = "practice"


class TestOandaExecution(unittest.TestCase):
    def setUp(self):
        domain = ENVIRONMENTS['api'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)
        self.executor = OandaExecutionHandler(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], Journaler())

    def testConnect(self):
        try:
            self.executor.connect()
            self.executor.stop()
        except:
            self.fail("Error connecting to Oanda ")

    def testOrderBuy_EUR_USD(self):
        self.executor.connect()
        side = "buy"
        event = OrderEvent("EUR_USD", 125, side)
        response = self.executor.execute_order(event)
        self.executor.stop()
        self.assertNotEqual(None, response)

        hasMessage = 'message' in response
        self.assertEqual(False, hasMessage, 'Unexpected response from broker - : %s' % response)

        self.assertEqual(response['instrument'], event.instrument)
        hasTradeOpened = 'tradeOpened' in response
        self.assertEqual(True, hasTradeOpened, "trade did not open by Oanda")
        trade = response['tradeOpened']
        self.assertEqual(trade['units'], 125)
        self.assertEqual(trade['side'], side)

    def testOrderBuy_USD_CHF(self):
        self.executor.connect()
        side = "buy"
        event = OrderEvent("USD_CHF", 125, side)
        response = self.executor.execute_order(event)
        self.executor.stop()
        self.assertNotEqual(None, response)

        hasMessage = 'message' in response
        self.assertEqual(False, hasMessage, 'Unexpected response from broker - : %s' % response)

        self.assertEqual(response['instrument'], event.instrument)
        hasTradeOpened = 'tradeOpened' in response
        self.assertEqual(True, hasTradeOpened, "trade did not open by Oanda")
        trade = response['tradeOpened']
        self.assertEqual(trade['units'], 125)
        self.assertEqual(trade['side'], side)

    def testQueryOrders(self):
        self.executor.connect()
        response = self.executor.get_orders()
        self.executor.stop()
        self.assertNotEqual(None, response)
        hasOrders = 'orders' in response
        self.assertEqual(True, hasOrders, "orders list was NOT returned by Oanda")
        orders = response['orders']
        self.assertNotEqual(None, orders)

    def testQueryOrder(self):
        self.executor.connect()
        response = self.executor.get_order('12300')
        self.executor.stop()
        self.assertNotEqual(None, response)
        self.assertEqual(11, response['code'])
        self.assertEqual('Order not found', response['message'])

    def testBuyLimitAndQueryOrder(self):
        self.executor.connect()
        side = "buy"
        expiry = get_time_with_zero_millis(100)
        event = OrderEvent("EUR_USD", 1000, side, order_type='limit', price=0.75, expiry=expiry)
        response = self.executor.execute_order(event)
        self.assertNotEqual(None, response)

        hasMessage = 'message' in response
        self.assertEqual(False, hasMessage, 'Unexpected response from broker - : %s' % response)

        self.assertEqual(response['instrument'], 'EUR_USD')

        hasOrderOpened = 'orderOpened' in response
        self.assertEqual(True, hasOrderOpened, "order did not open by Oanda")
        order = response['orderOpened']
        self.assertEqual(order['units'], 1000)
        self.assertEqual(order['side'], side)
        self.assertEqual(order['expiry'], expiry)

        response = self.executor.get_order(order['id'])
        self.executor.stop()
        self.assertNotEqual(None, response)
        self.assertEqual(response['id'], order['id'])
        self.assertEqual(response['instrument'], 'EUR_USD')
        self.assertEqual(response['type'], 'limit')
        self.assertEqual(response['price'], 0.75)
        self.assertEqual(response['units'], 1000)
        self.assertEqual(response['side'], side)
        self.assertEqual(response['expiry'], expiry)

    def test_should_execute_and_parse_buy_order_USD_CHF(self):
        self.executor.connect()
        side = "buy"
        event = OrderEvent("USD_CHF", 125, side)
        executed_order = self.executor.execute_order_and_parse_response(event)
        self.executor.stop()
        self.assertIsNotNone(executed_order)
        self.assertIsInstance(executed_order, ExecutedOrder
              , 'expecting an executed order of type [%s] but got of type [%s] - %s'
                % (type(ExecutedOrder), type(executed_order), executed_order))
        self.assertEqual(event, executed_order.order)

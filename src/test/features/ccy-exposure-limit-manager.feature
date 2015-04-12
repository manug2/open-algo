Feature: Risk Manager is available to pre check orders based on currency exposures

    Scenario: There is a RiskManager to evaluate currency exposure
        Given we want to trade
         then we use RiskManager to evaluate currency exposure

    Scenario: Currency exposuse calculator does not filter order
        Given we have ccy exposure manager with base currency SGD, default ccy limit
          and we want to buy 100 units of CHF_USD at market rate
          and there is no specific exposure limit for currencies CHF and USD
          and market rate to buy CHF is 1.1 units of base ccy
          and market rate to sell USD is 1.4 units of base ccy
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=CHF_USD, side=buy, order_type=market
          and filtered order has numerical units=100

    Scenario: Currency exposuse calculator filters large order
        Given we have ccy exposure manager with base currency SGD, default ccy limit
          and we want to buy 12345000 units of CHF_USD at market rate
          and there is no specific exposure limit for currencies CHF and USD
          and market rate to buy CHF is 1.0 units of base ccy
          and market rate to sell USD is 1.4 units of base ccy
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=CHF_USD, side=buy, order_type=market
          and filtered order has numerical units=5000

    Scenario Outline: Currency exposuse calculator filters orders
        Given we have ccy exposure manager with base currency <base ccy>, default ccy limit
          and we want to <side> <units> units of <ccy1>_<ccy2> at market rate
          and there is no specific exposure limit for currencies <ccy1> and <ccy1>
          and market rate for <ccy1> is <ccy1Bid>/<ccy1Ask> wrt <base ccy>
          and market rate for <ccy2> is <ccy2Bid>/<ccy2Ask> wrt <base ccy>
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=<ccy1>_<ccy2>, side=buy, order_type=market
          and filtered order has numerical units=<target units>
        Examples:
            | base ccy | side | ccy1 | ccy2 | units | ccy1Bid | ccy1Ask | ccy2Bid | ccy2Ask | order type | target units |
            | SGD      | buy  | CHF  | USD  | 12345 | 0.9     | 1.0     | 1.3     | 1.4     | market     | 5000         |
            | SGD      | buy  | CHF  | USD  | 12345 | 0.9     | 1.1     | 1.3     | 1.4     | market     | 5500         |
            | SGD      | buy  | CHF  | USD  | 12345 | 0.9     | 1.2     | 1.3     | 1.4     | market     | 6000         |
            | SGD      | buy  | CHF  | USD  | 1234  | 0.9     | 1.0     | 1.3     | 1.4     | market     | 1234         |




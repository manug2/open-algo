Feature: Risk Manager is available to pre check orders based on first currency exposure

    Scenario: There is a RiskManager to evaluate currency exposure
        Given we want to trade
         then we use RiskManager to evaluate currency exposure

    Scenario: Currency exposure calculator does not filter order
        Given we have ccy exposure manager with base currency SGD, default ccy limit
          and we want to buy 100 units of CHF_USD
          and there is no specific exposure limit for currencies CHF and USD
          and market rate to buy CHF is 1.1 units of base ccy
          and market rate to sell USD is 1.4 units of base ccy
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=CHF_USD, side=buy, order_type=market
          and filtered order has numerical units=100

    Scenario: Currency exposure calculator filters large order
        Given we have ccy exposure manager with base currency SGD, default ccy limit
          and we want to buy 12345000 units of CHF_USD
          and there is no specific exposure limit for currencies CHF and USD
          and market rate to buy CHF is 1.0 units of base ccy
          and market rate to sell USD is 1.4 units of base ccy
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=CHF_USD, side=buy, order_type=market
          and filtered order has numerical units=5000

    Scenario Outline: Currency exposure calculator filters orders
        Given we have ccy exposure manager with base currency <base ccy>, default ccy limit
          and we want to <side> <units> units of <ccy1>_<ccy2>
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


    Scenario Outline: Currency exposure calculator filters orders using specific limits, with unit fx rates
        Given we have ccy exposure manager with base currency <base ccy>, default ccy limit of <def limit>
          and we want to <side> <units> units of <ccy1>_<ccy2>
          and the specific exposure limit for currency <ccy1> is <ccy1 limit>
          and market rate for <ccy1> is 1.0/1.0 wrt <base ccy>
          and market rate for <ccy2> is 1.0/1.0 wrt <base ccy>
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=<ccy1>_<ccy2>, side=buy, order_type=market
          and filtered order has numerical units=<target units>
        Examples: with unit fx rates
            | base ccy | side | ccy1 | ccy2 | def limit | ccy1 limit | units | order type | target units | NOTES                  |
            | SGD      | buy  | CHF  | USD  | 10000     | 12000      | 15000 | market     | 12000        | default < spec < trade |
            | SGD      | buy  | CHF  | USD  | 10000     | 15000      | 12000 | market     | 12000        | default < trade < spec |
            | SGD      | buy  | CHF  | USD  | 10000     |  2000      | 15000 | market     |  2000        | spec < default < trade |
            | SGD      | buy  | CHF  | USD  | 10000     |  1000      |  2000 | market     |  1000        | spec < trade < default |
            | SGD      | buy  | CHF  | USD  | 10000     |  8000      |  1000 | market     |  1000        | trade < default < spec |
            | SGD      | buy  | CHF  | USD  | 10000     |  1000      |   100 | market     |   100        | trade < spec < default |

    Scenario Outline: Currency exposure calculator filters orders using specific limits, with some fx rates above 1
        Given we have ccy exposure manager with base currency <base ccy>, default ccy limit of <def limit>
          and we want to <side> <units> units of <ccy1>_<ccy2>
          and the specific exposure limit for currency <ccy1> is <ccy1 limit>
          and market rate for <ccy1> is <ccy1Bid>/<ccy1Ask> wrt <base ccy>
          and market rate for <ccy2> is <ccy2Bid>/<ccy2Ask> wrt <base ccy>
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=<ccy1>_<ccy2>, side=buy, order_type=market
          and filtered order has numerical units=<target units>
        Examples: with some fx rates
            | base ccy | side | ccy1 | ccy2 | def limit | ccy1 limit | units | ccy1Bid | ccy1Ask | ccy2Bid | ccy2Ask | order type | target units | NOTES                      |
            | SGD      | buy  | CHF  | USD  | 10000     | 12000      | 15000 | 1.05    | 1.1     | 1.3     | 1.4     | market     | 13200        | default < spec < trade*ask |
            | SGD      | buy  | CHF  | USD  | 10000     | 12000      | 15000 | 1.05    | 1.1     | 1.3     | 1.4     | market     | 13200        | default < trade*ask < spec |
            | SGD      | buy  | CHF  | USD  | 10000     | 1000       | 2000  | 1.05    | 1.1     | 1.3     | 1.4     | market     | 1100         | spec < trade*ask < default |
            | SGD      | buy  | CHF  | USD  | 10000     | 2000       | 15000 | 1.05    | 1.1     | 1.3     | 1.4     | market     | 2200         | spec < default < trade*ask |
            | SGD      | buy  | CHF  | USD  | 10000     | 8000       | 1000  | 1.05    | 1.1     | 1.3     | 1.4     | market     | 1000         | trade*ask < default < spec |
            | SGD      | buy  | CHF  | USD  | 10000     | 1000       | 100   | 1.05    | 1.1     | 1.3     | 1.4     | market     |  100         | trade*ask < spec < default |
            | SGD      | buy  | CHF  | USD  | 10000     |  110       | 100   | 1.05    | 1.1     | 1.3     | 1.4     | market     |  100         | trade*ask = spec < default |




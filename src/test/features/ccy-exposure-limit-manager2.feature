Feature: Risk Manager is available to pre check orders based on second currency exposure

    Scenario: Currency exposure calculator does not filter order
        Given we have ccy exposure manager with base currency SGD, default ccy short limit
          and we want to buy 100 units of CHF_USD
          and the specific exposure limit for currency CHF is 100000
          and there is no specific short exposure limit for currency USD
          and market rate to buy CHF is 1.05 units of base ccy
          and market rate to sell USD is 1.1 units of base ccy
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=CHF_USD and side=buy
          and filtered order has numerical units=100

    Scenario: Currency exposure calculator filters large order because of 2nd ccy
        Given we have ccy exposure manager with base currency SGD, default ccy short limit
          and we want to buy 12345000 units of CHF_USD
          and the specific exposure limit for currency CHF is 100000
          and there is no specific short exposure limit for currency USD
          and market rate to buy CHF is 1.05 units of base ccy
          and market rate to sell USD is 1.1 units of base ccy
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=CHF_USD and side=buy
          and filtered order has numerical units=5000

    Scenario Outline: Currency exposure calculator filters orders using 2nd ccy
        Given we have ccy exposure manager with base currency <base ccy>, default ccy short limit
          and we want to <side> <units> units of <ccy1>_<ccy2>
          and the specific exposure limit for currency <ccy1> is 100000
          and there is no specific short exposure limit for currency <ccy2>
          and market rate for <ccy1> is <ccy1Bid>/<ccy1Ask> wrt <base ccy>
          and market rate for <ccy2> is <ccy2Bid>/<ccy2Ask> wrt <base ccy>
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=<ccy1>_<ccy2> and side=buy
          and filtered order has numerical units=<target units>
        Examples:
            | base ccy | side | ccy1 | ccy2 | units | ccy1Bid | ccy1Ask | ccy2Bid | ccy2Ask | target units |
            | SGD      | buy  | CHF  | USD  | 12345 | 0.9     | 1.0     | 1.05    | 1.1     | 5000         |
            | SGD      | buy  | CHF  | USD  | 12345 | 0.9     | 1.1     | 1.05    | 1.1     | 5500         |
            | SGD      | buy  | CHF  | USD  | 12345 | 0.9     | 1.2     | 1.05    | 1.1     | 6000         |
            | SGD      | buy  | CHF  | USD  | 1234  | 0.9     | 1.0     | 1.05    | 1.1     | 1234         |


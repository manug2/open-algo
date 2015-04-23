Feature: Risk Manager is available to pre check orders based on second currency exposure

    Scenario: Currency exposure manager does not filter order
        Given we have ccy exposure manager with base currency SGD, default ccy short limit
          and we want to buy 100 units of CHF_USD
          and the specific exposure limit for currency CHF is 100000
          and there is no specific short exposure limit for currency USD
          and market rate for CHF is 1.1/1.15 wrt SGD
          and market rate for USD is 1.3/1.4 wrt SGD
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=CHF_USD and side=buy
          and filtered order has numerical units=100

    Scenario: Currency exposure manager filters large order because of 2nd ccy (=5000/1.3)
        Given we have ccy exposure manager with base currency SGD, default ccy short limit
          and we want to buy 12345000 units of CHF_USD
          and the specific exposure limit for currency CHF is 100000
          and there is no specific short exposure limit for currency USD
          and market rate for CHF is 0.99/1.0 wrt SGD
          and market rate for USD is 1.3/1.4 wrt SGD
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=CHF_USD and side=buy
          and filtered order has numerical units=3846

    Scenario Outline: Currency exposure manager filters orders using 2nd ccy
        Given we have ccy exposure manager with base currency <base ccy>, default ccy short limit
          and we want to <side> <units> units of <ccy1>_<ccy2>
          and the specific exposure limit for currency <ccy1> is 100000
          and there is no specific short exposure limit for currency <ccy2>
          and market rate for <ccy1> is <ccy1Bid>/<ccy1Ask> wrt <base ccy>
          and market rate for <ccy2> is <ccy2Bid>/<ccy2Ask> wrt <base ccy>
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=<ccy1>_<ccy2> and side=<side>
          and filtered order has numerical units=<target units>
        Examples:
            | base ccy | side | ccy1 | ccy2 | units | ccy1Bid | ccy1Ask | ccy2Bid | ccy2Ask | target units | NOTES                   |
            | SGD      | buy  | CHF  | USD  | 12345 | 0.9     | 1.0     | 1.05    | 1.1     | 4762         | def short / ccy2Bid     |
            | SGD      | sell | CHF  | USD  | 12345 | 1.0     | 1.0     | 1.05    | 1.15    | 4348         | min(def short / ccy2Ask, def limit / ccy1Bid)|
            | SGD      | buy  | EUR  | USD  | 12345 | 0.9     | 1.0     | 1.05    | 1.1     | 4762         | def short / ccy2Bid     |
            | SGD      | sell | EUR  | USD  | 12345 | 1.7     | 1.8     | 1.05    | 1.15    | 2941         | min(def short / ccy2Ask, def limit / ccy1Bid)|
            | SGD      | buy  | CHF  | USD  | 12345 | 0.95    | 1.1     | 1.1     | 1.2     | 4545         | def short / ccy2Bid     |
            | SGD      | buy  | CHF  | USD  | 12345 | 0.96    | 1.2     | 1.05    | 1.2     | 4762         | def short / ccy2Bid     |
            | SGD      | buy  | CHF  | USD  | 1234  | 0.97    | 1.0     | 1.05    | 1.1     | 1234         | trade < def short limit |


    Scenario Outline: Currency exposure manager filters orders using specific limits on 2nd currency, with unit fx rates
        Given we have ccy exposure manager, base currency <base ccy>, large default limit, default short ccy limit of <short limit>
          and we want to <side> <units> units of <ccy1>_<ccy2>
          and the specific short limit for currency <ccy2> is <ccy2 s. limit>
          and market rate for <ccy1> is 1.0/1.0 wrt <base ccy>
          and market rate for <ccy2> is 1.0/1.0 wrt <base ccy>
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=<ccy1>_<ccy2> and side=<side>
          and filtered order has numerical units=<target units>
        Examples: with unit fx rates
            | base ccy | side | ccy1 | ccy2 |short limit|ccy2 s. limit| units | target units | NOTES                  |
            | SGD      | buy  | CHF  | USD  | 10000     | 12000       | 15000 | 12000        | short < spec < trade   |
            | SGD      | sell | CHF  | USD  | 10000     | 12000       | 15000 | 10000        | CHF short = default short < trade   |
            | SGD      | buy  | CHF  | USD  | 10000     | 15000       | 12000 | 12000        | short < trade < spec   |
            | SGD      | buy  | CHF  | USD  | 10000     |  2000       | 15000 |  2000        | spec < short < trade   |
            | SGD      | buy  | CHF  | USD  | 10000     |  1000       |  2000 |  1000        | spec < trade < short   |
            | SGD      | buy  | CHF  | USD  | 10000     |  8000       |  1000 |  1000        | trade < short < spec   |
            | SGD      | buy  | CHF  | USD  | 10000     |  1000       |   100 |   100        | trade < spec < short   |
            | SGD      | buy  | CHF  | USD  | 10000     |  1000       |  1000 |  1000        | trade = spec < short   |
            | SGD      | buy  | CHF  | USD  | 10000     |   999       |  1000 |   999        | trade=spec-1 < short   |
            | SGD      | buy  | CHF  | USD  | 10000     |  1001       |  1000 |  1000        | trade=spec+1 < short   |


    Scenario Outline: Currency exposure manager filters orders using specific limits on 2nd currency, with some fx rates not equal to 1
        Given we have ccy exposure manager, base currency <base ccy>, large default limit, default short ccy limit of <short limit>
          and we want to <side> <units> units of <ccy1>_<ccy2>
          and the specific short limit for currency <ccy2> is <ccy2 s. limit>
          and market rate for <ccy1> is <ccy1Bid>/<ccy1Ask> wrt <base ccy>
          and market rate for <ccy2> is <ccy2Bid>/<ccy2Ask> wrt <base ccy>
         when when i say filter order
          then RiskManager returns filtered order
          and filtered order has instrument=<ccy1>_<ccy2> and side=<side>
          and filtered order has numerical units=<target units>
        Examples: with some fx rates
            | base ccy | side | ccy1 | ccy2 |short limit|ccy2 s. limit| units | ccy1Bid | ccy1Ask | ccy2Bid | ccy2Ask | target units | NOTES                                 |
            | SGD      | buy  | CHF  | USD  | 10000     | 12000       | 15000 | 1.05    | 1.1     | 1.2     | 1.3     | 10000        | short limit / ccy2Bid    |
            | SGD      | buy  | CHF  | USD  | 10000     | 12000       | 15000 | 0.95    | 0.98    | 1.3     | 1.4     |  9231        | default < spec < trade*ccy2ask, ccy1ask < 1 |
            | SGD      | buy  | CHF  | USD  | 10000     | 12000       | 15000 | 1.05    | 1.1     | 0.9     | 0.95    | 13333        | default < trade*ccy2ask < spec, ccy2ask>1   |


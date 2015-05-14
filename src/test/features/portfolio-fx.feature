Feature: trading system a has portfolio management module

  Background:
    Given rates queue is initialized
      and market rate cache is initialized

    Scenario: Portfolio Manager with two executed orders appended yields one position
        Given Portfolio Manager is initialized
          and a new executed order is available
          and executed order is appended to Portfolio Manager
          and a new executed order is available
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with number of items = 1


    Scenario: Portfolio Manager with two executed orders appended yields two executions
        Given Portfolio Manager is initialized
          and a new executed order is available
          and executed order is appended to Portfolio Manager
          and a new executed order is available
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields executions list with number of items = 2


    Scenario: Portfolio Manager with an executed order appended yields correct position
        Given Portfolio Manager is initialized
          and a new executed order is available to buy 40 CHF_USD units
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with units = 40


    Scenario: Portfolio Manager with two executed orders appended yields net position
        Given Portfolio Manager is initialized
          and a new executed order is available to buy 30 CHF_USD units
          and executed order is appended to Portfolio Manager
          and a new executed order is available to sell 10 CHF_USD units
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with units = 20


    Scenario: Portfolio Manager with two executed orders appended yields correct position per instrument
        Given Portfolio Manager is initialized
          and a new executed order is available to buy 40 CHF_USD units
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with CHF_USD units = 40


    Scenario: Portfolio Manager with two executed orders appended yields correct position per instrument
        Given Portfolio Manager is initialized
          and a new executed order is available to buy 40 CHF_USD units
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with CHF_USD units = 40


    Scenario: Portfolio Manager can re-evaluate unrealized profit using latest market price going up
        Given market rate cache is listening to ticks
          and Portfolio Manager is initialized with base currency USD, market rate cache
          and portfolio has an executed order to buy 100 CHF_USD units at 1.04
         when a price tick arrives for CHF_USD 1.05/1.1
          and market rate cache stops
         then Portfolio Manager evaluates CHF_USD PnL = 6


    Scenario: Portfolio Manager can evaluate unrealized loss using latest market price
        Given market rate cache is listening to ticks
          and Portfolio Manager is initialized with base currency USD, market rate cache
          and portfolio has an executed order to buy 100 CHF_USD units at 1.05
         when a price tick arrives for CHF_USD 1.04/1.08
          and market rate cache stops
         then Portfolio Manager evaluates CHF_USD PnL = 3


    Scenario Outline: Portfolio Manager can evaluate unrealized PnL using latest market price
        Given market rate cache is listening to ticks
          and Portfolio Manager is initialized with base currency <base ccy>, market rate cache
          and portfolio has an executed order to <exec side> <exec units> <instrument> units at <exec price>
         when a price tick arrives for <instrument> <bid>/<ask>
          and market rate cache stops
         then Portfolio Manager evaluates <instrument> PnL = <pnl>
        Examples: long or short position, rates up and down
            | base ccy  | exec side | exec units  | instrument  | exec price  | bid | ask | pnl | NOTES
            | USD       | buy       | 100         | CHF_USD     | 1.04        | 1.05| 1.1 |  6  | long, bid/ask goes up, stays above
            | USD       | buy       | 100         | CHF_USD     | 1.05        | 1.04| 1.08|  3  | long, bid goes under, ask stay above
            | USD       | buy       | 100         | CHF_USD     | 1.05        | 1.00| 1.01| -4  | long, bid/ask go under
            | USD       | sell      | 100         | CHF_USD     | 1.05        | 1.08| 1.09| -3  | short, bid/ask goes up, stays above
            | USD       | sell      | 100         | CHF_USD     | 1.05        | 1.01| 1.07|  4  | short, bid goes under, ask stay above
            | USD       | sell      | 100         | CHF_USD     | 1.05        | 1.00| 1.01|  5  | short, bid/ask go under



    Scenario: Portfolio Manager can evaluate unrealized loss for whole portfolio with one position
        Given market rate cache is listening to ticks
          and Portfolio Manager is initialized with base currency USD, market rate cache, ccy exposure manager
          and portfolio has an executed order to buy 100 CHF_USD units at 1.05
         when a price tick arrives for CHF_USD 1.04/1.08
          and market rate cache stops
         then Portfolio's total PnL = -7.41


    Scenario: Portfolio Manager can evaluate unrealized loss for whole portfolio with two long positions
        Given market rate cache is listening to ticks
          and Portfolio Manager is initialized with base currency USD, market rate cache, ccy exposure manager
          and portfolio has an executed order to buy 100 CHF_USD units at 1.05
          and portfolio has an executed order to buy 30 CHF_USD units at 1.07
         when a price tick arrives for CHF_USD 1.2/1.3
          and market rate cache stops
         then Portfolio's total PnL = -30


    Scenario: Portfolio Manager can evaluate unrealized loss for whole portfolio with two long and short positions
        Given market rate cache is listening to ticks
          and Portfolio Manager is initialized with base currency USD, market rate cache, ccy exposure manager
          and portfolio has an executed order to buy 140 CHF_USD units at 1.05
          and portfolio has an executed order to sell 30 CHF_USD units at 1.07
         when a price tick arrives for CHF_USD 1.09/1.10
          and market rate cache stops
         then Portfolio's total PnL = -10


    Scenario Outline: Portfolio Manager can evaluate unrealized loss for whole portfolio with two positions
        Given market rate cache is listening to ticks
          and Portfolio Manager is initialized with base currency <base ccy>, market rate cache, ccy exposure manager
          and portfolio has an executed order to <side1> <units1> <instr1> units at <price1>
          and portfolio has an executed order to <side2> <units2> <instr2> units at <price2>
         when a price tick arrives for <instr1> <bid1>/<ask1>
         when a price tick arrives for <instr2> <bid2>/<ask2>
          and market rate cache stops
         then Portfolio's total PnL = <pnl>
        Examples: two long short position, rates up and down
            | base ccy| side1 | units1 | instr1  | price1 | bid1 | ask1 | side2 | units2 | instr2  | price2 | bid2 | ask2 | pnl    | NOTES
            | USD     | buy   | 100    | CHF_USD | 1.04   | 1.05 | 1.1  | buy   | 100    | CHF_USD | 1.04   | 1.05 | 1.1  | -18.18 | long long same instr
            | USD     | buy   | 100    | CHF_USD | 1.04   | 1.05 | 1.1  | sell  | 100    | CHF_USD | 1.04   | 1.05 | 1.1  | 0      | long short same instr
            | USD     | buy   | 100    | CHF_USD | 1.04   | 1.21 | 1.22 | buy   | 100    | EUR_USD | 0.95   | 0.91 | 0.92 | -9.34  | long long diff instr


    @wip
    Scenario: Portfolio can issue order to close specific position

    @wip
    Scenario: Portfolio can issue order to close all positions

    @wip
    Scenario: Portfolio can be sent message to  order to close specific position

    @wip
    Scenario: Portfolio can be sent message to  order to close all positions





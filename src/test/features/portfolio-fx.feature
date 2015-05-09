Feature: trading system a has portfolio management module

  Background:
    Given rates queue is initialized

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
        Examples: long short position, rates up and down
            | base ccy  | exec side | exec units  | instrument  | exec price  | bid | ask | pnl | NOTES
            | USD       | buy       | 100         | CHF_USD     | 1.04        | 1.05| 1.1 |  6  | long, bid/ask goes up, stays above
            | USD       | buy       | 100         | CHF_USD     | 1.05        | 1.04| 1.08|  3  | long, bid goes under, ask stay above
            | USD       | buy       | 100         | CHF_USD     | 1.05        | 1.00| 1.01| -4  | long, bid/ask go under
            | USD       | sell      | 100         | CHF_USD     | 1.05        | 1.08| 1.09| -3  | short, bid/ask goes up, stays above
            | USD       | sell      | 100         | CHF_USD     | 1.05        | 1.01| 1.07|  4  | short, bid goes under, ask stay above
            | USD       | sell      | 100         | CHF_USD     | 1.05        | 1.00| 1.01|  5  | short, bid/ask go under



    Scenario: Portfolio Manager can evaluate unrealized loss for whole portfolio
        Given market rate cache is listening to ticks
          and Portfolio Manager is initialized with base currency USD, market rate cache
          and portfolio has an executed order to buy 100 CHF_USD units at 1.05
         when a price tick arrives for CHF_USD 1.04/1.08
          and market rate cache stops
         then Portfolio's total PnL = -7.41


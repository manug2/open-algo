Feature: trading system a has portfolio management module


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


    Scenario: Portfolio Manager can re-evaluate unrealized profit using latest market price
        Given Portfolio Manager is initialized with base currency USD, market rate cache
          and portfolio has an executed order to buy 100 CHF_USD units at 1.04
         when a price tick arrives for CHF_USD 1.05/1.1
         then Portfolio Manager evaluates CHF_USD PnL = 1


    Scenario: Portfolio Manager can evaluate unrealized loss using latest market price
        Given Portfolio Manager is initialized with base currency USD, market rate cache
          and portfolio has an executed order to buy 100 CHF_USD units at 1.05
         when a price tick arrives for CHF_USD 1.04/1.1
         then Portfolio Manager evaluates CHF_USD PnL = -1



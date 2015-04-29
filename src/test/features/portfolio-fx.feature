Feature: trading system a has portfolio management module


    Scenario: Portfolio Manager can append two executed orders and yield one position
        Given Portfolio Manager is initialized
          and a new executed order is available
          and executed order is appended to Portfolio Manager
          and a new executed order is available
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with number of items = 1


    Scenario: Portfolio Manager can append two executed orders and yield two executions
        Given Portfolio Manager is initialized
          and a new executed order is available
          and executed order is appended to Portfolio Manager
          and a new executed order is available
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields executions list with number of items = 2


    Scenario: Portfolio Manager can append executed order and yield correct position
        Given Portfolio Manager is initialized
          and a new executed order is available to buy 40 units
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with units = 40


    Scenario: Portfolio Manager can append two executed orders and yield net position
        Given Portfolio Manager is initialized
          and a new executed order is available to buy 30 units
          and executed order is appended to Portfolio Manager
          and a new executed order is available to sell 10 units
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with units = 20




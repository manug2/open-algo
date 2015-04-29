Feature: detail - trading system a has portfolio management module

    Scenario: Portfolio Manager can list positions when no trade is made
        Given Portfolio Manager is initialized
         then Portfolio Manager yields empty position list

    Scenario: Portfolio Manager can append position
        Given Portfolio Manager is initialized
          and a new executed order is available
         then executed order can be appended to Portfolio Manager

    Scenario: Portfolio Manager can append executed order and yield list
        Given Portfolio Manager is initialized
          and a new executed order is available
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields non-empty position list


    Scenario: Portfolio Manager can list executed order when no trade is made
        Given Portfolio Manager is initialized
         then Portfolio Manager yields empty executions list

    Scenario: Portfolio Manager can append executed order and yield list or executions
        Given Portfolio Manager is initialized
          and a new executed order is available
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields non-empty executions list


    Scenario: Portfolio Manager can append two executed orders and yield total position
        Given Portfolio Manager is initialized
          and a new executed order is available to buy 20 units
          and executed order is appended to Portfolio Manager
          and a new executed order is available to buy 30 units
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with units = 50


    Scenario: Portfolio Manager can append two executed orders and yield net negative position
        Given Portfolio Manager is initialized
          and a new executed order is available to buy 30 units
          and executed order is appended to Portfolio Manager
          and a new executed order is available to sell 50 units
          and executed order is appended to Portfolio Manager
         then Portfolio Manager yields positions list with units = -20



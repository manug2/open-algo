Feature: test fx cost predictor module against input events

  Background: rates queue is initialized

    Scenario: cost predictor does not evaluate when no rate is present
        Given Cost Predictor is initialized
         when a new order arrives
         then Cost Predictor gives error

    Scenario: cost predictor captures latest tick when available
        Given Cost Predictor is initialized
         when a new tick arrives
         then Cost Predictor has last event same as arrived tick

    Scenario: cost predictor evaluates based on available tick
        Given Cost Predictor is initialized
         when a new tick arrives
         then Cost Predictor has last spread based on last tick

    Scenario: cost predictor can evaluate based on available specific tick
        Given Cost Predictor is initialized
          and we want to buy 100 units of CHF_USD
         when a price tick arrives for CHF_USD 1.01/1.02
         then Cost Predictor can evaluate cost = 0.01

    Scenario: cost predictor can evaluate based on available ticks
        Given Cost Predictor is initialized
          and we want to buy 100 units of CHF_USD
         when a price tick arrives for CHF_USD 1.01/1.02
          and a price tick arrives for CHF_USD 1.03/1.05
         then Cost Predictor can evaluate cost = 0.015

    Scenario: cost predictor can evaluate based on available ticks for instruments
        Given Cost Predictor is initialized
          and we want to buy 100 units of CHF_USD
         when a price tick arrives for CHF_USD 1.01/1.02
         when a price tick arrives for EUR_USD 1/2
          and a price tick arrives for CHF_USD 1.03/1.05
         then Cost Predictor can evaluate cost = 0.015

    Scenario: cost predictor can evaluate based on available last ticks for specific instrument
        Given Cost Predictor is initialized
          and we want to buy 100 units of EUR_USD
         when a price tick arrives for CHF_USD 1.01/1.02
         when a price tick arrives for EUR_USD 1/2
          and a price tick arrives for CHF_USD 1.03/1.05
         then Cost Predictor can evaluate cost = 1.0
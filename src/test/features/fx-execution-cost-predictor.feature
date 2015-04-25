Feature: test fx cost predictor module against input events

    Scenario: cost predictor does not evaluate when no rate is present
        Given Cost Predictor is initialized
         when a new order arrives
         then Cost Predictor gives assertion error

    Scenario: cost predictor does not evaluate when no rate is present
        Given Cost Predictor is initialized
         when a new tick arrives
         then Cost Predictor has last event same as arrived tick


Feature: test fx cost predictor module against input rate events

    Scenario: cost predictor does not evaluate when no rate is present
        Given we have a cost predictor initialized
         when we input not event
         then cost predictor gives no output


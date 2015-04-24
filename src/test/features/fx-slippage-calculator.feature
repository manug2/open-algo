Feature: test fx slippage calculator module against input events and executions

    Scenario: slippage calculator does not evaluate when no rate is present
        Given we have a slippage calculator initialized
         when we input not event
         then slippage calculator gives no output


Feature: test fx slippage calculator module against input events and executions

    Scenario: slippage calculator does not evaluate when no rate is present
        Given Slippage Calculator is initialized
         when a new tick arrives
         then Slippage Calculator gives no output


Feature: detail - back testing module for testing strategy agains input events

    Scenario: a back tester does not test upon an invalid event
        Given we have a back tester initialized
        when we input an invalid event
        then tester gives no output


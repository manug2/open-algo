Feature: detail - market rate cache scenarios

  Background:
    Given rates queue is initialized
      and market rate cache is initialized

    Scenario: market rate cache can reject old ticks
        Given market rate cache is listening to ticks
          when an old tick arrives for CHF_USD 1.05/1.1
          and market rate cache stops
         then the old tick goes into exception queue



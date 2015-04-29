
Feature: detail - test algo trader using simulated events against expected output signals

    Scenario: algo trader does not generate any output signal when no event is present
        Given we have an event stream
          and we are using a dummy strategy and executor
	  and we have a trading bot
	  and bot is trading
         when no event occured
          and bot trading is stopped
         then trader generates no output

    Scenario: algo trader does not generate any output signal when an invalid input event occurs
        Given we have an event stream
          and we are using a dummy strategy and executor
	  and we have a trading bot
	  and bot is trading
         when we input an invalid event
          and bot trading is stopped
         then trader generates no output

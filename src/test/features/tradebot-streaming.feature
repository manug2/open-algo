Feature: test algo trader using simulated events against expected output signal

    Scenario: algo trader generates an order for execution
        Given we have an event stream
          and we are using a dummy strategy and executor
	  and we have a trading bot
	  and bot is trading
         when we input a price tick event
          and bot trading is stopped
         then bot generates an order



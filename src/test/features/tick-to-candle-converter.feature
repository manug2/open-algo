Feature: Oanda provides historical prices

    @wip
	Scenario: Ticks can be converted to 5 second candles
		Given we are receiving ticks
		 then converter can convert ticks to 5 second candles

    @wip
	Scenario: Ticks can be converted to 1 minute candles
		Given we are receiving ticks
		 then converter can convert ticks to 1 minute candles


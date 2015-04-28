Feature: Oanda provides historical prices

	Scenario: Sample ticks can be received from Oanda if connection is available
		Given we want to stream ticks from Oanda practice
		  and using api connection
		 when i say query prices for EUR_USD
		 then we receive historical ticks for this instrument

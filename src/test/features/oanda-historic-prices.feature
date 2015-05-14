Feature: Oanda provides historical prices

	Scenario: Sample ticks can be received from Oanda if connection is available
		Given we want to stream ticks from Oanda practice
		  and using api connection
		 when i say query prices for EUR_USD
		 then we receive historical ticks for this instrument

	Scenario: Oanda streams candle ticks based on requested frequency
		Given System is connected to Oanda sandbox using streaming connection for EUR_USD prices at interval of S5
		 then Oanda sends candle ticks at interval of S5

    @wip
	Scenario: Oanda streams candle ticks based on requested frequency 2
		Given System is connected to Oanda sandbox using streaming connection for last 50 EUR_USD prices at interval of M1
		 then Oanda sends 50 candle ticks at interval of M1

    @wip
	Scenario: Oanda streams candle ticks based on requested frequency for last some time
		Given System is connected to Oanda sandbox using streaming connection for EUR_USD prices at interval of S5 for last 10 minutes
		 then Oanda sends 50 candle ticks at interval of S5 for last 10 minutes

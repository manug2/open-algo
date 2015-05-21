Feature: Oanda provides historical prices

	Scenario: Sample ticks can be received from Oanda if connection is available
		Given we want to stream ticks from Oanda practice
		  and using api connection
		 when i say query prices for EUR_USD
		 then we receive historical ticks for this instrument

	Scenario: Oanda streams candle ticks based on requested frequency for last some time
		Given System is connected to Oanda sandbox using streaming connection for EUR_USD prices at interval of S5 for last 10 minutes
		 then we receive S5 candles for last 10 minutes

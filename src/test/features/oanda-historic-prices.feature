Feature: Oanda provides historical prices

	Scenario: Sample ticks can be received from Oanda if connection is available
		Given we want to stream ticks from Oanda sandbox
		  and using account_id=1234567, instrument=EUR_USD and token=abcdef0123456abcdef0123456-abcdef0123456abcdef0123456
		  and using api connection
		 when i say query prices for 'CHF_USD'
		 then we receive ticks for this instrument


	Scenario: Sample ticks can be received from Oanda if connection is available and logged by journaler
		Given we want to stream ticks from Oanda sandbox
		  and using account_id=1234567, instrument=EUR_USD and token=abcdef0123456abcdef0123456-abcdef0123456abcdef0123456
		  and using api connection
		 when i say query prices for 'CHF_USD'
		  and last tick was logged by the journaler as last event


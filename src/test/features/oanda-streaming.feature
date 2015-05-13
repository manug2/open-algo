Feature: Oanda provides streaming rates capability

	Scenario: Connection can be established with Oanda
		Given we want to establish connection to Oanda sandbox
		  and using account_id=1234567, instrument=EUR_USD and token=abcdef0123456abcdef0123456-abcdef0123456abcdef0123456
		  and using streaming connection
		 when i say connect
		 then we are able to connect to Oanda
		

	Scenario: Sample ticks can be received from Oanda if connection is available
		Given we want to stream ticks from Oanda sandbox
		  and using account_id=1234567, instrument=EUR_USD and token=abcdef0123456abcdef0123456-abcdef0123456abcdef0123456
		  and using streaming connection
		 when i say stream
		 then we received a tick


	Scenario: Sample ticks can be received from Oanda if connection is available and logged by journaler
		Given System is connected to Oanda sandbox using streaming connection for EUR_USD prices
		 then we received few ticks for this instrument
		  and journaler logs input events

	Scenario: Oanda sends heartbeats
		Given System is connected to Oanda sandbox using streaming connection for EUR_USD prices
		 then Oanda sends heartbeats


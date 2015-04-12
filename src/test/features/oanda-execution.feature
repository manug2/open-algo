Feature: Oanda provides order execution capability via API

	Scenario: Execution connection can be established with Oanda
		Given we want to establish connection to Oanda practice
		  and using api connection
		  and using authorization details from config file from path "../../../fx-oanda/"
		 when Executor connects
		 then system does not get a failure response

	Scenario: Execution order can be issued to Oanda
		Given Executor is setup to connect to Oanda practice using api connection
		  and we want to buy 125 units of EUR_USD
		 when i say execute order
		 then we received response from Oanda
		  and response has tradeOpened section
		  and response has instrument equal to EUR_USD
		  and response section tradeOpened has units equal to 100

	Scenario: Limit order can be issued to Oanda
		Given Executor is setup to connect to Oanda practice using api connection
		  and we put limit order to buy 125 units of EUR_USD at price 0.75 expiring in 2 minutes
		 when i say execute order
		 then we received response from Oanda
		  and response has orderOpened section
		  and response has instrument equal to EUR_USD
		  and response section orderOpened has units equal to 100
		  and response section orderOpened has side equal to buy

	Scenario: We can query open orders from Oanda
		Given Executor is setup to connect to Oanda practice using api connection
		  and we put limit order to buy 125 units of EUR_USD at price 0.75 expiring in 2 minutes
		  and we have executed the order
		 when i say query my orders
		 then we received response from Oanda
		  and response lists my original order


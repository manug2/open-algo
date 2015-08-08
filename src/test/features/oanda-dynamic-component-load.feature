Feature: can load dynamic components for Oanda

	Scenario: Load Oanda forex streaming components dynamically
		Given we want to dynamically load module "oandaComponents"
		  and we want to establish connection to Oanda sandbox
		  and using account_id=1234567, instrument=EUR_USD and token=abcdef0123456abcdef0123456-abcdef0123456abcdef0123456
		 when i say load given oanda components definition file
		 then we find component "prices" is of type "OandaEventStreamer"

	Scenario: Load Oanda forex streaming components dynamically and stream rates
		Given we want to dynamically load module "oandaComponents"
		  and we want to establish connection to Oanda sandbox
		  and using account_id=1234567, instrument=EUR_USD and token=abcdef0123456abcdef0123456-abcdef0123456abcdef0123456
		 when i say load given oanda components definition file
		 then we can start thread "price_thread" for component "prices"


	Scenario: Load Oanda forex trading bot dynamically and start trading
		Given we want to dynamically load module "oandaComponents"
		  and we want to establish connection to Oanda sandbox
		  and using account_id=1234567, instrument=EUR_USD and token=abcdef0123456abcdef0123456-abcdef0123456abcdef0123456
		 when i say load given oanda components definition file
		 then we can start thread "trade_thread" for component "tradeBot"

		

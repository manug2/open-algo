Feature: Risk Manager is available to pre check orders and make trading decisions based on current value of portfolio

	Scenario Outline: RiskManager filters FX order to default limit minus current holding if original amount is greater
		Given RiskManager with default position limit
		  and current holding of <instrument> is <current holding>
		  and there is no position limit for instrument <instrument>
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units equal to default position limit minus <current holding>
		Examples: 
			| base currency	| current holding	| side	| units	| instrument	| order type	|
			| SGD		| 100			| buy	| 12345	| CHF_USD	| market	|

	Scenario Outline: RiskManager filters FX order to original amount if less than default limit minus curr holding
		Given RiskManager with default position limit
		  and current holding of <instrument> is <current holding>
		  and there is no position limit for instrument <instrument>
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<units>
		Examples: 
			| base currency	| current holding	| side	| units	| instrument	| order type	|
			| SGD		| 10			| buy	| 15	| CHF_USD	| market	|

	Scenario Outline: RiskManager filters FX orders according to preset def limit
		Given RiskManager with default position limit of <pos limit>
		  and current holding of <instrument> is <current holding>
		  and there is no position limit for instrument <instrument>
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<target units>
		Examples: 
			| base currency	| pos limit	| current holding	| side	| units	| instrument	| order type	| target units	| COMMENTS		|
			| SGD		| 10000		| 2000			| buy	| 12345	| CHF_USD	| market	| 8000		| limit - currently held|	

	Scenario Outline: RiskManager filters FX orders according to preset def limit and specific limit
		Given RiskManager with default position limit of <pos limit>
		  and current holding of <instrument> is <current holding>
		  and position limit for instrument <instrument> is <instr limit> units
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<target units>
		Examples: 
			| base currency	| pos limit	| current holding	| instr limit	| side	| units	| instrument	| order type	| target units	| COMMENTS					|
			| SGD		| 10000		| 2000			| 5000		| buy	| 101	| CHF_USD	| market	| 101		| order+current < specific limit < def limit	|
			| SGD		| 100		| 500			| 2000		| buy	| 1234	| CHF_USD	| market	| 1234		| order+current < specific limit > def limit	|
			| SGD		| 1000		| 500			| 2000		| buy	| 12345	| CHF_USD	| market	| 1500		| order+current > specific limit > def limit	|
			| SGD		| 1000		| 50			| 200		| buy	| 500	| CHF_USD	| market	| 150		| order+current > specific limit < def limit	|



	Scenario Outline: RiskManager filters FX orders according to preset SHORT def limit and specific limit
		Given RiskManager with default short position limit of <short pos limit>
		  and current holding of <instrument> is <current holding>
		  and there is no position limit for instrument <instrument>
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<target units>
		Examples: 
			| base currency	| short pos limit	| current holding	| side	| units	| instrument	| order type	| target units	| COMMENTS - SHORT				|
			| SGD		| 100			| 50			| sell	| 1234	| CHF_USD	| market	| 150		| order > abs(-def limit) + current			|
			| SGD		| 1000			| -50			| sell	| 123	| CHF_USD	| market	| 123		| order < abs(-def limit - current)			|

	
	
	Scenario Outline: RiskManager filters FX order to remaining amount if less than specific short limit but greater than default short limit
		Given RiskManager with default short position limit of <short pos limit>
		  and current holding of <instrument> is <current holding>
		  and short position limit for instrument CHF_USD is <instr short limit> units
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<target units>
		Examples: 
			| base currency	| short pos limit	| current holding	| instr short limit	| side	| units	| instrument	| order type	| target units	| COMMENTS - SHORT				|
			| SGD		| 100			| -800			| 2000			| sell	| 1234	| CHF_USD	| market	| 1200		| order < abs(-spec limit - current), spec > def|
			| SGD		| 1000			| 0			| 2000			| sell	| 12345	| CHF_USD	| market	| 2000		| order > abs(-spec limit - current), spec > def|
			| SGD		| 1000			| 0			| 200			| sell	| 500	| CHF_USD	| market	| 200		| order > abs(-spec limit - current), spec < def|
	

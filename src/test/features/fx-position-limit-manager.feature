Feature: Risk Manager is available to pre check orders and make trading decisions when portfolio is empty

	Scenario: RiskManager filters FX order to default limit if original amount is greater
		Given RiskManager with default position limit
		  and we want to buy 123450000 units of CHF_USD at market rate
		  and there is no position limit for instrument CHF_USD
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=CHF_USD, side=buy, order_type=market
		  and filtered order has numerical units equal to default position limit

	Scenario: RiskManager filters FX order to original amount if less than default limit
		Given RiskManager with default position limit
		  and we want to buy 15 units of CHF_USD at market rate
		  and there is no position limit for instrument CHF_USD
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=CHF_USD, side=buy, order_type=market
		  and filtered order has numerical units=15


	Scenario Outline: RiskManager filters FX orders based on preset default position limit
		Given RiskManager with default position limit of <pos limit>
		  and we want to <side> <units> units of <instrument> at <order type> rate
		  and there is no position limit for instrument <instrument>
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<pos limit>
		Examples: Orders and default position limits
			| pos limit	| side	| units		| instrument	| order type	|
			| 100		| buy	| 1000		| CHF_USD	| market	|
			| 10000		| buy	| 12345		| CHF_USD	| market	|
	
	
	Scenario Outline: RiskManager filters FX order to original amount if less than default limit
		Given RiskManager with default position limit of <pos limit>
		  and we want to <side> <units> units of <instrument> at <order type> rate
		  and there is no position limit for instrument <instrument>
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<units>
		Examples: Orders and default position limits
			| pos limit	| side	| units		| instrument	| order type	|
			| 10000		| buy	| 123		| CHF_USD	| market	|

	Scenario Outline: RiskManager filters FX order to original amount if less than specific limit but greater than default
		Given RiskManager with default position limit of <pos limit>
		  and position limit for instrument <instrument> is <instr limit> units
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<units>
		Examples: Orders and specific position limits
			| pos limit	| instr limit	| side	| units		| instrument	| order type	|
			| 10000		| 2000		| buy	| 1234		| CHF_USD	| market	|
	
	Scenario Outline: RiskManager filters FX order to specific limit (greater or less than default limit)
		Given RiskManager with default position limit of <pos limit>
		  and position limit for instrument <instrument> is <instr limit> units
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<instr limit>
		Examples: Orders and specific position limits
			| pos limit	| instr limit	| side	| units		| instrument	| order type	|
			| 100		| 2000		| buy	| 12345		| CHF_USD	| market	|
			| 1000		| 200		| buy	| 500		| CHF_USD	| market	|
	
	
	Scenario Outline: RiskManager filters FX order to default short limit if original amount is greater
		Given RiskManager with default short position limit of <short pos limit>
		  and there is no position limit for instrument <instrument>
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<short pos limit>
		Examples: Orders and specific position limits
			| short pos limit	| side	| units		| instrument	| order type	|
			| 100			| sell	| 1234		| CHF_USD	| market	|


	Scenario Outline: RiskManager filters FX order to original amount if less than default SHORT limit
		Given RiskManager with default short position limit of <short pos limit>
		  and there is no position limit for instrument <instrument>
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<units>
		Examples: Orders and specific position limits
			| short pos limit	| side	| units		| instrument	| order type	|
			| 1000			| sell	| 123		| CHF_USD	| market	|

	Scenario Outline: RiskManager filters FX order to original amount if less than specific SHORT limit but greater than default short limit
		Given RiskManager with default short position limit of <short pos limit>
		  and short position limit for instrument <instrument> is <instr short limit> units
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<units>
		Examples: Orders and specific position limits
			| short pos limit	| instr short limit	| side	| units		| instrument	| order type	|
			| 100			| 2000			| sell	| 1234		| CHF_USD	| market	|

	
	Scenario Outline: RiskManager filters FX order to specific short limit (greater or less than default limit)
		Given RiskManager with default short position limit of <short pos limit>
		  and short position limit for instrument <instrument> is <instr short limit> units
		  and we want to <side> <units> units of <instrument> at <order type> rate
		 when when i say filter order
		 then RiskManager returns filtered order
		  and filtered order has instrument=<instrument>, side=<side>, order_type=<order type>
		  and filtered order has numerical units=<instr short limit>
		Examples: Orders and specific position limits
			| short pos limit	| instr short limit	| side	| units		| instrument	| order type	|
			| 1000			| 2000			| sell	| 12345		| CHF_USD	| market	|
			| 1000			| 200			| sell	| 500		| CHF_USD	| market	|



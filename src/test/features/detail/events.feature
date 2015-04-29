Feature: detail - there is a thing called 'event' in trading which is captured by a journaler

	Scenario: TickEvent can be created
		Given we want to trade
		 when we want to listen to tick
		 then we use TickEvent
		

	Scenario: OrderEvent can be created
		Given we want to trade
		 when we want to create order
		 then we use OrderEvent

	Scenario: journaler can be created
		Given we want to trade in event driven fashion utilizing a journaler
		 when we want to log event
		 then there is a journaler
		  and journaler can log event

	Scenario: journaler can be log as last event
		Given we want to trade in event driven fashion utilizing a journaler
		 when we receive a tick
		 then journaler logs show it as last event

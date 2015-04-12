# Wire components for Oanda Test FX service

from com.open.algo.oanda.streaming import StreamingForexPrices

token = "abcdef0123456abcdef0123456-abcdef0123456abcdef0123456"
instrument = "EUR_USD"
account_id = "12345678"
domain = "stream-fxpractice.oanda.com"

prices = StreamingForexPrices(
    domain, token, account_id,
    instrument, None, None
)


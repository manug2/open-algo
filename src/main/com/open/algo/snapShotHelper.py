__author__ = 'ManuGarg'


from com.open.algo.trading.fxPortfolio import FxPortfolio


class SnapShotHelper():

    def __init__(self):
        pass

    def create_portfolio_snap_shot(self, portfolio):
        snap_shot = dict()
        snap_shot['base_ccy'] = portfolio.get_base_ccy()
        snap_shot['opening_balance'] = portfolio.opening_balance
        snap_shot['balance'] = portfolio.get_balance()
        snap_shot['realized_pnl'] = portfolio.get_realized_pnl()
        snap_shot['positions'] = portfolio.positions
        snap_shot['executions'] = portfolio.executions
        snap_shot['avg_price'] = portfolio.positions_avg_price
        return snap_shot

    def load_portfolio_snap_shot(self, snap_shot):
        if not isinstance(snap_shot, dict):
            raise TypeError('Expecting dictionary to load portfolio snap shot, found [%s]' % type(snap_shot))

        if 'balance' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('balance', snap_shot.keys()))
        elif 'opening_balance' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('opening_balance', snap_shot.keys()))
        elif 'base_ccy' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('base_ccy', snap_shot.keys()))
        elif 'realized_pnl' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('realized_pnl', snap_shot.keys()))
        elif 'positions' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('positions', snap_shot.keys()))
        elif 'executions' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('executions', snap_shot.keys()))
        elif 'avg_price' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('avg_price', snap_shot.keys()))

        base_ccy = snap_shot['base_ccy']
        opening_balance = snap_shot['opening_balance']
        portfolio = FxPortfolio(base_ccy, opening_balance)

        portfolio.balance = snap_shot['balance']
        portfolio.realized_pnl = snap_shot['realized_pnl']
        portfolio.positions = snap_shot['positions']
        portfolio.executions = snap_shot['executions']
        portfolio.positions_avg_price = snap_shot['avg_price']

        return portfolio

    def create_snap_shot_from_strategy(self, strategy):
        snap_shot = dict()
        snap_shot['signaled_positions'] = strategy.get_signaled_positions()
        snap_shot['open_interests'] = strategy.get_open_interests()
        return snap_shot


    def load_snap_shot_into_strategy(self, snap_shot, strategy):
        if not isinstance(snap_shot, dict):
            raise TypeError('Expecting dictionary to load strategy snap shot, found [%s]' % type(snap_shot))

        if 'signaled_positions' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('signaled_positions', snap_shot.keys()))
        elif 'open_interests' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('open_interests', snap_shot.keys()))

        signaled_positions = snap_shot['signaled_positions']
        strategy.signaled_positions = signaled_positions
        open_interests = snap_shot['open_interests']
        strategy.open_interests = open_interests

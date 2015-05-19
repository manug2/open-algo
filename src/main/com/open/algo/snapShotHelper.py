__author__ = 'ManuGarg'


class SnapShotHelper():

    def __init__(self):
        pass

    def create_portfolio_snap_shot(self, portfolio):
        portfolio_snap_shot = dict()
        portfolio_snap_shot['realized pnl'] = portfolio.realized_pnl
        portfolio_snap_shot['positions'] = portfolio.positions
        portfolio_snap_shot['executions'] = portfolio.executions
        portfolio_snap_shot['avg price'] = portfolio.positions_avg_price
        return portfolio_snap_shot

    def load_portfolio_snap_shot(self, portfolio, snap_shot):
        if not isinstance(snap_shot, dict):
            raise TypeError('Expecting dictionary to load portfolio snap shot, found [%s]' % type(snap_shot))

        if 'realized pnl' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('realized pnl', snap_shot.keys()))
        elif 'positions' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('positions', snap_shot.keys()))
        elif 'executions' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('executions', snap_shot.keys()))
        elif 'avg price' not in snap_shot:
            raise ValueError('Expecting [%s] key in load portfolio snap shot dictionary, not found in keys [%s]'
                             % ('avg price', snap_shot.keys()))

        portfolio.realized_pnl = snap_shot['realized pnl']
        portfolio.positions = snap_shot['positions']
        portfolio.executions = snap_shot['executions']
        portfolio.positions_avg_price = snap_shot['avg price']



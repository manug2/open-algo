from com.open.algo.model import ExecutionCostPredictor


class FxSpreadCostEvaluator(ExecutionCostPredictor):
    def __init__(self):
        self.TYPE = 'TICK'
        self.rates = {}

    def __str__(self):
        msg = __class__.__name__
        return msg

    def eval_cost(self, order):
        raise NotImplementedError("Should implement 'eval_cost()' method")

    def set_rate(self, tick):
        raise NotImplementedError("Should implement 'set_rate()' method")

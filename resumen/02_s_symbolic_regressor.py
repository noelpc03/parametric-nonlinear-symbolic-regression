from gplearn.genetic import SymbolicRegressor
from gplearn.fitness import make_fitness
import pickle
from pathlib import Path

class SymbolicRegressorWrapper(SymbolicRegressor):
    def define_metric_function(self, fitness_fun, is_maximize=False):
        fitness = make_fitness(function=fitness_fun, greater_is_better=is_maximize)
        self.metric = fitness

    def set_new_target_generations(self, generations):
        self.set_params(generations=generations, warm_start=True)

    def save(self, name):
        filename = f"models/{name}.pkl"
        output_file = Path(filename)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(name):
        filename = f"models/{name}.pkl"
        model = SymbolicRegressorWrapper()
        with open(filename, "rb") as f:
            model = pickle.load(f)
        return model

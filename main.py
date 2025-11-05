import random
import joblib
from fast_events.runner import Runner
from fast_events.test_strategy import KevStrategy
from fast_events.framework import Timeframe
from tqdm import tqdm

class StrategyDataConfig:
  filename='ES_60_2025.03.28'
  data1=Timeframe.H1
  data2=Timeframe.D1
  min_bars=21

class StrategyParams:
  max_bars_in_trade= 3  # 2 - 30
  poi_num=5             # 0 - 15
  atr_mult_num=9        # 0 - 10
  atr_period_num=3      # 0 - 3
  min_bars=21

if __name__ == "__main__":
    num_simulations = 1000
    run_in_parallel = True

    runner = Runner()
    runner.prepare_data(StrategyDataConfig)

    def optimisation():
        StrategyParams.max_bars_in_trade = random.randint(2, 30)
        StrategyParams.poi_num = random.randint(0, 15)
        StrategyParams.atr_mult_num = random.randint(0, 10)
        StrategyParams.atr_period_num = random.randint(0, 3)
        return runner.run(KevStrategy, StrategyParams)

    if run_in_parallel:
        # Parallel execution
        print('Running simulations in parallel on', joblib.cpu_count(), 'cores...')
        with joblib.Parallel(n_jobs=-1) as parallel:
            results = parallel(joblib.delayed(optimisation)() for _ in tqdm(range(num_simulations), desc='Running simulations', unit='simulations', colour='BLUE', disable=False))
    else:
        # Sequential execution
        print('Running simulations sequentially...')
        for i in tqdm(range(num_simulations), desc='Running simulations', unit='simulations', colour='BLUE', disable=False):
            StrategyParams.max_bars_in_trade = random.randint(2, 30)
            StrategyParams.poi_num = random.randint(0, 15)
            StrategyParams.atr_mult_num = random.randint(0, 10)
            StrategyParams.atr_period_num = random.randint(0, 3)
            runner.run(KevStrategy, StrategyParams)

    positive_results = sum(1 for result in results if result > 0)
    total_results = len(results)
    percentage_positive = (positive_results / total_results) * 100 if total_results > 0 else 0

    print(f"Positive results: {positive_results}/{total_results} ({percentage_positive:.2f}%)")


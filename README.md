# Trading Backtesting Framework

A comprehensive Python-based backtesting framework for testing and analyzing trading strategies, with a focus on directional bias and event-driven approaches.

## Project Structure

```
├── framework/           # Core backtesting infrastructure
├── fast_events/        # Event-driven strategy implementation
├── plot/               # Visualization tools
├── data/              # Market data storage
│   └── parquet/       # Optimized data storage format
└── vector/            # Vector operations utilities
```

## Core Features

### Backtesting Engine
- Robust backtesting system implemented in `framework/backtester.py`
- Simulated trading environment via `framework/sim_trader.py`
- Efficient data management through `framework/data_manager.py`
- Support for multiple symbols and asset types

### Strategy Implementation
The project includes several strategy variations focusing on directional bias:
- Basic directional bias (`direccional_bias.py`)
- Minimum resolution version (`direccional_bias_min_res.py`, `direccional_bias_min_res_v2.py`)
- TF resolution implementations (`direccional_bias_tf_res.py`, `direccional_bias_tf_res_event.py`)

### Event-Driven Framework
- Fast event processing system in the `fast_events/` directory
- Custom strategy testing framework (`fast_events/test_strategy.py`)
- Event handling framework (`fast_events/framework.py`)

## Getting Started

### Prerequisites
- Python 3.x (see `.python-version` for specific version)
- Required packages listed in `pyproject.toml`

### Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install -e .
```

### Running Backtests
1. Place your market data in the `data/` directory
2. Configure your strategy parameters
3. Run backtests using:
```bash
python main.py
```

### Visualization
Use the plotting utilities in `plot/plot.py` to visualize backtest results and analyze strategy performance.

## Data Management
- Supports CSV format (example: `ES_60_2025.03.28.csv`)
- Utilizes Parquet format for efficient data storage
- Data similarity testing available through `framework/data_simularity_test.py`

## Development

### Testing
Run strategy tests using:
```bash
python fast_events/test_strategy.py
```

### Debug Configuration
VSCode launch configurations are available in `.vscode/launch.json`

## Documentation

### Modules

#### Framework
- `backtester.py`: Core backtesting engine
- `data_manager.py`: Market data handling and processing
- `sim_trader.py`: Simulated trading environment
- `symbols.py`: Symbol definitions and management
- `types.py`: Type definitions for the framework

#### Fast Events
- `framework.py`: Event processing framework
- `runner.py`: Strategy execution engine
- `test_strategy.py`: Strategy testing utilities

## Contributing
1. Fork the repository
2. Create your feature branch
3. Submit a pull request

## License
[Add appropriate license information]

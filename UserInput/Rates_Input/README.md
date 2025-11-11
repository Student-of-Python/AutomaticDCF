Your configuration file (rate_config.json) should follow this structure:

`{
  "settings": {
    "forecast_period": 5
  },
  "rates": {
    "revenue": {
      "mode": "Hybrid",
      "manual_rates": [0.03, 0.06],
      "auto_method": "MeanReverting",
      "parameters": {
        "terminal_rate": 0.03,
        "phi": 0.7,
        "kappa": 0.2
      }
    },
    "ebit": {
      "mode": "Manual",
      "manual_rates": [0.03, 0.04, 0.04, 0.01]
    },
    "capex": {
      "mode": "Auto",
      "auto_method": "ConvergingMovingAverage",
      "parameters": {
        "window": 3,
        "terminal_rate": -0.08
      }
    }
  }
}`

### Forecasting Modes

Each line item can be configured to run in one of three modes:

#### Manual Mode

You provide all rate values explicitly.

`"ebit": {
  "mode": "Manual",
  "manual_rates": [0.03, 0.04, 0.04, 0.01]
}`


Use this when: You already know the growth/decline assumptions.

What happens: The model simply uses the provided list of rates.

Notes: The number of rates should match or be shorter than your forecast period.

#### Auto Mode

All forecast rates are generated using one of the built-in statistical or smoothing methods.

`"capex": {
  "mode": "Auto",
  "auto_method": "ConvergingMovingAverage",
  "parameters": {
    "window": 3,
    "terminal_rate": -0.08
  }
}`


Use this when: You want the system to calculate rates automatically.

What happens: The chosen auto_method uses historical data to forecast new rates.

Parameters: Each method requires specific inputs (see the reference table below).

#### Hybrid Mode

Combines manual input (historical data) and an auto method for projecting future values.

`"revenue": {
  "mode": "Hybrid",
  "manual_rates": [0.03, 0.06],
  "auto_method": "MeanReverting",
  "parameters": {
    "terminal_rate": 0.03,
    "phi": 0.7,
    "kappa": 0.2
  }
}
`

Use this when: You have partial manual data but want the rest auto-generated.

What happens: The model uses your manual_rates as a base, then continues forecasting with the selected auto_method.

### **Supported Auto Methods and Parameters**

| Method Name  | Required Parameters      | Description  |
|---|--------------------------|---|
| MovingAverage  | window                   | Simple trailing moving average of recent rates.  |
| ConvergingMovingAverage  | window, terminal_rate    | Moving average that gradually converges to a terminal rate.  | 
|  ExponentialMovingAverage | window, alpha (optional) | Weighted average emphasizing recent data.  |
| ConvergingExponentialMovingAverage  |    window, terminal_rate, alpha (optional)| EMA that converges to a terminal rate.  |
|  WeightedMovingAverage |         window, weights                 | Weighted average using specified weights (must sum to 1).  |
| ConvergingWeightedMovingAverage  |      window, weights, terminal_rate                    | Weighted average converging toward a long-term rate.  |
| MeanReverting  |          terminal_rate, phi, kappa                | Damped convergence toward a target rate (mean-reversion model).  |
| LinearRate  |       terminal_rate                   | Linear interpolation between the last rate and the terminal rate.  |
| Uniform  |            max_randomness              | Adds random variation (±%) around the last rate.  |
|MonteCarlo| percentile, sigma, episodes|Forecasts using Monte Carlo simulations.|
|ConvergingMonteCarlo|terminal_rate, percentile, sigma, episodes|Monte Carlo simulation that converges toward a terminal rate.|

### **Key Parameters Explained**

| Parameter  | Type   | Example | Meaning  |
|---|--------|---------|---|
|  window | int    | 3       | Number of trailing years to use in averaging.  |
| terminal_rate  | float  |   0.03      | Long-term steady-state growth or decline rate.  |
| phi  | float  |   0.7      | Momentum factor for mean reversion (0–1 typical).  |
| kappa  | float  |    0.2     |  Pullback strength toward the mean rate (0–1 typical). |
| alpha  |  float     |    0.5     | Weighting factor for exponential methods.  |
| weights  |  list      |   [0.1, 0.3, 0.6]      | Custom weighting for past data (must sum to 1).  |
| max_randomness  |  float      |    0.1     |  Maximum ±10% variation for random methods. |
| percentile  |    float    |    0.9     | Monte Carlo percentile (e.g., 0.9 = 90th percentile outcome).  |
| episodes  |  int      |    100     | Number of Monte Carlo simulations to run.  |


### **Best Practices**

1. Always use decimal format for rates (e.g., `0.05` for 5%).
2. Choose one mode per category (**Manual, Auto, or Hybrid**).
3. When using `Auto` or `Hybrid`, ensure you specify:
   * **auto_method**
   * Any required `**parameters**` for that method
4. Remember to fill in all categories (`revenue, ebit, nopat, da, capex, nwc`)
5. `forecast_period` controls how many future periods the model will generate.

### **Quick Example**
`{
        'revenue': {'manual_rates': [0.03,0.06], 'auto_method' : ('MeanReverting', {'terminal_rate': 0.03, 'phi': 0.7, 'kappa': 0.2})}, #Hybird
        'ebit': [0.03,0.04,0.04,0.01], #Manual
        'capex': ('ConvergingMovingAverage', {'window': 3, 'terminal_rate': -0.08}), #Fully auto
        'nopat': ('MovingAverage', {'window': 3}),#Fully auto
        'nwc': ('ConvergingMovingAverage', {'window': 3, 'terminal_rate': -0.03}),#Fully auto
        'da': ('ConvergingMovingAverage', {'window': 3, 'terminal_rate': 0.06}),#Fully auto
        }`

### **Summary**

|  Mode | Input Required  | Automatically Forecasts  |
|---|---|---|
| Manual  | All rates  | No  |
| Auto  | Parameters only  | Yes  |
| Hybrid  | Partial rates + parameters  | Yes  |

1. [Author]  Gleb Sokhin
2. [Contact]  gsokhin@umass.edu
3. [Last Updated] Oct. 2025


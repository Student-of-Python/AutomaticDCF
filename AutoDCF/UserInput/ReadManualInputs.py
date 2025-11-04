from AutoDCF.UserInput import *
import json

def read_manual_inputs():
    combined_data = {}
    json_files = [
        'Settings/Settings.json',
        'OverrideVars/Core_Financial_Assumptions.json',
        'OverrideVars/Mundane_Variables.json',
        'Rates_Input/Operating_Forecast_Inputs.json'
    ]

    for file in json_files:
        with open(file, 'r') as f:
            current_data = json.load(f)
            combined_data = combined_data | current_data
    return combined_data





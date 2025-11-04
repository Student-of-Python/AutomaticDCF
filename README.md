# AutoDCF  
**Automated Discounted Cash Flow (DCF) Analysis Tool**  

This repository contains a Python‑based tool designed to automate the process of performing a discounted cash flow (DCF) valuation of a company. While this project is **not yet production ready**, it is my intention to refine and harden it for production use in the near future.

## Objective  
The primary goal of this project is to provide a flexible Python framework that:  
- Fetches or ingests relevant financial data (income statements, balance sheets, cash flows)  
- Projects future free cash flows and estimates terminal value  
- Discounts projected cash flows using a suitable cost of capital (e.g., WACC)  
- Produces a resulting enterprise or equity valuation, and optionally calculates a per‑share implied value  
- Supports sensitivity analysis and variations in key assumptions  

## Features & Techniques  
Key components and techniques implemented in the project include:  
- **Automated Data Ingestion** – Retrieving historical financial statements and key metrics as inputs for the model  
- **Cash Flow Projection** – Estimating future free cash flows to the firm (FCFF) or free cash flows to equity (FCFE) based on historical trends and assumption‑inputs  
- **Cost of Capital Calculation** – Discounting cash flows using the weighted average cost of capital (WACC), or other user‑specified discount rates  
- **Terminal Value Estimation** – Calculating the residual value beyond the explicit forecast horizon, using a constant‐growth or exit‐multiple method  
- **Present Value Calculation** – Bringing projected and terminal cash flows to present value to estimate enterprise or equity value  
- **Sensitivity & Scenario Analysis** – Allowing users to vary key assumptions (growth rates, discount rates, terminal growth) and observe impacts on valuation  
- **Modular Architecture** – Components for data ingestion, projection, discounting and reporting are structured for extensibility and future enhancement  

## Intended Usage  
1. Clone the repository:  
   ```bash
   git clone https://github.com/Student-of-Python/FinanceProjects.git
   cd FinanceProjects/AutoDCF
   pip install -r requirements.txt

## Usage

1. **Install dependencies**  
   Install required Python packages, e.g., `pandas`, `numpy`, and any data‑fetch APIs.  

2. **Adjust configuration/assumptions**  
   Modify parameters such as growth rates, forecast horizon, discount rate, and terminal growth to match your analysis scenario.  

3. **Run the tool**  
   Execute the script (Run_DCF.py) to perform a valuation. This will generate a spreadsheet containing the following:  
   - WACC
   - Terminal Growth Rate
   - Projected Price
   - Upside / Downside
   - Table with relevant columns (revenue, ebit, etc) and rates

4. **Inspect results**  
   Expect to see a spreadsheet either in the directory or in downloads ready to be opened. 

---

## Roadmap & Production‑Ready Goals

While the project is usable in its current form for experimentation, the following enhancements are planned to move toward a production‑ready state:

- Robust error handling and data validation (handling missing or incomplete financials)  
- Integration of live or subscription‑grade data sources
- Logging and comprehensive documentation for each module  
- **User interface** or dashboard to configure assumptions without editing code
- Versioning, release management, and continuous integration/deployment  
- Performance optimization and scalability improvements  

---

## Disclaimer

This tool is provided **as is**, for educational and exploratory purposes only. It is **not** intended as investment, legal, or tax advice. Any valuations generated should be used with caution and professional judgment. The author assumes no responsibility for any decisions made based on the results of this tool.  

---

## Contact

For questions, suggestions, or discussions related to this project, please reach out to me at gsokhin@umass.edu 

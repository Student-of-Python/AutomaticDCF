# Design Document

# **Section 1 \- Project Description** {#section-1---project-description}

## **1.1 Project** {#1.1-project}

DCF Calculator

## **1.2 Description** {#1.2-description}

Description

## **1.3 Revision History** {#1.3-revision-history}

| Date | Comment | Author |
| :---- | :---- | :---- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

**Contents**  
[Section 1 \- Project Description](#section-1---project-description)  
[1.1 Project](#1.1-project)  
[1.2 Description](#1.2-description)  
[1.3 Revision History](#1.3-revision-history)  
[Section 2 \- Overview](#section-2---overview)  
[2.1 Purpose](#2.1-purpose)  
[2.2 Scope](#2.2-scope)  
[2.3 Requirements](#2.3-requirements)  
[2.3.1 Estimates](#2.3.1-estimates)  
[2.3.2 Traceability Matrix](#2.3.2-traceability-matrix)  
[Section 3 \- System Architecture](#section-3---system-architecture)  
[Section 4 \- Data Dictionary](#section-4---data-dictionary)  
[Section 5 \- Software Domain Design](#section-5---software-domain-design)  
[5.1 Software Application Domain Chart](#5.1-software-application-domain-chart)  
[5.2 Software Application Domain](#5.2-software-application-domain)  
[5.2.1 Domain X](#5.2.1-domain-x)  
[5.2.1.1 Component Y of Domain X](#5.2.1.1-component-y-of-domain-x)  
> > > [5.2.1.1.1 Task Z of Component Y1 of Domain X](#5.2.1.1.1-task-z-of-component-y1-of-domain-x)  
[Section 6 – Data Design](#section-6-–-data-design)  
[6.1 Persistent/Static Data](#6.1-persistent/static-data)  
[6.1.1 Dataset](#6.1.1-dataset)  
[6.1.2 Static Data](#6.1.2-static-data)  
[6.1.3 Persisted data](#6.1.3-persisted-data)  
[6.2 Transient/Dynamic Data](#6.2-transient/dynamic-data)  
[6.3 External Interface Data](#6.3-external-interface-data)  
[6.4 Transformation of Data](#6.4-transformation-of-data)  
[Section 7 \- User Interface Design](#section-7---user-interface-design)  
[7.1 User Interface Design Overview](#7.1-user-interface-design-overview)  
[7.2 User Interface Navigation Flow](#7.2-user-interface-navigation-flow)  
[7.3 Use Cases / User Function Description](#7.3-use-cases-/-user-function-description)  
[Section 8 \- Other Interfaces](#section-8---other-interfaces)  
[8.1 Interface X](#8.1-interface-x)  
[Section 9 \- Extra Design Features / Outstanding Issues](#section-9---extra-design-features-/-outstanding-issues)  
[Section 10 – References](#section-10-–-references)  
[Section 11 – Glossary](#section-11-–-glossary)

# **Section 2 \- Overview** {#section-2---overview}

## **2.1 Purpose** {#2.1-purpose}

The overall purpose of the DCF calculator is to automate the basic DCF evaluation process. The intended audience is finance students who may want to use the calculated figure as a benchmarker.   


## **2.2 Scope** {#2.2-scope}

This calculator is aiming to automate the DCF process to provide an evaluation figure for a company. 


## **2.3 Requirements** {#2.3-requirements}

Your mileage may vary \-- we typically break down the requirements to provide a ballpark estimate.

### **2.3.1 Estimates** {#2.3.1-estimates}

| \# | Description | Hrs. Est. |
| ----- | ----- | ----- |
| 1 | Brief description of task / module with link | \# est |
|  | **TOTAL**: | \# est tot |

### **2.3.2 Traceability Matrix** {#2.3.2-traceability-matrix}

Cross reference this document with your requirements document and link where you satisfy each requirement

| SRS Requirement | SDD Module |
| :---- | :---- |
| Req 1 | 5.1.1 (link to module), 5.1.2 (link) |
|  |  |
|  |  |

# **Section 3 \- System Architecture** {#section-3---system-architecture}

Describe/include a figure of the overall system architecture (and where this module fits in)

# **Section 4 \- Data Dictionary** {#section-4---data-dictionary}

Brief description of each element in this module or a link to an actual data dictionary

(template of a database table description)

| Table |
| :---: |

| Field        | Notes                      |     Type      |
|--------------|----------------------------|:-------------:|
| TICKER       | Company ticker             |    STRING     |
| YEARS        | HISTORICAL YEARS           |      INT      |
| CAGR         | EXPECTED GROWTH            |     FLOAT     |
| MODE         | DCF MODE (exit vs perp)    | STRINGLITERAL |
| INCOME_STMT  | INCOME STATEMENT           |   DATACLASS   |
| BALANCE_STMT | BALANCE SHEET              |   DATACLASS   |
| CASH_STMT    | CASH STATEMENT             |   DATACLASS   |
| COMPANY_INFO | GENERAL INFO ABOUT COMPANY |   DATACLASS   |
| MACRO_VARS   | MACRO VARABLES             |   DATACLASS   |

# **Section 5 \- Software Domain Design** {#section-5---software-domain-design}

## **5.1 Software Application Domain Chart** {#5.1-software-application-domain-chart}

Describe / chart each major software application domain and the relationships between objects (UML, etc)

## **5.2 Software Application Domain** {#5.2-software-application-domain}



### **5.2.1 Domain X** {#5.2.1-domain-x}

There will 3 major components:
1. Data Fetching 
2. Preliminary Calculations
3. Primary Calculations

#### Data Fetching 

Data Fetching is responsible for gathering all the necessary data. Some of the data will include 

* Financial Statements
    * Income Statements
    * Cash Statements
    * Balance Sheet
* Company Profile 
* Macro economic variables

#### Preliminary Calculations

Data Fetching is responsible for calculating smaller variables as a preparation for the primary DCF calculation. Some operations will include

* Computing WACC
    * Cost of Equity 
    * Cost of Debt
* Forecasting Categories


#### Primary Calculation

Primary Calculation is responsible for calculating the actual DCF valuation figure. Some operations will include 

* Extracting Future Cash Flow 
* Applying method (Exit vs Perp)
* Calculating Share Price


#### 5.2.1.1 Component 1: Data Fetching {#5.2.1.1-component-1-data-fetching}

##### Component Definition & Control Flow
* **Single Responsibility: Responsible for acquiring data needed for calculations. 
* **Execution Trigger & Control Flow: Component is trigger by user entering valid parameters. Ends if successful query and transitions into next component, else raises error. 
* **State & Memory Management: Returns refreshed variables and static variables from existing file.

##### Component Interface Specification
| Interface Element | Identifier / Method Signature          | Type / Data Structure                           | Behavior & Preconditions                                             |
| :--- |:---------------------------------------|:------------------------------------------------|:---------------------------------------------------------------------|
| **Primary Input** | fetch_raw_data(ticker, lookback_years) | str, int                                        | Historical years must be positive integer                            |                                                                                    |
| **Output / Return** | RawFinancialDataset                    | FinancialStatements, CompanyProfile Dataclasses | Will only verify that fields are filled. No checking for abnormality |
| **Error / Exception** | ProviderAPIError, TickerNotFoundError  | CustomException Exception                       | TimeoutException                                                     |                                                   |

---

###### 5.2.1.1.1 Task 1: Financial Statements Ingestion {#5.2.1.1.1-task-1-financial-statements-ingestion}
* **Task Objective:** Collects Income, Cash statements and Balance sheet. 
* **Step-by-Step Data Flow:**
  1. **Request Dispatch:** Scraped from MacroTrends website
  2. **Raw Ingestion & Schema Check:** Checked if entry exists and if value is a value number
  3. **Normalization & Type Enforcement:** Null values raise error. 
  4. **Output Assembly:** Assembled into FinancialStatements Dataclass
* **Failure Handling & Boundary Rules:** Raises exception depending on the error, or may persist if exception can be resolved.

###### 5.2.1.1.2 Task 2: Profile & Macroeconomic Variable Ingestion {#5.2.1.1.2-task-2-profile--macroeconomic-variable-ingestion}
* **Task Objective:** Company Profile requested from YFinance. Macroeconomic are scraped if need to be refreshed, while static variables are loaded in. 
* **Step-by-Step Data Flow:**
  1. **Identifier Resolution:** Extract variables based on identifying company country. 
  2. **Snapshot Extraction:** Most variables will be refreshed upon request. Static variables that need to be loaded in is equity risk premium.
  3. **Immutability Packaging:** ---
* **Failure Handling & Boundary Rules:** Raise exception and gracefully terminate

---

#### 5.2.1.2 Component 2: Preliminary Calculations {#5.2.1.2-component-2-preliminary-calculations}

##### Component Definition & Control Flow
* **Single Responsibility:** Processes data to compute wacc, forecasted rates. This is intermediate step, not final calculation. 
* **Execution Trigger & Control Flow:** After data retrieval is successful, this is called sequentially 
* **State & Mutability:** Deterministic -- just computes wacc and rates based off of the data given. 

##### Component Interface Specification
| Interface Element | Identifier / Method Signature          | Type / Data Structure    | Behavior & Preconditions                            |
| :--- |:---------------------------------------|:-------------------------|:----------------------------------------------------|
| **Primary Input** | calculate_preliminary_metrics(dataset) | `RawFinancialDataset`    | Data from fetching data must be provided            |
| **Output / Return** | PreliminaryMetricsResult               | Custom dataclass, pandas | WACC, Cost of Equity, Cost of Debt, Margins, rates] |
| **Error / Exception** | --                                     | Custom Domain Exception  | Raises Exception based on error                     |

---

###### 5.2.1.2.1 Task 1: Cost of Capital (WACC) Calculation {#5.2.1.2.1-task-1-cost-of-capital-wacc-calculation}
* **Task Objective:** [Document the mathematical derivation of Cost of Equity (e.g., CAPM), Cost of Debt (after-tax), and capital structure weightings.]
* **Step-by-Step Data Flow:**
  1. **Cost of Equity Computation:** [List the exact formula, inputs (Risk-Free Rate, Beta, Market Risk Premium), and rounding/precision rules.]
  2. **Cost of Debt Computation:** [List how effective interest rate and marginal tax rate are determined and applied.]
  3. **Capital Weightings Determination:** [Document how Market Value of Equity and Total Debt are extracted to compute $W_e$ and $W_d$.]
  4. **WACC Synthesis:** [Document the final combination formula and numerical boundaries allowed for the discount rate.]
* **Failure Handling & Boundary Rules:** [Define how zero-debt firms, negative tax rates, or negative equity scenarios are handled.]

###### 5.2.1.2.2 Task 2: Forecasting Parameters & Margin Derivation {#5.2.1.2.2-task-2-forecasting-parameters--margin-derivation}
* **Task Objective:** [Detail how historical growth rates, operating margins, CapEx-to-revenue ratios, and working capital changes are derived to drive forward projections.]
* **Step-by-Step Data Flow:**
  1. **Historical Trend Extraction:** [Describe how year-over-year revenue growth rates and EBIT margins are calculated across statement periods.]
  2. **Reinvestment Rate Calculation:** [Describe how Net Working Capital ($\Delta NWC$) and CapEx trends are computed relative to sales.]
  3. **Base Metric Assembly:** [Specify how terminal growth rate constraints and baseline inputs are packaged for primary cash flow modeling.]
* **Failure Handling & Boundary Rules:** [Specify bounds checking (e.g., handling negative historical revenues or infinite growth artifacts).]

---

#### 5.2.1.3 Component 3: Primary Calculations {#5.2.1.3-component-3-primary-calculations}

##### Component Definition & Control Flow
* **Single Responsibility:** [Write 1–2 sentences explaining how this component consumes intermediate metrics from Component 2 to project cash flows, calculate terminal value, and derive intrinsic enterprise and per-share equity value.]
* **Execution Trigger & Control Flow:** [Describe the entry method, how the chosen terminal value methodology (Exit Multiple vs. Perpetuity Growth) is selected, and how final results are returned.]
* **Side-Effect Boundaries:** [Define that this component executes pure valuation logic without performing disk writes, network access, or UI rendering.]

##### Component Interface Specification
| Interface Element | Identifier / Method Signature | Type / Data Structure | Behavior & Preconditions |
| :--- | :--- | :--- | :--- |
| **Primary Input** | `[e.g., compute_valuation(prelim_metrics, method_config)]` | `[e.g., PreliminaryMetricsResult, ValuationConfig]` | [Document configuration options required (projection horizon, terminal method, discount frequency).] |
| **Output / Return** | `[e.g., ValuationSummary]` | `[e.g., Custom dataclass / TypedDict]` | [List final output fields: Present Value of FCF, Terminal Value, Enterprise Value, Equity Value, Per Share Price.] |
| **Error / Exception** | `[e.g., InvalidTerminalMethodError, InfiniteValuationError]` | `[e.g., Custom Domain Exception]` | [List failures raised when discount rate $\le$ perpetuity growth rate or invalid multiples are applied.] |

---

###### 5.2.1.3.1 Task 1: Future Free Cash Flow (FCFF) Projection & Discounting {#5.2.1.3.1-task-1-future-free-cash-flow-fcff-projection--discounting}
* **Task Objective:** [Explain how Unlevered Free Cash Flows are projected over the forecast horizon (e.g., years 1 through $N$) and discounted back to present value using WACC.]
* **Step-by-Step Data Flow:**
  1. **Annual FCFF Computation:** [Specify the exact accounting equation applied per forecast period: $EBIT \times (1 - t) + D\&A - CapEx - \Delta NWC$.]
  2. **Discount Factor Derivation:** [Specify whether end-of-year or mid-year discounting conventions are applied and provide the discount factor equation.]
  3. **Present Value Summation:** [Document the cumulative sum calculation for the discrete forecast horizon.]
* **Failure Handling & Boundary Rules:** [Define checks for exploding cash flows or invalid discount factors.]

###### 5.2.1.3.2 Task 2: Terminal Value & Share Price Derivation {#5.2.1.3.2-task-2-terminal-value--share-price-derivation}
* **Task Objective:** [Document the calculation of Terminal Value (via Gordon Growth Perpetuity and/or Exit Multiple), Enterprise Value to Equity Value bridge, and final per-share price.]
* **Step-by-Step Data Flow:**
  1. **Terminal Value Evaluation:** [State the branch logic: if Perpetuity Growth, apply $\frac{FCFF_{N+1}}{WACC - g}$; if Exit Multiple, apply $EBITDA_N \times \text{Multiple}$.]
  2. **Enterprise Value Calculation:** [Sum Present Value of discrete cash flows with Present Value of Terminal Value.]
  3. **Equity Bridge:** [Detail adjustments to transition Enterprise Value to Equity Value: $\text{Equity Value} = \text{Enterprise Value} + \text{Cash} - \text{Total Debt} - \text{Preferred Stock} - \text{Minority Interest}$.]
  4. **Per-Share Price Derivation:** [Divide Equity Value by diluted shares outstanding and enforce output precision (e.g., 2 decimal places).]
* **Failure Handling & Boundary Rules:** [Document guards against $WACC \le g$, zero shares outstanding, or negative per-share outputs.]

# **Section 6 – Data Design** {#section-6-–-data-design}

Describe the data contained in databases and other shared structures between domains or within the scope of the overall project architecture

## **6.1 Persistent/Static Data** {#6.1-persistent/static-data}

Describe/illustrate the logical data model or entity relationship diagrams for the persistent data (or static data if static)

### **6.1.1 Dataset** {#6.1.1-dataset}

Describe persisted object/dataset and its relationships to other entities/datasets

### **6.1.2 Static Data** {#6.1.2-static-data}

Describe static data

### **6.1.3 Persisted data** {#6.1.3-persisted-data}

Describe persisted data

## **6.2 Transient/Dynamic Data** {#6.2-transient/dynamic-data}

Describe any transient data, include any necessary subsections

## **6.3 External Interface Data** {#6.3-external-interface-data}

Any external interfaces’ data goes here (this is for the data, section 8 is for the interface itself)

## **6.4 Transformation of Data** {#6.4-transformation-of-data}

Describe any data transformation that goes on between design elements

# **Section 7 \- User Interface Design** {#section-7---user-interface-design}

## **7.1 User Interface Design Overview** {#7.1-user-interface-design-overview}

Pictures, high level requirements, mockups, etc.

## **7.2 User Interface Navigation Flow** {#7.2-user-interface-navigation-flow}

Diagram the flow from one screen to the next

## **7.3 Use Cases / User Function Description** {#7.3-use-cases-/-user-function-description}

Describe screen usage / function using use cases, or on a per function basis

# **Section 8 \- Other Interfaces** {#section-8---other-interfaces}

Identify any external interfaces used in the execution of this module, include technology and other pertinent data

## **8.1 Interface X** {#8.1-interface-x}

Describe interactions, protocols, message formats, failure conditions, handshaking, etc

# **Section 9 \- Extra Design Features / Outstanding Issues** {#section-9---extra-design-features-/-outstanding-issues}

Does not fit anywhere else above, but should be mentioned \-- goes here

# **Section 10 – References**  {#section-10-–-references}

Any documents which would be useful to understand this design document or which were used in drawing up this design.

# **Section 11 – Glossary** {#section-11-–-glossary}

Glossary of terms / acronyms
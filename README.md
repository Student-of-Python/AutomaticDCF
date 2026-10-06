# Design 
Overall Goal:
  Make a DCF calculator that outputs a valuation of a company. The input fields come from the website portal, and the output will be displayed as an excel file. 
The MVP design should be minimal -- supporting only the vital functions. Some minimal functions include fetching the right data, deriving important information from it, and calculating the company 
valuation from it.


Personal Goals:
1. Write clean code
2. Design from principles
3. Enforce good habits (primarily  YAGNI + KISS lol)

Audience:
User (web user, wants to use DCF)


## Requirements

### Functional
"Specific operation the application must do, or allow the user to do in order to be successful"

1. Shall take in a company from user input 
2. Must calculate valuation using DCF methodology
3. Shall query for financial statements + misc vars
4. Shall enable DCF method (exit mult vs perp?)
5. Shall export to DCF with verbosity

### Non-Functional
"A Non-Functional requirement imposes a specific restriction or constraint that the application must satisfy to be successful"

1. Respond appropriately to query exceptions? 
2. Handle invalid data correctly
3. Verbose when debugging
4. Store static vars internally


## Use Cases

### Use Case: Add Settings

Name: Add Settings
Goal: Adds settings into calculator
Summary: The user is able to add a company ticker to the calculator. The calculator will these settings for  valuation, provided no errors
Actors: User, static vars, MacroTrends website
Preconditions: None -- is first step. 
Trigger: User inputs a company ticker, potentially a method for DCF valuation (exit mult vs perp)
Primary action sequence:
1. Application verifies input options are valid.
2. Application queries company for its static vars and financial statements
3. Application validates data
4. Application outputs DCF calculation (excel?)

Alternate action sequence: Validation Fails
1. Application fails to validate input options  


Postcondition: The user will have a DCF valuation based on the metrics
Nonfunctional requirements: This use case will handle errors in validating user input
Glossary: For now, "settings" refers to company name, and potentially DCF valuation option 

### Use Case: Query Company Data

Name: Query Company Data
Goal: request data required for calculation 
Summary: Query company data will return the financial statements and static vars that will be used for calculations
Actors: Static vars, MacroTrend website
Preconditions: Valid user settings 
Trigger: User input (company ticker) is valid
Primary action sequence:
1. Application queries company data 
2. Application queries static vars by country of company
3. Application verifies data

Alternate action sequence: Unknown company
1. ... 
2. Application returns empty after query -- unknown company or data could not be reached

Alternate action sequence: Corrupted Data
1-2. ...
3. Application detects missing data needed for calculation -- fails to proceed forward

Postcondition: DCF calculator will have all necessary data to form a valuation
Nonfunctional requirements: Needs to scrape websites for financial data; updated from time to time for static vars
Glossary: MacroTrends website is the website that will be scraped from. Static vars is refering to non-financial statement variables (ex: risk free rate)

### Use Case: Output DCF

Name: Output DCF
Goal: Returns a DCF valuation to the user
Summary: User will receive the valuation according to the DCF calculator. 
Actors: User
Preconditions: Valid User Settings (and company data too)
Trigger: Company data is successfully queried
Primary action sequence:
1. Application calculates DCF valuation determined by the method (exit mult vs perp)
2. Application returns DCF valuation to the user
Alternate action sequence: None?
Postcondition: None, application terminates? Or waits for next input  
Nonfunctional requirements: Outputs depending on user preference??
Glossary: DCF valuation method is regarding the two types of DCF methods: exit multiple and perpetuity



## Misc

### Use Case Format

Name:
Goal:
Summary:
Actors:
Preconditions:
Trigger:
Primary action sequence:
Alternate action sequence:
Postcondition:
Nonfunctional requirements:
Glossary:


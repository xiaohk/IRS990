import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

CONTRI = "PYContributionsGrantsAmt"
INVEST = "PYInvestmentIncomeAmt"

# Build data frame for analysis
df = pd.DataFrame.from_csv('interest.csv', sep = '\t')

print(df[CONTRI].mean())

# More on the jupyter notebook

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

CONTRI = "PYContributionsGrantsAmt"
INVEST = "PYInvestmentIncomeAmt"

# Build data frame for analysis
df = pd.DataFrame.from_csv('interest.csv', sep = '\t')

df[CONTRI].std()
print(df[CONTRI].mean())

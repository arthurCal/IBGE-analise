# Databricks notebook source
import numpy as np
import pandas as pd

pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("darkgrid")

!pip install --upgrade pip > /dev/null
!pip install sidrapy > /dev/null
import sidrapy

import plotly.graph_objects as go

# COMMAND ----------

data = sidrapy.get_table(table_code="1737", territorial_level="1", ibge_territorial_code="all", period="last 1000", header='y')
data

# COMMAND ----------

df = data.copy() # deep copy
df = df.drop(['NC', 'NN', 'MC', 'MN', 'D1C', 'D1N', 'D2N', 'D3C'], axis=1) # removing clutter
df.columns = df.iloc[0] # setting first row as column names
df = df[1:].reset_index(drop=True) # dropping first row
 
df['Mês'] = pd.to_datetime(df['Mês (Código)'], format='%Y%m') 
df['Valor'] = df['Valor'].replace('...', np.NaN).astype(float)
df_pivot = df.pivot('Mês', 'Variável', 'Valor')

df_pivot = df_pivot.rename(columns={
                         "IPCA - Número-índice (base: dezembro de 1993 = 100)": "IPCA - Index-number(100=december 1993)", 
                         "IPCA - Variação acumulada em 12 meses": "IPCA - 12 month period accumulated inflation", 
                         "IPCA - Variação acumulada em 3 meses": "IPCA - 3 month period accumulated inflation",
                         "IPCA - Variação acumulada em 6 meses": "IPCA - 6 month period accumulated inflation",
                         "IPCA - Variação acumulada no ano": "IPCA - Year-long period accumulated inflation",
                         "IPCA - Variação mensal": "IPCA - monthly variation"})


df_pivot.reset_index().rename(columns={'Mês': 'Month', 'Variável': 'Variables'}).set_index('Month')

# COMMAND ----------

# DBTITLE 1,#1 - Mean, Median and Standard Deviation: Monthly Inflation from 2011 to 2020
inflacao_2011_2020 = df_pivot[(df_pivot.index >= '2011-01-01') & (df_pivot.index <= '2021-01-01')]['IPCA - monthly variation']

print('Variação da Inflação Mensal')
print('Mean:         ', round(inflacao_2011_2020.mean(), 2))
print('Median:       ', round(inflacao_2011_2020.median(), 2))
print('Std: ', round(inflacao_2011_2020.std(), 2))

fig, ax = plt.subplots(figsize=(16,9))

sns.kdeplot(inflacao_2011_2020, ax=ax)
ax.axvline(inflacao_2011_2020.mean(), 0, 0.5, color='g', label='Mean')
ax.axvline(inflacao_2011_2020.median(), 0, 0.5, color='r', label = 'Median');

ax.legend();

# COMMAND ----------

# DBTITLE 1,#2 - Mean, Median and Standard Deviation: Monthly Inflation for each year after 2000
inflationYearLong_2000onwards = pd.DataFrame(df_pivot[(df_pivot.index >= '2000-01-01')]['IPCA - monthly variation'])

inflationYearLong_2000onwards.groupby(inflacao_anual_2000_em_diante.index.year)['IPCA - monthly variation'].agg(['mean', 'median', 'std'])

# COMMAND ----------

# DBTITLE 1,#3 - Which year had the greatest accumulated inflation? 
yearInflation = df_pivot[df_pivot.index.month == 12]['IPCA - Year-long period accumulated inflation'].idxmax()

df_pivot.loc[pd.Timestamp(yearInflation)]

# COMMAND ----------

# DBTITLE 1,#4 - Which six-month period had the greatest accumulated inflation?
lowestInflationSemester = df_pivot['IPCA - 6 month period accumulated inflation'].idxmin()

df_pivot.loc[pd.Timestamp(lowestInflationSemester)]

# COMMAND ----------

# DBTITLE 1,Graph Visualization: Mean, Median and Standard Deviation, 2000-2022
inflationYearLong_2000onwards = pd.DataFrame(df_pivot[(df_pivot.index >= '2000-01-01')]['IPCA - monthly variation'])

stats = (inflationYearLong_2000onwards
         .groupby(inflationYearLong_2000onwards.index.year)['IPCA - monthly variation']
         .agg(['mean', 'median', 'std']))

fig, ax = plt.subplots(2, 1, figsize=(16,9))

fig.suptitle('Yearly Mean, Median and Standard Deviation of Inflation from 2000 to 2022', fontsize=25)

sns.lineplot(data=stats, x=stats.index, y='mean', label='Mean', ax=ax[0])
sns.lineplot(data=stats, x=stats.index, y='median', label='Median', ax=ax[0])
sns.lineplot(data=stats, x=stats.index, y='std', label='Std', ax=ax[0]) 

ax[0].set_xlabel('Year', fontsize=14)
ax[0].set_ylabel('Statistics', fontsize=14)
ax[0].set_xlim(1999, 2023)
ax[0].set_ylim(0, 1)

sns.boxplot(y=df_pivot[(df_pivot.index >= '2000-01-01')]['IPCA - monthly variation'], x=df_pivot[(df_pivot.index >= '2000-01-01')].index.year, ax=ax[1]);

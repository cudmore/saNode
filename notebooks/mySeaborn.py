import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt

#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context
#df = sns.load_dataset('../hcn4-Distance-Result.csv')

# plot the mean/median of HCN4 pixels to closest vasculature
path = '../hcn4-Distance-Result.csv'
df = pd.read_csv(path)

# decide which of head/mid/tail to plot
theseRegions = ['head', 'tail']
df = df[df['headMidTail'].isin(theseRegions)]

yStatName = 'median' # (median, mean)
sns.catplot(x='headMidTail', y=yStatName, hue='SAN', kind="point", data=df)

plt.show()

#
#
path = '../Density-Result-ch2.csv'
df = pd.read_csv(path)

# decide which of head/mid/tail to plot
theseRegions = ['head', 'tail']
df = df[df['headMidTail'].isin(theseRegions)]

yStatName = 'vMaskPercent' # (median, mean)
sns.catplot(x='headMidTail', y=yStatName, hue='SAN', kind="point", data=df)

plt.show()

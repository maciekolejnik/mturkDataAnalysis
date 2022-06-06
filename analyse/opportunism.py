import matplotlib.pyplot as plt
import scipy.stats as st
import pandas as pd
import numpy as np
import pingouin as ping
import analyse.aux as aux
from scipy.stats import mannwhitneyu

FILENAME = "plots/opportunism.png"
# compare returns in disclosed vs undisclosed conditions

def report(df):
    horizons = 'disclosed', 'undisclosed'
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(30, 10))
    data = [
        df.loc[(df['horizon'] == horizon) & (df['bot role'] == 'investor') &
               (pd.notna(df['last transfer prop']))]['last transfer prop']
        for horizon in horizons]
    # box plot first
    for i, h in enumerate(horizons):
        al = df[(df['horizon'] == h) & (df['bot role'] == 'investor')]
        print(f'Total: {len(al)} points for {h} horizon but only {len(data[i])} with nonzero')
    aux.boxplot(data, horizons, axs[0], 'return prop', test_normal=True)
    # overlaid histograms
    axs[1].hist(data[0], bins=4, range=(0,2), alpha=0.5, label='disclosed')
    axs[1].hist(data[1], bins=4, range=(0, 2), alpha=0.5, label='undisclosed')
    axs[1].legend(loc='upper right')
    # side by side bars
    bins = pd.cut(data[0], np.arange(-0.01, 2.5, 0.505), labels=False)
    print(bins)
    print(bins.value_counts())
    counts = bins.value_counts()
    print(counts)
    # print(counts[6])
    # exit(1)

    # number 3
    fig, ax = plt.subplots()
    # ax = axs[2]
    offsets = -.1, .1
    colors = 'r', 'g'
    bracket = lambda i: '[' if i == 0 else '('
    labels = [f'{bracket(i)}{i}, {i+.5}]' for i in np.arange(0, 2, 0.5)]
    # labels = '[0, .25]', '[.25, .25]', '[0, .25]', '[0, .25]', '[0, .25]', '[0, .25]',
    ax.set_xticks(range(0, 4), labels=labels)
    for i, horizon in enumerate(horizons):
        bins = pd.cut(data[i], np.arange(0, 2.5, 0.5), include_lowest=True, labels=False)
        counts = bins.value_counts().reindex([0, 1, 2, 3], fill_value=0)
        ax.bar(counts.index + offsets[i], counts.array, width=0.2, color=colors[i], align='center', label=horizon)
        # for j, label in enumerate(labels):
        #     count = counts[j] if j in counts.index else 0
        #     axs[2].bar(j + offsets[i], count, width=0.2, color=colors[i], align='center', label=horizon)
    ax.legend(loc='upper right')
    print("\n\n+------------------------------+")
    print("Human opportunism:")
    for i, d in enumerate(data):
        print(f'\nSummary of return proportions with {horizons[i]} horizon:')
        print(d.describe())
    print('Testing statistical significance between groups:')
    print(st.ttest_ind(*data))
    print(ping.ttest(*data))
    print(mannwhitneyu(*data))
    print("+------------------------------+")
    fig.savefig(FILENAME, transparent=False, dpi=300, bbox_inches="tight")
    print(f'Bot character plots saved to {FILENAME}')
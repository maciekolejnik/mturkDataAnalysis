import matplotlib.pyplot as plt

FILENAME = 'plots/demographics.png'


def report(df):
    all_labels = {
        'age': ['18-24', '25-34', '35-49', '50-64', '65+'],
        'gender': ['Neither', 'Female', 'Male', 'PNTS'],
        'education': ['$\leq$ High School', "Bachelor's",
                      "Master's", "$\geq$ PhD", "PNTS"],
        'robot exposure': ['No exposure', 'Limited exposure', 'Fair exposure',
                           'High exposure', 'Very high exposure'],
        'nationality': {
            '0': 'PNTS',
            '356': 'India',
            '702': 'Singapore',
            '826': 'UK',
            '840': 'US'
        }
    }
    df['nationality'] = df['nationality'].apply(str)  # little hack for nationality
    # use below to have all plots in one file
    # fig, axs = plt.subplots(nrows=1, ncols=5, figsize=(30, 6))
    angles = [0, 0, 0, 300, 0]
    font_sizes = [14,14,14,11,14]
    for i, cat in enumerate(['age', 'education', 'gender', 'nationality', 'robot exposure']):
        # use for one file
        # ax = axs[i]
        # use below for separate files
        fig, ax = plt.subplots()
        dist = df[cat].value_counts().sort_index()
        indexed_labels = [(i, all_labels[cat][i]) for i in dist.index.tolist()]
        print(f'{cat} distribution:')
        for j, label in indexed_labels:
            print(f'\t{label}: {dist[j]}')
        # ax.set_title(cat)
        labels = [label for (i, label) in indexed_labels]
        ax.pie(dist.values, labels=labels, textprops={'fontsize': font_sizes[i]},
               labeldistance=1.1, startangle=angles[i])
        fig.savefig(f'plots/demographics/{cat.split()[0]}.png')
    # plt.subplots_adjust(wspace=0.6)
    # fig.savefig(FILENAME, transparent=False, dpi=80, bbox_inches="tight")
    print(f'Demographics plots saved to plots/demographics')

import matplotlib.pyplot as plt

FILENAME = 'plots/demographics.png'


def report(df):
    all_labels = {
        'age': ['18-24', '25-34', '35-49', '50-64', '65+'],
        'gender': ['Neither', 'Female', 'Male', 'Prefer not to say'],
        'education': ['High School or lower', "Bachelor's Degree",
                      "Master's Degree", "PhD or higher", "Prefer not to say"],
        'robot exposure': ['No exposure', 'Limited exposure', 'Fair exposure',
                           'High exposure', 'Very high exposure'],
        'nationality': {
            '0': 'Prefer not to say',
            '356': 'India',
            '702': 'Singapore',
            '826': 'UK',
            '840': 'US'
        }
    }
    df['nationality'] = df['nationality'].apply(str)  # little hack for nationality
    fig, axs = plt.subplots(nrows=1, ncols=5, figsize=(30,6))
    # plt.style.use('ggplot')
    for i, cat in enumerate(['age', 'education', 'gender', 'nationality', 'robot exposure']):
        dist = df[cat].value_counts().sort_index()
        indexed_labels = [(i, all_labels[cat][i]) for i in dist.index.tolist()]
        print(f'{cat} distribution:')
        for j, label in indexed_labels:
            print(f'\t{label}: {dist[j]}')
        axs[i].set_title(cat)
        labels = [label for (i, label) in indexed_labels]
        axs[i].pie(dist.values, labels=labels)
    plt.subplots_adjust(wspace=0.6)
    fig.savefig(FILENAME, transparent=False, dpi=80, bbox_inches="tight")
    print(f'Demographics plots saved to {FILENAME}')

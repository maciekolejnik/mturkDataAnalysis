import analyse.aux as aux
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from scipy.stats import mannwhitneyu
from pingouin import ttest
import pandas as pd
import numpy as np
import seaborn as sn
from sklearn.metrics import confusion_matrix

FILENAME = 'plots/character.png'


def report(df):
    bot_characters = ['selfless', 'neutral', 'greedy']
    outcome_vars = ['fairness', 'total welfare']
    questionnaire = ['bot humanness', '∆trust bot', '∆trust general']

    def split_by_character(data, var):
        # return [data.query('`bot character` == @bot_character')[var]
        #         for bot_character in bot_characters]
        return [data.loc[lambda f: f['bot character'] == bot_character][var]
                for bot_character in bot_characters]

    fig, axs = plt.subplots(nrows=1, ncols=5, figsize=(30, 6))
    print("\n\n+------------------------------+")
    print("How outcomes vary depending on bot character:")
    for index, outcome_var in enumerate(outcome_vars):
        print('__________________')
        print(f'| {outcome_var.upper()} |')
        print('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾')
        data_by_character = split_by_character(df, outcome_var)
        for i, d in enumerate(data_by_character):
            print(f'For {bot_characters[i]}')
            print(d.describe())
        aux.boxplot(data_by_character, bot_characters, axs[index], outcome_var, test_normal=True, overlay_data=False)
        # for loop below manually overlays data points with color reflecting bot role
        # if not needed can be commented out and overlay_data=True passed above
        for j, char in enumerate(bot_characters):
            ys = [df[(df['bot character'] == char) & (df['bot role'] == role)][outcome_var] for role in ['investor', 'investee']]
            for i, y in enumerate(ys):
                shift = np.random.normal(0, 0.04, size=len(y))
                x = j + 1 + [0.02, -0.02][i] + [1, -1][i] * abs(shift)
                color = ['y', 'r'][i]
                axs[index].scatter(x=x, y=y, c=color, alpha=0.2)
        # analyse pairwise significance
        for i, j in [(i, j) for i in [0, 1, 2] for j in [0, 1, 2] if i < j]:
            print(f'\nTesting {bot_characters[i]} vs {bot_characters[j]}'.upper())
            # print('Standard t test:')
            # print(ttest_ind(data_by_character[i], data_by_character[j]))
            print('Fancy t test:')
            print(ttest(data_by_character[i], data_by_character[j]))
            print('Wilcoxon test:')
            print(mannwhitneyu(data_by_character[i], data_by_character[j]))

    # bucket 5 differnt into three different
    df['bot humanness'] = df['bot humanness'].apply(lambda v: min(4, max(2, v)))
    for index, question in enumerate(questionnaire):
        print(f'Consider {question}'.upper())
        ax = axs[index + 2]
        # print(df[question].unique().sort())
        outcomes = sorted(df[question].unique())
        number_of_outcomes = len(outcomes)
        def get_labels(qn):
            return ['disagree', 'neutral', 'agree'] if qn == 'bot humanness' else \
                ['decreased', 'no change', 'increased']
        # labels = {
        #     '5': ['strong\ndisagree', 'disagree', 'neutral', 'agree', 'strongly\nagree'],
        #     '3': ['decreased', 'no change', 'increased']
        # }
        ax.set_xticks(ticks=outcomes, labels=get_labels(question))
        ax.set_title(question)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))
        offsets = -0.2, 0, 0.2
        colors = 'b', 'g', 'r'
        for i, character in enumerate(bot_characters):
            data = df.query(f'`bot character` == @character')[question]
            print(f'Data for {character}:')
            # data = df.loc[lambda f: f['bot character'] == character][question]
            counts = data.value_counts()
            print(counts)
            x = counts.index
            y = list(map(lambda v: v / sum(counts.values), counts.values))
            ax.bar(x + offsets[i], y, width=0.2, color=colors[i], align='center', label=character)
        loc = 'left' if question == 'bot humanness' else 'right'
        ax.legend(loc=f'upper {loc}')
    fig.savefig(FILENAME, transparent=False, dpi=80, bbox_inches="tight")
    print(f'Bot character plots saved to {FILENAME}')

    # plot earnings depending on role
    df['human role'] = df.apply(
        lambda row: 'investor' if row['bot role'] == 'investee' else 'investee', axis=1)
    roles = 'investor', 'investee'
    players = 'bot', 'human'
    earnings = {
        player: {
            role: df[df[f'{player} role'] == role][f'earned {player}'] for role in roles
        } for player in players
        # 'bot': {
        #     role: df[df['bot role'] == role]['earned bot'] for role in roles
        # },
    }
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))
    # first simply by role
    data = [pd.concat([earnings[player][role] for player in players]) for role in roles]
    aux.boxplot(data, roles, axs[0], 'by role')
    # now by role and player
    data = [earnings[player][role] for player in players for role in roles]
    labels = [f'{player}\n({role})' for player in players for role in roles]
    aux.boxplot(data, labels, axs[1], 'by player and role')
    # save it
    fig.savefig('plots/earnings.png', transparent=False, dpi=80, bbox_inches="tight")
    print(f'Earnings plots saved to plots/earning.png')

    # earnings_data_by_role = pd.concat([df[df['bot role'] == 'investor']['earned bot'],
    #                                    df[df['bot role'] == 'investee']['earned human']])
    # aux.boxplot()

    # various ways of visualising bot humanness
    long_labels = ['strongly\ndisagree', 'disagree', 'neutral', 'agree', 'strongly\nagree']
    fig, axs = plt.subplots(nrows=1, ncols=4, figsize=(24, 6))
    question = 'bot humanness'
    axs[0].set_title('5 categories, absolute')
    axs[0].set_xticks(ticks=[1, 2, 3, 4, 5], labels=long_labels)
    offsets = -0.2, 0, 0.2
    colors = 'b', 'g', 'r'
    for i, character in enumerate(bot_characters):
        data = df[df['bot character'] == character][question]
        counts = data.value_counts()
        x = counts.index
        y = counts.values
        axs[0].bar(x + offsets[i], y, width=0.2, color=colors[i], align='center', label=character)
    axs[0].legend(loc='upper right')

    axs[1].set_title('5 categories, relative')
    axs[1].set_xticks(ticks=[1, 2, 3, 4, 5], labels=long_labels)
    axs[1].yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))
    offsets = -0.2, 0, 0.2
    colors = 'b', 'g', 'r'
    for i, character in enumerate(bot_characters):
        data = df[df['bot character'] == character][question]
        counts = data.value_counts()
        x = counts.index
        y = list(map(lambda v: v / sum(counts.values), counts.values))
        axs[1].bar(x + offsets[i], y, width=0.2, color=colors[i], align='center', label=character)
    axs[1].legend(loc='upper left')

    axs[2].set_title('3 categories, absolute')
    axs[2].set_xticks(ticks=[2, 3, 4], labels=['disagree', 'neutral', 'agree'])
    offsets = -0.2, 0, 0.2
    colors = 'b', 'g', 'r'
    for i, character in enumerate(bot_characters):
        data = df[df['bot character'] == character][question]
        data = data.apply(lambda v: min(4, max(2, v)))
        counts = data.value_counts()
        x = counts.index
        y = counts.values
        axs[2].bar(x + offsets[i], y, width=0.2, color=colors[i], align='center', label=character)
    axs[2].legend(loc='upper right')

    axs[3].set_title('3 categories, relative')
    axs[3].set_xticks(ticks=[2, 3, 4], labels=['disagree', 'neutral', 'agree'])
    axs[3].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    offsets = -0.2, 0, 0.2
    colors = 'b', 'g', 'r'
    for i, character in enumerate(bot_characters):
        data = df[df['bot character'] == character][question]
        data = data.apply(lambda v: min(4, max(2, v)))
        counts = data.value_counts()
        x = counts.index
        y = list(map(lambda v: v / sum(counts.values), counts.values))
        axs[3].bar(x + offsets[i], y, width=0.2, color=colors[i], align='center', label=character)
    axs[3].legend(loc='upper left')

    fig.savefig('plots/humanness.png', transparent=False, dpi=80, bbox_inches="tight")
    print(f'Perceived humanness plots saved to plots/humanness.png')

    print('Correlation between trust change to this bot and trust change to all robots:')
    print(df['∆trust bot'].corr(df['∆trust general']))

    # confusion matrix for bot trust change -> general trust change
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(3, 3))
    specific = df['∆trust bot']
    general = df['∆trust general']

    # print(specific.array)
    # print(general.array)
    # y_test = np.array([1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
    # predic = np.array([1, 2, 4, 3, 5, 1, 2, 4, 3, 5, 1, 2, 3, 4, 4])

    # columns = ['class %s' % (i) for i in list(ascii_uppercase)[0:len(np.unique(y_test))]]

    confm = confusion_matrix(specific, general)
    df_cm = pd.DataFrame(confm, index=[-1,0,1], columns=[-1,0,1])

    ax = sn.heatmap(df_cm, ax=ax, cmap='Oranges', cbar=False, annot=True, square=True)
    ax.yaxis.set_tick_params(rotation=0)
    ax.invert_yaxis()
    ax.set_ylabel('∆ trust bot')
    ax.set_xlabel('∆ trust general')
    fig.savefig('plots/confusion.png', transparent=False, dpi=80, bbox_inches="tight")
    print(f'Confusion matrix saved to plots/confusion.png')

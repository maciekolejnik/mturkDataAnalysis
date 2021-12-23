import matplotlib.pyplot as plt
import analyse.aux as aux
import scipy.stats as st
import pandas as pd
from scipy.stats import wilcoxon, mannwhitneyu


def report(df):
    # First compare all predictions globally
    compare_all_predictors(df)

    # now zoom in on how our model's predictions differ between
    # prior conditions
    evaluate_our_predictor(df)


def evaluate_our_predictor(df):
    filename = 'plots/preds-eval-priors.png'
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(24, 8))
    priors = ['informed', 'uniform']
    prior_labels = ['ɪɴꜰᴏʀᴍᴇᴅ', 'ᴜɴɪꜰᴏʀᴍ']
    roles = ['investor', 'investee']

    df_by_prior = [df[df['prior'] == prior]['csmg'] for prior in priors]
    aux.boxplot(df_by_prior, prior_labels, axs[0], 'all data', test_normal=False)
    print('Testing our predictor on all data between various priors')
    print('Mann Whitney U rank test:')
    print(mannwhitneyu(df_by_prior[0], df_by_prior[1]))
    for i, d in enumerate(df_by_prior):
        print(f'{priors[i]}:')
        print(d.describe(percentiles=[.1, .18, .19, .2, .25, .5, .75]))
    # print(st.ttest_ind(*df_by_prior))

    # df_by_role = [df[df['bot role'] == role]['csmg'] for role in roles]
    # aux.boxplot(df_by_role, roles, axs[1], 'all data')
    # print('Testing our predictor on all data between various roles')
    # print(st.ttest_ind(*df_by_role))

    # restrict to data under undisclosed horizon
    undish = df.loc[lambda f: f['horizon'] == 'undisclosed']
    undisclosed_horizon_by_prior = [undish[undish['prior'] == prior]['csmg'] for prior in priors]
    aux.boxplot(undisclosed_horizon_by_prior, prior_labels, axs[2], 'only undisclosed')
    print('Testing our predictor on undisclosed horizon data between various priors')
    print('Mann Whitney U rank test:')
    print(mannwhitneyu(undisclosed_horizon_by_prior[0], undisclosed_horizon_by_prior[1]))
    for i, d in enumerate(undisclosed_horizon_by_prior):
        print(f'{priors[i]}:')
        print(d.describe(percentiles=[.1, .18, .19, .2, .25, .5, .75]))
    # print(st.ttest_ind(*undisclosed_horizon_by_prior))
    fig.savefig(filename, transparent=False, dpi=80, bbox_inches="tight")
    print(f'Saved plots for pred evals by prior to {filename}')


def compare_all_predictors(df):
    print('Comparing all predictors...')
    predictors = ['csmg', 'dang', 'uniform', 'avg', 'last']
    predictor_labels = ['ᴄsᴍɢ', 'ᴅᴀɴɢ', 'ᴜɴɪғᴏʀᴍ', 'ᴀᴠɢ', 'ʟᴀsᴛ']
    filename = "plots/preds-eval-all.png"
    fig, axs = plt.subplots(nrows=1, ncols=4, figsize=(32, 8))
    for ax in axs:
        ax.set_ylabel("MSE")

    data_subsets = {
        'all': df,
        'informed': df[df['prior'] == 'informed'],
        'undisclosed': df[df['horizon'] == 'undisclosed'],
        'informed + undisclosed': df[(df['horizon'] == 'undisclosed') & (df['prior'] == 'informed')]
    }

    print(df[['bot role', 'horizon', 'prior', 'last transfer prop', 'csmg', 'dang', 'investments', 'returns']].sort_values(
        by='csmg', ascending=False).head(20))
    print(df[['bot role', 'horizon', 'prior', 'earned human', 'earned bot', 'investments', 'returns']].sort_values(
        by='earned bot', ascending=True).head(20))
    print(df[['bot role', 'horizon', 'prior', 'earned human', 'earned bot', 'investments', 'returns']].sort_values(
        by='earned human', ascending=True).head(20))
    print(df[(df['bot character'] == 'greedy')][['bot character','bot role', 'horizon', 'earned human',
                'earned bot', 'investments', 'returns', 'feedback']].sort_values(
        by='bot role', ascending=True).head(30))
    print(df[(df['bot character'] == 'greedy') & (df['bot role'] == 'investee')][['bot character',
            'bot role', 'horizon', 'earned human', 'earned bot', 'investments', 'returns']].sort_values(
        by='bot role', ascending=True).describe())
    print(df[['earned human', 'earned bot']].describe(percentiles=[.1,.25,.5, .75, .8,.85,.9,.95]))

    print('investor earnings:')
    print(pd.concat([df[df['bot role'] == 'investor']['earned bot'],
                                       df[df['bot role'] == 'investee']['earned human']]).describe())
    print('investee earnings:')
    print(pd.concat([df[df['bot role'] == 'investor']['earned human'],
                     df[df['bot role'] == 'investee']['earned bot']]).describe())
    exit(1)

    for i, (name, subset) in enumerate(data_subsets.items()):
        print(f'\n\nConsider {name} data'.upper())
        for p in predictors:
            print(f'Summary of {p} predictions:')
            print(subset[p].describe(percentiles=[.1, .25, .5, .75]))
        subset_by_predictor = [subset[predictor] for predictor in predictors]
        aux.boxplot(subset_by_predictor, predictor_labels, axs[i], f'{name} data', test_normal=False)
        for i,j in [(i, j) for i in range(5) for j in range(5) if i < j]:
            print(f'Comparing {predictors[i]} to {predictors[j]} using Wilcox test:')
            print(wilcoxon(subset_by_predictor[i], subset_by_predictor[j]))

    fig.savefig(filename, transparent=False, dpi=80, bbox_inches="tight")
    print(f'Saved plots for all pred evals to {filename}')

    # 'competition'
    measures = 'mean', '50%', 'std'
    scores = {
        pred: {'mean': 0, '50%': 0, 'std': 0} for pred in predictors
    }
    df = df[df['prior'] == 'informed']
    for _ in range(10):
        subset = df.sample(20)
        summaries = [subset[pred].describe() for pred in predictors]
        for measure in measures:
            # get index of max value of measure
            statistics = [summary[measure] for summary in summaries]
            best_pred = predictors[statistics.index(min(statistics))]
            scores[best_pred][measure] += 1

    print(scores)



import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


FILENAME_MONEY_REQ = 'plots/money-request.png'
FILENAME_TIMINGS = 'plots/preq-timings.png'

# SIDE = 4
NROWS = 8
NCOLS = 10

# answers_df contains answers to all preQ questions for each participant
# (so its a df indexed by user_id with columns: altruism, lottery1, .. etc
# timings_df has the same index but only four columns:
# - bot took - array of bot thinking times
# - human took - same for human
# - preQ events - list of events (start, moneyRequest, lottery1 etc)
# - preQ time series - timing of the events above (same length as events)
def report(answers_df, timings_df):
    # report results to 11-20 game
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))
    counts = answers_df['money request'].value_counts().sort_index()
    print(counts)
    x = counts.index
    y = counts.values
    possible_answers = range(11,21)
    ax.set_xticks(ticks=possible_answers)
    yticks = range(0, 30, 4)
    ylabels = [f'{n} ({int(n*10/8)}%)' for n in yticks]
    ax.set_yticks(ticks=yticks, labels=ylabels)
    # ax.set_title('Distribution of answers to 11-20 money request game')
    ax.bar(x, y, alpha=0.5, color='b', label='our results')
    expected_pc = 4, 0, 3, 6, 1, 6, 32, 30, 12, 6
    expected = pd.Series(expected_pc) * (8/10)
    ax.bar(x, expected, alpha=0.5, width=0.4, fill=False, hatch='//', label='expected [Arad]')
    ax.legend(loc='upper left')
    fig.savefig(FILENAME_MONEY_REQ, transparent=False, dpi=80, bbox_inches="tight")
    print(f'11-20 money request plots saved to {FILENAME_MONEY_REQ}')

    # plot time series
    # timings is a dictionary keyed by user_id with { time_series, events} values
    config = {
        'start': ['magenta', 1],
        'moneyRequest': ['blue', 2],
        'lottery1': ['cyan', 3],
        'lottery2': ['green', 4],
        'lottery3': ['yellow', 5],
        'trust': ['orange', 6],
        'altruism': ['red', 7],
        'submit': ['grey', 8]
    }
    labels = ['reading', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'submit']
    # timings_list = list(timings_df.values())
    # random.shuffle(timings_list)
    nplots = NROWS * NCOLS
    # selected_timings = timings_list[:nplots]
    selected_timings = timings_df.sample(nplots)
    fig, axs = plt.subplots(nrows=NROWS, ncols=NCOLS, figsize=(NCOLS*6, NROWS*6))
    for user_id, timing in selected_timings.iterrows():
        index = selected_timings.index.get_loc(user_id)
        i = index // NCOLS
        j = index % NCOLS
        ax = axs[i, j]
        time_series = timing['preQ time series']
        events = timing['preQ events']
        ax.set_yticks(range(1, 9), labels=labels)
        ax.set_ylim(bottom=0, top=9)
        total_duration = time_series[-1]
        ax.set_xticks([0, total_duration], labels=['0', str(int(total_duration))])
        ax.set_xlim(left=0, right=total_duration)
        ax.set_xlabel('time (sec)')
        prev_click_time = 0.0
        for i in range(0, len(time_series)):
            click_time = time_series[i]
            name = events[i]
            color, y = config[name]
            xmin = prev_click_time / total_duration
            xmax = click_time / total_duration
            ax.axhline(y=y, xmin=xmin, xmax=xmax, color=color, lw=4)
            duration = int(click_time - prev_click_time)
            ha = 'left' if i==0 else 'right' if i + 1 == len(time_series) else 'center'
            xmid = (prev_click_time + click_time) / 2
            ax.text(xmid, y + 0.1, str(duration), ha=ha, va='bottom')
            prev_click_time = click_time

    fig.savefig(FILENAME_TIMINGS, transparent=False, dpi=80, bbox_inches="tight")
    print(f'Pre-questionnaire answers timing plots saved to {FILENAME_TIMINGS}')

    # analyse total time spend on pre questionnaire
    print('Total time spent completing pre game questionnaire (reading time excluded):')
    submit_times = timings_df['preQ time series'].apply(lambda ts: ts[-1] - ts[0])
    pruned = submit_times[submit_times < 1000]
    print(pruned.describe())
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 2))
    ax.boxplot(pruned, showfliers=False, showmeans=True, vert=False, widths=0.5)
    ax.axvline(105, ls='--')
    ax.set_yticks(ticks=[])
    x = np.random.normal(1, 0.08, size=len(pruned))
    ax.scatter(x=pruned, y=x, c='y', alpha=0.2)
    fig.savefig('plots/preQ_times.png', transparent=False, dpi=80, bbox_inches="tight")

    # analyse time spend on Q1 as prop of total
    print('time spend on Q1 as prop of total')
    time_props = timings_df['preQ time series'].apply(lambda ts: (ts[1] - ts[0]) / (ts[-1] - ts[0]))
    # pruned = submit_times[submit_times < 1000]
    print(time_props.describe())
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 2))
    ax.boxplot(time_props, showfliers=False, showmeans=True, vert=False, widths=0.5)
    ax.axvline(.238, ls='--')
    ax.set_yticks(ticks=[])
    x = np.random.normal(1, 0.08, size=len(time_props))
    ax.scatter(x=time_props, y=x, c='y', alpha=0.2)
    fig.savefig('plots/preQ_time_props.png', transparent=False, dpi=80, bbox_inches="tight")

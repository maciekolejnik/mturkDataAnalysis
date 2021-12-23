import random
import pandas as pd

def report(coredf, auxdf):
    auxdf['bot took max'] = auxdf['bot took'].apply(lambda ts: max(ts))
    bot_thinking_times = pd.Series([t for ts in auxdf['bot took'] for t in ts], name='tt')
    print('__________')
    print('| TIMINGS |')
    print('‾‾‾‾‾‾‾‾‾‾')
    print('Summary of bot thinking times:')
    print(bot_thinking_times.describe(percentiles=[.25, .5, .75, .8, .9, .95, .98, .99]))
    print('How many are at least 30?')
    print(bot_thinking_times.to_frame().query('tt >= 30'))
    # print(auxdf['bot took max'].describe())
    # print(auxdf['bot took max'].sort_values().tail(5))
    return True
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
    timings_list = list(timings.values())
    random.shuffle(timings_list)
    nplots = pow(SIDE, 2)
    selected_timings = timings_list[:nplots]
    fig, axs = plt.subplots(nrows=SIDE, ncols=SIDE, figsize=(SIDE * 6, SIDE * 6))
    for index, timing in enumerate(selected_timings):
        i = index // SIDE
        j = index % SIDE
        ax = axs[i, j]
        time_series = timing['time_series']
        events = timing['events']
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
            print(f'iteration {i}: {xmin}, {xmax}')
            ax.axhline(y=y, xmin=xmin, xmax=xmax, color=color, lw=4)
            duration = int(click_time - prev_click_time)
            ha = 'left' if i == 0 else 'right' if i + 1 == len(time_series) else 'center'
            xmid = (prev_click_time + click_time) / 2
            ax.text(xmid, y + 0.1, str(duration), ha=ha, va='bottom')
            prev_click_time = click_time

    fig.savefig(FILENAME_TIMINGS, transparent=False, dpi=80, bbox_inches="tight")
    print(f'Bot character plots saved to {FILENAME_TIMINGS}')
import numpy as np
from scipy.stats import shapiro, normaltest, anderson, kstest


def boxplot(data, labels, ax, title, test_normal=False, overlay_data=True):
    ax.boxplot(data, labels=labels, showfliers=False, showmeans=True)
    for index, label in enumerate(labels):
        y = data[index]
        if test_normal:
            print('\nTesting normality of data to be plotted:')
            for name, test in [('Shapiro', shapiro), ('D\'Agostino', normaltest)]:
                stat, p = test(y)
                intro = f'According to {name} test, data labelled {label}'
                print(f'{intro} looks normal (p = {p})') if p > 0.05 \
                    else print(f'{intro} does not seem normal; p = {p}')
            result = anderson(y)
            print(f'Anderson test result: {result}')
            result = kstest(y, 'norm')
            print(f'Kolmogorov-Smirnov test result: {result}')
        if overlay_data:
            x = np.random.normal(index + 1, 0.04, size=len(y))
            ax.scatter(x=x, y=y, c='y', alpha=0.2)
    # ax.set_title(title)

import statistics as stats

# 1. how does horizon (disclosed vs undisclosed) affect last return proportion
#    compute mean and standard deviation of last transfer proportion in both cases


# pre: last investment is non zero
def get_last_return_prop(play):
    last_round = play.get('history')[-1]
    return last_round.get('returned') / last_round.get('invested')


def get_last_return_props(plays):
    participant_as_investee = \
        filter(lambda play: play.get('role') == 'investee', plays)
    last_invest_not_zero = \
        filter(lambda play: play.get('history')[-1].get('invested') > 0,
               participant_as_investee)
    return_props = list(map(get_last_return_prop, last_invest_not_zero))
    return return_props


def describe_last_return_prop(plays):
    participant_as_investee = \
        filter(lambda play: play.get('role') == 'investee', plays)
    last_invest_not_zero = \
        filter(lambda play: play.get('history')[-1].get('invested') > 0, participant_as_investee)
    return_props = list(map(get_last_return_prop, last_invest_not_zero))
    if len(return_props) == 0:
        return {
            'error': "no data"
        }
    return {
        'mean': stats.mean(return_props),
        'stdev': stats.stdev(return_props),
        'size': len(return_props)
    }


# 2. how does prior affect prediction quality
#    compute mean and stdev of PMSE in informed vs uninformed prior conditions


# 3. how do our predictions compare with other methods
#    list means and stdevs of all predictions methods


# 4. how does 'personality' of the bot affect the outcome, measured
#    by fairness (distribution of income) and social welfare (total income)
#    in the game. Again, we summarise it with a mean and stdev.
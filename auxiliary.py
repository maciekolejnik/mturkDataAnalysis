import statistics as stats


def other_role(role):
    return 'investee' if role == 'investor' else 'investor'


def compute_earned(history):
    investor = 0
    investee = 0
    for play_round in history:
        invested = play_round.get('invested')
        returned = play_round.get('returned')
        investor += 4 - invested + returned
        investee += 2 * invested - returned
    return {
        'investor': investor,
        'investee': investee
    }


def print_summary(user_id, condition):
    horizon = 'disclosed' if condition.get("horizonDisclosed") else 'undisclosed'
    bot_character = ["selfless", "neutral", "greedy"][condition.get("botCoeffs")]
    prior = 'informed' if condition.get("prior") else 'uninformed'
    bot_human = ['strongly disagrees', 'disagrees', 'neither agrees, nor disagrees',
                 'agrees', 'strongly agrees'][post_questionnaire.get("human") - 1]
    print(f'*-------- User {user_id} --------*')
    print(f'He played as {condition.get("role")} with {horizon} horizon' +
          f' against {bot_character} bot with {prior} prior')
    print(f'He earned {earned_human} units')
    print(f'Here is how the game went')
    for play_round in condition.get('history'):
        print(f'{play_round.get("invested")} {play_round.get("returned")}')
    print(f'Participant {bot_human} that bot played like a human')


def assign_play_prior(play_info, prior, initial_state, plays):
    if prior:
        play_info_copy = dict(play_info)
        play_info_copy.update({
            'prior': {
                'belief': initial_state.get('belief'),
                'metaParams': initial_state.get('metaParamsEstimations'),
                'trust': initial_state.get('trust')
            }
        })
        plays.get('informed').append(play_info_copy)
    else:
        plays.get('uninformed').append(play_info)


def assign_play_character(play_info, bot_coeffs, plays):
    if bot_coeffs == 0:
        plays.get('selfless').append(play_info)
    elif bot_coeffs == 1:
        plays.get('neutral').append(play_info)
    else:
        plays.get('greedy').append(play_info)


def assign_play_horizon(play_info, horizon, plays):
    plays.get('disclosed').append(play_info) if horizon else \
        plays.get('undisclosed').append(play_info)


def describe(array):
    return {
        'mean': stats.mean(array),
        'stdev': stats.stdev(array)
    }


# returns a string with mean and stdev of array
def summarise(array):
    return f'Mean: {stats.mean(array)}, stdev: {stats.stdev(array)}'

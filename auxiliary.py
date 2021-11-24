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

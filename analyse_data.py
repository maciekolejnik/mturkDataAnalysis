from google.cloud import firestore
import statistics as stats
# import numpy as np
import auxiliary as aux
import data_description as data_desc

# STEP 1: retrieve plays from the database
db = firestore.Client()
# use appropriate HIT ID below
plays_collection = db.collection(u'3OID399FYLWUQQPLVJ2GZE4HBI1FD4')

# print some basic numerical info about the data
# (how many passed comprehension check, how many got approved etc)
print(f'There were {len(list(plays_collection.stream()))} plays recorded.')

# order_by not only orders but also filters on existence
approved_assignments_ref = plays_collection.order_by(u'approved')
print(f'Out of these, {len(list(approved_assignments_ref.stream()))}'
      f' submitted an assignment which got approved.')

comprehension_passed_ref = \
    approved_assignments_ref.where(u'comprehension', u'array_contains', 684)
print(f'Out of these, {len(list(comprehension_passed_ref.stream()))}'
      f' participants passed the comprehension check.')

completed_game_ref = comprehension_passed_ref.order_by(u'earned')
print(f'Out of these, {len(list(completed_game_ref.stream()))}'
      f'participants completed the game and gave us useful data points.')

# STEP 1a: we create lists to categorise data for different TREATMENTS
# the FACTORS are as follows:
# 1. bot character: greedy (-1), neutral (0), selfless (1)
# 2. prior: uninformed (0), informed (1)
# 3. horizon: undisclosed (0), disclosed (1)
# 4. role of human: investor (0), investee (1)


# 1. first thing we wanna measure is how having a prior affects the prediction
# we therefore categorise plays based on whether prior was informed or not
# and for each play we store 
# - the history of play (*history*)
# - role of participant (*role*)
# - the prior (if applicable) consisting of 
#    -- belief + metaParamsEstimations + trust (*prior*)
# each play is stored as a dict with keys denoted by *<key>* above
# Apart from evaluating predictions in both cases we also study social welfare 
prior_informed = []
prior_uninformed = []


# 2. second thing we wanna measure is how bot's character (i.e. its goal coeffs)
# affects the outcome, in particular:
# - participant's perception of bot's "humanness"
# - average bot's income (as investor, as investee)
# - average participant's income (as investor, as investee)
# - participant's trust change 
# We therefore store plays in three different arrays and store following 
# play objects:
# { history, human, trustChange}
# incomes can be computed based on the history
greedy_plays = []
neutral_plays = []
selfless_plays = []

# 3. third thing we wanna measure is how much defection is there 
# when horizon is disclosed. we're particularly interested in the 
# case when participant is the investee and the last transfer
# we therefore store each play as following dict:
# { history, role}
horizon_disclosed = []
horizon_undisclosed = []

# STEP 2
# iterate over useful plays, print a summary of each
# and generate output CSV files in the meantime
completedPlays = list(completed_game_ref.stream())
print('Here is a summary of completed plays:')
# iterate over approved plays
for full_play in completedPlays:
    # for each play we print its summary
    print(f'*-------- User {full_play.id} --------*')
    play_dict = full_play.to_dict()
    # retrieve top level stuff
    condition = play_dict.get('condition')
    bot_setup = play_dict.get('botSetup')
    pre_questionnaire = play_dict.get('preQuestionnaire')
    post_questionnaire = play_dict.get('postQuestionnaire')
    humanness = post_questionnaire.get("human")  # 1-5 where 1=compl disagree
    trust_change = post_questionnaire.get("trustChange") - 1  # -1-1 where -1=decreased
    history = play_dict.get('history')
    earned = aux.compute_earned(history)  # playDict.get("earned") TODO: use this later
    initial_state = bot_setup.get('initialState')
    bot_coeffs = condition.get("botCoeffs")
    role = condition.get("role")

    earned_human = earned.get(role)
    earned_bot = earned.get(aux.other_role(role))
    # interpret lower level stuff
    horizon = 'disclosed' if condition.get("horizonDisclosed") else 'undisclosed'
    bot_character = ["selfless", "neutral", "greedy"][bot_coeffs]
    prior = 'informed' if condition.get("prior") else 'uninformed'

    bot_human = ['strongly disagrees', 'disagrees', 'neither agrees, nor disagrees',
                 'agrees', 'strongly agrees'][humanness - 1]
    # print summary
    print(f'He played as {role} with horizon {horizon}' +
          f' against {bot_character} bot with {prior} prior')
    print(f'He earned {earned} units')
    print(f'Here is how the game went')
    for play_round in history:
        print(f'{play_round.get("invested")} {play_round.get("returned")}')
    print(f'Participant {bot_human} that bot played like a human')

    # code below generates csv file for measuring social welfare, fairness
    # under different conditions

    # first record values of outcome variables, i.e.
    # - social welfare (combined earnings of both players)
    # - fairness (earnings of bot / earnings of human - 1)
    # - human's perceived 'humanness' of bot
    # - human's trust change towards bot
    socialWelfare = earned_human + earned_bot
    fairness = earned_human / earned_bot - 1  # as above
    # humanness already retrieved
    # trustChange already retrieved

    # generate csv line in format
    # - prior (0=informed, 1=uninformed)

    # another csv for comparing

    # 1. assign play based on prior
    prior_play = {
        'history': history,
        'role': role,
    }

    if prior == 'informed':
        prior_informed.append(prior_play.update({
            'prior': {
                'belief': initial_state.get('belief'),
                'metaParams': initial_state.get('metaParamsEstimations'),
                'trust': initial_state.get('trust')
            }
        }))
    else:
        prior_uninformed.append(prior_play)

    # 2. assign play based on bot coeffs
    botCoeffsPlay = {
        'history': history,
        'human': pre_questionnaire.get('human'),
        'trustChange': pre_questionnaire.get('trustChange')
    }
    if bot_coeffs == 0:
        selfless_plays.append(botCoeffsPlay)
    elif bot_coeffs == 1:
        neutral_plays.append(botCoeffsPlay)
    else:
        greedy_plays.append(botCoeffsPlay)

    # 3. assign play based on horizon
    if horizon == 'disclosed':
        horizon_disclosed.append(prior_play)
    else:
        horizon_undisclosed.append(prior_play)

# We have now categorised the data and generated CSV file containing
# controlled variables and response variables

# Below we gather some descriptive statistics from the data:

# how does last return differ between horizon conditions
disclosed_stats = data_desc.describe_last_return_prop(horizon_disclosed)
undisclosed_stats = data_desc.describe_last_return_prop(horizon_undisclosed)

disclosed_desc = 'no data' if 'error' in disclosed_stats else \
    f'mean={disclosed_stats.get("mean")}, stdev={disclosed_stats.get("stdev")}'
undisclosed_desc = 'no data' if 'error' in undisclosed_stats else \
    f'mean={undisclosed_stats.get("mean")}, stdev={undisclosed_stats.get("stdev")}'

print(f'Return proportion when horizon disclosed: {disclosed_desc}')
print(f'Return proportion when horizon undisclosed: {undisclosed_desc}')


# make it very explicit for horizon disclosed condition

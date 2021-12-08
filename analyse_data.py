import statistics as stats
import auxiliary as aux
import evaluate_predictors as pred_eval
import data_description as data_desc
import re
import matplotlib.pyplot as plt

from retrieve_data import DataSource, get_data, get_evals

# 'ARGUMENTS' (should be passed on cmd line but oh well)
PRINT_SUMMARIES = False
WRITE_FILE = False
HIT_ID = u'3HJ1EVZS3T8TBOSXTPWY3UWPO5NR34'
DATA_FILENAME = 'firstStudyBackup.json'
EVALS_FILENAME = 'firstStudyBackupEvals.json'
DATA_SOURCE = DataSource.FILE

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
plays_by_prior = {
    'informed': [],
    'uninformed': []
}


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
plays_by_bot_character = {
    'selfless': [],
    'neutral': [],
    'greedy': []
}
# greedy_plays = []
# neutral_plays = []
# selfless_plays = []

# 3. third thing we wanna measure is how much defection is there 
# when horizon is disclosed. we're particularly interested in the 
# case when participant is the investee and the last transfer
# we therefore store each play as following dict:
# { history, role}
plays_by_horizon = {
    'disclosed': [],
    'undisclosed': []
}
# horizon_disclosed = []
# horizon_undisclosed = []

if WRITE_FILE:
    first_line = True
    csv_file = open('trust-game-robot.csv', 'w')

# STEP 2
# iterate over useful plays, print a summary of each
# and generate output CSV files in the meantime
completed_plays = get_data(HIT_ID, DATA_FILENAME, DATA_SOURCE)
PRINT_SUMMARIES and print('Here is a summary of completed plays:')
feedbacks = {}
preds_evals = {}
# iterate over approved plays
for user_id, play_dict in completed_plays.items():
    # play_dict = full_play.to_dict()
    # user_id = full_play.id
    # 1. retrieve top level stuff for easier access
    condition = play_dict.get('condition')
    bot_setup = play_dict.get('botSetup')
    pre_questionnaire = play_dict.get('preQuestionnaire')
    post_questionnaire = play_dict.get('postQuestionnaire')
    history = play_dict.get('history')
    earned = play_dict.get("earned")
    feedback = play_dict['feedback']

    # 2. retrieve some lower level stuff
    initial_state = bot_setup.get('initialState')
    bot_coeffs = condition.get("botCoeffs")
    role = condition.get("role")
    horizon = condition['horizonDisclosed']
    earned_human = earned.get(role)
    earned_bot = earned.get(aux.other_role(role))

    # 3. print summary if needed
    PRINT_SUMMARIES and aux.print_summary(user_id, condition)

    # 4. Record outcome variables for this play
    # 4a. simple ones
    socialWelfare = earned_human + earned_bot
    fairness = (earned_human - earned_bot) / (
                earned_human + earned_bot)  # as above
    humanness = post_questionnaire.get("human")  # 1-5 where 1=compl disagree
    trust_change_general = post_questionnaire.get(
        "trustGeneral") - 1  # -1-1 where -1=decreased
    trust_change_specific = post_questionnaire.get(
        "trustSpecific") - 1  # -1-1 where -1=decreased
    # 4b. predictions
    # get evaluations computed in webppl for our predictor
    pred_evaluations = get_evals(HIT_ID, EVALS_FILENAME, DATA_SOURCE)
    # as a dict { user_id : { 'predictions' : {'fses': [list], 'pmses': [list], 'mses': [list]}}
    csmg_evals = pred_evaluations.get(user_id).get('predictions')
    evals = {
        'csmg': {
            'pmse': stats.mean(csmg_evals.get('pmses')),
            'mse': stats.mean(csmg_evals.get('mses')),
            'fse': stats.mean(csmg_evals.get('fses'))
        },
        'uniform': pred_eval.evaluate_uniform_predictor(history, role),
        'dang': pred_eval.evaluate_dang_predictor(history, role)
    }
    preds_evals[user_id] = evals

    # 4. generate a line of output csv file (if needed).
    if WRITE_FILE:
        # This line stores
        # - factors
        # - outcome variables
        # In particular, this is the format:
        # pr,hor,bc,r,f,tw,hum,stc,gtc
        # \       /\                  /
        #  factors   outcome variables
        #
        # where:
        # - pr=prior (0=uninformed, 1=informed)
        # - hor=horizon (0=undisclosed, 1=disclosed)
        # - bc=bot character (0=selfless, 1=neutral, 2=greedy)
        # - r=participant's role (0=investor, 1=investee)
        # - f=fairness (float in [-1,1])
        # - tw = total welfare (int in [28,56])
        # - hum = humanness of the bot as perceived by participant
        #     (1=compl disagree, 5=compl agree)
        # - stc = specific (for bot) trust change (-1=decreased, 1=increased)
        # - gtc = general (for all robots) trust change (-1=decreased, 1=increased)
        # TODO: include predictions evaluations here

        # 4a. factors
        pr = int(condition.get('prior'))
        hor = int(condition.get('horizonDisclosed'))
        bc = bot_coeffs
        r = int(condition.get('role') == 'investee')

        # 4b. outcome variables
        f = fairness
        tw = socialWelfare
        hum = humanness
        stc = trust_change_specific
        gtc = trust_change_general
        line = f'{pr},{hor},{bc},{r},{f:.2f},{tw},{hum},{stc},{gtc}'
        first_line or csv_file.write('\n')
        csv_file.write(line)
        first_line = False

    # 5. assign play to various buckets for descriptive statistics
    base_play_info = {
        'history': history,
        'role': role,
        'fairness': fairness,
        'total_welfare': socialWelfare,
        'humanness': humanness,
        'trust_specific': trust_change_specific,
        'trust_general': trust_change_general,
        'prediction_evaluations': evals
    }
    aux.assign_play_prior(dict(base_play_info), condition.get('prior'),
                          initial_state, plays_by_prior)
    aux.assign_play_character(
        dict(base_play_info), bot_coeffs, plays_by_bot_character)
    aux.assign_play_horizon(dict(base_play_info), horizon, plays_by_horizon)

    # 6. retrieve feedback if present
    trimmed = re.sub('[.]', '', feedback.lower())
    if len(trimmed) > 0 and \
            (trimmed not in ['none', 'n', 'n/a', 'nope', 'no', 'no feedback']):
        bot_character = ["selfless", "neutral", "greedy"][bot_coeffs]
        hor = 'disclosed' if horizon else 'undisclosed'
        feedback_message = \
            f'user {user_id} (played as {role} with {hor} horizon against ' \
            f'{bot_character} bot):\n\t{feedback}'
        feedbacks[user_id] = feedback_message

# We have now categorised the data and generated CSV file containing
# controlled variables and response variables
if WRITE_FILE:
    csv_file.close()

# Below we gather some descriptive statistics from the data:
print('Here are some descriptive statistics:')
counter = 1

# 1. How does last return differ between horizon conditions
# fig = plt.figure(figsize=(10, 7))
data = []
print(f'{counter}. '
      'First, we analyse how the proportion of last return of a participant '
      'depends on whether they know that the game lasts for 7 rounds. Hence '
      'we only consider plays in which the participant plays as investee '
      '(player 2) and where last investment of the bot (in round 7) is '
      'nonzero. The proportion refers to the ratio of the amount participant '
      'returned to the amount the bot invested. The results are as follows:')
for horizon_cond in ['disclosed', 'undisclosed']:
    return_props = data_desc.get_last_return_props(
        plays_by_horizon[horizon_cond])
    print(f'Return proportion when horizon {horizon_cond} (based on '
          f'{len(return_props)} participants): {aux.summarise(return_props)}')
    data.append(return_props)

# Creating plot
# plt.boxplot(data)
# show plot
# plt.show()

counter += 1
# 2. how do game outcomes, trust changes and perceived
# humanness depend on bot character?
print(f'\n{counter}. '
      'We analyse how the values of outcome variables (i.e., fairness, '
      'total welfare, [participant\'s perceived] humanness [of the bot], '
      'change of participant\'s trust towards the bot and change of '
      'participant\'s trust towards robots in general)')

print('Note that:')
print('- fairness is measured on a [-1, 1] scale where 0 represents a fair '
      'outcome (same earnings for both players), -1 means outcome that\'s '
      'completely unfair for the human (earned nothing) and 1 means the '
      'opposite. [Fairness is computed according to the following formula:')
print('fairness = (earned_human - earned_bot) / (earned_human + earned_bot)')
print(']')
print('- total welfare is simply sum of earnings of both players in the game '
      '(range [28-56]')
print('- humanness is measured on a scale 1 to 5 (only integers) where 5 '
      'means participant fully agrees bot played like a human and 1 means '
      'the opposite')
print('- trust changes are measured on a \'ternary\' scale {-1,0,1} where '
      '-1 = trust decrease, 0 = no change, 1 = trust increase')

# fig = plt.figure(figsize=(15, 3))
outcome_vars = ['fairness', 'total_welfare',
                'humanness', 'trust_specific', 'trust_general']
data = {var: [] for var in outcome_vars}
for character in ['selfless', 'neutral', 'greedy']:
    plays = plays_by_bot_character.get(character)
    print(f'\n{character} bot (based on {len(plays)} participants):\n' +
          '\t            mean | stdev\n')
    for outcome_var in outcome_vars:
        values = [play.get(outcome_var) for play in plays]
        desc = aux.describe(values)
        print(f'\t {outcome_var}: {desc["mean"]:+.2f} | '
              f'{desc["stdev"]:.2f}\n')
        data[outcome_var].append(values)

# for index, var in enumerate(outcome_vars):
#     plt.subplot(1, 5, index+1)
#     plt.gca().set_title(var)
#     plt.boxplot(data[var], labels=['selfless', 'neutral', 'greedy'])
# show plot
# plt.show()
counter += 1

print(f'\n{counter}. '
      f'We analyse how the quality of predictions, measured by PMSE '
      f'(probabilistic mean squared error) differs between the informed '
      f'vs uninformed prior treatments. The lower the value, the better:')
# 3. how does prior affect prediction quality
for prior in ['informed', 'uninformed']:
    plays = plays_by_prior.get(prior)
    pmses = [play['prediction_evaluations']['csmg']['pmse'] for play in plays]
    summary = aux.summarise(pmses)
    print(f'{prior} prior (based on {len(plays)} participants): {summary}')
counter += 1

# 4. any feedback left by users?
print(f'{counter}. Feedback left by users:')
for user_id, feedback in feedbacks.items():
    print(feedback)

# 5. analyse how participants answer pre game questions

# 6. compare evaluations
fig = plt.figure(figsize=(9, 3))

# evals = {
#     'csmg': {
#         'pmse': stats.mean(csmg_evals.get('pmses')),
#         'mse': stats.mean(csmg_evals.get('mses')),
#         'fse': stats.mean(csmg_evals.get('fses'))
#     },
#     'uniform': pred_eval.evaluate_uniform_predictor(history, role),
#     'dang': pred_eval.evaluate_dang_predictor(history, role)
# }

data = {}
for index, metric in enumerate(['pmse', 'mse', 'fse']):
    data[metric] = []
    for predictor in ['csmg', 'dang', 'uniform']:
        data[metric].append([pred_eval[predictor][metric]
                             for pred_eval in preds_evals.values()])
    plt.subplot(1, 3, index+1)
    plt.gca().set_title(metric)
    plt.boxplot(data[metric], labels=['our model', 'dang', 'uniform'])

plt.show()

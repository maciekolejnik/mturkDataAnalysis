import numpy as np

from retrieve_data import read_data_from_file, read_evals_from_file
import auxiliary as aux
import statistics as stats
import evaluate_predictors as pred_eval
import pandas as pd
import matplotlib.pyplot as plt
from analyse import demographics as dg
from analyse import pre_questionnaire as preq
from analyse import predictions as preds
from analyse import bot_character as bot_char
from analyse import opportunism as opp
from analyse import history as hist
import re

# this file retrieves the data stored in json format and generates a csv with
# info for statistical analysis

DATA_FILENAME = 'data/firstStudyBackup.json'
EVALS_FILENAME = 'data/firstStudyBackupEvals.json'
PRINT_FEEDBACKS = False
WRITE_CSV = False
REPORT_DEMOGRAPHICS = False
REPORT_PRE_QUESTIONNAIRE = False
REPORT_PREDICTIONS = False
REPORT_BOT_CHARACTER = True
REPORT_HUMAN_OPPORTUNISM = False
REPORT_HISTORY = False

completed_plays = read_data_from_file(DATA_FILENAME)
pred_evaluations = read_evals_from_file(EVALS_FILENAME)

demographics_labels = ['age', 'education', 'gender', 'nationality', 'robot exposure']
pre_questionnaire_labels = \
    ['altruism', 'lottery1', 'lottery2', 'lottery3', 'money request', 'trust']
treatments = ['bot character', 'horizon', 'prior', 'bot role']
actions = ['investments', 'returns']
outcome_vars = ['total welfare', 'fairness', 'last transfer prop', 'earned human', 'earned bot',
                'csmg', 'dang', 'uniform', 'last', 'avg']
post_questionnaire_labels = ['bot humanness', '∆trust bot', '∆trust general', 'feedback']
core_data_labels = demographics_labels + pre_questionnaire_labels + treatments + \
                   actions + outcome_vars + post_questionnaire_labels

aux_data_labels = ['bot took', 'human took', 'preQ events', 'preQ time series']
if WRITE_CSV:
    output_csv = open('trust-game-robot.csv', 'w')
    output_csv.write(','.join(core_data_labels))

core_data = {}
aux_data = {}
# preq_timings = {}
# histories = {}
# bot_roles = {}
feedbacks = {}
for user_id, play_dict in completed_plays.items():
    # 1. retrieve top level stuff for easier access
    condition = play_dict['condition']
    demographics = play_dict['demographic']
    bot_setup = play_dict['botSetup']
    pre_questionnaire = play_dict['preQuestionnaire']
    post_questionnaire = play_dict['postQuestionnaire']
    history = play_dict['history']
    earned = play_dict['earned']
    feedback = play_dict['feedback']

    # 2. retrieve some lower level stuff
    initial_state = bot_setup['initialState']
    bot_coeffs = condition['botCoeffs']
    human_role = condition['role']
    bot_role = aux.other_role(human_role)
    horizonDisclosed = condition['horizonDisclosed']
    priorInformed = condition['prior']
    earned_human = earned.get(human_role)
    earned_bot = earned.get(bot_role)

    # 3. game history
    investments = [r['invested'] for r in history]
    returns = [r['returned'] for r in history]
    # auxiliary data
    action_times = {
        player: [r['took'][player] for r in history] for player in ['bot', 'human']
    }
    # action_times = {
    #     'bot': [r['took']['bot'] for r in history],
    #     'human': [r['took']['human'] for r in history],
    # }
    preq_times = {
        'events': [e['event'] for e in pre_questionnaire['timeSeries']],
        'time_series': [float(e['elapsed']) for e in pre_questionnaire['timeSeries']]
    }

    # 4. outcome vars
    total_welfare = earned_human + earned_bot
    fairness = (earned_human - earned_bot) / (earned_human + earned_bot)
    prop = history[-1]['returned'] / history[-1]['invested'] if \
        history[-1]['invested'] > 0 else np.nan
    csmg = stats.mean(pred_evaluations[user_id]['predictions']['fses'])
    dang = pred_eval.evaluate_dang_predictor(history, human_role, user_id)['mse']
    uniform = pred_eval.evaluate_uniform_predictor(history, human_role)['mse']
    avg = pred_eval.evaluate_avg_predictor(history, human_role)['mse']
    last = pred_eval.evaluate_last_predictor(history, human_role)['mse']

    # 5. post questionnaire
    humanness = post_questionnaire.get("human")  # 1-5 where 1=compl disagree
    trust_change_general = post_questionnaire.get(
        "trustGeneral") - 1  # -1-1 where -1=decreased
    trust_change_specific = post_questionnaire.get(
        "trustSpecific") - 1  # -1-1 where -1=decreased

    # 6. treatment
    bc = ["selfless", "neutral", "greedy"][bot_coeffs]
    horizon = 'disclosed' if horizonDisclosed else 'undisclosed'
    prior = 'informed' if priorInformed else 'uniform'

    # here we collect all the data points
    core_data_points = list(demographics.values())
    core_data_points += list(pre_questionnaire['answers'].values())
    core_data_points += [bc, horizon, prior, bot_role]
    core_data_points += [investments, returns]
    core_data_points += [total_welfare, fairness, prop, earned_human,
                         earned_bot, csmg, dang, uniform, last, avg]
    core_data_points += [humanness, trust_change_specific, trust_change_general, feedback or '']

    aux_data_points = [*(action_times.values()), *preq_times.values()]

    core_data[user_id] = pd.Series(core_data_points, index=core_data_labels)
    aux_data[user_id] = pd.Series(aux_data_points, index=aux_data_labels)
    # histories[user_id] = history
    # time_series, events = zip(*[
    #     (float(e['elapsed']), e['event']) for e in pre_questionnaire['timeSeries']
    # ])
    # preq_timings[user_id] = {
    #     'time_series': time_series,
    #     'events': events
    # }
    # exit(1)
    # preq_timings[user_id] = pd.Series(pre_questionnaire['timeSeries'], index=)


    if WRITE_CSV:
        output_csv.write('\n')
        output_csv.write(','.join(core_data_points))

    if PRINT_FEEDBACKS:
        trimmed = re.sub('[.]', '', feedback.lower())
        if len(trimmed) > 0 and \
                (trimmed not in ['none', 'n', 'n/a', 'nope', 'no', 'no feedback']):
            bot_character = ["selfless", "neutral", "greedy"][bot_coeffs]
            # hor = 'disclosed' if horizon else 'undisclosed'
            feedback_message = \
                f'user {user_id} (played as {human_role} with {horizon} horizon against ' \
                f'{bot_character} bot):\n\t{feedback}'
            # feedback_message = f'\\{human_role}Sc & \\{horizon}Horizon & \\{bot_character}Bot & {feedback} \\\\'
            feedbacks[user_id] = feedback_message

WRITE_CSV and output_csv.close()

df = pd.DataFrame.from_dict(core_data, orient='index', columns=core_data_labels)
demdf = df[demographics_labels]
preqdf = df[pre_questionnaire_labels]
auxdf = pd.DataFrame.from_dict(aux_data, orient='index', columns=aux_data_labels)
    # pd.DataFrame.from_dict(
    # data[pre_questionnaire_labels], orient='index', columns=pre_questionnaire_labels)
print('Here is a sample of the data:')
print(df.head(3))

REPORT_DEMOGRAPHICS and dg.report(demdf.copy())
# REPORT_PRE_QUESTIONNAIRE and preq.report(preqdf.copy(), preq_timings)
REPORT_PRE_QUESTIONNAIRE and preq.report(preqdf.copy(), auxdf.copy())
REPORT_PREDICTIONS and preds.report(df.copy())
REPORT_BOT_CHARACTER and bot_char.report(df.copy())
REPORT_HUMAN_OPPORTUNISM and opp.report(df.copy())
REPORT_HISTORY and hist.report(df.copy(), auxdf.copy())

if PRINT_FEEDBACKS:
    print('Feedback left by users:')
    for user_id, feedback in feedbacks.items():
        print(feedback)

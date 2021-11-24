# below evaluation functions of various predictors.
# each takes two parameters:
# - history of play in the format { investments, returns }
# - role of the participant whose actions we wanna predict
# each returns a dict { mse, pmse }

# DANG - from the predicting trust game paper
def evaluate_dang_predictor(history, role):
    return {
        'mse': 1,
        'pmse': 1
    }


# UNIFORM - always predicts uniform
def evaluate_uniform_predictor(history, role):
    
    return {
        'mse': 1,
        'pmse': 1
    }

# LAST - predict next action is same as last (first one uniform)
def evaluate_last_predictor(history, role):
    return {
        'mse': 1,
        'pmse': 1
    }

# AVERAGE - predict next action is average of previous actions (first one uniform)
def evaluate_last_predictor(history, role):
    return {
        'mse': 1,
        'pmse': 1
    }

# RANDOM - predict next action by a random draw
def evaluate_random_predictor(history, role):
    return {
        'mse': 1,
        'pmse': 1
    }

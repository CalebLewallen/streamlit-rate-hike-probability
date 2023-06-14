import fed_funds_probability as ffp
import get_data as gd


def get_fomc_decision_data():
    """
    Returns 5 dataframes in a tuple: futures_data[0], meeting_data[1], complete_probability_tree[2], policy_moves[3], probabilty_tree_headers[4]
    """
    # Policy and market assumptions
    current_fed_funds = float(gd.get_effr())
    anticipated_policy_move = 0.25
    policy_move_threshold = 0.5

    # Pull in all of the necessary futures data to pass into calcualtions
    fomc_meetings = ffp.retrieve_fomc_meeting_dates()
    futures_data = ffp.import_futures_data()

    # Build the probability tables
    meeting_data = ffp.create_meeting_data_dataframe(futures_data, fomc_meetings, current_fed_funds)

    probability_events = ffp.build_probability_events(fomc_meetings, meeting_data, anticipated_policy_move)

    probability_tree_list = ffp.create_probability_tree(fomc_meetings, probability_events, anticipated_policy_move, current_fed_funds)[0]
    probability_tree_headers = ffp.create_probability_tree(fomc_meetings, probability_events, anticipated_policy_move, current_fed_funds)[1]
    probability_tree = ffp.create_probability_tree(fomc_meetings, probability_events, anticipated_policy_move, current_fed_funds)[2]

    complete_probability_tree = ffp.merge_probability_data(probability_events, probability_tree)

    policy_moves = ffp.anticipated_policy_moves(fomc_meetings, probability_tree_list, probability_tree_headers, policy_move_threshold)

    return futures_data, meeting_data, complete_probability_tree, policy_moves, probability_tree_headers
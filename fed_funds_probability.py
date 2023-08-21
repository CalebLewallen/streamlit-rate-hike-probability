import pandas as pd
import datetime as dt
import calendar as cal
import math
import get_data as gd


# Convert fomc_meetings string values into dates
def string_to_date_list_conversion(dateList):
    for date in range(len(dateList)):
        dateList[date] = dt.datetime.strptime(dateList[date], "%Y-%m-%d").date()
    return dateList

### SET UP CALCULATION VALUES ###
# current_fed_funds = 5.08 # This will need to be replaced by a request to the NY Fed at some point.
# anticipated_policy_move = 0.25

# Define the 2023 FOMC meeting dates
# Need a way to pull these programmatically too
def retrieve_fomc_meeting_dates():
    fomc_meetings = ['2023-06-14', 
                    '2023-07-26', 
                    '2023-09-20', 
                    '2023-11-01', 
                    '2023-12-13',
                    '2024-01-31',
                    '2024-03-20',
                    '2024-05-01',
                    '2024-06-12',
                    '2024-07-31',
                    '2024-09-18']
    
    run_date = dt.datetime.today().date()

    fomc_meetings_dates = string_to_date_list_conversion(fomc_meetings)

    filter_fomc_meetings = []
    for d in range(len(fomc_meetings_dates)):
        if fomc_meetings_dates[d] >= run_date:
            filter_fomc_meetings.append(fomc_meetings_dates[d])
    
    return filter_fomc_meetings


### IMPORT FUTURES DATA ###
def import_futures_data():

    last_meeting = max(retrieve_fomc_meeting_dates())
    last_meeting_last_day = cal.monthrange(last_meeting.year, last_meeting.month)[1]

    start_date = int(dt.date(dt.date.today().year,dt.date.today().month,1).strftime("%Y%m%d"))
    end_date = int(dt.date(last_meeting.year, last_meeting.month, last_meeting_last_day).strftime("%Y%m%d"))

    futures_data = gd.get_futures_data()[1]

    # Filter to just include 2023 dates
    futures_data = futures_data[(futures_data['expirationDate'] >= start_date) & (futures_data['expirationDate'] <= end_date)]

    # Convert expirationMonth column to full date
    futures_data['expirationDate'] = futures_data['expirationDate'].apply(lambda new_date: dt.datetime.strptime(str(new_date), "%Y%m%d").date())

    return futures_data


### COPY THIS LINE TO RETRIEVE THE LIST OF FOMC MEETING DATES
# fomc_meetings = retrieve_fomc_meeting_dates()

# We'll use this function to see if there's a meeting in one of our expiry months
def date_match(expiryDate, fomcMeetingDate):
    expiryDateMonth = expiryDate.strftime('%m')
    expiryDateYear = expiryDate.strftime('%Y')

    fomcMeetingDateMonth = fomcMeetingDate.month
    fomcMeetingDateYear = fomcMeetingDate.year

    if (int(expiryDateMonth) == int(fomcMeetingDateMonth)) & (int(expiryDateYear) == int(fomcMeetingDateYear)):
        return 1
    else:
        return 0

# Create a dataframe of Table 1 meeting data
def create_meeting_data_dataframe(futuresData, fomcMeetings, currentFedFunds):

    meeting_data = [["Expiry Month", "Price", "Implied Rate", "Meeting Day", "Month End Day", "Days After Meeting", "Beg Month Rate", "End Month Rate", "Change"]]
    index_value = 0

    # Convert string values into dates
    fomc_meetings_dates = fomcMeetings
    # fomc_meetings_dates = filter(lambda dates: dates >= dt.datetime.today(), fomc_meetings_dates)

    for index, row in futuresData.iterrows():
        # Iterate the Index
        index_value += 1

        if index < len(futuresData) - 1:
            next_row = futuresData.iloc[index + 1]

        else:
            pass

        # Grab relevant rows from dataframe
        expiry_date = row["expirationDate"]
        price = row["last"]

        #Calculate the implied rate that the futures contract corresponds to
        implied_rate = 100 - float(price)

        # Calculate FOMC Meeting Day -- if no meeting, set meeting day as zero (0)
        for i in range(len(fomc_meetings_dates)):
            date_check = date_match(expiry_date, fomc_meetings_dates[i])
            if date_check == 1:
                meeting_day = fomc_meetings_dates[i].day
                # last_day_of_month = cal.monthrange(fomc_meetings_dates[i].year, fomc_meetings_dates[i].month)[1]
                break
            else:
                meeting_day = 0

        # Calculate the last day of the month
        expiry_date_year = expiry_date.year
        expiry_date_month = expiry_date.month
        month_range_calc = cal.monthrange(expiry_date_year, expiry_date_month)

        month_end_day = month_range_calc[1]

        # print(meeting_day, month_end_day)

        #Calculate the Days after meeting
        days_after_meeting = month_end_day - meeting_day

        #Calculate the Month Beginning Rate
        if index_value == 1:
            beg_month_rate = currentFedFunds
        
        elif (index_value > 1) & (meeting_day == 0):
            beg_month_rate = implied_rate

        elif (index_value > 1) & (meeting_day != 0):
            beg_month_rate = previous_end_month_rate

        else:
            None

        # Calculate the Month Ending Rate
        if (meeting_day == 0):
            end_month_rate = beg_month_rate

        elif meeting_day == month_end_day:
            # print("It worked")
            end_month_rate = 100 - float(next_row["last"])

        elif meeting_day != 0:
            end_month_rate = ((implied_rate * month_end_day) - (beg_month_rate * meeting_day)) / days_after_meeting
        
        else:
            None
        
        # Store the end_month_rate for the next pass through
        previous_end_month_rate = end_month_rate

        # Calculate the change from the month beginning to month end
        rate_change = end_month_rate - beg_month_rate

        # Insert data into list
        row_data = [expiry_date, price, implied_rate, meeting_day, month_end_day, days_after_meeting, beg_month_rate, end_month_rate, rate_change]
        # print(row_data)

        # Insert row_data into list of lists
        meeting_data.append(row_data)

    meeting_data_df = pd.DataFrame(meeting_data[1:], columns=meeting_data[0])
    return meeting_data_df


### Builds the isolated probabilty events. Requires fomce_meetings, create_meeting_data_dataframe(), and anticipated_policy_move variables
def build_probability_events(fomcMeetings, meetingData, policyMove):
    
    adjusted_fomc_meetings = []
    isolated_probabilities = []
    
    # Convert meeting dates to first of month so they can be merged
    for date in range(len(fomcMeetings)):
        replaced_date = fomcMeetings[date].replace(day=1)
        adjusted_fomc_meetings.append(replaced_date)

    fomcMeetings_df = pd.DataFrame({"Expiry Month":adjusted_fomc_meetings})
    # print(adjusted_fomc_meetings)
    # print(meetingData)

    joined_list = pd.merge(fomcMeetings_df,
                           meetingData[['Expiry Month', 'Change']],
                           on="Expiry Month",
                           how='inner')

    joined_list.insert(0, "Meeting Dates", fomcMeetings)

    for ind in joined_list.index:
        move_probability = joined_list['Change'][ind] / policyMove
        isolated_probabilities.append(move_probability)

    joined_list.insert(3, "Isolated Probabilities", isolated_probabilities)
        
    return joined_list

def create_zero_list(probabilityRange):
    zero_list = [0] * probabilityRange  
    return zero_list

# This function will build out the probability tree for our probability_events. Returns a tuple containing just the tree in a list of lists [0],
# and a dataframe of the complete tree [1]
def create_probability_tree(fomcMeetings, probabilityEvents, anticipatedPolicyMove, currentFedFunds):
    
    """
    Will return a tuple of values: probability_tree [0], probability_tree_headers [1], probability_df [2]
    """

    meeting_count = len(fomcMeetings)
    starting_node = meeting_count
    probability_range = (meeting_count * 2) + 1

    probability_tree = []
    probability_tree_headers = []
    
    current_upper = math.ceil(currentFedFunds * 4) / 4
    current_lower = math.floor(currentFedFunds * 4) / 4
    current_mid = (current_upper + current_lower) / 2

    header_start = current_mid - (meeting_count * anticipatedPolicyMove)
    header_value = header_start

    cumulative_hike_probabilities = []
    cumulative_cut_probabilities = []

    ### CREATE TREE HEADERS ###
    for meeting in range(probability_range):
        probability_tree_headers.append(header_value)
        header_value = header_value + anticipatedPolicyMove


    ### CREATE PROBABILITY TREE ###
    for meeting in range(meeting_count):
        # Create a new blank list to build our probability tree on
        current_row = create_zero_list(probability_range)
        probability_tree.append(current_row)

        isolated_probability = probabilityEvents['Isolated Probabilities'][meeting]

        ### FRONT MEETING LOGIC ###

        # If the isolated probability is greater than zero, our move will be to the right.
        if (meeting == 0) & (isolated_probability >= 0):
            # Begin with the starting node, and move right.
            min_node = starting_node
            max_node = starting_node + 1

            probability_tree[meeting][min_node] = 1 - isolated_probability
            probability_tree[meeting][max_node] = isolated_probability

        # If the isolated probability is less than zero, our move will be to the left.
        elif (meeting == 0) & (isolated_probability < 0):
            # Begin with the starting node, and move left.
            min_node = starting_node - 1
            max_node = starting_node       
            
            probability_tree[meeting][max_node] = 1 - abs(isolated_probability)
            probability_tree[meeting][min_node] = isolated_probability

        ### TREE LOGIC ###

        # Start the next part of our probability tree, we're going to move the max_node right if the probability is positive
        elif (meeting > 0) & (isolated_probability >= 0):
            min_node = min_node
            max_node = max_node + 1

            for node in range(min_node, max_node + 1):
                probability_tree[meeting][node] = (probability_tree[meeting - 1][node - 1] * isolated_probability) + ((1 - isolated_probability) * probability_tree[meeting - 1][node])

        elif (meeting > 0) & (isolated_probability < 0):
            min_node = min_node - 1
            max_node = max_node

            for node in range(min_node, max_node + 1):
                probability_tree[meeting][node] = (abs(isolated_probability)*probability_tree[meeting - 1][node + 1]) + ((1- abs(isolated_probability))*probability_tree[meeting-1][node])
        
        else:
            None

    for hike_prob in range(len(probability_tree)):
        hike = sum(probability_tree[hike_prob][6:])
        cumulative_hike_probabilities.append(hike)

    for cut_prob in range(len(probability_tree)):
        cut = sum(probability_tree[cut_prob][0:4])
        cumulative_cut_probabilities.append(cut)
    
    probability_df = pd.DataFrame(probability_tree[0:], columns=probability_tree_headers)
    probability_df.insert(0, "Meeting Dates", fomcMeetings)
    probability_df.insert(1, "Cumulative Hike Probability", cumulative_hike_probabilities)
    probability_df.insert(2, "Cumulative Cut Probability", cumulative_cut_probabilities)

    return probability_tree, probability_tree_headers, probability_df

# This function will merge all of the probability events together into a single table. Requires the results of build_probability_events() and create_probability_tree()
def merge_probability_data(probabilityEvents, probabilityTree):
    complete_probability_tree = pd.merge(probabilityEvents,
                        probabilityTree,
                        on="Meeting Dates",
                        how="inner")
    
    return complete_probability_tree


# policy_move_threshold = 0.5

#This function takes the output of create_probability_tree[0], fomc_meetings list, and policy_move_threshold to create a dataframe corresponding with expected policy moves.
def anticipated_policy_moves(fomcMeetings, probabilityTreeList, probabilityTreeHeaders, policyMoveThreshold):

    policy_move = [['Meeting', 'Policy Range Midpoint', 'Policy Decision', 'Decision Confidence']]
    sum_position = len(fomcMeetings)
    policy_decision = 'No Move'

    #Start at midpoint, and when probability above or below that point is greater than policyMoveThreshold, then shift the sum_position up or down one
    for row in range(len(probabilityTreeList)):

        hike_probability = sum(probabilityTreeList[row][sum_position+1:])
        cut_probability = sum(probabilityTreeList[row][0:sum_position-1])
        no_move_probability = probabilityTreeList[row][sum_position]

        if hike_probability >= policyMoveThreshold:
            sum_position += 1
            policy_decision = 'Hike'
            decision_confidence = hike_probability

        elif cut_probability >= policyMoveThreshold:
            sum_position += -1
            policy_decision = 'Cut'
            decision_confidence = cut_probability

        else:
            policy_decision = 'No Move'
            decision_confidence = no_move_probability

        policy_range = probabilityTreeHeaders[sum_position]
        meeting = fomcMeetings[row]

        policy_move_row = [meeting, policy_range, policy_decision, decision_confidence]
        policy_move.append(policy_move_row)

    policy_move_df = pd.DataFrame(policy_move[1:], columns=policy_move[0])
    
    return policy_move_df


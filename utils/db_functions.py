from utils.db import execute, fetch
from models.datapoint import Datapoint
from datetime import datetime


async def db_check_token_user(user):
    query = """select * from users where username = :username"""
    values = {"username": user.username}
    result = await fetch(query, False, values)
    if result is None:
        return None
    else:
        return result


async def db_check_jwt_username(username):
    query = """select * from users where username = :username"""
    values = {"username": username}

    result = await fetch(query, True, values)
    if result is None:
        return False
    else:
        return True


async def db_get_user_moods(username):
    query = """select * from moods where username='""" + username + "'" + " order by epochday"
    print (query)
    moods = await fetch(query, False, None)
    return moods


async def db_insert_mood(username: str, moodin: str):

    # Store the date in YYYY-MM-DD format as a string (we actually don't need to do this, but when working with large tables
    # and epoch-oriented dates, it's very nice and better for database debugging to have a readable date in there also.

    nowstr = str(datetime.utcnow()).split()

    # epochdays is the number of days it's been since the "epoch" - January 1, 1970.
    # Since we will be using this in our calculations, it's useful to have them as a continuous integer

    epochdays = str(datetime.today() - datetime.utcfromtimestamp(0)).split()  # needs to be a str to include it in the INSERT statement
    print (epochdays)

    # The INSERT statement and DB will convert epochdays to an int, which is what we ultimately want
    query = """insert into moods(username, mood, date, epochday) values(""" + "'" + username + "', '" + moodin + "', '" + nowstr[0] + "'," + epochdays[0] + ")"
    print(query)

    await execute(query, False)
    query = """select * from moods where username='""" + username + "'"
    print(query)

    moods = await fetch(query, False, None)
    return moods


async def db_get_current_streak(username):
    query = """select username, epochday from moods order by username, epochday asc"""
    print (query)
    epochdays = await fetch(query, False, None)
    print (epochdays)

    # Go through the epochdays to find the streaks. In the absence of a persistent streaks table,
    # you need to scan through all of the data.  Create two Python dictionaries, one for current streaks
    # and one for longest streaks for each user.

    # NOTE: In a production database, you would certainly NOT calculate this each time,
    # you would instead run a batch process to initially populate a streaks table and instead work only from the latest streak onward.
    # Presumably during production you would be working with pre-existing data and have the ability to run a batch process on
    # that data to create a streaks table.  It is horribly inefficient to query the entire table and do all analysis in
    # the way it's being done here, but I don't have the luxury of setting up a table in advance and running a batch process
    # against it in this prototype.

    # The streaks table would ultimately have the structure:
    # (username: str, current_streak_cnt: int, current_streak_epochday: int, longest_streak: int, longest_streak_end_epochday: int)

    # What you would do basically would be to check the current_streak_epochday vs. the current epochday; if the
    # current is only one day greater, then you'd update the current_streak_cnt by one.  If the current streak is now greater
    # than the longest_streak, you'd also update the longest_streak +1 and longest_streak_end_epochday to the current day.

    current_streaks = {}
    longest_streaks = {}
    user_streaks = {}
    previous_day = 0
    streak_cnt = 0
    longest_streak = 0
    previous_uname = ""

    # Loop through all of the data returned from the database query.

    for datapoint in epochdays:
        dp = Datapoint(**datapoint) # Convert the database records returned to a Datapoint object to access the data

        # The data is sorted first by username and then by epochday, so we first look for a change in username.
        # If the username has changed, we must tabulate the data for the previous user before moving on.

        if (dp.username == previous_uname):
            if (dp.epochday > previous_day + 1):

                # Start tracking a new streak and save off previous streak

                if (streak_cnt >= 2):
                    longest_streak = streak_cnt + 1 if longest_streak < streak_cnt + 1 else longest_streak
                    print ("new streak found: ", streak_cnt + 1, ", ", previous_day, ", Longest Streak:", longest_streak)

                streak_cnt = 0
            elif (dp.epochday == previous_day + 1): # got an additional day of the same streak, so increment it
                streak_cnt += 1
            # NOTE: It is possible that a patient entered mood data more than once in the same day, so ignore it.
            # i.e. else: (do nothing and continue looping)

            previous_day = dp.epochday

        else:
            if (previous_uname == ""):  # This is the first record, so just reinitialize
                previous_uname = dp.username
                previous_day = 0
                streak_cnt = 0
            else:

                # Save off previous user's data before resetting

                print ("---- NEW USER: ", dp.username)
                longest_streak = streak_cnt + 1 if longest_streak < streak_cnt + 1 else longest_streak
                print ("Current streak for ", previous_uname, ": ", streak_cnt + 1, ", ", previous_day, ", Longest Streak:", longest_streak)

                # Save current streak and longest streak for this user.

                current_streaks[previous_uname] = streak_cnt + 1
                longest_streaks[previous_uname] = longest_streak

                previous_uname = dp.username
                previous_day = 0
                streak_cnt = 0
                longest_streak = 0


    # Save current streak and longest streak for the final user:

    longest_streak = streak_cnt+1 if longest_streak < streak_cnt+1 else longest_streak
    print("Current streak for ", previous_uname, ": ", streak_cnt+1, ", ", previous_day, ", Longest Streak:",
      longest_streak)

    current_streaks[previous_uname] = streak_cnt + 1
    longest_streaks[previous_uname] = longest_streak

    print ("Current Streaks: ", current_streaks)
    print ("Longest Streaks: ", longest_streaks)

    # Now determine the total streak count so we can determine percentages

    total_streaks = 0
    for streak in longest_streaks.values():
        total_streaks += streak

    print("Total Streaks: ", total_streaks)
    print ("User percentage for ", username, ": ", current_streaks[username]/total_streaks)

    user_streaks["current_streak"] = current_streaks[username]
    user_streaks["longest_streak"] = longest_streaks[username] # to make it easier to check, I'm also returning longest_streak
    user_streaks["percentile"] = current_streaks[username]/total_streaks

    return user_streaks



# This script takes the raw text of a cv as input and outputs a visual timeline of events.
# In addition to producing a timeline of events based on the raw text from a CV, this script also automatically
# identifies a "regime" for dates and events, meaning a pattern whereby event names either follow or precede the dateself.
# The script can also autmoatically classify events as either academic or professional/other and display the classification on the timeline.


import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import re
import datetime



parser = argparse.ArgumentParser()

# add argument for the name of the CV file to be processed
parser.add_argument('--input', '-i', type=str, help='The name of the file to extract a candidate profile timeline from')
# add argument for the value 'n', the number of characters needed to qualify as an event names
parser.add_argument('--number_characters', '-n', type=int, help='The number of characters to accept in the same line as a date')

args = parser.parse_args()

n = args.number_characters
# note that, if there is some set of labeled training data with correct event names and dates, n can be optimized with a simple Shell script






def Month_RegEx(string):
    # match months in the format 'Jan', 'jan', 'January', 'january' or '01'
    pattern = re.search(r'(^|[^a-zA-Z0-9]+?)(((?P<month01>[Jj]an(uary){0,1})|(?P<month02>[Ff]eb(ruary){0,1})|(?P<month03>[Mm]ar(ch){0,1})|(?P<month04>[Aa]pr(il){0,1})|(?P<month05>[Mm]ay)|(?P<month06>[Jj]un(e){0,1})|(?P<month07>[Jj]ul(y){0,1})|(?P<month08>[Aa]ug(ust){0,1})|(?P<month09>[Ss]ep(tember){0,1})|(?P<month10>[Oo]ct(ober){0,1})|(?P<month11>[Nn]ov(ember){0,1})|(?P<month12>[Dd]ec(ember){0,1}))[^a-zA-Z]+?)|((^|[^a-zA-Z0-9]+?)(?P<month_digits>(0[0-9])|(1[012]))[^0-9]+)[^a-zA-Z]*?$', string)
    return pattern

def Year_RegEx(string):
    # match years between 1950 and 2029
    pattern = re.search(r'^.*?((?P<year1>((19[5-9]\d)|(20[0-2]\d)))[^0-9]*(?P<year2>(((19[5-9]\d)|(20[0-2]\d)))|[Pp]resent)*).*?$', string)
    return pattern

def Candidate_Name(string):
    # match full name of candidate as the first only alpha string with 2 to 3 tokens (or initials) where they all begin with a capital letter
    pattern = re.search(r'(?P<name>([A-Z]([a-z]*|\.)\s){2,3})', string)
    return pattern

def Education(string):
    # match full name of candidate as the first only alpha string with 2 to 3 tokens (or initials) where they all begin with a capital letter
    pattern = re.search(r'(?P<edu>(BA|MA|MSc|Ph[Dd]|[Uu]niversity|[Cc]ollege|[Dd]egree|[Ss]tud[ie]|[Ss]emester|[Bb]achelor|[Mm]aster|[Dd]octora|[Pp]ost[-\s]{0,1}[Dd]oc))', string)
    return pattern




def Int_From_Month_String(string):
    # extract the integer for the month in the month pattern names
    if string[-2] == '0':
        digit = int(string[-1])
    else:
        digit = int(string[-2:])
    return digit




def Get_Dates(line, n, regime):
    index = None
    y1_index = 0
    y2_index = 0
    m1_index = 0
    m2_index = 0
    y1_index_r1 = 0
    y2_index_r1 = 0
    m1_index_r1 = 0
    m2_index_r1 = 0
    month_patterns = ['month01', 'month02', 'month03', 'month04', 'month05', 'month06', 'month07', 'month08', 'month09', 'month10', 'month11', 'month12', 'month_digits']
    # identify current month and year using datetime module, set continuous vairable for the 'present'
    now = datetime.datetime.now()
    present = now.year + (now.month / 12)
    # use regular expression to match up to two years in a single line
    year_pattern = Year_RegEx(line)
    # use regular expression to match up to two months in a single line
    month_pattern = Month_RegEx(line)
    try:
        year1 = year_pattern.group('year1')
        if year1 != None:
            # remember location of first and last character of year1 and all other non-None date values to pass to event extraction later
            # note: finding location of first and last characters by using line.find(year1[-1]) and line.find(year1[0]) cause errors for some reason,
            # but this alternative seems to work fine
            y1_index = line.find(year1) + len(year1)
            y1_index_r1 = line.find(year1)
    except AttributeError:
        year1 = None
    try:
        year2 = year_pattern.group('year2')
        if year2 != None:
            # account for special case of ongoing event
            if year2 == 'present':
                year2 = present
            if year2 == 'Present':
                year2 = present
            # remember location of first and last character of year2
            y2_index = line.find(year2[-1]) + len(year2)
            y2_index_r1 = line.find(year2)
    except AttributeError:
        year2 = None
    mons = []
    # only look for months if year(s) is/are specified
    if year1 != None:
        for pat in month_patterns:
            try:
                mon = month_pattern.group(pat)
                if mon != None:
                    # remember location of first and last character of month1
                    m1_index = line.find(mon) + len(mon)
                    m1_index_r1 = line.find(mon)
                    # make sure to store months as integers
                    if pat == 'month_digits':
                        mons.append(Int_From_Month_String(mon))
                    else:
                        # for months in non-digit format, use the last characters of the pattern name to derive digit representation
                        mons.append(Int_From_Month_String(pat))
                    # check if there is a second month in the line
                    ind = line.find(mon)
                    # add 2 to the index of the first character of the first recognised month to avoid any chance of it being counted twice
                    month_pattern = Month_RegEx(line[(ind + 2):])
                    for pat in month_patterns:
                        try:
                            mon = month_pattern.group(pat)
                            if mon != None:
                                # remember location of first and last character of month2
                                m2_index = line.find(mon) + len(mon)
                                m2_index_r1 = line.find(mon)
                                # make sure to store months as integers
                                if pat == 'month_digits':
                                    mons.append(Int_From_Month_String(mon))
                                else:
                                    # for months in non-digit format, use the last characters of the pattern name to derive digit representation
                                    mons.append(Int_From_Month_String(pat))
                        except AttributeError:
                            mon = None
            except AttributeError:
                mon = None
        # if no month is indicated, assume January for both, and if only one month is indicated, set the months equal to one another
        if len(mons) >= 1:
            month1 = mons[0]
            if len(mons) >= 2:
                month2 = mons[1]
            else:
                month2 = month1
        else:
            month1 = 1
            month2 = 1
    else:
        month1 = None
        month2 = None
    # when no year2 is indicated or detected, assume the event happened within one calendar year and set year2 equal to year1
    if year2 == None:
        year2 = year1
    # make sure to store years as floats (cannot use integers because of special 'present' case)
    if year1 != None:
        year1 = float(year1)
    if year2 != None:
        year2 = float(year2)
    # set index equal to the largest or smallest (depending on regime) of the non-zero date sub-part indices (also depending on regime)
    non_zero_indices = []
    if regime == 0:
        indices = [y1_index, y2_index, m1_index, m2_index]
    else:
        indices = [y1_index_r1, y2_index_r1, m1_index_r1, m2_index_r1]
    for i in indices:
        if i != 0:
            non_zero_indices.append(i)
    if len(non_zero_indices) > 0:
        if regime == 0:
            index = max(non_zero_indices)
        elif regime == 1:
            index = min(non_zero_indices)
    # log distance from index to use in determining regime
    if regime == 0:
        # count characters following index in support of (forward) regime 0
        char_count_from_index = len(line[index:])
    elif regime == 1:
        # count characters preceding index in support of (backward) regime 1
        char_count_from_index = len(line[:index])
    return year1, year2, month1, month2, index, char_count_from_index



def Learn_Regime(file):
    regime_0_count = 0
    regime_1_count = 0
    with open(file, 'r') as infh:
        # add character counts to respective regime counts
        for line in infh:
            regime_0_count += Get_Dates(line, n, 0)[5]
            regime_1_count += Get_Dates(line, n, 1)[5]
    infh.close()
    # set regime as regime with the highest count corresponding to that pattern
    if regime_1_count > regime_0_count:
        regime = 1
    else:
        regime = 0
    return regime

regime = Learn_Regime(args.input)






def Find_Event(text, regime, date_index):
    event = '?'
    # check that there is some text in the line at least n characters before or after (depending on regime) the index, otherwise leave event unknown
    if regime == 0:
        if len(text) > (date_index + n):
            # adding 1 will ensure that the event excludes the last character of the date and whitespace without cutting into the event text itself
            event = text[(date_index + 1):]
    elif regime == 1:
        if len(text[:date_index]) > n:
            # subtracting 1 will ensure that the event excludes the first characters of the first date without cutting into the event text itself
            event = text[:(date_index - 1)]
    return event




def Parse_Name_Dates_Events(file, regime):
    cand_name = None
    date_list = []
    event = None
    with open(file, 'r') as infh:
        lines = infh.readlines()
        for i in range(0, len(lines)):
            line = lines[i]
            # use regular expression to match candidates's name
            candidate_pattern = Candidate_Name(line)
            year1, year2, month1, month2, date_index, char_count_from_index = Get_Dates(line, n, regime)
            date = [year1, year2, month1, month2]
            if date[0] != None:
                if date_index != None:
                    # Assume that if an event is in the same line as the date, it will be all the text besides the date
                    # Otherwise, assume that the text of the event is the whole following or preceding (depending on regime) lines
                    # It is a reasonably safe assumption that a date will not be in the same line as a long description with event details
                    event = Find_Event(line, regime, date_index)
                    # if the event is not in the same line as the date, use previous or foillowing line as event
                    if event == '?':
                        if regime == 0:
                            # account for cases where the date in question is the first or last line, producing an IndexError
                            try:
                                event = lines[i + 1]
                            except IndexError:
                                event = '?'
                        elif regime == 1:
                            try:
                                event = lines[i - 1]
                            except IndexError:
                                event = '?'
                    # add event as fifth element of the date list
                    date.append(event)
            else:
                # add null event as fifth element of the date list
                date.append(None)
            # store all dates/events as a list of lists, for easy indexing
            date_list.append(date)
            if cand_name != None:
                continue
            else:
                try:
                    cand_name = candidate_pattern.group('name')
                except AttributeError:
                    cand_name = None
    infh.close()
    return cand_name, date_list







def Produce_Dataframe(file):
    cand_name, date_list = Parse_Name_Dates_Events(file, regime)
    # appropriately format data for the pandas dataframe (i.e. a list of lists where start and end dates are continuous variables)
    raw_data = []
    not_None = True
    for date in date_list:
        # ignore dates with None values
        if None in date:
            pass
        else:
            try:
                entry = []
                # rearrange so that the raw data is in the format [event, start date, end date, type]
                entry.append(date[4])
                # make the date continuous variables such that January 2010 = 2010.0, February 2010 = 2010.083, December 2010 = 2010.917, etc.
                entry.append(date[0] + ((date[2] - 1) / 12))
                entry.append(date[1] + ((date[3] - 1) / 12))
                # if education keywords are in the event name, classify as education type event by colouring it red
                if Education(date[4]) == None:
                    entry.append('blue')
                else:
                    entry.append('red')
                raw_data.append(entry)
            except IndexError:
                pass
    # sort events by start date
    sorted_raw_data = sorted(raw_data, key=lambda entry: entry[1])
    # create pandas dataframe
    dataframe = pd.DataFrame(sorted_raw_data, columns=['EventName', 'Start', 'End', 'Type'])
    return cand_name, dataframe


cand_name, dataframe = Produce_Dataframe(args.input)









def Produce_Timeline(dataframe):
    # general outline for matplotlib timeline taken from https://stackoverflow.com/questions/50883054/how-to-create-a-historical-timeline-with-python
    event = dataframe['EventName']
    type = dataframe['Type']
    begin = dataframe['Start']
    end = dataframe['End']
    length =  dataframe['End'] - dataframe['Start']

    # again identify current month and year using datetime module
    now = datetime.datetime.now()

    # set x axis limit on timeline to be the current month and year (as a continuous variable)
    x_max = now.year + (now.month / 12)
    # set origin to be the beginning of the calendar year before the first event
    x_min = ((dataframe.iloc[0].iloc[1]) // 1) - 1
    # set y axis limit to be the number of events
    y_max = len(dataframe)

    # plt.figure()
    plt.figure(figsize=(12,8))
    # add small sliver to width parameter so that points in time show up on the timeline
    plt.barh(range(len(begin)), (end-begin + 0.05), .3, left=begin, color=type)
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.tick_params(axis='both', which='minor', labelsize=20)
    # use candidate name automatically extracted earlier as title of timeline
    plt.title(cand_name, fontsize = '30')
    plt.xlabel('Year', fontsize = '20')
    plt.ylabel('blue = prefessional\nred = academic', fontsize = '10')
    plt.yticks(range(len(begin)), "")
    plt.xlim(x_min, x_max)
    plt.ylim(-1,y_max)
    for i in range(len(dataframe)):
        plt.text(begin.iloc[i] + length.iloc[i]/2,
                 i+.25, event.iloc[i],
                 ha='center', fontsize = '12')
    plt.show()
    plt.close()













if args.input != None:
    Produce_Timeline(dataframe)
else:
    print('ERROR: No input file specified')

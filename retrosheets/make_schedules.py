#!/usr/bin/env python

import pandas as pd
import numpy as np
import random
import sys
import os
import json

def old_main():

    teams = ['Cardinals', 'Nationals', 'Dodgers', 'Astros']

    nominal_season_length = 24
    home_games = int(nominal_season_length / 2)
    home_games_per_opp = int(home_games / (len(teams) - 1))
    print(f'Home Games Per Opponent: {home_games_per_opp}')

    schedule = dict()
    for team in teams:
        opp_teams = np.setdiff1d(teams, [team]).tolist()
        games = opp_teams * home_games_per_opp
        random.shuffle(games)
        schedule[team] = games

    for team in teams:
        print(f'{team}:{schedule[team]}')


def main(schedule_file, output_file=None, team_filter=None, season_length_limit=None, abbreviation_file='retrosheets/TEAMABR.TXT'):

    # try to get abbreviations
    try:
        current_yr = 2010 
        abbrev = pd.read_csv(abbreviation_file, comment='#', header=None,
                                names=['TEAM','LEAGUE', 'CITY', 'NAME', 'FIRST_YR', 'LAST_YR'],
                                keep_default_na=False)
                                # dtype={'TEAM':str,'LEAGUE':str, 'CITY':str, 'NAME':str, 'FIRST_YR':int, 'LAST_YR':int})
        abbrev = abbrev[ abbrev['LAST_YR']==current_yr]
    except:
        print(f'WARNING: Unable to read and/or process abbreviations file {abbreviation_file}, proceeding without.')
        abbrev = None



    # Field(s)      Meaning
    # 1          Date in the form "yyyymmdd"
    # 2          Number of game:
    #                     "0" - a single game
    #                     "1" - the first game of a double header including separate admission doubleheaders
    #                     "2" - the second game of a double header including separate admission doubleheaders
    # 3          Day of week("Sun","Mon","Tue","Wed","Thu","Fri","Sat")
    # 4-5        Visiting team and league
    # 6          Season game number for visiting team
    # 7-8        Home team and league
    # 9          Season game number for home team
    # 10         Day (D), Night (N), Afternoon (A), Evening (E for twinight)
    # 11         Postponement/cancellation indicator (more detail below)
    # 12         Date of makeup if played in the form "yyyymmdd" (more detail below)
    schedule_cols = ['DATE', 'GAME_TYPE', 'DAYOFWEEK', 'VISITOR', 'VISTOR_LEAGUE', 'VISTOR_NGAME', 
                        'HOME', 'HOME_LEAGUE', 'HOME_NGAME', 
                        'GAME_TIME', 'POSTPONE_TYPE', 'DATE_MAKEUP']
    raw_schedule = pd.read_csv(schedule_file, names=schedule_cols)
    
    full_schedule = raw_schedule[['VISITOR', 'HOME']]

    schedule = full_schedule[ full_schedule['VISITOR'].isin(team_filter) & full_schedule['HOME'].isin(team_filter) ]

    if not season_length_limit is None:
        print('Currently does not work with team_filter and season_length_limit both specific.  Ignoring length Limit...')
    else:
        idx = schedule.index[ (full_schedule['VISITOR'] == team_filter[0]) | (full_schedule['HOME'] == team_filter[0]) ]
        if not season_length_limit is None:
            idx = idx[:season_length_limit]

        for i in range(1, len(team_filter)):
            team = team_filter[i]
            ii = schedule.index[ (full_schedule['VISITOR'] == team) | (full_schedule['HOME'] == team) ]
            if not season_length_limit is None:
                ii = ii[:season_length_limit]
            
            idx = idx.union(ii)
            
        # schedule

        
        schedule = schedule.loc[idx]
        

    if not output_file is None:    
        schedule.reset_index(inplace=True, drop=True)
        schedule_json = schedule.to_json(orient='values')
        with open(output_file, 'w') as f:
            f.write(schedule_json)
    else:
        print(schedule)

if __name__ == '__main__': 
    schedule_file = 'retrosheets/schedule/2017SKED.TXT'
    
    output_file = 'schedule_2017.json'
    
    main(schedule_file, output_file=output_file, team_filter=['HOU', 'LAN', 'SLN', 'WAS'], season_length_limit=5)
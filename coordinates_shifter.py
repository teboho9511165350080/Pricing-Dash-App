
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 13:25:18 2021

@author: LekenoTR
"""

import pandas as pd
import math

def shift_coordinates (substations_final, chosen_study_years, slider):
    shifted_data = pd.DataFrame()
     
    if slider == 'slider':
        study_years = list([str(chosen_study_years), str(chosen_study_years)])
    else:
        study_years = chosen_study_years
    
    for index in range(int(min(study_years)), int(max(study_years))+1):
        radius = 0.0010*(index+1-int(min(study_years))) 
        # slave_data.sort_values(by=['Plant'], inplace=True)
        slave_data = (substations_final[substations_final['Year'] == index])
        slave_data.sort_values(by=['Plant'], inplace=True)
        slave_data = slave_data.reset_index(drop=True)
            
        for index2 in range(len(slave_data)):
            slave_data.loc[index2, 'Longitude'] += radius*math.cos((index2*math.pi*2)/(len(slave_data)))
            slave_data.loc[index2, 'Latitude'] += radius*math.sin((index2*math.pi*2)/(len(slave_data)))
                
        shifted_data = shifted_data.append(slave_data, ignore_index = True)
    substations_final = shifted_data 
        
    return substations_final
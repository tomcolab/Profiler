# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 20:38:53 2017

@author: thomas
"""

import pandas as pd
import numpy as np
from RawProfile import *
from tkinter import filedialog
from tkinter import *
import itertools
from tkinter import messagebox

#%%

#define available profile arrays
normal_profile_selection = np.array([1000,2000,3000,5000])
no_five_profile_selection = np.array([1000,2000,3000])

selection = normal_profile_selection
cutting_tolerance = 10

#filepath dialog
root = Tk()
root.withdraw()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Excel files","*.xlsx"),("all files","*.*")))


#%%
#load profile lengths in pandas dataframe
profiles_df = pd.read_excel(root.filename)
profiles_df = profiles_df.sort_values(profiles_df.columns[0], ascending=False)

#check which profiles are available
result = messagebox.askyesno("Verfügbare Profile","Ist ein 5 m Profil verfügbar?")
if not result:
     selection = no_five_profile_selection
     
#check for cutting tolerance     

#check for permutation depth 
check_series = profiles_df.copy()
check_series = check_series.sort_values(check_series.columns[0])
max_raw_profile_length = check_series.max().values
permutation_depth = 1                                                                             
for length in check_series.values:
     diff = max_raw_profile_length - length
     if(diff >= cutting_tolerance):
          max_raw_profile_length = diff
     else:
          break
     permutation_depth = permutation_depth + 1
     

#create permutations of values
perm_df_dict = get_permuted_dataframes(profiles_df, permutation_depth)


#%%
#TODO:
     #- implement remainder cutting based on prepared dataframes

#create work list of remaining profiles
profiles_array = profiles_df[profiles_df.columns[0]]                        
remaining_profiles_array = profiles_array.copy() 

#help members
raw_profile_list = []
garbage_array = np.array([])   
id_counter = 0   

#Define initial profile
LastProfile =  RawProfile("-1", 0)
LastProfile.remainder = 0


#create profiles                          
while(remaining_profiles_array.any()):
     
     if(LastProfile.remainder > 0):  
          #check for sum which fits best and does not violate cutting tolerances
          candidate_list = []
          for depth in perm_df_dict:
               #subtract remainder from remaining profile combinations
               subtrct_df = perm_df_dict[depth]
               subtrct_df["diff"] = LastProfile.remainder-subtrct_df["sum"]
               
               #remaining profile length shall be longer or equal the cutting tolerance
               subtrct_df["diff"] = subtrct_df["diff"].where(subtrct_df["diff"].values >= cutting_tolerance)
               
               #add candidates to the list
               if(subtrct_df["diff"].any()):
                    candidate_list.append(subtrct_df.loc[[subtrct_df["diff"].idxmin()]])
               
               
          if not candidate_list:
               LastProfile.scrap_remainder()
          else:  
               #take optimal candidate
               minimum = candidate_list[0]["diff"].values
               min_candidate = pd.DataFrame()
               
               for candidate in candidate_list:
                    if(candidate["diff"].values <= minimum):
                         minimum = candidate["diff"].values
                         min_candidate = candidate
               
     
               #gather all profile ids
               id_list = []
               for column in min_candidate.iteritems():
                    if "Id" in column[0]:
                         id_list.append(column[1].values)
               
               #cut profile for each profile id       
               for id in id_list:
                    LastProfile.cut_profile(id[0], np.asscalar(remaining_profiles_array[[id[0]]].values))
                    
                    #remove candidate from the list
                    remaining_profiles_array = remaining_profiles_array.drop(id[0])
                    perm_df_dict = drop_from_permutation_dataframes(id[0], perm_df_dict)
          
     
     else:
          #take largest profile to cut and compare it to possible profiles
          current_profile = remaining_profiles_array.max()
          current_profile_id = remaining_profiles_array.idxmax()
          
          
          #drop length from remaining profiles and all permutation dataframes   
          remaining_profiles_array = remaining_profiles_array.drop(current_profile_id)
          perm_df_dict = drop_from_permutation_dataframes(current_profile_id, perm_df_dict)
          
          #check fitting of avalable raw profiles
          for raw_profile in selection:
               if(raw_profile >= current_profile):
                    break
          
          id_counter = id_counter + 1
          NewRawProfile = RawProfile(id_counter, raw_profile)
          raw_profile_list.append(NewRawProfile)
          
          #Cut profile
          NewRawProfile.cut_profile(current_profile_id, current_profile)
          LastProfile = raw_profile_list[-1]

#Scrap remainder of very last profile          
LastProfile.scrap_remainder()

#%% Check profiles and create csv coordnation table

Profile_dict = {}

for raw in raw_profile_list:
     sub_dict = {}
     sub_dict["Länge (mm)"] = raw.length
     sub_dict["Ausschuss"] = raw.scrap
     for cut in raw.cut_list:
        sub_dict[cut.id] = cut.length
     Profile_dict[raw.id] = sub_dict
                 
export_df = pd.DataFrame
export_df = export_df.from_dict(Profile_dict)

#add total length and scrap to dataframe
export_df["Total"] = export_df.sum(axis=1)

#add empty column for visible section
export_df[" "] = np.nan

#add the amount of raw profiles to order

column_name = "Profil Bestell-Mengen"
raw_profiles = export_df.loc[["Länge (mm)"]].values

#%% export to excel
export_path = filedialog.asksaveasfile(mode =  "w", defaultextension=".xlsx")
writer = pd.ExcelWriter(export_path.name)
export_df.to_excel(writer, sheet_name = "Konfektion")
writer.save()

#%%

def drop_from_permutation_dataframes(current_profile_id, permutations_dfs_dict):
     for key in permutations_dfs_dict:
          for depth in range(1, key+1):
              drop_series = permutations_dfs_dict[key].loc[permutations_dfs_dict[key]["Id"+str(depth)] == current_profile_id]
              permutations_dfs_dict[key]  = permutations_dfs_dict[key].drop(drop_series.index)
     
     return permutations_dfs_dict     


def sums_of_permutations(permut_df, id_df):
     sum_dict = {}
     index = 0
     for tuple  in permut_df.itertuples(index=False, name=None):       
               sum_dict[index] = sum(tuple)
               index = index + 1
     
     sum_df = pd.DataFrame()
     sum_df = sum_df.from_dict(sum_dict)
     sum_df = sum_df.T
     sum_df.columns = ["sum"]
     sum_df = sum_df.join(id_df)
     sum_df = sum_df.sort_values("sum")
     return sum_df

def get_permuted_dataframes(profiles_df, max_depth):
     out_dict = {}
     for depth in range(1, max_depth+1):
          permut = get_permuted_values_df(profiles_df, depth)
          permut_ind = get_permuted_profile_ids_df(profiles_df, depth)
          permut_ind.columns = get_id_list(depth)
          out_dict[depth] = sums_of_permutations(permut, permut_ind)
          
     return out_dict
                 

def get_permuted_values_df(profiles_df, depth):
     permut_list = list(itertools.permutations(profiles_df.values, depth))
     permut_df = pd.DataFrame(permut_list)
     return permut_df
     
def get_permuted_profile_ids_df(profiles_df, depth):
     permut_list = list(itertools.permutations(profiles_df.index, depth))
     permut_df = pd.DataFrame(permut_list)
     return permut_df  

def get_id_list(depth):
     id_list = []
     for i in range(1, depth+1):
          id_list.append("Id"+str(i))
     return id_list


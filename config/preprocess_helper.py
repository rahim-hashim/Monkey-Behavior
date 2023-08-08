import re
import os
import sys
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from textwrap import indent
from pprint import pprint, pformat
from pprint import pprint
from collections import defaultdict
# Custom modules
from config import h5_helper
from config.image_diff import image_diff
# Custom classes
from classes.Session import Session

def add_external_cameras(session_df, session_obj):
  print('Checking for external camera files...')
  video_path = session_obj.video_path
  if os.path.exists(video_path):
    print('  External camera path: {}'.format(video_path))
    video_folders = os.listdir(video_path)
    if video_folders:
      cam_dict = defaultdict(list)
      cam_trials_dict = defaultdict(list)
      missing_trials_dict = defaultdict(list)
      print(f'  {len(session_df)} trials in session')
      print(f'  {len(video_folders)} external camera folders found')
      for v_index, video_folder in enumerate(tqdm(sorted(video_folders))):
        trial_num = video_folder.split('_')[2]
        # see if trial number is '0' or any number of zeros
        if re.match("^0+$", trial_num):
          for video_file in os.listdir(os.path.join(video_path, video_folder)):
            cam_name = video_file.split('-')[0]
            # initialize camera dictionaries
            cam_dict[cam_name] = []
            cam_trials_dict[cam_name] = []
            missing_trials_dict[cam_name] = []
        cam_trials_dict['folder'].append(int(trial_num))
        if int(trial_num) != 0 and int(trial_num)-1 not in cam_trials_dict['folder']:
          print('  Missing trial folder: {}'.format(int(trial_num)-1))
          for cam_name in cam_dict.keys():
            cam_dict[cam_name].append(np.nan)
        # empty trial camera folder
        if len(os.listdir(os.path.join(video_path, video_folder))) == 0:
          for cam_name in cam_dict.keys():
            cam_dict[cam_name].append(np.nan)
            missing_trials_dict[cam_name].append(int(trial_num))
            cam_trials_dict[cam_name].append(int(trial_num))
        # trial camera folder with files
        else:
          # look for video file for each camera
          for cam_name in cam_dict.keys():
            folder_video_files = os.listdir(os.path.join(video_path, video_folder))
            cam_video_file = [f for f in folder_video_files if cam_name in f]
            if cam_video_file:
              cam_dict[cam_name].append(os.path.join(video_path, video_folder, cam_video_file[0]))
              cam_trials_dict[cam_name].append(int(trial_num))
            else:
              cam_dict[cam_name].append(np.nan)
              missing_trials_dict[cam_name].append(int(trial_num))
              cam_trials_dict[cam_name].append(int(trial_num))
      # check for missing trials and add to DataFrame
      for cam_name in cam_dict.keys():
        print('    {} files found: {}'.format(cam_name, len(cam_dict[cam_name])))
        # print missing trials
        print('    Missing trials: {}'.format(missing_trials_dict[cam_name]))
        if len(cam_dict[cam_name]) != len(session_df):
          # see what number is missing from the list that should just be sequential
          t_index = [i for i in session_df['trial_num'] if int(i) not in cam_trials_dict[cam_name]]
          print('      Missing trials: {}'.format(t_index))
        try:
          session_df[cam_name] = cam_dict[cam_name]
        except Exception as error:
          # handle the exception
          print('  An exception occurred:', error) # An exception occurred: division by zero
          print('  External camera files not added to DataFrame.')
      print('  External camera files added to DataFrame.')
  else:
    print('  No external camera files found {}'.format(video_path))
  return session_df, session_obj

def preprocess_data(path_obj, start_date, end_date, monkey_input, experiment_name, reprocess_data, save_df, combine_dates):
  # preprocess data
  if reprocess_data:
    ml_config, trial_record, session_df, session_obj, error_dict, behavioral_code_dict = \
      h5_helper.h5_to_df(path_obj, start_date, end_date, monkey_input, save_df)
  # unpickle preprocessed data
  else:
    print('\nFiles uploaded from processed folder\n')
    all_selected_dates = h5_helper.date_selector(start_date, end_date)
    target_dir = os.listdir(path_obj.target_path)
    pkl_files_selected, dates_array = h5_helper.file_selector(target_dir, all_selected_dates, monkey_input)
    print('Pickled Files:')
    pprint(pkl_files_selected, indent=2)
    for f_index, f in enumerate(pkl_files_selected):
      target_pickle = os.path.join(path_obj.target_path, f)
      if os.path.exists(target_pickle):
        session_dict = pd.read_pickle(target_pickle)
        if f_index == 0:
          session_df = session_dict['data_frame']
          error_dict = session_dict['error_dict']
          behavioral_code_dict = session_dict['behavioral_code_dict']
        else:
          session_df_new = session_dict['data_frame']
          session_df = pd.concat([session_df, session_df_new], ignore_index=True)
          error_dict = session_dict['error_dict']
          behavioral_code_dict = session_dict['behavioral_code_dict']    
      else:
        print('\nPickled files missing. Reprocess or check data.')
        sys.exit()
      # session_obj contains session metadata
      session_obj = Session(session_df, monkey_input, experiment_name, behavioral_code_dict)
    
  # Save path for figures
  FIGURE_SAVE_PATH = image_diff(session_df,
                                session_obj,
                                path_obj,
                                combine_dates=combine_dates) # True will combine all dates into analysis
  session_obj.save_paths(path_obj.target_path, 
                          path_obj.tracker_path, 
                          path_obj.video_path,
                          FIGURE_SAVE_PATH)  
  
  # add external camera data
  session_df, session_obj = add_external_cameras(session_df, session_obj)  
  print(indent(pformat(session_df.columns), '  '))

  return session_df, session_obj, error_dict, behavioral_code_dict
import os
import sys
import pandas as pd
from textwrap import indent
from pprint import pprint, pformat
# Custom modules
import h5_helper
from pprint import pprint
from image_diff import image_diff
# Custom classes
from Session import Session

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
          session_df = session_df.append(session_df_new, ignore_index=True)
          error_dict = session_dict['error_dict']
          behavioral_code_dict = session_dict['behavioral_code_dict']    
      else:
        print('\nPickled files missing. Reprocess or check data.')
        sys.exit()
      # session_obj contains session metadata
      session_obj = Session(session_df, monkey_input, experiment_name, behavioral_code_dict)
      print(indent(pformat(session_df.columns), '  '))
    
  # combine_dates = True will combine all dates into analysis
  FIGURE_SAVE_PATH = image_diff(session_df,
                                session_obj,
                                path_obj,
                                combine_dates=combine_dates)
  print('Saving figures to: {}'.format(FIGURE_SAVE_PATH))
  session_obj.save_paths(path_obj.target_path, 
                          path_obj.tracker_path, 
                          path_obj.video_path,
                          FIGURE_SAVE_PATH)

  return session_df, session_obj, error_dict, behavioral_code_dict
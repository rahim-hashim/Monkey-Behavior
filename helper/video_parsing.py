import os
import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def get_frames(file_path):
   '''Implements OpenCV to read video file and return a list of frames'''
   cap = cv2.VideoCapture(file_path)
   # Get frame count
   frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
   # Get frame rate
   frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
   # Get frame size
   frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
   frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
   frame_size = (frame_width, frame_height)
   # Get duration
   duration = frame_count / frame_rate
   print('  Frame Count  : ', frame_count)
   print('  Frame Rate   : ', frame_rate)
   print(f'  Frame Size   :  {frame_width} x {frame_height}')
   # Check if the video file was successfully opened
   if not cap.isOpened():
      print("Error opening video file")
   frames = []
   # Read until video is completed
   while True:
      # Read next frame
      success, frame = cap.read()
      if not success:
         break
      # Add frame to list of frames
      frames.append(frame)
   cap.release()
   cv2.destroyAllWindows()
   return frames, frame_size

def find_epoch_frames(epoch_selected, trial_frame_times, epoch_start, epoch_end, v_index):
   '''
   Find the closest frame to the epoch start and end times
   
   Args:
      trial_frame_times (list): list of frame times for a trial
      epoch_start (list): list of epoch start times for a trial
      epoch_end (list): list of epoch end times for a trial
      v_index (int): index of the epoch start and end times

   Returns:
      frame_start_index (int): index of the closest frame to the epoch start time
      frame_end_index (int): index of the closest frame to the epoch end time
      start_frame (float): frame time of the closest frame to the epoch start time
      end_frame (float): frame time of the closest frame to the epoch end time
   '''
   epoch_start_time = epoch_start[v_index]
   epoch_end_time = epoch_end[v_index]
   print('Timings:')
   print(f'  {epoch_selected}  Dur   :  {epoch_end_time-epoch_start_time}')
   # Find the closest frame to the trace start and end times
   start_frame = min(trial_frame_times, key=lambda x: abs(x - epoch_start_time))
   end_frame = min(trial_frame_times, key=lambda x: abs(x - epoch_end_time))
   frame_start_index = list(trial_frame_times).index(start_frame)
   frame_end_index = list(trial_frame_times).index(end_frame)
   # To confirm that the closest frame is within the trace start and end times
   if start_frame < epoch_start_time:
      frame_start_index += 1
      start_frame = trial_frame_times[frame_start_index]
   if end_frame > epoch_end_time:
      frame_end_index -= 1
      end_frame = trial_frame_times[frame_end_index]
   print(f'  {epoch_selected}  Start :  {epoch_start_time}')
   print(f'  Start Frame  :  {round(start_frame)}')
   print(f'  {epoch_selected} End    :  {epoch_end_time}')
   print(f'  End Frame    :  {round(end_frame)}')
   return epoch_start_time, frame_start_index, frame_end_index, start_frame, end_frame

def eye_parsing(df, session_obj):
   pass

def behavior_parsing(df, session_obj, epoch_selected):
   print('Behavior')
   print('  Lick Duration: {}'.format(df['lick_duration'].iloc[0]))
   print('  Pupil Zero Duration: {}'.format(df['pupil_raster_window_avg'].iloc[0]))
   print('  Blink Duration: {}'.format(df['blink_duration_window'].iloc[0]))

def video_parsing(df, session_obj, trial_specified=None):
   '''
   Parse video files and extract frames for a specified epoch

   Args:
      df (DataFrame): DataFrame containing trial information
      session_obj (Session): Session object containing session information
      trial_specified (int): trial number to parse

   Returns:
      None
   '''
   date = df['date'].iloc[0]
   # Filter dataframe by trial number
   if trial_specified:
      df = df[df['trial_num'] == trial_specified]
   list_files = df['cam1_trial_name'].tolist()
   list_frame_times = df['cam1_trial_time'].tolist()
   epoch_selected = 'Outcome'
   behavior_parsing(df, session_obj, epoch_selected)
   eye_x = df['eye_x'].tolist()[0]
   eye_y = df['eye_y'].tolist()[0]
   lick_data = df['lick_raster'].tolist()[0]
   pupil_data = df['eye_pupil'].tolist()[0]
   blink_raster = df['blink_raster'].tolist()[0]
   pupil_zero_raster = [1 if x == 0 else 0 for x in pupil_data]
   start_str = epoch_selected + ' Start'
   end_str = epoch_selected + ' End'
   epoch_start = df[start_str].tolist()
   epoch_end = df[end_str].tolist()
   lick_raster_epoch = lick_data[epoch_start[0]:epoch_end[0]]
   pupil_raster_epoch = pupil_data[epoch_start[0]:epoch_end[0]]
   pupil_zero_raster_epoch = pupil_zero_raster[epoch_start[0]:epoch_end[0]]
   blink_raster_epoch = blink_raster[epoch_start[0]:epoch_end[0]]
   eye_x_epoch = eye_x[epoch_start[0]:epoch_end[0]]
   eye_y_epoch = eye_y[epoch_start[0]:epoch_end[0]]
   # Open .mp4 file
   for v_index, video_file in enumerate(list_files):
      # f, axarr = plt.subplots(1, 2)
      video_path_date = os.path.join(session_obj.video_path, date)
      file_name = video_file+'.mp4'
      file_path = os.path.join(video_path_date, file_name)
      if file_name in os.listdir(video_path_date):
         print('Video File: ', file_name)
         trial_frame_times = list_frame_times[v_index]
         # Get all frames from the video file
         frames, frame_size = get_frames(file_path)
         # Find the frames that correspond to the trace start and end times
         epoch_start_time, frame_start_index, frame_end_index, start_frame, end_frame = \
            find_epoch_frames(epoch_selected, trial_frame_times, epoch_start, epoch_end, v_index)
         for f_index, frame in enumerate(frames[frame_start_index:frame_end_index]):
            frame_time_in_epoch = round(trial_frame_times[f_index+frame_start_index] - epoch_start_time)
            lick_binary = lick_raster_epoch[frame_time_in_epoch]
            pupil_binary = round(pupil_raster_epoch[frame_time_in_epoch])
            blink_binary = round(blink_raster_epoch[frame_time_in_epoch])
            if lick_binary:
               lick_color = (0, 0, 255)
            else:
               lick_color = (255, 255, 255)
            if pupil_binary == 0:
               pupil_color = (255, 0, 0)
            else:
               pupil_color = (255, 255, 255)
            if blink_binary:
               blink_color = (255, 0, 0)
            else:
               blink_color = (255, 255, 255)
            if frame_size == (320, 240):
               frame = cv2.resize(frame, (640, 480))
            cv2.putText(frame, 'Time: '+str(frame_time_in_epoch), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, f'Eye X/Y: ({round(eye_x_epoch[frame_time_in_epoch], 1)},{round(eye_y_epoch[frame_time_in_epoch], 1)})', 
                  (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, 'Lick: '+str(lick_binary), 
                  (540, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, lick_color, 2)
            cv2.putText(frame, 'Blink: '+str(blink_binary), 
                  (540, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blink_color, 2)
            cv2.putText(frame, 'Pupil: '+str(pupil_binary), 
                  (540, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, pupil_color, 2)
            plt.imshow(frame)
            plt.show()
      if v_index > 5:
         break
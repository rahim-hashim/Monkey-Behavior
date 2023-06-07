import os
import cv2

class Path:
  def __init__(self, ROOT, EXPERIMENT, TASK, DATE):
    self.date = DATE
    self.root = ROOT
    data_dir = os.listdir(os.path.join('..', 'data', 'processed'))
    # find TASK in data_dir
    task_path = [x for x in data_dir if TASK in x][0]
    # find date in processed data directory
    processed_data_path = os.path.join('..', 'data', 'processed', task_path)
    self.session = [x for x in os.listdir(os.path.join(processed_data_path)) \
               if DATE in x][0]
    self.session_path  = os.path.join(processed_data_path, self.session)
    # find task in EXPERIMENT directory
    task_dir = os.path.join('..', 'tasks', EXPERIMENT)
    task_folder = [x for x in os.listdir(task_dir) if TASK in x][0]
    # find video in TASK directory
    self.video_path = os.path.join(task_dir, task_folder, 'videos')
    # where the extracted images from video_path will be saved
    self.images_path = os.path.join(ROOT, 'data', DATE)
    # Create directory to save frames
    if os.path.exists(self.images_path) == False:
      if os.path.exists(os.path.join(ROOT, 'data')) == False:
        os.mkdir(os.path.join(ROOT, 'data'))
      os.mkdir(self.images_path)

class FaceLandmarks:
  def __init__(self):
    ## see: https://stackoverflow.com/questions/30508922/error-215-empty-in-function-detectmultiscale
    self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    # from: https://www.youtube.com/watch?v=-TVUwH1PgBs
    # left eye indices
    self.left_eye = [22, 23, 24, 26, 110, 130, 157, 158, 159, 160, 161, 243]
    self.left_eye_top, self.left_eye_bottom = 23, 159
    self.left_eye_left, self.left_eye_right = 130, 243
    self.left_eyebrow = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
    # right eye indices
    self.right_eye = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    self.right_eyebrow = [336, 296, 334, 293, 300, 276, 283, 282, 295, 285 ]
    # all eyes
    self.eyes = self.left_eye + self.right_eye
    # self.right_eye = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    # lips indices
    self.lip = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375,291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95,185, 40]
    self.lower_lip = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
    self.upper_lip = [185, 40, 39, 37,0 ,267 ,269 ,270,409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78]
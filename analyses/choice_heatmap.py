import os
import numpy as np
from itertools import combinations
from matplotlib import pyplot as plt

def update_choice_matrix(choice_matrix, valences, df):
  for v_1_index, valence_1 in enumerate(valences):
    for v_2_index, valence_2 in enumerate(valences):
      if v_1_index == v_2_index:
        choice_matrix[v_1_index][v_2_index] = 0.5
        continue
      df_valence_1 = df[(df['valence_1'] == valence_1) &
                            (df['valence_2'] == valence_2) & 
                            (df['valence'] == valence_1)]
      df_valence_2 = df[(df['valence_1'] == valence_1) &
                            (df['valence_2'] == valence_2) &
                            (df['valence'] == valence_2)]
      if len(df_valence_1) + len(df_valence_2) == 0:
        # empty matrix
        choice_matrix[v_1_index][v_2_index] = np.nan
      else:
        proportion_val_1 = len(df_valence_1)/(len(df_valence_1)+len(df_valence_2))
        choice_matrix[v_1_index][v_2_index] = proportion_val_1
  return choice_matrix

def generate_ideal_matrix(choice_matrix, valences):
  for v_1_index, valence_1 in enumerate(valences):
    for v_2_index, valence_2 in enumerate(valences):
      if v_1_index == v_2_index:
        choice_matrix[v_1_index][v_2_index] = 0.5
        continue
      else:
        if valence_1 > valence_2:
          choice_matrix[v_1_index][v_2_index] = 1
        else:
          choice_matrix[v_1_index][v_2_index] = 0

  return choice_matrix

def plot_choice_valence(df, session_obj, ):
  '''heat map of choice trials'''
  FIGURE_SAVE_PATH = session_obj.figure_path
  # only get choice trials that are non-zero valence
  session_choice = df[(df['choice_trial'] == 1) & \
                      (df['fractal_count_in_block'] > 5)]
  session_choice = session_choice[(session_choice['valence_1'] != 0)]
  # get unique conditions
  f, axarr = plt.subplots(2,2)
  cmap = plt.cm.RdYlGn
  cmap.set_bad(color='black')  
  conditions = list(sorted(df['condition'].unique()))
  # get unique valences
  valences = sorted(df['valence_1'].unique(), reverse=True)
  for index, plot in enumerate(range(len(axarr.flat))):
    # empty matrix of zeros
    choice_matrix = np.zeros((len(valences), len(valences)))
    # condition specific
    if index < 2:
      condition = conditions[index]
      df_cond = df[df['condition'] == condition]
      choice_matrix = update_choice_matrix(choice_matrix, valences, df_cond)
      title = 'Condition {}'.format(condition)
    # all conditions
    elif index == 2:
      choice_matrix = update_choice_matrix(choice_matrix, valences, df)
      title = 'All Conditions'
    # ideal behavior
    elif index == 3:
      choice_matrix = generate_ideal_matrix(choice_matrix, valences)
      title = 'Ideal Behavior'

    # plot matrix
    row = 0
    if index >= 2:
      row = 1
    col = index % 2
    cbar = axarr[row][col].figure.colorbar(axarr[row][col].imshow(choice_matrix.T, cmap=cmap, vmin=0, vmax=1))
    axarr[row][col].set_title(title, fontsize=14)

    # legend for color bar
    axarr[row][col].set_xlabel('Stimulus L', fontsize=12)
    axarr[row][col].set_ylabel('Stimulus R', fontsize=12)
    axarr[row][col].set_xticks(range(len(valences)))
    axarr[row][col].set_yticks(range(len(valences)))
    axarr[row][col].set_xticklabels(valences, fontsize=8)
    axarr[row][col].set_yticklabels(valences, fontsize=8)

  f.suptitle('         Probability of Choosing Stimulus L', fontsize=18)
  f.tight_layout()
  plot_title = 'choice_heatmap.png'
  img_save_path = os.path.join(FIGURE_SAVE_PATH, plot_title)
  f.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches = 0.1)
  print(f'  {plot_title} saved.')
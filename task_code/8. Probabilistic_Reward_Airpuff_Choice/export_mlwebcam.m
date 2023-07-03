%% Run ML Webcam Export 
% For more info:
%   MonkeyLogic - https://monkeylogic.nimh.nih.
%   Functions - https://monkeylogic.nimh.nih.gov/docs_RuntimeFunctions.html#mlexportwebcam

function export_mlwebcam

disp('Performing mlexportwebcam function...')
ml_start = tic;
mlexportwebcam(delete_video=true);  % custom MonkeyLogic function 
ml_end = toc(ml_start);
disp(['Export complete. Elapsed time: ' num2str(ml_end)])

%% Moving Files
% Define the parent directory and folder name
parent_dir = pwd;
folder_name = 'videos';

% Find all files in the parent directory that contain ".mp4" in the name
files_to_move = dir(fullfile(parent_dir, '*.mp4*'));
if isempty(files_to_move)
    disp('No video files for specified session')
    return
end

% Get the current date and monkey name
date_split = split(files_to_move(1).name, '_');
date = date_split{1};
file_str = horzcat([date, '_', date_split{2}]);

% Create new 'videos' directory
videos_dir = fullfile(parent_dir, folder_name);
if ~exist(videos_dir, 'dir')
    mkdir_str = horzcat(['Making new directory: ', videos_dir]);
    disp(mkdir_str)
    mkdir(videos_dir)
end

% Create directory for specific session
date_dir = fullfile(parent_dir, folder_name, file_str);
if ~exist(date_dir, 'dir')
    disp('Making new directory:')
    mkdir(date_dir)
    mkdir_str = horzcat([' ', date_dir]);
    disp(mkdir_str)
end

% Loop through each file and move it to the new directory
moving_str = sprintf("Moving %d files to new directory", length(files_to_move));
disp(moving_str)
for i = 1:length(files_to_move)
    old_file_path = fullfile(parent_dir, files_to_move(i).name);
    new_file_path = fullfile(date_dir, files_to_move(i).name);
    movefile(old_file_path, new_file_path, "f");
end

disp(' Complete.')
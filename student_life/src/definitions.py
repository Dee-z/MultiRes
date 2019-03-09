import os
import pathlib

from src.utils.read_utils import read_yaml

# Defining Root Directory of the project.
ROOT_DIR = str(pathlib.Path(os.path.dirname(os.path.abspath(__file__))))
USER_HOME = pathlib.Path.home()

# File and Key Names
STUDENT_FOLDER_NAME_PREFIX = "student_"
BINNED_DATA_FILE_NAME = "var_binned_data"
BINNED_DATA_MISSING_VALES_FILE_NAME = "missing_values_mask"
BINNED_DATA_TIME_DELTA_FILE_NAME = "time_deltas_min"

# Config File Path
FEATURE_CONFIG_FILE_PATH = os.path.join(ROOT_DIR, "configurations/feature_processing.yaml")
DATA_MANAGER_CONFIG_FILE_PATH = os.path.join(ROOT_DIR, "configurations/data_manager_config.yaml")
MODEL_CONFIG_FILE_PATH = os.path.join(ROOT_DIR, "configurations/model_config.yaml")

# Frequency constants
DEFAULT_BASE_FREQ = 'min'

# Data manager config Keys
VAR_BINNED_DATA_MANAGER_ROOT = "student_life_var_binned_data"

# Universal Config Keys.
STUDENT_LIST_CONFIG_KEY = "student_list"
FEATURE_LIST_CONFIG_KEY = "feature_list"
LABEL_LIST_CONFIG_KEY = "label_list"
RESAMPLE_FREQ_CONFIG_KEY = "resample_freq_min"

# Data Folder Paths - LOCAL
MINIMAL_PROCESSED_DATA_PATH = str(os.path.join(ROOT_DIR, "../data/student_life_minimal_processed_data"))
BINNED_ON_VAR_FREQ_DATA_PATH = str(os.path.join(ROOT_DIR, "../data/student_life_var_binned_data"))

# Data Folder Paths - CLUSTER
# Overwrite Global Constants when cluster mode on.
config = read_yaml(FEATURE_CONFIG_FILE_PATH)
if config['cluster_mode']:
    cluster_data_root = config['data_paths']['cluster_data_path']
    MINIMAL_PROCESSED_DATA_PATH = pathlib.Path(
        os.path.join(cluster_data_root, "student_life_minimal_processed_data"))
    BINNED_ON_VAR_FREQ_DATA_PATH = pathlib.Path(
        os.path.join(cluster_data_root, "student_life_var_binned_data"))

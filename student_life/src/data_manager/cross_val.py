import numpy as np

from random import shuffle
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from src.utils import data_conversion_utils as conversions


SPLITTER_RANDOM_STATE = 100


def random_stratified_splits(data: dict, stratify_by="labels"):
    """

    @param data: Data in classic dict format.
    @param stratify_by: By what the splits need to be stratified.
           Accepts - `labels` and `students`.
    @return: Return splits which are randomize and stratified by labels.
    """
    keys, labels = conversions.extract_keys_and_labels_from_dict(data)
    keys, labels = np.array(keys), np.array(labels)

    if stratify_by == "students":
        student_ids = conversions.extract_student_ids_from_keys(keys)
        stratification_array = np.array(student_ids)
    else:
        stratification_array = labels

    (X_train, X_test,
     y_train, y_test,
     stratification_array, new_stratification_array) = train_test_split(keys,
                                                                        labels,
                                                                        stratification_array,
                                                                        test_size=0.40,
                                                                        shuffle=True,
                                                                        stratify=stratification_array)
    X_val, X_test = train_test_split(X_test,
                                     test_size=0.40,
                                     shuffle=True,
                                     stratify=new_stratification_array)

    return X_train.tolist(), X_val.tolist(), X_test.tolist()


def leave_one_subject_out_split(data: dict):
    """

    @param data: data for which the splits are needed to be generated.
    @return: Return generator object with different data split,
             with test and val belonging to the left out student.
    """

    keys, labels = conversions.extract_keys_and_labels_from_dict(data)
    student_ids = conversions.extract_distinct_student_idsfrom_keys(keys)

    for idx, left_out_student in enumerate(student_ids):
        students_for_training = student_ids[:idx] + student_ids[idx + 1:]
        train_ids = conversions.get_filtered_keys_for_these_students(*students_for_training, keys=keys)
        val_test_ids = conversions.get_filtered_keys_for_these_students(left_out_student, keys=keys)

        shuffle(train_ids)
        shuffle(val_test_ids)

        data['train_ids'] = train_ids
        val_len = len(val_test_ids)
        data['val_ids'] = val_test_ids
        data['test_ids'] = []

        yield data, left_out_student


def get_k_fod_cross_val_splits_stratified_by_students(data: dict, n_splits=5,
                                                      stratification_type="student_label",
                                                      filter_by_student_ids=None):
    splits = []

    data_keys = data['data'].keys()
    keys, labels = conversions.extract_keys_and_labels_from_dict(data)
    student_ids = conversions.extract_student_ids_from_keys(keys)
    student_ids_label = []

    if filter_by_student_ids is not None:
        student_ids, labels, data_keys = filter_student_id(filter_by_student_ids, student_ids, labels, list(data_keys))

    for i in range(len(student_ids)):
        student_ids_label.append(str(student_ids[i]) + "_" + str(labels[i]))

    student_ids_label = np.array(student_ids_label)
    data_keys = np.array(list(data_keys))
    student_ids = conversions.convert_list_of_strings_to_list_of_ints(student_ids)

    if stratification_type == "student":
        stratification_column = student_ids
    else:
        stratification_column = student_ids_label

    print(stratification_type)

    splitter = StratifiedKFold(n_splits=n_splits, random_state=SPLITTER_RANDOM_STATE)
    for train_index, val_index in splitter.split(X=data_keys, y=stratification_column):

        splitting_dict = {}
        splitting_dict['train_ids'] = data_keys[train_index].tolist()
        splitting_dict['val_ids'] = data_keys[val_index].tolist()
        splits.append(splitting_dict)

    return splits


def filter_student_id(filter_by_student_ids, student_id_list, labels_list, data_keys):
    filtered_student_id_list, filtered_labels_list, filtered_data_keys = [], [], []

    for idx, student_id in enumerate(student_id_list):
        if conversions.convert_to_int_if_str(student_id) in filter_by_student_ids:
            filtered_student_id_list.append(student_id)
            filtered_labels_list.append(labels_list[idx])
            filtered_data_keys.append(data_keys[idx])

    return filtered_student_id_list, filtered_labels_list, filtered_data_keys

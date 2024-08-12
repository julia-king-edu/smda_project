from copy import deepcopy
import pandas as pd
import json
import csv

# create helper function that i can include in codeblocks so it will request a confirmation of execution (to prevent unintentional deletion of data or usage of quotas)

def confirm_execution(prompt : str = "The current cell may delete previously gathered data or make a large number of requests. Do you want to execute it?"):
    """helper function that i can include in codeblocks so it will request a confirmation of execution (to prevent unintentional deletion of data or usage of quotas)

    Args:
        prompt (str, optional): What to prompt. Defaults to "The current cell may delete previously gathered data or make a large number of requests. Do you want to execute it?".
    """
    reset = input(f"{prompt} (yes/anything else): ").strip().lower()

    if reset != "yes":
        raise Exception("Execution aborted by user.")
    
    return


# write functions to write / load the search_results json (separate function is necessary as it needs to store datetime values. these need to be converted to string before saving and from string when loading)

def write_search_json(search_results : list, location : str = "data/search_results.json"):
    """Writes the given object to the results file of the search endpoint. Careful not to overwrite anything!

    Args:
        search_results (list): the results of the search endpoint so far
        location (str, optional): File location. Defaults to "data/search_results.json".
    """

    # copy so workspace version is not affected
    sr_copy = deepcopy(search_results)
    
    def datetime_to_str(dt):
        return dt.isoformat()

    def convert_for_write(entry):
        result = {}
        for key, value in entry.items():
            start, end = key
            # Convert datetime objects to ISO format strings
            result[f"{datetime_to_str(start)}${datetime_to_str(end)}"] = value
        return result

    # Convert the datetimes to string format
    saveable = [convert_for_write(phase) for phase in sr_copy]

    # Save to json
    with open(location, "w") as f:
        json.dump(saveable, f, indent = 4)

def read_search_json(location : str = "data/search_results.json") -> list:
    """Reads the results of the search endpoint so far.

    Args:
        location (str, optional): File Location. Defaults to "data/search_results.json".

    Returns:
        list: the results of the search endpoint so far
    """
    
    def str_to_datetime(s):
        return pd.to_datetime(s)

    def convert_after_read(entry):
        result = {}
        for key, value in entry.items():
            start_str, end_str = key.split("$")
            # Convert ISO format strings to datetime objects
            start = str_to_datetime(start_str)
            end = str_to_datetime(end_str)
            result[(start, end)] = value
        return result

    with open(location, "r") as f:
        loaded = json.load(f)

    # Apply conversion to each dictionary in the list
    search_results = [convert_after_read(entry) for entry in loaded]

    return search_results



# write functions to write / load the video data json (separate function is necessary as datetime values are stored. these need to be converted to string before saving and from string when loading)

def write_video_json(video_json : list, location : str = "data/videos.json"):
    """Writes the given object to the results file of the video data including metadata and comments. Careful not to overwrite anything!

    Args:
        video_json (list): the video data including metadata and comments generated so far
        location (str, optional): File location. Defaults to "data/videos.json".
    """
    
    # copy so workspace version is not affected
    vd_copy = deepcopy(video_json)
    
    def datetime_to_str(dt):
        return dt.isoformat()

    def convert_for_write(vd):
        for i in range(len(vd)):
            vd[i]["week_start"] = datetime_to_str(vd[i]["week_start"])
        return vd
            

    # Convert the datetimes to string format
    saveable = convert_for_write(vd_copy)

    # Save to json
    with open(location, "w") as f:
        json.dump(saveable, f, indent=4)

def read_video_json(location : str = "data/videos.json") -> list:
    """Reads the video data including metadata and comments generated so far.

    Args:
        location (str, optional): File Location. Defaults to "data/videos.json".

    Returns:
        list: the video data including metadata and comments generated so far
    """
    
    def str_to_datetime(s):
        return pd.to_datetime(s)

    def convert_after_read(vd):
        for i in range(len(vd)):
            vd[i]["week_start"] = str_to_datetime(vd[i]["week_start"])
        return vd

    with open(location, "r") as f:
        loaded = json.load(f)

    # Apply conversion to each dictionary in the list
    video_json = convert_after_read(loaded)

    return video_json

# functions to read/write the manual sample

def write_manual_sample(manual_sample : pd.DataFrame, filepath : str = "data/manual_sample.csv"):
    """Write the manual sample to a csv. Careful not to overwrite!

    Args:
        manual_sample (pd.DataFrame): manual sample
        filepath (str, optional): file path to save to. Defaults to "data/manual_sample.csv".
    """
    
    manual_sample.to_csv(filepath, index = False, quoting = csv.QUOTE_MINIMAL)
    
def read_manual_sample(filepath : str = "data/manual_sample.csv") -> pd.DataFrame:
    """Reads manual sample file, mostly here to complete the read/write function set.

    Args:
        filepath (str, optional): file path to manual sample file. Defaults to "data/manual_sample.csv".

    Returns:
        pd.DataFrame: maunual sample
    """

    manual_sample = pd.read_csv(filepath)
    manual_sample["conspirative"] = pd.to_numeric(manual_sample["conspirative"], errors = "coerce")
    manual_sample["conspirative"] = manual_sample["conspirative"].astype("boolean")
    return manual_sample

# functions to read/write the video df

def write_video_df(video_df : pd.DataFrame, filepath : str = "data/videos.csv"):
    """Write the manual sample to a csv. Careful not to overwrite!

    Args:
        manual_sample (pd.DataFrame): video df generated in data_processing
        filepath (str, optional): file path to save to. Defaults to "data/videos.csv".
    """
    
    video_df.to_csv(filepath, quoting = csv.QUOTE_MINIMAL)
    
def read_video_df(filepath : str = "data/videos.csv") -> pd.DataFrame:
    """Reads manual sample file, mostly here to complete the read/write function set.

    Args:
        filepath (str, optional): file path to manual sample file. Defaults to "data/videos.csv".

    Returns:
        pd.DataFrame: maunual sample
    """
    
    video_df = pd.read_csv(filepath)
    # convert label cols
    label_cols = [col for col in video_df if col.startswith("conspirative_")]
    for col in label_cols:
        video_df[col] = pd.to_numeric(video_df[col], errors = "coerce")
        video_df[col] = video_df[col].astype("boolean")
    
    # set id as index
    video_df = video_df.set_index("id")
    
    return video_df

def convert_conspirative_to_bool(df : pd.DataFrame) -> pd.DataFrame:
    # generate docstring by typing """
    
    df_copy = deepcopy(df)
    label_cols = [col for col in df_copy if col.startswith("conspirative_")]
    df_copy[label_cols] = df_copy[label_cols].astype("boolean")
    return df_copy
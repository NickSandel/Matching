import pandas as pd
from pandas.testing import assert_frame_equal
from pathlib import Path
import sys

# root directory
root_path = Path.cwd()
sys.path.append(str(root_path.resolve()))
from MatchingFunctions import *

def test_basic_cleaning():
    data = {'ID1_source': ['Value1', None, 'VALUE3'], 'ID2_source': ['VALUE2', 'value2', 'value2 value 3']}
    df = pd.DataFrame(data)
    expected_cleaned_data =  {'ID1_source': ['value1', None, 'value3'], 'ID2_source': ['value2', 'value2', 'value2value3']}
    expected_cleaned_data_df = pd.DataFrame(expected_cleaned_data)
    clean_columns = ['ID1_source', 'ID2_source']

    cleaned_df = clean_string_columns(df, clean_columns)
    assert_frame_equal(cleaned_df, expected_cleaned_data_df)

def test_namesplitting():
    # Example usage:
    data = {'Forename': ['John', 'Jane Mary', 'Alice Bob Charlie', 'Mike John', 'Sarah Anne'], 'MiddleNames': [None, None, None, 'Existing', None]}
    df = pd.DataFrame(data)

    expected_df = pd.DataFrame({'Forename': ['John', 'Jane', 'Alice', 'Mike John', 'Sarah'], 'MiddleNames': [None, 'Mary', 'Bob Charlie', 'Existing', 'Anne']})

    cleaned_df = clean_names(df)
    print(cleaned_df)
    print(expected_df)
    assert_frame_equal(cleaned_df, expected_df)
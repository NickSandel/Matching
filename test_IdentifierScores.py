from pathlib import Path
import sys

# root directory
root_path = Path.cwd()
sys.path.append(str(root_path.resolve()))
from MatchingFunctions import *

identifiers = ['UPN', 'NHS_Number']

def test_onePos():
    row_data = {
        'UPN_source': 'value1',
        'UPN_target': 'value1',
        'NHS_Number_source': 'value2',
        'NHS_Number_target': ''
    }
    assert(score_identifiers(row_data, identifiers)) == 1.0

def test_oneNeg():
    row_data = {
        'UPN_source': 'value1',
        'UPN_target': 'value10',
        'NHS_Number_source': 'value2',
        'NHS_Number_target': ''
    }
    assert(score_identifiers(row_data, identifiers)) == 0.0

def test_onePos_oneNeg():
    row_data = {
        'UPN_source': 'value1',
        'UPN_target': 'value1',
        'NHS_Number_source': 'value2',
        'NHS_Number_target': 'value4'
    }
    assert(score_identifiers(row_data, identifiers)) == 0.6

def test_allMissing():
    row_data = {
        'UPN_source': '',
        'UPN_target': '',
        'NHS_Number_source': None,
        'NHS_Number_target': None
    }
    assert(score_identifiers(row_data, identifiers)) == 0.5

def test_onePos_oneNaN():
    row_data = {
        'UPN_source': 'A12345',
        'UPN_target': 'A12345',
        'NHS_Number_source': np.nan,
        'NHS_Number_target': np.nan
    }
    assert(score_identifiers(row_data, identifiers)) == 1.0
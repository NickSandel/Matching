from pathlib import Path
import sys

# root directory
root_path = Path.cwd()
sys.path.append(str(root_path.resolve()))
from MatchingFunctions import *

def test_Exact():
    row_data = {
        'Postcode_source': 'RG14 1AB',
        'Postcode_target': 'RG14 1AB'
    }
    assert(score_location(row_data)) == 1.0

def test_SpaceDiff():
    row_data = {
        'Postcode_source': 'RG14 1AB',
        'Postcode_target': 'RG141AB'
    }
    assert(score_location(row_data)) == 1.0

def test_SourceMissing():
    row_data = {
        'Postcode_source': '',
        'Postcode_target': 'RG14 1AB'
    }
    assert(score_location(row_data)) == 0.75

def test_TargetMissing():
    row_data = {
        'Postcode_source': 'RG14 1AB',
        'Postcode_target': ''
    }
    assert(score_location(row_data)) == 0.75

def test_Mismatch():
    row_data = {
        'Postcode_source': 'RG13 1AB',
        'Postcode_target': 'RG14 2CD'
    }
    assert(score_location(row_data)) == 0.0

def test_None():
    row_data = {
        'Postcode_source': 'RG14 1AB',
        'Postcode_target': None
    }
    assert(score_location(row_data)) == 0.75

def test_First5():
    row_data = {
        'Postcode_source': 'RG14 1AB',
        'Postcode_target': 'RG14 1'
    }
    assert(score_location(row_data)) == 0.8

def test_First5_again():
    row_data = {
        'Postcode_source': 'RG14 1AB',
        'Postcode_target': 'RG14 1CD'
    }
    assert(score_location(row_data)) == 0.8


def test_First4():
    row_data = {
        'Postcode_source': 'RG1 1AB',
        'Postcode_target': 'RG1 1XD'
    }
    assert(score_location(row_data)) == 0.78
from pathlib import Path
import sys

# root directory
root_path = Path.cwd()
sys.path.append(str(root_path.resolve()))
from MatchingFunctions import *
from datetime import datetime

def test_Exact():
    row_data = {
        'DateOfBirth_source': datetime(1986,11,11),
        'DateOfBirth_target': datetime(1986,11,11)
    }
    assert(score_dob(row_data)) == 1.0

def test_Within5days():
    row_data = {
        'DateOfBirth_source': datetime(1986,11,11),
        'DateOfBirth_target': datetime(1986,11,6)
    }
    assert(score_dob(row_data)) == 0.9

def test_FarOut():
    row_data = {
        'DateOfBirth_source': datetime(1978,5,8),
        'DateOfBirth_target': datetime(1986,11,6)
    }
    assert(score_dob(row_data)) == 0

def test_MonthDaySwapped():
    row_data = {
        'DateOfBirth_source': datetime(1986,6,11),
        'DateOfBirth_target': datetime(1986,11,6)
    }
    assert(score_dob(row_data)) == 0.9

def test_YearWrong():
    row_data = {
        'DateOfBirth_source': datetime(1989,6,11),
        'DateOfBirth_target': datetime(1986,6,11)
    }
    assert(score_dob(row_data)) == 0.5

def test_DayWrong():
    row_data = {
        'DateOfBirth_source': datetime(1986,6,30),
        'DateOfBirth_target': datetime(1986,6,11)
    }
    assert(score_dob(row_data)) == 0.8

def test_MonthWrong():
    row_data = {
        'DateOfBirth_source': datetime(1986,5,11),
        'DateOfBirth_target': datetime(1986,6,11)
    }
    assert(score_dob(row_data)) == 0.8
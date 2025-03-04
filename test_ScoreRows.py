from pathlib import Path
import sys

# root directory
root_path = Path.cwd()
sys.path.append(str(root_path.resolve()))
from MatchingFunctions import *
from datetime import datetime

def test_dummyScore():
    row_data = {
        'UPN_source': 'W608202411027',
        'UPN_target': 'W608202411027',
        'NHS_Number_source': None,
        'NHS_Number_target': None,
        'Surname_source': 'person',
        'Surname_target': 'Nick',
        'MiddleNames_source': None,
        'MiddleNames_target': None,
        'Forename_source': 'Nick',
        'Forename_target': 'person',
        'Postcode_source': 'RG14 7GE',
        'Postcode_target': 'RG1 1XD',
        'DateOfBirth_source': datetime(1986,11,11),
        'DateOfBirth_target': datetime(1986,11,11)
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) > 0.7

def test_dummyCINScore():
    row_data = {
        'UPN_source': 'W608202411027',
        'UPN_target': 'W608202411027',
        'NHS_Number_source': None,
        'NHS_Number_target': None,
        'DateOfBirth_source': datetime(1986,11,11),
        'DateOfBirth_target': datetime(1986,11,11)
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) > 0.8

def test_mismatchedPatient():
    row_data = {
        'UPN_source': 'W608202411027',
        'UPN_target': None,
        'NHS_Number_source': None,
        'NHS_Number_target': '12345678',
        'Surname_source': 'person',
        'Surname_target': 'nick',
        'MiddleNames_source': 'berlindave',
        'MiddleNames_target': 'berlin',
        'Forename_source': 'nick',
        'Forename_target': 'person',
        'DateOfBirth_source': datetime(1986,11,11),
        'DateOfBirth_target': datetime(1986,11,11)
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) > 0.7

def test_twinLowMatch():
    row_data = {
        'UPN_source': 'W608202411027',
        'UPN_target': 'Z608202411027',
        'NHS_Number_source': None,
        'NHS_Number_target': None,
        'Surname_source': 'Nicky',
        'Surname_target': 'Nick',
        'MiddleNames_source': 'berlindave',
        'MiddleNames_target': 'berlindave',
        'Forename_source': 'person',
        'Forename_target': 'person',
        'DateOfBirth_source': datetime(1986,11,11),
        'DateOfBirth_target': datetime(1986,11,11)
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) < 0.7

def test_noneFuzzyBreak():
    row_data = {
        'UPN_source': 'W608202411027',
        'UPN_target': 'Z608202411027',
        'NHS_Number_source': None,
        'NHS_Number_target': None,
        'Surname_source': 'triffid',
        'Surname_target': 'person',
        'Forename_source': 'davey',
        'Forename_target': 'claire',
        'MiddleNames_source': 'pat',
        'MiddleNames_target': None,
        'DateOfBirth_source': datetime(1986,11,11),
        'DateOfBirth_target': datetime(1986,11,11)
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) < 0.5

def test_PatientsDobOnlyNoMatch():
    row_data = {
        'NHS_Number_source': '12345678',
        'NHS_Number_target': None,
        'Surname_source': None,
        'Surname_target': 'dave',
        'Forename_source': None,
        'Forename_target': 'davey',
        'MiddleNames_source': None,
        'MiddleNames_target': None,
        'DateOfBirth_source': datetime(1986,11,11),
        'DateOfBirth_target': datetime(1986,11,11)
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) < 0.7

def test_OddNameHit():
    row_data = {
        'NHS_Number_source': '7031456908',
        'NHS_Number_target': None,
        'UPN_source': None,
        'UPN_target': 'D310208309016',
        'Surname_source': 'pere',
        'Surname_target': 'mermoure',
        'Forename_source': 'truman',
        'Forename_target': 'landmark',
        'MiddleNames_source': 'a',
        'MiddleNames_target': 'mail tornado',
        'DateOfBirth_source': datetime(2007,9,18),
        'DateOfBirth_target': datetime(2007,9,18),
        'Postcode_source': None,
        'Postcode_target': 'HA3 9'
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) < 0.7

def test_CloseNameUndermatch():
    row_data = {
        'NHS_Number_source': '123456789',
        'NHS_Number_target': '123456789',
        'UPN_source': None,
        'UPN_target': 'D310208309016',
        'Surname_source': 'white',
        'Surname_target': 'white',
        'Forename_source': 'charles',
        'Forename_target': 'charlie',
        'MiddleNames_source': '',
        'MiddleNames_target': None,
        'DateOfBirth_source': datetime(2007,9,18),
        'DateOfBirth_target': datetime(2007,9,18),
        'Postcode_source': None,
        'Postcode_target': 'HA3 9'
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) > 0.7

def test_Patients_ClosePostcode4():
    row_data = {
        'NHS_Number_source': '123456789',
        'NHS_Number_target': None,
        'UPN_source': None,
        'UPN_target': 'D310208309016',
        'Surname_source': None,
        'Surname_target': 'white',
        'Forename_source': None,
        'Forename_target': 'charlie',
        'MiddleNames_source': None,
        'MiddleNames_target': None,
        'DateOfBirth_source': datetime(2007,9,18),
        'DateOfBirth_target': datetime(2007,9,18),
        'Postcode_source': 'HA39RT',
        'Postcode_target': 'HA39'
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) < 0.7

def test_Patients_ClosePostcode5():
    row_data = {
        'NHS_Number_source': '123456789',
        'NHS_Number_target': None,
        'UPN_source': None,
        'UPN_target': 'D310208309016',
        'Surname_source': None,
        'Surname_target': 'white',
        'Forename_source': None,
        'Forename_target': 'charlie',
        'MiddleNames_source': None,
        'MiddleNames_target': None,
        'DateOfBirth_source': datetime(2007,9,18),
        'DateOfBirth_target': datetime(2007,9,18),
        'Postcode_source': 'HA39RT',
        'Postcode_target': 'HA39R'
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) < 0.7

def test_Patients_Postcode():
    row_data = {
        'NHS_Number_source': '123456789',
        'NHS_Number_target': None,
        'UPN_source': None,
        'UPN_target': 'D310208309016',
        'Surname_source': None,
        'Surname_target': 'white',
        'Forename_source': None,
        'Forename_target': 'charlie',
        'MiddleNames_source': None,
        'MiddleNames_target': None,
        'DateOfBirth_source': datetime(2007,9,18),
        'DateOfBirth_target': datetime(2007,9,18),
        'Postcode_source': 'HA3 9RT',
        'Postcode_target': 'HA3 9RT'
    }
    assert(score_row_pair(row_data, 'Test', True)['Score']) > 0.7
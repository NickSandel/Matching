from pathlib import Path
import sys

# root directory
root_path = Path.cwd()
sys.path.append(str(root_path.resolve()))
from MatchingFunctions import *

def test_exact():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'Nick',
        'MiddleNames_source': 'berlin',
        'MiddleNames_target': 'berlin',
        'Surname_source': 'person',
        'Surname_target': 'person'
    }

    assert(score_names(row_data, debug=True)) == 1.0

def test_forenameNickname():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'Nicholas',
        'MiddleNames_source': 'berlin',
        'MiddleNames_target': 'berlin',
        'Surname_source': 'person',
        'Surname_target': 'person'
    }
    assert(score_names(row_data, debug=True)) == 0.85

def test_middlenameMissing_source():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'Nick',
        'MiddleNames_source': '',
        'MiddleNames_target': 'berlin',
        'Surname_source': 'person',
        'Surname_target': 'person'
    }

    assert(score_names(row_data, debug=True)) == 1.0

def test_middlenameMissing_target():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'Nick',
        'MiddleNames_source': 'berlin',
        'MiddleNames_target': None,
        'Surname_source': 'person',
        'Surname_target': 'person'
    }

    assert(score_names(row_data, debug=True)) == 1.0

def test_allWrong():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'Mary',
        'MiddleNames_source': 'Helen',
        'MiddleNames_target': 'berlin',
        'Surname_source': 'paris',
        'Surname_target': 'person'
    }

    assert(score_names(row_data, debug=True)) == 0.0

def test_nameMixWithMiddle():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'person',
        'MiddleNames_source': 'berlin',
        'MiddleNames_target': 'berlin',
        'Surname_source': 'person',
        'Surname_target': 'Nick'
    }

    assert(score_names(row_data, debug=True)) == 0.9

def test_nameMixBlankMiddle():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'person',
        'MiddleNames_source': '',
        'MiddleNames_target': 'berlin',
        'Surname_source': 'person',
        'Surname_target': 'Nick'
    }

    assert(score_names(row_data, debug=True)) == 0.9

def test_nameMixBlankMiddle2():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'person',
        'MiddleNames_source': '',
        'MiddleNames_target': '',
        'Surname_source': 'person',
        'Surname_target': 'Nick'
    }

    assert(score_names(row_data, debug=True)) == 0.9

def test_nameMixNoMiddle():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'person',
        'Surname_source': 'person',
        'Surname_target': 'Nick'
    }

    assert(score_names(row_data, debug=True)) == 0.9

def test_doubelBarreldSurnameSource():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'Nick',
        'Surname_source': 'person-mudgens',
        'Surname_target': 'person'
    }

    assert(score_names(row_data, debug=True)) == 1.0

def test_doubelBarreldSurnameTarget():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'Nick',
        'Surname_source': 'person',
        'Surname_target': 'mudgens-person'
    }

    assert(score_names(row_data, debug=True)) == 1.0

def test_doubelBarreldSurnamesNoMatch():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'Nick',
        'Surname_source': 'Dastardly-person',
        'Surname_target': 'mudgens-person'
    }

    assert(score_names(row_data, debug=True)) == 0.4


def test_fuzzyScores():
    row_data = {
        'Forename_source': 'Nicky',
        'Forename_target': 'Nick',
        'Surname_source': 'pearson',
        'Surname_target': 'person'
    }

    assert(score_names(row_data, debug=True)) == 0.8

def test_fuzzyAndPerfect():
    row_data = {
        'Forename_source': 'Nick',
        'Forename_target': 'Nick',
        'Surname_source': 'pearson',
        'Surname_target': 'person'
    }

    assert(score_names(row_data, debug=True)) == 0.85

def test_MiddleNameSpaces():
    row_data = {
        'Surname_source': 'person',
        'Surname_target': 'person',
        'MiddleNames_source': 'berlinDave',
        'MiddleNames_target': 'berlin',
        'Forename_source': 'Nick',
        'Forename_target': 'Nick'
    }

    assert(score_names(row_data, debug=True)) == 1.0

def test_MiddleNamesFuzzy():
    row_data = {
        'Surname_source': 'person',
        'Surname_target': 'person',
        'MiddleNames_source': 'DiannaShvlen',
        'MiddleNames_target': 'SShvlen',
        'Forename_source': 'Nick',
        'Forename_target': 'Nick'
    }

    assert(score_names(row_data, debug=True)) == 0.85

def test_OnePoorFuzzy():
    row_data = {
        'Surname_source': 'pere',
        'Surname_target': 'mermoure',
        'Forename_source': 'truman',
        'Forename_target': 'landmark',
        'MiddleNames_source': 'a',
        'MiddleNames_target': 'mail tornado'
    }

    assert(score_names(row_data, debug=True)) < 0.5

def test_ForenameOnly():
    row_data = {
        'Surname_source': 'hilltop',
        'Surname_target': 'mermoure',
        'Forename_source': 'truman',
        'Forename_target': 'truman',
        'MiddleNames_source': 'alvin',
        'MiddleNames_target': 'tornado'
    }

    assert(score_names(row_data, debug=True)) == 0.4
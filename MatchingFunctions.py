import pandas as pd
import numpy as np
import copy
from fastDamerauLevenshtein import damerauLevenshtein
from pathlib import Path
import sys
import os

def select_columns(df, match_columns):
    selected_columns = copy.copy(match_columns)
    
    # Keep the PK and Person_ID columns
    selected_columns.append('ID')
    selected_columns.append('Link_ID')
    selected_columns.append('Person_ID')
    selected_columns.append('Score')
    selected_columns.append('Current_Person_ID')
    
    # Filter columns that exist in the DataFrame
    existing_columns = [col for col in selected_columns if col in df.columns]

    # Select only the specified columns that exist in the DataFrame
    df_subset = df[existing_columns]
    
    return df_subset


def link_within_dataset(source, target, link_keys):
    df_source_filtered = source.dropna(subset=link_keys)
    df_target_filtered = target.dropna(subset=link_keys)

    # Perform a self-join on the 'Value' column
    merged_df = df_source_filtered.merge(df_target_filtered, on=link_keys, suffixes=('_source', '_target'))
    
    # Ensure the link_keys are in the dataset so scoring doesn't have to worry about them being present
    for key in link_keys:
        key_source = key + '_source'
        key_target = key + '_target'
        merged_df[key_source] = merged_df[key]
        merged_df[key_target] = merged_df[key]

    ID_source = 'ID_source'
    ID_target = 'ID_target'
    # Filter out duplicate pairs and pairs where the row IDs are the same. Also linking to lowest should form the largest group
    distinct_pairs = merged_df[merged_df[ID_source] < merged_df[ID_target]]
    
    # Rename ID back for subsequent steps
    distinct_pairs.rename(columns={'ID_source': 'ID', 'Link_ID_source': 'Link_ID'}, inplace=True) 

    print(f"Link on {','.join(str(x) for x in link_keys)} found {len(distinct_pairs)} distinct pairs")
    return distinct_pairs


def link_to_person_details(source, target, link_keys):
    df_source_filtered = source.dropna(subset=link_keys)
    df_target_filtered = target.dropna(subset=link_keys)

    # Perform a self-join on the 'Value' column
    merged_df = df_source_filtered.merge(df_target_filtered, on=link_keys, suffixes=('_source', '_target'))
    
    # Ensure the link_keys are in the dataset so scoring doesn't have to worry about them being present
    for key in link_keys:
        key_source = key + '_source'
        key_target = key + '_target'
        merged_df[key_source] = merged_df[key]
        merged_df[key_target] = merged_df[key]
    
    # I think for this one we don't need to deduplicate as the join won't be circular like in the table linking to itself

    print(f"Link on {','.join(str(x) for x in link_keys)} found {len(merged_df)} rows")
    return merged_df

def update_links(source_df, scored_df, score_cutoff=0.7):  
    scored_df_high = scored_df[scored_df['Score'] >= score_cutoff]
    scored_df_high = scored_df_high[['ID', 'ID_target']]
                                   
    merged_df = pd.merge(source_df, scored_df_high, on='ID', how='left')
    merged_df['Link_ID'] = merged_df['ID_target'].fillna(merged_df['Link_ID'])
    merged_df.drop(columns='ID_target', inplace=True)
    
    return merged_df

def update_person_id(source_df, scored_df, score_cutoff=0.7):  
    scored_df_high = scored_df[scored_df['Score'] >= score_cutoff]
    scored_df_high.rename(columns={'Score': 'Link_Score'}, inplace=True)
    scored_df_high = scored_df_high[['ID', 'Person_ID_target', 'Link_Score']]
                                   
    merged_df = pd.merge(source_df, scored_df_high, on='ID', how='left')
    merged_df['Person_ID'] = merged_df['Person_ID_target'].fillna(merged_df['Person_ID'])
    merged_df['Score'] = merged_df['Link_Score'].fillna(merged_df['Score'])
    merged_df.drop(columns=['Person_ID_target', 'Link_Score'], inplace=True)
    
    return merged_df

def is_populated(value):
    if pd.isna(value):
        return False
    return value not in ('', 0, None, np.nan)

def clean_names(df):
    # Specific cleaning for names. 
    # If there is no middle name but multiple space separated values in the forename then separate move any extra names to the middlenames column
    
    if 'Forename' in df.columns:
        if 'MiddleNames' not in df.columns:
            df['MiddleNames'] = None

        df = df.apply(split_forename, axis=1)
    return df

def split_forename(row):
    forename = row['Forename']
    middlenames = row['MiddleNames']

    # If Forename is not populated or middlenames is populated, do nothing
    if not is_populated(forename) or is_populated(middlenames):
        return row  

    split_names = forename.split()
    if len(split_names) > 1:
        # The first name remains in the 'Forename' column
        row['Forename'] = split_names[0]

        row['MiddleNames'] = ' '.join(split_names[1:])
    
    return row

def clean_string_columns(df, clean_columns):
    for column in clean_columns:
        if column in df.columns:
            df[column] = df[column].apply(clean_row_string)
    return df

def clean_row_string(value):
    if value is None:
        return None
    elif value == '':
        return None
    else:
        return value.lower().replace(' ','')

def score_identifiers(row, identifiers, debug=False):
    # Logic needs to check if columns are present and populated
    # Count up positive hits
    # Count up negative hits
    # All positive is 100% (blank vs populated doesn't count)
    # No postives is 0%
    # Each negative brings down by half starting at 100% (guess at how this should work but any negatives should drag score right down)

    positives = 0
    negatives = 0

    for identifier in identifiers:
        source_col = f"{identifier}_source"
        target_col = f"{identifier}_target"        

        if source_col in row and target_col in row:
            source_value = row[source_col]
            target_value = row[target_col]

            # Check if both source and target are populated
            if is_populated(source_value) and is_populated(target_value):
                if source_value == target_value:
                    positives += 1
                else:
                    negatives += 1

    if debug:
        print(f"Identifiers Positives: {positives}")
        print(f"Identifiers Negatives: {negatives}")

    if positives > 0 and negatives == 0:  # All positives
        return 1.0
    elif negatives > 0 and positives == 0: # All negatives
        return 0
    elif positives == 0 and negatives == 0:  # No positives or negatives
        return 0.5
    else:
        # Calculate score based on negatives
        score = 1.0 * (1 * positives / (2 ** negatives))
        if score > 1.0:
            return 1.0
        # Give a slightly higher score than nothing as there are positives in the mix
        elif positives == negatives:
            return 0.6
        else:
            return score
        
def fuzzy_link_name(name_source, name_target, debug=False):
    # If either name is None return 0
    if name_source is None or name_target is None:
        return 0
    
    shortest_name_length = min(len(name_source), len(name_target))
    longest_name_length = max(len(name_source), len(name_target))

    # If either name is wholly within the other return a reasonably high score
    if shortest_name_length > 3 and (name_source in name_target or name_target in name_source):
        return 0.95
    
    # For very close names where the main hindrance is the length of one vs the other then use the character link score/smallest name length
    # E.g. that means Nick and Nicholas can have a very close match instead of the longer name biasing it to far. 
    # It would also not find the smaller in the larger for this type of case
    if debug:
        print(f"Shortest name: {shortest_name_length}")
        print(f"Longest name: {longest_name_length}")
    if longest_name_length - shortest_name_length < 4: #For very close length names just do similarity, otherwise bias similarity by the shortest name
        if debug:
            print(f"Length diff is small, similarity = {damerauLevenshtein(name_source, name_target, similarity=True)}")
        return damerauLevenshtein(name_source, name_target, similarity=True)
    elif shortest_name_length < 4:
        # Can't make a judgement on such a small name vs a large one it will likely take very few edits and over bias the scoring
        return 0
    else:
        edits = damerauLevenshtein(name_source, name_target, similarity=False)
        if debug:
            print(f"Length difference is large, edits = {edits}")
        return (longest_name_length -edits)/shortest_name_length
    
def score_names(row, debug=False):
    # Name can be made of Surname, Middlenames and Forename
    # Name placement can be important so exact hits on correct placement will win out
    # Missing middlename should not subtract from score

    # TODO:
    # Names can be mixed up so score highly for exact hits but inexact placement
    # Then make use of nicknames for names
    # Then employ Jaro-Winkler for a fuzzy score on the parts, cross link them and get the best 3 while only allowing 1:1 for each
    # E.g. Surname can be best for Forename but then Middlename must be against Middlename
    identifiers = ['Surname', 'Forename', 'MiddleNames']

    positives = 0
    negatives = 0

    for identifier in identifiers:
        source_col = f"{identifier}_source"
        target_col = f"{identifier}_target"

        if source_col in row and target_col in row:
            source_value = row[source_col]
            target_value = row[target_col]

            # Check if both source and target are populated
            if is_populated(source_value) and is_populated(target_value):
                if source_value == target_value:
                    positives += 1
                # For Surname only if there is double-barrelling then if one part matches the whole other surname, treat it as a full hit
                elif identifier == 'Surname' and ('-' in source_value or '-' in target_value):
                    if source_value in target_value.split('-') or target_value in source_value.split('-'):
                        positives += 1
                # If multiple middle names are supplied in one but not the other check if one fully fits inside the other
                elif identifier == 'MiddleNames' and (source_value in target_value or target_value in source_value):
                        positives += 1
                else:
                    negatives += 1
    
    if debug:
        print(f"Name Positives: {positives}")
        print(f"Name Negatives: {negatives}")

    if positives > 1 and negatives == 0:  # More than 1 hit, all positive. Assumption will be this is Forename and Surname but if Middlename is paired with either and there are no negatives that's a good score too
        return 1.0
    elif positives == 0 and negatives == 0:  # No positives or negatives (no name present in one)
        return 0.5
    
    forename_source = row['Forename_source']
    forename_target = row['Forename_target']

    surname_source = row['Surname_source']
    surname_target = row['Surname_target']

    if 'MiddleNames_source' in row:
        middlenames_source = row['MiddleNames_source']
    else:
        middlenames_source = ''
    
    if 'MiddleNames_source' in row:
        middlenames_target = row['MiddleNames_target']
    else:
        middlenames_target = ''

    # Now check for nicknames in forename and middlename parts

    misplaced_foresurname = False
    # Now check for misplaced namings and give a lower but still decent score if they're mixed up in placement
    if (forename_source == surname_target and surname_source == forename_target):
        misplaced_foresurname = True

    if misplaced_foresurname and \
    (middlenames_source == middlenames_target or not is_populated(middlenames_source) or not is_populated(middlenames_target)):
        if debug:
            print("Misplaced namings hit")
        return 0.9

    # Now check correct placement but fuzzy links
    fuzzy_positives = 0
    fuzzy_negatives = 0
    fuzzy_link_cutoff = 0.75

    for identifier in identifiers:
        source_col = f"{identifier}_source"
        target_col = f"{identifier}_target"

        if source_col in row and target_col in row:
            source_value = row[source_col]
            target_value = row[target_col]

            # Check if both source and target are populated
            if is_populated(source_value) and is_populated(target_value):
                if fuzzy_link_name(source_value, target_value, debug) >= fuzzy_link_cutoff:
                    fuzzy_positives += 1
                else:
                    fuzzy_negatives += 1
                if debug:
                    print(f"Fuzzy score for {source_col}: {fuzzy_link_name(source_value, target_value)}")


    if debug:
        print(f"Fuzzy Positives: {fuzzy_positives}")
        print(f"Fuzzy Negatives: {fuzzy_negatives}")

    if positives > 0 and fuzzy_positives > 0 and fuzzy_negatives == 0:
        return 0.85
    elif fuzzy_positives > 1 and fuzzy_negatives == 0: 
        return 0.8
    elif fuzzy_positives > 1: 
        return 0.75
    
    # Misplaced forename and surname and fuzzy hit on middle
    if misplaced_foresurname and fuzzy_link_name(middlenames_source, middlenames_target, debug) >= fuzzy_link_cutoff:
        return 0.9
    
    elif fuzzy_link_name(middlenames_source, middlenames_target, debug) >= fuzzy_link_cutoff \
        and fuzzy_link_name(row['Forename_source'], row['Surname_target'], debug) >= fuzzy_link_cutoff \
        and fuzzy_link_name(row['Surname_source'], row['Forename_target'], debug) >= fuzzy_link_cutoff:
        return 0.8

    # If only one matched and wasn't fuzzy return a low score but enough to bump a match slightly
    if positives == 1:
        return 0.4

    # Default is name match is bad so return 0, we only want to return a positive or neutral result
    return 0
    
def score_dob(row, debug=False):
    if 'DateOfBirth_source' in row:
        # Every row should have a date of birth field which should be populated
        # Score exact hits as 1.0
        # Score within 5 days as 0.9
        source_value = row['DateOfBirth_source']
        target_value = row['DateOfBirth_target']

        if target_value is None or source_value is None:
            return 0.0
        elif source_value == target_value:
            return 1.0
        elif abs(source_value - target_value).days <= 5:
            return 0.9
        # Now try matching various parts of the Date of birth
        elif source_value.year == target_value.year and source_value.month == target_value.day and source_value.day == target_value.month:
            return 0.9
        elif source_value.year == target_value.year and source_value.month == target_value.month:
            return 0.8
        elif source_value.year == target_value.year and source_value.day == target_value.day:
            return 0.8
        elif source_value.month == target_value.month and source_value.day == target_value.day:
            return 0.5
        return 0.0
    else:
        return 0.0
    
def score_location(row, debug=False):
    # Postcode is not guaranteed in the data. If it's missing give a score of 0.9 so it doesn't bias down an otherwise good hit 
    # but it will still mean a positive hit gets a higher score
    # If it matches give 1.0
    # If it's there and mismatches give 0
    if 'Postcode_source' in row and 'Postcode_target' in row:
        if not is_populated(row['Postcode_source']) or not is_populated(row['Postcode_target']):
            return 0.75
        elif row['Postcode_source'].replace(' ','')==row['Postcode_target'].replace(' ',''):
            return 1.0
        # If first 5 characters match score close 0.9
        elif row['Postcode_source'].replace(' ','')[:5]==row['Postcode_target'].replace(' ','')[:5]:
            return 0.8
        # If first 4 characters match score close 0.85
        elif row['Postcode_source'].replace(' ','')[:4]==row['Postcode_target'].replace(' ','')[:4]:
            return 0.78
        else:
            return 0
    else:
        return 0.75

def score_row_pair(row, dataset, debug=False, identifiers=['NHS_Number', 'UPN']):
    identifiers_score = score_identifiers(row, identifiers, debug)

    names_score = score_names(row, debug)

    dob_score = score_dob(row, debug)

    location_score = score_location(row, debug)

    if 'Forename_source' in row and 'Surname_source' in row:
        # If there are no names and identifier is positive then treat name as full for scoring (name and identifiers aren't enough on their own)
        if not is_populated(row['Forename_source']) and not is_populated(row['Surname_source']) and identifiers_score == 1:
            names_score = 1.0
        # If identifiers actively conflict and there's no name, drop the identifier score a little
        elif identifiers_score == 0.6:
            identifiers_score = 0.5
        # Fiddle name score down slightly if Location is 0
        elif names_score == 0.4 and location_score == 0:
            names_score = 0.2
    # Equally if there are no name fields then bump the score if identifiers match
    elif identifiers_score == 1.0:
        names_score = 1.0

    # Give each part equal weighting to begin with
    final_score = (identifiers_score * 0.3 + names_score * 0.25 + dob_score * 0.3 + location_score * 0.15)
    if debug:
        print(f"Identifiers score: {identifiers_score}")
        print(f"Names score: {names_score}")
        print(f"DOB score: {dob_score}")
        print(f"Location score: {location_score}")

    if debug:
        return {'Score': final_score, 'Score_Identifiers': identifiers_score, 'Score_DOB': dob_score, 'Score_Names': names_score, 'Score_Location': location_score}
    else: 
        return final_score
      
# Now to score the links to assess if they are valid matches... they clearly are from a brief look above!
def score_rows(df, dataset, debug=False):
    #df['Score'] = df.apply(lambda row: score_row_pair(row, dataset=dataset, debug=debug), axis=1)
    if debug:
        if 'Score' in df.columns:
            df.drop(columns='Score', inplace=True)
        result = df.apply(lambda row: pd.Series(score_row_pair(row, dataset=dataset, debug=debug)), axis=1)
        df = pd.concat([df, result], axis=1)
    else:
        df['Score'] = df.apply(lambda row: score_row_pair(row, dataset=dataset, debug=debug), axis=1)
    return df

def safe_idxmax(group):
    try:
        return group['Score'].idxmax()
    except Exception as e:
        print(f"Error in group:\n{group}")
        print(f"Exception: {e}")
        return None

# Then will need to pick the best score for each source record so we only have the 1 output as the winner in the link
def pick_best_score(df, score_key):
    # Replace NaN values in 'Score' with 0
    df['Score'] = df['Score'].fillna(0)
    # Group by 'ID', find max score, pick lowest score_key in case of tie
    result = df.loc[df.groupby('ID').apply(lambda x: x['Score'].idxmax())]

    # Filter original dataframe based on max score and lowest score_key
    result = result.groupby('ID').apply(lambda x: x.loc[x[score_key].idxmin()]).reset_index(drop=True)

    print(f"Scoring finished with {len(result)} rows")
    
    return result
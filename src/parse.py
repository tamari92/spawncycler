#
#  parse.py
#
#  Author: Tamari (Nathan P. Ybanez)
#  Date of creation: 11/26/2020
#
#  Contains helper functions used to parse the input file
#


##  LICENSE INFORMATION
##  =======================================================================
##  This file is part of SpawnCycler.

##  SpawnCycler is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.

##  SpawnCycler is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.

##  You should have received a copy of the GNU General Public License
##  along with SpawnCycler.  If not, see <https://www.gnu.org/licenses/>.
##  =======================================================================


from copy import deepcopy

zed_tokens = {'Cyst': ['cy', 'cys', 'cyst', 'cc', 'clotc'],
              'Alpha Clot': ['al', 'alp', 'alph', 'alpha', 'ca', 'clota'],
              'Slasher': ['sl', 'sla', 'slas', 'slash', 'slashe', 'slasher', 'cs', 'clots'],
              'Crawler': ['cr', 'cra', 'craw', 'crawl', 'crawle', 'crawler'],
              'Gorefast': ['g', 'go', 'gor', 'gore', 'goref', 'gorefa', 'gorefas', 'gorefast', 'gf'],
              'Stalker': ['st', 'sta', 'stal', 'stalk', 'stalke', 'stalker'],
              'Bloat': ['b', 'bl', 'blo', 'bloa', 'bloat'],
              'Husk': ['h', 'hu', 'hus', 'husk'],
              'Siren': ['si', 'sir', 'sire', 'siren'],
              'E.D.A.R Trapper': ['edare', 'etr', 'ee', 'de'],
              'E.D.A.R Blaster': ['edarl', 'ebl', 'el', 'dl'],
              'E.D.A.R Bomber': ['edarr' 'ebo', 'er', 'dr'],
              'Scrake': ['sc', 'scr', 'scra', 'scrak', 'scrake'],
              'Quarter Pound': ['mi', 'min', 'mini', 'minif', 'minifl', 'minifle', 'minifles', 'miniflesh', 'minifleshp', 'minifleshpo', 'minifleshpou', 'minifleshpoun', 'minifleshpound', 'mf', 'mfp'],
              'Fleshpound': ['f', 'fl', 'fle', 'fles', 'flesh', 'fleshp', 'fleshpo', 'fleshpou', 'fleshpoun', 'fleshpound', 'fp'],
              'Alpha Scrake': ['alphasc', 'asc'],
              'Alpha Fleshpound': ['alphafp', 'afp', 'af'],
              'Dr. Hans Volter': ['hansvolter', 'hansv', 'hv'],
              'Patriarch': ['patriarch', 'pat', 'pt'],
              'Matriarch': ['matriarch', 'mat', 'mt'],
              'King Fleshpound': ['ki', 'kin', 'king', 'kingf', 'kingfl', 'kingfle', 'kingfles', 'kingflesh', 'kingfleshp', 'kingfleshpo', 'kingfleshpou', 'kingfleshpoun', 'kingfleshpound', 'kf', 'kfp'],
              'Abomination': ['abomination', 'abm', 'ab'], 
              'Abomination Spawn': ['as']} # Figure out the rest


def format_zed_id(id, albino=False, raged=False):
    if id in ['al', 'alp', 'alph', 'alpha', 'ca', 'clota']:
        return 'Alpha Clot' if not albino else 'Rioter'
    elif id in ['cy', 'cys', 'cyst', 'cc', 'clotc']:
        return 'Cyst'
    elif id in ['b', 'bl', 'blo', 'bloa', 'bloat']:
        return 'Bloat'
    elif id in ['cr', 'cra', 'craw', 'crawl', 'crawle', 'crawler']:
        return 'Crawler' if not albino else 'Elite Crawler'
    elif id in ['f', 'fl', 'fle', 'fles', 'flesh', 'fleshp', 'fleshpo', 'fleshpou', 'fleshpoun', 'fleshpound', 'fp']:
        if albino:
            return 'Alpha Fleshpound' if not raged else 'Alpha Fleshpound (Enraged)'
        else:
            return 'Fleshpound' if not raged else 'Fleshpound (Enraged)'
    elif id in ['g', 'go', 'gor', 'gore', 'goref', 'gorefa', 'gorefas', 'gorefast', 'gf']:
        return 'Gorefast' if not albino else 'Gorefiend'
    elif id in ['h', 'hu', 'hus', 'husk']:
        return 'Husk'
    elif id in ['mi', 'min', 'mini', 'minif', 'minifl', 'minifle', 'minifles', 'miniflesh', 'minifleshp', 'minifleshpo', 'minifleshpou', 'minifleshpoun', 'minifleshpound', 'mf', 'mfp']:
        return 'Quarter Pound' if not raged else 'Quarter Pound (Enraged)'
    elif id in ['sc', 'scr', 'scra', 'scrak', 'scrake']:
        return 'Scrake' if not albino else 'Alpha Scrake'
    elif id in ['si', 'sir', 'sire', 'siren']:
        return 'Siren'
    elif id in ['sl', 'sla', 'slas', 'slash', 'slashe', 'slasher', 'cs', 'clots']:
        return 'Slasher'
    elif id in ['st', 'sta', 'stal', 'stalk', 'stalke', 'stalker']:
        return 'Stalker'
    elif id in ['as']:
        return 'Abomination Spawn'
    elif id in ['hansvolter', 'hansv', 'hv']:
        return 'Dr. Hans. Volter'
    elif id in ['patriarch', 'pat', 'pt']:
        return 'Patriarch'
    elif id in ['ki', 'kin', 'king', 'kingf', 'kingfl', 'kingfle', 'kingfles', 'kingflesh', 'kingfleshp', 'kingfleshpo', 'kingfleshpou', 'kingfleshpoun', 'kingfleshpound', 'kf', 'kfp']:
        return 'King Fleshpound'
    elif id in ['abomination', 'abm', 'ab']: # Figure out the rest
        return 'Abomination'
    elif id in ['matriarch', 'mat', 'mt']:
        return 'Matriarch'
    elif id in ['alphasc', 'asc']:
        return 'Alpha Scrake'
    elif id in ['alphafp', 'afp', 'af']:
        return 'Alpha Fleshpound'
    elif id in ['edartrapper', 'edaremp', 'edartr', 'edare', 'etr', 'ee', 'de']:
        return 'E.D.A.R Trapper'
    elif id in ['edarblaster', 'edarlaser', 'edarbl', 'edarl', 'ebl', 'el', 'dl']:
        return 'E.D.A.R Blaster'
    elif id in ['edarbomber', 'edarrocket', 'edarbo', 'edarr' 'ebo', 'er', 'dr']:
        return 'E.D.A.R Bomber'
    else:
        print(f'{id} returned None')
        return None


# Returns a JSON-formatted version of the squad array
def format_squad(squad):
    new_squad = {}

    # First split the squad into individual zeds
    zeds = squad.split('_')

    # Now separate tokens and add into the dictionary
    for token in zeds:
        zed_count, zed_id = separate_token(token) # This is the identifier for the zed with the number stripped
        zed_id, quantifiers = strip_quantifiers(zed_id) # Check for quantifiers
        albino = False
        raged = False
        for q in quantifiers:
            if q == '!':
                raged = True
            else:
                albino = True

        # Get the "Nice Name" for the ZED
        zed_id = format_zed_id(zed_id.lower(), albino=albino, raged=raged)
        zed_count = int(zed_count)

        # Add it to the squad
        if zed_id in new_squad and new_squad[zed_id]['Raged'] == raged: # Already in the squad and same raged status
            new_squad.update({zed_id: {'Count': new_squad[zed_id]['Count'] + zed_count, 'Raged': raged}})
        else:
            new_squad.update({zed_id: {'Count': zed_count, 'Raged': raged}})

    return new_squad


# Takes in a token (ie: '4AL') and returns the count and zed identifier
def separate_token(token):
    zed_count = '' # The beginning of the token should have a number
    n = 0 # This is where the token parse stopped, to separate the number from the identifier
    while n < len(token):
        ch = token[n]
        if not ch.isnumeric(): # Stop at the first non-number
            break
        zed_count += ch
        n += 1

    # Get components of the spawndef
    zed_id = token[n:] # This is the identifier for the zed with the number stripped
    zed_count = int(token[:n])

    return zed_count, zed_id


# Strips all quantifiers (!, *) from the token and returns them as a list
def strip_quantifiers(token):
    quantifiers = []
    i = len(token) - 1
    while i >= 0:
        if token[i].isalnum(): # Want symbols only
            break
        quantifiers.append(token[i])
        i -= 1
    token = token[:i+1] # Remove the quantifiers
    return token, quantifiers


# Parses the syntax of the given file. Returns 'None' if successful
def parse_syntax_export(filename, wavedefs):
    errors = []
    fname = f" ('{filename}')" if filename != 'Untitled' else ''
    parse_prefix = f"Parse errors{fname}:\n\n"

    if len(wavedefs) not in [4, 7, 10]: # File must be 4, 7, or 10 lines (waves) long
        errors.append(f"{parse_prefix}{len(wavedefs):,d} wave(s) found in SpawnCycle.\nSpawnCycle length must be 4, 7, or 10 waves!\n")

    for i in range(len(wavedefs)):
        wave = wavedefs[i]
        if len(wave['Squads']) < 1: # No squads to parse!
            errors.append(f"{parse_prefix}wave {i+1}: No squads found to parse. Wave is empty!")

    return errors


# Parses the syntax of the given file. Returns 'None' if successful
def parse_syntax_import(filename, lines):
    waves = deepcopy(lines)
    total_ids = [] # Combination of all id lists for easy checking
    for l in zed_tokens.values():
        total_ids += l
    valid_quantifiers = ['*', '!']

    fname = f" ('{filename}')" if filename != 'Untitled' else ''
    parse_prefix = f"Parse errors{fname}:\n\n"

    errors = []

    if len(waves) not in [4, 7, 10]: # File must be 4, 7, or 10 lines (waves) long
        errors.append(f"{parse_prefix}{len(waves):,d} lines found in file '{filename}'.\nFile length must be 4, 7, or 10 lines!")
        return errors # Just leave after this error because it's likely there will be hundreds of syntax errors

    # Check for invalid characters or identifiers
    for i in range(len(waves)):
        waves[i] = waves[i].replace('\n', '') # Replace all newlines
        line_num = f"line {i+1}:"

        if waves[i][:15] != 'SpawnCycleDefs=': # Improper prefix
            errors.append(f"{parse_prefix}{line_num} Improper or missing wave prefix.\nDid you make sure to include 'SpawnCycleDefs=' at the start of each line?")
        
        # Check squads
        l = waves[i].replace('SpawnCycleDefs=', '')
        squads = l.split(',')
        if len(squads) < 1: # No squads to parse!
            errors.append(f"{parse_prefix}{line_num} No squads found to parse. Wave is empty!")

        # Now attempt to break down the wave and check tokens
        for j in range(len(squads)):
            squad = squads[j] # Current squad
            if len(squad) < 1: # Empty squad found
                errors.append(f"{parse_prefix}{line_num} Found empty/missing squad definition ({j+1}).")
                continue

            # Check for bad symbols first
            for ch in squad:
                if not ch.isalnum() and ch not in (valid_quantifiers + ['_']):
                    errors.append(f"{parse_prefix}{line_num} Invalid quantifier/delimiter '{ch}' in squad {j+1} (near '{squad}').\nValid squad delimiters are: '_' and ','\nValid quantifiers are: '*' and '!'")

            # Now check the individual tokens
            tokens = squad.split('_')
            total_zeds = 0
            for token in tokens:
                if len(token) < 1: # Empty token found
                    errors.append(f"{parse_prefix}{line_num} Found missing or broken token sequence in squad {j+1} (near '{squad}').")
                    continue
                # The beginning of the token should have a number
                zed_count = ''
                i = 0 # This is where the token parse stopped, to separate the number from the identifier
                while i < len(token):
                    ch = token[i]
                    if not ch.isnumeric(): # Stop at the first non-number
                        break
                    zed_count += ch
                    i += 1

                zed_id = token[i:] # This is the identifier for the zed with the number stripped
                if len(zed_count) < 1: # No number at the start of the token
                    errors.append(f"{parse_prefix}{line_num} Missing value prefix for token '{zed_id}' in squad {j+1} (near '{squad}').")
                    continue
                zed_count = int(zed_count)

                # Check for invalid quantifiers
                zed_id, quantifiers = strip_quantifiers(zed_id)

                # Now check the specific identifiers
                if zed_id.lower() not in total_ids:
                    errors.append(f"{parse_prefix}{line_num} Invalid ZED identifier '{zed_id}' found in squad {j+1} (near '{squad}').")

                # Found quantifiers. Make sure it's on the right ZED(s)
                if len(quantifiers) > 0:
                    sr_allowed = zed_tokens['Fleshpound'] + zed_tokens['Quarter Pound'] + zed_tokens['Alpha Fleshpound']
                    alb_allowed = zed_tokens['Alpha Clot'] + zed_tokens['Gorefast'] + zed_tokens['Crawler'] + zed_tokens['Fleshpound'] + zed_tokens['Scrake']
                    failed = False
                    for q in quantifiers:
                        if q == '!' and zed_id.lower() not in sr_allowed:
                            errors.append(f"{parse_prefix}{line_num} '!' quantifier not allowed for '{zed_id}' in squad {j+1} (near '{squad}').\nApplicable ZEDs are: Quarter Pound, Fleshpound, Alpha Fleshpound")
                            failed = True
                        if q == '*' and zed_id.lower() not in alb_allowed:
                            errors.append(f"{parse_prefix}{line_num} '*' quantifier not allowed for '{zed_id}' in squad {j+1} (near '{squad}').\nApplicable ZEDs are: Alpha Clot, Gorefast, Crawler, Scrake, Fleshpound")
                            failed = True
                    if failed: # Stop if it found invalid quantifiers
                        continue

                # Add this squad's ZED count to the total
                total_zeds += zed_count

            if total_zeds > 10: # Too many ZEDs in squad
                errors.append(f"{parse_prefix}{line_num} Squad {j+1} (near '{squad}') surpasses maximum capacity of 10 ZEDs.")

    return errors

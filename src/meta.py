#
#  meta.py
#
#  Author: Tamari
#  Date of creation: 3/2/2022
#
#  Contains code snippets for altering the program's metadata
#


##  LICENSE INFORMATION
##  =======================================================================
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <https://www.gnu.org/licenses/>.
##  =======================================================================
##
##  © Tamari 2020-2022
##  All rights reserved.

import json

_PATH_META = 'meta'

# Creates and inits the meta file if one doesn't exist
def init_metadict():
    meta_dict = {'recent_files': [],
                 'should_warn_zedset': True,
                 'should_warn_gensettings': True,
                 'should_warn_cyclelength': True,
                 'autosave_enabled': True,
                 'autosave_interval': 600,
                 'save_json_default_target': 0, # 0 always ask, 1 = adaptive (match length), 2 = preferred med, 3 = preferred long
                 'save_default_filetype': 0, # 0 = adaptive (match currently opened type), 1 = txt, 2 = json
                 'new_squad_min_amount': 1,
                 'analyze_default_length': 0} # 0 = last used, 1 = adaptive, 2 = preferred short, 3 = preferred med, 4 = preferred long
    with open(_PATH_META, 'w') as f:
        f.write(json.dumps(meta_dict))


# Returns the meta dictionary
def get_metadict():
    try: # Try to load the meta data
        f = open(_PATH_META, 'r')
    except: # Something went wrong. Make a new one instead
        init_metadict()

    with open(_PATH_META, 'r') as f:
        meta_dict = json.loads(f.readline())
    return meta_dict


# Returns a specific key from the meta dictionary
def get_keyvalue(key):
    meta_dict = get_metadict()
    if key not in meta_dict:
        init_metadict()
    return get_metadict()[key]


# Sets the given key to the given value
def set_keyvalue(key, value):
    meta_dict = get_metadict()
    meta_dict[key] = value # Set the value
    with open(_PATH_META, 'w') as f:
        f.write(json.dumps(meta_dict))
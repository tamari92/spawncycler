#
#  analyze.py
#
#  Author: Tamari
#  Date of creation: 11/27/2020
#
#  UI code for the 'Analyze' functionality
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


from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import widget_helpers
import meta

_DEF_FONT_FAMILY = 'Consolas'
_WAVESIZE_MIN = 1
_WAVESIZE_MAX = 255
_WAVESIZE_DELTA = 0.2115384615384615 # The percentage each wave increases by for every +1 WSF
_MAXMONSTERS_MIN = 1
_MAXMONSTERS_MAX = 512
_WINDOWSIZE_ANALYZE_W = 750
_WINDOWSIZE_ANALYZE_H = 1000


zed_weights = {'Cyst': 300,
               'Alpha Clot': 335,
               'Rioter': 450,
               'Slasher': 320,
               'Slasher Omega': 335,
               'Gorefast': 350,
               'Gorefast Omega': 375,
               'Gorefiend': 400,
               'Crawler': 350,
               'Tiny Crawler': 325,
               'Medium Crawler': 350,
               'Big Crawler': 375,
               'Huge Crawler': 400,
               'Ultra Crawler': 450,
               'Elite Crawler': 400,
               'Stalker': 375,
               'Stalker Omega': 425,
               'Bloat': 700,
               'Husk': 1000,
               'Husk Omega': 1100,
               'Tiny Husk': 700,
               'E.D.A.R Trapper': 1100,
               'E.D.A.R Blaster': 1200,
               'E.D.A.R Bomber': 1100,
               'Siren': 900,
               'Siren Omega': 1000,
               'Quarter Pound': 3000,
               'Quarter Pound (Enraged)': 4000,
               'Scrake': 3000,
               'Scrake Omega': 3500,
               'Scrake Emperor': 4000,
               'Tiny Scrake': 2500,
               'Alpha Scrake': 4000,
               'Fleshpound': 4000,
               'Fleshpound (Enraged)': 5000,
               'Fleshpound Omega': 5000,
               'Alpha Fleshpound': 3000,
               'Alpha Fleshpound (Enraged)': 4000,
               'Dr. Hans Volter': 8000,
               'Patriarch': 7000,
               'King Fleshpound': 8000,
               'Abomination': 8000,
               'Abomination Spawn': 200,
               'Matriarch': 10000}

# Colors
dark_colors = {'Trash': QtGui.QColor(85, 107, 43),
               'Medium': QtGui.QColor(140, 137, 56),
               'Large': QtGui.QColor(161, 67, 64),
               'Boss': QtGui.QColor(204, 82, 176),
               'Albino': QtGui.QColor(151, 76, 186),
               'Clots': QtGui.QColor(85, 107, 43),
               'Gorefasts': QtGui.QColor(107, 112, 49),
               'Crawlers / Stalkers': QtGui.QColor(117, 113, 62),
               'Robots': QtGui.QColor(140, 137, 56),
               'Scrakes': QtGui.QColor(130, 105, 73),
               'Fleshpounds': QtGui.QColor(161, 67, 64),
               'SpawnRage': QtGui.QColor(125, 44, 44),
               'Omega': QtGui.QColor(108, 69, 165),
               'Other': QtGui.QColor(75, 75, 75),
               'Total': QtGui.QColor(58, 122, 145)}
light_colors = {'Header': QtGui.QColor(100, 100, 100),
                'Trash': QtGui.QColor(185, 212, 131),
                'Medium': QtGui.QColor(240, 237, 152),
                'Large': QtGui.QColor(235, 165, 162),
                'Boss': QtGui.QColor(238, 186, 226),
                'Albino': QtGui.QColor(219, 182, 237),
                'Clots': QtGui.QColor(185, 212, 131),
                'Gorefasts': QtGui.QColor(200, 212, 131),
                'Crawlers / Stalkers': QtGui.QColor(212, 207, 131),
                'Robots': QtGui.QColor(240, 237, 152),
                'Scrakes': QtGui.QColor(227, 189, 154),
                'Fleshpounds': QtGui.QColor(235, 165, 162),
                'SpawnRage': QtGui.QColor(240, 122, 122),
                'Omega': QtGui.QColor(178, 153, 214),
                'Other': QtGui.QColor(175, 175, 175),
                'Total': QtGui.QColor(184, 214, 224)}


class AnalyzeDialog(object):
    def __init__(self, parent):
        self.parent = parent
        self.buttons = {'WaveButtons': {}}
        self.active_wave = 'merged'
        self.params = {} # All of the current analysis params are stored here

    # Returns the WaveSizeMultiplier based on the current WSF
    def get_wavesize_multiplier(self, wsf):
        if wsf <= 6:
            multis = [1.00, 1.00, 2.00, 2.75, 3.50, 4.00, 4.50]
            return multis[wsf]
        return 4.50 + ((wsf-6) * _WAVESIZE_DELTA) # WSF > 6

    # Returns the BaseNumZEDs based on the current wave and gamelength
    def get_base_num_zeds(self, wave_id, gamelength):
        base_num_zeds = [[25, 32, 35, 42], # Short (4 Wave)
                         [25, 28, 32, 32, 35, 40, 42], # Medium (7 Wave)
                         [25, 28, 32, 32, 35, 35, 35, 40, 42, 42]] # Long (10 Wave)
        return base_num_zeds[gamelength][wave_id]

    # Returns the DifficultyMod
    def get_difficulty_mod(self, difficulty):
        multis = [0.85, 1.00, 1.30, 1.70]
        return multis[difficulty]

    # Returns analysis data for the given wave
    def sample_wave(self, wave_id):
        # Wave is empty!
        if len(self.parent.wavedefs[wave_id]['Squads']) == 0:
            return None, [(0.0, 0.0)]

        # Params
        base_num_zeds = self.get_base_num_zeds(wave_id, self.params['GameLength'])
        diffmod = self.get_difficulty_mod(self.params['Difficulty'])
        wavesize_multi = self.get_wavesize_multiplier(self.params['WaveSizeFakes'])

        # The number of ZEDs that will be in this wave
        wave_num_zeds = int((base_num_zeds * diffmod * wavesize_multi) // 1)

        # Expand this wave's squads
        expanded_squads = self.expand_squads(self.parent.wavedefs[wave_id])
        
        # Simulate the wave!
        wave_stats = {'Total': wave_num_zeds,
                      'Category': {'Trash': 0, 'Medium': 0, 'Large': 0, 'Boss': 0, 'Total': 0}, 
                      'Name': {'Cyst': 0, 'Alpha Clot': 0, 'Slasher': 0, 'Slasher Omega': 0,  'Rioter': 0, 'Gorefast': 0, 'Gorefast Omega': 0, 'Gorefiend': 0, 'Crawler': 0, 'Elite Crawler': 0, 'Tiny Crawler': 0, 'Medium Crawler': 0, 'Big Crawler': 0,
                               'Huge Crawler': 0, 'Ultra Crawler': 0, 'Stalker': 0, 'Stalker Omega': 0, 'Abomination Spawn': 0, 'Bloat': 0, 'Husk': 0, 'Husk Omega': 0, 'Tiny Husk': 0, 'Siren': 0,
                               'Siren Omega': 0, 'E.D.A.R Trapper': 0, 'E.D.A.R Blaster': 0, 'E.D.A.R Bomber': 0, 'Quarter Pound': 0, 'Scrake': 0, 'Scrake Omega': 0, 'Tiny Scrake': 0,
                               'Scrake Emperor': 0, 'Alpha Scrake': 0, 'Fleshpound': 0, 'Fleshpound Omega': 0, 'Alpha Fleshpound': 0, 'King Fleshpound': 0, 'Dr. Hans Volter': 0,
                               'Patriarch': 0, 'Abomination': 0, 'Matriarch': 0, 'Total': 0},
                      'Group': {'Clots': 0, 'Gorefasts': 0, 'Crawlers / Stalkers': 0, 'Robots': 0, 'Scrakes': 0, 'Fleshpounds': 0, 'Albino': 0, 'Omega': 0, 'SpawnRage': 0, 'Total': 0},
                      'SpawnRage': {'Quarter Pound': 0, 'Fleshpound': 0, 'Alpha Fleshpound': 0, 'Total': 0}}

        trash_zeds = ['Cyst', 'Alpha Clot', 'Slasher', 'Rioter', 'Gorefast', 'Gorefiend',
                      'Crawler', 'Elite Crawler', 'Stalker', 'Slasher Omega', 'Gorefast Omega', 'Abomination Spawn',
                      'Stalker Omega', 'Tiny Crawler', 'Medium Crawler', 'Big Crawler', 'Huge Crawler', 'Ultra Crawler']
        medium_zeds = ['Bloat', 'Husk', 'Siren', 'E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber', 'Siren Omega', 'Husk Omega', 'Tiny Husk']
        large_zeds = ['Quarter Pound', 'Fleshpound', 'Scrake', 'Alpha Scrake', 'Alpha Fleshpound', 'Tiny Scrake',
                      'Scrake Omega', 'Scrake Emperor', 'Fleshpound Omega', 'Stalker Omega']
        albino = ['Rioter', 'Gorefiend', 'Elite Crawler', 'Alpha Scrake', 'Alpha Fleshpound']
        bosses = ['King Fleshpound', 'Abomination', 'Dr. Hans Volter', 'Patriarch', 'Matriarch']
        omega = ['Slasher Omega', 'Gorefast Omega', 'Stalker Omega', 'Tiny Crawler', 'Medium Crawler',
                 'Big Crawler', 'Huge Crawler', 'Ultra Crawler', 'Siren Omega', 'Husk Omega', 'Tiny Husk',
                 'Tiny Scrake', 'Scrake Omega', 'Scrake Emperor', 'Fleshpound Omega', 'Stalker Omega']
        j = 0

        for i in range(wave_num_zeds):
            next_zed = expanded_squads[j] # Get the next ZED to be spawned
            j = (j+1) % len(expanded_squads) # Roll back to the start of the array

            # Add to category stats
            if isinstance(next_zed, dict): # Special case for enraged Fleshpounds
                next_zed = next_zed['Raged'] # This is messy but I honestly can't be bothered anymore
                wave_stats['Group']['Fleshpounds'] += 1
                wave_stats['Group']['SpawnRage'] += 1
                wave_stats['SpawnRage'][next_zed] += 1
                wave_stats['SpawnRage']['Total'] += 1
                wave_stats['Category']['Large'] += 1
                if next_zed == 'Alpha Fleshpound':
                    wave_stats['Group']['Albino'] += 1
            else:
                # Trash ZEDs
                if next_zed in trash_zeds:
                    # Add to group stats
                    if next_zed in ['Cyst', 'Alpha Clot', 'Slasher', 'Rioter', 'Slasher Omega']:
                        wave_stats['Group']['Clots'] += 1
                    elif next_zed in ['Gorefast', 'Gorefiend', 'Gorefast Omega']:
                        wave_stats['Group']['Gorefasts'] += 1
                    elif next_zed in ['Crawler', 'Elite Crawler', 'Stalker', 'Tiny Crawler', 'Medium Crawler', 'Big Crawler', 'Huge Crawler', 'Ultra Crawler', 'Stalker Omega']:
                        wave_stats['Group']['Crawlers / Stalkers'] += 1
                    wave_stats['Category']['Trash'] += 1

                # Medium ZEDs
                elif next_zed in medium_zeds:
                    if next_zed in ['E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber']:
                        wave_stats['Group']['Robots'] += 1
                    wave_stats['Category']['Medium'] += 1

                # Large ZEDs
                elif next_zed in large_zeds:
                    if next_zed in ['Scrake', 'Alpha Scrake', 'Scrake Omega', 'Scrake Emperor', 'Tiny Scrake']:
                        wave_stats['Group']['Scrakes'] += 1
                    elif next_zed in ['Fleshpound', 'Alpha Fleshpound', 'Quarter Pound', 'Fleshpound Omega']:
                        wave_stats['Group']['Fleshpounds'] += 1
                    wave_stats['Category']['Large'] += 1

                # Bosses
                else:
                    wave_stats['Category']['Boss'] += 1

                if next_zed in albino: # Check for albinos
                    wave_stats['Group']['Albino'] += 1
                if next_zed in omega: # Check for omegas
                    wave_stats['Group']['Omega'] += 1

            # Add to totals
            wave_stats['Category']['Total'] += 1
            wave_stats['Group']['Total'] += 1
            wave_stats['Name']['Total'] += 1
            wave_stats['Name'][next_zed] += 1

        j = 0
        difficulty_data = [(0.0, 0.0)]
        currently_spawned_zeds = []
        expanded_wave = []
        while len(expanded_wave) < wave_num_zeds:
            expanded_wave += expanded_squads
        expanded_wave = expanded_wave[:wave_num_zeds]
            
        # Now calculate the difficulty
        # +MM is to account for the "wind down" (killing remaining ZEDs after ZED spawning stops)
        # In reality we never make it that far though in most cases
        for i in range(wave_num_zeds + self.params['MaxMonsters']):
            next_zed = None
            if j < len(expanded_wave):
                next_zed = expanded_wave[j] # Get the next ZED to be spawned
                j += 1

            if next_zed is not None: # Still ZEDs left to spawn
                if len(currently_spawned_zeds) == self.params['MaxMonsters']: # We've reached MaxMonsters
                    currently_spawned_zeds.pop(0) # Remove the first ZED and add the new one at the end
                currently_spawned_zeds.append(next_zed)
            else:
                if len(currently_spawned_zeds) == 0: # We ran out of zeds to pop (because MM is high)
                    break # Leave early. We had less ZEDs remaining than there were MaxMonsters
                currently_spawned_zeds.pop(0) # Remove the first ZED

            # Get the difficulty score at this point
            # ZED composition modifier: ZEDs have varying weights
            transcribe = {'Fleshpound': 'Fleshpound (Enraged)',
                          'Quarter Pound': 'Quarter Pound (Enraged)',
                          'Alpha Fleshpound': 'Alpha Fleshpound (Enraged)'}
            zed_count = sum([zed_weights[(z if not isinstance(z, dict) else transcribe[z['Raged']])] for z in currently_spawned_zeds])
            zed_diff_mod = 1.00 + (0.50 * self.params['Difficulty']) # ZED difficulty modifier: (harder difficulty = stronger attacks / more damage dealt)
            zed_comp_mod = zed_diff_mod * zed_count

            # Wave modifier, based on how far into the game this is.
            # Earlier waves tend to be harder due to less money/economy
            # Difficulty also affects this since it changes how much dosh you earn per kill
            max_wave = {0: 10, 1: 7, 2: 4}
            doshmod = {0: 1.00, 1: 1.25, 2: 1.50, 3: 1.75}
            wave_score_mod = doshmod[self.params['Difficulty']] + (float(wave_id+1) / float(max_wave[self.params['GameLength']]))
            
            # Longer waves tend to be harder due to resources (ammo, etc) having to be further spread out 
            wsf_mod = 1.50 + (float(self.params['WaveSizeFakes']) / 128.0)

            # Calculate the final score
            difficulty_score = wsf_mod * wave_score_mod * zed_comp_mod
            if difficulty_score > 750000.0: # Cap Difficulty Score at 750K
                difficulty_score = 750000.0
            percent_thru_wave = (float(i+1) / float(wave_num_zeds)) * 100 # How far into the wave this is
            
            difficulty_data.append((percent_thru_wave, float(difficulty_score)))

        return wave_stats, difficulty_data

    # Creates and returns a Table object representing the wave's data
    def create_waveframe(self, wave_data, merged=False, difficulty_data=None, axis_data=None):
        if wave_data is None and not merged: # Empty wave
            return

        # Style stuff
        ss_label = 'color: rgb(255, 255, 255);' # Stylesheet
        sp_fixed = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_fixed.setHorizontalStretch(0)
        sp_fixed.setVerticalStretch(0)
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(10)
        font_label.setWeight(75)
        font_button = QtGui.QFont()
        font_button.setFamily(_DEF_FONT_FAMILY)
        font_button.setPointSize(12)
        font_button.setWeight(75)

        # Create frame to hold everything
        frame = QtWidgets.QFrame()
        frame_layout = QtWidgets.QVBoxLayout(frame)
        frame_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        frame.setStyleSheet(f"color: rgb(255, 255, 255); background-color: rgb(50, 50, 50)")
        frame.setFrameShape(QtWidgets.QFrame.Box)
        frame.setFrameShadow(QtWidgets.QFrame.Plain)
        frame.setLineWidth(2)

        # Setup ZEDs by Category Table
        zed_category_data = [(0, 0, ' Name '),
                             (0, 1, '  Count  '),
                             (0, 2, '  % of Total  ')]
        row = 1
        col = 0
        # Iterate over all categories
        for (category, count) in wave_data['Category'].items():
            if self.params['Ignore Zeroes'] and count == 0: # Ignore zero fields
                continue
            else:
                percent = f"{((float(count) / float(wave_data['Total'])) * 100.0):.2f}%"
                zed_category_data.append((row, col, category))
                zed_category_data.append((row, col+1, f"{count:,d}"))
                zed_category_data.append((row, col+2, percent))
                row += 1
                col = 0

        # Create label and table
        label_zed_category = widget_helpers.create_label(None, text='ZEDs by Category', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
        table_zed_category = widget_helpers.create_table(None, zed_category_data, num_rows=len(zed_category_data) // 3, num_cols=3, stretch=False)
        
        # Format table
        widget_helpers.set_plain_border(table_zed_category, QtGui.QColor(255, 255, 255), 2)
        self.format_table(table_zed_category, table_type='categorical')

        # Create ZEDs by Category Pie Chart
        if self.params['Display Charts']:
            chart_data = []
            # Iterate over all categories
            for (category, count) in wave_data['Category'].items():
                if category not in ['Total'] and count > 0: # Ignore the 'Total' row. This shouldn't be in the pie chart
                    percent = (float(count) / float(wave_data['Total'])) * 100.0
                    chart_data.append((category, count, light_colors[category], percent))
            chart_zed_category = widget_helpers.create_chart(None, chart_data, '', chart_type='pie')

        # Create the ZEDs by Type Table
        zed_type_data = [(0, 0, ' Name '), # The different columns of the table
                         (0, 1, '  Count  '),
                         (0, 2, '  % of Total  '),
                         (0, 3, '  SpawnRage  ')]
        row = 1
        col = 0

        # Loop over all the ZEDs and their individual counts
        for (zed, count) in wave_data['Name'].items():
            if self.params['Ignore Zeroes'] and count == 0: # Ignore zero fields
                continue
            else:
                # Calculate the percentage this ZED is of the total
                percent = f"{((float(count) / float(wave_data['Total'])) * 100.0):.2f}%"
                
                if zed != 'Total': # Calculate SpawnRage for everything except the 'Total' row
                    spawnrage_percent_str = f" ({((float(wave_data['SpawnRage'][zed]) / float(wave_data['Name'][zed])) * 100.0):.2f}%)" if zed in ['Quarter Pound', 'Fleshpound', 'Alpha Fleshpound'] and wave_data['SpawnRage'][zed] > 0 else ''
                    spawnrage_str = ' ' if zed not in ['Quarter Pound', 'Fleshpound', 'Alpha Fleshpound'] else f"{wave_data['SpawnRage'][zed]:,d}{spawnrage_percent_str}"
                else: # This is for the 'Total' row. It has nothing to calculate, so leave blank
                    spawnrage_percent_str = ' '
                    spawnrage_str = ' '

                # Add the data to the table
                zed_type_data.append((row, col, zed))
                zed_type_data.append((row, col+1, f"{count:,d}"))
                zed_type_data.append((row, col+2, percent))
                zed_type_data.append((row, col+3, spawnrage_str))

                # Move down a row and reset the column
                row += 1
                col = 0

        # Create the table using the data
        label_zed_type = widget_helpers.create_label(None, text='\nZEDs by Type', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
        table_zed_type = widget_helpers.create_table(None, zed_type_data, num_rows=len(zed_type_data) // 4, num_cols=4, stretch=True)

        # Format table to have a nice border
        widget_helpers.set_plain_border(table_zed_type, QtGui.QColor(255, 255, 255), 2)
        self.format_table(table_zed_type, table_type='type')

        # Setup ZEDs by Group Table
        zed_group_data = [(0, 0, ' Name '),
                          (0, 1, '  Count  '),
                          (0, 2, '  % of Total  ')]
        row = 1
        col = 0
        group_items = list(wave_data['Group'].items())
        group_sum = sum([x[1] for x in group_items if x[0] != 'Total'])

        if group_sum > 0: # Only do this if there are groups to actually show
            # Add in the 'Other' row
            other_count = wave_data['Total'] - (wave_data['Group']['Clots'] + wave_data['Group']['Gorefasts'] + wave_data['Group']['Crawlers / Stalkers'] + wave_data['Group']['Robots'] + wave_data['Group']['Scrakes'] + wave_data['Group']['Fleshpounds'])
            other_row = ('Other', other_count)
            group_items.insert(-1, other_row)

            for (group, count) in group_items:
                if self.params['Ignore Zeroes'] and count == 0: # Ignore zero fields
                    continue
                else:
                    percent = f"{((float(count) / float(wave_data['Total'])) * 100.0):.2f}%"
                    zed_group_data.append((row, col, group))
                    zed_group_data.append((row, col+1, f"{count:,d}"))
                    zed_group_data.append((row, col+2, percent))
                    row += 1
                    col = 0

            label_zed_group = widget_helpers.create_label(None, text='\nZEDs by Group', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            table_zed_group = widget_helpers.create_table(None, zed_group_data, num_rows=len(zed_group_data) // 3, num_cols=3, stretch=True)
            
            # Format table
            widget_helpers.set_plain_border(table_zed_group, QtGui.QColor(255, 255, 255), 2)
            self.format_table(table_zed_group, table_type='categorical')

            # Create ZEDs by Group Pie Chart
            if self.params['Display Charts']:
                chart_data = []
                total_percent = 0.0
                total_count = 0
                # Iterate over all groups
                for (group, count) in wave_data['Group'].items():
                    if group not in ['Total', 'Albino', 'SpawnRage', 'Omega'] and count > 0: # Ignore Total/Albino/SpawnRage as they are not unique groups
                        percent = (float(count) / float(wave_data['Total'])) * 100.0
                        total_percent += percent
                        total_count += count
                        chart_data.append((group, count, light_colors[group], percent))
                # Add 'Other' group
                other_percent = 100.0 - total_percent
                other_count = wave_data['Total'] - total_count
                chart_data.append(('Other', other_count, QtGui.QColor(175, 175, 175), other_percent))
                chart_zed_group = widget_helpers.create_chart(None, chart_data, '', chart_type='pie')

        if difficulty_data is not None and self.params['Analyze Difficulty']:
            label_diff_text = f"\n\nESTIMATED WAVE DIFFICULTY" if not merged else f"\n\nSPAWNCYCLE DIFFICULTY"
            label_wave_diff = widget_helpers.create_label(None, text=label_diff_text, tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_mm = widget_helpers.create_label(None, text=f"Max Monsters:     {self.params['MaxMonsters']}\nDificulty:        {self.analysis_widgets['Difficulty'].currentText()}\nWave Size Fakes:  {self.params['WaveSizeFakes']}", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_assumes = widget_helpers.create_label(None, text=f"\nASSUMPTIONS", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_cs = widget_helpers.create_label(None, text=f"Spawn Poll:      1.00\nSpawn Mod:       0.00\nPlayers:         6\nTrash HP Fakes:  6\nLarge HP Fakes:  6\nBoss HP Fakes:   6\nFakes Mode:      ignore_humans\n\nAll ZEDs are killed in the order they spawn", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            chart_difficulty = widget_helpers.create_chart(None, difficulty_data, '', axis_data=axis_data, chart_type='line')

        # Add everything in
        frame_layout.addWidget(label_zed_category)
        frame_layout.addWidget(table_zed_category)
        if self.params['Display Charts']:
            frame_layout.addWidget(chart_zed_category)
        frame_layout.addWidget(label_zed_type)
        frame_layout.addWidget(table_zed_type)
        if group_sum > 0: # Only add groups if there are groups to even add
            frame_layout.addWidget(label_zed_group)
            frame_layout.addWidget(table_zed_group)
            if self.params['Display Charts']:
                frame_layout.addWidget(chart_zed_group)
        else:
            label_zed_group = widget_helpers.create_label(None, text='\nZEDs by Group', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_nodata = widget_helpers.create_label(None, text='\nNo Group Data to show!', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            frame_layout.addWidget(label_zed_group)
            frame_layout.addWidget(label_nodata)
        
        if difficulty_data is not None and self.params['Analyze Difficulty']:
            frame_layout.addWidget(label_wave_diff)
            frame_layout.addWidget(label_mm)
            frame_layout.addWidget(label_assumes)
            frame_layout.addWidget(label_cs)
            frame_layout.addWidget(chart_difficulty)

        # Everything that was used to make this frame
        children = {'Labels': {'ZEDs by Category': label_zed_category, 'ZEDs by Type': label_zed_type, 'ZEDs by Group': label_zed_group},
                    'Tables': {'ZEDs by Category': table_zed_category, 'ZEDs by Type': table_zed_type, 'ZEDs by Group': table_zed_group if group_sum > 0 else None}}
        if self.params['Display Charts']:
            children.update({'Charts': {'ZEDs by Category': chart_zed_category}})

        return frame, children

    # Color-codes the given table
    def format_table(self, table, table_type='categorical'):
        # Font stuff
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)

        # ZED lists
        trash_zeds = ['Cyst', 'Alpha Clot', 'Slasher', 'Rioter', 'Gorefast', 'Gorefiend',
                      'Crawler', 'Elite Crawler', 'Stalker', 'Slasher Omega', 'Gorefast Omega', 'Abomination Spawn',
                      'Stalker Omega', 'Tiny Crawler', 'Medium Crawler', 'Big Crawler', 'Huge Crawler', 'Ultra Crawler']
        medium_zeds = ['Bloat', 'Husk', 'Siren', 'E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber', 'Siren Omega', 'Husk Omega', 'Tiny Husk']
        large_zeds = ['Quarter Pound', 'Fleshpound', 'Scrake', 'Alpha Scrake', 'Alpha Fleshpound', 'Tiny Scrake',
                      'Scrake Omega', 'Scrake Emperor', 'Fleshpound Omega', 'Stalker Omega']
        albino_zeds = ['Rioter', 'Gorefiend', 'Elite Crawler', 'Alpha Scrake', 'Alpha Fleshpound']
        bosses = ['King Fleshpound', 'Abomination', 'Dr. Hans Volter', 'Patriarch', 'Matriarch']
        omega_zeds = ['Slasher Omega', 'Gorefast Omega', 'Stalker Omega', 'Tiny Crawler', 'Medium Crawler',
                 'Big Crawler', 'Huge Crawler', 'Ultra Crawler', 'Siren Omega', 'Husk Omega', 'Tiny Husk',
                 'Tiny Scrake', 'Scrake Omega', 'Scrake Emperor', 'Fleshpound Omega', 'Stalker Omega']

        if table_type == 'categorical': # Category table
            # Colorify header row
            header_cells = [(0, 0), (0, 1), (0, 2)]
            for (x, y) in header_cells:
                widget_helpers.format_cell(table, x, y, bg_color=light_colors['Header'], fg_color=None, font=font, alignment=QtCore.Qt.AlignHCenter)

            # Colorify rest of the table
            row = 1
            while row < table.rowCount():
                category = table.item(row, 0).text()
                for j in range(3): # Apply the colors to the row!
                    if j == 0: # First col should be left-aligned
                        widget_helpers.format_cell(table, row, j, bg_color=light_colors[category], fg_color=dark_colors[category], font=font)
                    else:
                        widget_helpers.format_cell(table, row, j, bg_color=light_colors[category], fg_color=dark_colors[category], font=font, alignment=QtCore.Qt.AlignHCenter)
                row += 1
        else: # Type table
            # Colorify header row
            header_cells = [(0, 0), (0, 1), (0, 2), (0, 3)]
            for (x, y) in header_cells:
                widget_helpers.format_cell(table, x, y, bg_color=light_colors['Header'], fg_color=None, font=font, alignment=QtCore.Qt.AlignHCenter)

            # Colorify rest of the table
            row = 1
            while row < table.rowCount():
                zed_type = table.item(row, 0).text()

                # Figure out what color this row should be
                if zed_type in albino_zeds:
                    bg_color = light_colors['Albino']
                    fg_color = dark_colors['Albino']
                elif zed_type in omega_zeds:
                    bg_color = light_colors['Omega']
                    fg_color = dark_colors['Omega']
                elif zed_type in trash_zeds:
                    bg_color = light_colors['Trash']
                    fg_color = dark_colors['Trash']
                elif zed_type in medium_zeds:
                    bg_color = light_colors['Medium']
                    fg_color = dark_colors['Medium']
                elif zed_type in large_zeds:
                    bg_color = light_colors['Large']
                    fg_color = dark_colors['Large']
                elif zed_type in bosses:
                    bg_color = light_colors['Boss']
                    fg_color = dark_colors['Boss']
                else:
                    bg_color = light_colors['Total']
                    fg_color = dark_colors['Total']

                for j in range(4): # Apply the colors to the row!
                    if j == 0: # First col should be left-aligned
                        widget_helpers.format_cell(table, row, j, bg_color=bg_color, fg_color=fg_color, font=font)
                    else:
                        widget_helpers.format_cell(table, row, j, bg_color=bg_color, fg_color=fg_color, font=font, alignment=QtCore.Qt.AlignHCenter)
                row += 1

    # Checks if its possible to analyze
    def check_state(self):
        errors = []

        # Check for SpawnCycle length
        all_empty = True
        for wave in self.parent.wavedefs:
            if len(wave['Squads']) > 0:
                all_empty = False
                break
        if all_empty or len(self.parent.wavedefs) < 1:
            errors.append(f"- Cannot analyze an empty SpawnCycle. Must have at least one wave with ZEDs within!")
        
        # Check GameLength
        if ((len(self.parent.wavedefs) > 4) and (self.analysis_widgets['GameLength'].currentIndex() == 0)) or ((len(self.parent.wavedefs) > 7) and (self.analysis_widgets['GameLength'].currentIndex() in [0, 1])):
            errors.append(f"- Game Length setting is shorter than the currently defined set of waves!")

        return errors

    # Publishes analysis data for the SpawnCycle
    def analyze_wavedefs(self):
        # Check for errors first
        errors = self.check_state()
        if len(errors) > 0: # Print errors
            diag_title = 'WARNING'
            diag_text = 'The following error(s) were encountered while attempting to Analyze:\n\n'
            diag_text += '\n'.join(errors)
            x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 200 # Anchor dialog to center of window
            y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
            diag = widget_helpers.create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            diag.exec_() # Show a dialog to tell user to check messages
            return

        self.clear_scrollarea() # First clear out any prev data

        # Show "Loading" dialog
        diag_title = 'Analyzing..'
        x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 50 # Anchor dialog to center of window
        y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y() + 100
        diag_text = f"Analyzing.."
        loading_diag = widget_helpers.create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=False)
        loading_diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
        loading_diag.show() # Show a dialog to tell user to check messages

        # Get analysis data for each wave
        wave_stats = []
        difficulty_data = []
        for i in range(len(self.parent.wavedefs)):
            wave_sample, diff_sample = self.sample_wave(i)
            wave_stats.append(wave_sample)
            difficulty_data.append(diff_sample)

        # Add missing data for missing waves
        if len(self.parent.wavedefs) not in [4, 7, 10]:
            if len(self.parent.wavedefs) < 4:
                next_interval = 4
            elif len(self.parent.wavedefs) < 7:
                next_interval = 7
            else:
                next_interval = 10

            num_to_add = next_interval - len(self.parent.wavedefs)
            wave_stats += [None for j in range(num_to_add)]
            difficulty_data += [[(0.0, 0.0)] for k in range(num_to_add)]
        
        # Combine wave stats
        merged = {'Total': 0,
                  'Category': {'Trash': 0, 'Medium': 0, 'Large': 0, 'Boss': 0, 'Total': 0}, 
                  'Name': {'Cyst': 0, 'Alpha Clot': 0, 'Slasher': 0, 'Rioter': 0, 'Gorefast': 0, 'Gorefiend': 0, 'Crawler': 0, 'Elite Crawler': 0,
                           'Stalker': 0, 'Bloat': 0, 'Husk': 0, 'Siren': 0, 'E.D.A.R Trapper': 0, 'E.D.A.R Blaster': 0, 'E.D.A.R Bomber': 0,
                           'Quarter Pound': 0, 'Fleshpound': 0, 'Scrake': 0, 'Alpha Scrake': 0, 'Alpha Fleshpound': 0, 'Abomination Spawn': 0, 'King Fleshpound': 0,
                           'Dr. Hans Volter': 0, 'Patriarch': 0, 'Abomination': 0, 'Matriarch': 0, 'Total': 0},
                  'Group': {'Clots': 0, 'Gorefasts': 0, 'Crawlers / Stalkers': 0, 'Albino': 0, 'Robots': 0, 'Scrakes': 0, 'Fleshpounds': 0, 'SpawnRage': 0, 'Total': 0},
                  'SpawnRage': {'Quarter Pound': 0, 'Fleshpound': 0, 'Alpha Fleshpound': 0, 'Total': 0}}
        
        for ws in wave_stats:
            if ws is not None:
                merged['Total'] += ws['Total']
                merged['Category'] = self.merge_dicts(merged['Category'], ws['Category'])
                merged['Name'] = self.merge_dicts(merged['Name'], ws['Name'])
                merged['Group'] = self.merge_dicts(merged['Group'], ws['Group'])
                merged['SpawnRage'] = self.merge_dicts(merged['SpawnRage'], ws['SpawnRage'])

        # Fonts, stylesheets
        ss_label = 'color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);' # Stylesheet
        ss_params = 'color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);'
        sp_fixed = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_fixed.setHorizontalStretch(0)
        sp_fixed.setVerticalStretch(0)
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(10)
        font_label.setWeight(75)

        # Display params
        stripped_fname = self.parent.filename.replace('.json', '').replace('.txt', '')
        params_label = widget_helpers.create_label(None, text=f"PARAMETERS", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame = QtWidgets.QFrame()
        params_frame_layout = QtWidgets.QVBoxLayout(params_frame)
        params_frame.setStyleSheet(f"color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);")
        params_frame.setFrameShape(QtWidgets.QFrame.Box)
        params_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        params_frame.setLineWidth(2)

        gamelength_label = widget_helpers.create_label(None, text=f"Game Length:          {self.analysis_widgets['GameLength'].currentText()}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(gamelength_label)
        difficulty_label = widget_helpers.create_label(None, text=f"Difficulty:           {self.analysis_widgets['Difficulty'].currentText()}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(difficulty_label)
        wsf_label = widget_helpers.create_label(None, text=f"Wave Size Fakes:      {self.analysis_widgets['WaveSizeFakes'].text()}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(wsf_label)
        
        oo_str = 'TRUE' if self.analysis_widgets['Overview Only'].isChecked() else 'FALSE'
        oo_label = widget_helpers.create_label(None, text=f"Overview Only:        {oo_str}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(oo_label)

        iz_str = 'TRUE' if self.analysis_widgets['Ignore Zeroes'].isChecked() else 'FALSE'
        iz_label = widget_helpers.create_label(None, text=f"Ignore Zeroes:        {iz_str}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(iz_label)

        ad_str = 'TRUE' if self.analysis_widgets['Analyze Difficulty'].isChecked() else 'FALSE'
        ad_label = widget_helpers.create_label(None, text=f"Analyze Difficulty:   {ad_str}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(ad_label)
        
        mm_label = widget_helpers.create_label(None, text=f"Max Monsters:         {self.analysis_widgets['MaxMonsters'].text()}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(mm_label)
        
        dc_str = 'TRUE' if self.analysis_widgets['Display Charts'].isChecked() else 'FALSE'
        dc_label = widget_helpers.create_label(None, text=f"Display Charts:       {dc_str}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(dc_label)

        # Add parameters stuff
        self.scrollarea_contents_layout.addWidget(params_label)
        self.scrollarea_contents_layout.addWidget(params_frame)
        self.analysis_widgets.update({'ParamsLabel': params_label, 'ParamsFrame': params_frame}) # Saving these so we can get to them later

        # Display combined stats
        avg_difficulty_data = [(0, 0.0)] + [(i+1, float(sum([y for _, y in difficulty_data[i]])) / float(len(difficulty_data[i]))) for i in range(0, len(difficulty_data))]
        axis_data = {'X': {'Title': '\nWave', 'Labels': [str(i) for i in range(1, len(difficulty_data)+1)], 'Min': 0, 'Max': len(self.parent.wavedefs)}, 'Y': {'Title': 'Average Difficulty\n', 'Tick': 10, 'Min': 0, 'Max': 755000}}
        merged_label = widget_helpers.create_label(None, text=f"\n\nALL WAVES", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        merged_frame, merged_frame_children = self.create_waveframe(merged, merged=True, difficulty_data=avg_difficulty_data, axis_data=axis_data) # Create table

        # Create dict of compiled data
        self.compiled_data = {'merged': (merged_label, merged_frame)}

        # Display stats per-wave
        if not self.params['Overview Only']:
            for i in range(len(wave_stats)):
                if wave_stats[i] is not None:
                    x_max = difficulty_data[i][-1][0]
                    axis_data = {'X': {'Title': '\nWave Progress (%)', 'Labels': ['10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'], 'Min': 0, 'Max': x_max}, 'Y': {'Title': 'Difficulty\n', 'Tick': 10, 'Min': 0, 'Max': 755000}}
                    wave_label = widget_helpers.create_label(None, text=f"\n\nWAVE {i+1}", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
                    wave_frame, wave_frame_children = self.create_waveframe(wave_stats[i], merged=False, difficulty_data=difficulty_data[i], axis_data=axis_data) # Create table
                    self.compiled_data.update({str(i): (wave_label, wave_frame)})

        # Set the first wave shown. This will either be the summary or the most recently viewed wave
        if not self.params['Overview Only']:
            if self.active_wave not in self.compiled_data: # This wave might not be available anymore!
                self.active_wave = 'merged' # Set it back to 'All' because that one's always available
            (wave_label, wave_frame) = self.compiled_data[self.active_wave]
        else: # Was on a numbered wave before and we might have turned the overview only flag on. Need to update accordingly
            (wave_label, wave_frame) = self.compiled_data['merged'] # Show only summary data
            self.active_wave = 'merged'

        self.scrollarea_contents_layout.addWidget(wave_label)
        self.scrollarea_contents_layout.addWidget(wave_frame)

        # Hide all previous wave buttons
        for button in self.buttons['WaveButtons'].values():
            button.setVisible(False)

        # Unhide the wave tab buttons we need
        for (wnum, data) in self.compiled_data.items():
            if data is not None:
                border_color = 'orange' if wnum == self.active_wave else 'white'
                wbutton = self.buttons['WaveButtons'][wnum]
                wbutton.setStyleSheet(f"color: rgb(255, 255, 255);\nbackground-color: rgb(40, 40, 40);\nborder: 2px solid {border_color};") # Set initial border
                wbutton.setVisible(True) # Unhide the button

        # Reset scrollbar to top
        #self.scrollarea.verticalScrollBar().setValue(0);

        loading_diag.close()
        self.parent.last_analyze_preset = self.params

        # Show a dialog indicating completion
        diag_title = 'SpawnCycler'
        x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 100 # Anchor dialog to center of window
        y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y() + 100
        diag_text = f"Analysis completed successfully!"
        diag = widget_helpers.create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
        diag.setWindowIcon(QtGui.QIcon('img/icon_check.png'))
        diag.exec_() # Show a dialog to tell user to check messages

    # Sets up the per wave tabs
    def setup_wave_buttons(self):
        # Fonts and stuff
        sp_button = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        font_button = QtGui.QFont()
        font_button.setFamily(_DEF_FONT_FAMILY)
        font_button.setPointSize(10)
        font_button.setWeight(75)

        wnums = ['merged', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for wnum in wnums:
            button_title = 'All' if wnum == 'merged' else f"Wave {int(wnum)+1}"
            wave_button = widget_helpers.create_button(None, None, None, text=button_title, size_policy=sp_button, font=font_button, options=False, squad=False, draggable=False)
            wave_button.setMinimumSize(QtCore.QSize(64, 32))
            wave_button.clicked.connect(partial(self.load_wave, wnum))
            self.buttons['WaveButtons'].update({wnum: wave_button}) # Add this so we can get to it easily later
            self.wave_button_layout.addWidget(wave_button)
            wave_button.setVisible(False)

    # Loads a wave into the analyzer's scroll area
    def load_wave(self, wave):
        # First clear the rest of the waves
        for i in reversed(range(self.scrollarea_contents_layout.count())): 
            self.scrollarea_contents_layout.itemAt(i).widget().setParent(None)

        # Set all wave buttons to white border
        for (wnum, wdata) in self.compiled_data.items():
            if wnum != wave:
                self.buttons['WaveButtons'][wnum].setStyleSheet(f"color: rgb(255, 255, 255);\nbackground-color: rgb(40, 40, 40);\nborder: 2px solid white;")
        self.buttons['WaveButtons'][wave].setStyleSheet(f"color: rgb(255, 255, 255);\nbackground-color: rgb(40, 40, 40);\nborder: 2px solid orange;") # Set the button for this wave

        # Load up the new wave
        (wave_label, wave_frame) = self.compiled_data[wave]
        self.scrollarea_contents_layout.addWidget(self.analysis_widgets['ParamsLabel'])
        self.scrollarea_contents_layout.addWidget(self.analysis_widgets['ParamsFrame'])
        self.scrollarea_contents_layout.addWidget(wave_label)
        self.scrollarea_contents_layout.addWidget(wave_frame)

        # Set the active wave in case we re-analyze without closing the window
        self.active_wave = wave

    # Merges dict B into A and returns a new dict C
    # Assumes all integer values
    def merge_dicts(self, a, b):
        merged = {}
        for key in b:
            if key in a:
                merged[key] = a[key] + b[key]
            else:
                merged[key] = b[key]
        return merged

    # Expands a wave's Squads into a 1-dimensional list
    def expand_squads(self, wavedef):
        expanded = []
        for squad in wavedef['Squads']:
            for (zed, data) in squad['ZEDs'].items():
                # Turn {'Clot': 4} into [Clot, Clot, Clot, Clot], etc
                if 'Enraged' in zed:
                    zed_name = zed.replace(' (Enraged)', '') # Kinda hacky. A dict entry means an enraged ZED
                    zeds = [{'Raged': zed_name} for i in range(data['Count'])]
                else:
                    zeds = [zed for i in range(data['Count'])]
                expanded += zeds

        return expanded

    # Clears out the entire scrollarea of all widgets
    def clear_scrollarea(self):
        for i in reversed(range(self.scrollarea_contents_layout.count())): 
            self.scrollarea_contents_layout.itemAt(i).widget().setParent(None)

    def setup_scrollarea(self, Dialog):
        self.scrollarea = QtWidgets.QScrollArea()
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(self.scrollarea.sizePolicy().hasHeightForWidth())
        self.scrollarea.setSizePolicy(sp)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setStyleSheet(f"color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);")
        self.scrollarea.setFrameShape(QtWidgets.QFrame.Box)
        self.scrollarea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrollarea.setLineWidth(2)
        self.scrollarea_contents = QtWidgets.QWidget()
        self.scrollarea_contents.setGeometry(QtCore.QRect(0, 0, 990, 815))
        self.scrollarea_contents_layout = QtWidgets.QVBoxLayout(self.scrollarea_contents)
        self.scrollarea_contents_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.scrollarea.setWidget(self.scrollarea_contents)

    def setup_options_pane(self, Dialog):
        # Style stuff
        ss = 'color: rgb(255, 255, 255);' # Stylesheet
        ss_cbox = 'QToolTip {color: rgb(0, 0, 0);} QComboBox {color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);}' # Stylesheet
        ss_label = "QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};"
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(10)
        font.setWeight(75)
        font_button = QtGui.QFont()
        font_button.setFamily(_DEF_FONT_FAMILY)
        font_button.setPointSize(12)
        font_button.setWeight(75)

        #gamelength_label = widget_helpers.create_label(None, text='Game Length', tooltip=None, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        simulate_button = widget_helpers.create_button(None, None, None, text=' Simulate! ', icon_path='img/icon_go.png', icon_w=24, icon_h=24, style="color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);", size_policy=sp, font=font_button, options=False, squad=False, draggable=False)
        simulate_button.clicked.connect(self.analyze_wavedefs)
        simulate_frame = QtWidgets.QFrame()
        simulate_frame_layout = QtWidgets.QHBoxLayout(simulate_frame)
        simulate_frame_layout.setAlignment(QtCore.Qt.AlignCenter)
        simulate_frame_layout.addWidget(simulate_button)

        # Set up GameLength area
        gamelength_label = widget_helpers.create_label(None, text='Game Length       ', tooltip="The Length of the game.\nDifferent Game Lengths affect the way the waves are sampled.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        gamelength_label.setStyleSheet(ss_label)
        gamelength_cbox = widget_helpers.create_combobox(None, options=['Short (4 Waves)', 'Medium (7 Waves)', 'Long (10 Waves)'], style=ss_cbox, size_policy=sp)
        gamelength_cbox.setToolTip(f"The Length of the game.\nDifferent Game Lengths affect the way the waves are sampled.")
        gamelength_cbox.setStyleSheet("QComboBox {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);} QToolTip {color: rgb(0, 0, 0)};")
        gamelength_cbox.activated.connect(partial(self.update_param, 'GameLength', gamelength_cbox))
        gamelength_frame = QtWidgets.QFrame()
        gamelength_frame_layout = QtWidgets.QHBoxLayout(gamelength_frame)
        gamelength_frame_layout.addWidget(gamelength_label)
        gamelength_frame_layout.addWidget(gamelength_cbox)
        gamelength_frame_layout.setAlignment(QtCore.Qt.AlignLeft)
        #gamelength_cbox.setEnabled(False)

        # Set up GameLength
        preferred_length = meta.get_keyvalue('analyze_default_length')
        numwaves = {0: 4, 1: 7, 2: 10} # Last used
        if (preferred_length == 0) and (self.parent.last_analyze_preset is not None) and (len(self.parent.wavedefs) <= numwaves[self.parent.last_analyze_preset['GameLength']]):
            gamelength_cbox.setCurrentIndex(self.parent.last_analyze_preset['GameLength'])
            self.params.update({'GameLength': self.parent.last_analyze_preset['GameLength']})
        elif (preferred_length == 2) and (len(self.parent.wavedefs) <= 4): # Preferred Short
            gamelength_cbox.setCurrentIndex(0)
            self.params.update({'GameLength': 0})
        elif (preferred_length == 3) and (len(self.parent.wavedefs) <= 7): # Preferred Medium
            gamelength_cbox.setCurrentIndex(1)
            self.params.update({'GameLength': 1})
        elif (preferred_length == 4) or (preferred_length == 0 and self.parent.last_analyze_preset is None): # Preferred Long or last used where we don't have a last used yet
            gamelength_cbox.setCurrentIndex(2)
            self.params.update({'GameLength': 2})

        # Adaptive. Pick the closest gamelength
        else:
            if len(self.parent.wavedefs) <= 4:
                gamelength_cbox.setCurrentIndex(0)
                self.params.update({'GameLength': 0})
            elif len(self.parent.wavedefs) <= 7:
                gamelength_cbox.setCurrentIndex(1)
                self.params.update({'GameLength': 1})
            else:
                gamelength_cbox.setCurrentIndex(2)
                self.params.update({'GameLength': 2})

        # Set up Difficulty area
        difficulty_label = widget_helpers.create_label(None, text='Difficulty        ', tooltip="The Difficulty of the game to sample from.\nHarder difficulties make the waves larger.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        difficulty_label.setStyleSheet(ss_label)
        difficulty_cbox = widget_helpers.create_combobox(None, options=['Normal', 'Hard', 'Suicidal', 'Hell on Earth'], style=ss_cbox, size_policy=sp)
        difficulty_cbox.setCurrentIndex(3) # HoE is default
        difficulty_cbox.setToolTip("The Difficulty of the game to sample from.\nHarder difficulties make the waves larger.")
        difficulty_cbox.setStyleSheet("QComboBox {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);} QToolTip {color: rgb(0, 0, 0)};")
        difficulty_cbox.activated.connect(partial(self.update_param, 'Difficulty', difficulty_cbox))
        self.params.update({'Difficulty': 3})
        difficulty_frame = QtWidgets.QFrame()
        difficulty_frame_layout = QtWidgets.QHBoxLayout(difficulty_frame)
        difficulty_frame_layout.addWidget(difficulty_label)
        difficulty_frame_layout.addWidget(difficulty_cbox)
        difficulty_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Set up WSF area
        wavesize_label = widget_helpers.create_label(None, text='Wave Size Fakes   ', tooltip="The number of players to sample the waves from.\nHigher values make the waves larger.\nAssumes the 'Ignore Humans' Fakes Mode setting.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        wavesize_label.setStyleSheet(ss_label)
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(10)
        font.setWeight(75)
        wavesize_textarea = widget_helpers.create_textfield('12', font, sp, ss, 48, 28)
        wavesize_textarea.setToolTip("The number of players to sample the waves from.\nHigher values make the waves larger.\nAssumes the 'Ignore Humans' Fakes Mode setting.")
        wavesize_textarea.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLineEdit {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50); border: 2px solid white;};")
        
        # Set up signals
        wavesize_textarea.textChanged.connect(partial(self.edit_textbox, wavesize_textarea))
        wavesize_textarea.editingFinished.connect(partial(self.commit_textbox, wavesize_textarea, 'WaveSizeFakes', _WAVESIZE_MIN, _WAVESIZE_MAX))

        # Initialize internal value
        self.params.update({'WaveSizeFakes': 12})
        wavesize_frame = QtWidgets.QFrame()
        wavesize_frame_layout = QtWidgets.QHBoxLayout(wavesize_frame)
        wavesize_frame_layout.addWidget(wavesize_label)
        wavesize_frame_layout.addWidget(wavesize_textarea)
        wavesize_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Set up Ignore Zeroes area
        iz_checkbox = QtWidgets.QCheckBox()
        iz_checkbox.setChecked(True)
        iz_checkbox.setToolTip("Don't display fields with zero value.")
        iz_checkbox.setStyleSheet("QToolTip {color: rgb(0, 0, 0)};")
        iz_checkbox.toggled.connect(partial(self.update_param, 'Ignore Zeroes', iz_checkbox))
        iz_label = widget_helpers.create_label(None, text='Ignore Zeroes          ', tooltip="Don't display fields with zero value.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        iz_label.setStyleSheet(ss_label)
        self.params.update({'Ignore Zeroes': iz_checkbox.isChecked()})
        iz_frame = QtWidgets.QFrame()
        iz_frame_layout = QtWidgets.QHBoxLayout(iz_frame)
        iz_frame_layout.addWidget(iz_label)
        iz_frame_layout.addWidget(iz_checkbox)
        iz_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Set up Analyze Difficulty area
        analyze_difficulty_checkbox = QtWidgets.QCheckBox()
        analyze_difficulty_checkbox.setChecked(True)
        analyze_difficulty_checkbox.setToolTip("Produce a chart showing the (relative) difficulty curve of the wave.")
        analyze_difficulty_checkbox.setStyleSheet("QToolTip {color: rgb(0, 0, 0)};")
        analyze_difficulty_checkbox.toggled.connect(self.update_analyze_difficulty)
        analyze_difficulty_label = widget_helpers.create_label(None, text='Analyze Difficulty     ', tooltip="Produce a chart showing the (relative) difficulty curve of the wave.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        analyze_difficulty_label.setStyleSheet(ss_label)
        self.params.update({'Analyze Difficulty': analyze_difficulty_checkbox.isChecked()})
        analyze_difficulty_frame = QtWidgets.QFrame()
        analyze_difficulty_frame_layout = QtWidgets.QHBoxLayout(analyze_difficulty_frame)
        analyze_difficulty_frame_layout.addWidget(analyze_difficulty_label)
        analyze_difficulty_frame_layout.addWidget(analyze_difficulty_checkbox)
        analyze_difficulty_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Set up Display Charts area
        display_charts_checkbox = QtWidgets.QCheckBox()
        display_charts_checkbox.setChecked(True)
        display_charts_checkbox.setToolTip("Show graphical charts related to Analysis data.")
        display_charts_checkbox.setStyleSheet("QToolTip {color: rgb(0, 0, 0)};")
        display_charts_checkbox.toggled.connect(partial(self.update_param, 'Display Charts', display_charts_checkbox))
        display_charts_label = widget_helpers.create_label(None, text='Display Charts         ', tooltip="Show graphical charts related to Analysis data.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        display_charts_label.setStyleSheet(ss_label)
        self.params.update({'Display Charts': display_charts_checkbox.isChecked()})
        display_charts_frame = QtWidgets.QFrame()
        display_charts_frame_layout = QtWidgets.QHBoxLayout(display_charts_frame)
        display_charts_frame_layout.addWidget(display_charts_label)
        display_charts_frame_layout.addWidget(display_charts_checkbox)
        display_charts_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Setup Overview Only area
        overview_only_checkbox = QtWidgets.QCheckBox()
        overview_only_checkbox.setChecked(False)
        overview_only_checkbox.setToolTip("Exclude individual wave statistics from the Analysis Results.")
        overview_only_checkbox.setStyleSheet("QToolTip {color: rgb(0, 0, 0)};")
        overview_only_checkbox.toggled.connect(partial(self.update_param, 'Overview Only', overview_only_checkbox))
        overview_only_label = widget_helpers.create_label(None, text='Overview Only     ', tooltip="Legacy feature: Exclude individual wave statistics from the Analysis Results. Speeds up analysis time.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        overview_only_label.setStyleSheet(ss_label)
        self.params.update({'Overview Only': overview_only_checkbox.isChecked()})
        overview_only_frame = QtWidgets.QFrame()
        overview_only_frame_layout = QtWidgets.QHBoxLayout(overview_only_frame)
        overview_only_frame_layout.addWidget(overview_only_label)
        overview_only_frame_layout.addWidget(overview_only_checkbox)
        overview_only_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Set up MaxMonsters area
        maxmonsters_label = widget_helpers.create_label(None, text='Max Monsters           ', tooltip="The maximum number of ZEDs that can be alive at once.\nHigher values make the waves more difficult.\nOnly used if the 'Analyze Difficulty' setting is TRUE.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        maxmonsters_label.setStyleSheet(ss_label)
        maxmonsters_textarea = widget_helpers.create_textfield('32', font, sp, ss, 48, 28)
        maxmonsters_textarea.setToolTip("The maximum number of ZEDs that can be alive at once.\nHigher values make the waves more difficult.\nOnly used if the 'Analyze Difficulty' setting is TRUE.")
        maxmonsters_textarea.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLineEdit {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50); border: 2px solid white;};")

        # Set up signals
        maxmonsters_textarea.textChanged.connect(partial(self.edit_textbox, maxmonsters_textarea))
        maxmonsters_textarea.editingFinished.connect(partial(self.commit_textbox, maxmonsters_textarea, 'MaxMonsters', _MAXMONSTERS_MIN, _MAXMONSTERS_MAX))

        # Initialize internal value
        self.params.update({'MaxMonsters': 32})
        maxmonsters_frame = QtWidgets.QFrame()
        maxmonsters_frame_layout = QtWidgets.QHBoxLayout(maxmonsters_frame)
        maxmonsters_frame_layout.addWidget(maxmonsters_label)
        maxmonsters_frame_layout.addWidget(maxmonsters_textarea)
        maxmonsters_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Put it all together
        config_frame = QtWidgets.QFrame()
        config_frame_layout = QtWidgets.QGridLayout(config_frame)
        config_frame_layout.setAlignment(QtCore.Qt.AlignTop)
        config_frame_layout.addWidget(gamelength_frame, 0, 0, 1, 1)
        config_frame_layout.addWidget(iz_frame, 0, 1, 1, 1)
        config_frame_layout.addWidget(difficulty_frame, 1, 0, 1, 1)
        config_frame_layout.addWidget(analyze_difficulty_frame, 1, 1, 1, 1)
        config_frame_layout.addWidget(wavesize_frame, 2, 0, 1, 1)
        config_frame_layout.addWidget(maxmonsters_frame, 2, 1, 1, 1)
        config_frame_layout.addWidget(overview_only_frame, 3, 0, 1, 1)
        config_frame_layout.addWidget(display_charts_frame, 3, 1, 1, 1)
        config_frame_layout.setSpacing(0)
        
        # Insert into main layout
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)

        self.options_pane = QtWidgets.QFrame()
        self.options_pane.setSizePolicy(sp)
        options_pane_layout = QtWidgets.QVBoxLayout(self.options_pane)
        options_pane_layout.addWidget(config_frame)
        options_pane_layout.addWidget(simulate_frame)
        self.options_pane.setStyleSheet(f"color: rgb(255, 255, 255); background-color: rgb(40, 40, 40)")
        self.options_pane.setFrameShape(QtWidgets.QFrame.Box)
        self.options_pane.setFrameShadow(QtWidgets.QFrame.Plain)
        self.options_pane.setLineWidth(2)

        self.buttons.update({'Analyze': simulate_button})
        self.analysis_widgets = {'GameLength': gamelength_cbox, 'Difficulty': difficulty_cbox, 'WaveSizeFakes': wavesize_textarea,
                                 'Ignore Zeroes': iz_checkbox, 'Analyze Difficulty': analyze_difficulty_checkbox, 'MaxMonsters': maxmonsters_textarea,
                                 'Overview Only': overview_only_checkbox, 'Display Charts': display_charts_checkbox}

    # Called when a textbox is edited
    def edit_textbox(self, textbox):
        if not textbox.text().isnumeric(): # NaN somehow (for example the field is empty)
            return

        # Remove any leading zeroes
        val = int(textbox.text()) # Conv to an int will remove the zeroes on its own. Guaranteed to be numeric at this point
        if val == 0:
            if textbox.text().count('0') > 1: # Special case for zero, just replace it. Stripping won't work here
                textbox.setText('0')
        else:
            textbox.setText(textbox.text().lstrip('0'))

    # Called when the WaveSizeFakes field is changed
    def commit_textbox(self, textbox, key, min_value, max_value):
        if not textbox.text().isnumeric():
            textbox.setText(str(self.params[key]))
            return

        # Same value as we already have set. Do nothing
        if int(textbox.text()) == self.params[key]:
            return

        # Set the value of the textfield
        val = int(textbox.text())
        if val < min_value: # Too low
            textbox.setText(str(min_value))
        elif val > max_value: # Too high
            textbox.setText(str(max_value))

        # Update the param
        self.update_param(key, textbox)

    # Updates a specific parameter
    def update_param(self, key, widget):
        if isinstance(widget, QtWidgets.QCheckBox):
            self.params.update({key: widget.isChecked()})
        elif isinstance(widget, QtWidgets.QComboBox):
            self.params.update({key: widget.currentIndex()})
        elif isinstance(widget, QtWidgets.QLineEdit):
            self.params.update({key: int(widget.text())})

    # Called when the Analyze Difficulty field is changed
    def update_analyze_difficulty(self):
        self.update_param('Analyze Difficulty', self.analysis_widgets['Analyze Difficulty'])

        mm_widget = self.analysis_widgets['MaxMonsters']
        if not self.analysis_widgets['Analyze Difficulty'].isChecked(): # Disable MaxMonsters
            mm_widget.setEnabled(False) # Gray out the textbox
            mm_widget.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLineEdit {color: rgb(0, 0, 0); background-color: rgb(50, 50, 50);};")
        else:
            mm_widget.setEnabled(True)
            mm_widget.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLineEdit {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")

    # Called when this dialog is closed
    def teardown(self):
        self.parent.analyze_dialog = None
        self.parent.last_analyze_preset = self.params

    # Called when this dialog is opened (if a preset was given)
    def load_preset(self, preset):
        # Set up the analysis widgets
        self.analysis_widgets['Difficulty'].setCurrentIndex(preset['Difficulty'])
        self.analysis_widgets['WaveSizeFakes'].setText(str(preset['WaveSizeFakes']))
        self.analysis_widgets['Ignore Zeroes'].setChecked(preset['Ignore Zeroes'])
        self.analysis_widgets['Analyze Difficulty'].setChecked(preset['Analyze Difficulty'])
        self.analysis_widgets['MaxMonsters'].setText(str(preset['MaxMonsters']))
        self.analysis_widgets['Overview Only'].setChecked(preset['Overview Only'])
        self.analysis_widgets['Display Charts'].setChecked(preset['Display Charts'])

        # Finally, override the params
        preset['GameLength'] = self.params['GameLength'] # Except for gamelength, cause this depends on the number of waves
        self.params = preset

    # Completely clears all analysis data
    def reset_state(self):
        self.results_label.setText('Analysis Results') # Reset title label
        self.clear_scrollarea() # Clear out any prev data

        # Clear all the wave buttons and clear any analysis data
        for wave_button in self.buttons['WaveButtons'].values():
            wave_button.setVisible(False)
        self.compiled_data = {}
        
    def setupUi(self, Dialog):
        Dialog.setFixedSize(_WINDOWSIZE_ANALYZE_W, _WINDOWSIZE_ANALYZE_H)
        Dialog.setStyleSheet("background-color: rgb(50, 50, 50);")

        # Style stuff
        ss = 'color: rgb(255, 255, 255);' # Stylesheet
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(12)
        font.setWeight(75)

        # Set up main layout
        self.main_layout = QtWidgets.QVBoxLayout(Dialog)
        self.setup_scrollarea(Dialog) # Set up main window stuff
        self.setup_options_pane(Dialog) # Set up the options buttons at the bottom

        # Set up wave button frame
        self.wave_button_frame = QtWidgets.QFrame()
        self.wave_button_layout = QtWidgets.QHBoxLayout(self.wave_button_frame)
        self.wave_button_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.wave_button_layout.setSpacing(0)

        # Set up the wave buttons
        self.setup_wave_buttons()
        
        # Put everything in
        self.params_label = widget_helpers.create_label(None, text='\nAnalysis Parameters', tooltip=None, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)
        file_ext = self.parent.get_file_ext(self.parent.filename)
        trunc = self.parent.truncate_filename(self.parent.filename)
        self.results_label = widget_helpers.create_label(None, text=f"Analysis Results{'' if file_ext is None else (' (' + trunc.replace(file_ext, '') + ')')}", tooltip=None, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.results_label)
        self.main_layout.addWidget(self.wave_button_frame)
        self.main_layout.addWidget(self.scrollarea)
        self.main_layout.addWidget(self.params_label)
        self.main_layout.addWidget(self.options_pane)
        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)

        # Load the last used preset (if one is given)
        if self.parent.last_analyze_preset is not None:
            self.load_preset(self.parent.last_analyze_preset)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate

#
#  analyze.py
#
#  Author: Tamari (Nathan P. Ybanez)
#  Date of creation: 11/27/2020
#
#  UI code for the 'Analyze' functionality
#

from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import widget_helpers

_DEF_FONT_FAMILY = 'Consolas'

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
                'Total': QtGui.QColor(184, 214, 224)}


# Represents a RGB color
class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"({self.r}, {self.g}, {self.b})"


class AnalyzeDialog(object):
    # Returns the WaveSizeMultiplier based on the current WSF
    def get_wavesize_multiplier(self, wsf):
        wavesz = [1.0, 2.0, 2.75, 3.5, 4.0, 4.5]
        if wsf == 0:
            return 1.0
        elif wsf <= 6:
            return wavesz[wsf-1]
        return 4.5 + ((wsf-6) * 0.211718) # 0.21175

    # Returns the BaseNumZEDs based on the current wave and gamelength
    def get_base_num_zeds(self, wave_id, gamelength):
        base_num_zeds = [[25, 32, 35, 42],
                       [25, 28, 32, 32, 35, 40, 42],
                       [25, 28, 32, 32, 35, 35, 35, 40, 42, 42]]
        return base_num_zeds[gamelength][wave_id]

    # Returns the DifficultyMod
    def get_difficulty_mod(self, difficulty):
        df = [0.85, 1.0, 1.3, 1.7]
        return df[difficulty]

    # Returns analysis data for the given wave
    def sample_wave(self, wave_id):
        # Params
        base_num_zeds = self.get_base_num_zeds(wave_id, self.params['GameLength'])
        diffmod = self.get_difficulty_mod(self.params['Difficulty'])
        wavesize_multi = self.get_wavesize_multiplier(self.params['WaveSizeFakes'])

        # The number of ZEDs that will be in this wave
        wave_num_zeds = int((base_num_zeds * diffmod * wavesize_multi) // 1)

        trash_zeds = ['Cyst', 'Alpha Clot', 'Slasher', 'Rioter', 'Gorefast', 'Gorefiend',
                      'Crawler', 'Elite Crawler', 'Stalker']
        medium_zeds = ['Bloat', 'Husk', 'Siren', 'E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber']
        large_zeds = ['Quarter Pound', 'Fleshpound', 'Scrake', 'Alpha Scrake', 'Alpha Fleshpound']
        albino = ['Rioter', 'Gorefiend', 'Elite Crawler', 'Alpha Scrake', 'Alpha Fleshpound']
        bosses = ['King Fleshpound', 'Abomination', 'Dr. Hans Volter', 'Patriarch', 'Matriarch', 'Abomination Spawn']

        # Expand this wave's squads
        expanded_squads = self.expand_squads(self.wavedefs[wave_id])
        j = 0

        # Simulate the wave!
        wave_stats = {'Total': wave_num_zeds,
                      'Category': {'Trash': 0, 'Medium': 0, 'Large': 0, 'Boss': 0, 'Total': 0}, 
                      'Name': {'Cyst': 0, 'Alpha Clot': 0, 'Slasher': 0, 'Rioter': 0, 'Gorefast': 0, 'Gorefiend': 0, 'Crawler': 0, 'Elite Crawler': 0,
                               'Stalker': 0, 'Bloat': 0, 'Husk': 0, 'Siren': 0, 'E.D.A.R Trapper': 0, 'E.D.A.R Blaster': 0, 'E.D.A.R Bomber': 0,
                               'Quarter Pound': 0, 'Fleshpound': 0, 'Scrake': 0, 'Alpha Scrake': 0, 'Alpha Fleshpound': 0, 'Abomination Spawn': 0, 'King Fleshpound': 0,
                               'Dr. Hans Volter': 0, 'Patriarch': 0, 'Abomination': 0, 'Matriarch': 0, 'Total': 0},
                      'Group': {'Clots': 0, 'Gorefasts': 0, 'Crawlers / Stalkers': 0, 'Robots': 0, 'Scrakes': 0, 'Fleshpounds': 0, 'Albino': 0, 'SpawnRage': 0, 'Total': 0},
                      'SpawnRage': {'Quarter Pound': 0, 'Fleshpound': 0, 'Alpha Fleshpound': 0, 'Total': 0}}

        # Count up the ZEDs
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
                    if next_zed in ['Cyst', 'Alpha Clot', 'Slasher', 'Rioter']:
                        wave_stats['Group']['Clots'] += 1
                    elif next_zed in ['Gorefast', 'Gorefiend']:
                        wave_stats['Group']['Gorefasts'] += 1
                    elif next_zed in ['Crawler', 'Elite Crawler', 'Stalker']:
                        wave_stats['Group']['Crawlers / Stalkers'] += 1
                    wave_stats['Category']['Trash'] += 1

                # Medium ZEDs
                elif next_zed in medium_zeds:
                    if next_zed in ['E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber']:
                        wave_stats['Group']['Robots'] += 1
                    wave_stats['Category']['Medium'] += 1

                # Large ZEDs
                elif next_zed in large_zeds:
                    if next_zed in ['Scrake', 'Alpha Scrake']:
                        wave_stats['Group']['Scrakes'] += 1
                    elif next_zed in ['Fleshpound', 'Alpha Fleshpound', 'Quarter Pound']:
                        wave_stats['Group']['Fleshpounds'] += 1
                    wave_stats['Category']['Large'] += 1

                # Bosses
                else:
                    wave_stats['Category']['Boss'] += 1

                if next_zed in albino: # Check for albinos
                    wave_stats['Group']['Albino'] += 1

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
                currently_spawned_zeds.pop(0) # Remove the first ZED

            trash_zeds = ['Cyst', 'Alpha Clot', 'Slasher', 'Rioter', 'Gorefast', 'Gorefiend',
                          'Crawler', 'Elite Crawler', 'Stalker', 'Abomination Spawn'] # Abom spawn is considered Trash ZED for this calculation
            medium_zeds = ['Bloat', 'Husk', 'Siren', 'E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber']
            large_zeds = ['Quarter Pound', 'Fleshpound', 'Scrake', 'Alpha Scrake', 'Alpha Fleshpound']
            albino = ['Rioter', 'Gorefiend', 'Elite Crawler', 'Alpha Scrake', 'Alpha Fleshpound']
            bosses = ['King Fleshpound', 'Abomination', 'Dr. Hans Volter', 'Patriarch', 'Matriarch']

            # Get the difficulty score at this point
            # ZED count modifier: ZEDs have varying weights
            zed_weights = {'Trash': 250, 'Medium': 1000, 'Large': 2000, 'Boss': 10000}
            num_trash = sum([1 if z in trash_zeds else 0 for z in currently_spawned_zeds])
            num_medium = sum([1 if z in medium_zeds else 0 for z in currently_spawned_zeds])
            num_large = sum([1 if z in large_zeds else 0 for z in currently_spawned_zeds])
            num_bosses = sum([1 if z in bosses else 0 for z in currently_spawned_zeds])
            zed_count_mod = ((num_trash * zed_weights['Trash']) + (num_medium * zed_weights['Medium']) +
                             (num_large * zed_weights['Large']) + (num_bosses * zed_weights['Boss']))
            zed_diff_mod = self.params['Difficulty'] + 1 # ZED difficulty modifier: (harder difficulty = stronger attacks / more damage dealt)
            zed_score_mod = zed_diff_mod * zed_count_mod

            # Wave modifier, based on how far into the game this is.
            # Earlier waves tend to be harder due to less money/economy
            # Difficulty also affects this since it changes how much dosh you earn per kill
            max_wave = {0: 10, 1: 7, 2: 4}
            doshmod = {0: 1.0, 1: 1.25, 2: 1.5, 3: 1.75}
            wave_score_mod = (1.5 * doshmod[self.params['Difficulty']]) * (float(wave_id+1) / float(max_wave[self.params['GameLength']]))
            
            # Calculate the final score
            difficulty_score = wave_score_mod * zed_score_mod

            if difficulty_score > 750000: # Cap Difficulty Score at 1M
                difficulty_score = 750000.0
            difficulty_data.append(((float(i+1) / float((wave_num_zeds))) * 100, float(difficulty_score)))

        return wave_stats, difficulty_data

    # Creates and returns a Table object representing the wave's data
    def create_waveframe(self, wave_data, merged=False, difficulty_data=None, axis_data=None):
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

        label_zed_category = widget_helpers.create_label(None, text='ZEDs by Category', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
        table_zed_category = widget_helpers.create_table(None, zed_category_data, num_rows=len(zed_category_data) // 3, num_cols=3, stretch=False)
        
        # Format table
        widget_helpers.set_plain_border(table_zed_category, Color(255, 255, 255), 2)
        self.format_table(table_zed_category, table_type='categorical')

        # Create ZEDs by Category Pie Chart
        if self.params['Display Charts']:
            chart_data = []
            for (category, count) in wave_data['Category'].items():
                if category not in ['Total'] and count > 0:
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
        widget_helpers.set_plain_border(table_zed_type, Color(255, 255, 255), 2)
        self.format_table(table_zed_type, table_type='type')

        # Setup ZEDs by Group Table
        zed_group_data = [(0, 0, ' Name '),
                          (0, 1, '  Count  '),
                          (0, 2, '  % of Total  ')]
        row = 1
        col = 0
        group_items = list(wave_data['Group'].items())
        group_sum = sum([x[1] for x in group_items if x[0] != 'Total'])

        if group_sum > 0:
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
            widget_helpers.set_plain_border(table_zed_group, Color(255, 255, 255), 2)
            self.format_table(table_zed_group, table_type='categorical')

            # Create ZEDs by Group Pie Chart
            if self.params['Display Charts']:
                chart_data = []
                for (group, count) in wave_data['Group'].items():
                    if group not in ['Total', 'Albino', 'SpawnRage'] and count > 0:
                        percent = (float(count) / float(wave_data['Total'])) * 100.0
                        chart_data.append((group, count, light_colors[group], percent))
                chart_zed_group = widget_helpers.create_chart(None, chart_data, '', chart_type='pie')

        if difficulty_data is not None and self.params['Analyze Difficulty']:
            label_diff_text = f"\n\nESTIMATED WAVE DIFFICULTY\n" if not merged else f"\n\nSPAWNCYCLE DIFFICULTY\n"
            label_wave_diff = widget_helpers.create_label(None, text=label_diff_text, tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_mm = widget_helpers.create_label(None, text=f"MaxMonsters:    {self.params['MaxMonsters']}\nDificulty:      {self.analysis_widgets['Difficulty'].currentText()}\nWaveSizeFakes:  {self.params['WaveSizeFakes']}", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_assumes = widget_helpers.create_label(None, text=f"\nASSUMPTIONS", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_cs = widget_helpers.create_label(None, text=f"SpawnPoll:  1.00\nSpawnMod:   0.00\nPlayers:    6\nFakesMode:  ignore_humans\n\nAll ZEDs are killed in the order they spawn", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            chart_difficulty = widget_helpers.create_chart(None, difficulty_data, '', axis_data=axis_data, chart_type='line')

        # Add everything in
        frame_layout.addWidget(label_zed_category)
        frame_layout.addWidget(table_zed_category)
        if self.params['Display Charts']:
            frame_layout.addWidget(chart_zed_category)
        frame_layout.addWidget(label_zed_type)
        frame_layout.addWidget(table_zed_type)
        if group_sum > 0:
            frame_layout.addWidget(label_zed_group)
            frame_layout.addWidget(table_zed_group)
            if self.params['Display Charts']:
                frame_layout.addWidget(chart_zed_group)
        else:
            label_zed_group = widget_helpers.create_label(None, text='\nZEDs by Group', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_nodata = widget_helpers.create_label(None, text='\nNo Group Data to Show!', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
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
        trash_zeds = ['Cyst', 'Alpha Clot', 'Slasher', 'Gorefast', 'Crawler', 'Stalker']
        albino_zeds = ['Rioter', 'Elite Crawler', 'Gorefiend', 'Alpha Scrake', 'Alpha Fleshpound']
        medium_zeds = ['Bloat', 'Husk', 'Siren', 'E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber']
        large_zeds = ['Quarter Pound', 'Fleshpound', 'Scrake']
        bosses = ['King Fleshpound', 'Abomination', 'Dr. Hans Volter', 'Patriarch', 'Matriarch', 'Abomination Spawn']

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
                if zed_type in trash_zeds:
                    bg_color = light_colors['Trash']
                    fg_color = dark_colors['Trash']
                elif zed_type in medium_zeds:
                    bg_color = light_colors['Medium']
                    fg_color = dark_colors['Medium']
                elif zed_type in large_zeds:
                    bg_color = light_colors['Large']
                    fg_color = dark_colors['Large']
                elif zed_type in albino_zeds:
                    bg_color = light_colors['Albino']
                    fg_color = dark_colors['Albino']
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

    # Publishes analysis data for the SpawnCycle
    def analyze_wavedefs(self):
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
        for i in range(len(self.wavedefs)):
            wave_sample, diff_sample = self.sample_wave(i)
            wave_stats.append(wave_sample)
            difficulty_data.append(diff_sample)

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
        title_label = widget_helpers.create_label(None, text=f"SPAWNCYCLE ANALYSIS " + (f":: {self.filename[:-4]}" if self.filename != 'Untitled' else ''), tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_label = widget_helpers.create_label(None, text=f"\n\nPARAMETERS", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
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

        self.scrollarea_contents_layout.addWidget(title_label)
        self.scrollarea_contents_layout.addWidget(params_label)
        self.scrollarea_contents_layout.addWidget(params_frame)

        # Display combined stats
        avg_difficulty_data = [(i, float(sum([y for _, y in difficulty_data[i]])) / float(len(difficulty_data[i]))) for i in range(0, len(difficulty_data))]
        axis_data = {'X': {'Title': '\nWave', 'Labels': [str(i) for i in range(1, len(difficulty_data)+1)], 'Min': 0, 'Max': len(self.wavedefs)}, 'Y': {'Title': 'Average Difficulty\n', 'Tick': 10, 'Min': 0, 'Max': 755000}}
        merged_label = widget_helpers.create_label(None, text=f"\n\nALL WAVES", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        merged_frame, merged_frame_children = self.create_waveframe(merged, merged=True, difficulty_data=avg_difficulty_data, axis_data=axis_data) # Create table
        self.scrollarea_contents_layout.addWidget(merged_label)
        self.scrollarea_contents_layout.addWidget(merged_frame)

        # Display stats per-wave
        if not self.params['Overview Only']:
            for i in range(len(wave_stats)):
                x_max = difficulty_data[i][-1][0]
                axis_data = {'X': {'Title': '\nWave Progress (%)', 'Labels': ['10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'], 'Min': 0, 'Max': x_max}, 'Y': {'Title': 'Difficulty\n', 'Tick': 10, 'Min': 0, 'Max': 755000}}
                wave_label = widget_helpers.create_label(None, text=f"\n\nWAVE {i+1}", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
                wave_frame, wave_frame_children = self.create_waveframe(wave_stats[i], merged=False, difficulty_data=difficulty_data[i], axis_data=axis_data) # Create table
                self.scrollarea_contents_layout.addWidget(wave_label)
                self.scrollarea_contents_layout.addWidget(wave_frame)
            
        # Reset scrollbar to top
        #self.scrollarea.verticalScrollBar().setValue(0);

        loading_diag.close()

        # Show a dialog indicating completion
        diag_title = 'SpawnCycler'
        x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 100 # Anchor dialog to center of window
        y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y() + 100
        diag_text = f"Analysis completed successfully!"
        diag = widget_helpers.create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
        diag.setWindowIcon(QtGui.QIcon('img/icon_check.png'))
        diag.exec_() # Show a dialog to tell user to check messages

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
                    zed_name = zed.replace(' (Enraged)', '')
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
        gamelength_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        gamelength_cbox = widget_helpers.create_combobox(None, options=['Short (4 Waves)', 'Medium (7 Waves)', 'Long (10 Waves)'], style=ss_cbox, size_policy=sp)
        gamelength_cbox.setToolTip(f"The Length of the game.\nDifferent Game Lengths affect the way the waves are sampled.")
        gamelength_frame = QtWidgets.QFrame()
        gamelength_cbox.setStyleSheet("QComboBox {color: rgb(175, 175, 175); background-color: rgb(60, 60, 60);} QToolTip {color: rgb(0, 0, 0)};")
        gamelength_frame_layout = QtWidgets.QHBoxLayout(gamelength_frame)
        gamelength_frame_layout.addWidget(gamelength_label)
        gamelength_frame_layout.addWidget(gamelength_cbox)
        gamelength_frame_layout.setAlignment(QtCore.Qt.AlignLeft)
        gamelength_cbox.setEnabled(False)

        if len(self.wavedefs) == 4:
            gamelength_cbox.setCurrentIndex(0)
            self.params.update({'GameLength': 0})
        elif len(self.wavedefs) == 7:
            gamelength_cbox.setCurrentIndex(1)
            self.params.update({'GameLength': 1})
        else:
            gamelength_cbox.setCurrentIndex(2)
            self.params.update({'GameLength': 2})

        # Set up Difficulty area
        difficulty_label = widget_helpers.create_label(None, text='Difficulty        ', tooltip="The Difficulty of the game to sample from.\nHarder difficulties make the waves larger.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        difficulty_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        difficulty_cbox = widget_helpers.create_combobox(None, options=['Normal', 'Hard', 'Suicidal', 'Hell on Earth'], style=ss_cbox, size_policy=sp)
        difficulty_cbox.setCurrentIndex(3) # HoE is default
        difficulty_cbox.setToolTip("The Difficulty of the game to sample from.\nHarder difficulties make the waves larger.")
        difficulty_cbox.setStyleSheet("QComboBox {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);} QToolTip {color: rgb(0, 0, 0)};")
        difficulty_cbox.activated.connect(self.update_difficulty)
        self.params.update({'Difficulty': 3})
        difficulty_frame = QtWidgets.QFrame()
        difficulty_frame_layout = QtWidgets.QHBoxLayout(difficulty_frame)
        difficulty_frame_layout.addWidget(difficulty_label)
        difficulty_frame_layout.addWidget(difficulty_cbox)
        difficulty_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Set up WSF area
        wavesize_label = widget_helpers.create_label(None, text='Wave Size Fakes   ', tooltip="The number of players to sample the waves from.\nHigher values make the waves larger.\nAssumes the 'Ignore Humans' FakesMode setting.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        wavesize_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(10)
        font.setWeight(75)
        wavesize_textarea = QtWidgets.QLineEdit()
        wavesize_textarea.setStyleSheet(ss)
        wavesize_textarea.setSizePolicy(sp)
        wavesize_textarea.setMaximumSize(QtCore.QSize(48, 28))
        wavesize_textarea.setFont(font)
        wavesize_textarea.setText('12')
        wavesize_textarea.setAlignment(QtCore.Qt.AlignCenter)
        wavesize_textarea.setToolTip("The number of players to sample the waves from.\nHigher values make the waves larger.\nAssumes the 'Ignore Humans' FakesMode setting.")
        wavesize_textarea.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLineEdit {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        wavesize_textarea.textChanged.connect(self.update_wavesize)
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
        iz_checkbox.toggled.connect(self.update_ignore_zeroes)
        iz_label = widget_helpers.create_label(None, text='Ignore Zeroes          ', tooltip="Don't display fields with zero value.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        iz_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
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
        analyze_difficulty_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
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
        display_charts_checkbox.toggled.connect(self.update_display_charts)
        display_charts_label = widget_helpers.create_label(None, text='Display Charts         ', tooltip="Show graphical charts related to Analysis data.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        display_charts_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
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
        overview_only_checkbox.toggled.connect(self.update_overview_only)
        overview_only_label = widget_helpers.create_label(None, text='Overview Only     ', tooltip="Exclude individual wave statistics from the Analysis Results.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        overview_only_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        self.params.update({'Overview Only': overview_only_checkbox.isChecked()})
        overview_only_frame = QtWidgets.QFrame()
        overview_only_frame_layout = QtWidgets.QHBoxLayout(overview_only_frame)
        overview_only_frame_layout.addWidget(overview_only_label)
        overview_only_frame_layout.addWidget(overview_only_checkbox)
        overview_only_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Set up MaxMonsters area
        maxmonsters_label = widget_helpers.create_label(None, text='MaxMonsters            ', tooltip="The maximum number of ZEDs that can be alive at once.\nHigher values make the waves more difficult.\nOnly used if the 'Analyze Difficulty' setting is TRUE.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        maxmonsters_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        maxmonsters_textarea = QtWidgets.QLineEdit()
        maxmonsters_textarea.setStyleSheet(ss)
        maxmonsters_textarea.setSizePolicy(sp)
        maxmonsters_textarea.setMaximumSize(QtCore.QSize(48, 28))
        maxmonsters_textarea.setFont(font)
        maxmonsters_textarea.setText('32')
        maxmonsters_textarea.setAlignment(QtCore.Qt.AlignCenter)
        maxmonsters_textarea.setToolTip("The maximum number of ZEDs that can be alive at once.\nHigher values make the waves more difficult.\nOnly used if the 'Analyze Difficulty' setting is TRUE.")
        maxmonsters_textarea.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLineEdit {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        maxmonsters_textarea.textChanged.connect(self.update_maxmonsters)
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

    # Called when the WaveSizeFakes field is changed
    def update_wavesize(self):
        # Force an int
        wsf_widget = self.analysis_widgets['WaveSizeFakes']
        if not wsf_widget.text().isnumeric(): # Only allow numbers in a certain range
            wsf_widget.setText('')
            return
        self.params.update({'WaveSizeFakes': int(wsf_widget.text())})

    # Called when the Ignore Zeroes field is changed
    def update_ignore_zeroes(self):
        self.params.update({'Ignore Zeroes': self.analysis_widgets['Ignore Zeroes'].isChecked()})

    # Called when the Overview Only field is changed
    def update_overview_only(self):
        self.params.update({'Overview Only': self.analysis_widgets['Overview Only'].isChecked()})

    # Called when the Display Charts field is changed
    def update_display_charts(self):
        self.params.update({'Display Charts': self.analysis_widgets['Display Charts'].isChecked()})

    # Called when the Analyze Difficulty field is changed
    def update_analyze_difficulty(self):
        self.params.update({'Analyze Difficulty': self.analysis_widgets['Analyze Difficulty'].isChecked()})

        mm_widget = self.analysis_widgets['MaxMonsters']
        if not self.analysis_widgets['Analyze Difficulty'].isChecked(): # Disable MaxMonsters
            mm_widget.setEnabled(False) # Gray out the textbox
            mm_widget.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLineEdit {color: rgb(0, 0, 0); background-color: rgb(50, 50, 50);};")
        else:
            mm_widget.setEnabled(True)
            mm_widget.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLineEdit {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")

    # Called when the Difficulty field is changed
    def update_difficulty(self):
        self.params.update({'Difficulty': self.analysis_widgets['Difficulty'].currentIndex()})

    # Called when the MaxMonsters field is changed
    def update_maxmonsters(self):
        # Force an int
        mm_widget = self.analysis_widgets['MaxMonsters']
        if not mm_widget.text().isnumeric(): # Only allow numbers in a certain range
            mm_widget.setText('')
            return
        self.params.update({'MaxMonsters': int(mm_widget.text())})

    # Called when this dialog is closed
    def teardown(self):
        self.save_preset(self.params)

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

        print(f"Loaded params: {self.params}")
        
    def setupUi(self, Dialog, wavedefs, filename, save_preset=None, last_preset=None):
        self.Dialog = Dialog
        self.buttons = {}
        self.filename = filename
        self.wavedefs = wavedefs # The wave data passed into the dialog
        self.save_preset = save_preset # Function called to save the parameters upon closing of the dialog
        self.params = {} # All of the current analysis params are stored here

        Dialog.setFixedSize(750, 1000)
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

        self.main_layout = QtWidgets.QVBoxLayout(Dialog)
        self.setup_scrollarea(Dialog) # Set up main window stuff
        self.setup_options_pane(Dialog) # Set up the options buttons at the bottom
        
        # Put everything in
        self.params_label = widget_helpers.create_label(None, text='\nAnalysis Parameters', tooltip=None, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)
        self.results_label = widget_helpers.create_label(None, text='Analysis Results', tooltip=None, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.results_label)
        self.main_layout.addWidget(self.scrollarea)
        self.main_layout.addWidget(self.params_label)
        self.main_layout.addWidget(self.options_pane)
        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)

        # Load the last used preset (if one is given)
        if last_preset is not None:
            self.load_preset(last_preset)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate

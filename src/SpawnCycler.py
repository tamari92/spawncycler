#
#  SpawnCycler.py
#
#  Author: Tamari
#  Date of creation: 11/14/2020
#
#  Main code base for SpawnCycler
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
from datetime import datetime, date
from functools import partial
from copy import deepcopy
from convert import ConvertDialog
from about import AboutDialog
from analyze import AnalyzeDialog
from generate import GenerateDialog
from settings import SettingsDialog
import sys
import meta
import json
import parse
import random
import widget_helpers

#import threading
#import cgitb 
#cgitb.enable(format = 'text')


_DEF_FONT_FAMILY = 'Consolas'
_RECENT_MAX = 8 # Max "Recent Files"
_WAVE_MAX = 10  # Max number of waves
_SQUAD_MAX = 10  # Max ZEDs in a squad
_ZED_MIN = 0 # Min ZEDs in a single definition
_ZED_MAX = 10 # Max ZEDs in a single definition
_FIX_TEXTFIELDS_INTERVAL = 10
has_swapped_modes = False # Has the user swapped ZED modes yet?
_WINDOWSIZE_MAIN_W = 1000 # Width of the main window
_WINDOWSIZE_MAIN_H = 1050 # Height of the main window


# IDs for all the zeds
zed_ids = {'Cyst': 'CY',
           'Alpha Clot': 'AL',
           'Slasher': 'SL',
           'Rioter': 'AL*',
           'Gorefast': 'GF',
           'Gorefiend': 'GF*',
           'Crawler': 'CR',
           'Elite Crawler': 'CR*',
           'Stalker': 'ST',
           'Bloat': 'BL',
           'Husk': 'HU',
           'Siren': 'SI',
           'E.D.A.R Trapper': 'DE',
           'E.D.A.R Blaster': 'DL',
           'E.D.A.R Bomber': 'DR',
           'Quarter Pound': 'MF',
           'Quarter Pound (Enraged)': 'MF!',
           'Fleshpound': 'FP',
           'Fleshpound (Enraged)': 'FP!',
           'Scrake': 'SC',
           'Alpha Scrake': 'SC*',
           'Alpha Fleshpound': 'FP*',
           'Alpha Fleshpound (Enraged)': 'FP*!',
           'Abomination Spawn': 'AS',
           'King Fleshpound': 'KF',
           'Dr. Hans Volter': 'HV',
           'Patriarch': 'PT',
           'Abomination': 'AB',
           'Matriarch': 'MT',
           'Slasher Omega': 'OSL',
           'Gorefast Omega': 'OGF',
           'Stalker Omega': 'OST',
           'Tiny Crawler': 'CRM',
           'Medium Crawler': 'MCR',
           'Big Crawler': 'BCR',
           'Huge Crawler': 'HCR',
           'Ultra Crawler': 'UCR',
           'Siren Omega': 'OS',
           'Husk Omega': 'OHS',
           'Tiny Husk': 'MHS',
           'Scrake Omega': 'OSC',
           'Scrake Emperor': 'ESC',
           'Tiny Scrake': 'TSC',
           'Fleshpound Omega': 'OFP'}

custom_zeds = ['E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber', 'Alpha Scrake', 'Alpha Fleshpound',
               'Alpha Fleshpound (Enraged)', 'Dr. Hans Volter', 'Patriarch', 'Abomination', 'Matriarch']
omega_zeds = ['Slasher Omega', 'Gorefast Omega', 'Stalker Omega', 'Tiny Crawler', 'Medium Crawler',
                  'Big Crawler', 'Huge Crawler', 'Ultra Crawler', 'Siren Omega', 'Husk Omega', 'Tiny Husk',
                  'Tiny Scrake', 'Scrake Omega', 'Scrake Emperor', 'Fleshpound Omega', 'Stalker Omega']


class Ui_MainWindow(object):
    def __init__(self, app):
        # Meta vars
        self.dirty = False # Whether or not the file needs saving before closing
        self.filename = 'Untitled'
        self.MainWindow = MainWindow
        self.buttons = {}
        self.zed_pane_buttons = {}
        self.wavedefs = []
        self.labels = {}
        self.message_labels = []
        self.app = app
        self.zed_mode = 'Omega'
        self.active_dialog = None
        self.analyze_dialog = None
        self.generate_dialog = None
        self.loaded_json = None
        self.json_autosave_target = None # The place the autosave goes to for JSON files
        self.last_generate_preset = None # Last preset used in the Generate dialog
        self.last_generate_mode = None # Last used zed mode in the Generate dialog
        self.last_analyze_preset = None # Last preset used in the Analyze dialog

        # Start checking if we can autosave
        self.autosave_timer = QtCore.QTimer()
        self.autosave_timer.timeout.connect(partial(self.save_to_file, False, True))
        self.autosave_timer.start(meta.get_keyvalue('autosave_interval') * 1000.0) # Convert to ms

        # Hack: Start fixing bad textfields
        self.textfield_timer = QtCore.QTimer()
        self.textfield_timer.timeout.connect(partial(self.update_zed_textfields))
        self.textfield_timer.start(_FIX_TEXTFIELDS_INTERVAL)

    def update_zed_textfields(self):
        for wavedef in self.wavedefs:
            for squad in wavedef['Squads']:
                for zed_data in squad['ZEDs'].values():
                    if (len(zed_data['Children']['Label'].text()) > 0) and (not zed_data['Children']['Label'].text().isnumeric()):
                        zed_data['Children']['Label'].setText(str(zed_data['Count']))

    # Switches from Default to Custom zed set
    def switch_zed_mode(self, should_warn=True):
        if self.zed_mode == 'Custom':
            # Hide custom ZEDs
            self.zed_pane_buttons['E.D.A.R Trapper'].setVisible(False)
            self.zed_pane_buttons['E.D.A.R Blaster'].setVisible(False)
            self.zed_pane_buttons['E.D.A.R Bomber'].setVisible(False)
            self.zed_pane_buttons['Alpha Scrake'].setVisible(False)
            self.zed_pane_buttons['Alpha Fleshpound'].setVisible(False)
            self.zed_pane_buttons['Alpha Fleshpound (Enraged)'].setVisible(False)
            self.zed_pane_buttons['Alpha Scrake'].setVisible(False)
            self.zed_pane_buttons['Dr. Hans Volter'].setVisible(False)
            self.zed_pane_buttons['Patriarch'].setVisible(False)
            self.zed_pane_buttons['Abomination'].setVisible(False)
            self.zed_pane_buttons['Matriarch'].setVisible(False)
            self.zed_pane_buttons['Abomination Spawn'].setVisible(False)

            # Hide default ZEDs
            self.zed_pane_buttons['Cyst'].setVisible(False)
            self.zed_pane_buttons['Slasher'].setVisible(False)
            self.zed_pane_buttons['Alpha Clot'].setVisible(False)
            self.zed_pane_buttons['Rioter'].setVisible(False)
            self.zed_pane_buttons['Gorefast'].setVisible(False)
            self.zed_pane_buttons['Gorefiend'].setVisible(False)
            self.zed_pane_buttons['Crawler'].setVisible(False)
            self.zed_pane_buttons['Elite Crawler'].setVisible(False)
            self.zed_pane_buttons['Stalker'].setVisible(False)
            self.zed_pane_buttons['Bloat'].setVisible(False)
            self.zed_pane_buttons['Husk'].setVisible(False)
            self.zed_pane_buttons['Siren'].setVisible(False)
            self.zed_pane_buttons['Quarter Pound'].setVisible(False)
            self.zed_pane_buttons['Quarter Pound (Enraged)'].setVisible(False)
            self.zed_pane_buttons['Fleshpound'].setVisible(False)
            self.zed_pane_buttons['Fleshpound (Enraged)'].setVisible(False)
            self.zed_pane_buttons['Scrake'].setVisible(False)
            self.zed_pane_buttons['King Fleshpound'].setVisible(False)

            # Show Omega ZEDs
            self.zed_pane_buttons['Slasher Omega'].setVisible(True)
            self.zed_pane_buttons['Gorefast Omega'].setVisible(True)
            self.zed_pane_buttons['Stalker Omega'].setVisible(True)
            self.zed_pane_buttons['Tiny Crawler'].setVisible(True)
            self.zed_pane_buttons['Medium Crawler'].setVisible(True)
            self.zed_pane_buttons['Big Crawler'].setVisible(True)
            self.zed_pane_buttons['Huge Crawler'].setVisible(True)
            self.zed_pane_buttons['Ultra Crawler'].setVisible(True)
            self.zed_pane_buttons['Siren Omega'].setVisible(True)
            self.zed_pane_buttons['Husk Omega'].setVisible(True)
            self.zed_pane_buttons['Tiny Husk'].setVisible(True)
            self.zed_pane_buttons['Scrake Omega'].setVisible(True)
            self.zed_pane_buttons['Scrake Emperor'].setVisible(True)
            self.zed_pane_buttons['Tiny Scrake'].setVisible(True)
            self.zed_pane_buttons['Fleshpound Omega'].setVisible(True)

            # Hide/show labels
            self.labels['Trash ZEDs'].setVisible(False)
            self.labels['Medium ZEDs'].setVisible(False)
            self.labels['Large ZEDs'].setVisible(False)
            self.labels['Bosses'].setVisible(False)
            self.labels['Omega Trash'].setVisible(True)
            self.labels['Omega Medium'].setVisible(True)
            self.labels['Omega Large'].setVisible(True)

            for button in self.zed_pane_buttons.values():
                button.setIconSize(QtCore.QSize(48, 48));

            # Update button
            self.buttons['Switch ZEDs'].setText(' Omega')
            self.zed_mode = 'Omega'
            #self.refresh_wavedefs()

        elif self.zed_mode == 'Omega':
            # Hide custom ZEDs
            self.zed_pane_buttons['E.D.A.R Trapper'].setVisible(False)
            self.zed_pane_buttons['E.D.A.R Blaster'].setVisible(False)
            self.zed_pane_buttons['E.D.A.R Bomber'].setVisible(False)
            self.zed_pane_buttons['Alpha Scrake'].setVisible(False)
            self.zed_pane_buttons['Alpha Fleshpound'].setVisible(False)
            self.zed_pane_buttons['Alpha Fleshpound (Enraged)'].setVisible(False)
            self.zed_pane_buttons['Alpha Scrake'].setVisible(False)
            self.zed_pane_buttons['Dr. Hans Volter'].setVisible(False)
            self.zed_pane_buttons['Patriarch'].setVisible(False)
            self.zed_pane_buttons['Abomination'].setVisible(False)
            self.zed_pane_buttons['Matriarch'].setVisible(False)
            self.zed_pane_buttons['Abomination Spawn'].setVisible(False)

            # Hide Omega ZEDs
            self.zed_pane_buttons['Slasher Omega'].setVisible(False)
            self.zed_pane_buttons['Gorefast Omega'].setVisible(False)
            self.zed_pane_buttons['Stalker Omega'].setVisible(False)
            self.zed_pane_buttons['Tiny Crawler'].setVisible(False)
            self.zed_pane_buttons['Medium Crawler'].setVisible(False)
            self.zed_pane_buttons['Big Crawler'].setVisible(False)
            self.zed_pane_buttons['Huge Crawler'].setVisible(False)
            self.zed_pane_buttons['Ultra Crawler'].setVisible(False)
            self.zed_pane_buttons['Siren Omega'].setVisible(False)
            self.zed_pane_buttons['Husk Omega'].setVisible(False)
            self.zed_pane_buttons['Tiny Husk'].setVisible(False)
            self.zed_pane_buttons['Scrake Omega'].setVisible(False)
            self.zed_pane_buttons['Scrake Emperor'].setVisible(False)
            self.zed_pane_buttons['Tiny Scrake'].setVisible(False)
            self.zed_pane_buttons['Fleshpound Omega'].setVisible(False)

            # Show default ZEDs
            self.zed_pane_buttons['Cyst'].setVisible(True)
            self.zed_pane_buttons['Slasher'].setVisible(True)
            self.zed_pane_buttons['Alpha Clot'].setVisible(True)
            self.zed_pane_buttons['Rioter'].setVisible(True)
            self.zed_pane_buttons['Gorefast'].setVisible(True)
            self.zed_pane_buttons['Gorefiend'].setVisible(True)
            self.zed_pane_buttons['Crawler'].setVisible(True)
            self.zed_pane_buttons['Elite Crawler'].setVisible(True)
            self.zed_pane_buttons['Stalker'].setVisible(True)
            self.zed_pane_buttons['Bloat'].setVisible(True)
            self.zed_pane_buttons['Husk'].setVisible(True)
            self.zed_pane_buttons['Siren'].setVisible(True)
            self.zed_pane_buttons['Quarter Pound'].setVisible(True)
            self.zed_pane_buttons['Quarter Pound (Enraged)'].setVisible(True)
            self.zed_pane_buttons['Fleshpound'].setVisible(True)
            self.zed_pane_buttons['Fleshpound (Enraged)'].setVisible(True)
            self.zed_pane_buttons['Scrake'].setVisible(True)
            self.zed_pane_buttons['King Fleshpound'].setVisible(True)
            self.zed_pane_buttons['Abomination Spawn'].setVisible(True)

            # Hide/show labels
            self.labels['Omega Trash'].setVisible(False)
            self.labels['Omega Medium'].setVisible(False)
            self.labels['Omega Large'].setVisible(False)
            self.labels['Trash ZEDs'].setVisible(True)
            self.labels['Medium ZEDs'].setVisible(True)
            self.labels['Large ZEDs'].setVisible(True)
            self.labels['Bosses'].setVisible(True)

            for button in self.zed_pane_buttons.values():
                button.setIconSize(QtCore.QSize(48, 48));

            # Update button
            self.buttons['Switch ZEDs'].setText(' Default')
            self.zed_mode = 'Default'
            #self.refresh_wavedefs()

        else: # Default zeds
            global has_swapped_modes
            if should_warn:
                if not has_swapped_modes and meta.get_keyvalue('should_warn_zedset'):
                    diag_title = 'WARNING'
                    diag_text = '\nThe Custom and Omega ZED sets are NOT supported by most Controlled Difficulty builds.\nUsing these ZEDs may break your SpawnCycle on those builds.\n\nUse at your own risk!\n'
                    x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-200 # Anchor dialog to center of window
                    y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
                    diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True, checkbox=True)
                    diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))

                    diag.exec_() # Show the dialog

                    # Check if the user clicked "Don't show this again"
                    if diag.checkbox.checkState(): # We know this will exist since checkbox=True
                        meta.set_keyvalue('should_warn_zedset', False) # Don't ever show the dialog again

                    has_swapped_modes = True # Never show this message again

            # Need to add all the custom zeds to the grid
            self.zed_pane_buttons['E.D.A.R Trapper'].setVisible(True)
            self.zed_pane_buttons['E.D.A.R Blaster'].setVisible(True)
            self.zed_pane_buttons['E.D.A.R Bomber'].setVisible(True)
            self.zed_pane_buttons['Alpha Scrake'].setVisible(True)
            self.zed_pane_buttons['Alpha Fleshpound'].setVisible(True)
            self.zed_pane_buttons['Alpha Fleshpound (Enraged)'].setVisible(True)
            self.zed_pane_buttons['Alpha Scrake'].setVisible(True)
            self.zed_pane_buttons['Dr. Hans Volter'].setVisible(True)
            self.zed_pane_buttons['Patriarch'].setVisible(True)
            self.zed_pane_buttons['Abomination'].setVisible(True)
            self.zed_pane_buttons['Matriarch'].setVisible(True)

            for button in self.zed_pane_buttons.values():
                button.setIconSize(QtCore.QSize(34, 34));

            # Update button
            self.buttons['Switch ZEDs'].setText(' Custom')            
            self.zed_mode = 'Custom'
            #self.refresh_wavedefs()

    # Removes the ZED from the given squad
    def remove_zed_from_squad(self, wave_id, squad_id, zed_id, count=1, replacement=False):
        this_squad = self.wavedefs[wave_id]['Squads'][squad_id]
        squad_layout = this_squad['Layout'] # Get the layout corresponding to this wave's squad box

        if zed_id not in this_squad['ZEDs']:
            return

        # Update the internal array and numerical display
        if count != 'all' and this_squad['ZEDs'][zed_id]['Count'] > 1:
            num_to_remove = count
            this_squad['ZEDs'][zed_id]['Count'] -= 1
            this_squad['ZEDs'][zed_id]['Children']['Label'].setText(str(this_squad['ZEDs'][zed_id]['Count']))
        else: # Last ZED of its type in the squad. Teardown the zed frame
            num_to_remove = this_squad['ZEDs'][zed_id]['Count']
            this_squad['ZEDs'][zed_id]['Children']['Label'].setParent(None)
            this_squad['ZEDs'][zed_id]['Children']['Button'].setParent(None)
            this_squad['ZEDs'][zed_id]['Frame'].setParent(None) # Disassociate the widgets 
            del this_squad['ZEDs'][zed_id]

        # Is this the last ZED in the Squad?
        total_zeds = sum([z['Count'] for z in this_squad['ZEDs'].values()])
        if total_zeds > 0:
            if total_zeds < _SQUAD_MAX:
                this_squad['Frame'].is_full = False
                this_squad['Frame'].setToolTip('')
                widget_helpers.set_plain_border(this_squad['Frame'], QtGui.QColor(255, 255, 255), 2)
        else: # Last ZED in Squad. We need to remove the entire Squad Frame
            this_squad['Layout'].setParent(None)
            this_squad['Frame'].setParent(None)
            self.wavedefs[wave_id]['Squads'].pop(squad_id)

        # Update the zed count
        old_count = int(self.wavedefs[wave_id]['Labels']['ZEDCount'].text().split()[2])
        self.wavedefs[wave_id]['Labels']['ZEDCount'].setText(f"Total ZEDs: {old_count - num_to_remove:,d}")

        self.refresh_wavedefs(squads=True, wave_id=wave_id) # Need to refresh everything
        
        # The file is now 'dirty'
        self.dirty = True
        if self.filename != 'Untitled': # Change filename to reflect
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)') # Only if file is named though

    # Called when a zed's textfield is typed into
    def edit_textbox(self, textbox, wave_id, squad_id, zed_id):
        if not textbox.text().isnumeric(): # NaN somehow (for example the field is empty)
            return

        # Remove any leading zeroes
        val = int(textbox.text()) # Conv to an int will remove the zeroes on its own. Guaranteed to be numeric at this point
        if val == 0:
            if textbox.text().count('0') > 1: # Special case for zero, just replace it. Stripping won't work here
                textbox.setText('0')
        else:
            textbox.setText(textbox.text().lstrip('0'))

    # Called when the user hits ENTER or clicks out of the zed's textfield
    def commit_textbox(self, textfield, wave_id, squad_id, zed_id):
        # Hack to get around Qt bug where this function gets called twice
        # Btw its really dumb this has to be done
        if textfield.text() != '':
            textfield.blockSignals(True)
        this_squad = self.wavedefs[wave_id]['Squads'][squad_id] # Easier to reference later

        # Set the real value of the zed in the squad
        if not textfield.text().isnumeric(): # NaN somehow (for example the field is empty)
            textfield.setText(str(this_squad['ZEDs'][zed_id]['Count'])) # Just put the old number back
            return
        
        val = int(textfield.text()) # Guaranteed to be numeric at this point

        # Constrain range
        # Figure out what the max will be (depends on how many zeds are in the squad)
        squad_count = sum([y['Count'] for (x, y) in this_squad['ZEDs'].items() if x != zed_id]) # Get total of all zeds in this squad (minus this zed)
        this_count = this_squad['ZEDs'][zed_id]['Count']
        max_count = _ZED_MAX - squad_count # The maximum this zed can be set to to not go over the 10 limit

        # Set the value of the textfield
        if val < _ZED_MIN: # Default min zeds is 0
            textfield.setText(str(_ZED_MIN))
            val = _ZED_MIN
        elif val > max_count: # Default max zeds is 10
            textfield.setText(str(max_count))
            val = max_count

        if val == _ZED_MIN: # Special case for zero
            # Clear out the squad
            for i in range(this_count):
                self.remove_zed_from_squad(wave_id, squad_id, zed_id, count=1)
        elif val < this_squad['ZEDs'][zed_id]['Count']: # Subtracting zeds
            difference = this_squad['ZEDs'][zed_id]['Count'] - val
            for i in range(difference):
                self.remove_zed_from_squad(wave_id, squad_id, zed_id, count=1)
        elif val > this_squad['ZEDs'][zed_id]['Count']: # Adding zeds
            difference = val - this_squad['ZEDs'][zed_id]['Count']
            for i in range(difference):
                self.add_zed_to_squad(wave_id, squad_id, zed_id, count=1, raged=this_squad['ZEDs'][zed_id]['Raged'])

        # Hack to get around Qt bug where this function gets called twice
        # Btw its really dumb this has to be done
        if textfield.text() != '':
            textfield.blockSignals(False)
            
    # Creates a new frame for a ZED in a squad (holding the icon and number)
    def create_zed_frame(self, parent, zed_button, wave_id, squad_id, zed_id):
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(12)
        font_label.setWeight(75)
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        ss_button = 'QToolTip {color: rgb(0, 0, 0)};\nQPushButton{background-color: rgb(40, 40, 40)};' # Stylesheet
        ss_label = 'color: rgb(255, 255, 255);' # Stylesheet

        # Create the frame
        zed_frame = QtWidgets.QFrame(parent)
        zed_frame.setSizePolicy(sp)
        zed_frame.setMinimumSize(QtCore.QSize(1, 1))
        zed_frame_layout = QtWidgets.QVBoxLayout(zed_frame) # Add layout
        zed_frame.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

        # Create label
        #zed_label = widget_helpers.create_label(zed_frame, text='1', style=ss_label, font=font_label)
        #zed_label.setAlignment(QtCore.Qt.AlignCenter)

        # Create zed count text field
        zed_textfield = widget_helpers.create_textfield('1', font_label, sp, ss_label, 28, 28)

        # Set up signals
        zed_textfield.editingFinished.connect(partial(self.commit_textbox, zed_textfield, wave_id, squad_id, zed_id))
        zed_textfield.textChanged.connect(partial(self.edit_textbox, zed_textfield, wave_id, squad_id, zed_id))

        # Create button frame
        zed_icon_frame = QtWidgets.QFrame()
        zed_icon_frame_layout = QtWidgets.QHBoxLayout(zed_icon_frame)
        zed_icon_frame_layout.addWidget(zed_button)
        zed_icon_frame_layout.setAlignment(QtCore.Qt.AlignCenter)
        zed_icon_frame_layout.setContentsMargins(0, 0, 0, 0)

        # Create up and down arrows
        icon_w = 8
        icon_h = 8
        button_frame = QtWidgets.QFrame()
        button_frame.setSizePolicy(sp)
        button_layout = QtWidgets.QHBoxLayout(button_frame)
        add_button = widget_helpers.create_button(None, None, None, style=ss_button, icon_path='img/icon_plus.png', size_policy=sp, icon_w=icon_w, icon_h=icon_h, squad=False, draggable=False)
        sub_button = widget_helpers.create_button(None, None, None, style=ss_button, icon_path='img/icon_minus.png', size_policy=sp, icon_w=icon_w, icon_h=icon_h, squad=False, draggable=False)

        # Hook up the buttons
        raged = True if '(Enraged)' in zed_id else False
        add_button.clicked.connect(partial(self.add_zed_to_squad, wave_id, squad_id, zed_id, 1, raged, False))
        sub_button.clicked.connect(partial(self.remove_zed_from_squad, wave_id, squad_id, zed_id, 1))

        # Add the stuff to the button layout
        button_layout.addWidget(sub_button)
        #button_layout.addWidget(zed_label)
        button_layout.addWidget(zed_textfield)
        button_layout.addWidget(add_button)
        button_layout.setAlignment(QtCore.Qt.AlignCenter)
        button_layout.setSpacing(1)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Put it all together
        zed_frame_layout.addWidget(zed_icon_frame)
        zed_frame_layout.addWidget(button_frame)
        zed_frame_layout.setSpacing(0)
        zed_frame_layout.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignTop)

        return zed_frame, {'Button': zed_button, 'Label': zed_textfield, 'AddButton': add_button, 'SubtractButton': sub_button}

    # Adds a squad to the specified wave
    def add_squad(self, wave_id, zed_id, count=1, raged=False):
        wave_layout = self.wavedefs[wave_id]['Layouts']['SquadFrame'] # Get the layout corresponding to this wave's squad box

        # Create new button for this ZED
        ss_button = 'QToolTip {color: rgb(0, 0, 0);\nbackground-color: rgb(40, 40, 40);}' # Stylesheet
        icon_w = 40
        icon_h = 40
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)

        ids = [wave_id, len(self.wavedefs[wave_id]['Squads']), zed_id]
        zed_button = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, ids, tooltip=zed_id, style=ss_button, icon_path=widget_helpers.get_icon_path(zed_id), icon_w=icon_w, icon_h=icon_h, size_policy=sp, squad=True, draggable=True)
        zed_button.replace_zeds = self.replace_zeds
        zed_button.remove_zed_from_squad = self.remove_zed_from_squad
        zed_button.zed_mode = self.zed_mode

        # Create a new frame for the squad
        squad_id = len(self.wavedefs[wave_id]['Squads'])
        squad_frame = widget_helpers.QFrame_Drag(self.wavedefs[wave_id]['Frames']['SquadFrame'], id=squad_id, squad=True)
        squad_frame.raise_() # Raise to top-layer
        squad_frame.wave_id = wave_id
        squad_frame.add_zed_to_squad = self.add_zed_to_squad
        squad_frame.remove_zed_from_squad = self.remove_zed_from_squad
        squad_frame.setSizePolicy(sp)
        squad_frame.setAcceptDrops(True)
        squad_frame.setStyleSheet('color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 255);')
        squad_frame.setFrameShape(QtWidgets.QFrame.Box)
        squad_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        squad_frame.setLineWidth(2)
        squad_frame.setSizePolicy(sp)
        squad_frame_layout = QtWidgets.QHBoxLayout(squad_frame) # Add layout
        zed_button.squad_uid = squad_frame.unique_id
        
        # Override for manually dragging ZED to the squad
        if '(Enraged)' in zed_id:
            raged = True

        # Create a frame for the ZED and its count
        zed_frame, zed_frame_children = self.create_zed_frame(squad_frame, zed_button, wave_id, squad_id, zed_id)
        
        # Set colors
        if raged:
            zed_frame_children['Label'].setStyleSheet("QLineEdit {color: rgb(255, 55, 55); background-color: rgb(50, 50, 50); border: 2px solid red;}")
            zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid red;}")
        elif zed_id in omega_zeds:
            zed_frame_children['Label'].setStyleSheet("QLineEdit {color: rgb(173, 98, 252); background-color: rgb(50, 50, 50); border: 2px solid purple;}")
            zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid purple;}")
        else:
            zed_frame_children['Label'].setStyleSheet("QLineEdit {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50); border: 2px solid white;}")
            zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid white;}")
            
        # Set label
        zed_frame_children['Label'].setText(str(count))

        # Add the widgets
        squad_frame_layout.addWidget(zed_frame)
        wave_layout.addWidget(squad_frame)

        vbar = self.wavedefs_scrollarea.verticalScrollBar()
        try: # Hacky: try to disconnect any functions on the vertical bar. If none, just ignore and do nothing
            vbar.rangeChanged.disconnect()
        except:
            pass

        # Set the horizontal scrollbar to the right
        hbar = self.wavedefs_scrollarea.horizontalScrollBar()
        hbar.rangeChanged.connect(lambda: hbar.setValue(hbar.maximum()))

        #self.refresh_wavedefs() # Need to refresh

        # Squad is full
        if count == _SQUAD_MAX:
            squad_frame.is_full = True # Mark as full
            squad_frame.setToolTip('This squad has reached capacity.')
            widget_helpers.set_plain_border(squad_frame, QtGui.QColor(245, 42, 20), 2)
            squad_frame.setStyleSheet('QToolTip {color: rgb(0, 0, 0)}\nQFrame_Drag {color: rgb(255, 0, 0); background-color: rgba(150, 0, 0, 30);}')

        # Update the internal array
        self.wavedefs[wave_id]['Squads'].append({'Frame': squad_frame, 'Layout': squad_frame_layout, 'ZEDs': {zed_id: {'Count': count, 'Raged': raged, 'Frame': zed_frame, 'Children': zed_frame_children}}})

        # Update the zed count
        old_count = int(self.wavedefs[wave_id]['Labels']['ZEDCount'].text().split()[2])
        self.wavedefs[wave_id]['Labels']['ZEDCount'].setText(f"Total ZEDs: {old_count + count:,d}")

        # The file is now 'dirty'
        self.dirty = True
        if self.filename != 'Untitled': # Change filename to reflect
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)') # Only if file is named though

    # Adds a new ZED to the given squad
    def add_zed_to_squad(self, wave_id, squad_id, zed_id, count=1, raged=False, ignore_capacity=False):
        this_squad = self.wavedefs[wave_id]['Squads'][squad_id]
        squad_layout = this_squad['Layout'] # Get the layout corresponding to this wave's squad box

        # Squad is full, disallow.
        if not ignore_capacity and this_squad['Frame'].is_full:
            self.add_message(f'Error: This squad has reached its maximum capacity of {_SQUAD_MAX} ZEDs!\nRemove some and try again.')
            return

        # Create new button for this ZED
        ss_button = 'QToolTip {color: rgb(0, 0, 0);\nbackground-color: rgb(40, 40, 40);}' # Stylesheet
        icon_w = 40
        icon_h = 40
        sp_button = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_button.setHorizontalStretch(0)
        sp_button.setVerticalStretch(0)
        ids = [wave_id, squad_id, zed_id]
        zed_button = widget_helpers.create_button(self.wavedefs[wave_id]['Frames']['SquadFrame'], self.app, ids, tooltip=zed_id, style=ss_button, icon_path=widget_helpers.get_icon_path(zed_id), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, squad=True, draggable=True)
        zed_button.replace_zeds = self.replace_zeds
        zed_button.remove_zed_from_squad = self.remove_zed_from_squad
        zed_button.zed_mode = self.zed_mode

        # Add the ZED
        sp_fixed = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_fixed.setHorizontalStretch(0)
        sp_fixed.setVerticalStretch(0)

        # Override for manually dragging ZED to the squad
        if '(Enraged)' in zed_id:
            raged = True

        # Update the internal array and numerical display
        if zed_id in this_squad['ZEDs']:
            this_squad['ZEDs'][zed_id]['Count'] += count
            this_squad['ZEDs'][zed_id]['Children']['Label'].setText(str(this_squad['ZEDs'][zed_id]['Count']))
        else: # Zed isn't in the squad yet
            zed_frame, zed_frame_children = self.create_zed_frame(this_squad['Frame'], zed_button, wave_id, squad_id, zed_id)

            # Set colors
            if raged:
                zed_frame_children['Label'].setStyleSheet("QLineEdit {color: rgb(255, 55, 55); background-color: rgb(50, 50, 50); border: 2px solid red;}")
                zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid red;}")
            elif zed_id in omega_zeds:
                zed_frame_children['Label'].setStyleSheet("QLineEdit {color: rgb(173, 98, 252); background-color: rgb(50, 50, 50); border: 2px solid purple;}")
                zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid purple;}")
            else:
                zed_frame_children['Label'].setStyleSheet("QLineEdit {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50); border: 2px solid white;}")
                zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid white;}")

            # Set Label
            zed_frame_children['Label'].setText(str(count))

            this_squad['ZEDs'][zed_id] = {'Count': count, 'Raged': raged, 'Frame': zed_frame, 'Children': zed_frame_children}
            squad_layout.addWidget(zed_frame)

        zed_button.squad_uid = this_squad['Frame'].unique_id

        # Has this squad reached capacity?
        total_zeds = sum([x['Count'] for x in this_squad['ZEDs'].values()])
        if total_zeds >= _SQUAD_MAX:
            this_squad['Frame'].is_full = True # Mark as full
            this_squad['Frame'].setToolTip('This squad has reached capacity.')
            widget_helpers.set_plain_border(this_squad['Frame'], QtGui.QColor(245, 42, 20), 2)
            this_squad['Frame'].setStyleSheet('QToolTip {color: rgb(0, 0, 0)}\nQFrame_Drag {color: rgb(255, 0, 0); background-color: rgba(150, 0, 0, 30);}')

        # Update the zed count
        old_count = int(self.wavedefs[wave_id]['Labels']['ZEDCount'].text().split()[2])
        self.wavedefs[wave_id]['Labels']['ZEDCount'].setText(f"Total ZEDs: {old_count + count:,d}")

        vbar = self.wavedefs_scrollarea.verticalScrollBar()
        hbar = self.wavedefs_scrollarea.horizontalScrollBar()
        try: # Hacky: try to disconnect any functions on the vertical bar. If none, just ignore and do nothing
            vbar.rangeChanged.disconnect()
        except:
            pass
        try: # Hacky: try to disconnect any functions on the horizontal bar. If none, just ignore and do nothing
            hbar.rangeChanged.disconnect()
        except:
            pass

        #self.refresh_wavedefs() # Need to refresh

        # The file is now 'dirty'
        self.dirty = True
        if self.filename != 'Untitled': # Change filename to reflect
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)') # Only if file is named though

    # Refreshes all wavedefs by correcting their numbering and functions
    def refresh_wavedefs(self, squads=True, wave_id=None, squad_id=None):
        wave_range = range(len(self.wavedefs)) if wave_id is None else range(wave_id, wave_id+1)
        for i in wave_range:
            thisdef = self.wavedefs[i]

            # Shift indices
            thisdef['ID'] = i
            thisdef['Frames']['WaveFrame'].id = i
            thisdef['Frames']['SquadFrame'].id = i
            thisdef['Labels']['WaveNumber'].setText(thisdef['Labels']['WaveNumber'].text().split()[0] + f" {thisdef['Frames']['WaveFrame'].id+1}")

            # Shift option button targets to match the new wave
            shiftup_button = thisdef['OptionsButtons']['Shift Up']
            shiftdn_button = thisdef['OptionsButtons']['Shift Down']
            clear_button = thisdef['OptionsButtons']['Clear']
            delete_button = thisdef['OptionsButtons']['Delete']
            widget_helpers.button_changetarget(shiftup_button, partial(self.shift_wavedef, thisdef['Frames']['WaveFrame'], 'up'))
            widget_helpers.button_changetarget(shiftdn_button, partial(self.shift_wavedef, thisdef['Frames']['WaveFrame'], 'down'))
            widget_helpers.button_changetarget(clear_button, partial(self.clear_wavedef, i, True))
            widget_helpers.button_changetarget(delete_button, partial(self.remove_wavedef, i, True))

            # Refresh squads
            if squads and len(thisdef['Squads']) > 0:
                # Shift +/- buttons to match the new wave
                for j in range(len(thisdef['Squads'])):
                    squad = thisdef['Squads'][j]
                    for (zed_id, zed_info) in squad['ZEDs'].items():
                        raged = '(Enraged)' in zed_id
                        widget_helpers.button_changetarget(zed_info['Children']['AddButton'], partial(self.add_zed_to_squad, i, j, zed_id, 1, raged, False))
                        widget_helpers.button_changetarget(zed_info['Children']['SubtractButton'], partial(self.remove_zed_from_squad, i, j, zed_id, 1))

                # Refresh squad wave ids
                for j in range(len(thisdef['Squads'])):
                    squad = thisdef['Squads'][j]
                    squad['Frame'].wave_id = i
                    for (zname, zdata) in squad['ZEDs'].items():
                        zdata['Children']['Button'].wave_id = i
                        # Retarget the signals
                        zdata['Children']['Label'].editingFinished.disconnect()
                        zdata['Children']['Label'].textChanged.disconnect()
                        zdata['Children']['Label'].editingFinished.connect(partial(self.commit_textbox, zdata['Children']['Label'], i, j, zname))
                        zdata['Children']['Label'].textChanged.connect(partial(self.edit_textbox, zdata['Children']['Label'], i, j, zname))

                # Refresh squad ids
                for j in range(len(thisdef['Squads'])):
                    squad = thisdef['Squads'][j]
                    squad['Frame'].id = j
                    for z in squad['ZEDs'].values():
                        z['Children']['Button'].squad_id = j
                        z['Children']['Button'].zed_mode = self.zed_mode

            # Disable Shift buttons if at the ends of the array
            # Kinda hacky but it'll work
            if i == 0:
                shiftup_button.setEnabled(False)
                shiftup_button.setToolTip('')
                widget_helpers.set_button_icon(shiftup_button, 'img/icon_shiftup_off.png', 18, 18)
            else:
                shiftup_button.setEnabled(True)
                shiftup_button.setToolTip('Shift this wave up by one')
                widget_helpers.set_button_icon(shiftup_button, 'img/icon_shiftup.png', 18, 18)

            if i == len(self.wavedefs) - 1:
                shiftdn_button.setEnabled(False)
                shiftdn_button.setToolTip('')
                widget_helpers.set_button_icon(shiftdn_button, 'img/icon_shiftdown_off.png', 18, 18)
            else:
                shiftdn_button.setEnabled(True)
                shiftdn_button.setToolTip('Shift this wave down by one')
                widget_helpers.set_button_icon(shiftdn_button, 'img/icon_shiftdown.png', 18, 18)

    # Moves the wave up or down
    def shift_wavedef(self, frame, dir=None):
        # Shift widgets
        idx_frame = self.wavedefs_scrollarea_layout.indexOf(frame)
        idx_label = idx_frame - 1

        new_idx_frame = idx_frame + 2 if dir == 'down' else idx_frame - 2;
        new_idx_label = idx_label + 2 if dir == 'down' else idx_label - 2;
        self.wavedefs_scrollarea_layout.removeWidget(self.wavedefs[frame.id]['Frames']['InfoFrame']);
        self.wavedefs_scrollarea_layout.removeWidget(self.wavedefs[frame.id]['Frames']['WaveFrame']);
        self.wavedefs_scrollarea_layout.insertWidget(new_idx_label, self.wavedefs[frame.id]['Frames']['InfoFrame']);
        self.wavedefs_scrollarea_layout.insertWidget(new_idx_frame, self.wavedefs[frame.id]['Frames']['WaveFrame']);

        # Shift the array contents
        first = frame.id
        second = frame.id+1 if dir == 'down' else frame.id-1
        t = self.wavedefs[first]
        self.wavedefs[first] = self.wavedefs[second]
        self.wavedefs[second] = t
            
        self.refresh_wavedefs(squads=True) # Refresh wavedefs state (update buttons, etc)

    # Deletes the wave from the list (and GUI)
    def remove_wavedef(self, id, should_warn=True):
        if should_warn and len(self.wavedefs[id]['Squads']) > 0: # Wave is non-empty. Display dialog!
            diag_title = 'Delete Wave'
            diag_text = 'Are you sure you want to delete this wave?\nAll data will be lost!'
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-150 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            choice_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y)
            choice_dialog.yes_button.clicked.connect(partial(self.dialog_accept, choice_dialog))
            choice_dialog.no_button.clicked.connect(partial(self.dialog_reject, choice_dialog))
            choice_dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            choice_dialog.exec_()
            if choice_dialog.accepted == False: # Didn't accept the dialog (don't delete)
                choice_dialog.setParent(None) # Remove the dialog
                return
            choice_dialog.setParent(None)

        # Remove the widgets
        for label in self.wavedefs[id]['Labels'].values():
            self.wavedefs_scrollarea_layout.removeWidget(label);
        self.wavedefs_scrollarea_layout.removeWidget(self.wavedefs[id]['Frames']['WaveFrame']);

        for label in self.wavedefs[id]['Labels'].values():
            label.setParent(None)
        self.wavedefs[id]['Frames']['SquadFrame'].setParent(None)
        self.wavedefs[id]['Frames']['WaveFrame'].setParent(None)
        self.wavedefs[id]['Frames']['InfoFrame'].setParent(None)

        self.wavedefs.pop(id) # Remove from array
        # Todo: Remove the squads as well

        self.refresh_wavedefs(squads=True) # Refresh wavedefs state (update buttons, etc)
        if len(self.wavedefs) < 10:
            self.buttons['Add Wave'].setVisible(True) # We can show the add button again 
                
        # File has been modified
        if self.filename == 'Untitled':
            self.dirty = True if len(self.wavedefs) > 0 else False
        else:
            self.dirty = True
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)')

    # Adds a new wave to the list
    def add_wavedef(self):
        # Label / button stuff
        ss = "color: rgb(255, 255, 255);"
        sp_fixed = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_fixed.setHorizontalStretch(0)
        sp_fixed.setVerticalStretch(0)
        sp_pref = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sp_pref.setHorizontalStretch(0)
        sp_pref.setVerticalStretch(0)
        sp_exp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sp_exp.setHorizontalStretch(0)
        sp_exp.setVerticalStretch(0)
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(12)
        font_label.setWeight(75)

        # Set up wave frame
        wavedef_frame = QtWidgets.QFrame(self.wavedefs_scrollarea_contents)
        wavedef_frame.id = len(self.wavedefs)

        wave_list = QtWidgets.QVBoxLayout(wavedef_frame)
        wave_layout = QtWidgets.QHBoxLayout()

        # Set up the vertical bar of options (shift up, shift down, delete)
        wave_options_frame = QtWidgets.QFrame(self.wavedefs_scrollarea_contents)
        wave_options_frame.setSizePolicy(sp_fixed)
        wave_options_layout = QtWidgets.QVBoxLayout(wave_options_frame)
        ss_button = 'QToolTip {color: rgb(0, 0, 0);\nbackground-color: rgb(40, 40, 40);}' # Stylesheet
        shiftup_button = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Shift Up', tooltip='Shift this wave upwards by one', style=ss_button, icon_path='img/icon_shiftup.png', icon_w=18, icon_h=18, size_policy=sp_fixed, draggable=False)
        shiftdn_button = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Shift Down', tooltip='Shift this wave downwards by one', style=ss_button, icon_path='img/icon_shiftdown.png', icon_w=18, icon_h=18, size_policy=sp_fixed, draggable=False)
        clear_button = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Clear', tooltip='Clear this wave of all ZEDs', style=ss_button, icon_path='img/icon_clear.png', icon_w=18, icon_h=18, size_policy=sp_fixed, draggable=False)
        delete_button = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Delete', tooltip='Remove this wave from the SpawnCycle', style=ss_button, icon_path='img/icon_delete.png', icon_w=18, icon_h=18, size_policy=sp_fixed, draggable=False)
        shiftup_button.clicked.connect(partial(self.shift_wavedef, wavedef_frame, 'up'))
        shiftdn_button.clicked.connect(partial(self.shift_wavedef, wavedef_frame, 'down'))
        clear_button.clicked.connect(partial(self.clear_wavedef, wavedef_frame.id, True))
        delete_button.clicked.connect(partial(self.remove_wavedef, wavedef_frame.id, True))
        options_buttons = {'Shift Up': shiftup_button,
                           'Shift Down': shiftdn_button,
                           'Clear': clear_button,
                           'Delete': delete_button}
        wave_options_layout.addWidget(shiftup_button)
        wave_options_layout.addWidget(shiftdn_button)
        wave_options_layout.addWidget(clear_button)
        wave_options_layout.addWidget(delete_button)

        # Create a frame to hold the Wave number and ZED count
        info_frame = QtWidgets.QFrame()
        info_frame_layout = QtWidgets.QHBoxLayout(info_frame)
        info_frame_layout.setAlignment(QtCore.Qt.AlignLeft)
        info_frame_layout.setSpacing(64)
        info_frame_layout.setContentsMargins(70, 8, 0, 0)

        # First add wave title label
        wavedef_label_text = f'\n        WAVE {len(self.wavedefs) + 1}' if len(self.wavedefs) > 0 else f'        WAVE {len(self.wavedefs) + 1}'
        wavedef_label = widget_helpers.create_label(self.wavedefs_scrollarea_contents, text=wavedef_label_text, style=ss, font=font_label)
        wavedef_label.setAlignment(QtCore.Qt.AlignLeft)
        wavedef_label.setSizePolicy(sp_fixed)
        info_frame_layout.addWidget(wavedef_label)

        # Now add the ZED count
        zedcount_label = widget_helpers.create_label(self.wavedefs_scrollarea_contents, text='Total ZEDs: 0', style=ss, font=font_label)
        zedcount_label.setAlignment(QtCore.Qt.AlignLeft)
        zedcount_label.setSizePolicy(sp_fixed)
        info_frame_layout.addWidget(zedcount_label)

        # Finally add it to the main layout
        self.wavedefs_scrollarea_layout.addWidget(info_frame)
        wave_layout.addWidget(wave_options_frame)

        # Add new frame for the wave's squads
        squads_frame = widget_helpers.QFrame_Drag(self.wavedefs_scrollarea_contents, id=len(self.wavedefs), squad=False)
        squads_frame.raise_() # Raise to top-layer
        squads_frame.add_squad = self.add_squad
        squads_frame.remove_zed_from_squad = self.remove_zed_from_squad
        squads_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        squads_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        squads_frame.setAcceptDrops(True)
        squads_frame.setStyleSheet('color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 255);')
        squads_frame.setFrameShape(QtWidgets.QFrame.Box)
        squads_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        squads_frame.setLineWidth(2)
        #squads_frame.setMinimumSize(QtCore.QSize(700, 0))
        squads_frame.setSizePolicy(sp_exp)
        squads_frame_layout = QtWidgets.QHBoxLayout(squads_frame) # Add layout
        squads_frame_layout.setAlignment(QtCore.Qt.AlignLeft)
        wave_layout.addWidget(squads_frame)

        wave_list.addLayout(wave_layout) # Finalize layout

        if len(self.wavedefs) < 1: # First wave added
            self.wavedefs_scrollarea_layout.insertWidget(0, info_frame)
        else:
            self.wavedefs_scrollarea_layout.insertWidget(self.wavedefs_scrollarea_layout.count()-2, info_frame)
        self.wavedefs_scrollarea_layout.insertWidget(self.wavedefs_scrollarea_layout.count()-1, wavedef_frame)

        # Move the vertical scrollbar to the bottom
        vbar = self.wavedefs_scrollarea.verticalScrollBar()
        vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.maximum()))

        self.wavedefs.append({'ID': len(self.wavedefs), 'Labels': {'WaveNumber': wavedef_label, 'ZEDCount': zedcount_label}, 'Layouts': {'SquadFrame': squads_frame_layout, 'InfoFrame': info_frame_layout}, 'Frames': {'WaveFrame': wavedef_frame, 'SquadFrame': squads_frame, 'InfoFrame': info_frame}, 'OptionsButtons': options_buttons, 'Squads': []})

        # Final wave: hide 'Add Wave' button
        if len(self.wavedefs) == _WAVE_MAX:
            self.buttons['Add Wave'].setVisible(False)

        self.refresh_wavedefs(squads=False) # Refresh wavedefs state (update buttons, etc)

    # Set up Options Pane
    def setup_options_pane(self):
        # Options pane size policy
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)

        # Options pane font
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)

        ss = 'QPushButton {color: rgb(255, 255, 255);\nbackground-color: rgb(40, 40, 40);}  QToolTip {color: rgb(0, 0, 0)};' # Stylesheet
        icon_w = 24
        icon_h = 24

        # Create options pane
        self.options_pane = QtWidgets.QHBoxLayout()
        self.options_pane.setSpacing(6)
        self.central_layout.addLayout(self.options_pane)

        # Import
        button_import = widget_helpers.create_button(self.central_widget, self.app, 'Open', text=' Open ', tooltip='Load a SpawnCycle from file', style=ss, icon_path='img/icon_open.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_import)
        self.buttons.update({'Open' : button_import})

        # Set up the main "Open File" menu
        ss_menu = "color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);"
        import_menu = QtWidgets.QMenu()
        import_menu.setMouseTracking(True);
        import_menu.setStyleSheet(ss_menu)
        import_menu.addAction('Browse..', partial(self.load_from_file, None))
        self.import_menu = import_menu
        button_import.setMenu(import_menu)

        # Create dummy "Recent" menu
        recent_menu = QtWidgets.QMenu('Recent Files')
        import_menu.addMenu(recent_menu)

        # Get the recent files list from the metadata
        self.recent_files = meta.get_keyvalue('recent_files')
        self.refresh_recent_menu() # Initialize the "Recent" menu
        
        # Save File
        button_export = widget_helpers.create_button(self.central_widget, self.app, 'Save', text=' Save ', target=partial(self.save_to_file, False, False), tooltip='Save the current SpawnCycle', style=ss, icon_path='img/icon_save.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_export)
        self.buttons.update({'Save' : button_export})

        # Save File As
        button_exportas = widget_helpers.create_button(self.central_widget, self.app, 'Save As', text=' Save As ', target=partial(self.save_to_file, True, False), tooltip='Save the current SpawnCycle with a designated name', style=ss, icon_path='img/icon_saveas.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_exportas)
        self.buttons.update({'Save As' : button_exportas})

        # Close File
        button_close = widget_helpers.create_button(self.central_widget, self.app, 'Close', text=' Close ', target=self.close_file, tooltip='Close the current SpawnCycle', style=ss, icon_path='img/icon_delete.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_close)
        self.buttons.update({'Close' : button_close})

        # Batch options
        button_batch = widget_helpers.create_button(self.central_widget, self.app, 'Batch', text=' Batch ', tooltip='Perform operations on the entire SpawnCycle', style=ss, icon_path='img/icon_batch.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, options=True, draggable=False)   
        self.options_pane.addWidget(button_batch)
        self.buttons.update({'Batch' : button_batch})

        # Populate the Batch Menu
        self.init_batch_menu()
        
        # Analyze SpawnCycle
        button_analyze = widget_helpers.create_button(self.central_widget, self.app, 'Analyze', text=' Analyze ', tooltip='Display SpawnCycle statistics', target=partial(self.open_dialog, 'analyze', 'Analyze SpawnCycle'), style=ss, icon_path='img/icon_analyze.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)   
        self.options_pane.addWidget(button_analyze)
        self.buttons.update({'Analyze' : button_analyze})

        # Generate Spawncycle
        button_generate = widget_helpers.create_button(self.central_widget, self.app, 'Generate', text=' Generate ', tooltip='Generate a SpawnCycle based on pre-determined critera', target=partial(self.open_dialog, 'generate', 'Generate SpawnCycle'), style=ss, icon_path='img/icon_generate.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)   
        self.options_pane.addWidget(button_generate)
        self.buttons.update({'Generate' : button_generate})

        # Convert SpawnCycles
        button_convert = widget_helpers.create_button(self.central_widget, self.app, 'Convert', text=' Convert ', tooltip="Convert SpawnCycles for use with FMX's CD Build", target=partial(self.open_dialog, 'convert', 'Convert SpawnCycles'), style=ss, icon_path='img/icon_switch.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_convert)
        self.buttons.update({'Convert' : button_convert})

        # Settings
        button_settings = widget_helpers.create_button(self.central_widget, self.app, 'Settings', text=' Settings ', tooltip='Access and alter program preferences', target=partial(self.open_dialog, 'settings', 'Settings'), style=ss, icon_path='img/icon_settings.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_settings)
        self.buttons.update({'Settings' : button_settings})

        # About
        button_about = widget_helpers.create_button(self.central_widget, self.app, 'About', text=' About ', tooltip='Show information about the program', target=partial(self.open_dialog, 'about', 'About'), style=ss, icon_path='img/icon_about.png', icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_about)
        self.buttons.update({'About' : button_about})

        # Set justification
        self.options_pane.setAlignment(QtCore.Qt.AlignLeft)

    def do_nothing(self): # Literally does nothing. Used to give a target to menu items that are waiting for a real target
        return

    # Initialize the "Recent Files" menu
    def refresh_recent_menu(self):
        recent_menu = QtWidgets.QMenu('Recent Files', self.import_menu)
        recent_menu.addAction('No files', self.do_nothing)

        if len(self.recent_files) > 0: # No recent files found
            recent_menu.removeAction(recent_menu.actions()[0]) # Remove the "No files"
            for fname in self.recent_files: # Populate the recent files list
                recent_menu.addAction(fname, partial(self.load_from_file, fname))

        self.import_menu.removeAction(self.import_menu.actions()[1]) # Remove the old "Recent" menu
        self.import_menu.addMenu(recent_menu) # Add the new "Recent" menu
        self.recent_menu = recent_menu

    def init_batch_menu(self):
        # Initialize Batch Button menus
        ss_menu = "color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);"
        batch_menu = QtWidgets.QMenu()
        batch_menu.setMouseTracking(True);
        batch_menu.setStyleSheet(ss_menu)
        batch_menu.addAction('Reverse Waves', self.reverse_wavedefs)
        
        replace_menu = QtWidgets.QMenu('Replace ZEDs ..', batch_menu)

        # Init replace menu
        for zed in zed_ids.keys():
            local_zeds = deepcopy(list(zed_ids.keys()))
            local_zeds.remove(zed) # Remove this ZED so it doesn't appear in the menu
            local_menu = QtWidgets.QMenu(zed, replace_menu)
            local_menu.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(50, 50, 50)")

            # Add the rest of the ZEDs to the menu
            for z in local_zeds:
                action = QtWidgets.QAction(z, local_menu)
                local_menu.addAction(action)
                should_warn = z in custom_zeds or z in omega_zeds
                action.triggered.connect(partial(self.replace_zeds, 'all', 'all', [zed], [z], should_warn))
            replace_menu.addMenu(local_menu)

        batch_menu.addMenu(replace_menu)
        self.buttons['Batch'].setMenu(batch_menu)

    # Given the wave ID, squad ID, and a list of zeds, replaces all zeds in squads with the chosen replacement(s)
    def replace_zeds(self, wave_id, squad_id, zeds_to_replace, replacements, should_warn=False):
        global has_swapped_modes
        if should_warn:
            if not has_swapped_modes and meta.get_keyvalue('should_warn_zedset'):
                diag_title = 'WARNING'
                diag_text = '\nThe Custom and Omega ZED sets are NOT supported by most Controlled Difficulty builds.\nUsing these ZEDs may break your SpawnCycle on those builds.\n\nUse at your own risk!\n'
                x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-200 # Anchor dialog to center of window
                y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
                diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True, checkbox=True)
                diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
                
                diag.exec_() # Show the dialog

                # Check if the user clicked "Don't show this again"
                if diag.checkbox.checkState(): # We know this will exist since checkbox=True
                    meta.set_keyvalue('should_warn_zedset', False) # Don't ever show the dialog again

                has_swapped_modes = True # Never show this message again

        # Figure out which waves and squads we're looping over
        wave_ids = [wave_id] if wave_id != 'all' else [i for i in range(len(self.wavedefs))]
        squad_ids = [[squad_id] for i in range(len(self.wavedefs))] if squad_id != 'all' else [[j for j in range(len(self.wavedefs[i]['Squads']))] for i in range(len(self.wavedefs))]

        zeds_replaced = 0
        replaced = False
        # Loop over the selected waves
        for wid in wave_ids:
            squads = self.wavedefs[wid]['Squads']

            # Loop over the selected squads
            for sid in squad_ids[wid]:
                this_squad_zeds = squads[sid]['ZEDs'] # The ZEDs in this squad

                for i in range(len(zeds_to_replace)): # Replace the ZEDs if they exist
                    zid = zeds_to_replace[i]
                    if zid in this_squad_zeds:
                        new_zid = replacements[i] # Get the new ZED info
                        zed_count = this_squad_zeds[zid]['Count']

                        raged = True if 'Enraged' in new_zid else False
                        self.add_zed_to_squad(wid, sid, new_zid, count=zed_count, raged=raged, ignore_capacity=True) # Add the new one
                        self.remove_zed_from_squad(wid, sid, zid, count='all', replacement=True) # Remove the old zed after to keep the squad (for squad with len 1)     
                        
                        replaced = True
                        zeds_replaced += zed_count

        if replaced:
            self.add_message(f"Replaced {zeds_replaced} {zeds_to_replace[0].replace(' (Enraged)', '')}{'s' if zeds_replaced > 1 else ''} successfully!")
            # Now we need to update stuff
            if wave_id == 'all':
                self.refresh_wavedefs(squads=True) # Need to refresh everything
            else:
                self.refresh_wavedefs(squads=True, wave_id=wave_id, squad_id=squad_id) # Need to refresh this squad
        else:
            self.add_message(f"Error: No ZEDs to replace!")

    # Reverses all waves
    def reverse_wavedefs(self):
        if len(self.wavedefs) == 0: # Can't reverse nothing
            self.add_message("Error: No wave data to reverse!")
            return

        # Add the current wave set as new waves in reverse order
        orig_len = len(self.wavedefs)
        i = orig_len - 1

        # Show "Reversing Waves" dialog
        diag_title = 'Reversing Waves..'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 90 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
        diag_text = f"Reversing Waves.."
        loading_diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=False)
        loading_diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
        loading_diag.show() # Show a dialog to tell user to check messages

        # Process waves in reverse order
        while i >= 0:
            self.add_wavedef() # Add a new wave temporarily
            # Loop over this wave's Squads
            for j in range(len(self.wavedefs[i]['Squads'])):
                k = 0
                # Loop over this Squad's ZEDs
                for (zed_id, zed_data) in self.wavedefs[i]['Squads'][j]['ZEDs'].items():
                    zed_count = zed_data['Count']
                    sr = zed_data['Raged']
                    if k == 0: # First ZED in the squad starts a new squad
                        self.add_squad(len(self.wavedefs)-1, zed_id, count=zed_count, raged=sr)
                    else:
                        self.add_zed_to_squad(len(self.wavedefs)-1, j, zed_id, count=zed_count, raged=sr)
                    k += 1 # Increment ZED counter
            i -= 1 # Increment wave counter

        # Remove the old waves
        for i in range(orig_len):
            self.remove_wavedef(0, should_warn=False)

        loading_diag.close()

    # Toggles autosave off/on
    def toggle_autosave(self):
        autosave_enabled = meta.get_keyvalue('autosave_enabled') # Get autosave status

        # Change the button's icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('img/icon_autosave_false.png' if autosave_enabled else 'img/icon_autosave_true.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttons['Autosave'].setIcon(icon)

        meta.set_keyvalue('autosave_enabled', not autosave_enabled) # Invert the value

        # Post a message
        self.add_message(f"Setting 'Autosave Enabled' set to {not autosave_enabled}")

    # Setup ZED Pane
    def setup_zed_pane(self):
        self.zed_pane = QtWidgets.QVBoxLayout()
        self.zed_pane.setObjectName("zed_pane")

        # Setup the QScrollArea used for the ZED Pane
        self.zed_grid = QtWidgets.QScrollArea(self.central_widget)
        self.zed_grid.horizontalScrollBar().setVisible(False)
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(self.zed_grid.sizePolicy().hasHeightForWidth())
        self.zed_grid.setMinimumSize(QtCore.QSize(160, 0))
        self.zed_grid.setSizePolicy(sp)
        self.zed_grid.setStyleSheet('color: rgb(255, 255, 255); background-color: rgba(40, 40, 40, 255);')
        self.zed_grid.setFrameShape(QtWidgets.QFrame.Box)
        self.zed_grid.setFrameShadow(QtWidgets.QFrame.Plain)
        self.zed_grid.setLineWidth(2)
        self.zed_grid.setWidgetResizable(True)
        self.zed_grid.setObjectName("zed_grid")

        # Setup the ZED Pane
        self.zed_grid_contents = QtWidgets.QWidget()
        self.zed_grid_contents.setGeometry(QtCore.QRect(0, 0, 150, 915))
        self.zed_grid_contents.setObjectName("zed_grid_contents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.zed_grid_contents)
        self.gridLayout_2.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignCenter)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # Icon sizes
        icon_w = 34 if self.zed_mode == 'Custom' else 48
        icon_h = 34 if self.zed_mode == 'Custom' else 48

        # SizePolicy for ZED Buttons
        sp_button = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_button.setHorizontalStretch(0)
        sp_button.setVerticalStretch(0)

        # Label stuff
        sp_label = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sp_label.setHorizontalStretch(0)
        sp_label.setVerticalStretch(0)
        ss_label = 'color: rgb(255, 255, 255);'
        ss_button = 'QToolTip {color: rgb(0, 0, 0);\nbackground-color: rgb(40, 40, 40);}' # Stylesheet
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(12)
        font_label.setBold(True)
        font_label.setWeight(75)

        # Set up ZED Toggle button
        sp_toggle = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sp_toggle.setHorizontalStretch(0)
        sp_toggle.setVerticalStretch(0)
        ss_toggle = 'QPushButton {color: rgb(255, 255, 255);\nbackground-color: rgb(40, 40, 40);} QToolTip {color: rgb(0, 0, 0)};' # Stylesheet
        button_switch = widget_helpers.create_button(self.central_widget, self.app, 'ZED Set', text=' Default' if self.zed_mode == 'Custom' else ' Custom', tooltip='Switch current ZED set', target=partial(self.switch_zed_mode, True), icon_path='img/icon_switch.png', icon_w=32, icon_h=32, style=ss_toggle, font=font_label, size_policy=sp_toggle, draggable=False)
        self.buttons.update({'Switch ZEDs' : button_switch})
        self.zed_pane.addWidget(button_switch)


        # Setup Trash ZEDs area
        label_trashzeds = widget_helpers.create_label(self.zed_grid_contents, text='Trash ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Trash ZEDs' : label_trashzeds})
        self.gridLayout_2.addWidget(label_trashzeds, 0, 0, 1, 1)
        widget_helpers.set_plain_border(label_trashzeds, color=QtGui.QColor(255, 255, 255), width=2)
        self.grid_trashzeds = QtWidgets.QGridLayout()
        self.grid_trashzeds.setObjectName("grid_trashzeds")

        button_cyst = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Cyst', tooltip='Cyst', style=ss_button, icon_path='img/icon_cyst.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_trashzeds.addWidget(button_cyst, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Cyst' : button_cyst})

        button_slasher = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Slasher', tooltip='Slasher', style=ss_button, icon_path='img/icon_slasher.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_trashzeds.addWidget(button_slasher, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Slasher' : button_slasher})

        button_alphaclot = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Alpha Clot', tooltip='Alpha Clot', style=ss_button, icon_path='img/icon_alphaclot.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_trashzeds.addWidget(button_alphaclot, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Alpha Clot' : button_alphaclot})

        button_rioter = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Rioter', tooltip='Rioter', style=ss_button, icon_path='img/icon_rioter.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_trashzeds.addWidget(button_rioter, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Rioter' : button_rioter})

        button_gorefast = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Gorefast', tooltip='Gorefast', style=ss_button, icon_path='img/icon_gorefast.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_trashzeds.addWidget(button_gorefast, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Gorefast' : button_gorefast})

        button_gorefiend = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Gorefiend', tooltip='Gorefiend', style=ss_button, icon_path='img/icon_gorefiend.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_trashzeds.addWidget(button_gorefiend, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'Gorefiend' : button_gorefiend})
        
        button_crawler = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Crawler', tooltip='Crawler', style=ss_button, icon_path='img/icon_crawler.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_trashzeds.addWidget(button_crawler, 3, 0, 1, 1)
        self.zed_pane_buttons.update({'Crawler' : button_crawler})

        button_elitecrawler = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Elite Crawler', tooltip='Elite Crawler', style=ss_button, icon_path='img/icon_elitecrawler.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_trashzeds.addWidget(button_elitecrawler, 3, 1, 1, 1)
        self.zed_pane_buttons.update({'Elite Crawler' : button_elitecrawler})

        button_stalker = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Stalker', tooltip='Stalker', style=ss_button, icon_path='img/icon_stalker.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_trashzeds.addWidget(button_stalker, 4, 0, 1, 1)
        self.zed_pane_buttons.update({'Stalker' : button_stalker})

        self.gridLayout_2.addLayout(self.grid_trashzeds, 1, 0, 1, 1)


        # Setup Medium ZEDs area
        label_mediumzeds = widget_helpers.create_label(self.zed_grid_contents, text='Medium ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Medium ZEDs' : label_mediumzeds})
        self.gridLayout_2.addWidget(label_mediumzeds, 2, 0, 1, 1)
        widget_helpers.set_plain_border(label_mediumzeds, color=QtGui.QColor(255, 255, 255), width=2)
        self.grid_mediumzeds = QtWidgets.QGridLayout()
        self.grid_mediumzeds.setObjectName("grid_mediumzeds")

        button_bloat = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Bloat', tooltip='Bloat', style=ss_button, icon_path='img/icon_bloat.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_mediumzeds.addWidget(button_bloat, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Bloat' : button_bloat})

        button_husk = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Husk', tooltip='Husk', style=ss_button, icon_path='img/icon_husk.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_mediumzeds.addWidget(button_husk, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Husk' : button_husk})

        button_siren = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Siren', tooltip='Siren', style=ss_button, icon_path='img/icon_siren.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_mediumzeds.addWidget(button_siren, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Siren' : button_siren})

        button_edar_emp = widget_helpers.create_button(self.zed_grid_contents, self.app, 'E.D.A.R Trapper', tooltip='E.D.A.R Trapper', style=ss_button, icon_path='img/icon_edar_emp.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_mediumzeds.addWidget(button_edar_emp, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'E.D.A.R Trapper' : button_edar_emp})

        button_edar_laser = widget_helpers.create_button(self.zed_grid_contents, self.app, 'E.D.A.R Blaster', tooltip='E.D.A.R Blaster', style=ss_button, icon_path='img/icon_edar_laser.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_mediumzeds.addWidget(button_edar_laser, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'E.D.A.R Blaster' : button_edar_laser})

        button_edar_rocket = widget_helpers.create_button(self.zed_grid_contents, self.app, 'E.D.A.R Bomber', tooltip='E.D.A.R Bomber', style=ss_button, icon_path='img/icon_edar_rocket.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_mediumzeds.addWidget(button_edar_rocket, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'E.D.A.R Bomber' : button_edar_rocket})

        self.gridLayout_2.addLayout(self.grid_mediumzeds, 3, 0, 1, 1)


        # Setup Large ZEDs area
        label_largezeds = widget_helpers.create_label(self.zed_grid_contents, text='Large ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Large ZEDs' : label_largezeds})
        self.gridLayout_2.addWidget(label_largezeds, 4, 0, 1, 1)
        widget_helpers.set_plain_border(label_largezeds, color=QtGui.QColor(255, 255, 255), width=2)
        self.grid_largezeds = QtWidgets.QGridLayout()
        self.grid_largezeds.setObjectName("grid_largezeds")

        button_quarterpound = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Quarter Pound', tooltip='Quarter Pound', style=ss_button, icon_path='img/icon_quarterpound.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_largezeds.addWidget(button_quarterpound, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Quarter Pound' : button_quarterpound})

        button_quarterpound_raged = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Quarter Pound (Enraged)', tooltip='Quarter Pound (Enraged)', style=ss_button, icon_path='img/icon_quarterpound.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_largezeds.addWidget(button_quarterpound_raged, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Quarter Pound (Enraged)' : button_quarterpound_raged})

        button_fleshpound = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Fleshpound', tooltip='Fleshpound', style=ss_button, icon_path='img/icon_fleshpound.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_largezeds.addWidget(button_fleshpound, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Fleshpound' : button_fleshpound})

        button_fleshpound_raged = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Fleshpound (Enraged)', tooltip='Fleshpound (Enraged)', style=ss_button, icon_path='img/icon_fleshpound.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_largezeds.addWidget(button_fleshpound_raged, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Fleshpound (Enraged)' : button_fleshpound_raged})

        button_scrake = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Scrake', tooltip='Scrake', style=ss_button, icon_path='img/icon_scrake.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_largezeds.addWidget(button_scrake, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Scrake' : button_scrake})

        button_alphascrake = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Alpha Scrake', tooltip='Alpha Scrake', style=ss_button, icon_path='img/icon_alphascrake.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_largezeds.addWidget(button_alphascrake, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'Alpha Scrake' : button_alphascrake})

        button_alphafleshpound = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Alpha Fleshpound', tooltip='Alpha Fleshpound', style=ss_button, icon_path='img/icon_alphafleshpound.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_largezeds.addWidget(button_alphafleshpound, 3, 0, 1, 1)
        self.zed_pane_buttons.update({'Alpha Fleshpound' : button_alphafleshpound})

        button_alphafleshpound_raged = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Alpha Fleshpound (Enraged)', tooltip='Alpha Fleshpound (Enraged)', style=ss_button, icon_path='img/icon_alphafleshpound.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_largezeds.addWidget(button_alphafleshpound_raged, 3, 1, 1, 1)
        self.zed_pane_buttons.update({'Alpha Fleshpound (Enraged)' : button_alphafleshpound_raged})
        
        self.gridLayout_2.addLayout(self.grid_largezeds, 5, 0, 1, 1)


        # Setup Bosses area
        label_bosses = widget_helpers.create_label(self.zed_grid_contents, text='Bosses', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Bosses' : label_bosses})
        self.gridLayout_2.addWidget(label_bosses, 6, 0, 1, 1)
        widget_helpers.set_plain_border(label_bosses, color=QtGui.QColor(255, 255, 255), width=2)
        self.grid_bosses = QtWidgets.QGridLayout()
        self.grid_bosses.setObjectName("grid_bosses")

        button_abomination_spawn = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Abomination Spawn', tooltip='Abomination Spawn', style=ss_button, icon_path='img/icon_abomspawn.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_bosses.addWidget(button_abomination_spawn, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Abomination Spawn' : button_abomination_spawn})

        button_kingfleshpound = widget_helpers.create_button(self.zed_grid_contents, self.app, 'King Fleshpound', tooltip='King Fleshpound', style=ss_button, icon_path='img/icon_kingfleshpound.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_bosses.addWidget(button_kingfleshpound, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'King Fleshpound' : button_kingfleshpound})

        button_hans = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Dr. Hans Volter', tooltip='Dr. Hans Volter', style=ss_button, icon_path='img/icon_hans.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_bosses.addWidget(button_hans, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Dr. Hans Volter' : button_hans})

        button_patriarch = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Patriarch', tooltip='Patriarch', style=ss_button, icon_path='img/icon_patriarch.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_bosses.addWidget(button_patriarch, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Patriarch' : button_patriarch})

        button_abomination = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Abomination', tooltip='Abomination', style=ss_button, icon_path='img/icon_abomination.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_bosses.addWidget(button_abomination, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Abomination' : button_abomination})

        button_matriarch = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Matriarch', tooltip='Matriarch', style=ss_button, icon_path='img/icon_matriarch.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_bosses.addWidget(button_matriarch, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'Matriarch' : button_matriarch})

        self.gridLayout_2.addLayout(self.grid_bosses, 7, 0, 1, 1)


        # Setup Omega Trash area
        label_omega_trash = widget_helpers.create_label(self.zed_grid_contents, text='Trash ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Omega Trash' : label_omega_trash})
        self.gridLayout_2.addWidget(label_omega_trash, 8, 0, 1, 1)
        widget_helpers.set_plain_border(label_omega_trash, color=QtGui.QColor(255, 255, 255), width=2)
        self.grid_omega_trash = QtWidgets.QGridLayout()
        self.grid_omega_trash.setObjectName("grid_omega_trash")

        button_slasher_omega = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Slasher Omega', tooltip='Slasher Omega', style=ss_button, icon_path='img/icon_slasher_omega.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_trash.addWidget(button_slasher_omega, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Slasher Omega' : button_slasher_omega})

        button_gorefast_omega = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Gorefast Omega', tooltip='Gorefast Omega', style=ss_button, icon_path='img/icon_gorefast_omega.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_trash.addWidget(button_gorefast_omega, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Gorefast Omega' : button_gorefast_omega})

        button_stalker_omega = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Stalker Omega', tooltip='Stalker Omega', style=ss_button, icon_path='img/icon_stalker_omega.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_trash.addWidget(button_stalker_omega, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Stalker Omega' : button_stalker_omega})

        button_crawler_tiny = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Tiny Crawler', tooltip='Tiny Crawler', style=ss_button, icon_path='img/icon_crawler_tiny.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_trash.addWidget(button_crawler_tiny, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Tiny Crawler' : button_crawler_tiny})

        button_crawler_medium = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Medium Crawler', tooltip='Medium Crawler', style=ss_button, icon_path='img/icon_crawler_medium.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_trash.addWidget(button_crawler_medium, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Medium Crawler' : button_crawler_medium})

        button_crawler_big = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Big Crawler', tooltip='Big Crawler', style=ss_button, icon_path='img/icon_crawler_big.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_trash.addWidget(button_crawler_big, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'Big Crawler' : button_crawler_big})

        button_crawler_huge = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Huge Crawler', tooltip='Huge Crawler', style=ss_button, icon_path='img/icon_crawler_huge.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_trash.addWidget(button_crawler_huge, 3, 0, 1, 1)
        self.zed_pane_buttons.update({'Huge Crawler' : button_crawler_huge})

        button_crawler_ultra = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Ultra Crawler', tooltip='Ultra Crawler', style=ss_button, icon_path='img/icon_crawler_ultra.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_trash.addWidget(button_crawler_ultra, 3, 1, 1, 1)
        self.zed_pane_buttons.update({'Ultra Crawler' : button_crawler_ultra})
        
        self.gridLayout_2.addLayout(self.grid_omega_trash, 9, 0, 1, 1)


        # Setup Omega Medium area
        label_omega_medium = widget_helpers.create_label(self.zed_grid_contents, text='Medium ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Omega Medium' : label_omega_medium})
        self.gridLayout_2.addWidget(label_omega_medium, 10, 0, 1, 1)
        widget_helpers.set_plain_border(label_omega_medium, color=QtGui.QColor(255, 255, 255), width=2)
        self.grid_omega_medium = QtWidgets.QGridLayout()
        self.grid_omega_medium.setObjectName("grid_omega_medium")

        button_siren_omega = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Siren Omega', tooltip='Siren Omega', style=ss_button, icon_path='img/icon_siren_omega.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_medium.addWidget(button_siren_omega, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Siren Omega' : button_siren_omega})

        button_husk_omega = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Husk Omega', tooltip='Husk Omega', style=ss_button, icon_path='img/icon_husk_omega.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_medium.addWidget(button_husk_omega, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Husk Omega' : button_husk_omega})

        button_husk_tiny = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Tiny Husk', tooltip='Tiny Husk', style=ss_button, icon_path='img/icon_husk_tiny.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_medium.addWidget(button_husk_tiny, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Tiny Husk' : button_husk_tiny})

        self.gridLayout_2.addLayout(self.grid_omega_medium, 11, 0, 1, 1)


        # Setup Omega Large area
        label_omega_large = widget_helpers.create_label(self.zed_grid_contents, text='Large ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Omega Large' : label_omega_large})
        self.gridLayout_2.addWidget(label_omega_large, 12, 0, 1, 1)
        widget_helpers.set_plain_border(label_omega_large, color=QtGui.QColor(255, 255, 255), width=2)
        self.grid_omega_large = QtWidgets.QGridLayout()
        self.grid_omega_large.setObjectName("grid_omega_large")

        button_scrake_omega = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Scrake Omega', tooltip='Scrake Omega', style=ss_button, icon_path='img/icon_scrake_omega.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_large.addWidget(button_scrake_omega, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Scrake Omega' : button_scrake_omega})

        button_scrake_emperor = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Scrake Emperor', tooltip='Scrake Emperor', style=ss_button, icon_path='img/icon_scrake_emperor.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_large.addWidget(button_scrake_emperor, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Scrake Emperor' : button_scrake_emperor})

        button_scrake_tiny = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Tiny Scrake', tooltip='Tiny Scrake', style=ss_button, icon_path='img/icon_scrake_tiny.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_large.addWidget(button_scrake_tiny, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Tiny Scrake' : button_scrake_tiny})

        button_fleshpound_omega = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Fleshpound Omega', tooltip='Fleshpound Omega', style=ss_button, icon_path='img/icon_fleshpound_omega.png', icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, draggable=True)
        self.grid_omega_large.addWidget(button_fleshpound_omega, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Fleshpound Omega' : button_fleshpound_omega})

        self.gridLayout_2.addLayout(self.grid_omega_large, 13, 0, 1, 1)


        # Highlight omega buttons
        button_slasher_omega.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_gorefast_omega.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_stalker_omega.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_fleshpound_omega.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_husk_omega.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_husk_tiny.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_siren_omega.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_scrake_omega.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_scrake_tiny.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_scrake_emperor.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_crawler_tiny.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_crawler_medium.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_crawler_big.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_crawler_huge.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")
        button_crawler_ultra.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid purple;}")

        # Highlight raged buttons
        button_quarterpound_raged.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid red;}")
        button_fleshpound_raged.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid red;}")
        button_alphafleshpound_raged.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid red;}")
        
        # Set up autosave button
        autosave_icon = 'img/icon_autosave_true.png' if meta.get_keyvalue('autosave_enabled') else 'img/icon_autosave_false.png'
        button_autosave = widget_helpers.create_button(self.central_widget, self.app, 'Autosave', text=' Autosave', tooltip='Toggle Autosave', target=partial(self.toggle_autosave), icon_path=autosave_icon, icon_w=32, icon_h=32, style=ss_toggle, font=font_label, size_policy=sp_toggle, draggable=False)
        self.buttons.update({'Autosave' : button_autosave})

        # Finalize ZED Pane
        self.zed_grid.setWidget(self.zed_grid_contents)
        self.zed_pane.addWidget(self.zed_grid)
        self.zed_pane.addWidget(button_autosave)
        self.main_area.addLayout(self.zed_pane)
        self.central_layout.addLayout(self.main_area)

    # Set up the WaveDefs area (where the waves are shown)
    def setup_wavedefs(self):
        # Set up WavesDef area
        self.wavedefs_area = QtWidgets.QVBoxLayout()
        self.wavedefs_scrollarea = widget_helpers.QScrollArea_Drag(self.central_widget)
        self.wavedefs_scrollarea.remove_zed_from_squad = self.remove_zed_from_squad # Store function for later
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(self.wavedefs_scrollarea.sizePolicy().hasHeightForWidth())
        self.wavedefs_scrollarea.setSizePolicy(sp)
        self.wavedefs_scrollarea.setWidgetResizable(True)
        self.wavedefs_scrollarea.setStyleSheet('color: rgb(255, 255, 255); background-color: rgba(40, 40, 40, 255);')
        self.wavedefs_scrollarea.setFrameShape(QtWidgets.QFrame.Box)
        self.wavedefs_scrollarea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.wavedefs_scrollarea.setLineWidth(2)
        self.wavedefs_scrollarea_contents = QtWidgets.QWidget()
        self.wavedefs_scrollarea_contents.setGeometry(QtCore.QRect(0, 0, 990, 815))

        # Set up scrollArea layout
        verticalLayout_3 = QtWidgets.QVBoxLayout(self.wavedefs_scrollarea_contents)
        self.wavedefs_scrollarea_layout = QtWidgets.QVBoxLayout()
        verticalLayout_3.addLayout(self.wavedefs_scrollarea_layout)
        self.wavedefs_scrollarea.setWidget(self.wavedefs_scrollarea_contents)
        self.wavedefs_area.addWidget(self.wavedefs_scrollarea)

        # Set up the "Add Wave" button
        sp_button = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_button.setHorizontalStretch(0)
        sp_button.setVerticalStretch(0)
        font_button = QtGui.QFont()
        font_button.setFamily(_DEF_FONT_FAMILY)
        font_button.setPointSize(12)
        font_button.setBold(True)
        font_button.setWeight(75)
        ss_button = 'QToolTip {color: rgb(0, 0, 0);\nbackground-color: rgb(40, 40, 40);}' # Stylesheet
        button_addwave = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Add Wave', target=self.add_wavedef, text=' Add Wave', tooltip='Add a new wave to the SpawnCycle', style=ss_button, icon_path='img/icon_add.png', icon_w=16, icon_h=16, font=font_button, size_policy=sp_button, draggable=False)
        self.wavedefs_scrollarea_layout.setAlignment(QtCore.Qt.AlignTop)
        self.wavedefs_scrollarea_layout.addWidget(button_addwave)
        self.buttons.update({'Add Wave' : button_addwave})

    # Adds a message to the 'Messages' window
    def add_message(self, message, prefix=True):
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(8)
        font_label.setWeight(75)
        ss_label = 'color: rgb(255, 255, 255);'
        out_msg = f"[{datetime.now().strftime('%H:%M')}] {message}" if prefix else message
        current_text = self.messages_textedit.toPlainText()
        if current_text != '':
            self.messages_textedit.setPlainText(f"{current_text}\n{out_msg}")
        else:
            self.messages_textedit.setPlainText(f"{current_text}{out_msg}")
        vbar = self.messages_textedit.verticalScrollBar()
        vbar.setValue(vbar.maximum())

    # Clears the messages window
    def clear_messages(self):
        self.messages_textedit.setText('')

    # Sets up the messages box
    def setup_messages(self):
        # Font stuff
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(12)
        font_label.setBold(True)
        font_label.setWeight(75)

        font_messages = QtGui.QFont()
        font_messages.setFamily(_DEF_FONT_FAMILY)
        font_messages.setPointSize(8)
        font_messages.setBold(True)
        font_messages.setWeight(75)

        sp_button = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_button.setHorizontalStretch(0)
        sp_button.setVerticalStretch(0)
        ss_button = 'QPushButton {color: rgb(255, 255, 255);\nbackground-color: rgb(40, 40, 40);} QToolTip {color: rgb(0, 0, 0)};' # Stylesheet
        ss_label = 'color: rgb(255, 255, 255);' # Stylesheet
        ss_textedit = 'color: rgb(255, 255, 255); background-color: rgba(40, 40, 40, 255);'

        # Set up Messages area
        messages_header_frame = QtWidgets.QFrame()
        messages_header_layout = QtWidgets.QHBoxLayout(messages_header_frame)
        messages_header_layout.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        messages_header_layout.setSpacing(15)
        label_messages_header = widget_helpers.create_label(self.central_widget, text='Messages', style=ss_label, font=font_label)
        label_messages_header.setAlignment(QtCore.Qt.AlignLeft)
        button_clear_messages = widget_helpers.create_button(self.central_widget, None, 'Clear', target=self.clear_messages, text=' Clear', tooltip='Clears all Messages', style=ss_button, font=font_messages, size_policy=sp_button, draggable=False)
        self.labels.update({'Messages Header' : label_messages_header})
        self.buttons.update({'Clear Messages' : button_clear_messages})
        messages_header_layout.addWidget(label_messages_header)
        messages_header_layout.addWidget(button_clear_messages)
        self.wavedefs_area.addWidget(messages_header_frame)

        # Set up Messages area
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.messages_textedit = QtWidgets.QTextEdit(self.central_widget)
        self.messages_textedit.setReadOnly(True)
        self.messages_textedit.setMinimumSize(QtCore.QSize(0, 96))
        self.messages_textedit.setSizePolicy(sp)
        self.messages_textedit.setFont(font_messages)
        self.messages_textedit.setStyleSheet(ss_textedit)
        self.messages_textedit.setFrameShape(QtWidgets.QFrame.Box)
        self.messages_textedit.setFrameShadow(QtWidgets.QFrame.Plain)
        self.messages_textedit.setLineWidth(2)
        self.wavedefs_area.addWidget(self.messages_textedit)
        self.main_area.addLayout(self.wavedefs_area)

    # Clears the wave of all zeds
    def clear_wavedef(self, id, should_warn=True):
        if should_warn and len(self.wavedefs[id]['Squads']) > 0: # Wave is non-empty. Display dialog!
            diag_title = 'Clear Wave'
            diag_text = 'Are you sure you want to clear all data from this wave?\nAll data will be lost!'
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-150 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            choice_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y)
            choice_dialog.yes_button.clicked.connect(partial(self.dialog_accept, choice_dialog))
            choice_dialog.no_button.clicked.connect(partial(self.dialog_reject, choice_dialog))
            choice_dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            choice_dialog.exec_()
            if choice_dialog.accepted == False: # Didn't accept the dialog (don't delete)
                choice_dialog.setParent(None) # Remove the dialog
                return
            choice_dialog.setParent(None)

        # Remove the widgets
        for i in reversed(range(self.wavedefs[id]['Layouts']['SquadFrame'].count())): 
            self.wavedefs[id]['Layouts']['SquadFrame'].itemAt(i).widget().setParent(None)
        self.wavedefs[id]['Labels']['ZEDCount'].setText('Total ZEDs: 0')
        self.wavedefs[id]['Squads'] = [] # Reset the internal implementation

        # File has been modified
        if self.filename == 'Untitled':
            num_squads = sum([len(wd['Squads']) for wd in self.wavedefs])
            self.dirty = True if num_squads > 0 else False # If the cycle is empty as a result of this, no need to mark dirty
        else:
            self.dirty = True
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)')

    # Completely clears the WaveDefs pane of all widgets
    def clear_wavedefs(self):
        for i in reversed(range(self.wavedefs_scrollarea_layout.count())): 
            self.wavedefs_scrollarea_layout.itemAt(i).widget().setParent(None)
        self.wavedefs = []

    def dialog_cancel(self, dialog):
        dialog.cancelled = True
        dialog.close()

    def dialog_accept(self, dialog):
        dialog.accepted = True
        dialog.close()

    def dialog_reject(self, dialog):
        dialog.accepted = False
        dialog.close()

    # Generates wavedefs from the given slider data
    def generate_wavedefs(self, slider_data):
        # The current file is 'dirty', needs saving before we populate with the new stuff
        if self.dirty:
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            diag_title = 'SpawnCycler'
            diag_text = 'This will overwrite ALL current wave data.\nDo you wish to continue?'
            save_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y)
            save_dialog.accepted = True
            save_dialog.no_button.clicked.connect(partial(self.dialog_reject, save_dialog))
            self.active_dialog = save_dialog
            save_dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            save_dialog.exec_()
            if not save_dialog.accepted:
                return

        # Close the Generate Window
        self.generate_dialog.close()
        self.active_dialog = None
        self.generate_dialog = None
        
        # First reset the entire window (delete all squads, etc)
        self.reset_state()

        # Generation stats
        num_squads_generated = 0
        num_zeds_generated = 0
        num_trash_generated = 0
        num_medium_generated = 0
        num_larges_generated = 0
        num_bosses_generated = 0
        num_albino_generated = 0
        num_spawnrage_generated = 0
        num_omega_generated = 0

        # Setup weights and zed arrays
        sd = slider_data
        types = ['Trash', 'Medium', 'Large', 'Boss']
        type_weights = [sd['Trash Density'], sd['Medium Density'], sd['Large Density'], sd['Boss Density']]
        trash_zeds = ['Cyst', 'Slasher', 'Alpha Clot', 'Gorefast', 'Crawler', 'Stalker',
                      'Slasher Omega', 'Gorefast Omega', 'Tiny Crawler', 'Medium Crawler',
                      'Big Crawler', 'Huge Crawler', 'Ultra Crawler', 'Stalker Omega']
        trash_weights = [sd['Cyst Density'], sd['Slasher Density'], sd['Alpha Clot Density'], sd['Gorefast Density'], sd['Crawler Density'], sd['Stalker Density'],
                         sd['Slasher Omega Density'], sd['Gorefast Omega Density'], sd['Tiny Crawler Density'], sd['Medium Crawler Density'], sd['Big Crawler Density'],
                         sd['Huge Crawler Density'], sd['Ultra Crawler Density'], sd['Stalker Omega Density']]
        medium_zeds = ['Bloat', 'Husk', 'Siren', 'E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber', 'Husk Omega', 'Tiny Husk', 'Siren Omega']
        medium_weights = [sd['Bloat Density'], sd['Husk Density'], sd['Siren Density'], sd['E.D.A.R Trapper Density'], sd['E.D.A.R Blaster Density'], sd['E.D.A.R Bomber Density'],
                          sd['Husk Omega Density'], sd['Tiny Husk Density'], sd['Siren Omega Density']]
        large_zeds = ['Scrake', 'Quarter Pound', 'Fleshpound', 'Scrake Omega', 'Scrake Emperor', 'Tiny Scrake', 'Fleshpound Omega']
        large_weights = [sd['Scrake Density'], sd['Quarter Pound Density'], sd['Fleshpound Density'], sd['Scrake Omega Density'], sd['Scrake Emperor Density'], sd['Tiny Scrake Density'], sd['Fleshpound Omega Density']]
        bosses = ['Dr. Hans Volter', 'Patriarch', 'King Fleshpound', 'Abomination', 'Matriarch', 'Abomination Spawn'] 
        boss_weights = [sd['Hans Density'], sd['Patriarch Density'], sd['King Fleshpound Density'], sd['Abomination Density'], sd['Matriarch Density'], sd['Abomination Spawn Density']]

        # Show "Loading" dialog
        diag_title = 'Generating..'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 90 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
        diag_text = f"Generating.."
        loading_diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=False)
        loading_diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
        loading_diag.show() # Show a dialog to tell user to check messages

        # Now we can generate
        waves = []
        for i in range(sd['Game Length']):
            # Booleans describing what can exist on this wave
            albino_allowed = ((i + 1) >= sd['Albino Min Wave'])
            spawnrage_allowed = ((i + 1) >= sd['SpawnRage Min Wave'])
            larges_min_wave_reached = ((i + 1) >= sd['Large Min Wave'])
            bosses_min_wave_reached = ((i + 1) >= sd['Boss Min Wave'])

            wave_squads = []

            # Generate squads
            num_squads_to_generate = random.randint(sd['Min Squads'], sd['Max Squads'])
            for j in range(num_squads_to_generate):
                num_squads_generated += 1
                num_zeds_to_generate = random.randint(sd['Squad Min Length'], sd['Squad Max Length'])
                new_squad = {}

                # Generate ZEDs and add them to the squads
                for k in range(num_zeds_to_generate):
                    # Determine what class of ZED to use (Trash, Large, etc)
                    zed_type = random.choices(types, weights=type_weights, k=1)[0]
                    larges_allowed = larges_min_wave_reached
                    bosses_allowed = bosses_min_wave_reached
                    num_zeds_generated += 1
                    spawnrage = False

                    # Special case for larges and boss minimum wave
                    while (zed_type == 'Large' and not larges_allowed) or (zed_type == 'Boss' and not bosses_allowed):
                        zed_type = random.choices(types, weights=type_weights, k=1)[0] # Keep re-rerolling until it's correct

                    # Add a Trash ZED
                    if zed_type == 'Trash':
                        zed_id = random.choices(trash_zeds, weights=trash_weights, k=1)[0] # Choose a ZED
                        num_trash_generated += 1

                        # Account for albinos
                        if albino_allowed:
                            if zed_id == 'Alpha Clot' and (random.randint(1, 100) <= sd['Alpha Clot Albino Density']):
                                zed_id = 'Rioter' # Make ZED an albino zed
                                num_albino_generated += 1
                            elif zed_id == 'Gorefast' and (random.randint(1, 100) <= sd['Gorefast Albino Density']):
                                zed_id = 'Gorefiend' # Make ZED an albino zed
                                num_albino_generated += 1
                            elif zed_id == 'Crawler' and (random.randint(1, 100) <= sd['Crawler Albino Density']):
                                zed_id = 'Elite Crawler' # Make ZED an albino zed
                                num_albino_generated += 1

                    # Add a Medium ZED
                    elif zed_type == 'Medium':
                        zed_id = random.choices(medium_zeds, weights=medium_weights, k=1)[0] # Choose a ZED
                        num_medium_generated += 1

                    # Add a Large ZED
                    elif zed_type == 'Large':
                        zed_id = random.choices(large_zeds, weights=large_weights, k=1)[0] # Choose a ZED
                        num_larges_generated += 1

                        # Account for albinos
                        if albino_allowed:
                            if zed_id == 'Scrake' and (random.randint(1, 100) <= sd['Scrake Albino Density']):
                                zed_id = 'Alpha Scrake' # Make ZED an albino zed
                                num_albino_generated += 1
                            elif zed_id == 'Fleshpound' and (random.randint(1, 100) <= sd['Fleshpound Albino Density']):
                                zed_id = 'Alpha Fleshpound' # Make ZED an albino zed
                                num_albino_generated += 1

                        # Account for spawnrage
                        if spawnrage_allowed:
                            if zed_id == 'Quarter Pound' and (random.randint(1, 100) <= sd['Quarter Pound Rage Density']):
                                zed_id += ' (Enraged)'
                                spawnrage = True
                                num_spawnrage_generated += 1
                            elif zed_id in ['Fleshpound', 'Alpha Fleshpound'] and random.randint(1, 100) <= sd['Fleshpound Rage Density']:
                                zed_id += ' (Enraged)'
                                spawnrage = True
                                num_spawnrage_generated += 1

                    # Add a Boss
                    else:
                        zed_id = random.choices(bosses, weights=boss_weights, k=1)[0] # Choose a ZED
                        num_bosses_generated += 1

                    # Check for omega
                    if zed_id in omega_zeds:
                        num_omega_generated += 1

                    if zed_id in new_squad and new_squad[zed_id]['Raged'] == spawnrage: # Already in the squad and same spawnrage status
                        new_squad.update({zed_id: {'Count': new_squad[zed_id]['Count'] + 1, 'Raged': spawnrage}})
                    else:
                        new_squad.update({zed_id: {'Count': 1, 'Raged': spawnrage}})

                wave_squads.append(new_squad)
            waves.append(wave_squads)

        # Populate the wavedefs using all this data
        self.populate_waves(waves)

        loading_diag.close()

        # Reset scrollbars
        vbar = self.wavedefs_scrollarea.verticalScrollBar()
        vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.minimum()))
        hbar = self.wavedefs_scrollarea.horizontalScrollBar()
        hbar.rangeChanged.connect(lambda: hbar.setValue(hbar.minimum()))

        # Show a dialog indicating completion
        diag_title = 'SpawnCycler'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
        diag_text = f"Generation completed successfully!"
        diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
        diag.setWindowIcon(QtGui.QIcon('img/icon_check.png'))
        diag.exec_() # Show a dialog to tell user to check messages

        # Post messages
        gen_str = (f"Generation complete!\n\n" +
                   f"Summary\n----------------------\n" +
                   f"{sd['Game Length']} Waves generated\n" +
                   f"{num_squads_generated} Squads generated\n" +
                   f"{num_zeds_generated} ZEDs generated ({num_trash_generated} Trash, {num_medium_generated} Mediums, {num_larges_generated} Larges, {num_bosses_generated} Bosses)\n" +
                   f"{num_albino_generated} Albino ZEDs generated\n" +
                   f"{num_omega_generated} Omega ZEDs generated\n" +
                   f"{num_spawnrage_generated} SpawnRaged ZEDs generated")
        self.add_message(gen_str)

    # Initializes the wavedefs table from a list of lines
    def populate_waves(self, waves):
        num_waves = num_squads = num_zeds = 0

        # Add waves
        custom_zeds_found = False
        for i in range(len(waves)):
            num_waves += 1
            wave_id = i
            self.add_wavedef() # Add wave frames etc

            # Add squads
            for j in range(len(waves[i])):
                num_squads += 1
                # Get a JSON-formatted version of the squad
                squad_id = j
                squad = waves[i][j]

                # Input all the ZEDs
                squad_items = list(squad.items())
                for k in range(len(squad_items)):
                    (zed_id, zed_data) = squad_items[k]
                    if zed_id in custom_zeds or zed_id in omega_zeds:
                        custom_zeds_found = True
                    zed_count = zed_data['Count'] # Unpack ZED data
                    num_zeds += zed_count
                    sr = zed_data['Raged']
                    
                    if k == 0: # First ZED in the squad starts a new squad
                        self.add_squad(wave_id, zed_id, count=zed_count, raged=sr)
                    else:
                        self.add_zed_to_squad(wave_id, squad_id, zed_id, count=zed_count, raged=sr)

        # Swap to the appropriate mode depending on the SpawnCycle
        if not custom_zeds_found and self.zed_mode == 'Custom': # Swap to vanilla if no custom zeds are found
            self.switch_zed_mode(should_warn=False)
            self.switch_zed_mode(should_warn=False)
        elif not custom_zeds_found and self.zed_mode == 'Omega': # Swap to vanilla if no custom zeds are found
            self.switch_zed_mode(should_warn=False)
        elif custom_zeds_found:
            global has_swapped_modes # Set the flag so it doesn't warn us
            has_swapped_modes = True

        return num_waves, num_squads, num_zeds

    # Returns the file extension
    def get_file_ext(self, filename):
        i = len(filename) - 1
        while i >= 0:
            if filename[i] == '.':
                return filename[i:]
            i -= 1
        return None

    # Opens the File Browser window to select a file to open
    def load_from_file(self, fname=None):
        # Ask user for filename to open, but only if no filename given
        if fname is None:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', '', 'Standard SpawnCycles (*.txt);;FMX SpawnCycles (*.json)',)
            if filename == '': # Leave if the user cancelled
                return
        else:
            filename = fname

        # Dialog stuff
        diag_title = 'Open File'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()

        # Attempt to read in the file
        file_ext = self.get_file_ext(filename) # Get file extension
        try:
            self.add_message(f"Attempting to open file '{filename}'..")

            if file_ext == '.json': # JSON-formatted SpawnCycle
                with open(filename, 'r') as f_in:
                    json_dict = json.load(f_in)

                    # Need to check for legacy JSONs and convert them properly
                    short_cycle = None
                    medium_cycle = None
                    long_cycle = None
                    if 'ShortSpawnCycle' in json_dict:
                        cycledef = json_dict['ShortSpawnCycle']
                        if isinstance(cycledef, dict) and cycledef != {}: 
                            short_cycle = list(json_dict['ShortSpawnCycle'].values())
                        elif isinstance(cycledef, list) and cycledef != []:
                            short_cycle = json_dict['ShortSpawnCycle']
                    if 'NormalSpawnCycle' in json_dict:
                        cycledef = json_dict['NormalSpawnCycle']
                        if isinstance(cycledef, dict) and cycledef != {}: 
                            medium_cycle = list(json_dict['NormalSpawnCycle'].values())
                        elif isinstance(cycledef, list) and cycledef != []:
                            medium_cycle = json_dict['NormalSpawnCycle']
                    if 'LongSpawnCycle' in json_dict:
                        cycledef = json_dict['LongSpawnCycle']
                        if isinstance(cycledef, dict) and cycledef != {}: 
                            long_cycle = list(json_dict['LongSpawnCycle'].values())
                        elif isinstance(cycledef, list) and cycledef != []:
                            long_cycle = json_dict['LongSpawnCycle']
                    num_cycles = (1 if short_cycle is not None else 0) + (1 if medium_cycle is not None else 0) + (1 if long_cycle is not None else 0)
                    
                    if num_cycles > 1: # Multiple spawncycles. Need to ask which one to open
                        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 90 # Anchor dialog to center of window
                        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
                        font = QtGui.QFont()
                        font.setPointSize(8)
                        font.setBold(True)
                        ss = "color: rgb(255, 255, 255);"
                        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
                        sp.setHorizontalStretch(0)
                        sp.setVerticalStretch(0)

                        # Create dialog
                        dialog = QtWidgets.QDialog()
                        dialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint|QtCore.Qt.WindowTitleHint) # Disable X and minimize
                        dialog.cancelled = False
                        dialog.accepted = False
                        hbox_master = QtWidgets.QHBoxLayout(dialog)

                        # Set up text label
                        dialog_label = QtWidgets.QLabel(dialog)
                        dialog_label.setFont(font)
                        dialog_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
                        dialog_label.setStyleSheet(ss)
                        dialog_label.setText('Multiple SpawnCycles were found.\nSelect one to load:\n')

                        # Set layout
                        vbox = QtWidgets.QVBoxLayout()
                        hbox = QtWidgets.QHBoxLayout()

                        if short_cycle is not None:
                            short_button = QtWidgets.QPushButton('Short (4 Waves)')
                            short_button.setFont(font)
                            short_button.setStyleSheet(ss)
                            short_button.setSizePolicy(sp)
                            short_button.clicked.connect(partial(self.dialog_accept, dialog))
                            hbox.addWidget(short_button)

                        if medium_cycle is not None:
                            medium_button = QtWidgets.QPushButton('Medium (7 Waves)')
                            medium_button.setFont(font)
                            medium_button.setStyleSheet(ss)
                            medium_button.setSizePolicy(sp)
                            medium_button.clicked.connect(partial(self.dialog_reject, dialog))
                            hbox.addWidget(medium_button)

                        if long_cycle is not None:
                            long_button = QtWidgets.QPushButton('Long (10 Waves)')
                            long_button.setFont(font)
                            long_button.setStyleSheet(ss)
                            long_button.setSizePolicy(sp)
                            long_button.clicked.connect(partial(self.dialog_cancel, dialog))
                            hbox.addWidget(long_button)

                        vbox.addWidget(dialog_label)
                        vbox.addLayout(hbox)
                        hbox_master.addLayout(vbox)

                        # Set up window
                        dialog.setWindowTitle('SpawnCycler')
                        dialog.setStyleSheet("background-color: rgb(40, 40, 40);")

                        # Move to x, y
                        dialog.move(x, y)
                        dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
                        dialog.exec_()
                        
                        if dialog.accepted: # Short SpawnCycle
                            target = short_cycle
                            self.json_autosave_target = 0
                        elif dialog.cancelled: # Long SpawnCycle
                            target = long_cycle
                            self.json_autosave_target = 2
                        else:
                            target = medium_cycle
                            self.json_autosave_target = 1
                    else: # Only one cycle found.
                        if short_cycle is not None:
                            target = short_cycle
                            self.json_autosave_target = 0
                        elif medium_cycle is not None:
                            target = medium_cycle
                            self.json_autosave_target = 1
                        else:
                            target = long_cycle
                            self.json_autosave_target = 2
                    
                    # Convert the JSON format back to the standard format
                    self.loaded_json = json_dict
                    lines = [f"SpawnCycleDefs={wd}" for wd in target]     

            else: # TXT-formatted SpawnCycle
                self.loaded_json = None
                self.json_autosave_target = None
                with open(filename, 'r') as f_in: 
                    lines = f_in.readlines()

        # Something went wrong!  
        except:
            # Diplay error
            diag_text = f"File '{filename}' could not be opened!\nEither the file doesn't exist, is locked, or has improper formatting."
            err_dialog = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
            err_dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            err_dialog.exec_()

            # Remove it from the recent files
            for fname in self.recent_files:
                if fname == filename:
                    self.recent_files.remove(fname)
                    self.refresh_recent_menu() # Refresh the "Recent" menu
            return

        self.add_message('Success!')

        # Now we can finally open the new file and process it.
        # The current file is 'dirty', needs saving before we populate with the new stuff
        if self.dirty:
            diag_text = 'Save changes before closing?'
            save_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y, yes_target=partial(self.save_to_file, False, False), cancel_button=True)
            save_dialog.cancel_button.clicked.connect(partial(self.dialog_cancel, save_dialog))
            save_dialog.cancelled = False
            self.active_dialog = save_dialog
            save_dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            save_dialog.exec_()
            if save_dialog.cancelled:
                self.add_message(f"Save cancelled.") # Post a message
                return
        self.active_dialog = None

        self.add_message(f"Attempting to parse file '{filename}'..") # Post a message
        # Parse the file to check for errors
        errors = parse.parse_syntax_import(filename, lines)
        if len(errors) > 0:
            self.add_message(errors[0])
            if len(errors) > 1:
                self.add_message('\n\n'.join([e.replace(f"Parse errors ('{filename}'):\n\n", '') for e in errors[1:]]), prefix=False)
            diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
            diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            diag.exec_() # Show a dialog to tell user to check messages
            return

        # Update the "Recent Files" menu
        self.add_filename_to_recent(filename)

        # Reset everything!
        self.reset_state()
        self.add_message(f"Parse successful!") # Post a message
        self.filename = filename

        # Show "Loading" dialog
        diag_title = 'Loading..'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 90 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
        diag_text = f"Loading.."
        loading_diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=False)
        loading_diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
        loading_diag.show() # Show a dialog to tell user to check messages

        # Convert lines into iterable waves
        waves = []
        for line in lines:
            line = line.replace(' ', '').replace('SpawnCycleDefs=', '').replace('\n', '')
            if len(line) > 0:
                squads = [parse.format_squad(squad) for squad in line.split(',')] # Convert squads to dict format
            else:
                squads = []
            waves.append(squads)

        num_waves, num_squads, num_zeds = self.populate_waves(waves) # Load up the waves!
        self.dirty = False # Not dirty after freshly loading a file
        self.add_message(f"Successfully loaded {len(self.wavedefs)} waves, {num_squads:,d} squads, {num_zeds:,d} zeds from file '{filename}'.") # Post a message

        loading_diag.close()

        # Reset scrollbars
        vbar = self.wavedefs_scrollarea.verticalScrollBar()
        vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.minimum()))
        hbar = self.wavedefs_scrollarea.horizontalScrollBar()
        hbar.rangeChanged.connect(lambda: hbar.setValue(hbar.minimum()))

        # Set new window title
        self.set_window_title(f"SpawnCycler ({self.truncate_filename(self.filename)})")

        # Check if analyze window is open and change the label
        if self.analyze_dialog is not None:
            truncated = self.truncate_filename(self.filename)
            file_ext = self.get_file_ext(truncated)
            self.analyze_dialog.ui.reset_state()
            self.analyze_dialog.ui.results_label.setText(f"Analysis Results{'' if file_ext is None else (' (' + truncated.replace(file_ext, '') + ')')}")

    # Closes the file and resets everything
    def close_file(self):
        # Dialog stuff
        diag_title = 'Close File'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()

        # Now we can finally open the new file and process it.
        # The current file is 'dirty', needs saving before we populate with the new stuff
        if self.dirty:
            diag_text = 'Save changes before closing?'
            save_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y, yes_target=partial(self.save_to_file, False, False), cancel_button=True)
            save_dialog.cancel_button.clicked.connect(partial(self.dialog_cancel, save_dialog))
            save_dialog.cancelled = False
            self.active_dialog = save_dialog
            save_dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            save_dialog.exec_()
            if save_dialog.cancelled: # User pressed cancel
                self.add_message(f"Save cancelled.") # Post a message
                return
        self.active_dialog = None
        self.reset_state()

        # Check if analyze window is open and change the label and reset state
        if self.analyze_dialog is not None:
            self.analyze_dialog.ui.reset_state()

    def handle_dialog_field(self):
        field = self.active_dialog.author_field
        button = self.active_dialog.yes_button

        if field.text() == '':
            button.setEnabled(False)
        else:
            button.setEnabled(True)

    # Saves the file to the disk
    def save_to_file(self, file_browser=True, autosave=False):
        # We can only autosave under the following conditions:
        # 1. Autosaving is enabled
        # 2. The file has a name
        # 3. The file is dirty and actually requires saving
        if autosave and (not meta.get_keyvalue('autosave_enabled') or self.filename == 'Untitled' or not self.dirty):
            return

        # Dialog stuff
        diag_title = 'SpawnCycler'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()

        fname = f" ('{self.filename}')" if self.filename != 'Untitled' else ''
        self.add_message(f"Attempting to parse file{fname.replace('(','').replace(')','')}..") # Post a message

        # Parse the file to check for errors
        errors = parse.parse_syntax_export(self.filename, self.wavedefs)
        if not autosave and len(errors) > 0:
            self.add_message(errors[0])
            if len(errors) > 1:
                self.add_message('\n\n'.join([e.replace(f"Parse errors{fname}:\n\n", '') for e in errors[1:]]), prefix=False)
            diag_text = f'{len(errors)} syntax error(s) were encountered.\nFile could not be saved.\nSee the Messages box below for more details.'
            diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            diag.exec_() # Show a dialog to tell user to check messages
            return

        # Warn the user if they do not have a cycle of the appropriate length (4/7/10) unless they suppress the warning
        if not autosave and len(self.wavedefs) not in [4, 7, 10] and meta.get_keyvalue('should_warn_cyclelength'):
            diag_title = 'WARNING'
            diag_text = f"\nYour SpawnCycle was found to contain {len(self.wavedefs)} wave(s).\nCD mandates that SpawnCycles contain 4, 7, or 10 waves.\n\nIf you continue, your SpawnCycle will not load in-game!\n"
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-200 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True, checkbox=True)
            diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))

            diag.exec_() # Show the dialog

            # Check if the user clicked "Don't show this again"
            if diag.checkbox.checkState(): # We know this will exist since checkbox=True
                meta.set_keyvalue('should_warn_cyclelength', False) # Don't ever show the dialog again

        # Warn the user if they have empty waves
        num_empty = sum([1 if len(wave['Squads']) <= 0 else 0 for wave in self.wavedefs])
        if not autosave and num_empty > 0 and meta.get_keyvalue('should_warn_emptywaves'):
            diag_title = 'WARNING'
            diag_text = f"\nYour SpawnCycle was found to contain {num_empty} empty wave(s).\n\nIf you continue, your SpawnCycle will not load in-game!\n"
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-200 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True, checkbox=True)
            diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))

            diag.exec_() # Show the dialog

            # Check if the user clicked "Don't show this again"
            if diag.checkbox.checkState(): # We know this will exist since checkbox=True
                meta.set_keyvalue('should_warn_emptywaves', False) # Don't ever show the dialog again

        # Ask user for filename to save as
        if file_browser or self.filename == 'Untitled':
            # Figure out the filetype to show
            preferred_filetype = meta.get_keyvalue('save_default_filetype')
            if preferred_filetype == 1: # txt
                filetype = 'Standard SpawnCycle (*.txt);;FMX SpawnCycle (*.json)'
            elif preferred_filetype == 2: # json
                filetype = 'FMX SpawnCycle (*.json);;Standard SpawnCycle (*.txt)'
            else: # Adaptive (default behavior)
                filetype = 'Standard SpawnCycle (*.txt);;FMX SpawnCycle (*.json)' if '.json' not in self.filename.lower() else 'FMX SpawnCycle (*.json);;Standard SpawnCycle (*.txt)'

            filename, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File As', '', filetype)
            if filename == '': # Leave if the user cancelled
                self.add_message(f"Save cancelled.") # Post a message
                return
        else:
            filename = self.filename

        # Show "Autosaving.."" dialog
        if autosave:
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 90 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            autosave_diag = widget_helpers.create_simple_dialog(self.central_widget, 'Autosaving..', 'Autosaving..', x, y, button=False)
            autosave_diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            autosave_diag.show() # Show a dialog to tell user to check messages

        # JSON: Need to get the author if none has been specified before (this is a new file)
        if not autosave and '.json' in filename.lower() and self.loaded_json is None:
            # We need to get the author and title, but only if its a manual save
            diag_title = 'SpawnCycler'
            diag_text = 'Please specify an Author for this SpawnCycle:'
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            author_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y, no=False, cancel_button=True)
            author_dialog.yes_button.setText("OK")
            author_dialog.yes_button.clicked.connect(partial(self.dialog_accept, author_dialog))
            author_dialog.yes_button.setEnabled(False)
            author_dialog.cancel_button.clicked.connect(partial(self.dialog_cancel, author_dialog))
            self.active_dialog = author_dialog
            author_dialog.cancelled = False

            # Create "Author" Label and Textbox
            ss = 'color: rgb(255, 255, 255);' # Stylesheet
            sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sp.setHorizontalStretch(0)
            sp.setVerticalStretch(0)
            font_textfield = QtGui.QFont()
            font_textfield.setFamily(_DEF_FONT_FAMILY)
            font_textfield.setPointSize(10)
            font_textfield.setWeight(75)
            
            author_dialog.author_field = QtWidgets.QLineEdit()
            author_dialog.author_field.setStyleSheet(ss)
            author_dialog.author_field.setSizePolicy(sp)
            author_dialog.author_field.setMaximumSize(QtCore.QSize(256, 28))
            author_dialog.author_field.setFont(font_textfield)
            author_dialog.author_field.setText('')
            author_dialog.author_field.setAlignment(QtCore.Qt.AlignLeft)
            author_dialog.author_field.setStyleSheet('color: rgb(255, 255, 255); background-color: rgb(60, 60, 60);')
            author_dialog.layout.insertWidget(1, author_dialog.author_field)

            author_dialog.author_field.textChanged.connect(self.handle_dialog_field)
            
            # Exec the dialog
            author_dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            author_dialog.exec_()

            if author_dialog.cancelled: # User hit 'Cancel'
                self.add_message(f"Save cancelled.") # Post a message
                return
            if author_dialog.accepted: # User hit OK
                self.loaded_json = {"Name": filename.lower().replace('.json', ''), "Author": author_dialog.author_field.text(), "Date": str(date.today()), "ShortSpawnCycle": [], "NormalSpawnCycle": [], "LongSpawnCycle": []} # Set this file up for saving
                author_dialog.close()
                self.active_dialog = None
                
        if '.json' not in filename.lower():
            self.loaded_json = None

        if autosave:
            self.add_message(f"Autosave initiated.") # Post a message
        self.add_message(f"Parse successful!") # Post a message

        # Save the file
        if self.loaded_json is None: # Saving TXT
            line_pfx = 'SpawnCycleDefs='
            with open(filename.lower(), 'w') as f:
                waves = []
                for wavedef in self.wavedefs:
                    wave_squads = []
                    for squad in wavedef['Squads']:
                        squad_zeds = [f"{zed_data['Count']}{zed_ids[zed_id]}" for (zed_id, zed_data) in squad['ZEDs'].items()]
                        wave_squads.append('_'.join(squad_zeds))
                    waves.append(f"{line_pfx}{','.join(wave_squads)}")
                f.write('\n'.join(waves))

        else: # Saving JSON
            # Create the SpawnCycle json
            cycle_list = []
            for wavedef in self.wavedefs:
                wave_squads = []
                for squad in wavedef['Squads']:
                    squad_zeds = [f"{zed_data['Count']}{zed_ids[zed_id]}" for (zed_id, zed_data) in squad['ZEDs'].items()]
                    wave_squads.append('_'.join(squad_zeds))
                cycle_list.append(f"{','.join(wave_squads)}")

            # Now save to the file
            with open(filename.lower(), 'w') as f:
                default_target = meta.get_keyvalue('save_json_default_target')

                if autosave: # Specific case for autosave
                    # Short was the last thing we opened or saved AND we have room
                    if self.json_autosave_target == 0 and len(self.wavedefs) <= 4:
                        target = 'ShortSpawnCycle'
                        self.add_message(f"Autosaving to Short SpawnCycle slot since this slot was last saved to or opened from...")

                    # Medium was the last thing we opened or saved AND we have room
                    elif self.json_autosave_target == 1 and len(self.wavedefs) <= 7:
                        target = 'NormalSpawnCycle'
                        self.add_message(f"Autosaving to Medium SpawnCycle slot since this slot was last saved to or opened from...")

                    # Long was the last thing we opened or saved AND we have room
                    elif self.json_autosave_target == 2:
                        target = 'LongSpawnCycle'
                        self.add_message(f"Autosaving to Long SpawnCycle slot since this slot was last saved to or opened from...")

                    # Our new cycle doesn't fit in the same spot we loaded from or last saved to. Use the adaptive setup
                    else:
                        if len(self.wavedefs) in [1, 2, 3, 4]:
                            target = 'ShortSpawnCycle'
                            self.json_autosave_target = 0
                            self.add_message(f"WARNING: Autosave data saved to Short SpawnCycle slot due to the new data not being compatible with the last used location...")
                        elif len(self.wavedefs) in [5, 6, 7]:
                            target = 'NormalSpawnCycle'
                            self.json_autosave_target = 1
                            self.add_message(f"WARNING: Autosave data saved to Medium SpawnCycle slot due to the new data not being compatible with the last used location...")  
                        else:
                            target = 'LongSpawnCycle'
                            self.json_autosave_target = 2
                            self.add_message(f"WARNING: Autosave data saved to Long SpawnCycle slot due to the new data not being compatible with the last used location...")
                        
                elif default_target == 0: # Always Ask
                    if len(self.wavedefs) <= 7: # No need to ask if we don't even have multiple targets to begin with
                        # Create dialog
                        font = QtGui.QFont()
                        font.setPointSize(8)
                        font.setBold(True)
                        ss = "color: rgb(255, 255, 255);"
                        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
                        sp.setHorizontalStretch(0)
                        sp.setVerticalStretch(0)
                        dialog = QtWidgets.QDialog()
                        dialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint|QtCore.Qt.WindowTitleHint) # Disable X and minimize
                        dialog.cancelled = False
                        dialog.accepted = False
                        hbox_master = QtWidgets.QHBoxLayout(dialog)

                        # Set up text label
                        dialog_label = QtWidgets.QLabel(dialog)
                        dialog_label.setFont(font)
                        dialog_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
                        dialog_label.setStyleSheet(ss)
                        dialog_label.setText('This SpawnCycle format supports multiple GameLengths.\nPlease select a GameLength to save the data to:\n')

                        # Set layout
                        vbox = QtWidgets.QVBoxLayout()
                        hbox = QtWidgets.QHBoxLayout()
                        
                        if len(self.wavedefs) <= 4: # Short is only a viable target if the cycle would fit
                            short_button = QtWidgets.QPushButton('Short (4 Waves)')
                            short_button.setFont(font)
                            short_button.setStyleSheet(ss)
                            short_button.setSizePolicy(sp)
                            short_button.clicked.connect(partial(self.dialog_accept, dialog))
                            hbox.addWidget(short_button)

                        # 7 waves is always a viable target
                        medium_button = QtWidgets.QPushButton('Medium (7 Waves)')
                        medium_button.setFont(font)
                        medium_button.setStyleSheet(ss)
                        medium_button.setSizePolicy(sp)
                        medium_button.clicked.connect(partial(self.dialog_reject, dialog))
                        hbox.addWidget(medium_button)

                        # 10 waves is always a viable target
                        long_button = QtWidgets.QPushButton('Long (10 Waves)')
                        long_button.setFont(font)
                        long_button.setStyleSheet(ss)
                        long_button.setSizePolicy(sp)
                        long_button.clicked.connect(partial(self.dialog_cancel, dialog))
                        hbox.addWidget(long_button)

                        # Finalize layout
                        vbox.addWidget(dialog_label)
                        vbox.addLayout(hbox)
                        hbox_master.addLayout(vbox)

                        # Set up window
                        dialog.setWindowTitle('SpawnCycler')
                        dialog.setStyleSheet("background-color: rgb(40, 40, 40);")

                        # Move to x, y
                        dialog.move(x, y)
                        dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
                        dialog.exec_()                    

                        if dialog.accepted: # Short SpawnCycle
                            target = 'ShortSpawnCycle'
                            self.json_autosave_target = 0
                        elif dialog.cancelled: # Long SpawnCycle
                            target = 'LongSpawnCycle'
                            self.json_autosave_target = 2
                        else:
                            target = 'NormalSpawnCycle'
                            self.json_autosave_target = 1
                    else:
                        target = 'LongSpawnCycle'
                        self.json_autosave_target = 2

                elif default_target == 2 and len(self.wavedefs) <= 7: # Preferred Medium
                    target = 'NormalSpawnCycle'
                    self.json_autosave_target = 1

                elif default_target == 3: # Preferred Long
                    target = 'LongSpawnCycle'
                    self.json_autosave_target = 2

                else: # Adaptive. Target the length based on how many waves are defined
                    if len(self.wavedefs) in [8, 9, 10]:
                        target = 'LongSpawnCycle'
                        self.json_autosave_target = 2
                    elif len(self.wavedefs) in [5, 6, 7]:
                        target = 'NormalSpawnCycle'
                        self.json_autosave_target = 1
                    else:
                        target = 'ShortSpawnCycle'
                        self.json_autosave_target = 0

                k = len(filename) - 1
                json_filename = None
                while k >= 0:
                    if filename[k] == '/':
                        json_filename = filename[k+1:]
                        break
                    k -= 1

                if json_filename is None:
                    json_filename = filename

                # Update the json data
                self.loaded_json.update({target: cycle_list})
                self.loaded_json.update({'Date': str(date.today())})
                self.loaded_json.update({'Name': json_filename.lower().replace('.json', '')})

                f.write(json.dumps(self.loaded_json))

        # Update the "Recent Files" menu
        self.add_filename_to_recent(filename)

        # Output the results to the message box
        num_squads = sum([len(w['Squads']) for w in self.wavedefs])
        num_zeds = 0
        for w in self.wavedefs:
            for s in w['Squads']:
                for z in s['ZEDs'].values():
                    num_zeds += z['Count']
        self.add_message(f"Successfully wrote {len(self.wavedefs)} waves, {num_squads:,d} squads, {num_zeds:,d} zeds to file '{filename}'.") # Post a message

        # File isn't dirty anymore
        self.dirty = False
        self.filename = filename # Set window title
        self.set_window_title('SpawnCycler (' + self.truncate_filename(self.filename) + ')')

        if self.active_dialog is not None: # We came from a dialog to get here. Close it
            self.active_dialog.close()

        if autosave: # Close the "Autosaving" dialog
            autosave_diag.close()

    # Resets everything back to normal
    def reset_state(self):
        self.dirty = False # Reset dirty status
        self.clear_wavedefs() # Delete all waves
        #self.clear_messages() # Delete all messages

        # Re-add the "Add Wave" button
        sp_button = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_button.setHorizontalStretch(0)
        sp_button.setVerticalStretch(0)
        font_button = QtGui.QFont()
        font_button.setFamily(_DEF_FONT_FAMILY)
        font_button.setPointSize(12)
        font_button.setBold(True)
        font_button.setWeight(75)
        ss_button = 'QToolTip {color: rgb(0, 0, 0);\nbackground-color: rgb(40, 40, 40);}' # Stylesheet
        button_addwave = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Add Wave', target=self.add_wavedef, text=' Add Wave', tooltip='Add a new wave to the SpawnCycle', style=ss_button, icon_path='img/icon_add.png', icon_w=16, icon_h=16, font=font_button, size_policy=sp_button, draggable=False)
        self.wavedefs_scrollarea_layout.setAlignment(QtCore.Qt.AlignTop)
        self.wavedefs_scrollarea_layout.addWidget(button_addwave)
        self.buttons.update({'Add Wave' : button_addwave})

        # Reset scrollbars
        vbar = self.wavedefs_scrollarea.verticalScrollBar()
        vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.minimum()))
        hbar = self.wavedefs_scrollarea.horizontalScrollBar()
        hbar.rangeChanged.connect(lambda: hbar.setValue(hbar.minimum()))

        # Reset dirty status
        self.dirty = False
        self.filename = 'Untitled'
        self.set_window_title(f'SpawnCycler (Untitled)') # Only if file is named though

    def setupUi(self, MainWindow):
        # Set up main window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(_WINDOWSIZE_MAIN_W, _WINDOWSIZE_MAIN_H)
        MainWindow.setStyleSheet("background-color: rgb(50, 50, 50);")
        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName("central_widget")
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.central_layout.setObjectName("central_layout")
        
        # Set up main area (the two columns)
        self.main_area = QtWidgets.QHBoxLayout()
        self.main_area.setObjectName("main_area")

        self.setup_options_pane() # Set up the options pane
        self.setup_wavedefs() # Set up the WaveDefs
        self.setup_messages() # Set up the Messages pane
        self.setup_zed_pane() # Set up the ZED pane

        # Finalize main window
        MainWindow.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1172, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Post initial message
        init_msg = (f"Welcome to SpawnCycler!\n\n"
                    f"To get started, click 'Add Wave' and simply drag-and-drop ZEDs from the right-hand pane to form Squads!\n"
                    f"A Squad is a group of ZEDs which CD will attempt to spawn (in order) as it reads through the SpawnCycle.\n\n"
                    f"To remove ZEDs from a Squad, simply drag the ZED out of the Squad and onto the empty background or press the \"-\" button under the ZED's icon.\n"
                    f"ZEDs can also be dragged between waves and Squads, by simply holding MOUSE1 (LMB) and dragging the icon.\n"
                    f"You can perform more actions by using MOUSE2 (RMB) on a ZED icon within a Squad.\n\n"
                    f"With this tool, you can create your own SpawnCycle, Import and alter other SpawnCycles, and even Generate SpawnCycles based on pre-determined criteria.\n"
                    f"The Analyze feature allows you to simulate the SpawnCycle and generate detailed summary information on a per-wave basis, including the number of ZEDs spawned and a difficulty estimate.\n\n"
                    f"Enjoy!\n")
        self.add_message(init_msg)

    # Sets the window title
    def set_window_title(self, title):
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate('SpawnCycler', title))

    # Opens the specified dialog
    def open_dialog(self, diag_type, title):
        # Convert
        if diag_type == 'convert':
            dialog = QtWidgets.QDialog(None, QtCore.Qt.WindowCloseButtonHint)
            dialog.ui = ConvertDialog()
            dialog.ui.setupUi(dialog)

        # Settings
        elif diag_type == 'settings':
            dialog = QtWidgets.QDialog(None, QtCore.Qt.WindowCloseButtonHint)
            dialog.ui = SettingsDialog(self)
            dialog.ui.setupUi(dialog)

        # Generate
        elif diag_type == 'generate':
            dialog = widget_helpers.CustomDialog(None, QtCore.Qt.WindowCloseButtonHint)
            dialog.ui = GenerateDialog(self, dialog)
            dialog.ui.setupUi()
            self.generate_dialog = dialog

        # Analyze
        elif diag_type == 'analyze':
            # Only open an analysis window if one isn't open already
            if self.analyze_dialog is not None:
                return

            # Open the dialog
            dialog = widget_helpers.CustomDialog(None, QtCore.Qt.WindowCloseButtonHint)
            dialog.ui = AnalyzeDialog(self)
            dialog.ui.setupUi(dialog)
            self.analyze_dialog = dialog

        # About
        else:
            dialog = QtWidgets.QDialog(None, QtCore.Qt.WindowCloseButtonHint)
            dialog.ui = AboutDialog()
            dialog.ui.setupUi(dialog)
        
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(QtGui.QIcon('img/logo.png'))

        # For the analysis window we don't want to block access to the rest of the program
        if diag_type in ['analyze']:
            dialog.show() # Non-blocking
        else:
            dialog.exec_()

    # Updates the "Recent Files" menu
    def add_filename_to_recent(self, filename):
        meta_dict = meta.get_metadict()

        if len(self.recent_files) == 0: # Special case: no recents. 
            self.recent_menu.removeAction(self.recent_menu.actions()[0]) # Remove the 'No files found'

        if filename in self.recent_files: # We've already recently opened this file
            self.recent_files.remove(filename) # Remove the old one
        else: # Never opened this file recently. Need to add it to the list
            if len(self.recent_files) == _RECENT_MAX: # Full. Need to pop one of the recent files out of the list
                self.recent_files.pop(-1)

        self.recent_files.insert(0, filename) # Add it to the "Recent Files" list
        
        # Save metadata
        meta.set_keyvalue('recent_files', self.recent_files)
        self.refresh_recent_menu() # Refresh the "Recent" menu

    def get_zed_mode(self):
        return self.zed_mode

    # Removes the path from the file, so only the filename.extension is left
    def truncate_filename(self, fname):
        if '/' not in fname:
            return fname
        i = -1
        while fname[i] != '/':
            i -= 1
        return fname[i+1:]

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle('SpawnCycler (Untitled)')
        MainWindow.setWindowIcon(QtGui.QIcon('img/logo.png'))

        self.switch_zed_mode() # Swap it to normal mode


# Custom MainWindow that calls an event when closed
class CustomMainWindow(QtWidgets.QMainWindow):
    # This function is called when the user presses the X (close) button
    def closeEvent(self, event):
        if self.ui.dirty: # File needs to be saved first
            diag_title = 'SpawnCycler'
            diag_text = 'Save changes before closing?'
            x = self.ui.central_widget.mapToGlobal(self.ui.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
            y = self.ui.central_widget.mapToGlobal(self.ui.central_widget.rect().center()).y()
            save_dialog = widget_helpers.create_choice_dialog(self.ui.central_widget, diag_title, diag_text, x, y, yes_target=partial(self.ui.save_to_file, False, False))
            self.ui.active_dialog = save_dialog
            save_dialog.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            save_dialog.exec_()

        # Close analysis window if open
        if self.ui.analyze_dialog is not None:
            self.ui.analyze_dialog.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = CustomMainWindow()
    ui = Ui_MainWindow(app)
    ui.setupUi(MainWindow)
    MainWindow.ui = ui
    MainWindow.show()
    sys.exit(app.exec_())

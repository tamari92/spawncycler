#
#  SpawnCycler.py
#
#  Author: Tamari (Nathan P. Ybanez)
#  Date of creation: 11/14/2020
#
#  Main code base for SpawnCycler
#

from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
from functools import partial
from copy import deepcopy
from about import *
from analyze import *
from generate import *
import os
import json
import parse
import random
import widget_helpers

#import threading
#import cgitb 
#cgitb.enable(format = 'text')

# Things I could add maybe:
# 1. AutoSave?

_DEF_FONT_FAMILY = 'Consolas'
_RECENT_MAX = 5 # Max "Recent Files"
_WAVE_MAX = 10  # Max number of waves
_SQUAD_MAX = 10  # Max ZEDs in a squad
has_swapped_modes = False # Has the user swapped ZED modes yet?

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
           'Scrake': 'SC',
           'Quarter Pound': 'MF',
           'Quarter Pound (Enraged)': 'MF!',
           'Fleshpound': 'FP',
           'Fleshpound (Enraged)': 'FP!',
           'Alpha Scrake': 'SC*',
           'Alpha Fleshpound': 'FP*',
           'Alpha Fleshpound (Enraged)': 'FP*!',
           'Dr. Hans Volter': 'HV',
           'Patriarch': 'PT',
           'Matriarch': 'MT',
           'King Fleshpound': 'KF',
           'Abomination': 'AB',
           'Abomination Spawn': 'AS'}


def resource_path(relative_path):
    #return relative_path
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    print(f'returning {os.path.join(base_path, relative_path)}')
    return os.path.join(base_path, relative_path)


# Represents a RGB color
class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"({self.r}, {self.g}, {self.b})"


class Ui_MainWindow(object):
    def __init__(self, app):
        self.app = app
        self.zed_mode = 'Custom'
        self.save_dialog = None
        self.last_generate_preset = None # Last preset used in the Generate dialog
        self.last_generate_mode = None # Last used zed mode in the Generate dialog
        self.last_analyze_preset = None # Last preset used in the Analyze dialog
        

    # Switches from Default to Custom zed set
    def switch_zed_mode(self, should_warn=True):
        if self.zed_mode == 'Custom':
            # Need to remove all the custom zeds from the grid
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

            for button in self.zed_pane_buttons.values():
                button.setIconSize(QtCore.QSize(48, 48));

            # Update button
            self.buttons['Switch ZEDs'].setText(' Custom')
            self.default_replace_menu.menuAction().setVisible(True)
            self.custom_replace_menu.menuAction().setVisible(False)
            self.zed_mode = 'Default'
            self.refresh_wavedefs()
        else:
            global has_swapped_modes
            if should_warn:
                if not has_swapped_modes:
                    diag_title = 'WARNING'
                    diag_text = '\nThe Custom ZED set is NOT supported by most Controlled Difficulty builds.\nUsing these ZEDs may break your SpawnCycle on those builds.\n\nUse at your own risk!\n'
                    x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-200 # Anchor dialog to center of window
                    y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
                    diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
                    diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
                    diag.exec_() # Show a dialog to tell user to check messages
                    has_swapped_modes = True # Never show this message again
            else:
                has_swapped_modes = True

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
            self.buttons['Switch ZEDs'].setText(' Default')
            self.default_replace_menu.menuAction().setVisible(False)
            self.custom_replace_menu.menuAction().setVisible(True)
            self.zed_mode = 'Custom'
            self.refresh_wavedefs()

    # Removes the ZED from the given squad
    def remove_zed_from_squad(self, wave_id, squad_id, zed_id, count=1):
        this_squad = self.wavedefs[wave_id]['Squads'][squad_id]
        #print(f"(Before deletion) Squads for Wave {wave_id+1}:\n{self.wavedefs[wave_id]}")
        squad_layout = this_squad['Layout'] # Get the layout corresponding to this wave's squad box

        #print(f"zed = {zed_id}")
        #print(f"wave_id = {wave_id}")
        #print(f"squad_id = {squad_id}")
        #print('\n\nThis squad (before)')
        #print(this_squad)
        #print('\nSquads before:')
        #print(self.wavedefs[wave_id]['Squads'])

        # Update the internal array and numerical display
        if count != 'all' and this_squad['ZEDs'][zed_id]['Count'] > 1:
            this_squad['ZEDs'][zed_id]['Count'] -= 1
            if 'Enraged' in zed_id:
                this_squad['ZEDs'][zed_id]['Children']['Label'].setText(str(this_squad['ZEDs'][zed_id]['Count']) + ' !')
            else:
                this_squad['ZEDs'][zed_id]['Children']['Label'].setText(str(this_squad['ZEDs'][zed_id]['Count']))
        else: # Last ZED of its type in the squad. Teardown the zed frame
            this_squad['ZEDs'][zed_id]['Children']['Label'].setParent(None)
            this_squad['ZEDs'][zed_id]['Children']['Button'].setParent(None)
            this_squad['ZEDs'][zed_id]['Frame'].setParent(None) # Disassociate the widgets 
            del this_squad['ZEDs'][zed_id]

        #print(f"Removed {zed_id} from Squad {squad_id+1} in Wave {wave_id+1}")
        #print(f"(After deletion) Squads for Wave {wave_id+1}:\n{self.wavedefs[wave_id]}")

        # Is this the last squad in the entire wave?
        if len(this_squad['ZEDs'].keys()) > 0:
            this_squad['Frame'].is_full = False
            this_squad['Frame'].setToolTip('')
            widget_helpers.set_plain_border(this_squad['Frame'], Color(255, 255, 255), 2)
        else: # Last ZED in entire squad. We need to remove the entire Squad Frame too
            this_squad['Layout'].setParent(None)
            this_squad['Frame'].setParent(None)
            self.wavedefs[wave_id]['Squads'].pop(squad_id)
            print(self.wavedefs[wave_id])
            
        #print('\n\nThis squad (after)')
        #print(this_squad)
        
        #print('Squads after:')
        #print(self.wavedefs[wave_id]['Squads'])

        self.refresh_wavedefs() # Need to refresh everything
        
        # The file is now 'dirty'
        self.dirty = True
        if self.filename != 'Untitled': # Change filename to reflect
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)') # Only if file is named though

    # Creates a new frame for a ZED in a squad (holding the icon and number)
    def create_zed_frame(self, parent, zed_button):
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(12)
        font_label.setWeight(75)
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        ss_label = 'color: rgb(255, 255, 255);' # Stylesheet

        # Create the frame
        zed_frame = QtWidgets.QFrame(parent)
        zed_frame.setSizePolicy(sp)
        zed_frame.setMinimumSize(QtCore.QSize(1, 1))
        zed_frame_layout = QtWidgets.QVBoxLayout(zed_frame) # Add layout
        zed_frame.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

        # Create label
        zed_label = widget_helpers.create_label(zed_frame, text='1', style=ss_label, font=font_label)
        zed_label.setAlignment(QtCore.Qt.AlignCenter)

        # Put it all together
        zed_frame_layout.addWidget(zed_button)
        zed_frame_layout.addWidget(zed_label)
        zed_frame_layout.setSpacing(0)

        return zed_frame, {'Button': zed_button, 'Label': zed_label}

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
        squad_frame = widget_helpers.QFrame_Drag(self.wavedefs[wave_id]['Frames']['SquadFrame'], id=len(self.wavedefs[wave_id]['Squads']), squad=True)
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
        zed_frame, zed_frame_children = self.create_zed_frame(squad_frame, zed_button)
        if raged:
            zed_frame_children['Label'].setText(str(count) + ' !')
            zed_frame_children['Label'].setStyleSheet("color: rgb(255, 55, 55);")
            zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid red;}")
        else:
            zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid white;}")
            zed_frame_children['Label'].setText(str(count))

        # Add the widgets
        squad_frame_layout.addWidget(zed_frame)
        wave_layout.addWidget(squad_frame)

        # Set the horizontal scrollbar to the right
        hbar = self.wavedefs_scrollarea.horizontalScrollBar()
        hbar.rangeChanged.connect(lambda: hbar.setValue(hbar.maximum()))

        self.refresh_wavedefs() # Need to refresh

        # Squad is full
        if count == _SQUAD_MAX:
            squad_frame.is_full = True # Mark as full
            squad_frame.setToolTip('This squad has reached capacity.')
            widget_helpers.set_plain_border(squad_frame, Color(245, 42, 20), 2)
            squad_frame.setStyleSheet('QToolTip {color: rgb(0, 0, 0)}\nQFrame_Drag {color: rgb(255, 0, 0); background-color: rgba(150, 0, 0, 30);}')
            #squad_frame.anim.start()

        # Update the internal array
        #print(f"Added new squad ({len(self.wavedefs[wave_id]['Squads'])}) to Wave {wave_id+1}")
        self.wavedefs[wave_id]['Squads'].append({'Frame': squad_frame, 'Layout': squad_frame_layout, 'ZEDs': {zed_id: {'Count': count, 'Raged': raged, 'Frame': zed_frame, 'Children': zed_frame_children}}})
        #print(f"Squads for Wave {wave_id+1}")
        #for s in self.wavedefs[wave_id]['Squads']:
            #print(s)

        # The file is now 'dirty'
        self.dirty = True
        if self.filename != 'Untitled': # Change filename to reflect
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)') # Only if file is named though

    # Adds a new ZED to the given squad
    def add_zed_to_squad(self, wave_id, squad_id, zed_id, count=1, raged=False):
        #print(zed_id)
        this_squad = self.wavedefs[wave_id]['Squads'][squad_id]
        squad_layout = this_squad['Layout'] # Get the layout corresponding to this wave's squad box

        # Squad is full, disallow.
        if this_squad['Frame'].is_full:
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
        #print(f"Added {zed_id} to Squad {squad_id+1} in Wave {wave_id+1}")
        if zed_id in this_squad['ZEDs']:
            this_squad['ZEDs'][zed_id]['Count'] += count
            if raged:
                this_squad['ZEDs'][zed_id]['Children']['Label'].setText(str(this_squad['ZEDs'][zed_id]['Count']) + ' !')
            else:
                this_squad['ZEDs'][zed_id]['Children']['Label'].setText(str(this_squad['ZEDs'][zed_id]['Count']))
        else: # Zed isn't in the squad yet
            zed_frame, zed_frame_children = self.create_zed_frame(this_squad['Frame'], zed_button)

            if raged: # Mark spawn raged FP
                zed_frame_children['Label'].setStyleSheet("color: rgb(255, 55, 55);")
                zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid red;}")
                zed_frame_children['Label'].setText(str(count) + ' !')
            else:
                zed_frame_children['Button'].setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQSquadButton {border: 2px solid white;}")
                zed_frame_children['Label'].setText(str(count))

            this_squad['ZEDs'][zed_id] = {'Count': count, 'Raged': raged, 'Frame': zed_frame, 'Children': zed_frame_children}
            squad_layout.addWidget(zed_frame)

        #print(f"Squads for Wave {wave_id+1}:\n{self.wavedefs[wave_id]['Squads']}")
        zed_button.squad_uid = this_squad['Frame'].unique_id

        # Has this squad reached capacity?
        total_zeds = sum([x['Count'] for x in this_squad['ZEDs'].values()])
        if total_zeds == _SQUAD_MAX:
            this_squad['Frame'].is_full = True # Mark as full
            this_squad['Frame'].setToolTip('This squad has reached capacity.')
            widget_helpers.set_plain_border(this_squad['Frame'], Color(245, 42, 20), 2)
            this_squad['Frame'].setStyleSheet('QToolTip {color: rgb(0, 0, 0)}\nQFrame_Drag {color: rgb(255, 0, 0); background-color: rgba(150, 0, 0, 30);}')
            #this_squad['Frame'].anim.start()

        self.refresh_wavedefs() # Need to refresh

        # The file is now 'dirty'
        self.dirty = True
        if self.filename != 'Untitled': # Change filename to reflect
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)') # Only if file is named though

    # Refreshes all wavedefs by correcting their numbering and functions
    def refresh_wavedefs(self):
        for i in range(len(self.wavedefs)):
            thisdef = self.wavedefs[i]
            # Shift indices
            thisdef['ID'] = i
            thisdef['Frames']['WaveFrame'].id = i
            thisdef['Frames']['SquadFrame'].id = i
            thisdef['Label'].setText(thisdef['Label'].text().split()[0] + f" {thisdef['Frames']['WaveFrame'].id+1}")

            # Shift option button targets to match the new wave
            shiftup_button = thisdef['OptionsButtons']['Shift Up']
            shiftdn_button = thisdef['OptionsButtons']['Shift Down']
            delete_button = thisdef['OptionsButtons']['Delete']
            widget_helpers.button_changetarget(shiftup_button, partial(self.shift_wavedef, thisdef['Frames']['WaveFrame'], 'up'))
            widget_helpers.button_changetarget(shiftdn_button, partial(self.shift_wavedef, thisdef['Frames']['WaveFrame'], 'down'))
            widget_helpers.button_changetarget(delete_button, partial(self.remove_wavedef, i, True))

            # Refresh squad wave ids
            for squad in self.wavedefs[i]['Squads']:
                squad['Frame'].wave_id = i
                for z in squad['ZEDs'].values():
                    z['Children']['Button'].wave_id = i

            # Refresh squad ids
            j = 0
            for squad in self.wavedefs[i]['Squads']:
                squad['Frame'].id = j
                for z in squad['ZEDs'].values():
                    z['Children']['Button'].squad_id = j
                    z['Children']['Button'].zed_mode = self.zed_mode
                j += 1

            # Disable Shift buttons if at the ends of the array
            # Kinda hacky but it'll work
            if i == 0:
                shiftup_button.setEnabled(False)
                shiftup_button.setToolTip('')
                widget_helpers.set_button_icon(shiftup_button, resource_path('img/icon_shiftup_off.png'), 24, 24)
            else:
                shiftup_button.setEnabled(True)
                shiftup_button.setToolTip('Shift this wave up by one')
                widget_helpers.set_button_icon(shiftup_button, resource_path('img/icon_shiftup.png'), 24, 24)

            if i == len(self.wavedefs) - 1:
                shiftdn_button.setEnabled(False)
                shiftdn_button.setToolTip('')
                widget_helpers.set_button_icon(shiftdn_button, resource_path('img/icon_shiftdown_off.png'), 24, 24)
            else:
                shiftdn_button.setEnabled(True)
                shiftdn_button.setToolTip('Shift this wave down by one')
                widget_helpers.set_button_icon(shiftdn_button, resource_path('img/icon_shiftdown.png'), 24, 24)

    # Moves the wave up or down
    def shift_wavedef(self, frame, dir=None):
        # Shift widgets
        idx_frame = self.wavedefs_scrollarea_layout.indexOf(frame)
        idx_label = idx_frame - 1

        new_idx_frame = idx_frame + 2 if dir == 'down' else idx_frame - 2;
        new_idx_label = idx_label + 2 if dir == 'down' else idx_label - 2;
        self.wavedefs_scrollarea_layout.removeWidget(self.wavedefs[frame.id]['Label']);
        self.wavedefs_scrollarea_layout.removeWidget(self.wavedefs[frame.id]['Frames']['WaveFrame']);
        self.wavedefs_scrollarea_layout.insertWidget(new_idx_label, self.wavedefs[frame.id]['Label']);
        self.wavedefs_scrollarea_layout.insertWidget(new_idx_frame, self.wavedefs[frame.id]['Frames']['WaveFrame']);

        #print('shifted ' + self.wavedefs[frame.id]['orig'] + f' {dir}')

        # Shift the array contents
        first = frame.id
        second = frame.id+1 if dir == 'down' else frame.id-1
        t = self.wavedefs[first]
        self.wavedefs[first] = self.wavedefs[second]
        self.wavedefs[second] = t
            
        self.refresh_wavedefs() # Refresh wavedefs state (update buttons, etc)
        #print([w['orig'] for w in self.wavedefs])
        #print([w['ID'] for w in self.wavedefs])
        #print([w['Frames']['WaveFrame'].id for w in self.wavedefs])
        #print([w['Frames']['SquadFrame'].id for w in self.wavedefs])
        #print(' ')

    # Deletes the wave from the list (and GUI)
    def remove_wavedef(self, id, should_warn=True):
        #print(f'deleting wave {id+1}')

        #print(self.wavedefs[id]['Squads'])
        if should_warn and len(self.wavedefs[id]['Squads']) > 0: # Wave is non-empty. Display dialog!
            diag_title = 'Delete Wave'
            diag_text = 'Are you sure you want to delete this wave?\nAll data will be lost!'
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-150 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            choice_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y)
            choice_dialog.yes_button.clicked.connect(partial(self.dialog_accept, choice_dialog))
            choice_dialog.no_button.clicked.connect(partial(self.dialog_reject, choice_dialog))
            choice_dialog.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            choice_dialog.exec_()
            if choice_dialog.accepted == False: # Didn't accept the dialog (don't delete)
                choice_dialog.setParent(None) # Remove the dialog
                return
            choice_dialog.setParent(None)

        # Remove the widgets
        self.wavedefs_scrollarea_layout.removeWidget(self.wavedefs[id]['Label']);
        self.wavedefs_scrollarea_layout.removeWidget(self.wavedefs[id]['Frames']['WaveFrame']);

        #print(f'id is {id}')
        #print('wavedefs before deletion:')
        #for i in range(len(self.wavedefs)):
        #    print({'real_index': i, 'orig': self.wavedefs[i]['orig'], 'Saved ID': self.wavedefs[i]['ID']})
        self.wavedefs[id]['Label'].setParent(None)
        self.wavedefs[id]['Frames']['SquadFrame'].setParent(None)
        self.wavedefs[id]['Frames']['WaveFrame'].setParent(None)

        self.wavedefs.pop(id) # Remove from array
        # Todo: Remove the squads as well

        #print('\nwavedefs before renumbering (after deletion):')
        #for i in range(len(self.wavedefs)):
        #    print({'real_index': i, 'orig': self.wavedefs[i]['orig'], 'Saved ID': self.wavedefs[i]['ID']})

        self.refresh_wavedefs() # Refresh wavedefs state (update buttons, etc)
        if len(self.wavedefs) < 10:
            self.buttons['Add Wave'].setVisible(True) # We can show the add button again

        # File has been modified
        self.dirty = True
        if self.filename != 'Untitled':
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)')

        #print('\nFINAL wavedefs after deletion:')
        #for i in range(len(self.wavedefs)):
        #    print({'real_index': i, 'orig': self.wavedefs[i]['orig'], 'Saved ID': self.wavedefs[i]['ID']})

        #print([w['orig'] for w in self.wavedefs])
        #print([w['ID'] for w in self.wavedefs])
        #print([w['Frames']['WaveFrame'].id for w in self.wavedefs])
        #print([w['Frames']['SquadFrame'].id for w in self.wavedefs])
        #print(' ')

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
        shiftup_button = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Shift Up', tooltip='Shift this wave upwards by one', style=ss_button, icon_path=resource_path('img/icon_shiftup.png'), icon_w=24, icon_h=24, size_policy=sp_fixed, draggable=False)
        shiftdn_button = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Shift Down', tooltip='Shift this wave downwards by one', style=ss_button, icon_path=resource_path('img/icon_shiftdown.png'), icon_w=24, icon_h=24, size_policy=sp_fixed, draggable=False)
        delete_button = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Delete', tooltip='Delete this wave', style=ss_button, icon_path=resource_path('img/icon_delete.png'), icon_w=24, icon_h=24, size_policy=sp_fixed, draggable=False)
        shiftup_button.clicked.connect(partial(self.shift_wavedef, wavedef_frame, 'up'))
        shiftdn_button.clicked.connect(partial(self.shift_wavedef, wavedef_frame, 'down'))
        delete_button.clicked.connect(partial(self.remove_wavedef, wavedef_frame.id, True))
        options_buttons = {'Shift Up': shiftup_button,
                           'Shift Down': shiftdn_button,
                           'Delete': delete_button}
        wave_options_layout.addWidget(shiftup_button)
        wave_options_layout.addWidget(shiftdn_button)
        wave_options_layout.addWidget(delete_button)

        # First add wave title label
        wavedef_label_text = f'\n        WAVE {len(self.wavedefs) + 1}' if len(self.wavedefs) > 0 else f'        WAVE {len(self.wavedefs) + 1}'
        wavedef_label = widget_helpers.create_label(self.wavedefs_scrollarea_contents, text=wavedef_label_text, style=ss, font=font_label)
        wavedef_label.setAlignment(QtCore.Qt.AlignLeft)
        wavedef_label.setSizePolicy(sp_fixed)
        self.wavedefs_scrollarea_layout.addWidget(wavedef_label)
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
            self.wavedefs_scrollarea_layout.insertWidget(0, wavedef_label)
        else:
            self.wavedefs_scrollarea_layout.insertWidget(self.wavedefs_scrollarea_layout.count()-2, wavedef_label)
        self.wavedefs_scrollarea_layout.insertWidget(self.wavedefs_scrollarea_layout.count()-1, wavedef_frame)

        # Move the vertical scrollbar to the bottom
        vbar = self.wavedefs_scrollarea.verticalScrollBar()
        vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.maximum()))

        self.wavedefs.append({'orig': chr(65+len(self.wavedefs)), 'ID': len(self.wavedefs), 'Label': wavedef_label, 'Layouts': {'SquadFrame': squads_frame_layout}, 'Frames': {'WaveFrame': wavedef_frame, 'SquadFrame': squads_frame}, 'OptionsButtons': options_buttons, 'Squads': []})

        # Final wave: hide 'Add Wave' button
        if len(self.wavedefs) == _WAVE_MAX:
            self.buttons['Add Wave'].setVisible(False)

        self.refresh_wavedefs() # Refresh wavedefs state (update buttons, etc)

        #print([w['orig'] for w in self.wavedefs])
        #print([w['ID'] for w in self.wavedefs])
        #print([w['Frames']['WaveFrame'].id for w in self.wavedefs])
        #print([w['Frames']['SquadFrame'].id for w in self.wavedefs])
        #print(' ')

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

        button_text_color = Color(255, 255, 255)
        button_bg_color = Color(40, 40, 40)
        ss = 'QPushButton {color: rgb' + str(button_text_color) + ';\nbackground-color: rgb' + str(button_bg_color) + ';}' # Stylesheet
        icon_w = 24
        icon_h = 24

        # Create options pane
        self.options_pane = QtWidgets.QHBoxLayout()
        self.options_pane.setSpacing(6)
        self.central_layout.addLayout(self.options_pane)

        # Import
        button_import = widget_helpers.create_button(self.central_widget, self.app, 'Open', text=' Open ', tooltip='Load a SpawnCycle from file', style=ss, icon_path=resource_path('img/icon_open.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
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

        try: # Try to load the meta data
            f = open('meta', 'r')
        except FileNotFoundError: # No meta found, create one
            with open('meta', 'w') as f_in:
                f_in.write(json.dumps({'Recent Files': []}))

        # Get the recent files list from the metadata
        with open('meta', 'r') as f:
            meta_dict = json.loads(f.readline())
        self.recent_files = meta_dict['Recent Files']
        self.refresh_recent_menu() # Initialize the "Recent" menu
        
        # Save File
        button_export = widget_helpers.create_button(self.central_widget, self.app, 'Save', text=' Save ', target=partial(self.save_to_file, False), tooltip='Save the current SpawnCycle', style=ss, icon_path=resource_path('img/icon_save.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_export)
        self.buttons.update({'Save' : button_export})

        # Save File As
        button_exportas = widget_helpers.create_button(self.central_widget, self.app, 'Save As', text=' Save As ', target=partial(self.save_to_file, True), tooltip='Save the current SpawnCycle with a designated name', style=ss, icon_path=resource_path('img/icon_saveas.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_exportas)
        self.buttons.update({'Save As' : button_exportas})

        # Close File
        button_close = widget_helpers.create_button(self.central_widget, self.app, 'Close', text=' Close ', target=self.close_file, tooltip='Close the current SpawnCycle', style=ss, icon_path=resource_path('img/icon_delete.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_close)
        self.buttons.update({'Close' : button_close})

        # Batch options
        button_batch = widget_helpers.create_button(self.central_widget, self.app, 'Batch', text=' Batch ', tooltip='Perform operations on the entire SpawnCycle', style=ss, icon_path=resource_path('img/icon_batch.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, options=True, draggable=False)   
        self.options_pane.addWidget(button_batch)
        self.buttons.update({'Batch' : button_batch})

        batch_menu, default_replace_menu, custom_replace_menu = self.init_batch_menu()
        self.default_replace_menu = default_replace_menu
        self.custom_replace_menu = custom_replace_menu
        button_batch.setMenu(batch_menu)
        
        # Analyze Spawncycle
        button_analyze = widget_helpers.create_button(self.central_widget, self.app, 'Analyze', text=' Analyze ', tooltip='Display SpawnCycle statistics', target=self.open_analyze_dialog, style=ss, icon_path=resource_path('img/icon_analyze.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)   
        self.options_pane.addWidget(button_analyze)
        self.buttons.update({'Analyze' : button_analyze})

        # Generate Spawncycle
        button_generate = widget_helpers.create_button(self.central_widget, self.app, 'Generate', text=' Generate ', tooltip='Generate a SpawnCycle based on pre-determined critera', target=self.open_generate_dialog, style=ss, icon_path=resource_path('img/icon_generate.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)   
        self.options_pane.addWidget(button_generate)
        self.buttons.update({'Generate' : button_generate})

        # View Help
        button_about = widget_helpers.create_button(self.central_widget, self.app, 'About', text=' About ', tooltip='Show information about the program', target=self.open_about_dialog, style=ss, icon_path=resource_path('img/icon_about.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
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
        
        default_replace_menu = QtWidgets.QMenu('Replace ZEDs ..', batch_menu)
        custom_replace_menu = QtWidgets.QMenu('Replace ZEDs ..', batch_menu)
        custom_zeds = ['E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber', 'Alpha Scrake', 'Alpha Fleshpound',
                       'Alpha Fleshpound (Enraged)', 'Dr. Hans Volter', 'Patriarch', 'Abomination', 'Matriarch']

        # Init Default replace menu
        for zed in zed_ids.keys():
            if zed in custom_zeds:
                continue

            local_zeds = deepcopy(list(zed_ids.keys()))
            local_zeds.remove(zed) # Remove this ZED so it doesn't appear in the menu
            local_menu = QtWidgets.QMenu(zed, default_replace_menu)
            local_menu.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(50, 50, 50)")

            for z in local_zeds:
                if z in custom_zeds:
                    continue
                action = QtWidgets.QAction(z, local_menu)
                local_menu.addAction(action)
                action.triggered.connect(partial(self.replace_zeds, 'all', 'all', [zed], [z]))

            default_replace_menu.addMenu(local_menu)

        # Init Custom replace menu
        for zed in zed_ids.keys():
            local_zeds = deepcopy(list(zed_ids.keys()))
            local_zeds.remove(zed) # Remove this ZED so it doesn't appear in the menu
            local_menu = QtWidgets.QMenu(zed, custom_replace_menu)
            local_menu.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(50, 50, 50)")

            for z in local_zeds:
                action = QtWidgets.QAction(z, local_menu)
                local_menu.addAction(action)
                action.triggered.connect(partial(self.replace_zeds, 'all', 'all', [zed], [z]))

            custom_replace_menu.addMenu(local_menu)

        batch_menu.addMenu(default_replace_menu)
        batch_menu.addMenu(custom_replace_menu)

        return batch_menu, default_replace_menu, custom_replace_menu

    # Given the wave ID, squad ID, and a list of zeds, replaces all zeds in squads with the chosen replacement(s)
    def replace_zeds(self, wave_id, squad_id, zeds_to_replace, replacements):
        #print(f"wave_id={wave_id}, squad_id={squad_id}, zeds_to_replace={zeds_to_replace}, replacements={replacements}")
        
        # Figure out which waves and squads we're looping over
        wave_ids = [wave_id] if wave_id != 'all' else [i for i in range(len(self.wavedefs))]
        squad_ids = [[squad_id] for i in range(len(self.wavedefs))] if squad_id != 'all' else [[j for j in range(len(self.wavedefs[i]['Squads']))] for i in range(len(self.wavedefs))]

        zeds_replaced = 0
        replaced = False
        # Loop over the selected waves
        for wid in wave_ids:
            squads = self.wavedefs[wid]['Squads']

            # Loop over the selected squads
            #print(squad_ids)
            for sid in squad_ids[wid]:
                this_squad_zeds = squads[sid]['ZEDs'] # The ZEDs in this squad

                for i in range(len(zeds_to_replace)): # Replace the ZEDs if they exist
                    zid = zeds_to_replace[i]
                    if zid in this_squad_zeds:
                        new_zid = replacements[i] # Get the new ZED info
                        zed_count = this_squad_zeds[zid]['Count']

                        raged = True if 'Enraged' in new_zid else False
                        self.add_zed_to_squad(wid, sid, new_zid, count=zed_count, raged=raged) # Add the new one
                        self.remove_zed_from_squad(wid, sid, zid, count='all') # Remove the old zed after to keep the squad (for squad with len 1)     
                        
                        replaced = True
                        zeds_replaced += zed_count

        if replaced:
            self.add_message(f"Replaced {zeds_replaced} {zeds_to_replace[0]}{'s' if zeds_replaced > 1 else ''} successfully!")
            self.refresh_wavedefs() # Need to refresh everything
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
        while i >= 0:
            self.add_wavedef() # Add a new wave temporarily
            for j in range(len(self.wavedefs[i]['Squads'])):
                k = 0
                for (zed_id, zed_data) in self.wavedefs[i]['Squads'][j]['ZEDs'].items():
                    zed_count = zed_data['Count']
                    sr = zed_data['Raged']
                    if k == 0: # First ZED in the squad starts a new squad
                        self.add_squad(len(self.wavedefs)-1, zed_id, count=zed_count, raged=sr)
                    else:
                        self.add_zed_to_squad(len(self.wavedefs)-1, j, zed_id, count=zed_count, raged=sr)
                    k += 1
            i -= 1

        # Remove the old waves
        for i in range(orig_len):
            self.remove_wavedef(0, should_warn=False)

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
        ss_toggle = 'QPushButton {color: rgb(255, 255, 255);\nbackground-color: rgb(40, 40, 40);}' # Stylesheet
        button_switch = widget_helpers.create_button(self.central_widget, self.app, 'ZED Set', text=' Default' if self.zed_mode == 'Custom' else ' Custom', tooltip='Switch current ZED set', target=partial(self.switch_zed_mode, True), icon_path=resource_path('img/icon_switch.png'), icon_w=32, icon_h=32, style=ss_toggle, font=font_label, size_policy=sp_toggle, draggable=False)
        self.buttons.update({'Switch ZEDs' : button_switch})
        self.zed_pane.addWidget(button_switch)

        # Setup Trash ZEDs area
        label_trashzeds = widget_helpers.create_label(self.zed_grid_contents, text='Trash ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Trash ZEDs' : label_trashzeds})
        self.gridLayout_2.addWidget(label_trashzeds, 0, 0, 1, 1)
        widget_helpers.set_plain_border(label_trashzeds, color=Color(255, 255, 255), width=2)
        self.grid_trashzeds = QtWidgets.QGridLayout()
        self.grid_trashzeds.setObjectName("grid_trashzeds")

        button_cyst = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Cyst', tooltip='Cyst', style=ss_button, icon_path=resource_path('img/icon_cyst.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_cyst, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Cyst' : button_cyst})

        button_slasher = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Slasher', tooltip='Slasher', style=ss_button, icon_path=resource_path('img/icon_slasher.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_slasher, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Slasher' : button_slasher})

        button_alphaclot = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Alpha Clot', tooltip='Alpha Clot', style=ss_button, icon_path=resource_path('img/icon_alphaclot.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_alphaclot, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Alpha Clot' : button_alphaclot})

        button_rioter = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Rioter', tooltip='Rioter', style=ss_button, icon_path=resource_path('img/icon_rioter.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_rioter, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Rioter' : button_rioter})

        button_gorefast = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Gorefast', tooltip='Gorefast', style=ss_button, icon_path=resource_path('img/icon_gorefast.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_gorefast, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Gorefast' : button_gorefast})

        button_gorefiend = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Gorefiend', tooltip='Gorefiend', style=ss_button, icon_path=resource_path('img/icon_gorefiend.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_gorefiend, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'Gorefiend' : button_gorefiend})
        
        button_crawler = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Crawler', tooltip='Crawler', style=ss_button, icon_path=resource_path('img/icon_crawler.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_crawler, 3, 0, 1, 1)
        self.zed_pane_buttons.update({'Crawler' : button_crawler})

        button_elitecrawler = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Elite Crawler', tooltip='Elite Crawler', style=ss_button, icon_path=resource_path('img/icon_elitecrawler.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_elitecrawler, 3, 1, 1, 1)
        self.zed_pane_buttons.update({'Elite Crawler' : button_elitecrawler})

        button_stalker = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Stalker', tooltip='Stalker', style=ss_button, icon_path=resource_path('img/icon_stalker.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_stalker, 4, 0, 1, 1)
        self.zed_pane_buttons.update({'Stalker' : button_stalker})

        self.gridLayout_2.addLayout(self.grid_trashzeds, 1, 0, 1, 1)

        # Setup Medium ZEDs area
        label_mediumzeds = widget_helpers.create_label(self.zed_grid_contents, text='Medium ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Medium ZEDs' : label_mediumzeds})
        self.gridLayout_2.addWidget(label_mediumzeds, 2, 0, 1, 1)
        widget_helpers.set_plain_border(label_mediumzeds, color=Color(255, 255, 255), width=2)
        self.grid_mediumzeds = QtWidgets.QGridLayout()
        self.grid_mediumzeds.setObjectName("grid_mediumzeds")

        button_bloat = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Bloat', tooltip='Bloat', style=ss_button, icon_path=resource_path('img/icon_bloat.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_bloat, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Bloat' : button_bloat})

        button_husk = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Husk', tooltip='Husk', style=ss_button, icon_path=resource_path('img/icon_husk.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_husk, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Husk' : button_husk})

        button_siren = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Siren', tooltip='Siren', style=ss_button, icon_path=resource_path('img/icon_siren.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_siren, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Siren' : button_siren})

        button_edar_emp = widget_helpers.create_button(self.zed_grid_contents, self.app, 'E.D.A.R Trapper', tooltip='E.D.A.R Trapper', style=ss_button, icon_path=resource_path('img/icon_edar_emp.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_edar_emp, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'E.D.A.R Trapper' : button_edar_emp})

        button_edar_laser = widget_helpers.create_button(self.zed_grid_contents, self.app, 'E.D.A.R Blaster', tooltip='E.D.A.R Blaster', style=ss_button, icon_path=resource_path('img/icon_edar_laser.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_edar_laser, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'E.D.A.R Blaster' : button_edar_laser})

        button_edar_rocket = widget_helpers.create_button(self.zed_grid_contents, self.app, 'E.D.A.R Bomber', tooltip='E.D.A.R Bomber', style=ss_button, icon_path=resource_path('img/icon_edar_rocket.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_edar_rocket, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'E.D.A.R Bomber' : button_edar_rocket})

        self.gridLayout_2.addLayout(self.grid_mediumzeds, 3, 0, 1, 1)

        # Setup Large ZEDs area
        label_largezeds = widget_helpers.create_label(self.zed_grid_contents, text='Large ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Large ZEDs' : label_largezeds})
        self.gridLayout_2.addWidget(label_largezeds, 4, 0, 1, 1)
        widget_helpers.set_plain_border(label_largezeds, color=Color(255, 255, 255), width=2)
        self.grid_largezeds = QtWidgets.QGridLayout()
        self.grid_largezeds.setObjectName("grid_largezeds")

        button_quarterpound = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Quarter Pound', tooltip='Quarter Pound', style=ss_button, icon_path=resource_path('img/icon_quarterpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_quarterpound, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Quarter Pound' : button_quarterpound})

        button_quarterpound_raged = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Quarter Pound (Enraged)', tooltip='Quarter Pound (Enraged)', style=ss_button, icon_path=resource_path('img/icon_quarterpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_quarterpound_raged, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Quarter Pound (Enraged)' : button_quarterpound_raged})

        button_fleshpound = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Fleshpound', tooltip='Fleshpound', style=ss_button, icon_path=resource_path('img/icon_fleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_fleshpound, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Fleshpound' : button_fleshpound})

        button_fleshpound_raged = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Fleshpound (Enraged)', tooltip='Fleshpound (Enraged)', style=ss_button, icon_path=resource_path('img/icon_fleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_fleshpound_raged, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Fleshpound (Enraged)' : button_fleshpound_raged})

        button_scrake = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Scrake', tooltip='Scrake', style=ss_button, icon_path=resource_path('img/icon_scrake.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_scrake, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Scrake' : button_scrake})

        button_alphascrake = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Alpha Scrake', tooltip='Alpha Scrake', style=ss_button, icon_path=resource_path('img/icon_alphascrake.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_alphascrake, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'Alpha Scrake' : button_alphascrake})

        button_alphafleshpound = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Alpha Fleshpound', tooltip='Alpha Fleshpound', style=ss_button, icon_path=resource_path('img/icon_alphafleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_alphafleshpound, 3, 0, 1, 1)
        self.zed_pane_buttons.update({'Alpha Fleshpound' : button_alphafleshpound})

        button_alphafleshpound_raged = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Alpha Fleshpound (Enraged)', tooltip='Alpha Fleshpound (Enraged)', style=ss_button, icon_path=resource_path('img/icon_alphafleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_alphafleshpound_raged, 3, 1, 1, 1)
        self.zed_pane_buttons.update({'Alpha Fleshpound (Enraged)' : button_alphafleshpound_raged})
        
        self.gridLayout_2.addLayout(self.grid_largezeds, 5, 0, 1, 1)

        # Setup Bosses area
        label_bosses = widget_helpers.create_label(self.zed_grid_contents, text='Bosses', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Bosses' : label_bosses})
        self.gridLayout_2.addWidget(label_bosses, 6, 0, 1, 1)
        widget_helpers.set_plain_border(label_bosses, color=Color(255, 255, 255), width=2)
        self.grid_bosses = QtWidgets.QGridLayout()
        self.grid_bosses.setObjectName("grid_bosses")

        button_abomination_spawn = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Abomination Spawn', tooltip='Abomination Spawn', style=ss_button, icon_path=resource_path('img/icon_abomspawn.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_abomination_spawn, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Abomination Spawn' : button_abomination_spawn})

        button_kingfleshpound = widget_helpers.create_button(self.zed_grid_contents, self.app, 'King Fleshpound', tooltip='King Fleshpound', style=ss_button, icon_path=resource_path('img/icon_kingfleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_kingfleshpound, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'King Fleshpound' : button_kingfleshpound})

        button_hans = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Dr. Hans Volter', tooltip='Dr. Hans Volter', style=ss_button, icon_path=resource_path('img/icon_hans.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_hans, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Dr. Hans Volter' : button_hans})

        button_patriarch = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Patriarch', tooltip='Patriarch', style=ss_button, icon_path=resource_path('img/icon_patriarch.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_patriarch, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Patriarch' : button_patriarch})

        button_abomination = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Abomination', tooltip='Abomination', style=ss_button, icon_path=resource_path('img/icon_abomination.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_abomination, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Abomination' : button_abomination})

        button_matriarch = widget_helpers.create_button(self.zed_grid_contents, self.app, 'Matriarch', tooltip='Matriarch', style=ss_button, icon_path=resource_path('img/icon_matriarch.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_matriarch, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'Matriarch' : button_matriarch})

        self.gridLayout_2.addLayout(self.grid_bosses, 7, 0, 1, 1)

        # Highlight raged buttons
        button_quarterpound_raged.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid red;}")
        button_fleshpound_raged.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid red;}")
        button_alphafleshpound_raged.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}\nQZedPaneButton {border: 2px solid red;}")

        # Finalize ZED Pane
        self.zed_grid.setWidget(self.zed_grid_contents)
        self.zed_pane.addWidget(self.zed_grid)
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
        button_addwave = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Add Wave', target=self.add_wavedef, text=' Add Wave', tooltip='Add a new wave to the SpawnCycle', style=ss_button, icon_path=resource_path('img/icon_add.png'), icon_w=16, icon_h=16, font=font_button, size_policy=sp_button, draggable=False)
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

        ss_label = 'color: rgb(255, 255, 255);' # Stylesheet
        ss_textedit = 'color: rgb(255, 255, 255); background-color: rgba(40, 40, 40, 255);'

        # Set up Messages area
        label_messages_header = widget_helpers.create_label(self.central_widget, text='Messages', style=ss_label, font=font_label)
        label_messages_header.setAlignment(QtCore.Qt.AlignLeft)
        self.labels.update({'Messages Header' : label_messages_header})
        self.wavedefs_area.addWidget(label_messages_header)

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

    # Completely clears the WaveDefs pane of all widgets
    def clear_wavedefs(self):
        for i in reversed(range(self.wavedefs_scrollarea_layout.count())): 
            self.wavedefs_scrollarea_layout.itemAt(i).widget().setParent(None)
        self.wavedefs = []

    # Completely clears the Messages box
    def clear_messages(self):
        for l in self.message_labels:
            l.setParent(None)
        self.message_labels = []

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
    def generate_wavedefs(self, slider_data, GenerateDialog):
        # The current file is 'dirty', needs saving before we populate with the new stuff
        if self.dirty:
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            diag_title = 'SpawnCycler'
            diag_text = 'This will overwrite ALL current wave data.\nDo you wish to continue?'
            save_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y)
            save_dialog.accepted = True
            save_dialog.no_button.clicked.connect(partial(self.dialog_reject, save_dialog))
            self.save_dialog = save_dialog
            save_dialog.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            save_dialog.exec_()
            if not save_dialog.accepted:
                return

        # Close the Generate Window
        GenerateDialog.close()
        self.save_dialog = None

        # Load last used preset
        self.last_generate_mode = GenerateDialog.ui.zed_mode
        last_used = list(GenerateDialog.ui.get_slider_values().values())
        if last_used[0] == 4: # Fix up the wave number
            last_used[0] = 1
        elif last_used[0] == 7:
            last_used[0] = 2
        else:
            last_used[0] = 3
        self.last_generate_preset = last_used

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

        # Setup weights and zed arrays
        sd = slider_data
        types = ['Trash', 'Medium', 'Large', 'Boss']
        type_weights = [sd['Trash Density'], sd['Medium Density'], sd['Large Density'], sd['Boss Density']]
        trash_zeds = ['Cyst', 'Slasher', 'Alpha Clot', 'Gorefast', 'Crawler', 'Stalker']
        trash_weights = [sd['Cyst Density'], sd['Slasher Density'], sd['Alpha Clot Density'], sd['Gorefast Density'], sd['Crawler Density'], sd['Stalker Density']]
        medium_zeds = ['Bloat', 'Husk', 'Siren', 'E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber']
        medium_weights = [sd['Bloat Density'], sd['Husk Density'], sd['Siren Density'], sd['E.D.A.R Trapper Density'], sd['E.D.A.R Blaster Density'], sd['E.D.A.R Bomber Density']]
        large_zeds = ['Scrake', 'Quarter Pound', 'Fleshpound']
        large_weights = [sd['Scrake Density'], sd['Quarter Pound Density'], sd['Fleshpound Density']]
        bosses = ['Dr. Hans Volter', 'Patriarch', 'King Fleshpound', 'Abomination', 'Matriarch', 'Abomination Spawn'] 
        boss_weights = [sd['Hans Density'], sd['Patriarch Density'], sd['King Fleshpound Density'], sd['Abomination Density'], sd['Matriarch Density'], sd['Abomination Spawn Density']]

        # Show "Loading" dialog
        diag_title = 'Generating..'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 90 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
        diag_text = f"Generating.."
        loading_diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=False)
        loading_diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
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

                    if zed_id in new_squad and new_squad[zed_id]['Raged'] == spawnrage: # Already in the squad and same spawnrage status
                        new_squad.update({zed_id: {'Count': new_squad[zed_id]['Count'] + 1, 'Raged': spawnrage}})
                    else:
                        new_squad.update({zed_id: {'Count': 1, 'Raged': spawnrage}})

                wave_squads.append(new_squad)
            waves.append(wave_squads)

        # Populate the wavedefs using all this data
        self.populate_waves(waves, generated=True)

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
        diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_check.png')))
        diag.exec_() # Show a dialog to tell user to check messages

        # Post messages
        gen_str = (f"Generation complete!\n\n"
                   f"Summary\n----------------------\n"
                   f"{sd['Game Length']} Waves generated\n"
                   f"{num_squads_generated} Squads generated\n"
                   f"{num_zeds_generated} ZEDs generated ({num_trash_generated} Trash, {num_medium_generated} Mediums, {num_larges_generated} Larges, {num_bosses_generated} Bosses)\n"
                   f"{num_albino_generated} Albino ZEDs generated\n"
                   f"{num_spawnrage_generated} SpawnRaged ZEDs generated")
        self.add_message(gen_str)

    # Initializes the wavedefs table from a list of lines
    def populate_waves(self, lines, generated=False):
        num_waves = num_squads = num_zeds = 0
        custom_zeds = ['E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber', 'Dr. Hans Volter', 
                       'Patriarch', 'Abomination', 'Matriarch', 'Alpha Scrake', 'Alpha Fleshpound']
        # First format the lines into an iterable array
        if not generated:
            waves = []
            for line in lines:
                line = line.replace(' ', '')
                line = line.replace('SpawnCycleDefs=', '')
                line = line.replace('\n', '') # Replace all newlines
                waves.append(line.split(','))
        else:
            waves = lines

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
                if not generated:
                    squad = parse.format_squad(waves[i][j])
                else:
                    squad = waves[i][j]

                # Input all the ZEDs
                squad_items = list(squad.items())
                for k in range(len(squad_items)):
                    (zed_id, zed_data) = squad_items[k]
                    if zed_id in custom_zeds:
                        custom_zeds_found = True
                    zed_count = zed_data['Count'] # Unpack ZED data
                    num_zeds += zed_count
                    sr = zed_data['Raged']
                    
                    if k == 0: # First ZED in the squad starts a new squad
                        self.add_squad(wave_id, zed_id, count=zed_count, raged=sr)
                    else:
                        self.add_zed_to_squad(wave_id, squad_id, zed_id, count=zed_count, raged=sr)

        # Swap to the appropriate mode depending on the SpawnCycle
        if custom_zeds_found and self.zed_mode == 'Default':
            self.switch_zed_mode(should_warn=False)
        elif not custom_zeds_found and self.zed_mode == 'Custom':
            self.switch_zed_mode(should_warn=False)

        return num_waves, num_squads, num_zeds

    # Opens the File Browser window to select a file to open
    def load_from_file(self, fname=None):
        # Ask user for filename to open, but only if no filename given
        if fname is None:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', '', 'Text Files (*.txt)',)
            if filename == '': # Leave if the user cancelled
                return
        else:
            filename = fname

        # Dialog stuff
        diag_title = 'Open File'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()

        # Attempt to read in the file
        try:
            with open(filename, 'r') as f_in: 
                lines = f_in.readlines()

        # Something went wrong!  
        except:
            # Diplay error
            diag_text = f"File '{filename}' could not be opened!\nEither the file doesn't exist, or it is inaccessible somehow."
            err_dialog = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
            err_dialog.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            err_dialog.exec_()

            # Remove it from the recent files
            for fname in self.recent_files:
                if fname == filename:
                    self.recent_files.remove(fname)
                    self.refresh_recent_menu() # Refresh the "Recent" menu
            return

        # Now we can finally open the new file and process it.
        # The current file is 'dirty', needs saving before we populate with the new stuff
        if self.dirty:
            diag_text = 'Save changes before closing?'
            save_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y, yes_target=partial(self.save_to_file, False), cancel_button=True)
            save_dialog.cancel_button.clicked.connect(partial(self.dialog_cancel, save_dialog))
            save_dialog.cancelled = False
            self.save_dialog = save_dialog
            save_dialog.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            save_dialog.exec_()
            if save_dialog.cancelled:
                return
        self.save_dialog = None

        self.add_message(f"Attempting to parse file '{filename}'..") # Post a message
        # Parse the file to check for errors
        errors = parse.parse_syntax_import(filename, lines)
        if len(errors) > 0:
            self.add_message(errors[0])
            if len(errors) > 1:
                self.add_message('\n\n'.join([e.replace(f"Parse errors ('{filename}'):\n\n", '') for e in errors[1:]]), prefix=False)
            diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
            diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
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
        loading_diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
        loading_diag.show() # Show a dialog to tell user to check messages

        # Load up the waves!
        num_waves, num_squads, num_zeds = self.populate_waves(lines)
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
        #print(self.filename)

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
            save_dialog = widget_helpers.create_choice_dialog(self.central_widget, diag_title, diag_text, x, y, yes_target=partial(self.save_to_file, False), cancel_button=True)
            save_dialog.cancel_button.clicked.connect(partial(self.dialog_cancel, save_dialog))
            save_dialog.cancelled = False
            self.save_dialog = save_dialog
            save_dialog.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            save_dialog.exec_()
            if save_dialog.cancelled:
                return
        self.save_dialog = None
        self.reset_state()

    # Saves the file to the disk
    def save_to_file(self, file_browser=True):
        # Dialog stuff
        diag_title = 'SpawnCycler'
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()

        fname = f" ('{self.filename}')" if self.filename != 'Untitled' else ''
        self.add_message(f"Attempting to parse file{fname}..") # Post a message

        # Parse the file to check for errors
        errors = parse.parse_syntax_export(self.filename, self.wavedefs)
        if len(errors) > 0:
            self.add_message(errors[0])
            if len(errors) > 1:
                self.add_message('\n\n'.join([e.replace(f"Parse errors{fname}:\n\n", '') for e in errors[1:]]), prefix=False)
            diag_text = f'{len(errors)} syntax error(s) were encountered.\nFile could not be saved.\nSee the Messages box below for more details.'
            diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            diag.exec_() # Show a dialog to tell user to check messages
            return

        # Ask user for filename to save as
        #print(file_browser)
        if file_browser or self.filename == 'Untitled':
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File As', '', 'Text File (*.txt)')
            if filename == '': # Leave if the user cancelled
                return
        else:
            filename = self.filename

        self.add_message(f"Parse successful!") # Post a message

        # Save the file
        line_pfx = 'SpawnCycleDefs='
        with open(filename, 'w') as f:
            waves = []
            for wavedef in self.wavedefs:
                wave_squads = []
                for squad in wavedef['Squads']:
                    squad_zeds = [f"{zed_data['Count']}{zed_ids[zed_id]}" for (zed_id, zed_data) in squad['ZEDs'].items()]
                    wave_squads.append('_'.join(squad_zeds))
                waves.append(f"{line_pfx}{','.join(wave_squads)}")
            f.write('\n'.join(waves))

        num_squads = sum([len(w['Squads']) for w in self.wavedefs])
        num_zeds = 0
        for w in self.wavedefs:
            for s in w['Squads']:
                for z in s['ZEDs'].values():
                    num_zeds += z['Count']
        self.add_message(f"Successfully wrote {len(self.wavedefs)} waves, {num_squads:,d} squads, {num_zeds:,d} zeds to file '{filename}'.") # Post a message

        # Update the "Recent Files" menu
        self.add_filename_to_recent(filename)

        # File isn't dirty anymore
        self.dirty = False
        self.filename = filename # Set window title
        self.set_window_title('SpawnCycler (' + self.truncate_filename(self.filename) + ')')

        if self.save_dialog is not None: # We came from a dialog to get here. Close it
            self.save_dialog.close()

    # Resets everything back to normal
    def reset_state(self):
        self.dirty = False # Reset dirty status
        self.clear_wavedefs() # Delete all waves
        self.clear_messages() # Delete all messages

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
        button_addwave = widget_helpers.create_button(self.wavedefs_scrollarea_contents, self.app, 'Add Wave', target=self.add_wavedef, text=' Add Wave', tooltip='Add a new wave to the SpawnCycle', style=ss_button, icon_path=resource_path('img/icon_add.png'), icon_w=16, icon_h=16, font=font_button, size_policy=sp_button, draggable=False)
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
        # Meta vars
        self.dirty = False # Whether or not the file needs saving before closing
        self.filename = 'Untitled'
        self.MainWindow = MainWindow
        self.buttons = {}
        self.zed_pane_buttons = {}
        self.wavedefs = []
        self.labels = {}
        self.message_labels = []

        # Set up main window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 1000)
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
                    f"To remove ZEDs from a Squad, simply drag the ZED out of the Squad and onto the empty background.\n"
                    f"You can perform more actions by using MOUSE2 (RMB) on a ZED icon within a Squad.\n\n"
                    f"With this tool, you can create your own SpawnCycle, Import and alter other SpawnCycles, or even Generate SpawnCycles based on pre-determined criteria.\n\n"
                    f"Enjoy!\n")
        self.add_message(init_msg)

    # Sets the window title
    def set_window_title(self, title):
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate('SpawnCycler', title))

    # Opens the 'About' menu
    def open_about_dialog(self):
        dialog = QtWidgets.QDialog()
        dialog.ui = AboutDialog()
        dialog.ui.setupUi(dialog)
        dialog.setWindowTitle('About')
        dialog.setWindowIcon(QtGui.QIcon(resource_path('img/logo.png')))
        dialog.exec_()

    # Opens the 'Generate' menu
    def open_generate_dialog(self):
        dialog = QtWidgets.QDialog()
        dialog.ui = GenerateDialog()
        dialog.ui.setupUi(dialog, self.generate_wavedefs, self.last_generate_preset, self.last_generate_mode)
        dialog.setWindowTitle('Generate SpawnCycle')
        dialog.setWindowIcon(QtGui.QIcon(resource_path('img/logo.png')))
        dialog.exec_()

    # Called by the Analyze GUI to save the last used preset (so it can be restored later)
    def save_analyze_preset(self, preset):
        self.last_analyze_preset = preset

    # Opens the 'Analyze' menu
    def open_analyze_dialog(self):
        error_msg = ''

        # Invalid SpawnCycle length
        if len(self.wavedefs) not in [4, 7, 10]:
            error_msg += f"Cannot analyze SpawnCycle of length {len(self.wavedefs)} wave(s).\nWave count must be 4, 7, or 10!\n"

        # Check for empty waves
        if len(self.wavedefs) > 0:
            found = False
            for wave in self.wavedefs:
                if len(wave['Squads']) > 0:
                    found = True
            if not found:
                error_msg += f"Cannot analyze empty waves. All waves must have at least one ZED!\n\n"

        # Print errors
        if error_msg != '':
            self.add_message(error_msg)
            diag_title = 'WARNING'
            diag_text = 'Errors occurred while attempting to Analyze.\nCheck the Messages box below for more details.'
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-200 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            diag = widget_helpers.create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            diag.exec_() # Show a dialog to tell user to check messages
            return

        # Open the dialog
        dialog = widget_helpers.CustomDialog()
        dialog.ui = AnalyzeDialog()
        dialog.ui.setupUi(dialog, self.wavedefs, self.truncate_filename(self.filename), save_preset=self.save_analyze_preset, last_preset=self.last_analyze_preset)
        dialog.setWindowTitle('Analyze SpawnCycle')
        dialog.setWindowIcon(QtGui.QIcon(resource_path('img/logo.png')))
        dialog.exec_()

    # Updates the "Recent Files" menu
    def add_filename_to_recent(self, filename):
        with open('meta', 'r') as f: # Get the metadata
            meta_dict = json.loads(f.readline())

        if len(self.recent_files) == 0: # Special case: no recents. 
            self.recent_menu.removeAction(self.recent_menu.actions()[0]) # Remove the 'No files found'

        if filename in self.recent_files: # We've already recently opened this file
            self.recent_files.remove(filename) # Remove the old one
        else: # Never opened this file recently. Need to add it to the list
            if len(self.recent_files) == _RECENT_MAX: # Full. Need to pop one of the recent files out of the list
                self.recent_files.pop(-1)

        self.recent_files.insert(0, filename) # Add it to the "Recent Files" list
        
        # Save metadata
        with open('meta', 'w') as f:
            meta_dict['Recent Files'] = self.recent_files
            f.write(json.dumps(meta_dict))

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
        MainWindow.setWindowIcon(QtGui.QIcon(resource_path('img/logo.png')))
        self.switch_zed_mode()


# Custom MainWindow that calls an event when closed
class CustomMainWindow(QtWidgets.QMainWindow):
    # This function is called when the user presses the X (close) button
    def closeEvent(self, event):
        if self.ui.dirty: # File needs to be saved first
            diag_title = 'SpawnCycler'
            diag_text = 'Save changes before closing?'
            x = self.ui.central_widget.mapToGlobal(self.ui.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
            y = self.ui.central_widget.mapToGlobal(self.ui.central_widget.rect().center()).y()
            save_dialog = widget_helpers.create_choice_dialog(self.ui.central_widget, diag_title, diag_text, x, y, yes_target=partial(self.ui.save_to_file, False))
            self.ui.save_dialog = save_dialog
            save_dialog.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            save_dialog.exec_()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    MainWindow = CustomMainWindow()
    ui = Ui_MainWindow(app)
    ui.setupUi(MainWindow)
    MainWindow.ui = ui
    MainWindow.show()
    sys.exit(app.exec_())

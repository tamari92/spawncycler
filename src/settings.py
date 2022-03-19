#
#  settings.py
#
#  Author: Tamari
#  Date of creation: 3/9/2022
#
#  Displays a menu to change program settings


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
##  © Tamari, 2020-2022
##  All rights reserved.


from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import widget_helpers
import meta
import json

_DEF_FONT_FAMILY = 'Consolas'
_WINDOWSIZE_SETTINGS_W = 500
_WINDOWSIZE_SETTINGS_H = 540

# Settings stuff
setting_tooltips = {'should_warn_zedset': 'Display a warning when changing to a ZED Set that is not officially supported by most CD builds.',
                    'should_warn_gensettings': 'Display a warning when using Generator settings that are not officially supported by most CD builds.',
                    'should_warn_cyclelength': 'Display a warning when saving a SpawnCycle of invalid length.',
                    'should_warn_emptywaves': 'Display a warning when saving a SpawnCycle that contains empty waves.',
                    'autosave_enabled': 'Toggles Autosave functionality.\n\nAn autosave can only occur if:\n1. Autosave is enabled (see above)\n2. The file has a name (it has been saved before)\n3. The file has unsaved changes',
                    'autosave_interval': 'The interval at which SpawnCycler will autosave your work.\nGiven value is in seconds.\n\nAn autosave can only occur if:\n1. Autosave is enabled (see above)\n2. The file has a name (it has been saved before)\n3. The file has unsaved changes',
                    'save_json_default_target': 'For JSON SpawnCycles only.\nSets the default GameLength that SpawnCycler will save data into when manually saving:\n\nAlways Ask  -  Always ask for confirmation whenever multiple destinations are available.\nAdaptive  -  Assign the SpawnCycle to the closest compatible GameLength.\nPreferred Medium  -  Attempt to assign the SpawnCycle to the Medium GameLength. Defaults to Adaptive if this is not possible for any reason.\nPreferred Long  -  Attempt to assign the SpawnCycle to the Long GameLength. Defaults to Adaptive if this is not possible for any reason.\n\nNote that for Autosaving, SpawnCycler attempts to assign the SpawnCycle to the last opened or saved to slot, and uses the Adaptive setting if this is not possible.',
                    'save_default_filetype': 'Sets the default filetype that SpawnCycler uses when opening the Save or Save As menus:\n\nAdaptive  -  Use the currently opened filetype.\nStandard  -  The Standard (.txt) format used by most builds of CD.\nCustom  -  The Custom (.json) format used by Forrest Mark X\'s CD Build.',
                    'new_squad_min_amount': 'Sets the minimum amount of ZEDs added when creating a new squad.',
                    'analyze_default_length': 'Sets the default GameLength that the Analyze tool will use for sampling:\n\nLast Used  -  Sample using the previously used GameLength. Uses \'Preferred Long\' when opening the Analyzer for the first time.\nAdaptive  -  Sample using the closest GameLength to the current amount of waves in the SpawnCycle\nPreferred Short  -  Sample using the Short GameLength if available. Defaults to Adaptive if this is not possible for any reason.\nPreferred Medium  -  Sample using the Medium GameLength if available. Defaults to Adaptive if this is not possible for any reason.\nPreferred Long  -  Sample using the Long GameLength if available. Defaults to Adaptive if this is not possible for any reason.'}

setting_nicenames = {'should_warn_zedset': 'Warn when using custom ZED sets',
                      'should_warn_gensettings': 'Warn when using custom Generator settings',
                      'should_warn_cyclelength': 'Warn when saving invalid length',
                      'should_warn_emptywaves': 'Warn when saving empty waves',
                      'autosave_enabled': 'Autosave Enabled',
                      'autosave_interval': 'Autosave Interval',
                      'save_json_default_target': 'Default JSON Manual Save Length',
                      'save_default_filetype': 'Default Manual Save Filetype',
                      'new_squad_min_amount': 'New Squad Minimum ZED Amount',
                      'analyze_default_length': 'Default Analyze Sample GameLength'}

setting_nicenames_dropdown = {'save_json_default_target': ['Always Ask', 'Adaptive', 'Preferred Medium', 'Preferred Long'],
                              'save_default_filetype': ['Adaptive', 'Standard (.txt)', 'Custom (.json)'],
                              'analyze_default_length': ['Last Used', 'Adaptive', 'Preferred Short', 'Preferred Medium', 'Preferred Long']}


class SettingsDialog(object):
    def __init__(self, parent):
        self.parent = parent
        
    def create_checkbox_field(self, text, key, tooltip):
        # Label stuff
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(10)
        font.setWeight(75)

        # Set everything up
        frame = QtWidgets.QFrame()
        hbox = QtWidgets.QHBoxLayout(frame)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        checkbox = QtWidgets.QCheckBox()
        checkbox.setChecked(meta.get_keyvalue(key))
        checkbox.setStyleSheet("QToolTip {color: rgb(0, 0, 0);};")
        label = QtWidgets.QLabel()
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {color: rgb(255, 255, 255);}\nQToolTip {color: rgb(0, 0, 0);};")
        label.setText(text)

        children = {'Label': label, 'Checkbox': checkbox}

        # Add tooltips
        label.setToolTip(tooltip)
        checkbox.setToolTip(tooltip)

        # Add to the frame
        hbox.addWidget(label)
        hbox.addWidget(checkbox)

        return frame, children

    def create_textentry_field(self, text, key, tooltip, w=64, h=20):
        # Label stuff
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(10)
        font.setWeight(75)

        # Set everything up
        frame = QtWidgets.QFrame()
        hbox = QtWidgets.QHBoxLayout(frame)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        textbox = widget_helpers.create_textfield(str(meta.get_keyvalue(key)), w=48, font=font, style="QLineEdit {color: rgb(255, 255, 255); background-color: rgb(75, 75, 75);}\nQToolTip {color: rgb(0, 0, 0);};")
        label = QtWidgets.QLabel()
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {color: rgb(255, 255, 255);}\nQToolTip {color: rgb(0, 0, 0);};")
        label.setText(text)

        children = {'Label': label, 'Textfield': textbox}

        # Add tooltips
        label.setToolTip(tooltip)
        textbox.setToolTip(tooltip)

        # Add to the frame
        hbox.addWidget(label)
        hbox.addWidget(textbox)

        return frame, children

    def create_choice_field(self, text, options, key, tooltip):
        # Label stuff
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(10)
        font.setWeight(75)

        ss_cbox = 'QToolTip {color: rgb(0, 0, 0);} QComboBox {color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);}' # Stylesheet
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)

        # Set everything up
        frame = QtWidgets.QFrame()
        hbox = QtWidgets.QHBoxLayout(frame)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        cbox = widget_helpers.create_combobox(None, options=options, style=ss_cbox, size_policy=sp)
        cbox.setCurrentIndex(meta.get_keyvalue(key))
        label = QtWidgets.QLabel()
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {color: rgb(255, 255, 255);}\nQToolTip {color: rgb(0, 0, 0);};")
        label.setText(text)

        children = {'Label': label, 'ComboBox': cbox}

        # Add tooltips
        label.setToolTip(tooltip)
        cbox.setToolTip(tooltip)

        # Add to the frame
        hbox.addWidget(label)
        hbox.addWidget(cbox)

        return frame, children

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

    # Called when a textbox is committed
    def commit_textbox(self, textbox, key, min_value=None, max_value=None):
        if not textbox.text().isnumeric(): # Ignore non-numbers
            textbox.setText(str(meta.get_keyvalue(key)))
            return

        val = int(textbox.text())

        # Set the value of the textfield
        if min_value is not None and val < min_value: # Too low
            val = min_value
        elif max_value is not None and val > max_value: # Too high
            val = max_value

        # Set the value
        textbox.setText(str(val))

        # Same value as we already have set. Do nothing
        if int(textbox.text()) == meta.get_keyvalue(key):
            return

        meta.set_keyvalue(key, val)

        if key == 'autosave_interval':
            self.parent.autosave_timer.start(meta.get_keyvalue('autosave_interval') * 1000.0) # Convert to ms

        # Post a message
        self.parent.add_message(f"Setting '{setting_nicenames[key]}' set to {val}")

    def commit_checkbox(self, checkbox, key):
        meta.set_keyvalue(key, checkbox.isChecked())

        # Change the autosave button's icon
        if key == 'autosave_enabled':
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap('img/icon_autosave_false.png' if not meta.get_keyvalue('autosave_enabled') else 'img/icon_autosave_true.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.parent.buttons['Autosave'].setIcon(icon)

        # Post a message
        self.parent.add_message(f"Setting '{setting_nicenames[key]}' set to {checkbox.isChecked()}")

    def commit_combobox(self, combobox, key, translation=None):
        val = translation[combobox.currentIndex()] if translation is not None else combobox.currentIndex()
        if val == meta.get_keyvalue(key):
            return
        meta.set_keyvalue(key, val)

        # Post a message
        self.parent.add_message(f"Setting '{setting_nicenames[key]}' set to '{setting_nicenames_dropdown[key][combobox.currentIndex()]}'")

    def setup_fields(self):
        # Label stuff
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(10)
        font_label.setWeight(75)
        sp_header = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        ss_header = "color: rgb(255, 255, 255); background-color: rgba(255, 255, 255, 30);"
        ss_label = 'color: rgb(255, 255, 255);'

        # Create labels
        spacer_label = widget_helpers.create_label(None, text='\n', style=ss_label, font=font_label, size_policy=sp_header, alignment=QtCore.Qt.AlignCenter)
        general_settings_label = widget_helpers.create_label(None, text='\nGeneral Settings\n', size_policy=sp_header, font=font_label, alignment=QtCore.Qt.AlignCenter)
        general_settings_label.setStyleSheet(ss_header)
        general_settings_label.setFrameShape(QtWidgets.QFrame.Box)
        general_settings_label.setFrameShadow(QtWidgets.QFrame.Plain)
        general_settings_label.setLineWidth(2)

        # Set up ZED Set warning
        should_warn_zedset_frame, should_warn_zedset_children = self.create_checkbox_field(f"{setting_nicenames['should_warn_zedset']}   ", 'should_warn_zedset', setting_tooltips['should_warn_zedset'])
        should_warn_zedset_children['Checkbox'].toggled.connect(partial(self.commit_checkbox, should_warn_zedset_children['Checkbox'], 'should_warn_zedset'))

        # Set up Generator Settings warning
        should_warn_gensettings_frame, should_warn_gensettings_children = self.create_checkbox_field(f"{setting_nicenames['should_warn_gensettings']}   ", 'should_warn_gensettings', setting_tooltips['should_warn_gensettings'])
        should_warn_gensettings_children['Checkbox'].toggled.connect(partial(self.commit_checkbox, should_warn_gensettings_children['Checkbox'], 'should_warn_gensettings'))

        # Set up Cycle Length warning
        should_warn_cyclelength_frame, should_warn_cyclelength_children = self.create_checkbox_field(f"{setting_nicenames['should_warn_cyclelength']}   ", 'should_warn_cyclelength', setting_tooltips['should_warn_cyclelength'])
        should_warn_cyclelength_children['Checkbox'].toggled.connect(partial(self.commit_checkbox, should_warn_cyclelength_children['Checkbox'], 'should_warn_cyclelength'))

        # Set up Empty Wave warning
        should_warn_emptywaves_frame, should_warn_emptywaves_children = self.create_checkbox_field(f"{setting_nicenames['should_warn_emptywaves']}   ", 'should_warn_emptywaves', setting_tooltips['should_warn_emptywaves'])
        should_warn_emptywaves_children['Checkbox'].toggled.connect(partial(self.commit_checkbox, should_warn_emptywaves_children['Checkbox'], 'should_warn_emptywaves'))

        # Set up Autosave Enabled
        autosave_enabled_frame, autosave_enabled_children = self.create_checkbox_field(f"{setting_nicenames['autosave_enabled']}   ", 'autosave_enabled', setting_tooltips['autosave_enabled'])
        autosave_enabled_children['Checkbox'].toggled.connect(partial(self.commit_checkbox, autosave_enabled_children['Checkbox'], 'autosave_enabled'))

        # Set up Autosave Interval
        autosave_interval_frame, autosave_interval_children = self.create_textentry_field(f"{setting_nicenames['autosave_interval']}   ", 'autosave_interval', setting_tooltips['autosave_interval'])
        autosave_interval_children['Textfield'].textChanged.connect(partial(self.edit_textbox, autosave_interval_children['Textfield']))
        autosave_interval_children['Textfield'].editingFinished.connect(partial(self.commit_textbox, autosave_interval_children['Textfield'], 'autosave_interval', 10, None))

        # Set up JSON default save
        save_json_default_target_frame, save_json_default_target_children = self.create_choice_field(f"{setting_nicenames['save_json_default_target']}   ", setting_nicenames_dropdown['save_json_default_target'], 'save_json_default_target', setting_tooltips['save_json_default_target'])
        save_json_default_target_children['ComboBox'].activated.connect(partial(self.commit_combobox, save_json_default_target_children['ComboBox'], 'save_json_default_target', None))

        # Set up default save filetype
        save_default_filetype_frame, save_default_filetype_children = self.create_choice_field(f"{setting_nicenames['save_default_filetype']}   ", setting_nicenames_dropdown['save_default_filetype'], 'save_default_filetype', setting_tooltips['save_default_filetype'])
        save_default_filetype_children['ComboBox'].activated.connect(partial(self.commit_combobox, save_default_filetype_children['ComboBox'], 'save_default_filetype', None))

        # Set up New ZED Min Amount
        new_squad_min_amount_frame, new_squad_min_amount_children = self.create_textentry_field(f"{setting_nicenames['new_squad_min_amount']}   ", 'new_squad_min_amount', setting_tooltips['new_squad_min_amount'])
        new_squad_min_amount_children['Textfield'].textChanged.connect(partial(self.edit_textbox, new_squad_min_amount_children['Textfield']))
        new_squad_min_amount_children['Textfield'].editingFinished.connect(partial(self.commit_textbox, new_squad_min_amount_children['Textfield'], 'new_squad_min_amount', 1, 10))

        # Set up default analyze length
        analyze_default_length_frame, analyze_default_length_children = self.create_choice_field(f"{setting_nicenames['analyze_default_length']}   ", setting_nicenames_dropdown['analyze_default_length'], 'analyze_default_length', setting_tooltips['analyze_default_length'])
        analyze_default_length_children['ComboBox'].activated.connect(partial(self.commit_combobox, analyze_default_length_children['ComboBox'], 'analyze_default_length', None))

        # Add to central layout
        self.scrollarea_layout.addWidget(general_settings_label)
        self.scrollarea_layout.addWidget(should_warn_zedset_frame)
        self.scrollarea_layout.addWidget(should_warn_gensettings_frame)
        self.scrollarea_layout.addWidget(should_warn_cyclelength_frame)
        self.scrollarea_layout.addWidget(should_warn_emptywaves_frame)
        self.scrollarea_layout.addWidget(autosave_enabled_frame)
        self.scrollarea_layout.addWidget(autosave_interval_frame)
        self.scrollarea_layout.addWidget(save_json_default_target_frame)
        self.scrollarea_layout.addWidget(save_default_filetype_frame)
        self.scrollarea_layout.addWidget(new_squad_min_amount_frame)
        self.scrollarea_layout.addWidget(analyze_default_length_frame)

    def setupUi(self, Dialog):
        # Set up main window
        Dialog.setFixedSize(_WINDOWSIZE_SETTINGS_W, _WINDOWSIZE_SETTINGS_H)
        Dialog.setStyleSheet("background-color: rgb(50, 50, 50);")
        self.central_layout = QtWidgets.QVBoxLayout(Dialog)

        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.scrollarea = QtWidgets.QScrollArea()
        self.scrollarea.setSizePolicy(sp)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setStyleSheet('color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);')
        self.scrollarea.setFrameShape(QtWidgets.QFrame.Box)
        self.scrollarea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrollarea.setLineWidth(2)
        scrollarea_contents = QtWidgets.QWidget()
        self.scrollarea.setWidget(scrollarea_contents)
        self.scrollarea_layout = QtWidgets.QVBoxLayout(scrollarea_contents)
        self.scrollarea_layout.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.central_layout.addWidget(self.scrollarea)
        
        # Initialize window components
        self.setup_fields()

        # Set up OK button
        ok_button = QtWidgets.QPushButton('OK')
        ok_button.setStyleSheet("color: rgb(255, 255, 255);")
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(ok_button.sizePolicy().hasHeightForWidth())
        ok_button.setSizePolicy(sp)
        ok_button.clicked.connect(Dialog.close)
        self.central_layout.addWidget(ok_button)

        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate


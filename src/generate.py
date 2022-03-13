#
#  generate.py
#
#  Author: Tamari
#  Date of creation: 11/21/2020
#
#  UI code for the 'Generate' functionality
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
has_swapped_modes_generate = False

_WINDOWSIZE_GENERATE_W = 800
_WINDOWSIZE_GENERATE_H = 1000

omega_zeds = ['Slasher Omega', 'Gorefast Omega', 'Stalker Omega', 'Tiny Crawler', 'Medium Crawler',
              'Big Crawler', 'Huge Crawler', 'Ultra Crawler', 'Siren Omega', 'Husk Omega', 'Tiny Husk',
              'Tiny Scrake', 'Scrake Omega', 'Scrake Emperor', 'Fleshpound Omega', 'Stalker Omega']

class GenerateDialog(object):
    def __init__(self, parent, Dialog):
        self.cancelled = False
        self.params = {}
        self.param_widgets = {}
        self.slider_panes = {}
        self.buttons = {}
        self.zed_mode = 'Custom' # Start in custom mode to populate everything
        self.Dialog = Dialog
        self.parent = parent

    # Creates a button with the ZED icon in it
    def create_zed_button(self, zed_id):
        icon_path = widget_helpers.get_icon_path(zed_id)
        icon_w = icon_h = 40
        if zed_id in omega_zeds:
            ss = "QToolTip {color: rgb(0, 0, 0);\nbackground-color: rgb(40, 40, 40);}\nQPushButton {border: 2px solid purple;}"
        else:
            ss = 'QToolTip {color: rgb(0, 0, 0);\nbackground-color: rgb(40, 40, 40);}' # Stylesheet
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        button = widget_helpers.create_button(None, None, None, tooltip=zed_id, style=ss, icon_path=icon_path, icon_w=icon_w, icon_h=icon_h, size_policy=sp, options=False, squad=False, draggable=False)

        return button

    # Called when a generator textbox is edited
    def edit_textbox(self, textbox, slider):
        if not textbox.text().isnumeric(): # NaN somehow (for example the field is empty)
            return

        # Remove any leading zeroes
        val = int(textbox.text()) # Conv to an int will remove the zeroes on its own. Guaranteed to be numeric at this point
        if val == 0:
            if textbox.text().count('0') > 1: # Special case for zero, just replace it. Stripping won't work here
                textbox.setText('0')
        else:
            textbox.setText(textbox.text().lstrip('0'))

    # Updates the given slider with the value of the textbox
    def commit_textbox(self, textbox, slider):
        if not textbox.text().isnumeric(): # Ignore non-numbers
            textbox.setText(str(slider.value()))
            return

        # Same value as we already have set. Do nothing
        if int(textbox.text()) == slider.value():
            return

        val = int(textbox.text())

        # Constrain range
        # Figure out what the min and max will be
        min_value = slider.minimum()
        max_value = slider.maximum()

        # Set the value of the textfield
        if val < min_value: # Too low
            val = min_value
        elif val > max_value: # Too high
            val = max_value

        slider.setValue(val) # Update the slider
        textbox.setText(str(slider.value()))

    # Updates the given slider with the value of the textbox
    def update_slider_gamelength(self, slider, affected):
        # Get current value of slider
        val = slider.value()

        # Update the child sliders and textboxes depending on this slider
        if val == 1: # Short
            for aff in affected:
                aff['High Label'].setText(' 4    ')
                aff['Slider'].setMaximum(4)
        elif val == 2: # Medium
            for aff in affected:
                aff['High Label'].setText(' 7    ')
                aff['Slider'].setMaximum(7)
        else: # Long
            for aff in affected:
                aff['High Label'].setText(' 10   ')
                aff['Slider'].setMaximum(10)


    # Updates the given textbox with the value of the slider
    def update_textbox(self, textbox, slider):
        textbox.setText(str(slider.value()))
        textbox.setAlignment(QtCore.Qt.AlignCenter)

    # Creates, initializes, and returns an entire HBox pane with Low/High labels plus a slider
    def create_slider_pane(self, low_text, high_text, min_value, max_value, tick_interval, tooltip=None, width=480, default='max', alignment=QtCore.Qt.AlignCenter, text_box=True):
        # Label stuff
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(10)
        font.setWeight(75)
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        ss_label = 'QLabel {color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);}\nQToolTip {color: rgb(0, 0, 0);}' # Stylesheet
        ss_le = 'QLineEdit {color: rgb(255, 255, 255); background-color: rgb(40, 40, 40); border: 2px solid white;}\nQToolTip {color: rgb(0, 0, 0);}' # Stylesheet
        ss_slider = 'QSlider {color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);}\nQToolTip {color: rgb(0, 0, 0);}' # Stylesheet

        # Create components
        low_label = widget_helpers.create_label(None, text=low_text, style=ss_label, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)
        slider = widget_helpers.create_slider(min_value, max_value, tick_interval, style=ss_slider, width=width, default=default)
        high_label = widget_helpers.create_label(None, text=high_text, style=ss_label, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)

        # Set tooltip
        if tooltip is not None:
            low_label.setToolTip(tooltip)
            slider.setToolTip(tooltip)
            high_label.setToolTip(tooltip)

        # Create text edit
        if text_box:
            # Style stuff
            ss = 'color: rgb(255, 255, 255);' # Stylesheet
            font = QtGui.QFont()
            font.setFamily(_DEF_FONT_FAMILY)
            font.setPointSize(10)
            font.setWeight(75)

            # Create textbox
            val = default if default != 'max' else max_value
            text_edit = widget_helpers.create_textfield(str(val), font, sp, ss_le, 48, 28)

            # Connect textbox signals
            text_edit.textChanged.connect(partial(self.edit_textbox, text_edit, slider))
            text_edit.editingFinished.connect(partial(self.commit_textbox, text_edit, slider))

            # Connect the slider to the textbox
            slider.valueChanged.connect(partial(self.update_textbox, text_edit, slider))

        # Create an hbox to put these in
        frame = QtWidgets.QFrame()
        hbox = QtWidgets.QHBoxLayout(frame)
        hbox.setAlignment(alignment)
        hbox.addWidget(low_label)
        hbox.addWidget(slider)
        hbox.addWidget(high_label)
        if text_box:
            hbox.addWidget(text_edit)
        frame.setSizePolicy(sp)
        frame.setStyleSheet("background-color: rgb(40, 40, 40);")

        # Components used to create the pane
        children = {'Layout': hbox, 'Low Label': low_label, 'Slider': slider, 'High Label': high_label}
        if text_box:
            children.update({'TextBox': text_edit})

        return {'Frame': frame, 'Children': children}

    def swap_modes(self, first_time=False):
        if self.zed_mode == 'Default': # Swap to Custom
            if not first_time:
                global has_swapped_modes_generate
                if not has_swapped_modes_generate and meta.get_keyvalue('should_warn_gensettings'):
                    diag_title = 'WARNING'
                    diag_text = '\nThe Custom Settings are NOT supported by most Controlled Difficulty builds.\nUsing these settings may break the generated SpawnCycle on those builds.\n\nUse at your own risk!\n'
                    x = self.Dialog.mapToGlobal(self.Dialog.rect().center()).x()-200 # Anchor dialog to center of window
                    y = self.Dialog.mapToGlobal(self.Dialog.rect().center()).y()
                    diag = widget_helpers.create_simple_dialog(self.Dialog, diag_title, diag_text, x, y, button=True, checkbox=True)
                    diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))

                    diag.exec_() # Show the dialog

                    # Check if the user clicked "Don't show this again"
                    if diag.checkbox.checkState(): # We know this will exist since checkbox=True
                        meta.set_keyvalue('should_warn_gensettings', False) # Don't ever show the dialog again

                    has_swapped_modes_generate = True # Never show this message again

            # Show custom stuff
            self.slider_panes['Slasher Omega Density']['Frame'].setVisible(True)
            self.slider_panes['Gorefast Omega Density']['Frame'].setVisible(True)
            self.slider_panes['Tiny Crawler Density']['Frame'].setVisible(True)
            self.slider_panes['Medium Crawler Density']['Frame'].setVisible(True)
            self.slider_panes['Big Crawler Density']['Frame'].setVisible(True)
            self.slider_panes['Huge Crawler Density']['Frame'].setVisible(True)
            self.slider_panes['Ultra Crawler Density']['Frame'].setVisible(True)
            self.slider_panes['Stalker Omega Density']['Frame'].setVisible(True)
            self.slider_panes['Husk Omega Density']['Frame'].setVisible(True)
            self.slider_panes['Tiny Husk Density']['Frame'].setVisible(True)
            self.slider_panes['Siren Omega Density']['Frame'].setVisible(True)
            self.slider_panes['E.D.A.R Trapper Density']['Frame'].setVisible(True)
            self.slider_panes['E.D.A.R Blaster Density']['Frame'].setVisible(True)
            self.slider_panes['E.D.A.R Bomber Density']['Frame'].setVisible(True)
            self.slider_panes['Scrake Albino Density']['Frame'].setVisible(True)
            self.slider_panes['Scrake Omega Density']['Frame'].setVisible(True)
            self.slider_panes['Scrake Emperor Density']['Frame'].setVisible(True)
            self.slider_panes['Tiny Scrake Density']['Frame'].setVisible(True)
            self.slider_panes['Fleshpound Albino Density']['Frame'].setVisible(True)
            self.slider_panes['Fleshpound Omega Density']['Frame'].setVisible(True)
            self.slider_panes['Hans Density']['Frame'].setVisible(True)
            self.slider_panes['Patriarch Density']['Frame'].setVisible(True)
            self.slider_panes['Abomination Density']['Frame'].setVisible(True)
            self.slider_panes['Matriarch Density']['Frame'].setVisible(True)

            # Set default values
            self.slider_panes['Slasher Omega Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Gorefast Omega Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Tiny Crawler Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Medium Crawler Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Big Crawler Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Huge Crawler Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Ultra Crawler Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Stalker Omega Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Husk Omega Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Tiny Husk Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Siren Omega Density']['Children']['Slider'].setValue(100)
            self.slider_panes['E.D.A.R Trapper Density']['Children']['Slider'].setValue(100)
            self.slider_panes['E.D.A.R Blaster Density']['Children']['Slider'].setValue(100)
            self.slider_panes['E.D.A.R Bomber Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Scrake Albino Density']['Children']['Slider'].setValue(30)
            self.slider_panes['Scrake Omega Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Scrake Emperor Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Tiny Scrake Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Fleshpound Albino Density']['Children']['Slider'].setValue(30)
            self.slider_panes['Fleshpound Omega Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Hans Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Patriarch Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Abomination Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Matriarch Density']['Children']['Slider'].setValue(100)

            self.buttons['Swap Modes'].setText(' Custom ')
            self.zed_mode = 'Custom'
        else: # Swap to Default
            # Hide all custom stuff
            self.slider_panes['Slasher Omega Density']['Frame'].setVisible(False)
            self.slider_panes['Gorefast Omega Density']['Frame'].setVisible(False)
            self.slider_panes['Tiny Crawler Density']['Frame'].setVisible(False)
            self.slider_panes['Medium Crawler Density']['Frame'].setVisible(False)
            self.slider_panes['Big Crawler Density']['Frame'].setVisible(False)
            self.slider_panes['Huge Crawler Density']['Frame'].setVisible(False)
            self.slider_panes['Ultra Crawler Density']['Frame'].setVisible(False)
            self.slider_panes['Stalker Omega Density']['Frame'].setVisible(False)
            self.slider_panes['Husk Omega Density']['Frame'].setVisible(False)
            self.slider_panes['Tiny Husk Density']['Frame'].setVisible(False)
            self.slider_panes['Siren Omega Density']['Frame'].setVisible(False)
            self.slider_panes['E.D.A.R Trapper Density']['Frame'].setVisible(False)
            self.slider_panes['E.D.A.R Blaster Density']['Frame'].setVisible(False)
            self.slider_panes['E.D.A.R Bomber Density']['Frame'].setVisible(False)
            self.slider_panes['Scrake Albino Density']['Frame'].setVisible(False)
            self.slider_panes['Scrake Omega Density']['Frame'].setVisible(False)
            self.slider_panes['Scrake Emperor Density']['Frame'].setVisible(False)
            self.slider_panes['Tiny Scrake Density']['Frame'].setVisible(False)
            self.slider_panes['Fleshpound Albino Density']['Frame'].setVisible(False)
            self.slider_panes['Fleshpound Omega Density']['Frame'].setVisible(False)
            self.slider_panes['Hans Density']['Frame'].setVisible(False)
            self.slider_panes['Patriarch Density']['Frame'].setVisible(False)
            self.slider_panes['Abomination Density']['Frame'].setVisible(False)
            self.slider_panes['Matriarch Density']['Frame'].setVisible(False)

            # Set default values
            self.slider_panes['Slasher Omega Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Gorefast Omega Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Tiny Crawler Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Medium Crawler Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Big Crawler Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Huge Crawler Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Ultra Crawler Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Stalker Omega Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Husk Omega Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Tiny Husk Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Siren Omega Density']['Children']['Slider'].setValue(0)
            self.slider_panes['E.D.A.R Trapper Density']['Children']['Slider'].setValue(0)
            self.slider_panes['E.D.A.R Blaster Density']['Children']['Slider'].setValue(0)
            self.slider_panes['E.D.A.R Bomber Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Scrake Albino Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Scrake Omega Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Scrake Emperor Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Tiny Scrake Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Fleshpound Albino Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Fleshpound Omega Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Hans Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Patriarch Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Abomination Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Matriarch Density']['Children']['Slider'].setValue(0)

            self.buttons['Swap Modes'].setText(' Default ')
            self.zed_mode = 'Default'

    # Set up main window stuff
    def setup_main_area(self, Dialog):
        Dialog.setFixedSize(_WINDOWSIZE_GENERATE_W, _WINDOWSIZE_GENERATE_H)
        Dialog.setStyleSheet("background-color: rgb(50, 50, 50);")
        self.main_layout = QtWidgets.QVBoxLayout(Dialog)
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

    # Sets up the options buttons at the bottom of the window
    def setup_button_pane(self, Dialog):
        # Style stuff
        ss = 'QPushButton {color: rgb(255, 255, 255);\nbackground-color: rgb(40, 40, 40);} QToolTip {color: rgb(0, 0, 0)};' # Stylesheet
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(12)
        font.setWeight(75)

        # Create buttons
        generate_button = widget_helpers.create_button(None, None, None, text=' Generate! ', tooltip='Generate the SpawnCycle using the selected settings.', icon_path='img/icon_go.png', icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font, options=False, squad=False, draggable=False)
        generate_button.clicked.connect(self.accept_preset)
        presets_button = widget_helpers.create_button(None, None, None, text=' Presets ', tooltip='Load a preset Generator configuration.', icon_path='img/icon_presets.png', icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font, options=True, squad=False, draggable=False)
        targets =   {'Light': partial(self.load_preset, 'Light'),
                     'Moderate': partial(self.load_preset, 'Moderate'),
                     'Heavy': partial(self.load_preset, 'Heavy'),
                     'Albino': partial(self.load_preset, 'Albino'),
                     'Poundemonium': partial(self.load_preset, 'Poundemonium'),
                     'GSO': partial(self.load_preset, 'GSO'),
                     'Min Settings': partial(self.load_preset, 'Min Settings'),
                     'Max Settings': partial(self.load_preset, 'Max Settings'),
                     'Putrid Pollution': partial(self.load_preset, 'Putrid Pollution'),
                     'Sonic Subversion': partial(self.load_preset, 'Sonic Subversion'),
                     'Android Annihilation': partial(self.load_preset, 'Android Annihilation'),
                     'Arachnophobia': partial(self.load_preset, 'Arachnophobia'),
                     'Cloaked Carnage': partial(self.load_preset, 'Cloaked Carnage'),
                     'Hellish Inferno': partial(self.load_preset, 'Hellish Inferno'),
                     'Trash Only': partial(self.load_preset, 'Trash Only'),
                     'Medium Only': partial(self.load_preset, 'Medium Only'),
                     'Large Only': partial(self.load_preset, 'Large Only'),
                     'Boss Only': partial(self.load_preset, 'Boss Only'),
                     'Large-less': partial(self.load_preset, 'Large-less'),
                     'Custom Craziness': partial(self.load_preset, 'Custom Craziness'),
                     'Boss Rush': partial(self.load_preset, 'Boss Rush'),
                     'Omega Onslaught': partial(self.load_preset, 'Omega Onslaught')}
        tooltips = {'Light': 'Predominantly Trash ZEDs',
                    'Moderate': 'Decent mixture of Trash and Large ZEDs',
                    'Heavy': 'Predominantly Large ZEDs',
                    'Albino': 'Predominantly Albino ZEDs',
                    'Poundemonium': 'Predominantly Larges, spawning earlier in the cycle',
                    'GSO': 'Almost all Fleshpounds, spawning very early in the cycle',
                    'Min Settings': 'All settings are at their minimum values',
                    'Max Settings': 'All settings are at their maximum values',
                    'Putrid Pollution': 'Predominantly Bloats',
                    'Sonic Subversion': 'Predominantly Sirens',
                    'Android Annihilation': 'Predominantly E.D.A.Rs',
                    'Arachnophobia': 'Predominantly Crawlers',
                    'Cloaked Carnage': 'Predominantly Stalkers',
                    'Hellish Inferno': 'Predominantly Husks',
                    'Trash Only': 'Only Trash ZEDs spawn',
                    'Medium Only': 'Only Medium ZEDs spawn',
                    'Large Only': 'Only Large ZEDs spawn',
                    'Boss Only': 'Only Bosses spawn',
                    'Large-less': 'No Large ZEDs or Bosses at all',
                    'Custom Craziness': 'Predominantly Custom ZEDs',
                    'Boss Rush': 'Predominantly Bosses',
                    'Omega Onslaught': 'Predominantly Omega ZEDs'}
        presets_button.init_menu(targets, tooltips)

        # Setup mode button
        mode_button = widget_helpers.create_button(None, None, None, text=' Default ', tooltip='Swap the current ZED set/settings.', icon_path='img/icon_switch.png', icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font, options=False, squad=False, draggable=False)
        mode_button.clicked.connect(self.swap_modes)
        reset_button = widget_helpers.create_button(None, None, None, text=' Restore Defaults ', tooltip='Reset all settings back to their defaults.', icon_path='img/icon_clear.png', icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font, options=False, squad=False, draggable=False)
        reset_button.clicked.connect(partial(self.load_preset, 'Default', None))
        self.button_pane = QtWidgets.QFrame()

        # Insert everything into the layout
        button_pane_layout = QtWidgets.QGridLayout(self.button_pane)
        button_pane_layout.addWidget(generate_button, 0, 0, 1, 1)
        button_pane_layout.addWidget(presets_button, 0, 1, 1, 1)
        button_pane_layout.addWidget(reset_button, 0, 2, 1, 1)
        button_pane_layout.addWidget(mode_button, 0, 3, 1, 1)
        
        self.buttons.update({'Generate': generate_button})
        self.buttons.update({'Reset': reset_button})
        self.buttons.update({'Presets': presets_button})
        self.buttons.update({'Swap Modes': mode_button})

    # Sets up the scrollarea where all of the main options are
    def setup_scrollarea(self, Dialog):
        # Label stuff
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(10)
        font_label.setWeight(75)
        sp_label = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp_label.setHorizontalStretch(0)
        sp_label.setVerticalStretch(0)
        ss_label = 'QLabel {color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);}\nQToolTip {color: rgb(0, 0, 0);}' # Stylesheet
        ss_header = "color: rgb(255, 255, 255); background-color: rgba(255, 255, 255, 30);"

        # Create labels
        spacer_label1 = widget_helpers.create_label(None, text='\n', style=ss_label, font=font_label, size_policy=sp_label, alignment=QtCore.Qt.AlignCenter)
        spacer_label2 = widget_helpers.create_label(None, text='\n', style=ss_label, font=font_label, size_policy=sp_label, alignment=QtCore.Qt.AlignCenter)
        self.general_settings_label = widget_helpers.create_label(None, text='\nGeneral Settings\n', font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.general_settings_label.setStyleSheet(ss_header)
        self.general_settings_label.setFrameShape(QtWidgets.QFrame.Box)
        self.general_settings_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.general_settings_label.setLineWidth(2)

        # Create General slider panes
        wavelength_min_pane = self.create_slider_pane('Min Squads Per Wave      1   ', ' 100  ', 1, 100, 100, tooltip='Sets the MIN number of Squads that can be in a single wave.', width=384, default=8)
        wavelength_max_pane = self.create_slider_pane('Max Squads Per Wave      1   ', ' 100  ', 1, 100, 100, tooltip='Sets the MAX number of Squads that can be in a single wave.', width=384, default=15)
        squadlength_min_pane = self.create_slider_pane('Min Squad Size           1   ', ' 10   ', 1, 10, 10, tooltip='Sets the MIN number of ZEDs that can be in a single Squad.', width=384, default=3)
        squadlength_max_pane = self.create_slider_pane('Max Squad Size           1   ', ' 10   ', 1, 10, 10, tooltip='Sets the MAX number of ZEDs that can be in a single Squad.', width=384, default=7)
        albino_minwave_pane = self.create_slider_pane('Albino Min Wave          1   ', ' 10   ', 1, 10, 1, tooltip='Sets the earliest wave that Albino ZEDs can occur.', width=384, default=3)
        large_minwave_pane = self.create_slider_pane('Large ZED Min Wave       1   ', ' 10   ', 1, 10, 1, tooltip='Sets the earliest wave that Large ZEDs can spawn.', width=384, default=4)
        spawnrage_minwave_pane = self.create_slider_pane('SpawnRage Min Wave       1   ', ' 10   ', 1, 10, 1, tooltip='Sets the earliest wave that SpawnRaged FP/QP/AFP can occur.', width=384, default=7)
        boss_minwave_pane = self.create_slider_pane('Boss Min Wave            1   ', ' 10   ', 1, 10, 1, tooltip='Sets the earliest wave that Bosses can spawn.', width=384, default=7)

        # Specific settings needed for the gamelength slider since it affects the others
        gamelength_pane = self.create_slider_pane('SpawnCycle Length      Short ', ' Long', 1, 3, 1, tooltip='Sets the length of the SpawnCycle:\nShort = 4 Waves\nMedium = 7 Waves\nLong = 10 Waves', width=384, text_box=False)
        affected = [albino_minwave_pane['Children'], large_minwave_pane['Children'], spawnrage_minwave_pane['Children'], boss_minwave_pane['Children']]
        gamelength_pane['Children']['Slider'].valueChanged.connect(partial(self.update_slider_gamelength, gamelength_pane['Children']['Slider'], affected))
        
        # Add this stuff to the global dict to access later
        self.slider_panes.update({'Game Length': gamelength_pane})
        self.slider_panes.update({'Min Squads': wavelength_min_pane})
        self.slider_panes.update({'Max Squads': wavelength_max_pane})
        self.slider_panes.update({'Squad Min Length': squadlength_min_pane})
        self.slider_panes.update({'Squad Max Length': squadlength_max_pane})
        self.slider_panes.update({'Albino Min Wave': albino_minwave_pane})
        self.slider_panes.update({'Large Min Wave': large_minwave_pane})
        self.slider_panes.update({'SpawnRage Min Wave': spawnrage_minwave_pane})
        self.slider_panes.update({'Boss Min Wave': boss_minwave_pane})

        density_tooltip_pfx = 'Sets the relative Density for'
        density_tooltip_sfx = 'to appear in the SpawnCycle.'

        # Create Global Density slider panes
        self.density_settings_label = widget_helpers.create_label(None, text='\nCategory Settings\n', font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.density_settings_label.setStyleSheet(ss_header)
        self.density_settings_label.setFrameShape(QtWidgets.QFrame.Box)
        self.density_settings_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.density_settings_label.setLineWidth(2)
        trash_density_pane = self.create_slider_pane('Trash Density           0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Trash ZEDs {density_tooltip_sfx}", width=384)
        medium_density_pane = self.create_slider_pane('Medium Density          0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Medium ZEDs {density_tooltip_sfx}", width=384)
        large_density_pane = self.create_slider_pane('Large Density           0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Large ZEDs {density_tooltip_sfx}", width=384)
        boss_density_pane = self.create_slider_pane('Boss Density            0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Bosses {density_tooltip_sfx}", width=384, default=0)

        # Add this stuff to the global dict to access later
        self.slider_panes.update({'Trash Density': trash_density_pane})
        self.slider_panes.update({'Medium Density': medium_density_pane})
        self.slider_panes.update({'Large Density': large_density_pane})
        self.slider_panes.update({'Boss Density': boss_density_pane})

        # Create ZED labels
        self.trash_label = widget_helpers.create_label(None, text='\nTrash ZEDs', style=ss_label, font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.medium_label = widget_helpers.create_label(None, text='\n\nMedium ZEDs', style=ss_label, font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.large_label = widget_helpers.create_label(None, text='\n\nLarge ZEDs', style=ss_label, font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.boss_label = widget_helpers.create_label(None, text='\n\nBosses', style=ss_label, font=font_label, alignment=QtCore.Qt.AlignCenter)

        # Create ZED settings slider panes
        self.zed_settings_label = widget_helpers.create_label(None, text='\nZED Settings\n', font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.zed_settings_label.setStyleSheet(ss_header)
        self.zed_settings_label.setFrameShape(QtWidgets.QFrame.Box)
        self.zed_settings_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.zed_settings_label.setLineWidth(2)

        cyst_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Cysts {density_tooltip_sfx}")
        slasher_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Slashers {density_tooltip_sfx}")
        slasher_omega_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Slasher Omegas {density_tooltip_sfx}")
        alphaclot_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Alpha Clots {density_tooltip_sfx}")
        alphaclot_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Alpha Clots to become Rioters.', width=256, default=30)
        gorefast_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Gorefasts {density_tooltip_sfx}")
        gorefast_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Gorefasts to become Gorefiends.', width=256, default=30)
        gorefast_omega_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Gorefast Omegas {density_tooltip_sfx}")
        crawler_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Crawlers {density_tooltip_sfx}")
        crawler_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Crawlers to become Elite Crawlers.', width=256, default=30)
        crawler_tiny_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Tiny Crawlers {density_tooltip_sfx}")
        crawler_medium_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Medium Crawlers {density_tooltip_sfx}")
        crawler_big_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Big Crawlers {density_tooltip_sfx}")
        crawler_huge_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Huge Crawlers {density_tooltip_sfx}")
        crawler_ultra_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Ultra Crawlers {density_tooltip_sfx}")
        stalker_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Stalkers {density_tooltip_sfx}")
        stalker_omega_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Stalker Omegas {density_tooltip_sfx}")
        bloat_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Bloats {density_tooltip_sfx}")
        husk_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Husks {density_tooltip_sfx}")
        husk_omega_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Husk Omegas {density_tooltip_sfx}")
        husk_tiny_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Tiny Husks {density_tooltip_sfx}")
        siren_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Sirens {density_tooltip_sfx}")
        siren_omega_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Siren Omegas {density_tooltip_sfx}")
        edar_trapper_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} E.D.A.R Trappers {density_tooltip_sfx}")
        edar_blaster_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} E.D.A.R Blasters {density_tooltip_sfx}")
        edar_bomber_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} E.D.A.R Bombers {density_tooltip_sfx}")
        scrake_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Scrakes {density_tooltip_sfx}")
        scrake_omega_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Scrake Omegas {density_tooltip_sfx}")
        scrake_emperor_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Scrake Emperors {density_tooltip_sfx}")
        scrake_tiny_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Tiny Scrakes {density_tooltip_sfx}")
        quarterpound_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Quarter Pounds {density_tooltip_sfx}")
        quarterpound_rage_pane = self.create_slider_pane('SpawnRage Chance      0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Quarter Pounds to spawn Enraged.', width=256, default=10)
        fleshpound_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Fleshpounds {density_tooltip_sfx}")
        fleshpound_rage_pane = self.create_slider_pane('SpawnRage Chance      0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Fleshpounds/Alpha Fleshpounds to spawn Enraged.', width=256, default=10)
        fleshpound_omega_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Fleshpound Omegas {density_tooltip_sfx}")
        scrake_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Scrakes to become Alpha Scrakes.', width=256, default=30)
        fleshpound_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Fleshpounds to become Alpha Fleshpounds.', width=256, default=30)
        hans_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} Dr. Hans Volter {density_tooltip_sfx}")
        patriarch_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} the Patriarch {density_tooltip_sfx}")
        kingfleshpound_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} King Fleshpound {density_tooltip_sfx}")
        abomination_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} the Abomination {density_tooltip_sfx}")
        matriarch_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} the Matriarch {density_tooltip_sfx}")
        abominationspawn_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} Abomination Spawns {density_tooltip_sfx}")

        # Add buttons into hboxes
        cyst_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Cyst'))
        slasher_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Slasher'))
        slasher_omega_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Slasher Omega'))
        alphaclot_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Alpha Clot'))
        gorefast_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Gorefast'))
        gorefast_omega_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Gorefast Omega'))
        crawler_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Crawler'))
        crawler_tiny_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Tiny Crawler'))
        crawler_medium_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Medium Crawler'))
        crawler_big_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Big Crawler'))
        crawler_huge_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Huge Crawler'))
        crawler_ultra_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Ultra Crawler'))
        stalker_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Stalker'))
        stalker_omega_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Stalker Omega'))
        bloat_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Bloat'))
        husk_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Husk'))
        husk_omega_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Husk Omega'))
        husk_tiny_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Tiny Husk'))
        siren_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Siren'))
        siren_omega_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Siren Omega'))
        edar_trapper_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('E.D.A.R Trapper'))
        edar_blaster_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('E.D.A.R Blaster'))
        edar_bomber_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('E.D.A.R Bomber'))
        scrake_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Scrake'))
        scrake_omega_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Scrake Omega'))
        scrake_emperor_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Scrake Emperor'))
        scrake_tiny_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Tiny Scrake'))
        quarterpound_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Quarter Pound'))
        fleshpound_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Fleshpound'))
        fleshpound_omega_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Fleshpound Omega'))
        hans_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Dr. Hans Volter'))
        patriarch_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Patriarch'))
        kingfleshpound_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('King Fleshpound'))
        abomination_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Abomination'))
        matriarch_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Matriarch'))
        abominationspawn_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Abomination Spawn'))

        # Add this stuff to the global dict to access later
        self.slider_panes.update({'Cyst Density': cyst_pane})
        self.slider_panes.update({'Slasher Density': slasher_pane})
        self.slider_panes.update({'Slasher Omega Density': slasher_omega_pane})
        self.slider_panes.update({'Alpha Clot Density': alphaclot_pane})
        self.slider_panes.update({'Alpha Clot Albino Density': alphaclot_albino_pane})
        self.slider_panes.update({'Gorefast Density': gorefast_pane})
        self.slider_panes.update({'Gorefast Albino Density': gorefast_albino_pane})
        self.slider_panes.update({'Gorefast Omega Density': gorefast_omega_pane})
        self.slider_panes.update({'Crawler Density': crawler_pane})
        self.slider_panes.update({'Crawler Albino Density': crawler_albino_pane})
        self.slider_panes.update({'Tiny Crawler Density': crawler_tiny_pane})
        self.slider_panes.update({'Medium Crawler Density': crawler_medium_pane})
        self.slider_panes.update({'Big Crawler Density': crawler_big_pane})
        self.slider_panes.update({'Huge Crawler Density': crawler_huge_pane})
        self.slider_panes.update({'Ultra Crawler Density': crawler_ultra_pane})
        self.slider_panes.update({'Stalker Density': stalker_pane})
        self.slider_panes.update({'Stalker Omega Density': stalker_omega_pane})
        self.slider_panes.update({'Bloat Density': bloat_pane})
        self.slider_panes.update({'Husk Density': husk_pane})
        self.slider_panes.update({'Husk Omega Density': husk_omega_pane})
        self.slider_panes.update({'Tiny Husk Density': husk_tiny_pane})
        self.slider_panes.update({'Siren Density': siren_pane})
        self.slider_panes.update({'Siren Omega Density': siren_omega_pane})
        self.slider_panes.update({'E.D.A.R Trapper Density': edar_trapper_pane})
        self.slider_panes.update({'E.D.A.R Blaster Density': edar_blaster_pane})
        self.slider_panes.update({'E.D.A.R Bomber Density': edar_bomber_pane})
        self.slider_panes.update({'Scrake Density': scrake_pane})
        self.slider_panes.update({'Scrake Albino Density': scrake_albino_pane})
        self.slider_panes.update({'Scrake Omega Density': scrake_omega_pane})
        self.slider_panes.update({'Scrake Emperor Density': scrake_emperor_pane})
        self.slider_panes.update({'Tiny Scrake Density': scrake_tiny_pane})
        self.slider_panes.update({'Quarter Pound Density': quarterpound_pane})
        self.slider_panes.update({'Quarter Pound Rage Density': quarterpound_rage_pane})
        self.slider_panes.update({'Fleshpound Density': fleshpound_pane})
        self.slider_panes.update({'Fleshpound Albino Density': fleshpound_albino_pane})
        self.slider_panes.update({'Fleshpound Rage Density': fleshpound_rage_pane})
        self.slider_panes.update({'Fleshpound Omega Density': fleshpound_omega_pane})
        self.slider_panes.update({'Hans Density': hans_pane})
        self.slider_panes.update({'Patriarch Density': patriarch_pane})
        self.slider_panes.update({'King Fleshpound Density': kingfleshpound_pane})
        self.slider_panes.update({'Abomination Density': abomination_pane})
        self.slider_panes.update({'Matriarch Density': matriarch_pane})
        self.slider_panes.update({'Abomination Spawn Density': abominationspawn_pane})

        # Insert everything into the layout(s)
        self.scrollarea_contents_layout.addWidget(self.general_settings_label)
        self.scrollarea_contents_layout.addWidget(gamelength_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(wavelength_min_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(wavelength_max_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(squadlength_min_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(squadlength_max_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(albino_minwave_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(large_minwave_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(spawnrage_minwave_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(boss_minwave_pane['Frame'])

        self.scrollarea_contents_layout.addWidget(spacer_label1)
        self.scrollarea_contents_layout.addWidget(self.density_settings_label)
        self.scrollarea_contents_layout.addWidget(trash_density_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(medium_density_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(large_density_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(boss_density_pane['Frame'])

        self.scrollarea_contents_layout.addWidget(spacer_label2)
        self.scrollarea_contents_layout.addWidget(self.zed_settings_label)
        self.scrollarea_contents_layout.addWidget(self.trash_label)
        self.scrollarea_contents_layout.addWidget(cyst_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(slasher_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(slasher_omega_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(alphaclot_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(alphaclot_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(gorefast_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(gorefast_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(gorefast_omega_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(crawler_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(crawler_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(crawler_tiny_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(crawler_medium_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(crawler_big_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(crawler_huge_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(crawler_ultra_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(stalker_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(stalker_omega_pane['Frame'])

        self.scrollarea_contents_layout.addWidget(self.medium_label)
        self.scrollarea_contents_layout.addWidget(bloat_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(husk_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(husk_omega_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(husk_tiny_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(siren_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(siren_omega_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(edar_trapper_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(edar_blaster_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(edar_bomber_pane['Frame'])

        self.scrollarea_contents_layout.addWidget(self.large_label)
        self.scrollarea_contents_layout.addWidget(scrake_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(scrake_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(scrake_omega_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(scrake_emperor_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(scrake_tiny_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(quarterpound_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(quarterpound_rage_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(fleshpound_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(fleshpound_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(fleshpound_rage_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(fleshpound_omega_pane['Frame'])

        self.scrollarea_contents_layout.addWidget(self.boss_label)
        self.scrollarea_contents_layout.addWidget(hans_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(patriarch_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(kingfleshpound_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(abomination_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(matriarch_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(abominationspawn_pane['Frame'])

    # Called when this dialog is closed
    def teardown(self):
        last_preset = list(self.get_slider_values().values())
        last_preset[0] = (1 if last_preset[0] == 4 else (2 if last_preset[0] == 7 else 3))
        self.parent.last_generate_mode = self.zed_mode
        self.parent.last_generate_preset = last_preset

    # Loads a preset into the generator
    def load_preset(self, preset):
        presets = {'Light': [3, 15, 20, 3, 5, 5, 7, 10, 10,                        100, 50, 15, 0,               100, 100, 0, 100, 5, 100, 5, 0, 100, 5, 0, 0, 0, 0, 0, 100, 0,                      100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 0, 100, 0, 0, 0,                   0, 0, 0, 0, 0, 0],
                   'Moderate': [3, 20, 25, 4, 7, 4, 4, 8, 10,                      75, 60, 35, 0,                100, 100, 0, 100, 10, 100, 10, 0, 100, 10, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Heavy': [3, 30, 35, 5, 10, 2, 2, 7, 10,                        60, 50, 40, 0,                100, 100, 0, 100, 15, 100, 15, 0, 100, 15, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 10, 100, 0, 10, 0,                 0, 0, 0, 0, 0, 0],
                   'Albino': [3, 25, 30, 4, 8, 1, 4, 8, 10,                        100, 30, 30, 0,               50, 50, 0, 100, 80, 100, 80, 0, 100, 80, 0, 0, 0, 0, 0, 50, 0,                      100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Poundemonium': [3, 25, 35, 5, 10, 4, 3, 8, 10,                 30, 30, 65, 0,                100, 100, 0, 100, 15, 100, 15, 0, 100, 15, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   50, 0, 0, 0, 0, 100, 7, 100, 0, 7, 0,                    0, 0, 0, 0, 0, 0],
                   'GSO': [3, 25, 40, 8, 10, 4, 3, 5, 10,                          15, 15, 100, 0,               100, 100, 0, 100, 15, 100, 15, 0, 100, 15, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   10, 0, 0, 0, 0, 100, 12, 100, 0, 12, 0,                  0, 0, 0, 0, 0, 0],
                   'Min Settings': [1, 1, 50, 1, 8, 1, 1, 1, 4,                    100, 100, 100, 0,             100, 100, 0, 100, 0, 100, 0, 0, 100, 0, 0, 0, 0, 0, 0, 100, 0,                      100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 0, 100, 0, 0, 0,                   0, 0, 100, 0, 0, 100],
                   'Max Settings': [3, 100, 100, 10, 10, 1, 1, 1, 10,              100, 100, 100, 0,             100, 100, 0, 100, 100, 100, 100, 0, 100, 100, 0, 0, 0, 0, 0, 100, 0,                100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 100, 100, 0, 100, 0,               0, 0, 100, 0, 0, 100],
                   'Putrid Pollution': [3, 15, 25, 5, 8, 3, 5, 10, 10,             60, 75, 10, 0,                100, 100, 0, 100, 5, 100, 5, 0, 100, 5, 0, 0, 0, 0, 0, 100, 0,                      100, 30, 0, 0, 30, 0, 0, 0, 0,                     100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Sonic Subversion': [3, 15, 25, 5, 8, 3, 5, 10, 10,             60, 75, 10, 0,                100, 100, 0, 100, 5, 100, 5, 0, 100, 5, 0, 0, 0, 0, 0, 100, 0,                      30, 30, 0, 0, 100, 0, 0, 0, 0,                     100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Android Annihilation': [3, 15, 25, 5, 8, 3, 5, 10, 10,         60, 75, 10, 0,                100, 100, 0, 100, 5, 100, 5, 0, 100, 5, 0, 0, 0, 0, 0, 100, 0,                      30, 30, 0, 0, 30, 0, 10, 100, 100,                 100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Arachnophobia': [3, 15, 25, 5, 8, 3, 5, 10, 10,                100, 10, 10, 0,               10, 10, 0, 10, 5, 10, 5, 0, 100, 15, 0, 0, 0, 0, 0, 10,  0,                         100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Cloaked Carnage': [3, 15, 25, 5, 8, 3, 5, 10, 10,              100, 10, 10, 0,               10, 10, 0, 10, 5, 10, 5, 0, 10, 5, 0, 0, 0, 0, 0, 100, 0,                           100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Hellish Inferno': [2, 15, 25, 5, 10, 2, 4, 7, 7,               10, 100, 10, 0,               100, 100, 0, 100, 10, 100, 10, 0, 100, 10, 0, 0, 0, 0, 0, 100, 0,                   0, 100, 0, 0, 0, 0, 0, 0, 0,                       100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Trash Only': [3, 15, 20, 1, 4, 3, 4, 8, 10,                    100, 0, 0, 0,                 100, 100, 0, 100, 10, 100, 10, 0, 100, 10, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Medium Only': [3, 15, 20, 1, 4, 3, 4, 8, 10,                   0, 100, 0, 0,                 100, 100, 0, 100, 10, 100, 10, 0, 100, 10, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Large Only': [3, 15, 20, 1, 4, 3, 1, 8, 10,                    0, 0, 100, 0,                 100, 100, 0, 100, 10, 100, 10, 0, 100, 10, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   0, 0, 0, 0, 0, 0],
                   'Boss Only': [3, 15, 20, 1, 4, 3, 4, 8, 1,                      0, 0, 0, 100,                 100, 100, 0, 100, 10, 100, 10, 0, 100, 10, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 5, 100, 0, 5, 0,                   100, 100, 100, 100, 100, 100],
                   'Large-less': [2, 15, 25, 5, 10, 3, 7, 7, 7,                    100, 100, 0, 0,               100, 100, 0, 100, 30, 100, 30, 0, 100, 30, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 10, 100, 0, 10, 0,                 0, 0, 0, 0, 0, 0],
                   'Custom Craziness': [3, 20, 30, 3, 6, 2, 4, 7, 7,               100, 100, 100, 50,            100, 100, 0, 100, 10, 100, 10, 0, 100, 10, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 100, 100, 100,             100, 35, 0, 0, 0, 75, 8, 100, 35, 8, 0,                  100, 100, 100, 100, 100, 0],
                   'Boss Rush': [1, 15, 20, 3, 6, 2, 3, 4, 2,                      10, 10, 10, 100,              100, 100, 0, 10, 100, 100, 100, 0, 10, 10, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 100, 100, 100,             100, 15, 0, 0, 0, 100, 5, 100, 15, 5, 0,                 100, 100, 100, 100, 100, 0],
                   'Omega Onslaught': [3, 8, 15, 3, 7, 3, 4, 10, 10,               100, 100, 100, 0,             100, 100, 75, 100, 10, 100, 10, 75, 100, 10, 20, 20, 20, 5, 5, 100, 75,             100, 100, 75, 15, 100, 75, 0, 0, 0,                100, 0, 15, 5, 15, 100, 0, 100, 0, 0, 60,                0, 0, 0, 0, 0, 0],
                   'Default': [3, 8, 15, 3, 7, 3, 4, 7, 7,                         100, 100, 100, 0,             100, 100, 0, 100, 30, 100, 30, 0, 100, 30, 0, 0, 0, 0, 0, 100, 0,                   100, 100, 0, 0, 100, 0, 0, 0, 0,                   100, 0, 0, 0, 0, 100, 10, 100, 0, 10, 0,                 0, 0, 100, 0, 0, 100]}

        if isinstance(preset, list): # This an old preset from last generation
            preset_data = preset
            if self.parent.last_generate_mode is not None and self.parent.last_generate_mode == 'Custom':
                self.swap_modes()
                self.swap_modes()
            elif self.parent.last_generate_mode is not None and self.parent.last_generate_mode == 'Default':
                self.swap_modes()
        else: # User selected a preset from the menu
            preset_data = presets[preset]

            # Swap to the appropriate ZED set for these presets for the first time
            if preset == 'Default' and self.zed_mode == 'Custom':
                self.swap_modes()
            elif preset in ['Boss Rush', 'Custom Craziness', 'Boss Only', 'Android Annihilation', 'Omega Onslaught'] and self.zed_mode == 'Default':
                self.swap_modes()
            elif preset not in ['Boss Rush', 'Custom Craziness', 'Boss Only', 'Android Annihilation', 'Omega Onslaught'] and self.zed_mode == 'Custom':
                self.swap_modes()

        # Activate the preset
        sliders = [x['Children']['Slider'] for x in self.slider_panes.values()]
        for i in range(len(preset_data)):
            sliders[i].setValue(preset_data[i])

    # Returns true if the entire list has the given value for each cell
    def all_value(self, lst, value):
        for val in lst:
            if val != value:
                return False
        return True

    # Checks if its possible to generate
    def check_state(self):
        errors = []
        sv = self.get_slider_values() 
        trash_vals = [sv['Cyst Density'], sv['Alpha Clot Density'], sv['Slasher Density'], sv['Gorefast Density'], sv['Crawler Density'], sv['Stalker Density']]
        medium_vals = [sv['Bloat Density'], sv['Husk Density'], sv['Siren Density'], sv['E.D.A.R Trapper Density'], sv['E.D.A.R Blaster Density'], sv['E.D.A.R Bomber Density']]
        large_vals = [sv['Scrake Density'], sv['Quarter Pound Density'], sv['Fleshpound Density']]
        boss_vals = [sv['Hans Density'], sv['Patriarch Density'], sv['King Fleshpound Density'], sv['Abomination Density'], sv['Matriarch Density'], sv['Abomination Spawn Density']]

        # Ensure slider values are correct
        if sv['Min Squads'] > sv['Max Squads']:
            errors.append(f"- Min Squads Per Wave must be <= Max Squads Per Wave")
        if sv['Squad Min Length'] > sv['Squad Max Length']:
            errors.append(f"- Min Squad Size must be <= Max Squad Size")
        if sv['Trash Density'] != 0 and self.all_value(trash_vals, 0):
            errors.append(f"- Trash Density found to be non-zero but all ZEDs in category have 0% Density!")
        if sv['Medium Density'] != 0 and self.all_value(medium_vals, 0):
            errors.append(f"- Medium Density found to be non-zero but all ZEDs in category have 0% Density!")
        if sv['Large Density'] != 0 and self.all_value(large_vals, 0):
            errors.append(f"- Large Density found to be non-zero but all ZEDs in category have 0% Density!")
        if sv['Boss Density'] != 0 and self.all_value(boss_vals, 0):
            errors.append(f"- Boss Density found to be non-zero but all ZEDs in category have 0% Density!")
        if sv['Trash Density'] == 0 and sv['Medium Density'] == 0 and sv['Large Density'] == 0 and sv['Boss Density'] == 0:
            errors.append(f"- At least one Category Density setting must be non-zero!")
        if sv['Large Min Wave'] > 1 and sv['Trash Density'] == 0 and sv['Medium Density'] == 0 and sv['Large Density'] > 0 and sv['Boss Density'] == 0:
            errors.append(f"- Params suggest Larges Only but Large ZED Min Wave found to be > 1!")
        if sv['Boss Min Wave'] > 1 and sv['Trash Density'] == 0 and sv['Medium Density'] == 0 and sv['Large Density'] == 0 and sv['Boss Density'] > 0:
            errors.append(f"- Params suggest Bosses Only but Boss Min Wave found to be > 1!")
        if sv['Large Min Wave'] > 1 and sv['Boss Min Wave'] > 1 and sv['Trash Density'] == 0 and sv['Medium Density'] == 0 and sv['Large Density'] > 0 and sv['Boss Density'] > 0:
            errors.append(f"- Params suggest Larges/Bosses Only but Large ZED Min Wave and Boss Min Wave found to be > 1!")

        return errors

    # Compiles all current slider data and passes it back to the main window
    def accept_preset(self):
        # Check slider values first to make sure they're okay
        errors = self.check_state()

        if len(errors) > 0: # Errors occurred
            # Show a dialog explaining this
            diag_title = 'SpawnCycler'
            x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
            y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
            err_text = '\n'.join(errors)
            diag_text = f"The following error(s) were encountered while attempting to Generate:\n\n{err_text}\n"
            diag = widget_helpers.create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
            diag.exec_() # Show a dialog to tell user to check messages
        else: # No errors. Good to go!
            self.parent.generate_wavedefs(self.get_slider_values())

    # Returns the values of all sliders as a neatly formatted dict
    def get_slider_values(self):
        slider_vals = {}
        for (key, data) in self.slider_panes.items():
            slider_vals.update({key: data['Children']['Slider'].value()})

        # Change game length at last second (to actual wave count)
        if slider_vals['Game Length'] == 3:
            slider_vals['Game Length'] = 10
        elif slider_vals['Game Length'] == 2:
            slider_vals['Game Length'] = 7
        else:
            slider_vals['Game Length'] = 4

        return slider_vals

    def setupUi(self):
        self.setup_main_area(self.Dialog) # Set up main window stuff
        self.setup_button_pane(self.Dialog) # Set up the options buttons at the bottom
        self.setup_scrollarea(self.Dialog) # Sets up the scrollarea where all of the main options are
        
        # Put everything in
        self.main_layout.addWidget(self.scrollarea)
        self.main_layout.addWidget(self.button_pane)

        self.retranslateUi(self.Dialog)
        QtCore.QMetaObject.connectSlotsByName(self.Dialog)

        # Swap back to default mode
        if self.parent.last_generate_preset is not None:
            self.load_preset(self.parent.last_generate_preset)
        else:
            self.swap_modes()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate


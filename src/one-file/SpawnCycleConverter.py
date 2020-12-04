#
#  SpawnCycleConverter.py
#
#  Author: Tamari (Nathan P. Ybanez)
#  Date of creation: 12/1/2020
#
#  Addon for SpawnCycler that converts a set of standard CD SpawnCycles
#  into a bundled JSON for use with Forrest Mark X's build of Controlled Difficulty
#

from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import date, datetime
from functools import partial
from copy import deepcopy
import json
import os

_DEF_FONT_FAMILY = 'Consolas'


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


# Resolves the path for an image (used for pyinstaller)
def resource_path(relative_path):
    #return relative_path
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    #print(f'returning {os.path.join(base_path, relative_path)}')
    return os.path.join(base_path, relative_path)


# Creates and returns a simple dialog box with an OK button (if specified)
def create_simple_dialog(parent, title, text, x, y, button=True, button_target=None):
    dialog = QtWidgets.QDialog()
    dialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint|QtCore.Qt.WindowTitleHint) # Disable X and minimize
    hbox_master = QtWidgets.QHBoxLayout(dialog)

    # Set up text label
    dialog_label = QtWidgets.QLabel(dialog)
    font = QtGui.QFont()
    font.setPointSize(8)
    font.setBold(True)
    dialog_label.setObjectName('dialog_label')
    dialog_label.setFont(font)
    dialog_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
    dialog_label.setStyleSheet("color: rgb(255, 255, 255);")
    dialog_label.setText(text)

    # Set up OK button
    if button:
        ok_button = QtWidgets.QPushButton('OK')
        ok_button.setStyleSheet("color: rgb(255, 255, 255);")
        ok_button.setObjectName('ok_button')
        
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(ok_button.sizePolicy().hasHeightForWidth())
        ok_button.setSizePolicy(sp)

        if button_target is not None:
            ok_button.clicked.connect(button_target)
        else:
            ok_button.clicked.connect(dialog.close)

    # Set layout
    vbox = QtWidgets.QVBoxLayout()
    vbox.setObjectName('vbox')
    hbox = QtWidgets.QHBoxLayout()
    hbox.setObjectName('hbox')
    if button:
        hbox.addWidget(ok_button)
    vbox.addWidget(dialog_label)
    vbox.addLayout(hbox)
    hbox_master.addLayout(vbox)

    # Set up window
    dialog.setWindowTitle(title)
    dialog.setStyleSheet("background-color: rgb(40, 40, 40);")

    # Move to x, y
    dialog.move(x, y)

    return dialog


# Returns a QLabel with the given parameters
def create_label(parent, text=None, tooltip=None, style=None, font=None, size_policy=None, alignment=None):
    label = QtWidgets.QLabel(parent)

    if text is not None: # Set button text
        label.setText(text)

    if tooltip is not None:
        label.setToolTip(tooltip)

    if size_policy is not None: # Set size policy
        label.setSizePolicy(size_policy)

    if font is not None: # Set font
        label.setFont(font)

    if style is not None: # Set style sheet
        label.setStyleSheet(style)

    if alignment is not None:
        label.setAlignment(alignment)
    else:
        label.setAlignment(QtCore.Qt.AlignCenter)

    return label


# Returns a QButton with the given parameters
def create_button(parent, text=None, target=None, tooltip=None, style=None, icon_path=None, icon_w=None, icon_h=None, font=None, size_policy=None):
    button = QtWidgets.QPushButton(parent)

    if target is not None: # Button is assigned to do something on-click
        button.clicked.connect(target)

    if text is not None: # Set button text
        button.setText(text)

    if tooltip is not None: # Set button tooltip
        button.setToolTip(tooltip)

    if style is not None: # Set style sheet
        button.setStyleSheet(style)

    if icon_path is not None: # Set icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(icon_w, icon_h))

    if size_policy is not None: # Set size policy
        button.setSizePolicy(size_policy)

    if font is not None: # Set font
        button.setFont(font)

    return button


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
def parse_syntax_import(filename, lines):
    waves = deepcopy(lines)
    total_ids = [] # Combination of all id lists for easy checking
    for l in zed_tokens.values():
        total_ids += l
    valid_quantifiers = ['*', '!']

    parse_prefix = f"Parse errors ('{filename}'):\n\n"

    errors = []

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


class Ui_MainWindow(object):
    def __init__(self):
        pass

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

    # Initializes the fields
    def setup_fields(self):
        ss = 'color: rgb(255, 255, 255);' # Stylesheet
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        font_label = QtGui.QFont()
        font_label.setFamily(_DEF_FONT_FAMILY)
        font_label.setPointSize(12)
        font_label.setWeight(75)
        font_textfield = QtGui.QFont()
        font_textfield.setFamily(_DEF_FONT_FAMILY)
        font_textfield.setPointSize(10)
        font_textfield.setWeight(75)

        # Create "SpawnCycle Name" Label and Textbox
        name_label = create_label(self.central_widget, text='SpawnCycle Name', style=ss, font=font_label)
        name_label.setAlignment(QtCore.Qt.AlignLeft)
        self.name_widget = QtWidgets.QLineEdit()
        self.name_widget.setStyleSheet(ss)
        self.name_widget.setSizePolicy(sp)
        self.name_widget.setMaximumSize(QtCore.QSize(256, 28))
        self.name_widget.setFont(font_textfield)
        self.name_widget.setText('')
        self.name_widget.setAlignment(QtCore.Qt.AlignLeft)
        self.name_widget.setStyleSheet('color: rgb(255, 255, 255); background-color: rgb(60, 60, 60);')

        # Create "Author" Label and Textbox
        author_label = create_label(self.central_widget, text='\nAuthor', style=ss, font=font_label)
        author_label.setAlignment(QtCore.Qt.AlignLeft)
        self.author_widget = QtWidgets.QLineEdit()
        self.author_widget.setStyleSheet(ss)
        self.author_widget.setSizePolicy(sp)
        self.author_widget.setMaximumSize(QtCore.QSize(256, 28))
        self.author_widget.setFont(font_textfield)
        self.author_widget.setText('')
        self.author_widget.setAlignment(QtCore.Qt.AlignLeft)
        self.author_widget.setStyleSheet('color: rgb(255, 255, 255); background-color: rgb(60, 60, 60);')

        # Create "Creation Date" Label and Calendar
        date_label = create_label(self.central_widget, text='\nCreation Date', style=ss, font=font_label)
        date_label.setAlignment(QtCore.Qt.AlignLeft)
        date_frame = QtWidgets.QFrame()
        date_frame.setSizePolicy(sp)
        date_layout = QtWidgets.QHBoxLayout(date_frame)
        self.date_widget = QtWidgets.QCalendarWidget()
        self.date_widget.setMinimumDate(QtCore.QDate(2018, 1, 1))
        today = date.today()
        self.date_widget.setMaximumDate(QtCore.QDate(today.year, today.month, today.day)) # Max date is today
        self.date_widget.setGridVisible(True)
        self.date_widget.setSizePolicy(sp)
        self.date_widget.setStyleSheet("color: rgb(0, 0, 0); background-color: rgb(200, 200, 200);")
        date_frame.setStyleSheet(ss)
        date_frame.setFrameShape(QtWidgets.QFrame.Box)
        date_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        date_frame.setLineWidth(2)
        date_layout.addWidget(self.date_widget)

        file1_label = create_label(self.central_widget, text='\nShort (4 Wave) SpawnCycle', style=ss, font=font_label)
        file2_label = create_label(self.central_widget, text='\nMedium (7 Wave) SpawnCycle', style=ss, font=font_label)
        file3_label = create_label(self.central_widget, text='\nLong (10 Wave) SpawnCycle', style=ss, font=font_label)
        file1_frame, file1_widget = self.create_browsefield()
        file2_frame, file2_widget = self.create_browsefield()
        file3_frame, file3_widget = self.create_browsefield()
        file1_label.setAlignment(QtCore.Qt.AlignLeft)
        file2_label.setAlignment(QtCore.Qt.AlignLeft)
        file3_label.setAlignment(QtCore.Qt.AlignLeft)
        self.file1_widget = file1_widget
        self.file2_widget = file2_widget
        self.file3_widget = file3_widget


        # Create go button
        filler_label = create_label(self.central_widget, text='\n', style=ss, font=font_label)
        self.convert_button = create_button(None, text=' Convert! ', icon_path=resource_path('img/icon_go.png'), icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font_label)
        self.convert_button.setStyleSheet('color: rgb(255, 255, 255); background-color: rgb(60, 60, 60);')
        self.convert_button.clicked.connect(self.convert_spawncycles)

        self.scrollarea_layout.addWidget(name_label)
        self.scrollarea_layout.addWidget(self.name_widget)
        self.scrollarea_layout.addWidget(author_label)
        self.scrollarea_layout.addWidget(self.author_widget)
        self.scrollarea_layout.addWidget(date_label)
        self.scrollarea_layout.addWidget(date_frame)
        self.scrollarea_layout.addWidget(file1_label)
        self.scrollarea_layout.addWidget(file1_frame)
        self.scrollarea_layout.addWidget(file2_label)
        self.scrollarea_layout.addWidget(file2_frame)
        self.scrollarea_layout.addWidget(file3_label)
        self.scrollarea_layout.addWidget(file3_frame)
        self.scrollarea_layout.addWidget(filler_label)
        self.scrollarea_layout.addWidget(self.convert_button)

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
        ss_textedit = 'color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);'

        # Set up Messages area
        label_messages = create_label(self.central_widget, text='\nMessages', style=ss_label, font=font_label)
        label_messages.setAlignment(QtCore.Qt.AlignLeft)
        
        # Set up Messages area
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.messages_textedit = QtWidgets.QTextEdit(self.central_widget)
        self.messages_textedit.setReadOnly(True)
        self.messages_textedit.setMinimumSize(QtCore.QSize(0, 64))
        self.messages_textedit.setSizePolicy(sp)
        self.messages_textedit.setFont(font_messages)
        self.messages_textedit.setStyleSheet(ss_textedit)
        self.messages_textedit.setFrameShape(QtWidgets.QFrame.Box)
        self.messages_textedit.setFrameShadow(QtWidgets.QFrame.Plain)
        self.messages_textedit.setLineWidth(2)


        # Add to central layout
        self.scrollarea_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.scrollarea_layout.addWidget(label_messages)
        self.scrollarea_layout.addWidget(self.messages_textedit)

    # Creates a textfield with a Browse button
    def create_browsefield(self):
        textfield_frame = QtWidgets.QFrame()
        textfield_layout = QtWidgets.QHBoxLayout(textfield_frame)
        textfield_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Create text edit
        ss = 'color: rgb(255, 255, 255); background-color: rgb(60, 60, 60);' # Stylesheet
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(10)
        font.setWeight(75)
        textfield = QtWidgets.QLineEdit()
        textfield.setStyleSheet(ss)
        textfield.setSizePolicy(sp)
        textfield.setMinimumSize(QtCore.QSize(512, 28))
        textfield.setFont(font)

        # Set the default value of the textbox
        textfield.setText('')
        textfield.setAlignment(QtCore.Qt.AlignLeft)

        # Create browse button
        textfield_button = create_button(None, 'Browse..', target=partial(self.browse_file, textfield), style=ss, font=font, size_policy=sp)
        textfield_button.setStyleSheet('color: rgb(255, 255, 255); background-color: rgb(60, 60, 60);')

        # Add to layout
        textfield_layout.addWidget(textfield)
        textfield_layout.addWidget(textfield_button)

        return textfield_frame, textfield

    # Opens the File Browser
    def browse_file(self, textfield):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', '', 'Text Files (*.txt)',)
        textfield.setText(filename)

    # Attempts to open the given file and return its lines
    def load_from_file(self, filename):
        try: # Attempt to read in the file
            with open(filename, 'r') as f: 
                lines = f.readlines()
        except: # Something went wrong!  
            # Return error
            return None
        return lines

    def convert_spawncycles(self):
        # First we need to parse
        json_dict = self.parse_fields()
        if json_dict is None: # Errors occurred. Can't do anything
            return

        # Now its safe to save
        filename = json_dict['Name'].lower() + '.json'
        dirpath = str(QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Directory')) # Open the dialog and get the dir to save in
        fullpath = f"{dirpath}/{filename}"
        with open(fullpath, 'w') as f_out: # Save the file
            f_out.write(json.dumps(json_dict).replace(' ', ''))

        # Add a message
        self.add_message(f"Conversion successful! Saved to '{fullpath}'.")

        # Show a dialog upon completion
        x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 90 # Anchor dialog to center of window
        y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
        diag_title = 'SpawnCycle Converter'
        diag_text = f'Conversion successful!'
        diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
        diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_check.png')))
        diag.exec_() # Show a dialog to tell user to check messages
 
    # Checks the Name field for errors. Returns errors if they are found
    def parse_name(self):
        nw_text = self.name_widget.text()

        if len(nw_text) == 0: # No name given at all
            return f"Error: No Name given for SpawnCycle!"
        elif nw_text.count(' ') > 0: # No spaces allowed
            return f"Error: Spaces are not allowed in SpawnCycle Name!\nUse the '_' (underscore) character instead."
        elif not nw_text.isalnum() and '_' not in nw_text: # Alphanumeric names only
            return f"Error: SpawnCycle Name must be alphanumeric!"
        return None

    # Checks the Author field for errors. Returns errors if they are found
    def parse_author(self):
        aw_text = self.author_widget.text()

        if len(aw_text) == 0: # No name given at all
            return f"Error: No Author given for SpawnCycle!"
        return None

    # Converts a SpawnCycle from its line format into a JSON-format
    def spawncycle_to_dict(self, lines):
        spawncycle_dict = {}
        for i in range(len(lines)):
            spawncycle_dict.update({str(i): lines[i].replace('SpawnCycleDefs=', '').replace('\n', '')})
        return spawncycle_dict

    # Checks over each field and makes sure it's set appropriately. Reports an error if not
    def parse_fields(self):
        # Check Name field
        err = self.parse_name()
        if err is not None:
            self.add_message(err)
            return None

        # Check Author field
        err = self.parse_author()
        if err is not None:
            self.add_message(err)
            return None

        # Check SpawnCycles
        file1_name = self.file1_widget.text()
        file2_name = self.file2_widget.text()
        file3_name = self.file3_widget.text()

        # Special case: All three fields are empty
        if len(file1_name) == 0 and len(file2_name) == 0 and len(file3_name) == 0:
            self.add_message(f"Error: No SpawnCycles specified to convert!")
            return None

        # Attempt to open the files
        # Short SpawnCycle
        if len(file1_name) > 0: # Only if a file was specified, though
            file1_lines = self.load_from_file(file1_name)
            if file1_lines is None: # File unopenable
                self.add_message(f"Error: File '{file1_name}' could not be opened!\nEither the file doesn't exist, or it is inaccessible somehow.")
                return None

            if len(file1_lines) != 4: # Must be 4 lines (waves)
                self.add_message(f"Error: 'Short' SpawnCycle must be exactly 4 lines ({len(file1_lines)} lines found in file)!")
                return None

            # Parse the SpawnCycle and check for any errors
            errors = parse_syntax_import(file1_name, file1_lines)
            if len(errors) > 0:
                self.add_message(errors[0])
                if len(errors) > 1:
                    self.add_message('\n\n'.join([e.replace(f"Parse errors ('{file1_name}'):\n\n", '') for e in errors[1:]]), prefix=False)

                # Show a dialog stating that errors occurred
                x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
                diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
                diag.exec_() # Show a dialog to tell user to check messages
                return None

            self.add_message(f"Parse of file '{file1_name}' successful!") # Post a message

        # Medium SpawnCycle
        if len(file2_name) > 0: # Only if a file was specified, though
            file2_lines = self.load_from_file(file2_name)
            if file2_lines is None: # File unopenable
                self.add_message(f"Error: File '{file2_name}' could not be opened!\nEither the file doesn't exist, or it is inaccessible somehow.")
                return None

            if len(file2_lines) != 7: # Must be 7 lines (waves)
                self.add_message(f"Error: 'Medium' SpawnCycle must be exactly 7 lines ({len(file2_lines)} lines found in file)!")
                return None

            # Parse the SpawnCycle and check for any errors
            errors = parse_syntax_import(file2_name, file2_lines)
            if len(errors) > 0:
                self.add_message(errors[0])
                if len(errors) > 1:
                    self.add_message('\n\n'.join([e.replace(f"Parse errors ('{file2_name}'):\n\n", '') for e in errors[1:]]), prefix=False)

                # Show a dialog stating that errors occurred
                x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
                diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
                diag.exec_() # Show a dialog to tell user to check messages
                return None

            self.add_message(f"Parse of file '{file2_name}' successful!") # Post a message

        # Long SpawnCycle
        if len(file3_name) > 0: # Only if a file was specified, though
            file3_lines = self.load_from_file(file3_name)
            if file3_lines is None: # File unopenable
                self.add_message(f"Error: File '{file3_name}' could not be opened!\nEither the file doesn't exist, or it is inaccessible somehow.")
                return None

            if len(file3_lines) != 10: # Must be 7 lines (waves)
                self.add_message(f"Error: 'Long' SpawnCycle must be exactly 10 lines ({len(file3_lines)} lines found in file)!")
                return None

            # Parse the SpawnCycle and check for any errors
            errors = parse_syntax_import(file3_name, file3_lines)
            if len(errors) > 0:
                self.add_message(errors[0])
                if len(errors) > 1:
                    self.add_message('\n\n'.join([e.replace(f"Parse errors ('{file3_name}'):\n\n", '') for e in errors[1:]]), prefix=False)

                # Show a dialog stating that errors occurred
                x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
                diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
                diag.exec_() # Show a dialog to tell user to check messages
                return None

            self.add_message(f"Parse of file '{file3_name}' successful!") # Post a message

        # If we reach this point, it's safe to create the JSON
        sdate = self.date_widget.selectedDate()
        sdate_str = f"{sdate.year()}-{sdate.month():02d}-{sdate.day():02d}"
        json_dict = {'Name': self.name_widget.text(), 'Author': self.author_widget.text(), 'Date': sdate_str, 'ShortSpawnCycle': {}, 'NormalSpawnCycle': {}, 'LongSpawnCycle': {}}

        if len(file1_name) > 0:
            spawncycle1 = self.spawncycle_to_dict(file1_lines)
            json_dict.update({'ShortSpawnCycle': spawncycle1})

        if len(file2_name) > 0:
            spawncycle2 = self.spawncycle_to_dict(file2_lines)
            json_dict.update({'NormalSpawnCycle': spawncycle2})

        if len(file3_name) > 0:
            spawncycle3 = self.spawncycle_to_dict(file3_lines)
            json_dict.update({'LongSpawnCycle': spawncycle3})

        return json_dict # Parse success!

    def setupUi(self):
        # Set up main window
        MainWindow.setFixedSize(800, 1000)
        MainWindow.setStyleSheet("background-color: rgb(50, 50, 50);")
        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)

        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.scrollarea = QtWidgets.QScrollArea(self.central_widget)
        self.scrollarea.setSizePolicy(sp)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setStyleSheet('color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);')
        self.scrollarea.setFrameShape(QtWidgets.QFrame.Box)
        self.scrollarea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrollarea.setLineWidth(2)
        scrollarea_contents = QtWidgets.QWidget()
        self.scrollarea.setWidget(scrollarea_contents)
        self.scrollarea_layout = QtWidgets.QVBoxLayout(scrollarea_contents)
        self.central_layout.addWidget(self.scrollarea)
        
        # Initialize window components
        self.setup_fields()
        self.setup_messages()

        # Finalize main window
        MainWindow.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 20))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle('SpawnCycle Converter')
        MainWindow.setWindowIcon(QtGui.QIcon(resource_path('img/logo.png')))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi()
    MainWindow.ui = ui
    MainWindow.show()
    sys.exit(app.exec_())
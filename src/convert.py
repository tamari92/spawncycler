#
#  convert.py
#
#  Author: Tamari (Nathan P. Ybanez)
#  Date of creation: 12/1/2020
#
#  Converts a set of standard CD SpawnCycles into a bundled JSON for use 
#  with Forrest Mark X's build of Controlled Difficulty
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
##  © Nathan Ybanez, 2020
##  All rights reserved.


from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import date, datetime
from functools import partial
from copy import deepcopy
import widget_helpers
import parse
import json

_DEF_FONT_FAMILY = 'Consolas'

class ConvertDialog(object):
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
        name_label = widget_helpers.create_label(self.scrollarea, text='SpawnCycle Name', style=ss, font=font_label)
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
        author_label = widget_helpers.create_label(self.scrollarea, text='\nAuthor', style=ss, font=font_label)
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
        date_label = widget_helpers.create_label(self.scrollarea, text='\nCreation Date', style=ss, font=font_label)
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

        file1_label = widget_helpers.create_label(self.scrollarea, text='\nShort (4 Wave) SpawnCycle', style=ss, font=font_label)
        file2_label = widget_helpers.create_label(self.scrollarea, text='\nMedium (7 Wave) SpawnCycle', style=ss, font=font_label)
        file3_label = widget_helpers.create_label(self.scrollarea, text='\nLong (10 Wave) SpawnCycle', style=ss, font=font_label)
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
        filler_label = widget_helpers.create_label(self.scrollarea, text='\n', style=ss, font=font_label)
        self.convert_button = widget_helpers.create_button(None, None, None, text=' Convert! ', icon_path='img/icon_go.png', icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font_label)
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
        label_messages = widget_helpers.create_label(self.scrollarea, text='\nMessages', style=ss_label, font=font_label)
        label_messages.setAlignment(QtCore.Qt.AlignLeft)
        
        # Set up Messages area
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.messages_textedit = QtWidgets.QTextEdit(self.scrollarea)
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
        textfield_button = widget_helpers.create_button(None, None, None, 'Browse..', target=partial(self.browse_file, textfield), style=ss, font=font, size_policy=sp)
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
        x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 90 # Anchor dialog to center of window
        y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
        diag_title = 'SpawnCycler'
        diag_text = f'Conversion successful!'
        diag = widget_helpers.create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
        diag.setWindowIcon(QtGui.QIcon('img/icon_check.png'))
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
            errors = parse.parse_syntax_import(file1_name, file1_lines)
            if len(errors) > 0:
                self.add_message(errors[0])
                if len(errors) > 1:
                    self.add_message('\n\n'.join([e.replace(f"Parse errors ('{file1_name}'):\n\n", '') for e in errors[1:]]), prefix=False)

                # Show a dialog stating that errors occurred
                x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = widget_helpers.create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
                diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
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
            errors = parse.parse_syntax_import(file2_name, file2_lines)
            if len(errors) > 0:
                self.add_message(errors[0])
                if len(errors) > 1:
                    self.add_message('\n\n'.join([e.replace(f"Parse errors ('{file2_name}'):\n\n", '') for e in errors[1:]]), prefix=False)

                # Show a dialog stating that errors occurred
                x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = widget_helpers.create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
                diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
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
            errors = parse.parse_syntax_import(file3_name, file3_lines)
            if len(errors) > 0:
                self.add_message(errors[0])
                if len(errors) > 1:
                    self.add_message('\n\n'.join([e.replace(f"Parse errors ('{file3_name}'):\n\n", '') for e in errors[1:]]), prefix=False)

                # Show a dialog stating that errors occurred
                x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = widget_helpers.create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
                diag.setWindowIcon(QtGui.QIcon('img/icon_warning.png'))
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

    def setupUi(self, Dialog):
        # Set up main window
        Dialog.setFixedSize(800, 1000)
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
        self.central_layout.addWidget(self.scrollarea)
        
        # Initialize window components
        self.setup_fields()
        self.setup_messages()

        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate


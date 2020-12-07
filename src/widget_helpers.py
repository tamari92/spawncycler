#
#  widget_helpers.py
#
#  Author: Tamari (Nathan P. Ybanez)
#  Date of creation: 11/16/2020
#
#  Helper functions for QWidgets (and custom widgets)
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


from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
from functools import partial
import random

icon_mapping = {'Cyst' : 'img/icon_cyst.png',
                'Slasher' : 'img/icon_slasher.png',
                'Alpha Clot' : 'img/icon_alphaclot.png',
                'Rioter' : 'img/icon_rioter.png',
                'Gorefast' : 'img/icon_gorefast.png',
                'Gorefiend' : 'img/icon_gorefiend.png',
                'Crawler' : 'img/icon_crawler.png',
                'Elite Crawler' : 'img/icon_elitecrawler.png',
                'Stalker' : 'img/icon_stalker.png',
                'Bloat' : 'img/icon_bloat.png',
                'Husk' : 'img/icon_husk.png',
                'Siren' : 'img/icon_siren.png',
                'E.D.A.R Trapper' : 'img/icon_edar_emp.png',
                'E.D.A.R Blaster' : 'img/icon_edar_laser.png',
                'E.D.A.R Bomber' : 'img/icon_edar_rocket.png',
                'Scrake' : 'img/icon_scrake.png',
                'Alpha Scrake' : 'img/icon_alphascrake.png',
                'Quarter Pound' : 'img/icon_quarterpound.png',
                'Quarter Pound (Enraged)' : 'img/icon_quarterpound.png',
                'Fleshpound' : 'img/icon_fleshpound.png',
                'Fleshpound (Enraged)' : 'img/icon_fleshpound.png',
                'Alpha Fleshpound' : 'img/icon_alphafleshpound.png',
                'Alpha Fleshpound (Enraged)' : 'img/icon_alphafleshpound.png',
                'Dr. Hans Volter' : 'img/icon_hans.png',
                'Patriarch' : 'img/icon_patriarch.png',
                'King Fleshpound' : 'img/icon_kingfleshpound.png',
                'Abomination' : 'img/icon_abomination.png',
                'Matriarch' : 'img/icon_matriarch.png',
                'Abomination Spawn' : 'img/icon_abomspawn.png'}

used_ids = []


# Represents a RGB color
class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"({self.r}, {self.g}, {self.b})"


# Custom QDialog that calls an event when closed
class CustomDialog(QtWidgets.QDialog):
    # This function is called when the user presses the X (close) button
    def closeEvent(self, event):
        self.ui.teardown()


# Custom version of QPushButton that supports Drag & Drop
class QZedPaneButton(QtWidgets.QPushButton):
    def __init__(self, parent, app, id):
        super().__init__(parent)
        self.app = app
        self.id = id

    def mouseMoveEvent(self, e):
        if e.buttons() != QtCore.Qt.LeftButton: # Ignore all except LMB press
            return
        # Change cursor to match the zed moved
        pm = QtGui.QPixmap(icon_mapping[self.id]).scaled(48, 48)
        mimeData = QtCore.QMimeData()
        drag = QtGui.QDrag(self)
        drag.setPixmap(pm)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        self.setDown(False)
        dropAction = drag.exec_(QtCore.Qt.CopyAction)

    def dragMoveEvent(self, e):
        e.acceptProposedAction()


# Custom version of QPushButton that supports Drag & Drop
class QSquadButton(QtWidgets.QPushButton):
    def __init__(self, parent, wave_id, squad_id, zed_id):
        super().__init__(parent)
        self.wave_id = wave_id
        self.squad_id = squad_id
        self.zed_id = zed_id

    def mouseMoveEvent(self, e):
        if e.buttons() != QtCore.Qt.LeftButton: # Ignore all except LMB press
            return
        # Change cursor to match the zed moved
        pm = QtGui.QPixmap(icon_mapping[self.zed_id]).scaled(48, 48)
        mimeData = QtCore.QMimeData()
        drag = QtGui.QDrag(self)
        drag.setPixmap(pm)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        self.setDown(False)
        dropAction = drag.exec_(QtCore.Qt.CopyAction)

    def mousePressEvent(self, e):
        if e.buttons() != QtCore.Qt.RightButton:
            return

        # Set up RMB menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
        remove_action = QtWidgets.QAction('Remove ZED from Squad', self)

        # Create RMB context menu
        self.menu = QtWidgets.QMenu(self)
        self.menu.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(50, 50, 50)")
        self.menu.addAction(remove_action)

        # Define Replacements menu
        zeds = list(icon_mapping.keys())
        zeds.remove(self.zed_id) # Remove this ZED so it doesn't appear in the menu
        replace_menu = QtWidgets.QMenu('Replace ZED with..', self)
        replace_menu.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(50, 50, 50)")

        custom_zeds = ['E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber', 'Alpha Scrake', 'Alpha Fleshpound',
                       'Alpha Fleshpound (Enraged)', 'Dr. Hans Volter', 'Patriarch', 'Abomination', 'Matriarch']
        
        for z in zeds:
            if self.zed_mode == 'Default' and z in custom_zeds:
                continue
            action = QtWidgets.QAction(z, self)
            replace_menu.addAction(action)
            action.triggered.connect(partial(self.replace_zeds, self.wave_id, self.squad_id, [self.zed_id], [z]))

        self.menu.addMenu(replace_menu)

        # Link signals
        remove_action.triggered.connect(partial(self.remove_zed_from_squad, self.wave_id, self.squad_id, self.zed_id, 'all'))

    # Show RMB context menu
    def on_context_menu(self, point):
        self.menu.exec_(self.mapToGlobal(point))  

    def dragMoveEvent(self, e):
        e.acceptProposedAction()


# Custom version of QPushButton that supports a RMB-menu
class QOptionsButton(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__(parent)

    # Sets up the options menu
    def init_menu(self, params):
        self.menu = QtWidgets.QMenu(self)
        self.menu.setMouseTracking(True);
        self.menu.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);")
        for (name, targ) in params.items():
            self.menu.addAction(name, targ)
        self.setMenu(self.menu)


# Custom version of QFrame that supports Drag & Drop
class QFrame_Drag(QtWidgets.QFrame):
    def __init__(self, parent, id, squad=True):
        super().__init__(parent)
        self.id = id
        self.unique_id = self.get_unique_id()
        self.is_full = False
        self.squad = squad # Dictates how behavior will be handled when things are dragged in
        self.setAcceptDrops(True)
        self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 255);")

    # Generates a unique ID for this frame
    def get_unique_id(self):
        uid = random.randint(1, 2147483647)
        global used_ids
        while uid in used_ids:
            uid = random.randint(1, 2147483647)
        used_ids.append(uid)
        return uid

    # Called when something first enters the widget
    def dragEnterEvent(self, e):
        zed_button = e.source()

        # Button came from the ZED Pane
        if isinstance(zed_button, QZedPaneButton):
            if not self.is_full: # Non-full squad and button from ZED Pane
                self.setStyleSheet("color: rgb(255, 128, 0); background-color: rgba(150, 90, 0, 30);")
        
        # Button came from a Squad
        elif isinstance(zed_button, QSquadButton):
            if self.squad: # This frame represents a Squad
                if not self.is_full and self.unique_id != zed_button.squad_uid: # Can't be the same Squad, though
                    self.setStyleSheet("color: rgb(255, 128, 0); background-color: rgba(150, 90, 0, 30);")
            else: # This frame represents a wave
                self.setStyleSheet("color: rgb(255, 128, 0); background-color: rgba(150, 90, 0, 30);")
        
        e.acceptProposedAction()

    # Called when something is dragged out of the widget
    def dragLeaveEvent(self, e):
        if not self.is_full:
            self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 255);")
        e.accept()

    # Called when something is dragged across the widget
    def dragMoveEvent(self, e):
        zed_button = e.source()

        # Button came from the ZED Pane
        if isinstance(zed_button, QZedPaneButton):
            e.acceptProposedAction() # Accept all ZED pane buttons
            return

        # Button came from a Squad
        elif isinstance(zed_button, QSquadButton):
            if self.squad and self.unique_id != zed_button.squad_uid: # Dragging into a squad, but NOT the same squad it came from
                e.acceptProposedAction()
                return
            elif not self.squad: # Dragging into a wave
                e.acceptProposedAction()
                return
        e.ignore()
        
    # Called when something is released onto the widget
    def dropEvent(self, e):
        zed_button = e.source()

        # Button came from the ZED pane
        if isinstance(zed_button, QZedPaneButton):
            if not self.is_full: # Squad is full. Change frame color
                self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 255);") # Reset border color

            if not self.squad: # This frame represents a wave
                self.add_squad(self.id, zed_button.id)
            else: # This frame represents a squad
                self.add_zed_to_squad(self.wave_id, self.id, zed_button.id)

            e.acceptProposedAction()

        # Button came from a Squad
        elif isinstance(e.source(), QSquadButton): 
            if self.squad: # Frame represents a Squad that is NOT full
                if self.is_full:
                    self.add_zed_to_squad(self.wave_id, self.id, zed_button.zed_id) # Trigger the error but do nothing else
                    return
                self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 255);") # Reset border color
                self.remove_zed_from_squad(zed_button.wave_id, zed_button.squad_id, zed_button.zed_id) # Remove the button from it's original squad
                self.add_zed_to_squad(self.wave_id, self.id, zed_button.zed_id) # Add the dragged zed to squad this frame corresponds to

            else: # Frame represents a wave
                self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 255);") # Reset border color
                self.remove_zed_from_squad(zed_button.wave_id, zed_button.squad_id, zed_button.zed_id) # Remove the button from it's original squad
                self.add_squad(self.id, e.source().zed_id) # Add a new squad to the wave

        e.ignore()
        

# Custom version of QScrollArea that supports Drag & Drop
class QScrollArea_Drag(QtWidgets.QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)

    # Called when something is dragged onto the widget
    def dragEnterEvent(self, e):
        if not isinstance(e.source(), QSquadButton): # Only accept drops from Squad ZEDs
            e.ignore()
            return
        e.acceptProposedAction()

    # Called when something is dragged out of the widget
    def dragLeaveEvent(self, e):
        e.ignore()

    # Called when something is dragged across the widget
    def dragMoveEvent(self, e):
        if not isinstance(e.source(), QSquadButton): # Only accept drops from Squad ZEDs
            e.ignore()
            return
        e.acceptProposedAction()

    # Called when something is released onto the widget
    def dropEvent(self, e):
        zed_button = e.source()
        if not isinstance(zed_button, QSquadButton): # Only accept drops from Squad ZEDs
            e.ignore()
            return
        else:
            self.remove_zed_from_squad(zed_button.wave_id, zed_button.squad_id, zed_button.zed_id)
            e.acceptProposedAction()


# Sets the object to have a white border around it
def set_plain_border(obj, color, width):
    obj.setStyleSheet(f"color: rgb{color};")
    obj.setFrameShape(QtWidgets.QFrame.Box)
    obj.setFrameShadow(QtWidgets.QFrame.Plain)
    obj.setLineWidth(width)


# Changes the button's click target
def button_changetarget(button, new_targ):
    button.clicked.disconnect()
    button.clicked.connect(new_targ)


# Changes a button's icon
def set_button_icon(button, icon_path, width, height):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    button.setIcon(icon)
    button.setIconSize(QtCore.QSize(width, height))


# Returns a ZED icon path
def get_icon_path(zed_id):
    return icon_mapping[zed_id]


# Creates and returns a chart of the given type, initialized with the given data
# Code adapted from https://codeloop.org/pyqtchart-how-to-create-piechart-in-pyqt5/
# Originally written by Parwiz Forogh, modified by me
def create_chart(parent, data, title, axis_data=None, chart_type='pie'):
    # Create Pie Chart
    if chart_type == 'pie':
        # Create the data series and initialize it
        default_series = QtChart.QPieSeries()
        for (name, value, color, percentage) in data:
            sl = default_series.append(name, value)
            sl.setLabel(f"{name}\n({percentage:.2f}%)")
            sl.setBrush(color)

        # Modify series
        default_series.setPieSize(0.75)
        default_series.setLabelsVisible()
        default_series.setLabelsPosition(QtChart.QPieSlice.LabelOutside)

        # Create the chart
        chart = QtChart.QChart()
        chart.addSeries(default_series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QtChart.QChart.AllAnimations)
        chart.setTitle(title)
        chart.legend().setVisible(False)
        #chart.legend().setAlignment(QtCore.Qt.AlignBottom)
        chart.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(225, 225, 225)))

        # Initialize a chart view
        chartview = QtChart.QChartView(chart)
        chartview.setRenderHint(QtGui.QPainter.Antialiasing)
        chartview.setMinimumSize(QtCore.QSize(600, 400))
        chartview.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        return chartview

    # Line Chart
    else:
        default_series = QtChart.QLineSeries()
        for (x, y) in data:
            sl = default_series.append(x, y)

        # Create chart
        chart = QtChart.QChart()
        chart.addSeries(default_series)
        chart.setAnimationOptions(QtChart.QChart.SeriesAnimations)
        chart.setTitle(title)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(225, 225, 225)))

        if axis_data is not None:
            axis_x = QtChart.QCategoryAxis() # Y-axis
            axis_x.setRange(axis_data['X']['Min'], axis_data['X']['Max'])
            axis_x.setTitleText(axis_data['X']['Title'])
            cur_tick = axis_data['X']['Max'] * 0.1
            for i in range(len(axis_data['X']['Labels'])):
                axis_x.append(f"{axis_data['X']['Labels'][i]}", cur_tick)
                cur_tick += (float(axis_data['X']['Max']) / len(axis_data['X']['Labels']))
            chart.addAxis(axis_x, QtCore.Qt.AlignBottom)
            axis_y = QtChart.QCategoryAxis() # Y-axis
            axis_y.setTitleText(axis_data['Y']['Title'])
            axis_y.setRange(axis_data['Y']['Min'], axis_data['Y']['Max'])
            axis_y.append('Easy', float(axis_data['Y']['Max']) * 0.1)
            axis_y.append('Moderate', float(axis_data['Y']['Max']) * 0.9)
            axis_y.append('Difficult', float(axis_data['Y']['Max']) * 1.3)
            chart.addAxis(axis_y, QtCore.Qt.AlignLeft)  
            default_series.attachAxis(axis_x)
            default_series.attachAxis(axis_y)

        chartview = QtChart.QChartView(chart)
        chartview.setRenderHint(QtGui.QPainter.Antialiasing)
        chartview.setMinimumSize(QtCore.QSize(600, 400))
        chartview.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        return chartview


# Returns a QButton with the given parameters
def create_button(parent, app, id, text=None, target=None, tooltip=None, style=None, icon_path=None, icon_w=None, icon_h=None, font=None, size_policy=None, squad=False, options=False, draggable=True):
    if draggable:
        if squad:
            wave_id = id[0]
            squad_id = id[1]
            zed_id = id[2]
            button = QSquadButton(parent, wave_id, squad_id, zed_id)
        else:
            button = QZedPaneButton(parent, app, id)
    elif options:
        button = QOptionsButton(parent)
    else:
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


# Creates, initializes, and returns a QSlider
def create_slider(min_value, max_value, tick_interval, width=480, default='max'):
    slider = QtWidgets.QSlider()
    sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    sp.setHorizontalStretch(0)
    sp.setVerticalStretch(0)
    slider.setSizePolicy(sp)
    slider.setMinimumSize(QtCore.QSize(width, 0))
    slider.setMinimum(min_value)
    slider.setMaximum(max_value)
    if default == 'max':
        slider.setValue(max_value)
    else:
        slider.setValue(default)
    slider.setOrientation(QtCore.Qt.Horizontal)
    slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
    slider.setTickInterval(tick_interval)

    return slider


# Returns a QComboBox with the specified options
def create_combobox(parent, options, style=None, size_policy=None):
    cbox = QtWidgets.QComboBox(parent)
    cbox.addItems(options) # Init the fields

    if style is not None:
        cbox.setStyleSheet(style)

    if size_policy is not None:
        cbox.setSizePolicy(size_policy)

    return cbox


# Returns a QTableWidget with the specified options
def create_table(parent, data, num_rows=2, num_cols=2, stretch=True):
    table = QtWidgets.QTableWidget(parent)
    table.setRowCount(num_rows)
    table.setColumnCount(num_cols)

    for (x, y, contents) in data:
        item = QtWidgets.QTableWidgetItem(contents)
        item.setFlags(item.flags() & QtCore.Qt.ItemIsEditable) # Make the cell un-editable
        table.setItem(x, y, item)
        
    table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    table.setMaximumSize(get_table_size(table))
    table.setMinimumSize(get_table_size(table))
    
    if stretch:
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    else:
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().hide()
    table.verticalHeader().hide()

    return table


# Returns a QSize object representing the true size of the given table (without any headers)
def get_table_size(table):
    w = table.verticalHeader().width() + 4
    for i in range(table.columnCount()):
        w += table.columnWidth(i)
    h = table.horizontalHeader().height() + 4
    for i in range(table.rowCount()):
        h += table.rowHeight(i)
    return QtCore.QSize(w, h-24)


# Formats the given cell of a QTableWidget
def format_cell(table, row, col, bg_color=None, fg_color=None, font=None, alignment=QtCore.Qt.AlignLeft):
    table.item(row, col).setTextAlignment(alignment|QtCore.Qt.AlignVCenter)

    if fg_color is not None: # Apply foreground color
        table.item(row, col).setForeground(fg_color)

    if bg_color is not None: # Apply background color
        table.item(row, col).setBackground(bg_color)

    if font is not None: # Apply font
        table.item(row, col).setFont(font)


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


# Creates and returns a Y/N dialog box
def create_choice_dialog(parent, title, text, x, y, yes_target=None, no_target=None, cancel_button=False, cancel_target=None):
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

    # Set up Yes button
    yes_button = QtWidgets.QPushButton('Yes')
    yes_button.setStyleSheet("color: rgb(255, 255, 255);")
    yes_button.setObjectName('yes_button')
    
    sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    sp.setHorizontalStretch(0)
    sp.setVerticalStretch(0)
    yes_button.setSizePolicy(sp)
    dialog.yes_button = yes_button

    # Assign the target of the yes button
    if yes_target is not None:
        yes_button.clicked.connect(yes_target)
    else:
        yes_button.clicked.connect(dialog.close)

    # Set up No button
    no_button = QtWidgets.QPushButton('No')
    no_button.setStyleSheet("color: rgb(255, 255, 255);")
    no_button.setObjectName('no_button')
    no_button.setSizePolicy(sp)
    dialog.no_button = no_button

    # Assign the target of the no button
    if no_target is not None:
        no_button.clicked.connect(no_target)
    else:
        no_button.clicked.connect(dialog.close)

    # Set up Cancel button
    if cancel_button:
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.setStyleSheet("color: rgb(255, 255, 255);")
        cancel_button.setObjectName('cancel_button')
        cancel_button.setSizePolicy(sp)
        dialog.cancel_button = cancel_button

        # Assign the target of the cancel button
        if cancel_target is not None:
            cancel_button.clicked.connect(cancel_target)
        else:
            cancel_button.clicked.connect(dialog.close)

    # Set layout
    vbox = QtWidgets.QVBoxLayout()
    vbox.setObjectName('vbox')
    hbox = QtWidgets.QHBoxLayout()
    hbox.setObjectName('hbox')
    hbox.addWidget(yes_button) # Add buttons
    hbox.addWidget(no_button)
    if cancel_button:
        hbox.addWidget(cancel_button)
    vbox.addWidget(dialog_label)
    vbox.addLayout(hbox)
    hbox_master.addLayout(vbox)

    # Set up window
    dialog.setWindowTitle(title)
    dialog.setStyleSheet("background-color: rgb(40, 40, 40);")

    # Move to x, y
    dialog.move(x, y)

    return dialog


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

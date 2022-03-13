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
##  © Nathan Ybanez, 2020-2022
##  All rights reserved.


from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
from functools import partial
import meta
import random

_DEF_FONT_FAMILY = 'Consolas'

used_ids = []

# Maps ZED names to their icon path
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
                'Abomination Spawn' : 'img/icon_abomspawn.png',
                'Slasher Omega': 'img/icon_slasher_omega.png',
                'Fleshpound Omega': 'img/icon_fleshpound_omega.png',
                'Gorefast Omega': 'img/icon_gorefast_omega.png',
                'Husk Omega': 'img/icon_husk_omega.png',
                'Tiny Husk': 'img/icon_husk_tiny.png',
                'Scrake Emperor': 'img/icon_scrake_emperor.png',
                'Scrake Omega': 'img/icon_scrake_omega.png',
                'Tiny Scrake': 'img/icon_scrake_tiny.png',
                'Siren Omega': 'img/icon_siren_omega.png',
                'Stalker Omega': 'img/icon_stalker_omega.png',
                'Big Crawler': 'img/icon_crawler_big.png',
                'Huge Crawler': 'img/icon_crawler_huge.png',
                'Medium Crawler': 'img/icon_crawler_medium.png',
                'Tiny Crawler': 'img/icon_crawler_tiny.png',
                'Ultra Crawler': 'img/icon_crawler_ultra.png'}


# Custom QDialog that calls an event when closed
class CustomDialog(QtWidgets.QDialog):
    # This function is called when the user presses the X (close) button
    def closeEvent(self, event):
        self.ui.teardown()

    # Override for closing via ESC
    def reject(self):
        self.close()


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

        cz = ['E.D.A.R Trapper', 'E.D.A.R Blaster', 'E.D.A.R Bomber', 'Alpha Scrake', 'Alpha Fleshpound',
              'Alpha Fleshpound (Enraged)', 'Dr. Hans Volter', 'Patriarch', 'Abomination', 'Matriarch',
              'Slasher Omega', 'Gorefast Omega', 'Stalker Omega', 'Tiny Crawler', 'Medium Crawler',
              'Big Crawler', 'Huge Crawler', 'Ultra Crawler', 'Siren Omega', 'Husk Omega', 'Tiny Husk',
              'Tiny Scrake', 'Scrake Omega', 'Scrake Emperor', 'Fleshpound Omega', 'Stalker Omega']
        
        for z in zeds:
            action = QtWidgets.QAction(z, self)
            replace_menu.addAction(action)
            action.triggered.connect(partial(self.replace_zeds, self.wave_id, self.squad_id, [self.zed_id], [z], z in cz))

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
    def init_menu(self, targets, tooltips):
        self.menu = QtWidgets.QMenu(self)
        self.menu.setMouseTracking(True);
        self.menu.setStyleSheet("QMenu {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);} QToolTip {color: rgb(0, 0, 0)};")
        targets = list(targets.items())
        tooltips = list(tooltips.values())
        for i in range(len(tooltips)):
            act = self.menu.addAction(targets[i][0], targets[i][1]).setToolTip(tooltips[i])
        self.menu.setToolTipsVisible(True)
        self.setMenu(self.menu)


# Custom version of QFrame that supports Drag & Drop
class QSwapFrame(QtWidgets.QFrame):
    def __init__(self, parent, wave_id, squad_id):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.wave_id = wave_id
        self.squad_id = squad_id
        self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 0);")

    # Called when something first enters the widget
    def dragEnterEvent(self, e):
        zed_button = e.source()
        if not isinstance(zed_button, QSquadButton):
            e.ignore()
            return
        else:
            self.setFrameShape(QtWidgets.QFrame.Box)
            self.setFrameShadow(QtWidgets.QFrame.Plain)
            self.setLineWidth(10)
            self.setStyleSheet("color: rgb(50, 50, 255); background-color: rgba(50, 50, 255, 30);")
        e.acceptProposedAction()

    # Called when something is dragged out of the widget
    def dragLeaveEvent(self, e):
        self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 0);")
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setLineWidth(0)
        e.accept()

    # Called when something is dragged across the widget
    def dragMoveEvent(self, e):
        zed_button = e.source()
        if not isinstance(zed_button, QSquadButton):
            e.ignore() # Accept all ZED pane buttons
            return
        else:
            e.acceptProposedAction()
        
    # Called when something is released onto the widget
    def dropEvent(self, e):
        zed_button = e.source()

        if not isinstance(zed_button, QSquadButton):
            e.ignore()
            return
        else:
            self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 0);") # Reset border color
            self.setFrameShape(QtWidgets.QFrame.NoFrame)
            self.setLineWidth(0)
        e.ignore()


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
                self.add_squad(self.id, zed_button.id, count=meta.get_keyvalue('new_squad_min_amount'))
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
    obj.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()});")
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


# Creates and returns a QLineEdit
def create_textfield(default, font=None, size_policy=None, style=None, w=28, h=28, edit_target=None, commit_target=None):
    # Setup stuff
    if font is None:
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(12)
        font.setWeight(75)
    if size_policy is None:
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
    if style is None:
        style = 'color: rgb(255, 255, 255);' # Stylesheet

    # Create the field
    textfield = QtWidgets.QLineEdit()
    textfield.setStyleSheet(style)
    textfield.setSizePolicy(size_policy)
    textfield.setMaximumSize(QtCore.QSize(w, h))
    textfield.setFont(font)
    textfield.setText(default)
    textfield.setAlignment(QtCore.Qt.AlignCenter)

    # Set up signals
    if edit_target is not None:
        textfield.textChanged.connect(edit_target)   
    if commit_target is not None:
        textfield.editingFinished.connect(commit_target)

    return textfield
    

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
def create_slider(min_value, max_value, tick_interval, style=None, width=480, default='max'):
    slider = QtWidgets.QSlider()
    sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    sp.setHorizontalStretch(0)
    sp.setVerticalStretch(0)
    slider.setSizePolicy(sp)
    slider.setMinimumSize(QtCore.QSize(width, 0))
    slider.setMinimum(min_value)
    slider.setMaximum(max_value)

    # Set default value
    if default == 'max':
        slider.setValue(max_value)
    else:
        slider.setValue(default)

    # Set style
    if style is not None:
        slider.setStyleSheet(style)

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
def create_choice_dialog(parent, title, text, x, y, no=True, cancel_button=False, yes_target=None, no_target=None, cancel_target=None):
    dialog = QtWidgets.QDialog()
    dialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint|QtCore.Qt.WindowTitleHint) # Disable X and minimize
    hbox_master = QtWidgets.QHBoxLayout(dialog)

    # Set up text label
    dialog_label = QtWidgets.QLabel(dialog)
    font = QtGui.QFont()
    font.setPointSize(8)
    font.setBold(True)
    dialog_label.setFont(font)
    dialog_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
    dialog_label.setStyleSheet("color: rgb(255, 255, 255);")
    dialog_label.setText(text)

    # Set up Yes button
    yes_button = QtWidgets.QPushButton('Yes')
    yes_button.setStyleSheet("color: rgb(255, 255, 255);")
    
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
    if no:
        no_button = QtWidgets.QPushButton('No')
        no_button.setStyleSheet("color: rgb(255, 255, 255);")
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
        cancel_button.setSizePolicy(sp)
        dialog.cancel_button = cancel_button

        # Assign the target of the cancel button
        if cancel_target is not None:
            cancel_button.clicked.connect(cancel_target)
        else:
            cancel_button.clicked.connect(dialog.close)

    # Set layout
    vbox = QtWidgets.QVBoxLayout()
    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(yes_button) # Add buttons
    if no:
        hbox.addWidget(no_button)
    if cancel_button:
        hbox.addWidget(cancel_button)
    vbox.addWidget(dialog_label)
    vbox.addLayout(hbox)
    hbox_master.addLayout(vbox)
    dialog.layout = vbox

    # Set up window
    dialog.setWindowTitle(title)
    dialog.setStyleSheet("background-color: rgb(40, 40, 40);")

    # Move to x, y
    dialog.move(x, y)

    return dialog


# Creates and returns a simple dialog box with an OK button and checkbox (if specified)
def create_simple_dialog(parent, title, text, x, y, button=True, button_target=None, checkbox=False):
    dialog = QtWidgets.QDialog()
    dialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint|QtCore.Qt.WindowTitleHint) # Disable X and minimize
    hbox_master = QtWidgets.QHBoxLayout(dialog)

    # Set up text label
    dialog_label = QtWidgets.QLabel(dialog)
    font = QtGui.QFont()
    font.setPointSize(8)
    font.setBold(True)
    dialog_label.setFont(font)
    dialog_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
    dialog_label.setStyleSheet("color: rgb(255, 255, 255);")
    dialog_label.setText(text)

    # Set up OK button
    if button:
        ok_button = QtWidgets.QPushButton('OK')
        ok_button.setStyleSheet("color: rgb(255, 255, 255);")
        
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(ok_button.sizePolicy().hasHeightForWidth())
        ok_button.setSizePolicy(sp)

        if button_target is not None:
            ok_button.clicked.connect(button_target)
        else:
            ok_button.clicked.connect(dialog.close)

    # Set up checkbox
    if checkbox:
        diag_checkbox = QtWidgets.QCheckBox()
        diag_checkbox.setChecked(False)

        # Set up checkbox label
        checkbox_label = QtWidgets.QLabel(dialog)
        checkbox_label.setFont(font)
        checkbox_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        checkbox_label.setStyleSheet("color: rgb(255, 255, 255);")
        checkbox_label.setText("Don't show this again")

        # Set up the frame
        checkbox_frame = QtWidgets.QFrame()
        checkbox_frame_layout = QtWidgets.QHBoxLayout(checkbox_frame)
        checkbox_frame_layout.addWidget(checkbox_label)
        checkbox_frame_layout.addWidget(diag_checkbox)
        checkbox_frame_layout.setAlignment(QtCore.Qt.AlignCenter)

        dialog.checkbox = diag_checkbox # Save a reference so we can get to it later

    # Set layout
    vbox_master = QtWidgets.QVBoxLayout()
    hbox_button = QtWidgets.QHBoxLayout()
    hbox_button.setAlignment(QtCore.Qt.AlignCenter)
    if button:
        if checkbox:
            hbox_button.addWidget(checkbox_frame)
        hbox_button.addWidget(ok_button)
    vbox_master.addWidget(dialog_label)
    vbox_master.addLayout(hbox_button)
    hbox_master.addLayout(vbox_master)

    # Set up window
    dialog.setWindowTitle(title)
    dialog.setStyleSheet("background-color: rgb(40, 40, 40);")

    # Move to x, y
    dialog.move(x, y)

    return dialog

#
#  SpawnCycler.py
#
#  Author: Tamari (Nathan P. Ybanez)
#  Date of creation: 11/14/2020
#
#  Main code base for SpawnCycler
#

from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
from datetime import datetime, date
from functools import partial
from copy import deepcopy
import os
import json
import random

#import threading
#import cgitb 
#cgitb.enable(format = 'text')

# Things I could add maybe:
# 1. AutoSave?

_DEF_FONT_FAMILY = 'Consolas'
_RECENT_MAX = 8 # Max "Recent Files"
_WAVE_MAX = 10  # Max number of waves
_SQUAD_MAX = 10  # Max ZEDs in a squad
has_swapped_modes = False # Has the user swapped ZED modes yet?
has_swapped_modes_generate = False # Has the user swapped ZED modes yet? Used for generation
used_ids = [] # Used Frame IDs (to force uniqueness)

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
                'Abomination Spawn' : 'img/icon_abomspawn.png'}


# Zed name mapping to tokens (used in parsing)
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
                'Other': QtGui.QColor(175, 175, 175),
                'Total': QtGui.QColor(184, 214, 224)}


# Resolves the path for an image (used for pyinstaller)
def resource_path(relative_path):
    #return relative_path
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    #print(f'returning {os.path.join(base_path, relative_path)}')
    return os.path.join(base_path, relative_path)


# CUSTOM CLASSES
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
        pm = QtGui.QPixmap(resource_path(icon_mapping[self.id])).scaled(48, 48)
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
        pm = QtGui.QPixmap(resource_path(icon_mapping[self.zed_id])).scaled(48, 48)
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
            if self.squad and not self.is_full: # Frame represents a Squad that is NOT full
                self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(50, 50, 50, 255);") # Reset border color
                self.remove_zed_from_squad(zed_button.wave_id, zed_button.squad_id, zed_button.zed_id) # Remove the button from it's original squad
                self.add_zed_to_squad(self.wave_id, self.id, zed_button.zed_id) # Add the dragged zed to squad this frame corresponds to

            elif not self.squad: # Frame represents a wave
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


# WIDGET HELPERS
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
    return resource_path(icon_mapping[zed_id])


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
def parse_syntax_export(filename, wavedefs):
    errors = []
    fname = f" ('{filename}')" if filename != 'Untitled' else ''
    parse_prefix = f"Parse errors{fname}:\n\n"

    if len(wavedefs) not in [4, 7, 10]: # File must be 4, 7, or 10 lines (waves) long
        errors.append(f"{parse_prefix}{len(wavedefs):,d} wave(s) found in SpawnCycle.\nSpawnCycle length must be 4, 7, or 10 waves!\n")

    for i in range(len(wavedefs)):
        wave = wavedefs[i]
        if len(wave['Squads']) < 1: # No squads to parse!
            errors.append(f"{parse_prefix}wave {i+1}: No squads found to parse. Wave is empty!")

    return errors


# Parses the syntax of the given file. Returns 'None' if successful
def parse_syntax_import(filename, lines):
    waves = deepcopy(lines)
    total_ids = [] # Combination of all id lists for easy checking
    for l in zed_tokens.values():
        total_ids += l
    valid_quantifiers = ['*', '!']

    fname = f" ('{filename}')" if filename != 'Untitled' else ''
    parse_prefix = f"Parse errors{fname}:\n\n"

    errors = []

    if len(waves) not in [4, 7, 10]: # File must be 4, 7, or 10 lines (waves) long
        errors.append(f"{parse_prefix}{len(waves):,d} lines found in file '{filename}'.\nFile length must be 4, 7, or 10 lines!")
        return errors # Just leave after this error because it's likely there will be hundreds of syntax errors

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


# GENERATE WINDOW
class GenerateDialog(object):
    # Creates a button with the ZED icon in it
    def create_zed_button(self, zed_id):
        icon_path = get_icon_path(zed_id)
        icon_w = icon_h = 40
        ss = 'QToolTip {color: rgb(0, 0, 0);\nbackground-color: rgb(40, 40, 40);}' # Stylesheet
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        button = create_button(None, None, None, tooltip=zed_id, style=ss, icon_path=icon_path, icon_w=icon_w, icon_h=icon_h, size_policy=sp, options=False, squad=False, draggable=False)

        return button

    # Updates the given slider with the value of the textbox
    def update_slider(self, textbox, slider):
        plaintxt = textbox.text()
        # Truncate input that's too long
        slider_maxlen = len(str(slider.maximum()))
        if len(plaintxt) > slider_maxlen:
            # Only allow as many chars as the max value's num chars
            textbox.setText(plaintxt[:slider_maxlen])
            textbox.setAlignment(QtCore.Qt.AlignCenter)
            plaintxt = plaintxt[:slider_maxlen]

            # Move cursor to end
            #c = QtGui.QTextCursor(textbox.textCursor())
            #c.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
            #textbox.setTextCursor(c)

        if not plaintxt.isnumeric(): # Ignore non-numbers
            return

        val = int(plaintxt) if int(plaintxt) >= 0 else 0
        slider.setValue(val) # Update the slider

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
        #c = QtGui.QTextCursor(textbox.textCursor())
        #c.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
        #textbox.setTextCursor(c)
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
        ss = 'QLabel {color: rgb(255, 255, 255); background-color: rgb(40, 40, 40);}\nQToolTip {color: rgb(0, 0, 0);}' # Stylesheet

        low_label = create_label(None, text=low_text, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)
        slider = create_slider(min_value, max_value, tick_interval, width=width, default=default)
        high_label = create_label(None, text=high_text, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)

        if tooltip is not None:
            low_label.setToolTip(tooltip)

        # Create text edit
        if text_box:
            ss = 'color: rgb(255, 255, 255);' # Stylesheet
            font = QtGui.QFont()
            font.setFamily(_DEF_FONT_FAMILY)
            font.setPointSize(10)
            font.setWeight(75)
            text_edit = QtWidgets.QLineEdit()
            text_edit.setStyleSheet(ss)
            text_edit.setSizePolicy(sp)
            text_edit.setMaximumSize(QtCore.QSize(48, 28))
            text_edit.setFont(font)

            # Set the default value of the textbox
            val = default if default != 'max' else max_value
            text_edit.setText(str(val))
            text_edit.setAlignment(QtCore.Qt.AlignCenter)

            # Connect the textbox to the slider
            text_edit.textChanged.connect(partial(self.update_slider, text_edit, slider))

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
                if not has_swapped_modes_generate:
                    diag_title = 'WARNING'
                    diag_text = '\nThe Custom Settings are NOT supported by most Controlled Difficulty builds.\nUsing these settings may break the generated SpawnCycle on those builds.\n\nUse at your own risk!\n'
                    x = self.Dialog.mapToGlobal(self.Dialog.rect().center()).x()-200 # Anchor dialog to center of window
                    y = self.Dialog.mapToGlobal(self.Dialog.rect().center()).y()
                    diag = create_simple_dialog(self.Dialog, diag_title, diag_text, x, y, button=True)
                    diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
                    diag.exec_() # Show a dialog to tell user to check messages
                    has_swapped_modes_generate = True # Never show this message again

            # Show custom stuff
            self.slider_panes['E.D.A.R Trapper Density']['Frame'].setVisible(True)
            self.slider_panes['E.D.A.R Blaster Density']['Frame'].setVisible(True)
            self.slider_panes['E.D.A.R Bomber Density']['Frame'].setVisible(True)
            self.slider_panes['Scrake Albino Density']['Frame'].setVisible(True)
            self.slider_panes['Fleshpound Albino Density']['Frame'].setVisible(True)
            self.slider_panes['Hans Density']['Frame'].setVisible(True)
            self.slider_panes['Patriarch Density']['Frame'].setVisible(True)
            self.slider_panes['Abomination Density']['Frame'].setVisible(True)
            self.slider_panes['Matriarch Density']['Frame'].setVisible(True)

            # Set default values
            self.slider_panes['E.D.A.R Trapper Density']['Children']['Slider'].setValue(100)
            self.slider_panes['E.D.A.R Blaster Density']['Children']['Slider'].setValue(100)
            self.slider_panes['E.D.A.R Bomber Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Scrake Albino Density']['Children']['Slider'].setValue(30)
            self.slider_panes['Fleshpound Albino Density']['Children']['Slider'].setValue(30)
            self.slider_panes['Hans Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Patriarch Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Abomination Density']['Children']['Slider'].setValue(100)
            self.slider_panes['Matriarch Density']['Children']['Slider'].setValue(100)

            self.buttons['Swap Modes'].setText(' Default Settings ')
            self.zed_mode = 'Custom'
        else: # Swap to Default
            # Hide all custom stuff
            self.slider_panes['E.D.A.R Trapper Density']['Frame'].setVisible(False)
            self.slider_panes['E.D.A.R Blaster Density']['Frame'].setVisible(False)
            self.slider_panes['E.D.A.R Bomber Density']['Frame'].setVisible(False)
            self.slider_panes['Scrake Albino Density']['Frame'].setVisible(False)
            self.slider_panes['Fleshpound Albino Density']['Frame'].setVisible(False)
            self.slider_panes['Hans Density']['Frame'].setVisible(False)
            self.slider_panes['Patriarch Density']['Frame'].setVisible(False)
            self.slider_panes['Abomination Density']['Frame'].setVisible(False)
            self.slider_panes['Matriarch Density']['Frame'].setVisible(False)

            # Set default values
            self.slider_panes['E.D.A.R Trapper Density']['Children']['Slider'].setValue(0)
            self.slider_panes['E.D.A.R Blaster Density']['Children']['Slider'].setValue(0)
            self.slider_panes['E.D.A.R Bomber Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Scrake Albino Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Fleshpound Albino Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Hans Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Patriarch Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Abomination Density']['Children']['Slider'].setValue(0)
            self.slider_panes['Matriarch Density']['Children']['Slider'].setValue(0)

            self.buttons['Swap Modes'].setText(' Custom Settings ')
            self.zed_mode = 'Default'

    # Set up main window stuff
    def setup_main_area(self, Dialog):
        Dialog.setFixedSize(800, 1000)
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
        ss = 'color: rgb(255, 255, 255);\nbackground-color: rgb(40, 40, 40);' # Stylesheet
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        font = QtGui.QFont()
        font.setFamily(_DEF_FONT_FAMILY)
        font.setPointSize(12)
        font.setWeight(75)

        # Create buttons
        generate_button = create_button(None, None, None, text=' Generate! ', icon_path=resource_path('img/icon_go.png'), icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font, options=False, squad=False, draggable=False)
        generate_button.clicked.connect(self.accept_preset)
        presets_button = create_button(None, None, None, text=' Presets ', icon_path=resource_path('img/icon_presets.png'), icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font, options=True, squad=False, draggable=False)
        menu_opts = {'Light': partial(self.load_preset, 'Light'),
                     'Moderate': partial(self.load_preset, 'Moderate'),
                     'Heavy': partial(self.load_preset, 'Heavy'),
                     'Albino': partial(self.load_preset, 'Albino'),
                     'Poundemonium': partial(self.load_preset, 'Poundemonium'),
                     'GSO': partial(self.load_preset, 'GSO'),
                     'Min Settings': partial(self.load_preset, 'Min Settings'),
                     'Max Settings': partial(self.load_preset, 'Max Settings'),
                     'Unseen Annihilation': partial(self.load_preset, 'Unseen Annihilation'),
                     'Hellish Inferno': partial(self.load_preset, 'Hellish Inferno'),
                     'Trash Only': partial(self.load_preset, 'Trash Only'),
                     'Medium Only': partial(self.load_preset, 'Medium Only'),
                     'Large Only': partial(self.load_preset, 'Large Only'),
                     'Boss Only': partial(self.load_preset, 'Boss Only'),
                     'Large-less': partial(self.load_preset, 'Large-less'),
                     'Custom Craziness': partial(self.load_preset, 'Custom Craziness'),
                     'Boss Rush': partial(self.load_preset, 'Boss Rush')}
        presets_button.init_menu(menu_opts)

        mode_button = create_button(None, None, None, text=' Custom Settings ', icon_path=resource_path('img/icon_switch.png'), icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font, options=False, squad=False, draggable=False)
        mode_button.clicked.connect(self.swap_modes)
        self.button_pane = QtWidgets.QFrame()
        button_pane_layout = QtWidgets.QHBoxLayout(self.button_pane)
        button_pane_layout.addWidget(generate_button)
        button_pane_layout.addWidget(presets_button)
        button_pane_layout.addWidget(mode_button)

        self.buttons.update({'Generate': generate_button})
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
        spacer_label1 = create_label(None, text='\n', style=ss_label, font=font_label, size_policy=sp_label, alignment=QtCore.Qt.AlignCenter)
        spacer_label2 = create_label(None, text='\n', style=ss_label, font=font_label, size_policy=sp_label, alignment=QtCore.Qt.AlignCenter)
        self.general_settings_label = create_label(None, text='\nGeneral Settings\n', font=font_label, alignment=QtCore.Qt.AlignCenter)
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
        self.density_settings_label = create_label(None, text='\nGlobal Density Settings\n', font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.density_settings_label.setStyleSheet(ss_header)
        self.density_settings_label.setFrameShape(QtWidgets.QFrame.Box)
        self.density_settings_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.density_settings_label.setLineWidth(2)
        trash_density_pane = self.create_slider_pane('Trash ZED Density       0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Trash ZEDs {density_tooltip_sfx}", width=384)
        medium_density_pane = self.create_slider_pane('Medium ZED Density      0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Medium ZEDs {density_tooltip_sfx}", width=384)
        large_density_pane = self.create_slider_pane('Large ZED Density       0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Large ZEDs {density_tooltip_sfx}", width=384)
        boss_density_pane = self.create_slider_pane('Boss Density            0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Bosses {density_tooltip_sfx}", width=384, default=0)

        # Add this stuff to the global dict to access later
        self.slider_panes.update({'Trash Density': trash_density_pane})
        self.slider_panes.update({'Medium Density': medium_density_pane})
        self.slider_panes.update({'Large Density': large_density_pane})
        self.slider_panes.update({'Boss Density': boss_density_pane})

        # Create ZED labels
        self.trash_label = create_label(None, text='\nTrash ZEDs', style=ss_label, font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.medium_label = create_label(None, text='\n\nMedium ZEDs', style=ss_label, font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.large_label = create_label(None, text='\n\nLarge ZEDs', style=ss_label, font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.boss_label = create_label(None, text='\n\nBosses', style=ss_label, font=font_label, alignment=QtCore.Qt.AlignCenter)

        # Create ZED settings slider panes
        self.zed_settings_label = create_label(None, text='\nZED Density Settings\n', font=font_label, alignment=QtCore.Qt.AlignCenter)
        self.zed_settings_label.setStyleSheet(ss_header)
        self.zed_settings_label.setFrameShape(QtWidgets.QFrame.Box)
        self.zed_settings_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.zed_settings_label.setLineWidth(2)

        cyst_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Cysts {density_tooltip_sfx}")
        alphaclot_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Alpha Clots {density_tooltip_sfx}")
        slasher_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Slashers {density_tooltip_sfx}")
        alphaclot_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Alpha Clots to become Rioters.', width=256, default=30)
        gorefast_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Gorefasts {density_tooltip_sfx}")
        gorefast_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Gorefasts to become Gorefiends.', width=256, default=30)
        crawler_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Crawlers {density_tooltip_sfx}")
        crawler_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Crawlers to become Elite Crawlers.', width=256, default=30)
        stalker_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Stalkers {density_tooltip_sfx}")
        bloat_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Bloats {density_tooltip_sfx}")
        husk_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Husks {density_tooltip_sfx}")
        siren_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Sirens {density_tooltip_sfx}")
        edar_trapper_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} E.D.A.R Trappers {density_tooltip_sfx}")
        edar_blaster_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} E.D.A.R Blasters {density_tooltip_sfx}")
        edar_bomber_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} E.D.A.R Bombers {density_tooltip_sfx}")
        scrake_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Scrakes {density_tooltip_sfx}")
        quarterpound_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Quarter Pounds {density_tooltip_sfx}")
        quarterpound_rage_pane = self.create_slider_pane('SpawnRage Chance      0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Quarter Pounds to spawn Enraged.', width=256, default=10)
        fleshpound_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, tooltip=f"{density_tooltip_pfx} Fleshpounds {density_tooltip_sfx}")
        fleshpound_rage_pane = self.create_slider_pane('SpawnRage Chance      0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Fleshpounds to spawn Enraged.', width=256, default=10)
        scrake_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets the chance for Scrakes to become Alpha Scrakes.', width=256, default=30)
        fleshpound_albino_pane = self.create_slider_pane('Albino Chance         0% ', ' 100%   ', 0, 100, 10, tooltip='Sets chance for Fleshpounds to become Alpha Fleshpounds.', width=256, default=30)
        hans_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} Dr. Hans Volter {density_tooltip_sfx}")
        patriarch_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} the Patriarch {density_tooltip_sfx}")
        kingfleshpound_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} King Fleshpound {density_tooltip_sfx}")
        abomination_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} the Abomination {density_tooltip_sfx}")
        matriarch_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} the Matriarch {density_tooltip_sfx}")
        abominationspawn_pane = self.create_slider_pane('  0% ', ' 100%   ', 0, 100, 10, default=100, tooltip=f"{density_tooltip_pfx} Abomination Spawns {density_tooltip_sfx}")

        # Add buttons into hboxes
        cyst_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Cyst'))
        alphaclot_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Alpha Clot'))
        slasher_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Slasher'))
        gorefast_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Gorefast'))
        crawler_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Crawler'))
        stalker_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Stalker'))
        bloat_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Bloat'))
        husk_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Husk'))
        siren_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Siren'))
        edar_trapper_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('E.D.A.R Trapper'))
        edar_blaster_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('E.D.A.R Blaster'))
        edar_bomber_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('E.D.A.R Bomber'))
        scrake_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Scrake'))
        quarterpound_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Quarter Pound'))
        fleshpound_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Fleshpound'))
        hans_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Dr. Hans Volter'))
        patriarch_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Patriarch'))
        kingfleshpound_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('King Fleshpound'))
        abomination_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Abomination'))
        matriarch_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Matriarch'))
        abominationspawn_pane['Children']['Layout'].insertWidget(0, self.create_zed_button('Abomination Spawn'))

        # Add this stuff to the global dict to access later
        self.slider_panes.update({'Cyst Density': cyst_pane})
        self.slider_panes.update({'Alpha Clot Density': alphaclot_pane})
        self.slider_panes.update({'Alpha Clot Albino Density': alphaclot_albino_pane})
        self.slider_panes.update({'Slasher Density': slasher_pane})
        self.slider_panes.update({'Gorefast Density': gorefast_pane})
        self.slider_panes.update({'Gorefast Albino Density': gorefast_albino_pane})
        self.slider_panes.update({'Crawler Density': crawler_pane})
        self.slider_panes.update({'Crawler Albino Density': crawler_albino_pane})
        self.slider_panes.update({'Stalker Density': stalker_pane})
        self.slider_panes.update({'Bloat Density': bloat_pane})
        self.slider_panes.update({'Husk Density': husk_pane})
        self.slider_panes.update({'Siren Density': siren_pane})
        self.slider_panes.update({'E.D.A.R Trapper Density': edar_trapper_pane})
        self.slider_panes.update({'E.D.A.R Blaster Density': edar_blaster_pane})
        self.slider_panes.update({'E.D.A.R Bomber Density': edar_bomber_pane})
        self.slider_panes.update({'Scrake Density': scrake_pane})
        self.slider_panes.update({'Scrake Albino Density': scrake_albino_pane})
        self.slider_panes.update({'Quarter Pound Density': quarterpound_pane})
        self.slider_panes.update({'Quarter Pound Rage Density': quarterpound_rage_pane})
        self.slider_panes.update({'Fleshpound Density': fleshpound_pane})
        self.slider_panes.update({'Fleshpound Albino Density': fleshpound_albino_pane})
        self.slider_panes.update({'Fleshpound Rage Density': fleshpound_rage_pane})
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
        self.scrollarea_contents_layout.addWidget(alphaclot_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(alphaclot_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(gorefast_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(gorefast_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(crawler_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(crawler_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(stalker_pane['Frame'])

        self.scrollarea_contents_layout.addWidget(self.medium_label)
        self.scrollarea_contents_layout.addWidget(bloat_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(husk_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(siren_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(edar_trapper_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(edar_blaster_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(edar_bomber_pane['Frame'])

        self.scrollarea_contents_layout.addWidget(self.large_label)
        self.scrollarea_contents_layout.addWidget(scrake_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(scrake_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(quarterpound_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(quarterpound_rage_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(fleshpound_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(fleshpound_albino_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(fleshpound_rage_pane['Frame'])

        self.scrollarea_contents_layout.addWidget(self.boss_label)
        self.scrollarea_contents_layout.addWidget(hans_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(patriarch_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(kingfleshpound_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(abomination_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(matriarch_pane['Frame'])
        self.scrollarea_contents_layout.addWidget(abominationspawn_pane['Frame'])

    # Loads a preset into the generator
    def load_preset(self, preset, last_used_mode=None):
        presets = {'Light': [3, 15, 20, 3, 5, 5, 7, 10, 10, 100, 50, 15, 0, 100, 100, 5, 100, 100, 5, 100, 5, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0],
                   'Moderate': [3, 20, 25, 4, 7, 4, 4, 8, 10, 75, 60, 35, 0, 100, 100, 10, 100, 100, 10, 100, 10, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 5, 100, 0, 5, 0, 0, 0, 0, 0, 0],
                   'Heavy': [3, 30, 35, 5, 10, 2, 2, 7, 10, 60, 50, 40, 0, 100, 100, 15, 100, 100, 15, 100, 15, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 10, 100, 0, 10, 0, 0, 0, 0, 0, 0],
                   'Albino': [3, 25, 30, 4, 8, 1, 4, 8, 10, 100, 30, 30, 0, 50, 100, 80, 50, 100, 80, 100, 80, 50, 100, 100, 100, 0, 0, 0, 100, 0, 100, 5, 100, 0, 5, 0, 0, 0, 0, 0, 0],
                   'Poundemonium': [3, 25, 35, 5, 10, 4, 3, 8, 10, 30, 30, 65, 0, 100, 100, 15, 100, 100, 15, 100, 15, 100, 100, 100, 100, 0, 0, 0, 50, 0, 100, 7, 100, 0, 7, 0, 0, 0, 0, 0, 0],
                   'GSO': [3, 25, 40, 8, 10, 4, 3, 5, 10, 15, 15, 100, 0, 100, 100, 15, 100, 100, 15, 100, 15, 100, 100, 100, 100, 0, 0, 0, 10, 0, 100, 12, 100, 0, 12, 0, 0, 0, 0, 0, 0],
                   'Min Settings': [1, 1, 50, 1, 8, 1, 1, 1, 4, 100, 100, 100, 0, 100, 100, 0, 100, 100, 0, 100, 0, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 0, 100, 0, 0, 0, 0, 100, 0, 0, 100],
                   'Max Settings': [3, 100, 100, 10, 10, 1, 1, 1, 10, 100, 100, 100, 0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 100, 100, 0, 100, 0, 0, 100, 0, 0, 100],
                   'Unseen Annihilation': [3, 15, 25, 5, 8, 3, 5, 10, 10, 100, 10, 10, 0, 10, 10, 5, 10, 10, 5, 10, 5, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 5, 100, 0, 5, 0, 0, 0, 0, 0, 0],
                   'Hellish Inferno': [2, 15, 25, 5, 10, 2, 4, 7, 7, 10, 100, 10, 0, 100, 100, 10, 100, 100, 10, 100, 10, 100, 0, 100, 0, 0, 0, 0, 100, 0, 100, 5, 100, 0, 5, 0, 0, 0, 0, 0, 0],
                   'Trash Only': [3, 15, 20, 1, 4, 3, 4, 8, 10, 100, 0, 0, 0, 100, 100, 10, 100, 100, 10, 100, 10, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 5, 100, 0, 5, 0, 0, 0, 0, 0, 0],
                   'Medium Only': [3, 15, 20, 1, 4, 3, 4, 8, 10, 0, 100, 0, 0, 100, 100, 10, 100, 100, 10, 100, 10, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 5, 100, 0, 5, 0, 0, 0, 0, 0, 0],
                   'Large Only': [3, 15, 20, 1, 4, 3, 1, 8, 10, 0, 0, 100, 0, 100, 100, 10, 100, 100, 10, 100, 10, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 5, 100, 0, 5, 0, 0, 0, 0, 0, 0],
                   'Boss Only': [3, 15, 20, 1, 4, 3, 4, 8, 1, 0, 0, 0, 100, 100, 100, 10, 100, 100, 10, 100, 10, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 5, 100, 0, 5, 100, 100, 100, 100, 100, 100],
                   'Large-less': [2, 15, 25, 5, 10, 3, 7, 7, 7, 100, 100, 0, 0, 100, 100, 30, 100, 100, 30, 100, 30, 100, 100, 100, 100, 0, 0, 0, 100, 0, 100, 10, 100, 0, 10, 0, 0, 0, 0, 0, 0],
                   'Custom Craziness': [3, 20, 30, 3, 6, 2, 4, 7, 7, 100, 100, 100, 50, 100, 100, 10, 100, 100, 10, 100, 10, 100, 100, 100, 100, 100, 100, 100, 100, 35, 75, 8, 100, 35, 8, 100, 100, 100, 100, 100, 0],
                   'Boss Rush': [1, 15, 20, 3, 6, 2, 3, 4, 2, 10, 10, 10, 100, 100, 100, 10, 100, 100, 10, 100, 10, 100, 100, 100, 100, 100, 100, 100, 100, 15, 100, 5, 100, 15, 5, 100, 100, 100, 100, 100, 0]}

        if isinstance(preset, list): # This an old preset from last generation
            preset_data = preset
            if last_used_mode is not None and last_used_mode == 'Custom':
                self.swap_modes()
                self.swap_modes()
            elif last_used_mode is not None and last_used_mode == 'Default':
                self.swap_modes()
        else: # User selected a preset from the menu
            preset_data = presets[preset]

            # Swap to the appropriate ZED set for these presets for the first time
            if preset in ['Boss Rush', 'Custom Craziness', 'Boss Only'] and self.zed_mode == 'Default':
                self.swap_modes()
            elif preset not in ['Boss Rush', 'Custom Craziness', 'Boss Only'] and self.zed_mode == 'Custom':
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

    # Compiles all current slider data and passes it back to the main window
    def accept_preset(self):
        # Check slider values first to make sure they're okay
        sv = self.get_slider_values()
        trash_vals = [sv['Cyst Density'], sv['Alpha Clot Density'], sv['Slasher Density'], sv['Gorefast Density'], sv['Crawler Density'], sv['Stalker Density']]
        medium_vals = [sv['Bloat Density'], sv['Husk Density'], sv['Siren Density'], sv['E.D.A.R Trapper Density'], sv['E.D.A.R Blaster Density'], sv['E.D.A.R Bomber Density']]
        large_vals = [sv['Scrake Density'], sv['Quarter Pound Density'], sv['Fleshpound Density']]
        boss_vals = [sv['Hans Density'], sv['Patriarch Density'], sv['King Fleshpound Density'], sv['Abomination Density'], sv['Matriarch Density'], sv['Abomination Spawn Density']]
        errors = []

        # Ensure slider values are correct
        if sv['Min Squads'] > sv['Max Squads']:
            errors.append(f"'Min Squads Per Wave' must be <= 'Max Squads Per Wave'")
        if sv['Squad Min Length'] > sv['Squad Max Length']:
            errors.append(f"'Min Squad Size' must be <= 'Max Squad Size'")
        if sv['Trash Density'] != 0 and self.all_value(trash_vals, 0):
            errors.append(f"'Trash Density' found to be non-zero but all ZEDs in category have 0% Density!")
        if sv['Medium Density'] != 0 and self.all_value(medium_vals, 0):
            errors.append(f"'Medium Density' found to be non-zero but all ZEDs in category have 0% Density!")
        if sv['Large Density'] != 0 and self.all_value(large_vals, 0):
            errors.append(f"'Large Density' found to be non-zero but all ZEDs in category have 0% Density!")
        if sv['Boss Density'] != 0 and self.all_value(boss_vals, 0):
            errors.append(f"'Boss Density' found to be non-zero but all ZEDs in category have 0% Density!")
        if sv['Trash Density'] == 0 and sv['Medium Density'] == 0 and sv['Large Density'] == 0 and sv['Boss Density'] == 0:
            errors.append(f"At least one Global Density must be non-zero!")
        if sv['Large Min Wave'] > 1 and sv['Trash Density'] == 0 and sv['Medium Density'] == 0 and sv['Large Density'] > 0 and sv['Boss Density'] == 0:
            errors.append(f"Params suggest Larges Only but 'Large ZED Min Wave' found to be > 1!")
        if sv['Boss Min Wave'] > 1 and sv['Trash Density'] == 0 and sv['Medium Density'] == 0 and sv['Large Density'] == 0 and sv['Boss Density'] > 0:
            errors.append(f"Params suggest Bosses Only but 'Boss ZED Min Wave' found to be > 1!")
        if sv['Large Min Wave'] > 1 and sv['Boss Min Wave'] > 1 and sv['Trash Density'] == 0 and sv['Medium Density'] == 0 and sv['Large Density'] > 0 and sv['Boss Density'] > 0:
            errors.append(f"Params suggest Larges/Bosses Only but 'Large ZED Min Wave' and 'Boss Min Wave' found to be > 1!")

        if len(errors) > 0: # Errors occurred
            # Show a dialog explaining this
            diag_title = 'SpawnCycler'
            x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
            y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
            err_text = '\n'.join(errors)
            diag_text = f"The following error(s) were encountered while attempting to Generate:\n\n{err_text}\n"
            diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            diag.exec_() # Show a dialog to tell user to check messages
        else: # No errors. Good to go!
            self.generate_target(sv, self.Dialog)

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

    def setupUi(self, Dialog, generate_target, last_used_preset=None, last_used_mode=None):
        self.cancelled = False
        self.slider_panes = {}
        self.buttons = {}
        self.generate_target = generate_target
        self.zed_mode = 'Custom' # Start in custom mode to populate everything
        self.Dialog = Dialog

        self.setup_main_area(Dialog) # Set up main window stuff
        self.setup_button_pane(Dialog) # Set up the options buttons at the bottom
        self.setup_scrollarea(Dialog) # Sets up the scrollarea where all of the main options are
        
        # Put everything in
        self.main_layout.addWidget(self.scrollarea)
        self.main_layout.addWidget(self.button_pane)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        # Swap back to default mode
        if last_used_preset is not None:
            self.load_preset(last_used_preset, last_used_mode=last_used_mode)
        else:
            self.swap_modes()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate


# ANALYZE WINDOW
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
                if len(currently_spawned_zeds) == 0: # We ran out of zeds to pop (because MM is high)
                    break
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
            
            # Longer waves tend to be harder due to resources having to be further spread out 
            wsf_mod = 1.0 + (float(self.params['WaveSizeFakes']) / 128.0)

            # Calculate the final score
            difficulty_score = wsf_mod * wave_score_mod * zed_score_mod

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

        label_zed_category = create_label(None, text='ZEDs by Category', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
        table_zed_category = create_table(None, zed_category_data, num_rows=len(zed_category_data) // 3, num_cols=3, stretch=False)
        
        # Format table
        set_plain_border(table_zed_category, Color(255, 255, 255), 2)
        self.format_table(table_zed_category, table_type='categorical')

        # Create ZEDs by Category Pie Chart
        if self.params['Display Charts']:
            chart_data = []
            for (category, count) in wave_data['Category'].items():
                if category not in ['Total'] and count > 0:
                    percent = (float(count) / float(wave_data['Total'])) * 100.0
                    chart_data.append((category, count, light_colors[category], percent))
            chart_zed_category = create_chart(None, chart_data, '', chart_type='pie')

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
        label_zed_type = create_label(None, text='\nZEDs by Type', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
        table_zed_type = create_table(None, zed_type_data, num_rows=len(zed_type_data) // 4, num_cols=4, stretch=True)

        # Format table to have a nice border
        set_plain_border(table_zed_type, Color(255, 255, 255), 2)
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

            label_zed_group = create_label(None, text='\nZEDs by Group', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            table_zed_group = create_table(None, zed_group_data, num_rows=len(zed_group_data) // 3, num_cols=3, stretch=True)
            
            # Format table
            set_plain_border(table_zed_group, Color(255, 255, 255), 2)
            self.format_table(table_zed_group, table_type='categorical')

            # Create ZEDs by Group Pie Chart
            if self.params['Display Charts']:
                chart_data = []
                total_percent = 0.0
                total_count = 0
                for (group, count) in wave_data['Group'].items():
                    if group not in ['Total', 'Albino', 'SpawnRage'] and count > 0:
                        percent = (float(count) / float(wave_data['Total'])) * 100.0
                        total_percent += percent
                        total_count += count
                        chart_data.append((group, count, light_colors[group], percent))
                # Add 'Other' group
                other_percent = 100.0 - total_percent
                other_count = wave_data['Total'] - total_count
                chart_data.append(('Other', other_count, QtGui.QColor(175, 175, 175), other_percent))
                chart_zed_group = create_chart(None, chart_data, '', chart_type='pie')

        if difficulty_data is not None and self.params['Analyze Difficulty']:
            label_diff_text = f"\n\nESTIMATED WAVE DIFFICULTY" if not merged else f"\n\nSPAWNCYCLE DIFFICULTY"
            label_wave_diff = create_label(None, text=label_diff_text, tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_mm = create_label(None, text=f"Max Monsters:     {self.params['MaxMonsters']}\nDificulty:        {self.analysis_widgets['Difficulty'].currentText()}\nWave Size Fakes:  {self.params['WaveSizeFakes']}", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_assumes = create_label(None, text=f"\nASSUMPTIONS", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_cs = create_label(None, text=f"Spawn Poll:      1.00\nSpawn Mod:       0.00\nPlayers:         6\nTrash HP Fakes:  6\nLarge HP Fakes:  6\nBoss HP Fakes:   6\nFakes Mode:      ignore_humans\n\nAll ZEDs are killed in the order they spawn", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            chart_difficulty = create_chart(None, difficulty_data, '', axis_data=axis_data, chart_type='line')

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
            label_zed_group = create_label(None, text='\nZEDs by Group', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
            label_nodata = create_label(None, text='\nNo Group Data to Show!', tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignLeft)
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
                format_cell(table, x, y, bg_color=light_colors['Header'], fg_color=None, font=font, alignment=QtCore.Qt.AlignHCenter)

            # Colorify rest of the table
            row = 1
            while row < table.rowCount():
                category = table.item(row, 0).text()
                for j in range(3): # Apply the colors to the row!
                    if j == 0: # First col should be left-aligned
                        format_cell(table, row, j, bg_color=light_colors[category], fg_color=dark_colors[category], font=font)
                    else:
                        format_cell(table, row, j, bg_color=light_colors[category], fg_color=dark_colors[category], font=font, alignment=QtCore.Qt.AlignHCenter)
                row += 1
        else: # Type table
            # Colorify header row
            header_cells = [(0, 0), (0, 1), (0, 2), (0, 3)]
            for (x, y) in header_cells:
                format_cell(table, x, y, bg_color=light_colors['Header'], fg_color=None, font=font, alignment=QtCore.Qt.AlignHCenter)

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
                        format_cell(table, row, j, bg_color=bg_color, fg_color=fg_color, font=font)
                    else:
                        format_cell(table, row, j, bg_color=bg_color, fg_color=fg_color, font=font, alignment=QtCore.Qt.AlignHCenter)
                row += 1

    # Publishes analysis data for the SpawnCycle
    def analyze_wavedefs(self):
        self.clear_scrollarea() # First clear out any prev data

        # Show "Loading" dialog
        diag_title = 'Analyzing..'
        x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 50 # Anchor dialog to center of window
        y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y() + 100
        diag_text = f"Analyzing.."
        loading_diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=False)
        loading_diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
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
        title_label = create_label(None, text=f"SPAWNCYCLE ANALYSIS " + (f":: {self.filename[:-4]}" if self.filename != 'Untitled' else ''), tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_label = create_label(None, text=f"\n\nPARAMETERS", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame = QtWidgets.QFrame()
        params_frame_layout = QtWidgets.QVBoxLayout(params_frame)
        params_frame.setStyleSheet(f"color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);")
        params_frame.setFrameShape(QtWidgets.QFrame.Box)
        params_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        params_frame.setLineWidth(2)

        gamelength_label = create_label(None, text=f"Game Length:          {self.analysis_widgets['GameLength'].currentText()}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(gamelength_label)
        difficulty_label = create_label(None, text=f"Difficulty:           {self.analysis_widgets['Difficulty'].currentText()}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(difficulty_label)
        wsf_label = create_label(None, text=f"Wave Size Fakes:      {self.analysis_widgets['WaveSizeFakes'].text()}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(wsf_label)
        
        oo_str = 'TRUE' if self.analysis_widgets['Overview Only'].isChecked() else 'FALSE'
        oo_label = create_label(None, text=f"Overview Only:        {oo_str}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(oo_label)

        iz_str = 'TRUE' if self.analysis_widgets['Ignore Zeroes'].isChecked() else 'FALSE'
        iz_label = create_label(None, text=f"Ignore Zeroes:        {iz_str}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(iz_label)

        ad_str = 'TRUE' if self.analysis_widgets['Analyze Difficulty'].isChecked() else 'FALSE'
        ad_label = create_label(None, text=f"Analyze Difficulty:   {ad_str}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(ad_label)
        
        mm_label = create_label(None, text=f"Max Monsters:         {self.analysis_widgets['MaxMonsters'].text()}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(mm_label)
        
        dc_str = 'TRUE' if self.analysis_widgets['Display Charts'].isChecked() else 'FALSE'
        dc_label = create_label(None, text=f"Display Charts:       {dc_str}", tooltip=None, style=ss_params, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        params_frame_layout.addWidget(dc_label)

        self.scrollarea_contents_layout.addWidget(title_label)
        self.scrollarea_contents_layout.addWidget(params_label)
        self.scrollarea_contents_layout.addWidget(params_frame)

        # Display combined stats
        avg_difficulty_data = [(0, 0.0)] + [(i+1, float(sum([y for _, y in difficulty_data[i]])) / float(len(difficulty_data[i]))) for i in range(0, len(difficulty_data))]
        axis_data = {'X': {'Title': '\nWave', 'Labels': [str(i) for i in range(1, len(difficulty_data)+1)], 'Min': 0, 'Max': len(self.wavedefs)}, 'Y': {'Title': 'Average Difficulty\n', 'Tick': 10, 'Min': 0, 'Max': 755000}}
        merged_label = create_label(None, text=f"\n\nALL WAVES", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
        merged_frame, merged_frame_children = self.create_waveframe(merged, merged=True, difficulty_data=avg_difficulty_data, axis_data=axis_data) # Create table
        self.scrollarea_contents_layout.addWidget(merged_label)
        self.scrollarea_contents_layout.addWidget(merged_frame)

        # Display stats per-wave
        if not self.params['Overview Only']:
            for i in range(len(wave_stats)):
                x_max = difficulty_data[i][-1][0]
                axis_data = {'X': {'Title': '\nWave Progress (%)', 'Labels': ['10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'], 'Min': 0, 'Max': x_max}, 'Y': {'Title': 'Difficulty\n', 'Tick': 10, 'Min': 0, 'Max': 755000}}
                wave_label = create_label(None, text=f"\n\nWAVE {i+1}", tooltip=None, style=ss_label, font=font_label, size_policy=sp_fixed, alignment=QtCore.Qt.AlignCenter)
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
        diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
        diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_check.png')))
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

        #gamelength_label = create_label(None, text='Game Length', tooltip=None, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        simulate_button = create_button(None, None, None, text=' Simulate! ', icon_path=resource_path('img/icon_go.png'), icon_w=24, icon_h=24, style="color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);", size_policy=sp, font=font_button, options=False, squad=False, draggable=False)
        simulate_button.clicked.connect(self.analyze_wavedefs)
        simulate_frame = QtWidgets.QFrame()
        simulate_frame_layout = QtWidgets.QHBoxLayout(simulate_frame)
        simulate_frame_layout.setAlignment(QtCore.Qt.AlignCenter)
        simulate_frame_layout.addWidget(simulate_button)

        # Set up GameLength area
        gamelength_label = create_label(None, text='Game Length       ', tooltip="The Length of the game.\nDifferent Game Lengths affect the way the waves are sampled.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        gamelength_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        gamelength_cbox = create_combobox(None, options=['Short (4 Waves)', 'Medium (7 Waves)', 'Long (10 Waves)'], style=ss_cbox, size_policy=sp)
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
        difficulty_label = create_label(None, text='Difficulty        ', tooltip="The Difficulty of the game to sample from.\nHarder difficulties make the waves larger.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        difficulty_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        difficulty_cbox = create_combobox(None, options=['Normal', 'Hard', 'Suicidal', 'Hell on Earth'], style=ss_cbox, size_policy=sp)
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
        wavesize_label = create_label(None, text='Wave Size Fakes   ', tooltip="The number of players to sample the waves from.\nHigher values make the waves larger.\nAssumes the 'Ignore Humans' Fakes Mode setting.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
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
        wavesize_textarea.setToolTip("The number of players to sample the waves from.\nHigher values make the waves larger.\nAssumes the 'Ignore Humans' Fakes Mode setting.")
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
        iz_label = create_label(None, text='Ignore Zeroes          ', tooltip="Don't display fields with zero value.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
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
        analyze_difficulty_label = create_label(None, text='Analyze Difficulty     ', tooltip="Produce a chart showing the (relative) difficulty curve of the wave.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
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
        display_charts_label = create_label(None, text='Display Charts         ', tooltip="Show graphical charts related to Analysis data.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
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
        overview_only_label = create_label(None, text='Overview Only     ', tooltip="Exclude individual wave statistics from the Analysis Results.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
        overview_only_label.setStyleSheet("QToolTip {color: rgb(0, 0, 0);}; QLabel {color: rgb(255, 255, 255); background-color: rgb(50, 50, 50);};")
        self.params.update({'Overview Only': overview_only_checkbox.isChecked()})
        overview_only_frame = QtWidgets.QFrame()
        overview_only_frame_layout = QtWidgets.QHBoxLayout(overview_only_frame)
        overview_only_frame_layout.addWidget(overview_only_label)
        overview_only_frame_layout.addWidget(overview_only_checkbox)
        overview_only_frame_layout.setAlignment(QtCore.Qt.AlignLeft)

        # Set up MaxMonsters area
        maxmonsters_label = create_label(None, text='Max Monsters           ', tooltip="The maximum number of ZEDs that can be alive at once.\nHigher values make the waves more difficult.\nOnly used if the 'Analyze Difficulty' setting is TRUE.", style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignLeft)
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
        if not wsf_widget.text().isnumeric():
            wsf_widget.setText('0') # Just set it to default if they provide a non-number
            self.params.update({'WaveSizeFakes': 0})
            return

        # Remove any leading zeroes
        wsf = int(wsf_widget.text()) # Conv to an int will remove the zeroes on its own. Guaranteed to be numeric at this point
        if wsf == 0:
            if wsf_widget.text().count('0') > 1: # Special case for zero, just replace it. Stripping won't work here
                self.analysis_widgets['WaveSizeFakes'].setText('0')
        else:
            self.analysis_widgets['WaveSizeFakes'].setText(wsf_widget.text().lstrip('0'))
        
        # Only allow numbers between 0 and 128
        if wsf < 0:
            self.analysis_widgets['WaveSizeFakes'].setText('0')
            wsf = 0
        elif wsf > 128:
            self.analysis_widgets['WaveSizeFakes'].setText('128')
            wsf = 128

        self.params.update({'WaveSizeFakes': wsf})

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
        if not mm_widget.text().isnumeric():
            mm_widget.setText('1') # Just set it to default if they provide a non-number
            self.params.update({'MaxMonsters': 1})
            return

        # Remove any leading zeroes
        mm = int(mm_widget.text()) # Conv to an int will remove the zeroes on its own. Guaranteed to be numeric at this point
        self.analysis_widgets['MaxMonsters'].setText(mm_widget.text().lstrip('0'))

        # Only allow numbers between 1 and 256
        if mm < 1:
            self.analysis_widgets['MaxMonsters'].setText('1')
            mm = 1
        elif mm > 256:
            self.analysis_widgets['MaxMonsters'].setText('256')
            mm = 256

        self.params.update({'MaxMonsters': mm})

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
        self.params_label = create_label(None, text='\nAnalysis Parameters', tooltip=None, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)
        self.results_label = create_label(None, text='Analysis Results', tooltip=None, style=ss, font=font, size_policy=sp, alignment=QtCore.Qt.AlignCenter)
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
        name_label = create_label(self.scrollarea, text='SpawnCycle Name', style=ss, font=font_label)
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
        author_label = create_label(self.scrollarea, text='\nAuthor', style=ss, font=font_label)
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
        date_label = create_label(self.scrollarea, text='\nCreation Date', style=ss, font=font_label)
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

        file1_label = create_label(self.scrollarea, text='\nShort (4 Wave) SpawnCycle', style=ss, font=font_label)
        file2_label = create_label(self.scrollarea, text='\nMedium (7 Wave) SpawnCycle', style=ss, font=font_label)
        file3_label = create_label(self.scrollarea, text='\nLong (10 Wave) SpawnCycle', style=ss, font=font_label)
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
        filler_label = create_label(self.scrollarea, text='\n', style=ss, font=font_label)
        self.convert_button = create_button(None, None, None, text=' Convert! ', icon_path=resource_path('img/icon_go.png'), icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font_label)
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
        label_messages = create_label(self.scrollarea, text='\nMessages', style=ss_label, font=font_label)
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
        textfield_button = create_button(None, None, None, 'Browse..', target=partial(self.browse_file, textfield), style=ss, font=font, size_policy=sp)
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
        diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
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
            errors = parse_syntax_import(file1_name, file1_lines)
            if len(errors) > 0:
                self.add_message(errors[0])
                if len(errors) > 1:
                    self.add_message('\n\n'.join([e.replace(f"Parse errors ('{file1_name}'):\n\n", '') for e in errors[1:]]), prefix=False)

                # Show a dialog stating that errors occurred
                x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
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
            errors = parse_syntax_import(file2_name, file2_lines)
            if len(errors) > 0:
                self.add_message(errors[0])
                if len(errors) > 1:
                    self.add_message('\n\n'.join([e.replace(f"Parse errors ('{file2_name}'):\n\n", '') for e in errors[1:]]), prefix=False)

                # Show a dialog stating that errors occurred
                x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
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
            errors = parse_syntax_import(file3_name, file3_lines)
            if len(errors) > 0:
                self.add_message(errors[0])
                if len(errors) > 1:
                    self.add_message('\n\n'.join([e.replace(f"Parse errors ('{file3_name}'):\n\n", '') for e in errors[1:]]), prefix=False)

                # Show a dialog stating that errors occurred
                x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
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
        name_label = create_label(self.scrollarea, text='SpawnCycle Name', style=ss, font=font_label)
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
        author_label = create_label(self.scrollarea, text='\nAuthor', style=ss, font=font_label)
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
        date_label = create_label(self.scrollarea, text='\nCreation Date', style=ss, font=font_label)
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

        file1_label = create_label(self.scrollarea, text='\nShort (4 Wave) SpawnCycle', style=ss, font=font_label)
        file2_label = create_label(self.scrollarea, text='\nMedium (7 Wave) SpawnCycle', style=ss, font=font_label)
        file3_label = create_label(self.scrollarea, text='\nLong (10 Wave) SpawnCycle', style=ss, font=font_label)
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
        filler_label = create_label(self.scrollarea, text='\n', style=ss, font=font_label)
        self.convert_button = create_button(None, None, None, text=' Convert! ', icon_path=resource_path('img/icon_go.png'), icon_w=24, icon_h=24, style=ss, size_policy=sp, font=font_label)
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
        label_messages = create_label(self.scrollarea, text='\nMessages', style=ss_label, font=font_label)
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
        textfield_button = create_button(None, None, None, 'Browse..', target=partial(self.browse_file, textfield), style=ss, font=font, size_policy=sp)
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
        diag_title = 'SpawnCycle Converter'
        diag_text = f'Conversion successful!'
        diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
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
                x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
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
                x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
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
                x = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).x() - 150 # Anchor dialog to center of window
                y = self.scrollarea.mapToGlobal(self.scrollarea.rect().center()).y()
                diag_title = 'WARNING'
                diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
                diag = create_simple_dialog(self.scrollarea, diag_title, diag_text, x, y, button=True)
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




# ABOUT DIALOG
class AboutDialog(object):
    def setupUi(self, Dialog):
        # Font used for all text
        font = QtGui.QFont()
        font.setFamily('Consolas')
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)

        # Main stuff
        Dialog.resize(630, 630)
        Dialog.setStyleSheet('background-color: rgb(40, 40, 40);')

        # Set up the logo image
        self.logo = QtWidgets.QLabel(Dialog)
        self.logo.setGeometry(QtCore.QRect(180, 20, 281, 271))
        self.logo.setText('')
        self.logo.setPixmap(QtGui.QPixmap(resource_path('img/logo.png')))
        self.logo.setScaledContents(True)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)

        # Set up description
        self.description = QtWidgets.QTextEdit(Dialog)
        self.description.setGeometry(QtCore.QRect(30, 350, 571, 231))
        self.description.setFont(font)
        self.description.setStyleSheet('color: rgb(255, 255, 255);\nborder-color: rgba(255, 255, 255, 0);\nbackground-color: rgb(50, 50, 50);')
        self.description.setReadOnly(True)
        self.description.setFrameShape(QtWidgets.QFrame.Box)
        self.description.setFrameShadow(QtWidgets.QFrame.Plain)
        self.description.setLineWidth(1)

        # Set up author label
        self.author_label = QtWidgets.QLabel(Dialog)
        self.author_label.setGeometry(QtCore.QRect(220, 300, 191, 41))
        self.author_label.setFont(font)
        self.author_label.setStyleSheet('color: rgb(255, 255, 255);\nbackground-color: rgb(50, 50, 50);')
        self.author_label.setAlignment(QtCore.Qt.AlignCenter)
        self.author_label.setFrameShape(QtWidgets.QFrame.Box)
        self.author_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.author_label.setLineWidth(1)

        # Set up button
        self.ok_button = QtWidgets.QPushButton(Dialog)
        self.ok_button.setGeometry(QtCore.QRect(280, 590, 75, 23))
        self.ok_button.setStyleSheet('color: rgb(255, 255, 255);\nbackground-color: rgb(60, 60, 60);')

        self.retranslateUi(Dialog)
        self.ok_button.clicked.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.description.setHtml(_translate('Dialog', "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                                    "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                                    "p, li { white-space: pre-wrap; }\n"
                                                    "</style></head><body style=\" font-family:\'Consolas\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#2aed11;\">SpawnCycler</span></span><span style=\" font-size:9pt;\"> is a utility designed to help you Create, Edit, Generate, and Analyze SpawnCycles for Killing Floor 2\'s <span style=\" font-size:9pt; color:#2aed11;\">Controlled Difficulty</span> <span style=\" font-size:9pt;\">mod.</span></p>\n"
                                                    "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;\"><br /></p>\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">Through a <span style=\" font-size:9pt; color:#2aed11;\">simplistic UI</span><span style=\" font-size:9pt;\"> and intuitive <span style=\" font-size:9pt; color:#2aed11;\">drag-and-drop features</span><span style=\" font-size:9pt;\">, one can create a SpawnCycle in a much simpler (and quicker) fashion than creating it the old-fashioned way with a Text Editor.</span></p>\n"
                                                    "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;\"><br /></p>\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#2aed11;\">Quality-of-life features</span><span style=\" font-size:9pt;\"> such as a built-in parser ensure <span style=\" font-size:9pt; color:#2aed11;\">maximum ease-of-use</span><span style=\" font-size:9pt;\"> and make iterations quick and simple, with <span style=\" font-size:9pt; color:#2aed11;\">minimal errors</span><span style=\" font-size:9pt;\">.</span></p>\n"
                                                    "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;\"><br /></p>\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">If you have any feedback to give me, I can be reached at:</span></p>\n"
                                                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\"><br /></span><span style=\" font-size:9pt; color:#ffaa00;\">Discord:</span><span style=\" font-size:9pt;\"> Tamari#6292<br /></span><span style=\" font-size:9pt; color:#ffaa00;\">Email:</span><span style=\" font-size:9pt;\"> nate92@gmail.com<br /></span><span style=\" font-size:9pt; color:#ffaa00;\">Steam:</span><span style=\" font-size:9pt;\"> steamcommunity.com/id/tamaritm</span></p></body></html>"))
        self.author_label.setText(_translate('Dialog', 'SpawnCycler v1.0\nby Tamari'))
        self.ok_button.setText(_translate('Dialog', 'OK'))


# MAIN WINDOW
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
                    diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
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
        squad_layout = this_squad['Layout'] # Get the layout corresponding to this wave's squad box

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

        # Is this the last squad in the entire wave?
        if len(this_squad['ZEDs'].keys()) > 0:
            this_squad['Frame'].is_full = False
            this_squad['Frame'].setToolTip('')
            set_plain_border(this_squad['Frame'], Color(255, 255, 255), 2)
        else: # Last ZED in entire squad. We need to remove the entire Squad Frame too
            this_squad['Layout'].setParent(None)
            this_squad['Frame'].setParent(None)
            self.wavedefs[wave_id]['Squads'].pop(squad_id)

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
        zed_label = create_label(zed_frame, text='1', style=ss_label, font=font_label)
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
        zed_button = create_button(self.wavedefs_scrollarea_contents, self.app, ids, tooltip=zed_id, style=ss_button, icon_path=get_icon_path(zed_id), icon_w=icon_w, icon_h=icon_h, size_policy=sp, squad=True, draggable=True)
        zed_button.replace_zeds = self.replace_zeds
        zed_button.remove_zed_from_squad = self.remove_zed_from_squad
        zed_button.zed_mode = self.zed_mode

        # Create a new frame for the squad
        squad_frame = QFrame_Drag(self.wavedefs[wave_id]['Frames']['SquadFrame'], id=len(self.wavedefs[wave_id]['Squads']), squad=True)
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
            set_plain_border(squad_frame, Color(245, 42, 20), 2)
            squad_frame.setStyleSheet('QToolTip {color: rgb(0, 0, 0)}\nQFrame_Drag {color: rgb(255, 0, 0); background-color: rgba(150, 0, 0, 30);}')
            #squad_frame.anim.start()

        # Update the internal array
        self.wavedefs[wave_id]['Squads'].append({'Frame': squad_frame, 'Layout': squad_frame_layout, 'ZEDs': {zed_id: {'Count': count, 'Raged': raged, 'Frame': zed_frame, 'Children': zed_frame_children}}})

        # The file is now 'dirty'
        self.dirty = True
        if self.filename != 'Untitled': # Change filename to reflect
            self.set_window_title(f'SpawnCycler ({self.truncate_filename(self.filename)}*)') # Only if file is named though

    # Adds a new ZED to the given squad
    def add_zed_to_squad(self, wave_id, squad_id, zed_id, count=1, raged=False):
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
        zed_button = create_button(self.wavedefs[wave_id]['Frames']['SquadFrame'], self.app, ids, tooltip=zed_id, style=ss_button, icon_path=get_icon_path(zed_id), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button, squad=True, draggable=True)
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

        zed_button.squad_uid = this_squad['Frame'].unique_id

        # Has this squad reached capacity?
        total_zeds = sum([x['Count'] for x in this_squad['ZEDs'].values()])
        if total_zeds == _SQUAD_MAX:
            this_squad['Frame'].is_full = True # Mark as full
            this_squad['Frame'].setToolTip('This squad has reached capacity.')
            set_plain_border(this_squad['Frame'], Color(245, 42, 20), 2)
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
            button_changetarget(shiftup_button, partial(self.shift_wavedef, thisdef['Frames']['WaveFrame'], 'up'))
            button_changetarget(shiftdn_button, partial(self.shift_wavedef, thisdef['Frames']['WaveFrame'], 'down'))
            button_changetarget(delete_button, partial(self.remove_wavedef, i, True))

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
                set_button_icon(shiftup_button, resource_path('img/icon_shiftup_off.png'), 24, 24)
            else:
                shiftup_button.setEnabled(True)
                shiftup_button.setToolTip('Shift this wave up by one')
                set_button_icon(shiftup_button, resource_path('img/icon_shiftup.png'), 24, 24)

            if i == len(self.wavedefs) - 1:
                shiftdn_button.setEnabled(False)
                shiftdn_button.setToolTip('')
                set_button_icon(shiftdn_button, resource_path('img/icon_shiftdown_off.png'), 24, 24)
            else:
                shiftdn_button.setEnabled(True)
                shiftdn_button.setToolTip('Shift this wave down by one')
                set_button_icon(shiftdn_button, resource_path('img/icon_shiftdown.png'), 24, 24)

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

        # Shift the array contents
        first = frame.id
        second = frame.id+1 if dir == 'down' else frame.id-1
        t = self.wavedefs[first]
        self.wavedefs[first] = self.wavedefs[second]
        self.wavedefs[second] = t
            
        self.refresh_wavedefs() # Refresh wavedefs state (update buttons, etc)

    # Deletes the wave from the list (and GUI)
    def remove_wavedef(self, id, should_warn=True):
        if should_warn and len(self.wavedefs[id]['Squads']) > 0: # Wave is non-empty. Display dialog!
            diag_title = 'Delete Wave'
            diag_text = 'Are you sure you want to delete this wave?\nAll data will be lost!'
            x = self.central_widget.mapToGlobal(self.central_widget.rect().center()).x()-150 # Anchor dialog to center of window
            y = self.central_widget.mapToGlobal(self.central_widget.rect().center()).y()
            choice_dialog = create_choice_dialog(self.central_widget, diag_title, diag_text, x, y)
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

        self.wavedefs[id]['Label'].setParent(None)
        self.wavedefs[id]['Frames']['SquadFrame'].setParent(None)
        self.wavedefs[id]['Frames']['WaveFrame'].setParent(None)

        self.wavedefs.pop(id) # Remove from array
        # Todo: Remove the squads as well

        self.refresh_wavedefs() # Refresh wavedefs state (update buttons, etc)
        if len(self.wavedefs) < 10:
            self.buttons['Add Wave'].setVisible(True) # We can show the add button again

        # File has been modified
        self.dirty = True
        if self.filename != 'Untitled':
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
        shiftup_button = create_button(self.wavedefs_scrollarea_contents, self.app, 'Shift Up', tooltip='Shift this wave upwards by one', style=ss_button, icon_path=resource_path('img/icon_shiftup.png'), icon_w=24, icon_h=24, size_policy=sp_fixed, draggable=False)
        shiftdn_button = create_button(self.wavedefs_scrollarea_contents, self.app, 'Shift Down', tooltip='Shift this wave downwards by one', style=ss_button, icon_path=resource_path('img/icon_shiftdown.png'), icon_w=24, icon_h=24, size_policy=sp_fixed, draggable=False)
        delete_button = create_button(self.wavedefs_scrollarea_contents, self.app, 'Delete', tooltip='Delete this wave', style=ss_button, icon_path=resource_path('img/icon_delete.png'), icon_w=24, icon_h=24, size_policy=sp_fixed, draggable=False)
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
        wavedef_label = create_label(self.wavedefs_scrollarea_contents, text=wavedef_label_text, style=ss, font=font_label)
        wavedef_label.setAlignment(QtCore.Qt.AlignLeft)
        wavedef_label.setSizePolicy(sp_fixed)
        self.wavedefs_scrollarea_layout.addWidget(wavedef_label)
        wave_layout.addWidget(wave_options_frame)

        # Add new frame for the wave's squads
        squads_frame = QFrame_Drag(self.wavedefs_scrollarea_contents, id=len(self.wavedefs), squad=False)
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
        button_import = create_button(self.central_widget, self.app, 'Open', text=' Open ', tooltip='Load a SpawnCycle from file', style=ss, icon_path=resource_path('img/icon_open.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
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
        button_export = create_button(self.central_widget, self.app, 'Save', text=' Save ', target=partial(self.save_to_file, False), tooltip='Save the current SpawnCycle', style=ss, icon_path=resource_path('img/icon_save.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_export)
        self.buttons.update({'Save' : button_export})

        # Save File As
        button_exportas = create_button(self.central_widget, self.app, 'Save As', text=' Save As ', target=partial(self.save_to_file, True), tooltip='Save the current SpawnCycle with a designated name', style=ss, icon_path=resource_path('img/icon_saveas.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_exportas)
        self.buttons.update({'Save As' : button_exportas})

        # Close File
        button_close = create_button(self.central_widget, self.app, 'Close', text=' Close ', target=self.close_file, tooltip='Close the current SpawnCycle', style=ss, icon_path=resource_path('img/icon_delete.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_close)
        self.buttons.update({'Close' : button_close})

        # Batch options
        button_batch = create_button(self.central_widget, self.app, 'Batch', text=' Batch ', tooltip='Perform operations on the entire SpawnCycle', style=ss, icon_path=resource_path('img/icon_batch.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, options=True, draggable=False)   
        self.options_pane.addWidget(button_batch)
        self.buttons.update({'Batch' : button_batch})

        batch_menu, default_replace_menu, custom_replace_menu = self.init_batch_menu()
        self.default_replace_menu = default_replace_menu
        self.custom_replace_menu = custom_replace_menu
        button_batch.setMenu(batch_menu)
        
        # Analyze Spawncycle
        button_analyze = create_button(self.central_widget, self.app, 'Analyze', text=' Analyze ', tooltip='Display SpawnCycle statistics', target=self.open_analyze_dialog, style=ss, icon_path=resource_path('img/icon_analyze.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)   
        self.options_pane.addWidget(button_analyze)
        self.buttons.update({'Analyze' : button_analyze})

        # Generate Spawncycle
        button_generate = create_button(self.central_widget, self.app, 'Generate', text=' Generate ', tooltip='Generate a SpawnCycle based on pre-determined critera', target=self.open_generate_dialog, style=ss, icon_path=resource_path('img/icon_generate.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)   
        self.options_pane.addWidget(button_generate)
        self.buttons.update({'Generate' : button_generate})

        # Convert SpawnCycles
        button_convert = create_button(self.central_widget, self.app, 'Convert', text=' Convert ', tooltip="Convert SpawnCycles for use with FMX's CD Build", target=self.open_convert_dialog, style=ss, icon_path=resource_path('img/icon_switch.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
        self.options_pane.addWidget(button_convert)
        self.buttons.update({'Convert' : button_convert})

        # View Help
        button_about = create_button(self.central_widget, self.app, 'About', text=' About ', tooltip='Show information about the program', target=self.open_about_dialog, style=ss, icon_path=resource_path('img/icon_about.png'), icon_w=icon_w, icon_h=icon_h, font=font, size_policy=sp, draggable=False)
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
        button_switch = create_button(self.central_widget, self.app, 'ZED Set', text=' Default' if self.zed_mode == 'Custom' else ' Custom', tooltip='Switch current ZED set', target=partial(self.switch_zed_mode, True), icon_path=resource_path('img/icon_switch.png'), icon_w=32, icon_h=32, style=ss_toggle, font=font_label, size_policy=sp_toggle, draggable=False)
        self.buttons.update({'Switch ZEDs' : button_switch})
        self.zed_pane.addWidget(button_switch)

        # Setup Trash ZEDs area
        label_trashzeds = create_label(self.zed_grid_contents, text='Trash ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Trash ZEDs' : label_trashzeds})
        self.gridLayout_2.addWidget(label_trashzeds, 0, 0, 1, 1)
        set_plain_border(label_trashzeds, color=Color(255, 255, 255), width=2)
        self.grid_trashzeds = QtWidgets.QGridLayout()
        self.grid_trashzeds.setObjectName("grid_trashzeds")

        button_cyst = create_button(self.zed_grid_contents, self.app, 'Cyst', tooltip='Cyst', style=ss_button, icon_path=resource_path('img/icon_cyst.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_cyst, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Cyst' : button_cyst})

        button_slasher = create_button(self.zed_grid_contents, self.app, 'Slasher', tooltip='Slasher', style=ss_button, icon_path=resource_path('img/icon_slasher.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_slasher, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Slasher' : button_slasher})

        button_alphaclot = create_button(self.zed_grid_contents, self.app, 'Alpha Clot', tooltip='Alpha Clot', style=ss_button, icon_path=resource_path('img/icon_alphaclot.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_alphaclot, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Alpha Clot' : button_alphaclot})

        button_rioter = create_button(self.zed_grid_contents, self.app, 'Rioter', tooltip='Rioter', style=ss_button, icon_path=resource_path('img/icon_rioter.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_rioter, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Rioter' : button_rioter})

        button_gorefast = create_button(self.zed_grid_contents, self.app, 'Gorefast', tooltip='Gorefast', style=ss_button, icon_path=resource_path('img/icon_gorefast.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_gorefast, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Gorefast' : button_gorefast})

        button_gorefiend = create_button(self.zed_grid_contents, self.app, 'Gorefiend', tooltip='Gorefiend', style=ss_button, icon_path=resource_path('img/icon_gorefiend.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_gorefiend, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'Gorefiend' : button_gorefiend})
        
        button_crawler = create_button(self.zed_grid_contents, self.app, 'Crawler', tooltip='Crawler', style=ss_button, icon_path=resource_path('img/icon_crawler.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_crawler, 3, 0, 1, 1)
        self.zed_pane_buttons.update({'Crawler' : button_crawler})

        button_elitecrawler = create_button(self.zed_grid_contents, self.app, 'Elite Crawler', tooltip='Elite Crawler', style=ss_button, icon_path=resource_path('img/icon_elitecrawler.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_elitecrawler, 3, 1, 1, 1)
        self.zed_pane_buttons.update({'Elite Crawler' : button_elitecrawler})

        button_stalker = create_button(self.zed_grid_contents, self.app, 'Stalker', tooltip='Stalker', style=ss_button, icon_path=resource_path('img/icon_stalker.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_trashzeds.addWidget(button_stalker, 4, 0, 1, 1)
        self.zed_pane_buttons.update({'Stalker' : button_stalker})

        self.gridLayout_2.addLayout(self.grid_trashzeds, 1, 0, 1, 1)

        # Setup Medium ZEDs area
        label_mediumzeds = create_label(self.zed_grid_contents, text='Medium ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Medium ZEDs' : label_mediumzeds})
        self.gridLayout_2.addWidget(label_mediumzeds, 2, 0, 1, 1)
        set_plain_border(label_mediumzeds, color=Color(255, 255, 255), width=2)
        self.grid_mediumzeds = QtWidgets.QGridLayout()
        self.grid_mediumzeds.setObjectName("grid_mediumzeds")

        button_bloat = create_button(self.zed_grid_contents, self.app, 'Bloat', tooltip='Bloat', style=ss_button, icon_path=resource_path('img/icon_bloat.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_bloat, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Bloat' : button_bloat})

        button_husk = create_button(self.zed_grid_contents, self.app, 'Husk', tooltip='Husk', style=ss_button, icon_path=resource_path('img/icon_husk.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_husk, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Husk' : button_husk})

        button_siren = create_button(self.zed_grid_contents, self.app, 'Siren', tooltip='Siren', style=ss_button, icon_path=resource_path('img/icon_siren.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_siren, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Siren' : button_siren})

        button_edar_emp = create_button(self.zed_grid_contents, self.app, 'E.D.A.R Trapper', tooltip='E.D.A.R Trapper', style=ss_button, icon_path=resource_path('img/icon_edar_emp.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_edar_emp, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'E.D.A.R Trapper' : button_edar_emp})

        button_edar_laser = create_button(self.zed_grid_contents, self.app, 'E.D.A.R Blaster', tooltip='E.D.A.R Blaster', style=ss_button, icon_path=resource_path('img/icon_edar_laser.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_edar_laser, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'E.D.A.R Blaster' : button_edar_laser})

        button_edar_rocket = create_button(self.zed_grid_contents, self.app, 'E.D.A.R Bomber', tooltip='E.D.A.R Bomber', style=ss_button, icon_path=resource_path('img/icon_edar_rocket.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_mediumzeds.addWidget(button_edar_rocket, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'E.D.A.R Bomber' : button_edar_rocket})

        self.gridLayout_2.addLayout(self.grid_mediumzeds, 3, 0, 1, 1)

        # Setup Large ZEDs area
        label_largezeds = create_label(self.zed_grid_contents, text='Large ZEDs', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Large ZEDs' : label_largezeds})
        self.gridLayout_2.addWidget(label_largezeds, 4, 0, 1, 1)
        set_plain_border(label_largezeds, color=Color(255, 255, 255), width=2)
        self.grid_largezeds = QtWidgets.QGridLayout()
        self.grid_largezeds.setObjectName("grid_largezeds")

        button_quarterpound = create_button(self.zed_grid_contents, self.app, 'Quarter Pound', tooltip='Quarter Pound', style=ss_button, icon_path=resource_path('img/icon_quarterpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_quarterpound, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Quarter Pound' : button_quarterpound})

        button_quarterpound_raged = create_button(self.zed_grid_contents, self.app, 'Quarter Pound (Enraged)', tooltip='Quarter Pound (Enraged)', style=ss_button, icon_path=resource_path('img/icon_quarterpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_quarterpound_raged, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'Quarter Pound (Enraged)' : button_quarterpound_raged})

        button_fleshpound = create_button(self.zed_grid_contents, self.app, 'Fleshpound', tooltip='Fleshpound', style=ss_button, icon_path=resource_path('img/icon_fleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_fleshpound, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Fleshpound' : button_fleshpound})

        button_fleshpound_raged = create_button(self.zed_grid_contents, self.app, 'Fleshpound (Enraged)', tooltip='Fleshpound (Enraged)', style=ss_button, icon_path=resource_path('img/icon_fleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_fleshpound_raged, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Fleshpound (Enraged)' : button_fleshpound_raged})

        button_scrake = create_button(self.zed_grid_contents, self.app, 'Scrake', tooltip='Scrake', style=ss_button, icon_path=resource_path('img/icon_scrake.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_scrake, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Scrake' : button_scrake})

        button_alphascrake = create_button(self.zed_grid_contents, self.app, 'Alpha Scrake', tooltip='Alpha Scrake', style=ss_button, icon_path=resource_path('img/icon_alphascrake.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_alphascrake, 2, 1, 1, 1)
        self.zed_pane_buttons.update({'Alpha Scrake' : button_alphascrake})

        button_alphafleshpound = create_button(self.zed_grid_contents, self.app, 'Alpha Fleshpound', tooltip='Alpha Fleshpound', style=ss_button, icon_path=resource_path('img/icon_alphafleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_alphafleshpound, 3, 0, 1, 1)
        self.zed_pane_buttons.update({'Alpha Fleshpound' : button_alphafleshpound})

        button_alphafleshpound_raged = create_button(self.zed_grid_contents, self.app, 'Alpha Fleshpound (Enraged)', tooltip='Alpha Fleshpound (Enraged)', style=ss_button, icon_path=resource_path('img/icon_alphafleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_largezeds.addWidget(button_alphafleshpound_raged, 3, 1, 1, 1)
        self.zed_pane_buttons.update({'Alpha Fleshpound (Enraged)' : button_alphafleshpound_raged})
        
        self.gridLayout_2.addLayout(self.grid_largezeds, 5, 0, 1, 1)

        # Setup Bosses area
        label_bosses = create_label(self.zed_grid_contents, text='Bosses', style=ss_label, font=font_label, size_policy=sp_label)
        self.labels.update({'Bosses' : label_bosses})
        self.gridLayout_2.addWidget(label_bosses, 6, 0, 1, 1)
        set_plain_border(label_bosses, color=Color(255, 255, 255), width=2)
        self.grid_bosses = QtWidgets.QGridLayout()
        self.grid_bosses.setObjectName("grid_bosses")

        button_abomination_spawn = create_button(self.zed_grid_contents, self.app, 'Abomination Spawn', tooltip='Abomination Spawn', style=ss_button, icon_path=resource_path('img/icon_abomspawn.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_abomination_spawn, 0, 0, 1, 1)
        self.zed_pane_buttons.update({'Abomination Spawn' : button_abomination_spawn})

        button_kingfleshpound = create_button(self.zed_grid_contents, self.app, 'King Fleshpound', tooltip='King Fleshpound', style=ss_button, icon_path=resource_path('img/icon_kingfleshpound.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_kingfleshpound, 0, 1, 1, 1)
        self.zed_pane_buttons.update({'King Fleshpound' : button_kingfleshpound})

        button_hans = create_button(self.zed_grid_contents, self.app, 'Dr. Hans Volter', tooltip='Dr. Hans Volter', style=ss_button, icon_path=resource_path('img/icon_hans.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_hans, 1, 0, 1, 1)
        self.zed_pane_buttons.update({'Dr. Hans Volter' : button_hans})

        button_patriarch = create_button(self.zed_grid_contents, self.app, 'Patriarch', tooltip='Patriarch', style=ss_button, icon_path=resource_path('img/icon_patriarch.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_patriarch, 1, 1, 1, 1)
        self.zed_pane_buttons.update({'Patriarch' : button_patriarch})

        button_abomination = create_button(self.zed_grid_contents, self.app, 'Abomination', tooltip='Abomination', style=ss_button, icon_path=resource_path('img/icon_abomination.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
        self.grid_bosses.addWidget(button_abomination, 2, 0, 1, 1)
        self.zed_pane_buttons.update({'Abomination' : button_abomination})

        button_matriarch = create_button(self.zed_grid_contents, self.app, 'Matriarch', tooltip='Matriarch', style=ss_button, icon_path=resource_path('img/icon_matriarch.png'), icon_w=icon_w, icon_h=icon_h, size_policy=sp_button)
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
        self.wavedefs_scrollarea = QScrollArea_Drag(self.central_widget)
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
        button_addwave = create_button(self.wavedefs_scrollarea_contents, self.app, 'Add Wave', target=self.add_wavedef, text=' Add Wave', tooltip='Add a new wave to the SpawnCycle', style=ss_button, icon_path=resource_path('img/icon_add.png'), icon_w=16, icon_h=16, font=font_button, size_policy=sp_button, draggable=False)
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
        label_messages_header = create_label(self.central_widget, text='Messages', style=ss_label, font=font_label)
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
            save_dialog = create_choice_dialog(self.central_widget, diag_title, diag_text, x, y)
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
        loading_diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=False)
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
        diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
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
                    squad = format_squad(waves[i][j])
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
            err_dialog = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
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
            save_dialog = create_choice_dialog(self.central_widget, diag_title, diag_text, x, y, yes_target=partial(self.save_to_file, False), cancel_button=True)
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
        errors = parse_syntax_import(filename, lines)
        if len(errors) > 0:
            self.add_message(errors[0])
            if len(errors) > 1:
                self.add_message('\n\n'.join([e.replace(f"Parse errors ('{filename}'):\n\n", '') for e in errors[1:]]), prefix=False)
            diag_text = f'{len(errors)} syntax error(s) were encountered during the import.\nFile could not be loaded.\nSee the Messages box below for more details.'
            diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
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
        loading_diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=False)
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
            save_dialog = create_choice_dialog(self.central_widget, diag_title, diag_text, x, y, yes_target=partial(self.save_to_file, False), cancel_button=True)
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
        errors = parse_syntax_export(self.filename, self.wavedefs)
        if len(errors) > 0:
            self.add_message(errors[0])
            if len(errors) > 1:
                self.add_message('\n\n'.join([e.replace(f"Parse errors{fname}:\n\n", '') for e in errors[1:]]), prefix=False)
            diag_text = f'{len(errors)} syntax error(s) were encountered.\nFile could not be saved.\nSee the Messages box below for more details.'
            diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            diag.exec_() # Show a dialog to tell user to check messages
            return

        # Ask user for filename to save as
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
        button_addwave = create_button(self.wavedefs_scrollarea_contents, self.app, 'Add Wave', target=self.add_wavedef, text=' Add Wave', tooltip='Add a new wave to the SpawnCycle', style=ss_button, icon_path=resource_path('img/icon_add.png'), icon_w=16, icon_h=16, font=font_button, size_policy=sp_button, draggable=False)
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

    # Opens the 'Convert' menu
    def open_convert_dialog(self):
        dialog = QtWidgets.QDialog()
        dialog.ui = ConvertDialog()
        dialog.ui.setupUi(dialog)
        dialog.setWindowTitle('Convert SpawnCycles')
        dialog.setWindowIcon(QtGui.QIcon('img/logo.png'))
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
            diag = create_simple_dialog(self.central_widget, diag_title, diag_text, x, y, button=True)
            diag.setWindowIcon(QtGui.QIcon(resource_path('img/icon_warning.png')))
            diag.exec_() # Show a dialog to tell user to check messages
            return

        # Open the dialog
        dialog = CustomDialog()
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
            save_dialog = create_choice_dialog(self.ui.central_widget, diag_title, diag_text, x, y, yes_target=partial(self.ui.save_to_file, False))
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

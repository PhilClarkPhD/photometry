"""
This program performs zdff analysis on photometry data. Inputs must match the Neurophotometrics format
(https://neurophotometrics.com/).

Created by Phil Clark and Anthony Moreno-Sanchez January 2022.

TODO:
    1. IF DIO == True, add perievent function and call in analyze function
    2. IF DIO == True, output perievent csv with same file name as zdff + '_perievent' on export click
    3. calculate time(s) for self.df_470 for csv output and plotting
    4. finish load_DIO function to calculate timestamps for DIO inputs
"""
import os
import sys

import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
    QFileDialog, QLabel, QInputDialog, QMessageBox, QVBoxLayout

import zdff

# Paths
THIS_SCRIPTS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATA_DIRECTORY = os.path.join(THIS_SCRIPTS_DIRECTORY, "sample_data")

DEFAULT_470_PATH = os.path.join(DATA_DIRECTORY, "470_unilateral.csv")
DEFAULT_415_PATH = os.path.join(DATA_DIRECTORY, "415_unilateral.csv")
DEFAULT_TIMESTAMPS_PATH = os.path.join(DATA_DIRECTORY, "470_timestamps.csv")

# Styles
# See https://materialui.co/colors/ for colors in a consistent palette
BUTTON_COLOR = "#2E7D32"
BACKGROUND_COLOR = "#263238"


def run():
    if not sys.version_info.major == 3 and sys.version_info.minor >= 9:
        print("Error: this program must be run with Python 3.9")
        exit(1)

    print("Loading GUI...")
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        font-size: 20px;
    """)
    gui = Window()
    gui.show()
    print("Done.")
    sys.exit(app.exec_())


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        # set window size
        self.setGeometry(50, 50, 300, 500)
        self.setWindowTitle('photometry analysis')

        # vars to check if data is unilateral or bilateral
        self.bilateral_470 = None
        self.bilateral_415 = None

        # error box
        self.error_box = QMessageBox()
        self.error_box.setIcon(QMessageBox.Critical)

        # Set Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # add home page to window
        layout.addWidget(self.home())

    def home(self):
        """
        Creates the home page where buttons and labels are displayed
        """
        home = QWidget()
        button_layout = QVBoxLayout()
        home.setStyleSheet(f'background-color: {BACKGROUND_COLOR};')

        # Define buttons / labels and add them to layout

        # Labels for fields are conventionally above their corresponding UI element
        # 470 file label and button
        self._run_sample_label = QLabel("470 file", self)
        button_layout.addWidget(self._run_sample_label)
        self._run_sample_label.setStyleSheet('color: white;')

        run_sample_button = QPushButton('Load and analyze sample data', self)
        run_sample_button.clicked.connect(self.on_analyze_sample_click)
        button_layout.addWidget(run_sample_button)

        # 470 file label and button
        self._470_label = QLabel("470 file", self)
        button_layout.addWidget(self._470_label)
        self._470_label.setStyleSheet('color: white;')

        load_470_btn = QPushButton('Load 470 writer', self)
        load_470_btn.clicked.connect(self.on_load_470_click)
        button_layout.addWidget(load_470_btn)

        # 415 file label and button
        self._415_label = QLabel("415 file", self)
        button_layout.addWidget(self._415_label)
        self._415_label.setStyleSheet('color: white;')

        load_415_btn = QPushButton('Load 415 writer', self)
        load_415_btn.clicked.connect(self.on_load_415_click)
        button_layout.addWidget(load_415_btn)

        # timestamps label and button
        self._timestamps_label = QLabel("timestamps file", self)
        button_layout.addWidget(self._timestamps_label)
        self._timestamps_label.setStyleSheet('color: white;')

        load_timestamps_btn = QPushButton('load 470 timestamps', self)
        load_timestamps_btn.clicked.connect(self.on_load_timestamps_click)
        button_layout.addWidget(load_timestamps_btn)

        # DIO label and button
        self._DIO_label = QLabel("DIO file", self)
        button_layout.addWidget(self._DIO_label)
        self._DIO_label.setStyleSheet('color: white;')

        load_DIO_button = QPushButton('load DIO', self)
        load_DIO_button.clicked.connect(self.load_DIO)
        button_layout.addWidget(load_DIO_button)

        # analyze button
        analyze_btn = QPushButton('analyze', self)
        analyze_btn.clicked.connect(self.analyze)
        button_layout.addWidget(analyze_btn)

        # export button
        export_btn = QPushButton('export', self)
        export_btn.clicked.connect(self.export)
        button_layout.addWidget(export_btn)

        buttons = [
            analyze_btn,
            export_btn,
            load_415_btn,
            load_470_btn,
            load_DIO_button,
            load_timestamps_btn,
            run_sample_button,
        ]

        for button in buttons:
            button.setStyleSheet(f'background-color: {BUTTON_COLOR}; color: white')

        # add button_layout to home tab
        home.setLayout(button_layout)

        return home

    def on_load_470_click(self):
        """
        asks user to select .csv file containing 470 data - required for analyze/export!
        """
        # Path.home() is an OS-portable way to find the home directory
        file = QFileDialog.getOpenFileName(self, 'Open 470 writer', DATA_DIRECTORY)
        file_path = file[0]
        self._470_label.setText(f"470 file: {os.path.basename(file_path)}")
        self.load_470_from_path(file_path)

    def load_470_from_path(self, file_path:str) -> None:
        # load file and create attribute in Window class
        self.df_470 = pd.read_csv(file_path)
        setattr(Window, 'df_470', True)

        # check if data is bilateral
        if 'Region1G' in self.df_470.columns:
            self.bilateral_470 = True
        else:
            self.bilateral_470 = False

    def on_load_415_click(self):
        """
        asks user to select .csv file containing 415 data - required for analyze/export!
        """
        file = QFileDialog.getOpenFileName(self, 'Open 415 writer', DATA_DIRECTORY)
        file_path = file[0]
        self._415_label.setText(f"415 file: {str(os.path.basename(file_path))}")
        self.load_415_from_path(file_path)

    def load_415_from_path(self, file_path:str) -> None:
        # load file and create attribute in Window class
        self.df_415 = pd.read_csv(file_path)
        setattr(Window, 'df_415', True)

        # check if data is bilateral
        if 'Region1G' in self.df_415.columns:
            self.bilateral_415 = True
        else:
            self.bilateral_415 = False

    def on_load_timestamps_click(self):
        """
        asks user to select .csv file containing 470 timestamp data - required for analyze/export!
        """
        file = QFileDialog.getOpenFileName(self, 'Open 470 timestamp file', DATA_DIRECTORY)
        file_path = file[0]
        self._timestamps_label.setText(f"Timestamps file: {str(os.path.basename(file_path))}")

    def load_timestamps_from_path(self, file_path:str) -> None:
        # load file and create attribute in Window class
        self.df_timestamps = pd.read_csv(file_path)
        setattr(Window, 'df_timestamps', True)
        self.df_timestamps.columns = ['Timestamp', 'FrameCounter']

    def load_DIO(self):
        """
        asks user to select .csv file containing DIO data - not required for analyze/export
        """
        file = QFileDialog.getOpenFileName(self, 'Open 415 writer', DATA_DIRECTORY)
        file_path = file[0]
        self._DIO_label.setText(f"DIO file: {str(os.path.basename(file_path))}")

        self.df_DIO = pd.read_csv(file_path)

        # TODO: Finish this per to-do list
        # Should this raise NotImplementedError?

    def check_files_loaded(self):
        """
        Check that files have been loaded
        """
        if not hasattr(Window, 'df_470') or not hasattr(Window, 'df_415') or not hasattr(Window, 'df_timestamps'):
            self.error_box.setText('Must load 470 writer, 415 writer, and timestamp files!')
            self.error_box.exec_()
        else:
            pass

    def check_inputs(self):
        """
        This method checks input files and dataframes and raises an error box in the GUI if a check fails
        """
        self.check_files_loaded()

        # check naming of data columns in 415 and 470 writers
        if 'Region0G' not in self.df_470.columns or 'Region0G' not in self.df_415.columns:
            self.error_box.setText('Check data column names! [Region0G, Region1G]')
            self.error_box.exec_()

        # check that 470 and 415 row numbers are equal and correct if not True -  required for analyze/export
        if len(self.df_470) != len(self.df_415):
            self.df_470.drop(self.df_470.tail(1).index, inplace=True)
            self.df_timestamps.drop(self.df_timestamps.tail(1).index, inplace=True)
        else:
            pass

        # check 470 and 415 row number again and bring up error box if dataframes are not equal
        if len(self.df_470) != len(self.df_415):
            self.error_box.setText('470 and 415 writer must have equal number of rows!')
            self.error_box.exec_()

        if len(self.df_timestamps) != len(self.df_470):
            self.error_box.setText('470 writer and 470 timestamp files must have equal number of rows!')
            self.error_box.exec_()
            self.analyze.kill()  # TODO: self.analyze is a function without a kill method

        # check that bilateral variable for 470 and 415 match
        if self.bilateral_470 != self.bilateral_415 and self.bilateral_470 is not None:
            self.error_box.setText('Number of Regions do not match between 470 and 415')
            self.error_box.exec_()
            self.analyze.kill()  # TODO: self.analyze is a function without a kill method

    def analyze(self):
        """
        This method runs the actual zdff analysis we want as an output and plots the result
        """
        self.check_inputs()

        # add timestamps column and time column to self.df_470
        self.df_470['Timestamp'] = self.df_timestamps['Timestamp']
        self.df_470['Time(s)'] = [(x - self.df_470['Timestamp'][0]) / 1000 for x in self.df_470['Timestamp']]

        # compute zdff for Region0 and Region1 (if bilateral) or Region0 (if unilateral). Show plot of final zdff
        if self.bilateral_470:
            self.df_470['zdff_Region0G'] = zdff.get_zdFF(self.df_415['Region0G'].values, self.df_470['Region0G'].values)
            self.df_470['zdff_Region1G'] = zdff.get_zdFF(self.df_415['Region1G'].values, self.df_470['Region1G'].values)

            a = pg.plot(self.df_470['Time(s)'], self.df_470['zdff_Region0G'], pen='g', title='zdff_Region0G', )
            a.setLabel('left', "zdFF")
            a.setLabel('bottom', "time (s)")

            purple = pg.mkPen(color=(148, 0, 211))
            b = pg.plot(self.df_470['Time(s)'], self.df_470['zdff_Region1G'], pen=purple, title='zdff_Region1G')
            b.setLabel('left', "zdFF")
            b.setLabel('bottom', "time (s)")

        else:
            self.df_470['zdff_Region0G'] = zdff.get_zdFF(self.df_415['Region0G'].values, self.df_470['Region0G'].values)

            a = pg.plot(self.df_470['Time(s)'], self.df_470['zdff_Region0G'], pen='g', title='zdff_Region0G', )
            a.setLabel('left', "zdFF")
            a.setLabel('bottom', "time (s)")

    def on_analyze_sample_click(self) -> None:
        self.load_470_from_path(DEFAULT_470_PATH)
        self.load_415_from_path(DEFAULT_415_PATH)
        self.load_timestamps_from_path(DEFAULT_TIMESTAMPS_PATH)
        self.analyze()

    def name_file(self):
        """
        Ask user to name output file
        """
        get_name = QInputDialog()
        name, ok = get_name.getText(self, 'Enter file name', 'Enter file name')
        return name

    def export(self):
        """
        Ask user to select directory for saving .csv output
        """
        self.check_files_loaded()

        name = str(self.name_file())
        file = QFileDialog.getExistingDirectory(self, 'Select folder', DATA_DIRECTORY)
        file_path = os.path.join(file, name)

        self.df_470.to_csv(file_path + '.csv', sep=',', index=False)


if __name__ == "__main__":
    run()

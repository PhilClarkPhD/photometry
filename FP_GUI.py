'''
This program performs zdff analysis on photometry data. Inputs must match the Neurophotometrics format
(https://neurophotometrics.com/). Created by Phil Clark and Anthony Moreno-Sanchez January 2022.
'''

'''
TODO:
    1. IF DIO == True, add perievent function and call in analyze function
    2. IF DIO == True, output perievent csv with same file name as zdff + '_perievent' on export click
    3. calculate time(s) for self.df_470 for csv output and plotting
    4. finish load_DIO function to calculate timestamps for DIO inputs
'''

import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, \
    QFileDialog, QLabel, QInputDialog, QMessageBox, QTabWidget, QVBoxLayout, \
    QGridLayout, QCheckBox, QComboBox, QHBoxLayout
import sys
import pandas as pd
import os
import zdFF

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

        #add home page to window
        layout.addWidget(self.home())

    def home(self):
        '''
        Creates the home page where buttons and labels are displayed
        '''

        home = QWidget()
        button_layout = QVBoxLayout()
        home.setStyleSheet('background-color: black;')

        ## Define buttons / labels and add them to layout

        # load 470 button
        load_470_btn = QPushButton('Load 470 writer', self)
        load_470_btn.clicked.connect(self.load_470)
        button_layout.addWidget(load_470_btn)

        # label for 470 file
        self._470_label = QLabel("470 file: {}".format(''), self)
        button_layout.addWidget(self._470_label)
        self._470_label.setStyleSheet('color: white;')

        # load 415 button
        load_415_btn = QPushButton('Load 415 writer', self)
        load_415_btn.clicked.connect(self.load_415)
        button_layout.addWidget(load_415_btn)

        # label for 415 file
        self._415_label = QLabel("415 file: {}".format(''), self)
        button_layout.addWidget(self._415_label)
        self._415_label.setStyleSheet('color: white;')

        # load timestamps button
        load_timestamps_btn = QPushButton('load 470 timestamps', self)
        load_timestamps_btn.clicked.connect(self.load_timestamps)
        button_layout.addWidget(load_timestamps_btn)

        # label for timestamps
        self._timestamps_label = QLabel("timestamps file: {}".format(''), self)
        button_layout.addWidget(self._timestamps_label)
        self._timestamps_label.setStyleSheet('color: white;')

        # load DIO button
        load_DIO_btn = QPushButton('load DIO', self)
        load_DIO_btn.clicked.connect(self.load_DIO)
        button_layout.addWidget(load_DIO_btn)

        # label for DIO
        self._DIO_label = QLabel("DIO file: {}".format(''), self)
        button_layout.addWidget(self._DIO_label)
        self._DIO_label.setStyleSheet('color: white;')


        # analyze button
        analyze_btn = QPushButton('analyze', self)
        analyze_btn.clicked.connect(self.analyze)
        button_layout.addWidget(analyze_btn)


        # export button
        export_btn = QPushButton('export', self)
        export_btn.clicked.connect(self.export)
        button_layout.addWidget(export_btn)


        # set button styles
        load_470_btn.setStyleSheet('background-color: green; color: white;')
        load_415_btn.setStyleSheet('background-color: green; color: white;')
        load_DIO_btn.setStyleSheet('background-color: green; color: white;')
        load_timestamps_btn.setStyleSheet('background-color: green; color: white;')
        analyze_btn.setStyleSheet('background-color: green; color: white;')
        export_btn.setStyleSheet('background-color: green; color: white;')

        # add button_layout to home tab
        home.setLayout(button_layout)

        return home


    def load_470(self):
        '''
        asks user to select .csv file containing 470 data - required for analyze/export!
        '''

        file = QFileDialog.getOpenFileName(self, 'Open 470 writer', r'C:\\')
        file_path = file[0]
        self._470_label.setText("470 file: {}".format(str(os.path.basename(file_path))))

        # load file and create attribute in Window class
        self.df_470 = pd.read_csv(file_path)
        setattr(Window, 'df_470', True)

        # check if data is bilateral
        if 'Region1G' in self.df_470.columns:
            self.bilateral_470 = True
        else:
            self.bilateral_470 = False


    def load_415(self):
        '''
        asks user to select .csv file containing 415 data - required for analyze/export!
        '''

        file = QFileDialog.getOpenFileName(self, 'Open 415 writer', r'C:\\')
        file_path = file[0]
        self._415_label.setText("415 file: {}".format(str(os.path.basename(file_path))))

        # load file and create attribute in Window class
        self.df_415 = pd.read_csv(file_path)
        setattr(Window, 'df_415', True)

        # check if data is bilateral
        if 'Region1G' in self.df_415.columns:
            self.bilateral_415 = True
        else:
            self.bilateral_415 = False


    def load_timestamps(self):
        '''
        asks user to select .csv file containing 470 timestamp data - required for analyze/export!
        '''

        file = QFileDialog.getOpenFileName(self, 'Open 470 timestamp file', r'C:\\')
        file_path = file[0]
        self._timestamps_label.setText("timestamps file: {}".format(str(os.path.basename(file_path))))

        # load file and create attribute in Window class
        self.df_timestamps = pd.read_csv(file_path)
        setattr(Window, 'df_timestamps', True)

        self.df_timestamps.columns = ['Timestamp','FrameCounter']


    def load_DIO(self):
        '''
        asks user to select .csv file containing DIO data - not required for analyze/export
        '''

        file = QFileDialog.getOpenFileName(self, 'Open 415 writer', r'C:\\')
        file_path = file[0]
        self._DIO_label.setText("DIO file: {}".format(str(os.path.basename(file_path))))

        self.df_DIO = pd.read_csv(file_path)

        #...Finish this per to-do list

    def check_files_loaded(self):
        '''
        Check that files have been loaded
        '''

        if not hasattr(Window, 'df_470') or not hasattr(Window, 'df_415') or not hasattr(Window, 'df_timestamps'):
            self.error_box.setText('Must load 470 writer, 415 writer, and timestamp files!')
            self.error_box.exec_()
        else:
            pass

    def check_inputs(self):
        '''
        This method checks input files and dataframes and raises an error box in the GUI if a check fails
        '''

        self.check_files_loaded()

        # check naming of data columns in 415 and 470 writers
        if 'Region0G' not in self.df_470.columns or 'Region0G' not in self.df_415.columns:
            self.error_box.setText('Check data column names! [Region0G, Region1G]')
            self.error_box.exec_()

        # check that 470 and 415 row numbers are equal and correct if not True -  required for analyze/export
        if len(self.df_470) != len(self.df_415):
            self.df_470.drop(self.df_470.tail(1).index, inplace = True)
            self.df_timestamps.drop(self.df_timestamps.tail(1).index, inplace = True)
        else:
            pass

        # check 470 and 415 row number again and bring up error box if df's are not equal
        if len(self.df_470) != len(self.df_415):
            self.error_box.setText('470 and 415 writer must have equal number of rows!')
            self.error_box.exec_()


        if len(self.df_timestamps) != len(self.df_470):
            self.error_box.setText('470 writer and 470 timestamp files must have equal number of rows!')
            self.error_box.exec_()
            self.analyze.kill()

        # check that bilateral variable for 470 and 415 match
        if self.bilateral_470 != self.bilateral_415 and self.bilateral_470 != None:
            self.error_box.setText('Number of Regions do not match between 470 and 415')
            self.error_box.exec_()
            self.analyze.kill()


    def analyze(self):
        '''
        This method runs the actual zdff analysis we want as an output and plots the result
        '''

        self.check_inputs()

        #add timestamps column and time column to self.df_470
        self.df_470['Timestamp'] = self.df_timestamps['Timestamp']
        self.df_470['Time(s)'] = [(x - self.df_470['Timestamp'][0])/1000 for x in self.df_470['Timestamp']]


        # compute zdff for Region0 and Region1 (if bilateral) or Region0 (if unilateral). Show plot of final zdff
        if self.bilateral_470 == True:
            self.df_470['zdff_Region0G'] = zdFF.get_zdFF(self.df_415['Region0G'].values,self.df_470['Region0G'].values)
            self.df_470['zdff_Region1G'] = zdFF.get_zdFF(self.df_415['Region1G'].values,self.df_470['Region1G'].values)

            a = pg.plot(self.df_470['Time(s)'], self.df_470['zdff_Region0G'], pen='g', title='zdff_Region0G', )
            a.setLabel('left', "zdFF")
            a.setLabel('bottom', "time (s)")

            purple = pg.mkPen(color=(148, 0, 211))
            b = pg.plot(self.df_470['Time(s)'], self.df_470['zdff_Region1G'], pen=purple, title='zdff_Region1G')
            b.setLabel('left', "zdFF")
            b.setLabel('bottom', "time (s)")

        else:
            self.df_470['zdff_Region0G'] = zdFF.get_zdFF(self.df_415['Region0G'].values, self.df_470['Region0G'].values)

            a = pg.plot(self.df_470['Time(s)'], self.df_470['zdff_Region0G'], pen='g', title='zdff_Region0G', )
            a.setLabel('left', "zdFF")
            a.setLabel('bottom', "time (s)")


    def name_file(self):
        '''
        Ask user to name output file
        '''

        get_name = QInputDialog()
        name, ok = get_name.getText(self, 'Enter file name', 'Enter file name')
        return name

    def export(self):
        '''
        Ask user to select directory for saving .csv output
        '''

        self.check_files_loaded()

        name = str(self.name_file())
        file = QFileDialog.getExistingDirectory(self, 'Select folder', r'C:\\')
        file_path = file + '/' + name

        self.df_470.to_csv(file_path + '.csv', sep=',', index=False)

def run():
    app = QApplication(sys.argv)
    GUI = Window()
    GUI.show()
    sys.exit(app.exec_())

run()
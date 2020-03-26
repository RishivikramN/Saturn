from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QSplashScreen)
from PyQt5.QtGui import *
from PyQt5.QtChart import *
from PyQt5.QtCore import *
import csv
import sys
import time

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.dark_palette = QPalette()

        self.dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        self.dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        self.dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        self.dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        self.dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        self.dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        self.dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.source_df_dict={}
        self.target_df_dict={}
        self.target_df_modulename={}
        self.target_df_error={}
        self.sourcefilename = ''
        self.targetfilename = ''
        QApplication.setPalette(self.dark_palette)
        QApplication.setStyle("Fusion")
        #self.ShowSplashscreen()
        self.MainScreenLayout()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.sourcegroupbox, 0, 1)
        mainLayout.addWidget(self.targetgroupbox, 1, 1)     
        mainLayout.addWidget(self.comparebutton, 2, 1)   
        mainLayout.addWidget(self.exportresultbutton, 3, 1)        
        mainLayout.setColumnStretch(1, 2)
        self.setLayout(mainLayout)

    def ShowSplashscreen(self):
        splash_pix = QPixmap('DD.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        splash.setEnabled(False)
        splash.setMask(splash_pix.mask())
        splash.show()
        timer = QElapsedTimer()
        timer.start()
        while timer.elapsed() < 2000 :
            pass
    def MainScreenLayout(self):
        #Groupbox
        self.sourcegroupbox = QGroupBox("Choose the Source File")
        self.targetgroupbox = QGroupBox("Choose the Target File")
        
        sourceLabel = QLabel("Source File:")
        self.sourcetextbox = QLineEdit(self)
        self.sourcetextbox.setReadOnly(True)
        sourceFileButton = QPushButton("Open Source File")
        sourceFileButton.clicked.connect(self.SourceFileOpener)
        
        targetLabel = QLabel("Target File:")
        self.targettextbox = QLineEdit(self)
        self.targettextbox.setReadOnly(True)
        targetFileButton = QPushButton("Open Target File")
        targetFileButton.clicked.connect(self.TargetFileOpener)

        sourcelayout = QVBoxLayout()
        sourcelayout.addWidget(sourceLabel)
        sourcelayout.addWidget(self.sourcetextbox)        
        sourcelayout.addWidget(sourceFileButton)
        
        sourcelayout.addStretch(1)       
        

        targetlayout = QVBoxLayout()
        targetlayout.addWidget(targetLabel)
        targetlayout.addWidget(self.targettextbox)
        targetlayout.addWidget(targetFileButton)
        targetlayout.addStretch(1)
        
        self.comparebutton = QPushButton("Compare Result")
        self.comparebutton.clicked.connect(self.CreateChart)

        self.exportresultbutton = QPushButton("Export Result")
        self.exportresultbutton.clicked.connect(self.ExportResultsInCSV)

        self.sourcegroupbox.setLayout(sourcelayout)
        self.targetgroupbox.setLayout(targetlayout)

    def SourceFileOpener(self):
        self.sourcefilename,_ = QFileDialog.getOpenFileName(self,"Source File","","CSV Files (*.csv)")
        self.sourcetextbox.setText(self.sourcefilename)

    def TargetFileOpener(self):
        self.targetfilename,_ = QFileDialog.getOpenFileName(self,"Target File","","CSV Files (*.csv)")
        self.targettextbox.setText(self.targetfilename)

    def ExportResultsInCSV(self):
        if(self.CSVDataPreprocessor()):
            return 
        exportfilename,_ = QFileDialog.getSaveFileName(self,"Save Result File","","CSV Files (*.csv)")
        with open(exportfilename, 'w', newline='') as output_file:
            fieldnames=['ScenarioName','ScenarioRunStatus','ModuleName','Error']
            writer = csv.DictWriter(output_file,fieldnames=fieldnames)
            writer.writeheader()
            
            for item in self.modified:
                writer.writerow({'ScenarioName':item,'ScenarioRunStatus':self.target_df_dict[item],'ModuleName':self.target_df_modulename[item],'Error':self.target_df_error[item]})

    def CSVComparer(self):
        source_keys = set(self.source_df_dict.keys())
        target_keys = set(self.target_df_dict.keys())
        intersect_keys = source_keys.intersection(target_keys)
        added = source_keys - target_keys
        removed = target_keys - source_keys
        modified = {i : (self.source_df_dict[i], self.target_df_dict[i]) for i in intersect_keys if self.source_df_dict[i] != self.target_df_dict[i]}
        same = set(i for i in intersect_keys if self.source_df_dict[i] == self.target_df_dict[i])
        return added, removed, modified, same

    def CSVDataPreprocessor(self):
        maxInt = sys.maxsize
        #Input Exception Handler
        if self.sourcefilename == '' or self.targetfilename == '':
            alert = QMessageBox.warning(self,'Alert',"No input file has been chosen",QMessageBox.Ok)
            return True
        #Source Data preprocessing
        while True:
            try:
                csv.field_size_limit(maxInt)
                with open(self.sourcefilename, mode='r') as csv_file:
                    csv_reader = csv.DictReader(csv_file,delimiter='\t')
                    for row in csv_reader:
                        self.source_df_dict.update(dict({row["ScenarioName"]:row["ScenarioRunStatus"]}))
                    break
            except OverflowError:
                maxInt = int(maxInt/10)
        #Target Data preprocessing
        while True:
            try:
                csv.field_size_limit(maxInt)
                with open(self.targetfilename, mode='r') as csv_file:
                    csv_reader = csv.DictReader(csv_file,delimiter='\t')
                    for row in csv_reader:
                        self.target_df_dict.update(dict({row["ScenarioName"]:row["ScenarioRunStatus"]}))
                        self.target_df_modulename.update(dict({row["ScenarioName"]:row["ModuleName"]}))
                        self.target_df_error.update(dict({row['ScenarioName']:row["Error"]}))
                    break
            except OverflowError:
                maxInt = int(maxInt/10)
        self.added, self.removed, self.modified, self.same = self.CSVComparer()
    
    def StatusCounter(self):
        self.success=0
        self.failed=0
        self.running=0
        for item in self.modified.keys():
            if str(self.target_df_dict[item]) == 'Completed Sucessfully':
                self.success+=1
            elif str(self.target_df_dict[item]) == 'Completed With Errors':
                self.failed+=1
            elif str(self.target_df_dict[item]) == 'Running':
                self.running+=1
    def CreateChart(self):
        if(self.CSVDataPreprocessor()):
            return
        self.StatusCounter()
        if self.success == 0 or self.failed==0:
            alert = QMessageBox.warning(self,'Alert',"No Difference Between Both Reports",QMessageBox.Ok)
            return
        data = {
        "Success=="+str(self.success): (self.success, QColor("green")),
        "Failed=="+str(self.failed): (self.failed, QColor("red")),
        "Running=="+str(self.running): (self.running, QColor("yellow"))
        }

        series = QPieSeries()
        
        for name, (value, color) in data.items():
            _slice = series.append(name, value)
            _slice.setBrush(color)

        chart = QChart()
        
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)
        chart.addSeries(series)
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        

        self.chartdialog = QDialog()
        self.chartdialog.setWindowTitle("Regression Comparison Chart")
        
        chartlayout = QHBoxLayout()
        chartlayout.addWidget(chartview)
        self.chartdialog.setLayout(chartlayout)
        self.chartdialog.resize(500,500)
        self.chartdialog.show()

if __name__ == '__main__':
    appctxt = ApplicationContext()
    gallery = WidgetGallery()
    gallery.setMinimumSize(500,500)
    gallery.setMaximumSize(500,500)
    gallery.show()
    sys.exit(appctxt.app.exec_())

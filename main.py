from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QSplashScreen,QMenuBar,QStatusBar,QMainWindow)
from PyQt5.QtGui import *
from PyQt5.QtChart import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui
import csv
import sys
import time
import xlsxwriter
from xlrd import open_workbook

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
        self.source_df_module_name={}
        self.source_df_error={}
        self.target_df_dict={}
        self.target_df_modulename={}
        self.target_df_error={}
        self.sourcefilename = ''
        self.targetfilename = ''
        self.modified={} 
        self.same={}
        self.added={}
        QApplication.setPalette(self.dark_palette)
        QApplication.setStyle("Fusion")

        self.MainScreenLayout()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.sourcegroupbox, 0, 1)
        mainLayout.addWidget(self.targetgroupbox, 1, 1)     
        mainLayout.addWidget(self.comparebutton, 2, 1)   
        mainLayout.addWidget(self.exportresultbutton, 3, 1)        
        mainLayout.setColumnStretch(1, 2)
        self.setLayout(mainLayout)

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
        
        self.StatusCounter()

        exportfilename,_ = QFileDialog.getSaveFileName(self,"Save Result File","","Excel Files (*.xlsx)")
        
        workbook= xlsxwriter.Workbook(exportfilename)
        deltaworksheet=workbook.add_worksheet('Delta Report')
        failedworksheet=workbook.add_worksheet('Failed In Both Run')
        passedworksheet=workbook.add_worksheet('Passed In Both Run')
        row=0
        col=0

        deltaworksheet.write(row,col,'ScenarioName')
        deltaworksheet.write(row,col+1,'ScenarioRunStatus')
        deltaworksheet.write(row,col+2,'ModuleName')
        deltaworksheet.write(row,col+3,'Error')
        row+=1
        for item in self.modified.keys():
            deltaworksheet.write(row,col,item)
            deltaworksheet.write(row,col+1,self.target_df_dict[item])
            deltaworksheet.write(row,col+2,self.target_df_modulename[item])
            deltaworksheet.write(row,col+3,self.target_df_error[item])
            row+=1

        row=0
        col=0

        failedworksheet.write(row,col,'ScenarioName')
        failedworksheet.write(row,col+1,'ScenarioRunStatus')
        failedworksheet.write(row,col+2,'ModuleName')
        failedworksheet.write(row,col+3,'Error')
        row+=1
        for item in self.same_failed_dict.keys():
            failedworksheet.write(row,col,item)
            failedworksheet.write(row,col+1,self.source_df_dict[item])
            failedworksheet.write(row,col+2,self.source_df_module_name[item])
            failedworksheet.write(row,col+3,self.source_df_error[item])
            row+=1

        row=0
        col=0

        passedworksheet.write(row,col,'ScenarioName')
        passedworksheet.write(row,col+1,'ScenarioRunStatus')
        passedworksheet.write(row,col+2,'ModuleName')
        passedworksheet.write(row,col+3,'Error')
        row+=1
        for item in self.same_success_dict.keys():
            passedworksheet.write(row,col,item)
            passedworksheet.write(row,col+1,self.source_df_dict[item])
            passedworksheet.write(row,col+2,self.source_df_module_name[item])
            passedworksheet.write(row,col+3,self.source_df_error[item])
            row+=1

        workbook.close()
        
    def CSVComparer(self):
        source_keys = set(self.source_df_dict.keys())
        target_keys = set(self.target_df_dict.keys())
        intersect_keys = source_keys.intersection(target_keys)
        added = source_keys - target_keys
        removed = target_keys - source_keys
        added = {i:self.source_df_dict[i] for i in added}
        modified = {i: (self.source_df_dict[i], self.target_df_dict[i]) for i in intersect_keys if self.source_df_dict[i] != self.target_df_dict[i]}
        same = {i: (self.source_df_dict[i], self.target_df_dict[i]) for i in intersect_keys if self.source_df_dict[i] == self.target_df_dict[i]}
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
                        self.source_df_module_name.update(dict({row["ScenarioName"]:row["ModuleName"]}))
                        self.source_df_error.update(dict({row['ScenarioName']:row["Error"]}))
                    
                #Cleaning the dictionary
                dirtykeys=[]
                for item in self.source_df_dict.keys():
                    if item  == '':
                        continue
                    if (str(self.source_df_dict[item]) == 'Completed Sucessfully'):
                        pass
                    elif (str(self.source_df_dict[item]) == 'Completed With Errors'):
                        pass
                    elif (str(self.source_df_dict[item]) == 'Failed in Initial Run'):
                        pass
                    elif (str(self.source_df_dict[item]) =='Running'):
                        pass
                    elif (str(self.source_df_dict[item]) =='Failed in First Run'):
                        pass
                    else:
                        dirtykeys.append(item)
                
                for item in dirtykeys:
                    del self.source_df_dict[item]

                dirtykeys=[]
                for item in self.source_df_module_name.keys():
                    if item  == '':
                        continue
                    if (self.source_df_module_name[item] == '') or (self.source_df_module_name[item] is None):
                        dirtykeys.append(item)
                for item in dirtykeys:
                    del self.source_df_module_name[item]

                dirtykeys=[]
                for item in self.source_df_error.keys():
                    if self.source_df_error[item] is None:
                        dirtykeys.append(item)
                for item in dirtykeys:
                    del self.source_df_error[item]
                
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
                   
                #Cleaning the dictionary
                dirtykeys=[]
                for item in self.target_df_dict.keys():
                    if item  == '':
                        continue
                    if (str(self.target_df_dict[item]) == 'Completed Sucessfully'):
                        pass
                    elif (str(self.target_df_dict[item]) =='Completed With Errors'):
                        pass
                    elif (str(self.target_df_dict[item]) =='Failed in Initial Run'):
                        pass
                    elif (str(self.target_df_dict[item]) =='Running'):
                        pass
                    elif (str(self.target_df_dict[item]) =='Failed in First Run'):
                        pass
                    else:
                        dirtykeys.append(item)
                for item in dirtykeys:
                    del self.target_df_dict[item]

                dirtykeys=[]
                for item in self.target_df_modulename.keys():
                    if item  == '':
                        continue
                    if (self.target_df_modulename[item] == '') or (self.target_df_modulename[item] is None):
                        dirtykeys.append(item)
                for item in dirtykeys:
                    del self.target_df_modulename[item]
                
                dirtykeys=[]
                for item in self.target_df_error.keys():
                    if self.target_df_error[item] is None :
                        dirtykeys.append(item)
                for item in dirtykeys:
                    del self.target_df_error[item]
                
                break
            except OverflowError:
                maxInt = int(maxInt/10)
        self.added, self.removed, self.modified, self.same = self.CSVComparer()
    
    def StatusCounter(self):

        self.success=0
        self.failed=0
        self.same_success=0
        self.same_failed=0
        self.source_others=0
        self.target_others=0

        self.source_success_dict={}
        self.source_failed_dict={}

        self.same_success_dict={}
        self.same_failed_dict={}

            
        for item in self.source_df_dict.keys():
            try:
                if str(self.source_df_dict[item]) == 'Completed Sucessfully':
                    self.source_success_dict.update(dict({item:self.source_df_dict[item]}))
                elif str(self.source_df_dict[item]) == 'Completed With Errors':
                    self.source_failed_dict.update(dict({item:self.source_df_dict[item]}))
                else:
                    self.source_others+=1
            except KeyError as error:
                print(error)
        
        for item in self.modified.keys():
            if str(self.target_df_dict[item]) == 'Completed Sucessfully':
                self.success+=1
            elif str(self.target_df_dict[item]) == 'Completed With Errors':
                self.failed+=1
            else:
                self.target_others+=1
        
        for item in self.added:
            if str(self.source_df_dict[item]) == 'Completed Sucessfully':
                self.same_success+=1
            elif str(self.source_df_dict[item]) == 'Completed With Errors':
                self.same_failed+=1
            else:
                self.target_others+=1
            
        for item in self.same.keys():
            if str(self.source_df_dict[item]) == 'Completed Sucessfully':
                self.same_success+=1
                self.same_success_dict.update(dict({item:self.source_df_dict[item]}))
            elif str(self.source_df_dict[item]) == 'Completed With Errors':
                self.same_failed+=1
                self.same_failed_dict.update(dict({item:self.source_df_dict[item]}))
            else:
                self.target_others+=1
        
        return

    def CreateChart(self):
        if(self.CSVDataPreprocessor()):
           return
        self.StatusCounter()
        if self.success == 0 or self.failed==0:
            alert = QMessageBox.warning(self,'Alert',"No Difference Between Both Reports",QMessageBox.Ok)
            return
        self.chartdialog = ChartDialog(self)
        self.chartdialog.show()

#Classes for Chart UI
class Ui_MainWindow(object):
    def setupUi(self, Dialog):
        Dialog.resize(1600, 500)
        self.centralwidget = QWidget(Dialog)
        self.centralwidget.setWindowTitle("Regression Comparison chart")

        oldregressionlabel=QLabel(self.centralwidget)
        oldregressionlabel.setText("Old Regression Run")
        oldregressionlabel.move(60,80)

        newregressionlabel = QLabel(self.centralwidget)
        newregressionlabel.setText("New Regression Run")
        newregressionlabel.move(60,220)
        
        legend_failed = QLabel(self.centralwidget)
        legend_failed.setText("Failed Scenarios")
        legend_failed.move(370,395)

        
        legend_success = QLabel(self.centralwidget)
        legend_success.setText("Passed Scenarios")
        legend_success.move(520,395)

        legend_others =QLabel(self.centralwidget)
        legend_others.setText("Others")
        legend_others.move(680,395)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

class ChartDialog(WidgetGallery):
    def __init__(self,widgetgallery, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_MainWindow()  
        self.ui.setupUi(self)
        self.Source_Success_dict=widgetgallery.source_success_dict
        self.Source_Failed_dict=widgetgallery.source_failed_dict

        self.success=widgetgallery.success
        self.same_success=widgetgallery.same_success
        self.failed=widgetgallery.failed
        self.same_failed=widgetgallery.same_failed
        self.source_others=widgetgallery.source_others
        self.target_others=widgetgallery.target_others
    
    #ChartDrawer
    def paintEvent(self, event):
        screenwidth=700
        factor=1600
        deltadistance = 270
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(3)
        #Old Regression Run
        if len(self.Source_Failed_dict) != 0:
            pen.setColor(QColor(Qt.darkRed))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.darkRed))
            painter.drawRoundedRect(40+deltadistance, 40, (len(self.Source_Failed_dict))/screenwidth * factor, 100, 10, 10)
            pen.setColor(QColor(Qt.white))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.white))
            painter.drawText(QRect(40+deltadistance, 40, (len(self.Source_Failed_dict))/screenwidth * factor, 100),Qt.AlignCenter,str(len(self.Source_Failed_dict)))
            
           
        if len(self.Source_Success_dict)!=0:
            pen.setColor(QColor(Qt.darkGreen))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.darkGreen))
            painter.drawRoundedRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30, 40, (len(self.Source_Success_dict)/screenwidth)*factor, 100, 10, 10)
            pen.setColor(QColor(Qt.white))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.white))
            painter.drawText(QRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30, 40, (len(self.Source_Success_dict)/screenwidth)*factor, 100),Qt.AlignCenter,str(len(self.Source_Success_dict)))
        
        if self.source_others !=0:
            pen.setColor(QColor(Qt.darkBlue))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.darkBlue))
            painter.drawRoundedRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30+(len(self.Source_Success_dict)/screenwidth)*factor+30,40,(self.source_others/screenwidth)*factor,100,10,10)
            pen.setColor(QColor(Qt.white))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.white))
            painter.drawText(QRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30+(len(self.Source_Success_dict)/screenwidth)*factor+30,40,(self.source_others/screenwidth)*factor,100),Qt.AlignCenter,str(self.source_others))

        #New Regression Run
        if self.success!=0:
            pen.setColor(QColor(Qt.darkGreen))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.darkGreen))
            painter.drawRoundedRect(40+deltadistance, 180, (self.success/screenwidth) * factor, 100, 10, 10)
            pen.setColor(QColor(Qt.white))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.white))
            painter.drawText(QRect(40+deltadistance, 180, (self.success/screenwidth) * factor, 100),Qt.AlignCenter,str(self.success))
        distance1=40+deltadistance+((self.success/screenwidth) * factor)+10
        if self.same_failed!=0:
            pen.setColor(QColor(Qt.darkRed))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.darkRed))
            painter.drawRoundedRect(distance1, 180, (self.same_failed/screenwidth) * factor, 100, 10, 10)
            pen.setColor(QColor(Qt.white))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.white))
            painter.drawText(QRect(distance1, 180, (self.same_failed/screenwidth) * factor, 100),Qt.AlignCenter,str(self.same_failed))
        distance2= (abs(len(self.Source_Success_dict)-len(self.Source_Failed_dict))/2)+deltadistance
        if self.same_success!=0:
            pen.setColor(QColor(Qt.darkGreen))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.darkGreen))
            painter.drawRoundedRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30, 180, (self.same_success/screenwidth) * factor, 100, 10, 10)
            pen.setColor(QColor(Qt.white))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.white))
            painter.drawText(QRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30, 180, (self.same_success/screenwidth) * factor, 100),Qt.AlignCenter,str(self.same_success))
        distance3 =  distance2 + ((self.same_success/screenwidth) * factor)+20
        
        if self.failed!=0:
            pen.setColor(QColor(Qt.darkRed))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.darkRed))
            painter.drawRoundedRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30+(self.same_success/screenwidth) * factor+10, 180, (self.failed/screenwidth) * factor, 100, 10, 10)
            pen.setColor(QColor(Qt.white))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.white))
            painter.drawText(QRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30+(self.same_success/screenwidth) * factor+10, 180, (self.failed/screenwidth) * factor, 100),Qt.AlignCenter,str(self.failed))
        
        if self.target_others!=0:
            pen.setColor(QColor(Qt.darkBlue))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.darkBlue))
            painter.drawRoundedRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30+(self.same_success/screenwidth) * factor+10+(self.failed/screenwidth) * factor+30,180,(self.target_others/screenwidth)*factor,100,10,10)
            pen.setColor(QColor(Qt.white))
            painter.setPen(pen)
            painter.setBrush(QColor(Qt.darkBlue))
            painter.drawText(QRect(40+deltadistance+(len(self.Source_Failed_dict))/screenwidth * factor+30+(self.same_success/screenwidth) * factor+10+(self.failed/screenwidth) * factor+30,180,(self.target_others/screenwidth)*factor,100),Qt.AlignCenter,str(self.target_others))

        pen.setColor(QColor(Qt.darkRed))
        painter.setPen(pen)
        painter.setBrush(QColor(Qt.darkRed))
        painter.drawRect(350,400,10,10)

        pen.setColor(QColor(Qt.darkGreen))
        painter.setPen(pen)
        painter.setBrush(QColor(Qt.darkGreen))
        painter.drawRect(500,400,10,10)

        pen.setColor(QColor(Qt.darkBlue))
        painter.setPen(pen)
        painter.setBrush(QColor(Qt.darkBlue))
        painter.drawRect(660,400,10,10)

        painter.end()
        

if __name__ == '__main__':
    appctxt = ApplicationContext()
    gallery = WidgetGallery()
    gallery.setMinimumSize(500,500)
    gallery.setMaximumSize(500,500)
    gallery.show()
    sys.exit(appctxt.app.exec_())

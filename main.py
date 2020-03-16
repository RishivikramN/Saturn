from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog)
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import pyqtSlot
import pandas as pd
import csv
import sys

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

        QApplication.setPalette(self.dark_palette)
        QApplication.setStyle("Fusion")
       
        self.MainScreenLayout()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.sourcegroupbox, 0, 1)
        mainLayout.addWidget(self.targetgroupbox, 1, 1)        
        mainLayout.addWidget(self.exportresultbutton, 2, 1)
        mainLayout.setColumnStretch(1, 1)
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
        
        self.exportresultbutton = QPushButton("Export Result")
        self.exportresultbutton.clicked.connect(self.CSVDataPreprocessor)

        self.sourcegroupbox.setLayout(sourcelayout)
        self.targetgroupbox.setLayout(targetlayout)

    def SourceFileOpener(self):
        self.sourcefilename,_ = QFileDialog.getOpenFileName(self,"Source File","","CSV Files (*.csv)")
        self.sourcetextbox.setText(self.sourcefilename)

    def TargetFileOpener(self):
        self.targetfilename,_ = QFileDialog.getOpenFileName(self,"Target File","","CSV Files (*.csv)")
        self.targettextbox.setText(self.targetfilename)

    def ExportResultsInCSV(self):
        exportfilename,_ = QFileDialog.getSaveFileName(self,"Save Result File","","CSV Files (*.csv)")
        with open(exportfilename, 'w', newline='') as output_file:
            fieldnames=['ScenarioName','ScenarioRunStatus']
            writer = csv.DictWriter(output_file,fieldnames=fieldnames)
            writer.writeheader()
            
            for item in self.modified:
                writer.writerow({'ScenarioName':item,'ScenarioRunStatus':self.target_df_dict[item]})

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
        #Source Data preprocessing
        source_df = pd.read_csv(self.sourcefilename, delimiter='\t')
        source_df=source_df[['ScenarioName','ScenarioRunStatus']]
        source_transpose_df = source_df.set_index('ScenarioName').T
        self.source_df_dict= source_transpose_df.to_dict('list')
        #Target Data preprocessing
        target_df = pd.read_csv(self.targetfilename, delimiter='\t')
        target_df=target_df[['ScenarioName','ScenarioRunStatus']]
        target_transpose_df = target_df.set_index('ScenarioName').T
        self.target_df_dict= target_transpose_df.to_dict('list')
        self.added, self.removed, self.modified, self.same = self.CSVComparer()
        self.ExportResultsInCSV()

if __name__ == '__main__':
    appctxt = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.setMinimumSize(500,500)
    gallery.setMaximumSize(500,500)
    gallery.setWindowTitle("Saturn v0.0.1")
    gallery.setWindowIcon(QIcon("icon.ico"))
    gallery.show()
    sys.exit(appctxt.exec_())
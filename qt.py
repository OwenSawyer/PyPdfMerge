from PyQt5.QtCore import (QDir, QIODevice, QFile, QFileInfo, Qt, QTextStream,
        QUrl)
from PyQt5.QtGui import QDesktopServices, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QComboBox,
                             QDialog, QFileDialog, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
                             QProgressDialog, QPushButton, QSizePolicy, QTableWidget,
                             QTableWidgetItem, QTableView, QVBoxLayout)

from PyPDF2 import PdfFileMerger

from functools import partial

class File:
    def __init__(self, name, size):
        self.name = name
        self.size = size

class PdfMerger:
    def __init__(self):
        pass

    @staticmethod
    def merge(output_path, input_paths):
        pdf_merger = PdfFileMerger(strict=False)

        for path in input_paths:
            pdf_merger.append(path)

        with open(output_path, 'wb') as fileobj:
            pdf_merger.write(fileobj)

class Window(QDialog):

    DOWN    = 1
    UP      = -1


    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.pdf_merger = PdfMerger()

        browseButton = self.createButton("&Browse...", self.browse)
        findButton = self.createButton("&Generate", self.generate)

        self.fileComboBox = self.createComboBox("merged.pdf")
        self.directoryComboBox = self.createComboBox(QDir.currentPath())

        fileLabel = QLabel("Output file name:")
        directoryLabel = QLabel("Browse:")
        self.filesFoundLabel = QLabel()

        self.createFilesTable()

        generateLayout = QHBoxLayout()
        generateLayout.addStretch()
        generateLayout.addWidget(findButton)

        mainLayout = QGridLayout()
        mainLayout.addWidget(fileLabel, 0, 0)
        mainLayout.addWidget(self.fileComboBox, 0, 1, 1, 2)


        mainLayout.addWidget(directoryLabel, 1, 0)
        mainLayout.addWidget(self.directoryComboBox, 1, 1)
        mainLayout.addWidget(browseButton, 1, 2)

        self.upBtn = QPushButton('Up', self)
        self.downBtn = QPushButton('Down', self)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.upBtn)
        self.buttonLayout.addWidget(self.downBtn)
        mainLayout.addLayout(self.buttonLayout, 2, 0)

        mainLayout.addWidget(self.filesTable, 3, 0, 1, 3)
        mainLayout.addWidget(self.filesFoundLabel, 4, 0)
        mainLayout.addLayout(generateLayout, 5, 0, 1, 3)
        self.setLayout(mainLayout)

        self.setWindowTitle("Find Files")
        self.resize(700, 300)

    def browse(self):
        filter = "TXT (*.txt);;PDF (*.pdf)"
        self.files = QFileDialog.getOpenFileNames(self, caption="Select Files", directory = QDir.currentPath())[0]
        print(self.files) # (['E:/Scan_0011.pdf', 'E:/Scan_0013.pdf', 'E:/Scan_0014.pdf', 'E:/Scan_0016.pdf'], 'All Files (*)')

        self.find(self.files)

    @staticmethod
    def updateComboBox(comboBox):
        if comboBox.findText(comboBox.currentText()) == -1:
            comboBox.addItem(comboBox.currentText())

    def find(self, files):

        #self.filesTable.setRowCount(0)

        path = self.directoryComboBox.currentText()
        self.updateComboBox(self.directoryComboBox)
        self.currentDir = QDir(path)

        self.showFiles(files)

    def showFiles(self, files):
        for fn in files:
            print(fn)
            file = QFile(self.currentDir.absoluteFilePath(fn))
            size = QFileInfo(file).size()

            fileNameItem = QStandardItem(fn)
            fileNameItem.setFlags(fileNameItem.flags() ^ Qt.ItemIsEditable)
            sizeItem = QStandardItem("%d KB" % (int((size + 1023) / 1024)))
            sizeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            sizeItem.setFlags(sizeItem.flags() ^ Qt.ItemIsEditable)

            column1 = fileNameItem
            column2 = sizeItem



            self.model.appendRow([column1, column2])
            # row = self.filesTable.rowCount()
            # self.filesTable.insertRow(row)
            # self.filesTable.setItem(row, 0, fileNameItem)
            # self.filesTable.setItem(row, 1, sizeItem)

        self.filesFoundLabel.setText("%d file(s) found (Double click on a file to open it)" % len(files))
        #self.table.model().layoutChanged.emit()

    def createButton(self, text, member):
        button = QPushButton(text)
        button.clicked.connect(member)
        return button

    def createComboBox(self, text=""):
        comboBox = QComboBox()
        comboBox.setEditable(True)
        comboBox.addItem(text)
        comboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return comboBox

    def createFilesTable(self):
        self.filesTable = QTableView(self) #0,2
        self.filesTable.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'Size'])
        self.filesTable.setModel(self.model)

        #self.filesTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        #self.filesTable.verticalHeader().hide()
        #self.filesTable.setShowGrid(False)

        #self.filesTable.cellActivated.connect(self.openFileOfItem)

        # self.table = QTableView(self)
        # self.table.setSelectionBehavior(self.table.SelectRows)
        #
        # self.model = QStandardItemModel(20, 6, self)
        # self.table.setModel(self.model)


    def openFileOfItem(self, row, column):
        item = self.filesTable.item(row, 0)

        QDesktopServices.openUrl(QUrl(self.currentDir.absoluteFilePath(item.text())))

    def moveItem(self, row, direction):
        currentRow = self.filesTable.listWidget.currentRow()
        currentItem = self.filesTable.listWidget.takeItem(currentRow)
        if currentRow == 0 or currentRow == len(self.ventana.listWidget):
            pass
        else:
            self.filesTable.listWidget.insertItem(currentRow + direction, currentItem)

    def moveCurrentRow(self, direction=DOWN):
        if direction not in (self.DOWN, self.UP):
            return

        model = self.model
        selModel = self.table.selectionModel()
        selected = selModel.selectedRows()
        if not selected:
            return

        items = []
        indexes = sorted(selected, key=lambda x: x.row(), reverse=(direction==self.DOWN))

        for idx in indexes:
            items.append(model.itemFromIndex(idx))
            rowNum = idx.row()
            newRow = rowNum+direction
            if not (0 <= newRow < model.rowCount()):
                continue

            rowItems = model.takeRow(rowNum)
            model.insertRow(newRow, rowItems)

        selModel.clear()
        for item in items:
            selModel.select(item.index(), selModel.Select|selModel.Rows)

    def generate(self):
        self.pdf_merger.merge(self.fileComboBox.currentText(), self.files)
        # open alert box ? or onscreen prompt?

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()

    sys.exit(app.exec_())

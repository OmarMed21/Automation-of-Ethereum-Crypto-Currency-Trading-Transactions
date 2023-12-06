import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QBrush, QColor, QLinearGradient
from PyQt5.QtCore import Qt
from matplotlib import pyplot
import pandas as pd
from utils import transactions, send_data_to_google_sheets
import matplotlib.pyplot as plt
from matplotlib import cm

## call the function to assign the data to variable Transactions_data
TRANSACTIONS_DATA = transactions()

class DataFrameViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Etherscan Crypto Trading Application')
        self.setGeometry(100, 100, 800, 600)

        # Load Data
        self.df = TRANSACTIONS_DATA

        # Set the window icon
        self.setWindowIcon(QIcon('Logo.png'))

        self.layout = QVBoxLayout()

        # Create a QPushButton to load a DataFrame
        self.load_button = QPushButton('View Data', self)
        self.load_button.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_button)

        # Create a QPushButton to export the DataFrame to Google Sheets
        self.export_button = QPushButton('Export to Google Sheets', self)
        self.export_button.clicked.connect(self.export_to_google_sheets)
        self.layout.addWidget(self.export_button)


        # Create QTableWidget to display the DataFrame
        self.table_widget = QTableWidget(self)
        self.layout.addWidget(self.table_widget)

        # Create QLabel to display export status
        self.export_status_label = QLabel('', self)
        self.layout.addWidget(self.export_status_label)

        self.setLayout(self.layout)

    def load_data(self):
        # For simplicity, a sample DataFrame is created here. You can modify this part to load your own data.
        # Columns to be styled with gradient 
        self.gradient_columns = ['ETH', 'NOK']

        # Clear the existing table
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)

        # Set the number of rows and columns
        self.table_widget.setRowCount(self.df.shape[0])
        self.table_widget.setColumnCount(self.df.shape[1])

        # Set the column headers
        self.table_widget.setHorizontalHeaderLabels(self.df.columns)

        # Populate the table with DataFrame values
        for i in range(self.df.shape[0]):
            for j in range(self.df.shape[1]):
                value = str(self.df.iat[i, j])
                item = QTableWidgetItem(value)

                # Check if the current column is in the list of columns where you want the gradient
                if self.df.columns[j] in self.gradient_columns:
                    gradient_value = (self.df.iat[i, j] - self.df[self.df.columns[j]].min()) / (self.df[self.df.columns[j]].max() - self.df[self.df.columns[j]].min())
                    gradient_color = self.get_gradient_color(gradient_value)
                    item.setBackground(QBrush(gradient_color))
                    item.setForeground(QBrush(QColor('white')))

                self.table_widget.setItem(i, j, item)

        # Resize columns to content
        self.table_widget.resizeColumnsToContents()

    def get_gradient_color(self, value):
        # Choose a spectral colormap from matplotlib
        colormap = cm.get_cmap('Spectral')

        # Create a gradient color based on the value
        color = QColor.fromRgbF(*colormap(value)[:3])

        return color

    def export_to_google_sheets(self):
        try:
            send_data_to_google_sheets(TRANSACTIONS_DATA)
            self.export_status_label.setText('Export successfully!')
        except Exception as e:
            print(f"Export to Google Sheets failed: {e}")
            self.export_status_label.setText('Export failed')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataFrameViewer()
    window.show()
    sys.exit(app.exec_())

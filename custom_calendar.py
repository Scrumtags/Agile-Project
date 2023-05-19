import datetime
from db_controller import Database_Controller
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import timedelta


class DayWidget(QWidget):
    """

    Widget for dates in custom_calendar
    
    Limited to 5 listings
    
    -------------------------
    | MONTH DATE   CATEGORY |
    |      [ LISTING ]      |
    |      [ LISTING ]      |
    |      [ LISTING ]      |
    |      [ LISTING ]      |
    |      [ LISTING ]      |
    -------------------------

    """
    button_clicked = pyqtSignal(object)
    background_clicked = pyqtSignal(object)

    def __init__(self, data, parent=None):
        super().__init__()

        # Set Class Properties
        if data is None:
            self.data = None
        else:
            self.data = data
            
        self.current_date = self.data['current_date']
        self.event_id = int
        self.count = 0
        
        # Set Widget Layout
        frame = QFrame()
        self.layout_main = QVBoxLayout(frame)
        self.setLayout(self.layout_main)
        self.layout_header = QHBoxLayout()
        self.layout_listing = QVBoxLayout()
        self.layout_main.setStretchFactor(self.layout_header, 20)
        self.layout_main.addLayout(self.layout_header)
        self.layout_main.setStretchFactor(self.layout_listing, 80)
        self.layout_main.addLayout(self.layout_listing)
        self.layout_header.setAlignment(Qt.AlignTop)
        self.layout_main.setAlignment(Qt.AlignTop)
        self.layout_main.setSpacing(0)
        self.layout_listing.setSpacing(0)
        self.layout_main.setContentsMargins(4, 4, 4, 4)
        self.layout_listing.setAlignment(Qt.AlignTop)  
        # layout_header.setContentsMargins(10, 0, 10, 0)
        self.setAutoFillBackground(True)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        # Set the background color to white if current_date.month == data['date'].month
        if today == self.data['date'].strftime('%Y-%m-%d'):
            palette = self.palette()
            palette.setColor(QPalette.Background, QColor(179, 245, 196))
            self.setPalette(palette)
        elif self.current_date.month == self.data['date'].month:
            palette = self.palette()
            palette.setColor(QPalette.Background, Qt.white)
            self.setPalette(palette)
        else:
            palette = self.palette()
            palette.setColor(QPalette.Background, QColor(224, 224, 224))
            self.setPalette(palette)

        # Day label
        if self.data['date'].day == 1:
            self.labelDay = QLabel(data['date'].strftime("%B %d"))
        else:
            self.labelDay = QLabel(data['date'].strftime("%d"))
        self.layout_header.addWidget(self.labelDay)
        
        # Event / Schedule creation (limit of 5 listings per date)
        self.populate_listings()
        
        # Category Label
        if self.count != 0:
            self.categoryLabel = QLabel(str(self.count))
        else:
            self.categoryLabel = QLabel("")
        # self.categoryLabel.setStyleSheet(" font-size: 8pt; color: #fcbfbb; ")
        self.categoryLabel.setStyleSheet(" color: #fcbfbb; ")
        self.categoryLabel.setAlignment(Qt.AlignRight)
        self.layout_header.addWidget(self.categoryLabel)


    def populate_listings(self):
        i = 0
        for item in self.data['data']:
            if i < 5:
                self.event_id = item[0]
                listing = QPushButton(item[1])
                listing.setFont(QFont('Arial', 8))
                if item[5] == 0:
                    listing.setStyleSheet(" background-color: #fcbfbb; ")
                    self.count += 1
                self.layout_listing.addWidget(listing)
                listing.clicked.connect(lambda checked, event_id=self.event_id: self.button_clicked.emit(event_id))
                i += 1
            
            
    # def get_count(self):
    #     count = 0
    #     for event in self.data['data']:
    #         count += 1
    #     return count

    def background_clicked_event(self):
        """
        When background of widget is clicked connect to mainwidget, view_daily function
        - sends to day view and updates selected_date
        """
        date = QDate(self.data['date'].year, self.data['date'].month, self.data['date'].day)
        self.background_clicked.emit(date)

    def mousePressEvent(self, event):
        """
        When background of widget is clicked connect to mainwidget, view_daily function
        - sends to day view and updates selected_date
        Args:
            event (_type_): _description_
        """
        if event.button() == Qt.LeftButton:
            self.background_clicked_event()


class CustomCalendarWidget(QWidget):
    button_clicked = pyqtSignal(object)
    background_clicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__()
        
        self.current_date = datetime.datetime.now()    
        self.db_connection = Database_Controller()
        
        frame = QFrame()
        self.main_layout = QVBoxLayout(frame)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.main_layout)
        self.layoutUpper = QHBoxLayout()
        self.main_layout.setStretchFactor(self.layoutUpper, 20)
        self.layoutMiddle = QHBoxLayout()
        self.main_layout.setStretchFactor(self.layoutMiddle, 20)
        self.layoutUpper.setContentsMargins(0, 0, 0, 10)
        self.buttonNextMonth = QPushButton("Next")
        self.buttonPreviousMonth = QPushButton("Prev")
        self.labelMonth = QLabel(self.current_date.strftime("%B %Y"))

        self.buttonNextMonth.clicked.connect(self.next_month)
        self.buttonPreviousMonth.clicked.connect(self.previous_month)
        self.layoutUpper.addWidget(self.buttonPreviousMonth)
        self.layoutUpper.addWidget(self.labelMonth)
        self.layoutUpper.addWidget(self.buttonNextMonth)

        self.main_layout.addLayout(self.layoutUpper)
        days = ["Sunday", "Monday", "Tuesday",
                "Wednesday", "Thursday", "Friday", "Saturday"]
        for day in days:
            self.layoutMiddle.addWidget(QLabel(day))

        self.main_layout.addLayout(self.layoutMiddle)
        self.labelMonth.setAlignment(Qt.AlignCenter)

        self.days_layout = QGridLayout()
        self.main_layout.addLayout(self.days_layout)
        self.main_layout.setStretchFactor(self.days_layout, 60)

        self.set_defaults()

    def set_defaults(self):
        self.clear_days()
        self.get_month()
        self.first = self.calculate_first()
        self.day_of_week = self.calculate_day()
        self.start_date = self.calculate_start()
        self.populate_days()

    def next_month(self):
        self.current_date = self.current_date + timedelta(days=30)
        self.set_defaults()

    def previous_month(self):
        self.current_date = self.current_date - timedelta(days=30)
        self.set_defaults()

    def populate_days(self):
        date = self.start_date
        for row in range(5):
            for column in range(7):
                listings = self.db_connection.get_date_listing(date)
                data = {
                    "current_date": self.current_date,
                    "date": date,
                    "data": listings
                }
                dayWidget = DayWidget(data, parent=self)
                self.days_layout.addWidget(dayWidget, row, column)
                date = date + timedelta(days=1)
                dayWidget.button_clicked.connect(self.button_emit)
                dayWidget.background_clicked.connect(self.background_emit)

    def background_emit(self, date):
        self.background_clicked.emit(date)

    def button_emit(self, listing):
        self.button_clicked.emit(listing)
    
    def clear_days(self):
        for i in range(self.days_layout.count()):
            item = self.days_layout.itemAt(i)
            item.widget().close()

    def get_month(self):
        self.labelMonth.setText(self.current_date.strftime("%B %Y"))

    def calculate_first(self):
        return self.current_date.replace(day=1)

    def calculate_day(self):
        return self.current_date.weekday()

    def calculate_start(self):
        return self.first - timedelta(days=self.first.weekday() + 1)

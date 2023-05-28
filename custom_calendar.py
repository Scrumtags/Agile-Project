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

    # signals to emit to parent widget
    button_clicked = pyqtSignal(object)
    background_clicked = pyqtSignal(object)

    def __init__(self, data, parent=None):
        """

        Args:
            data int: event_id used to populate 5 listings onto day widget
        """
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
        self.layout_listing.setSpacing(1)
        self.layout_main.setContentsMargins(4, 4, 4, 4)
        self.layout_listing.setAlignment(Qt.AlignTop)
        self.setAutoFillBackground(True)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        # Set the background color to white if current_date.month == data['date'].month
        if today == self.data['date'].strftime('%Y-%m-%d'):
            # set color green if today date == date for events
            palette = self.palette()
            palette.setColor(QPalette.Background, QColor(179, 245, 196))
            self.setPalette(palette)
        elif self.current_date.month == self.data['date'].month:
            # set white if day is in month
            palette = self.palette()
            palette.setColor(QPalette.Background, Qt.white)
            self.setPalette(palette)
        else:
            # set gray if data date not in date
            palette = self.palette()
            palette.setColor(QPalette.Background, QColor(224, 224, 224))
            self.setPalette(palette)

        # if data[date] equals 1 then add month-day else just day
        if self.data['date'].day == 1:
            self.labelDay = QLabel(data['date'].strftime("%B %d"))
        else:
            self.labelDay = QLabel(data['date'].strftime("%d"))
        # add widget to layout
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

    # creates 5 listings for that day
    def populate_listings(self):
        i = 0
        for item in self.data['data']:
            if i < 5:
                self.event_id = item[0]
                # set listing structure and properties
                listing = QPushButton()
                listing_layout = QVBoxLayout(listing)
                listing_layout.setContentsMargins(0, 0, 0, 0)
                listing.setLayout(listing_layout)
                listing_title = QLabel(item[1])
                listing_layout.addWidget(listing_title)
                listing_title.setStyleSheet("font-size: 12px;")
                listing_title.adjustSize()
                listing_title.setAlignment(Qt.AlignCenter)
                # if completion status is incomplete set different styling
                if item[5] == 0:
                    listing.setStyleSheet("""
                        QPushButton {
                            background-color: #fcbfbb;
                            border: 1px solid #7aa7c7;
                            color: #39739d;
                            font-size: 15px;
                            font-weight: 400;
                            outline: none;
                        }
                    """)
                    self.count += 1
                self.layout_listing.addWidget(listing)
                # assign callback to listings with lambda to not explicitly define each event 
                listing.clicked.connect(lambda checked, event_id=self.event_id: self.button_clicked.emit(event_id))
                i += 1

    def background_clicked_event(self):
        """
        inherited function

        When background of widget is clicked connect to mainwidget, view_daily function
        - sends to day view and updates selected_date
        """
        date = QDate(self.data['date'].year, self.data['date'].month, self.data['date'].day)
        self.background_clicked.emit(date)

    def mousePressEvent(self, event):
        """
        inherited function

        When background of widget is clicked connect to mainwidget, view_daily function
        - sends to day view and updates selected_date
        """
        if event.button() == Qt.LeftButton:
            self.background_clicked_event()


class CustomCalendarWidget(QWidget):
    """
        custom calendar widget created for studybuddy
    """

    # signals to emit to parent widget
    button_clicked = pyqtSignal(object)
    background_clicked = pyqtSignal(object)
    previous_month_clicked = pyqtSignal(object)
    next_month_clicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__()

        self.current_date = datetime.datetime.now()
        # database connection to populate days on calendar
        self.db_connection = Database_Controller()

        # define widget structure
        frame = QFrame()
        self.main_layout = QVBoxLayout(frame)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
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
        # set the days of the week labels
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
        # delete all daywidgets
        self.clear_days()
        # set month label
        self.get_month()
        # calculate first day of month
        self.first = self.calculate_first()
        # calculate day of week
        self.day_of_week = self.calculate_day()
        # calculate start date for the calendar
        self.start_date = self.calculate_start()
        # populate daywidgets
        self.populate_days()

    # button to add 1 month
    def next_month(self):
        self.next_month_clicked.emit(self.current_date)
        self.set_defaults()

    # function to go back 1 month
    def previous_month(self):
        self.previous_month_clicked.emit(self.current_date)
        self.set_defaults()

    # creates all the daywidgets for calendar
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

    # signal to connect background to view_daily in studybuddy
    def background_emit(self, date):
        self.background_clicked.emit(date)

    # signal to connect background to edit_note in studybuddy
    def button_emit(self, listing):
        self.button_clicked.emit(listing)

    # destroy all days in calendar to repopulate
    def clear_days(self):
        for i in range(self.days_layout.count()):
            item = self.days_layout.itemAt(i)
            item.widget().close()

    # functions just for calculations to store as properties
    def get_month(self):
        self.labelMonth.setText(self.current_date.strftime("%B %Y"))

    # calculate first day of week based on stored date
    def calculate_first(self):
        return self.current_date.replace(day=1)

    # function to get what day of the week stored date is
    def calculate_day(self):
        return self.current_date.weekday()
    
    # calculate first box date for the calendar
    def calculate_start(self):
        return self.first - timedelta(days=self.first.weekday() + 1)

    # date passed by parent widget to update calendar widget
    def set_current_date(self, date):
        """
        Summary:
            updates calendar date to sync calendar widget with parent date
        Args:
            date: datetime.datetime obj
        """
        self.current_date = date
        self.set_defaults()
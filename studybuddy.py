import sys
import time
import datetime
from time import mktime
from PyQt5.QtWidgets import *
from datetime import datetime, timedelta
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from sqlite3 import Error
from db_controller import Database_Controller
from custom_calendar import *
import resources

"""""
SQLite database

# events 
1 - event_id                INTEGER
2 - title                   TEXT
3 - description             TEXT
4 - start_date              DATE
5 - end_date                DATE
6 - completion_status       BOOLEAN

# tags
1 - tag_id                  INTEGER
2 - tag_name                TEXT

# schedules
1 - schedule_id             INTEGER
2 - title                   TEXT
3 - description             TEXT
4 - start_date              DATE
5 - end_date                DATE
6 - day_of_week             TEXT

# event_tags
1 - event_id                INTEGER
2 - tag_id                  INTEGER

# schedule_tags
1 - schedule_id             INTEGER
2 - tag_id                  INTEGER

"""""


class Main(QMainWindow):
    def __init__(self):
        # Inherit all methods and properties from QMainWindow
        super(Main, self).__init__()
        # Load UI file created in Qt Designer
        loadUi("new_ui.ui", self)
        # Load Resources
        self.connectDB = Database_Controller()
        self.validate_tags_list()
        self.database_tags = self.connectDB.get_all_tags()

        """
        Indexes

        0 - Month View
        1 - Modify Event View
        2 - Daily View
        3 - Weekly View
        4 - Search View
        5 - Schedule View
        6 - Modify Schedule View
        7 - Settings View

        """

        self.calendar_widget = CustomCalendarWidget()
        self.calendar_widget.button_clicked.connect(self.edit_event)
        self.calendar_widget.background_clicked.connect(self.view_day)
        self.layoutMonthlyCalendar.addWidget(self.calendar_widget)

        # Navigation Menu

        ## Calendar
        self.buttonNavigationCalendar.clicked.connect(self.view_calendar)
        ### Calendar Sub-buttons
        self.buttonNavigationCalendarDay.clicked.connect(self.view_day)
        self.buttonNavigationCalendarMonth.clicked.connect(self.view_month)
        self.buttonNavigationCalendarWeek.clicked.connect(self.view_week)
        ## Search
        self.buttonNavigationSearch.clicked.connect(self.view_search)
        ## Schedule
        self.buttonNavigationScheduleView.clicked.connect(self.view_schedule)
        # Settings
        self.buttonNavigationSettings.clicked.connect(self.view_settings)

        ### Schedule View Buttons
        self.buttonScheduleViewAdd.clicked.connect(self.create_schedule)
        self.buttonScheduleSubmit.clicked.connect(self.schedule_manager)
        self.scheduleDelete.clicked.connect(self.delete_schedule)
        self.scheduleUpdate.clicked.connect(self.edit_schedule)
        ### Schedule Edit/Add Buttons
        self.buttonScheduleCancel.clicked.connect(self.view_schedule)

        # Daily View
        self.buttonViewDailyAdd.clicked.connect(self.create_event)
        self.buttonViewDailyEdit.clicked.connect(self.edit_event)
        self.buttonViewDailyDelete.clicked.connect(self.delete_event)
        self.tableViewDaily.doubleClicked.connect(self.edit_event)
        self.buttonViewDailyBack.clicked.connect(self.view_month)
        self.buttonNextDate.clicked.connect(self.next_day)
        self.buttonPreviousDate.clicked.connect(self.previous_day)

        # Create / Edit Event View
        self.buttonModifyEventSubmit.clicked.connect(self.event_manager)
        self.buttonModifyEventCancel.clicked.connect(self.view_day)
        self.buttonModifyEventAddTag.clicked.connect(self.add_event_tag)
        self.buttonModifyEventDeleteTag.clicked.connect(self.delete_event_tag)

        # Weekly View
        self.buttonViewWeeklyBack.clicked.connect(self.view_month)

        # Settings
        self.buttonSettingsHolidayImport.clicked.connect(self.get_holidays)

        # Defaults
        self.__set_defaults()

    # Application Functions
    def __set_defaults(self):
        # hide widgets
        self.selected_date = QDate.currentDate()
        headers = [self.tableSearch, self.tableWidget, self.tableViewDaily, self.tableviewSunday, self.tableviewMonday, self.tableviewTuesday, self.tableviewWednesday, self.tableviewThursday, self.tableviewFriday, self.tableviewSaturday]
        for table in headers:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stackedWidgetViews.setCurrentIndex(0)
        self.buttonNavigationCalendar.setDisabled(True)
        self.buttonNavigationCalendarMonth.setDisabled(True)
        self.popularize_weekly_list()
        self.tableViewDaily.setColumnHidden(0, True)
        

    # Navigation Buttons


    def validate_tags_list(self):
        #check the tag list on whether they associate with an event
        all_event_tags = self.connectDB.get_all_event_tags()
        all_tags = self.connectDB.get_all_tags()

        for tag in all_tags:
            event_tag_found = False

            for event_tag in all_event_tags:
                print(event_tag[1],"and",tag[0])
                if event_tag[1] == tag[0]:
                    event_tag_found = True
                    break
            print(event_tag_found)
            if event_tag_found is False:
                #delete the tag
                self.connectDB.del_tag(tag[0])
               
        

    def popularize_weekly_list(self):

        self.min_date = self.get_sunday()
        self.data = self.connectDB.query_week(self.min_date)
        self.weekly_data = []
        for item in self.data:
            dic = {
                'event_id': item[0],
                'title': item[1],
                'description': item[2],
                'start_date': item[3],
                'end_date': item[4],
                'completion_status': item[5]
            }
            self.weekly_data.append(dic)
        self.tableViewDaily.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(0, True)

    def view_calendar(self):
        self.toggle_navigation()
        self.buttonNavigationCalendar.setDisabled(True)
        self.buttonNavigationCalendarMonth.setDisabled(True)
        self.stackedWidgetViews.setCurrentIndex(0)
        self.calendar_buttons.show()

    def view_day(self, data=None):
        if data:
            self.selected_date = data
        self.stackedWidgetViews.setCurrentIndex(1)
        self.toggle_calendar_buttons()
        self.buttonNavigationCalendarDay.setDisabled(True)
        self.populate_daily()
        self.labelViewDailyDate.setText(self.selected_date.toString("MMM dd"))

    def view_month(self):
        self.stackedWidgetViews.setCurrentIndex(0)
        self.toggle_calendar_buttons()
        self.buttonNavigationCalendarMonth.setDisabled(True)

    def view_week(self):
        self.stackedWidgetViews.setCurrentIndex(2)
        self.toggle_calendar_buttons()
        self.buttonNavigationCalendarWeek.setDisabled(True)

        if self.selected_date.dayOfWeek() == 7:

            thisWeeksSunday = time.strptime(str(self.selected_date.year()) + ' ' + str(self.selected_date.weekNumber()[0]) + ' 0', '%Y %W %w')
            self.labelMonth.setText("Week " + str(self.selected_date.weekNumber()[0]+1)+" of "+ str(self.selected_date.year()))
        else:
            thisWeeksSunday = time.strptime(str(self.selected_date.year()) + ' ' + str(self.selected_date.weekNumber()[0]-1) + ' 0', '%Y %W %w')
            self.labelMonth.setText("Week " + str(self.selected_date.weekNumber()[0])+" of "+ str(self.selected_date.year()))

        thisWeeksSunday = datetime.datetime.fromtimestamp(mktime(thisWeeksSunday))
        thisWeeksSunday = thisWeeksSunday.strftime('%Y-%m-%d')

        date_1 = datetime.datetime.strptime(thisWeeksSunday, '%Y-%m-%d')

        self.sun = (date_1 + timedelta(days=0)).strftime("%B %d")
        self.mon = (date_1 + timedelta(days=1)).strftime("%B %d")
        self.tue = (date_1 + timedelta(days=2)).strftime("%B %d")
        self.wed = (date_1 + timedelta(days=3)).strftime("%B %d")
        self.thu = (date_1 + timedelta(days=4)).strftime("%B %d")
        self.fri = (date_1 + timedelta(days=5)).strftime("%B %d")
        self.sat = (date_1 + timedelta(days=6)).strftime("%B %d")

        self.labelSunday.setText(self.sun)
        self.labelMonday.setText(self.mon)
        self.labelTuesday.setText(self.tue)
        self.labelWednesday.setText(self.wed)
        self.labelThursday.setText(self.thu)
        self.labelFriday.setText(self.fri)
        self.labelSaturday.setText(self.sat)
        self.popularize_weekly_list()
        self.display_weekly_view()

    def view_search(self):
        self.stackedWidgetViews.setCurrentIndex(4)
        self.toggle_navigation()
        self.radioSearchAll.setChecked(True)
        self.buttonNavigationSearch.setDisabled(True)
        self.date_search()

    def view_schedule(self):
        self.stackedWidgetViews.setCurrentIndex(5)
        self.toggle_navigation()
        self.buttonNavigationScheduleView.setDisabled(True)
        self.populate_schedule()

    def view_settings(self):
        self.stackedWidgetViews.setCurrentIndex(7)
        self.toggle_navigation()
        self.buttonNavigationSettings.setDisabled(True)

    # EVENTS

    def create_event(self):
        self.set_event_defaults()
        for item in self.database_tags:
            self.comboModifyEventTagsAdd.addItem(item[1])
        self.edit_flag = 0
        self.stackedWidgetViews.setCurrentIndex(3)

        cur = self.connectDB.conn.cursor()
        query = 'SELECT * FROM events'

        row_count = 1
        tablerow = 0
        for row in cur.execute(query):
            self.tableViewDaily.setRowCount(row_count)
            self.tableViewDaily.setItem(tablerow, 0, QTableWidgetItem(row[5]))
            self.tableViewDaily.setItem(tablerow, 1, QTableWidgetItem(row[1]))
            self.tableViewDaily.setItem(tablerow, 2, QTableWidgetItem(row[3]))
            self.tableViewDaily.setItem(tablerow, 3, QTableWidgetItem(row[4]))
            tablerow += 1
            row_count += 1

    def edit_event(self, data=None):
        self.edit_flag = 1
        current_tags = []
        self.stackedWidgetViews.setCurrentIndex(3)
        self.set_event_defaults()

        selected_row = self.tableViewDaily.selectedItems()
        if len(selected_row) == 1:
            table = self.tableViewDaily
            row_number = self.tableViewDaily.row(selected_row[0])
            self.event_id = int(table.item(row_number, 0).text())
            print("event_id",self.event_id)
        elif data is not None:
            self.event_id = data
        else:
            return

        tags_ids = self.connectDB.get_event_tags(self.event_id)
        tags = self.connectDB.get_tags(tags_ids)
        column_count = 1
        column_number = 0
        for tag in tags:
            self.tableModifyEventTags.setColumnCount(column_count)
            self.tableModifyEventTags.setItem(
                0, column_number, QTableWidgetItem(tag))
            column_number += 1
            column_count += 1

        for column in range(self.tableModifyEventTags.columnCount()):
            item = self.tableModifyEventTags.item(0, column)
            if item is not None:
                current_tags.append(item)
            
        for item in self.database_tags:
            check_same_tag = False
            for tags in current_tags:
                if item[1] == tags.text():
                    check_same_tag = True
            if check_same_tag is False:
                self.comboModifyEventTagsAdd.addItem(item[1])

       
        cur = self.connectDB.conn.cursor()
        sql = """SELECT * FROM events WHERE event_id = ?"""
        values = (self.event_id, )

        for item in cur.execute(sql, values):
            syear, smonth, sday = item[3].split('-')
            eyear, emonth, eday = item[4].split('-')
            sdateSelected = QDate(int(syear), int(smonth), int(sday))
            edateSelected = QDate(int(eyear), int(emonth), int(eday))
            self.dataModifyEventTitle.setText(item[1])
            self.dataModifyEventDescription.setText(item[2])
            self.dataModifyEventStatus.setValue(item[5])

            self.dataModifyEventEndDate.setMinimumDate(edateSelected)
            self.dataModifyEventStartDate.setDate(sdateSelected)
            self.dataModifyEventEndDate.setDate(edateSelected)
            self.labelModifyEventDate.setText(edateSelected.toString("MMM dd"))
            self.selected_date = edateSelected








    def delete_event(self):
        if len(self.tableViewDaily.selectedItems()) > 0:
            row = self.tableViewDaily.currentRow()
            event_id = self.tableViewDaily.item(row, 0).text()
            try:
                self.connectDB.delete_event(event_id)
                self.tableViewDaily.removeRow(row)
            except Error as e:
                print(e)
                return

    def event_manager(self):
        if self.edit_flag == 0:
            print("edit_flag 0")
            self.connectDB.create_event(self.get_event_data())
        elif self.edit_flag == 1:
            print("edit_flag 1 ")
            self.connectDB.update_event(self.get_event_data())
        self.set_event_defaults()
        self.populate_daily()
        self.calendar_widget.populate_days()
        self.view_day()

    def add_event_tag(self):
        current_tags = []
        for column in range(self.tableModifyEventTags.columnCount()):
            item = self.tableModifyEventTags.item(0, column)
            if item is not None:
                current_tags.append(item)
        tag = self.comboModifyEventTagsAdd.currentText()
        if tag == "":
            return
        for tags in current_tags:
            if tag == tags.text():
                return

        item = QTableWidgetItem(tag)
        self.comboModifyEventTagsAdd.removeItem(
            self.comboModifyEventTagsAdd.findText(tag))
        self.tableModifyEventTags.setColumnCount(
            self.tableModifyEventTags.columnCount() + 1)
        self.tableModifyEventTags.setItem(
            0, self.tableModifyEventTags.columnCount() - 1, item)
        self.comboModifyEventTagsAdd.setCurrentText("")

    def delete_event_tag(self):
        current_tags = []
        for column in range(self.tableModifyEventTags.columnCount()):
            item = self.tableModifyEventTags.item(0, column)
            if item is not None:
                current_tags.append(item)
        if self.tableModifyEventTags.selectedItems():
            selected_item = self.tableModifyEventTags.selectedItems()[0]
            tag = selected_item.text()
            for tags in current_tags:
                if tag == tags:
                    return
            self.tableModifyEventTags.removeColumn(selected_item.column())
            self.comboModifyEventTagsAdd.addItem(tag)
    
    # SCHEDULE
    def create_schedule(self):
        self.edit_flag = 0
        self.dataScheduleTags.clear()
        self.dataScheduleTitle.clear()
        self.dataScheduleDescription.clear()
        self.dataScheduleStartDate.clear()
        self.dataScheduleEndDate.clear()
        self.stackedWidgetViews.setCurrentIndex(6)
        self.dataScheduleStartDate.setMinimumDate(QDate.currentDate())
        self.dataScheduleEndDate.setMinimumDate(QDate.currentDate())
        self.dataScheduleStartDate.setDate(QDate.currentDate())
        self.dataScheduleEndDate.setDate(QDate.currentDate())

    def delete_schedule(self):
        if len(self.tableWidget.selectedItems()) > 0:
            row = self.tableWidget.currentRow()
            self.schedule_id = self.tableWidget.item(row, 0).text()
            try:
                self.connectDB.delete_schedule(self.schedule_id)
            except Error as e:
                print(e)
                return
            self.tableWidget.removeRow(row)

    def edit_schedule(self):
        self.edit_flag = 1
        self.stackedWidgetViews.setCurrentIndex(6)
        if len(self.tableWidget.selectedItems()) > 0:
            row = self.tableWidget.currentRow()
            self.schedule_id = self.tableWidget.item(row, 0).text()
            cur = self.connectDB.conn.cursor()
            sql = """SELECT * FROM schedules WHERE schedule_id = ?"""
            values = (self.schedule_id, )
            row_count = 1
            tablerow = 0
            for row in cur.execute(sql, values):
                self.dataScheduleTitle.setText(row[1])
                self.dataScheduleDescription.setText(row[2])
                year, month, day = row[3].split('-')
                year1, month2, day2 = row[4].split("-")
                self.qdateV = QDate(int(year), int(month), int(day))
                self.qdateV2 = QDate(int(year1), int(month2), int(day2))
                self.dataScheduleStartDate.setDate(self.qdateV)
                self.dataScheduleStartDate.setMinimumDate(self.qdateV)
                self.dataScheduleEndDate.setMinimumDate(self.qdateV2)
                self.dataScheduleEndDate.setDate(self.qdateV2)
                tablerow += 1
                row_count += 1

    def get_schedule_data(self):
        title = self.dataScheduleTitle.text()
        description = self.dataScheduleDescription.toPlainText()
        start_date = self.dataScheduleStartDate.text()
        end_date = self.dataScheduleEndDate.text()
        if self.edit_flag == 0:
            data = {
                "title": title,
                "description": description,
                "start_date": start_date,
                "end_date": end_date}
        elif self.edit_flag == 1:
            data = {
                "title": title,
                "schedule_id": self.schedule_id,
                "description": description,
                "start_date": start_date,
                "end_date": end_date
            }
        return data

    def schedule_manager(self):
        if self.edit_flag == 0:
            self.connectDB.create_schedule(self.get_schedule_data())
        elif self.edit_flag == 1:
            self.connectDB.edit_schedule(self.get_schedule_data())
        self.view_schedule()

    # OTHER

    def convert_qdate(self, qdate):
        return qdate.toPyDate()

    def next_day(self):
        next_day = self.convert_qdate(self.selected_date) + timedelta(days=1)
        self.selected_date = QDate(next_day.year, next_day.month, next_day.day)
        self.populate_daily()

    def previous_day(self):
        prev_day =  self.convert_qdate(self.selected_date) - timedelta(days=1)
        self.selected_date = QDate(prev_day.year, prev_day.month, prev_day.day)
        self.populate_daily()

    def toggle_date_selector(self):
        self.date_pick.setHidden(not self.date_pick.isHidden())

    def toggle_navigation(self):
        buttons = [self.buttonNavigationCalendar, self.buttonNavigationSearch, self.buttonNavigationScheduleView, self.buttonNavigationSettings]
        for button in buttons:
            button.setDisabled(False)
        self.toggle_calendar_buttons()
        self.calendar_buttons.hide()

    def toggle_calendar_buttons(self):
        buttons = [self.buttonNavigationCalendarMonth, self.buttonNavigationCalendarWeek, self.buttonNavigationCalendarDay]
        if not self.buttonNavigationCalendar.isEnabled():
            for button in buttons:
                button.setDisabled(False)

    def format_completion_status(self, data):
        if data == 0:
            return "Incomplete"
        else:
            return "Completed"

    def get_sunday(self):
        if self.selected_date.dayOfWeek() == 7:
            thisWeeksSunday = time.strptime(str(self.selected_date.year(
            )) + ' ' + str(self.selected_date.weekNumber()[0]) + ' 0', '%Y %W %w')
        else:
            thisWeeksSunday = time.strptime(str(self.selected_date.year(
            )) + ' ' + str(self.selected_date.weekNumber()[0]-1) + ' 0', '%Y %W %w')

        thisWeeksSunday = datetime.datetime.fromtimestamp(
            mktime(thisWeeksSunday))
        thisWeeksSunday = thisWeeksSunday.strftime('%Y-%m-%d')
        sunday = datetime.datetime.strptime(thisWeeksSunday, "%Y-%m-%d")

        return sunday

    def set_event_defaults(self):
        self.dataModifyEventTitle.clear()
        self.dataModifyEventDescription.clear()
        self.dataModifyEventStartDate.clear()
        self.dataModifyEventEndDate.clear()
        self.dataModifyEventStatus.setValue(0)
        self.comboModifyEventTagsAdd.clear()
        self.tableModifyEventTags.clear()
        self.tableModifyEventTags.setColumnCount(0)
        self.tableModifyEventTags.setRowCount(1)
        self.comboModifyEventTagsAdd.addItem("")

    def get_event_data(self):
        current_tags = []
        create_new_tags = []
        for column in range(self.tableModifyEventTags.columnCount()):
            item = self.tableModifyEventTags.item(0, column)
            if item is not None:
                current_tags.append(item.text())
        for tag in current_tags:
            checkTag = False
            for tag_database in self.database_tags:
                
                if tag == tag_database[1]:
                    checkTag = True
                    break
            if checkTag is False:
                #create a new tag
                create_new_tags.append(tag)

        new_tag_list = list(set(current_tags)-set(create_new_tags))
        
        
        print("create new tags",create_new_tags)


        #delete all event_tags for current event_id
        self.connectDB.del_event_tags(self.event_id)


        #create tags that doesn't exist in the database
        for tag in create_new_tags:
            self.connectDB.create_tags(tag)
            for id in self.connectDB.get_tag_id(tag):
                new_tag_id = id[0]
                print("new tag id:",new_tag_id)
            self.connectDB.create_event_tags(self.event_id,new_tag_id)
        
        #create event_tags that doesn't exist in the database
        for tag in new_tag_list:
            for id in self.connectDB.get_tag_id(tag):
                new_tag_id = id[0]
            self.connectDB.create_event_tags(self.event_id,new_tag_id)
        self.validate_tags_list()
       

        if self.edit_flag == 0:
            data = {
                "title": self.dataModifyEventTitle.text(),
                # "tags": self.dataModifyEventTags.text(),
                "description": self.dataModifyEventDescription.toPlainText(),
                "start_date": self.dataModifyEventStartDate.text(),
                "end_date": self.dataModifyEventEndDate.text(),
                "completion_status": self.dataModifyEventStatus.value()
            }
        else:
            data = {
                "event_id": self.event_id,
                "title": self.dataModifyEventTitle.text(),
                # "tags": self.dataModifyEventTags.text(),
                "description": self.dataModifyEventDescription.toPlainText(),
                "start_date": self.dataModifyEventStartDate.text(),
                "end_date": self.dataModifyEventEndDate.text(),
                "completion_status": self.dataModifyEventStatus.value()
            }
        return data

    def display_weekly_view(self):

        self.sun_list = []
        self.mon_list = []
        self.tue_list = []
        self.wed_list = []
        self.thu_list = []
        self.fri_list = []
        self.sat_list = []
        self.tableviewSunday.setRowCount(0)
        self.tableviewMonday.setRowCount(0)
        self.tableviewTuesday.setRowCount(0)
        self.tableviewWednesday.setRowCount(0)
        self.tableviewThursday.setRowCount(0)
        self.tableviewFriday.setRowCount(0)
        self.tableviewSaturday.setRowCount(0)
        for task in self.weekly_data:

            end_date_formatted = datetime.datetime.strptime(
                task['end_date'], "%Y-%m-%d").strftime("%B %d")

            if end_date_formatted == self.sun:
                self.sun_list.append(task)
            elif end_date_formatted == self.mon:
                self.mon_list.append(task)
            elif end_date_formatted == self.tue:
                self.tue_list.append(task)
            elif end_date_formatted == self.wed:
                self.wed_list.append(task)
            elif end_date_formatted == self.thu:
                self.thu_list.append(task)
            elif end_date_formatted == self.fri:
                self.fri_list.append(task)
            elif end_date_formatted == self.sat:
                self.sat_list.append(task)
            else:
                continue

        date_list = [self.sun_list, self.mon_list, self.tue_list,
                     self.wed_list, self.thu_list, self.fri_list, self.sat_list]
        table_list = [self.tableviewSunday, self.tableviewMonday, self.tableviewTuesday,
                      self.tableviewWednesday, self.tableviewThursday, self.tableviewFriday, self.tableviewSaturday]

        for i in range(0, 7):
            row_count = 1
            tablerow = 0
            for alist in date_list[i]:
                table_list[i].setRowCount(row_count)
                table_list[i].setItem(
                    tablerow, 0, QTableWidgetItem(alist['title']))
                table_list[i].setItem(
                    tablerow, 1, QTableWidgetItem(self.format_completion_status(alist['completion_status'])))
                tablerow += 1
                row_count += 1

    def date_search(self):
        self.dataSearch.textChanged.connect(self.date_search_helper)
        self.radioSearchAll.toggled.connect(self.date_search_helper)
        self.radioSearchDescription.toggled.connect(self.date_search_helper)
        self.radioSearchEndDate.toggled.connect(self.date_search_helper)
        self.radioSearchStartDate.toggled.connect(self.date_search_helper)
        self.radioSearchStatus.toggled.connect(self.date_search_helper)
        self.radioSearchTitle.toggled.connect(self.date_search_helper)

    def date_search_helper(self):
        self.tableSearch.setRowCount(0)
        check = "*"
        if self.radioSearchAll.isChecked():
            check = "*"
        elif self.radioSearchDescription.isChecked():
            check = "description"
        elif self.radioSearchEndDate.isChecked():
            check = "end_date"
        elif self.radioSearchStartDate.isChecked():
            check = "start_date"
        elif self.radioSearchStatus.isChecked():
            check = "completion_status"
        elif self.radioSearchTitle.isChecked():
            check = "title"
        else:
            check = "*"

        cur = self.connectDB.conn.cursor()
        if len(self.dataSearch.text()) > 0:
            query = self.connectDB.search_data(check, self.dataSearch.text())
            row_count = 1
            tablerow = 0
            for row in cur.execute(query):
                if row is not None:
                    self.tableSearch.setRowCount(row_count)
                    # event_id - hidden
                    self.tableSearch.setItem(
                        tablerow, 0, QTableWidgetItem(row[1]))
                    # title
                    self.tableSearch.setItem(
                        tablerow, 1, QTableWidgetItem(row[2]))
                    # start date
                    self.tableSearch.setItem(
                        tablerow, 2, QTableWidgetItem(row[3]))
                    # completion
                    self.tableSearch.setItem(
                        tablerow, 3, QTableWidgetItem(row[4]))
                    self.tableSearch.setItem(
                        tablerow, 4, QTableWidgetItem(self.format_completion_status(row[5])))
                    tablerow += 1
                    row_count += 1

    def populate_daily(self):
        """
        SQL QUERY DELETE
        """
        self.labelViewDailyDate.setText(self.selected_date.toString("MMM dd"))
        dateSelected = self.selected_date
        self.labelModifyEventDate.setText(dateSelected.toString("MMM dd"))
        self.dataModifyEventStartDate.setMinimumDate(dateSelected)
        self.dataModifyEventEndDate.setMinimumDate(dateSelected)
        self.dataModifyEventStartDate.setDate(dateSelected)
        self.dataModifyEventEndDate.setDate(dateSelected)
        self.tableViewDaily.setRowCount(0)

        # Grab data from database and populate qLineEdit boxes
        cur = self.connectDB.conn.cursor()
        cur2 = self.connectDB.conn.cursor()
        query = """SELECT * FROM events where date(end_date) = ?"""
        params = (dateSelected.toString("yyyy-MM-dd"), )
        row_count = 1
        tablerow = 0
        for row in cur.execute(query, params):
            if row is not None:
                query_tag = """SELECT tags.tag_name FROM event_tags, tags WHERE event_tags.tag_id = tags.tag_id and event_tags.event_id = ?"""
                params_tag = (str(row[0]),)
                tag_list = []
                tag_str = ""
                for tag in cur2.execute(query_tag,params_tag):
                    tag_list.append(tag[0])
                tag_str = ', '.join(tag_list)
                
                self.tableViewDaily.setRowCount(row_count)
                # event_id - hidden
                self.tableViewDaily.setItem(
                    tablerow, 0, QTableWidgetItem(str(row[0])))
                # title
                self.tableViewDaily.setItem(
                    tablerow, 1, QTableWidgetItem(row[1]))
                self.tableViewDaily.setItem(
                    tablerow, 2, QTableWidgetItem(tag_str))
                # start date
                self.tableViewDaily.setItem(
                    tablerow, 3, QTableWidgetItem(row[4]))
                # completion
                self.tableViewDaily.setItem(
                    tablerow, 4, QTableWidgetItem(self.format_completion_status(row[5])))
                tablerow += 1
                row_count += 1

    def populate_schedule(self):
        cur = self.connectDB.conn.cursor()
        query = """SELECT * FROM schedules """
        # params = (dateSelected.toString("yyyy-MM-dd"), )
        row_count = 1
        tablerow = 0
        for row in cur.execute(query):
            if row is not None:
                self.tableWidget.setRowCount(row_count)
                # event_id - hidden
                self.tableWidget.setItem(
                    tablerow, 0, QTableWidgetItem(str(row[0])))
                # description
                self.tableWidget.setItem(
                    tablerow, 5, QTableWidgetItem(row[2])
                )
                # title
                self.tableWidget.setItem(
                    tablerow, 1, QTableWidgetItem(row[1]))
                # start date
                self.tableWidget.setItem(
                    tablerow, 2, QTableWidgetItem(row[3]))
                # completion
                self.tableWidget.setItem(
                    tablerow, 3, QTableWidgetItem(row[4]))
                self.tableWidget.setItem(
                    tablerow, 4, QTableWidgetItem(row[5])
                )

                tablerow += 1
                row_count += 1

    def get_holidays(self):
        province_id =  self.comboBoxHolidayImport.currentIndex()
        if province_id != 0:
            self.connectDB.get_holidays(province_id)
        self.calendar_widget.populate_days()

class Notification(QDialog):
    def __init__(self):
        super(Notification, self).__init__()
        pass

if __name__ == "__main__":
    """
    Loads UI and initializes studybuddy window
    """
    with open("style.qss", "r") as style_sheet:
        styling = style_sheet.read()
    # Create QApplication Instance
    app = QApplication(sys.argv)
    app.setStyleSheet(styling)
    # Create Main Instance
    studybuddy = Main()
    # Load Main (GUI)
    studybuddy.show()
    # Start QApplication
    app.exec_()

import json
import subprocess
import threading
import time
from datetime import datetime
from hashlib import md5
from json import JSONDecodeError
from random import random

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QAbstractItemView, QTableWidgetItem
from qfluentwidgets import FluentIcon as FIF, TextEdit, IndeterminateProgressBar, InfoBar, InfoBarIcon, InfoBarPosition
from qfluentwidgets import (
    PrimaryPushSettingCard,
    SubtitleLabel,
    setFont,
    ExpandLayout,
    TableWidget
)

from core.notification import notify
from window import Window

MAIN_BANNER = 'gui/assets/banner_home_bg.png'


class MyQLabel(QLabel):
    button_clicked_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(MyQLabel, self).__init__(parent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.button_clicked_signal.emit()

    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)


class HomeFragment(QFrame):
    updateButtonState = pyqtSignal(bool)  # 创建用于更新按钮状态的信号

    def __init__(self, parent: Window = None, config=None):
        super().__init__(parent=parent)
        self.log_entries = None
        self.config = config
        self.once = True
        self.event_map = {}
        self.expandLayout = QVBoxLayout(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.info_box = QFrame(self)
        self.info_box.setFixedHeight(45)
        self.infoLayout = QHBoxLayout(self.info_box)

        self.crt_line_index = -1


        title = f'蔚蓝档案自动脚本 {self.config.get("name")}'
        self.banner_visible = self.config.get('bannerVisibility')
        self.label = SubtitleLabel(title, self)
        self.info = SubtitleLabel('无任务', self)
        setFont(self.label, 24)
        setFont(self.info, 24)

        self.infoLayout.addWidget(self.label, 0, Qt.AlignLeft)
        self.infoLayout.addStretch(1)
        self.infoLayout.addWidget(self.info, 0, Qt.AlignRight)

        self.banner = MyQLabel(self)
        self.banner.setFixedHeight(200)
        self.banner.setMaximumHeight(200)
        pixmap = QPixmap(MAIN_BANNER).scaled(
            self.banner.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.banner.setPixmap(pixmap)
        self.banner.setScaledContents(True)
        self.banner.setVisible(self.banner_visible)

        self.startup_card = PrimaryPushSettingCard(
            self.tr('启动'),
            FIF.CARE_RIGHT_SOLID,
            self.tr('档案，启动'),
            '开始你的档案之旅',
            self
        )

        self.bottomLayout = QHBoxLayout()

        self.label_update = QLabel(self)

        self.column_1 = QVBoxLayout(self)
        self.column_2 = QVBoxLayout(self)

        self.table_view = TableWidget(self)
        self.table_view.setColumnCount(3)
        self.table_view.setFixedWidth(360)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(2, 1)
        # hide index column
        self.table_view.verticalHeader().setVisible(False)

        self.table_view.setHorizontalHeaderLabels(['内容', '贡献者', '提交时间'])
        # self.table_view.setCellWidget(0,0, self.label_update)
        threading.Thread(target=self.fetch_update_info, daemon=True).start()

        self.label_logger = QLabel(self)
        self.logger_box = TextEdit(self)
        self.logger_box.setReadOnly(True)
        # self.table_view.setStyleSheet('QTableWidget{background: #fff;corner-radius: 10px;}')

        self.label_c_1 = QLabel('更新历史', self)
        self.label_c_2 = QLabel('运行日志', self)

        self.label_c_1.setStyleSheet('font-size: 20px;font-weight: 400;font-family: "Microsoft YaHei"')
        self.label_c_2.setStyleSheet('font-size: 20px;font-weight: 400;font-family: "Microsoft YaHei"')

        self.column_1.addWidget(self.label_c_1)
        self.column_2.addWidget(self.label_c_2)

        self.column_1.addWidget(self.table_view)
        self.column_2.addWidget(self.logger_box)

        self.bottomLayout.addLayout(self.column_1)
        self.bottomLayout.addLayout(self.column_2)
        self.bottomLayout.setSpacing(10)

        self.__initLayout()

        self._main_thread_attach = MainThread(self.config)
        self.config.set_main_thread(self._main_thread_attach)
        # self.scheduler = self.config.get_main_thread().get_baas_thread().scheduler

        self._main_thread_attach.button_signal.connect(self.set_button_state)
        self._main_thread_attach.logger_signal.connect(self.logger_box.append)
        self._main_thread_attach.update_signal.connect(self.call_update)

        config.add_signal('update_signal', self._main_thread_attach.update_signal)
        # self.banner.button_clicked_signal.connect(self._main_thread_attach.get_screen)
        self.startup_card.clicked.connect(self._start_clicked)
        # set a hash object name for this widget
        self.object_name = md5(f'{time.time()}%{random()}'.encode('utf-8')).hexdigest()
        self.setObjectName(self.object_name)

    def fetch_update_info(self):
        GIT_HOME = './toolkit/Git/bin/git.exe'
        # 获取提交日志
        result = subprocess.run([GIT_HOME, 'log'], capture_output=True, text=True, encoding='utf-8')
        output = result.stdout
        # print(output)
        # 解析提交日志
        self.log_entries = []
        current_entry = {}
        for line in output.split('\n'):
            if line.startswith('commit'):
                if current_entry:
                    self.log_entries.append(current_entry)
                current_entry = {'id': line.split()[1][0:6]}
            elif line.startswith('Author:'):
                _author = line.split(':')[1].strip()
                _author = _author.split('<')[0].strip()
                current_entry['author'] = _author
            elif line.startswith('Date:'):
                _date = line.split(': ')[1].strip()
                _date = datetime.strptime(_date, "%a %b %d %H:%M:%S %Y %z").strftime("%Y-%m-%d %H:%M:%S")
                current_entry['date'] = _date
            elif line.startswith('    '):
                if 'message' in current_entry:
                    current_entry['message'] += line.strip()
                else:
                    current_entry['message'] = line.strip()

        if current_entry:
            self.log_entries.append(current_entry)

        self.table_view.setRowCount(len(self.log_entries))
        for i, entry in enumerate(self.log_entries):
            self.table_view.setItem(i, 0, QTableWidgetItem(entry['id']))
            self.table_view.setItem(i, 1, QTableWidgetItem(entry['author']))
            self.table_view.setItem(i, 2, QTableWidgetItem(entry['date']))
            self.table_view.itemClicked.connect(self.table_view_item_clicked)

    def table_view_item_clicked(self, item):
        if item.row() == self.crt_line_index:
            return
        self.crt_line_index = item.row()
        InfoBar(
            icon=InfoBarIcon.SUCCESS,
            title='设置成功',
            content=f'该版本更新内容为\n'+self.log_entries[item.row()]['message'],
            orient=Qt.Vertical,  # vertical layout
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self.parent()
        ).show()

    def resizeEvent(self, event):
        # 自动调整banner尺寸（保持比例）
        _s = self.banner.size().width() / 1920.0
        self.banner.setFixedHeight(min(int(_s * 450), 200))
        # 重新设置banner图片以保持清晰度
        pixmap = QPixmap(MAIN_BANNER).scaled(
            self.banner.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.banner.setPixmap(pixmap)
        self.banner.setScaledContents(True)
        # if self.banner_visible:
        #     self.logger_box.setFixedHeight(int(self.parent().height() * 0.35))
        # else:
        #     self.logger_box.setFixedHeight(int(self.parent().height() * 0.7))

    def call_update(self, data=None, parent=None):
        try:
            if self.event_map == {}:
                with open('./config/' + self.config.config_dir + '/event.json', 'r', encoding='utf-8') as f:
                    event_config = json.load(f)
                    for item in event_config:
                        self.event_map[item['func_name']] = item['event_name']

            if data:
                if type(data[0]) is dict:
                    self.info.setText(f'正在运行：{self.event_map[data[0]["func_name"]]}')
                else:
                    self.info.setText(f'正在运行：{data[0]}')
                    self.config.get_main_thread().get_baas_thread().scheduler.set_current_task(data[0])

            # with open('./config/' + self.config.config_dir + '/display.json', 'r', encoding='utf-8') as f:
            #     config = json.load(f)
            # if config['running'] is None or config['running'] == 'Empty':
            #     self.info.setText('无任务')
            # else:
            #     self.info.setText('正在运行：' + config['running'])
            # print('call_update:', parent, args, kwargs)

            # if data:
            #     (self.parent().parent().parent()).call_update()
        except JSONDecodeError:
            # 有时json会是空值报错, 原因未知
            print("Empty JSON data")

    def set_button_state(self, state):
        self.startup_card.button.setText(state)
        self._main_thread_attach.running = True if state == "停止" else False

    def __initLayout(self):
        self.expandLayout.setSpacing(28)
        if self.banner_visible:
            self.expandLayout.addWidget(self.banner)
        self.expandLayout.addWidget(self.info_box)
        self.expandLayout.addWidget(self.startup_card)
        # self.vBoxLayout.addWidget(self.logger_box)
        # self.logger_box.setLayout(self.logger_box_layout)

        self.expandLayout.addLayout(self.bottomLayout)
        self.setLayout(self.expandLayout)
        # self.startupCard.clicked.connect(self.__init_starter)

    def _start_clicked(self):
        self.call_update()
        if self._main_thread_attach.running:
            self._main_thread_attach.stop_play()
        else:
            self._main_thread_attach.start()

    def get_main_thread(self):
        return self._main_thread_attach

    # def __init_starter(self):
    # if self._main_thread is None:
    #     from main import Main
    #     self._main_thread = Main(logger_box=self.logger)
    # threading.Thread(target=self.__worker, daemon=True).start()

    # def __worker(self):
    #     if self._main_thread.flag_run:
    #         self._main_thread.flag_run = False
    #         self.updateButtonState.emit(False)  # 发送信号，更新按钮状态
    #         self._main_thread.send('stop')
    #     else:
    #         self._main_thread.flag_run = True
    #         self.updateButtonState.emit(True)  # 发送信号，更新按钮状态
    #         self._main_thread.send('start')


class MainThread(QThread):
    button_signal = pyqtSignal(str)
    logger_signal = pyqtSignal(str)
    update_signal = pyqtSignal(list)

    def __init__(self, config):
        super(MainThread, self).__init__()
        self.config = config
        self.hash_name = md5(f'{time.time()}%{random()}'.encode('utf-8')).hexdigest()
        self._main_thread = None
        self.Main = None
        self.running = False

    def run(self):
        self.running = True
        self.display('停止')
        self._init_script()
        self._main_thread.logger.info("Starting Blue Archive Auto Script...")
        self._main_thread.send('start')

    def stop_play(self):
        self.running = False
        if self._main_thread is None:
            return
        self.display('启动')
        self._main_thread.send('stop')
        self.exit(0)

    def _init_script(self):
        while self.Main is None:
            time.sleep(0.01)
        if self._main_thread is None:
            assert self.Main is not None
            self._main_thread = self.Main.get_thread(self.config, name=self.hash_name, logger_signal=self.logger_signal,
                                                     button_signal=self.button_signal, update_signal=self.update_signal)
            self.config.add_signal('update_signal', self.update_signal)
        self._main_thread.init_all_data()

    def display(self, text):
        self.button_signal.emit(text)

    def start_hard_task(self):
        self._init_script()
        self.update_signal.emit(['困难关推图'])
        self.display('停止')
        if self._main_thread.send('solve', 'explore_hard_task'):
            notify(title='BAAS', body='困难图推图已完成')
        self.update_signal.emit(['无任务'])
        self.display('启动')

    def start_normal_task(self):
        self._init_script()
        self.update_signal.emit(['普通关推图'])
        self.display('停止')
        if self._main_thread.send('solve', 'explore_normal_task'):
            notify(title='BAAS', body='普通图推图已完成')
        self.update_signal.emit(['无任务'])
        self.display('启动')

    def start_fhx(self):
        self._init_script()
        if self._main_thread.send('solve', 'de_clothes'):
            notify(title='BAAS', body='反和谐成功，请重启BA下载资源')

    def start_main_story(self):
        self._init_script()
        self.update_signal.emit(['自动主线剧情'])
        self.display('停止')
        if self._main_thread.send('solve', 'main_story'):
            if self._main_thread.flag_run:
                notify(title='BAAS', body='主线剧情已完成')
        self.update_signal.emit(['无任务'])
        self.display('启动')

    def start_group_story(self):
        self._init_script()
        self.update_signal.emit(['自动小组剧情'])
        self.display('停止')
        if self._main_thread.send('solve', 'group_story'):
            if self._main_thread.flag_run:
                notify(title='BAAS', body='小组剧情已完成')
        self.display('启动')
        self.update_signal.emit(['无任务'])

    def start_mini_story(self):
        self._init_script()
        self.display('停止')
        self.update_signal.emit(['自动支线剧情'])
        if self._main_thread.send('solve', 'mini_story'):
            if self._main_thread.flag_run:
                notify(title='BAAS', body='支线剧情已完成')
        self.display('启动')
        self.update_signal.emit(['无任务'])

    def start_explore_activity_story(self):
        self._init_script()
        self.display('停止')
        self.update_signal.emit(['自动活动剧情'])
        if self._main_thread.send('solve', 'explore_activity_story'):
            if self._main_thread.flag_run:
                notify(title='BAAS', body='活动剧情已完成')
        self.display('启动')
        self.update_signal.emit(['无任务'])

    def start_explore_activity_mission(self):
        self._init_script()
        self.display('停止')
        self.update_signal.emit(['自动活动任务'])
        if self._main_thread.send('solve', 'explore_activity_mission'):
            if self._main_thread.flag_run:
                notify(title='BAAS', body='活动任务已完成')
        self.display('启动')
        self.update_signal.emit(['无任务'])

    def start_explore_activity_challenge(self):
        self._init_script()
        self.update_signal.emit(['自动活动挑战'])
        self.display('停止')
        if self._main_thread.send('solve', 'explore_activity_challenge'):
            if self._main_thread.flag_run:
                notify(title='BAAS', body='活动挑战推图已完成')
        self.display('启动')
        self.update_signal.emit(['无任务'])

    def get_baas_thread(self):
        return self._main_thread

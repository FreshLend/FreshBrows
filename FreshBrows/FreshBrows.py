##################################################################################
#                                                                                #
#                        F R E S H L E N D    S T U D I O                        #
#                                                                                #
#                                APP: FRESHBROWS                                 #
# Авторы: FreshGame                                                              #
#                                                                                #
##################################################################################

import sys
import os
from PyQt5.QtCore import QUrl, QSettings
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QTabWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtGui import QIcon

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FreshBrows')
        self.resize(1080, 820)
        self.setWindowIcon(QIcon('icons/browser_icon.png'))

        # Создание директорий для данных браузера и кеша
        data_dir = os.path.join(os.getcwd(), 'browser_data')
        cache_dir = os.path.join(data_dir, 'cache')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        self.profile = QWebEngineProfile("MyProfile", self)
        self.profile.setCachePath(cache_dir)
        self.profile.setPersistentStoragePath(data_dir)

        self.settings = QSettings(os.path.join(data_dir, 'settings.ini'), QSettings.IniFormat)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_on_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        home_page = os.path.abspath('FreshBrows.html')
        self.add_new_tab(QUrl.fromLocalFile(home_page), 'Homepage')

        self.is_dark_theme = self.settings.value("is_dark_theme", False, type=bool)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        nav_bar = QHBoxLayout()

        # Кнопки навигации
        back_btn = QPushButton(QIcon('icons/back.png'), '')
        forward_btn = QPushButton(QIcon('icons/forward.png'), '')
        reload_btn = QPushButton(QIcon('icons/reload.png'), '')
        home_btn = QPushButton(QIcon('icons/home.png'), '')

        # События кнопок
        back_btn.clicked.connect(lambda: self.tabs.currentWidget().back())
        forward_btn.clicked.connect(lambda: self.tabs.currentWidget().forward())
        reload_btn.clicked.connect(lambda: self.tabs.currentWidget().reload())
        home_btn.clicked.connect(self.navigate_home)

        add_tab_btn = QPushButton(QIcon('icons/plus.png'), '')  # Изменено здесь
        add_tab_btn.clicked.connect(self.add_tab_clicked)

        # Добавляем кнопки в панель навигации
        nav_bar.addWidget(back_btn)
        nav_bar.addWidget(forward_btn)
        nav_bar.addWidget(reload_btn)
        nav_bar.addWidget(home_btn)
        nav_bar.addWidget(add_tab_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        self.theme_btn = QPushButton('Toggle Theme')
        self.theme_btn.clicked.connect(self.toggle_theme)
        nav_bar.addWidget(self.theme_btn)

        vbox = QVBoxLayout()
        vbox.addLayout(nav_bar)

        main_widget = QWidget()
        main_widget.setLayout(vbox)
        self.setMenuWidget(main_widget)

        self.apply_styles()

    def navigate_home(self):
        home_page = os.path.abspath('FreshBrows.html')
        self.tabs.currentWidget().setUrl(QUrl.fromLocalFile(home_page))

    def update_tab_icon(self, icon, index):
        if self.tabs is not None:
            self.tabs.setTabIcon(index, icon)

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None or qurl == QUrl(''):
            home_page = os.path.abspath('FreshBrows.html')
            qurl = QUrl.fromLocalFile(home_page)

        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, QIcon('icons/browser_icon.png'), label)  # Установите иконку по умолчанию
        self.tabs.setCurrentIndex(i)

        browser.iconChanged.connect(lambda icon, i=i: self.update_tab_icon(icon, i))

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    def tab_on_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - FreshBrows" % title)

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        if hasattr(self, 'url_bar'):
            if browser != self.tabs.currentWidget():
                return

            # Проверка является ли текущий URL домашней страницей
            home_page = os.path.abspath('FreshBrows.html')
            home_url = QUrl.fromLocalFile(home_page).toString()

            if q.toString() == home_url:
                # Если это домашняя страница, отображаем пустую строку или "Домашняя страница"
                self.url_bar.setText("Домашняя страница")
            else:
                # В другом случае отображаем полный URL
                self.url_bar.setText(q.toString())
                self.url_bar.setCursorPosition(0)

    def add_tab_clicked(self):
        self.add_new_tab()

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_styles()

    def apply_styles(self):
        if self.is_dark_theme:
            self.setStyleSheet("""
                QWidget {
                    background-color: #333;
                    color: #CCC;
                }
                QLineEdit {
                    border: 1px solid #555;
                    border-radius: 10px;
                    padding: 5px;
                    background-color: #555;
                    color: #EEE;
                }
                QPushButton {
                    border: 1px solid #666;
                    border-radius: 10px;
                    padding: 5px;
                    background-color: #555;
                    color: #FF5555; /* Яркий акцент для кнопок */
                }
                QPushButton:hover {
                    border: 1px solid #777;
                    background-color: #666;
                    color: #FFFFFF; /* Светлее при наведении */
                }
                QTabWidget::pane {
                    border-top: 2px solid #666;
                }
                QTabBar::tab {
                    background: #555;
                    color: #EEE;
                }
                QTabBar::tab:selected {
                    background: #666;
                    color: #FFF;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #EEE;
                    color: #333;
                }
                QLineEdit {
                    border: 1px solid #CCC;
                    border-radius: 10px;
                    padding: 5px;
                    background-color: #FFF;
                    color: #333;
                }
                QPushButton {
                    border: 1px solid #BBB;
                    border-radius: 10px;
                    padding: 5px;
                    background-color: #DDD;
                    color: #333;
                }
                QPushButton:hover {
                    border: 1px solid #AAA;
                    background-color: #CCC;
                }
                QTabWidget::pane {
                    border-top: 2px solid #CCC;
                }
                QTabBar::tab {
                    background: #DDD;
                    color: #333;
                }
                QTabBar::tab:selected {
                    background: #EEE;
                    color: #000;
                }
            """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = SimpleBrowser()
    browser.show()
    sys.exit(app.exec_())

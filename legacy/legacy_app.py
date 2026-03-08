#!/home/hotel/Documentos/EsmeraldaV1/venv/bin/python
import sys
import os
import time
import threading
import shutil
import subprocess
import platform
import json
import math
from datetime import date, datetime, timedelta
from decimal import Decimal

# PySide6 carga rápido, esto está bien aquí
from PySide6.QtCore import (Qt, QRect, QTimer, QTime, QDate, QSize, QDateTime, QLocale, QRegularExpression, Signal, QModelIndex, QAbstractTableModel, QModelIndex)
from PySide6.QtGui import (QPixmap, QCursor, QColor, QFont, QGuiApplication, QIcon, QKeySequence,  QRegularExpressionValidator, QShortcut)  # Agrega los que necesites
from PySide6.QtWidgets import (QApplication, QHeaderView, QTextEdit, QTableWidgetItem, QAbstractScrollArea, QGroupBox, QScrollArea, QSplashScreen, QWidget, QMainWindow, QProgressBar, QDialog, QMessageBox, QInputDialog, QItemDelegate,
                               QFrame, QTabWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
                               QLabel, QLineEdit, QPlainTextEdit, QPushButton, QCheckBox, QTableWidget, QTableView, QAbstractItemView,
                               QComboBox, QStyledItemDelegate, QTimeEdit, QDateEdit, QDateTimeEdit, QSpinBox, QDoubleSpinBox, QAbstractSpinBox, QSpacerItem, QSizePolicy, QFileDialog)

# Requests suele ser rápido, pero si puedes moverlo, mejor.
import requests
from requests.exceptions import ConnectionError

# --- IMPORTS PESADOS (¡BORRA ESTOS DE AQUÍ!) ---
# Mueve estos imports DENTRO de las funciones donde se usan:
import pandas as pd
import mysql.connector as mc
import telebot

HOTEL = "PRUEBA"

# ----- Database Config ---------

json_config = open('config.json')

data = json.load(json_config)

host_ip = data[0].get("database_ip")
database_user = data[0].get("database_user")
database_password = data[0].get("database_password")

json_config.close()


class PagoWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ventas')
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setFixedHeight(740)
        self.setWindowIcon(QIcon(f"img/minilogo.ico"))
        layout = QGridLayout(self)
        self.center_window()

        self.SettingsWindow = SettingsWindow()
        self.TableViewData = TableViewData()

        self.int_validator = QRegularExpressionValidator(
            QRegularExpression(r'[0-9]+'))
        str_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[a-z A-Z]*$'))
        self.hab_num = "01"
        self.transaccion = ""
        self.id_estancia = ""
        self.dolarprice = 0.00
        self.temp_closeEvent = True

        self.setStyleSheet('''
        QLabel {
                background: rgba(0, 0, 0, 0);
                color: rgb(242, 242, 242);
                font-size: 16px;
                font-weight: bold}

        QLineEdit:focus QPushButton:focus {
            border: 2px solid #00CF35;
            padding: 3px}

        QDateEdit {
            font-size: 14px;
            color: black;
            background-color: white;
            padding: 2px
        }
        ''')

  ######################################### MainWindow Data #########################################

        FRusuario = QFrame()
        RFhab_layout = QFormLayout()
        FRusuario.setLayout(RFhab_layout)
        RFhab_layout.setVerticalSpacing(10)
        layout.addWidget(FRusuario, 0, 0)

# ---------------------------------------------------------------------------------------------------
        atendido_por = QLabel("Atendido por  ")
        RFhab_layout.setWidget(
            0, QFormLayout.LabelRole, atendido_por)

        self.input_atendido_por = QLineEdit()
        self.input_atendido_por.setFocusPolicy(Qt.ClickFocus)
        RFhab_layout.setWidget(
            0, QFormLayout.FieldRole, self.input_atendido_por)

  ######################################### Cliente Data #########################################

        self.tab_huespedes = QTabWidget()
        self.tab_huespedes.setStyleSheet('''
        QTabBar:tab {
            background-color: rgb(40, 40, 40);
            height: auto;
            width: auto;
            padding: 2px;
            margin-top: 4px;
        }

        QTabBar:tab:selected {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 #11998E, stop:0 #38ef7d);
            font-weight: bold;
            margin-top: 0px;
        }
        ''')

        self.corner_widget = QWidget()

        for i in range(6):
            self.add_huesped_tab(i)

        layout.addWidget(self.tab_huespedes, 1, 0, 3, 1)

  ######################################### Stay Duration #########################################

        stay = QFrame()
        layout.addWidget(stay, 4, 0, 2, 1)
        stay.setStyleSheet("border-radius: 2px;")
        stay_layout = QFormLayout()
        stay_layout.setVerticalSpacing(10)
        stay.setLayout(stay_layout)


# ---------------------------------------------------------------------------------------------------
        procedencia = QLabel()
        procedencia.setText("Procedencia")
        stay_layout.setWidget(
            0, QFormLayout.LabelRole, procedencia)

        self.input_procedencia = QComboBox()
        self.input_procedencia.addItems(
            ["Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar", "Carabobo", "Cojedes", "Delta Amacuro", "Distrito Capital", "Falcón", "Guárico", "Lara", "Mérida", "Miranda", "Monagas", "Nueva Esparta", "Portuguesa", "Sucre", "Táchira", "Trujillo", "Vargas", "Yaracuy", "Zulia", "Extranjero"])
        self.input_procedencia.setEditable(True)
        self.input_procedencia.setValidator(str_validator)
        stay_layout.setWidget(
            0, QFormLayout.FieldRole, self.input_procedencia)

        destino = QLabel()
        destino.setText("Destino")
        stay_layout.setWidget(
            1, QFormLayout.LabelRole, destino)

        self.input_destino = QComboBox()
        self.input_destino.addItems(
            ["Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar", "Carabobo", "Cojedes", "Delta Amacuro", "Distrito Capital", "Falcón", "Guárico", "Lara", "Mérida", "Miranda", "Monagas", "Nueva Esparta", "Portuguesa", "Sucre", "Táchira", "Trujillo", "Vargas", "Yaracuy", "Zulia", "Extranjero"])
        self.input_destino.setEditable(True)
        self.input_destino.setValidator(str_validator)
        stay_layout.setWidget(
            1, QFormLayout.FieldRole, self.input_destino)

# ---------------------------------------------------------------------------------------------------

        line = QFrame()
        stay_layout.setWidget(
            2, QFormLayout.SpanningRole, line)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

# ---------------------------------------------------------------------------------------------------
        fhentrada = QLabel()
        fhentrada.setText("Entrada")
        stay_layout.setWidget(
            3, QFormLayout.LabelRole, fhentrada)

        self.input_fentrada = QDateTimeEdit()
        self.input_fentrada.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.input_fentrada.setDisplayFormat("hh:mm / dd-MM-yyyy")
        self.input_fentrada.setCalendarPopup(True)
        self.input_fentrada.calendarWidget().setLocale(QLocale(QLocale.Spanish))
        self.input_fentrada.setEnabled(True)
        stay_layout.setWidget(
            3, QFormLayout.FieldRole, self.input_fentrada)

# ---------------------------------------------------------------------------------------------------
        fhsalida = QLabel()
        fhsalida.setText("Salida")
        stay_layout.setWidget(
            4, QFormLayout.LabelRole, fhsalida)

        self.input_fsalida = QDateTimeEdit()
        self.input_fsalida.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.input_fsalida.setDisplayFormat("hh:mm / dd-MM-yyyy")
        self.input_fsalida.setEnabled(False)
        stay_layout.setWidget(
            4, QFormLayout.FieldRole, self.input_fsalida)

        estadia_dias = QLabel(self)
        estadia_dias.setText("Dias")
        stay_layout.setWidget(
            5, QFormLayout.LabelRole, estadia_dias)

        self.input_estadia_dias = QSpinBox()
        self.input_estadia_dias.setMinimum(1)
        self.input_estadia_dias.valueChanged.connect(self.set_days)
        stay_layout.setWidget(
            5, QFormLayout.FieldRole, self.input_estadia_dias)


# ------------------------------------------------------------------------------------------------

        self.bparcial = QPushButton(self)
        self.bparcial.setFixedWidth(120)
        stay_layout.setWidget(
            6, QFormLayout.LabelRole, self.bparcial)

        self.bhospedaje = QPushButton(self)
        stay_layout.setWidget(
            6, QFormLayout.FieldRole, self.bhospedaje)

  ######################################### Hab Payment #########################################

        formaPago = QFrame()
        formaPago.setMinimumSize(320, 500)
        layout.addWidget(formaPago, 0, 1, 6, 1)
# ---------------------------------------------------------------------------------------------------

        self.FRcosto = QFrame(formaPago)
        self.FRcosto.setGeometry(QRect(0, 0, 340, 100))

        estadia = QLabel(formaPago)
        estadia.setGeometry(QRect(15, 8, 125, 25))
        estadia.setText("Estadia tipo")

        self.estadia_type = QLabel(formaPago)
        self.estadia_type.setGeometry(QRect(114, 8, 170, 25))

        hab_costo = QLabel(formaPago)
        hab_costo.setGeometry(
            QRect(14, 36, 80, 30))
        hab_costo.setText("Costo")

        self.costo_dolar = QLabel(formaPago)
        self.costo_dolar.setGeometry(QRect(96, 38, 200, 25))

        self.costo_bs = QLabel(formaPago)
        self.costo_bs.setGeometry(QRect(96, 66, 200, 25))
        self.costo_bs.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0); color: rgb(242, 242, 242); font-size: 20px; font-weight: bold;")


# ---------------------------------------------------------------------------------------------------

        bolivares = QLabel(formaPago)
        bolivares.setGeometry(QRect(230, 120, 90, 20))
        bolivares.setText("Bolivares")

        dolares = QLabel(formaPago)
        dolares.setGeometry(QRect(145, 120, 90, 20))
        dolares.setText("Dolares")
# ---------------------------------------------------------------------------------------------------
        self.FP1 = QComboBox(formaPago)
        self.FP1.setFocusPolicy(Qt.ClickFocus)
        self.FP1.setGeometry(QRect(14, 152, 106, 25))

        self.input_FP1 = QDoubleSpinBox(formaPago)
        self.input_FP1.setGeometry(QRect(140, 152, 54, 28))

        self.FP1_bs = QLabel(formaPago)
        self.FP1_bs.setGeometry(QRect(230, 152, 90, 28))
# ---------------------------------------------------------------------------------------------------
        self.FP2 = QComboBox(formaPago)
        self.FP2.setFocusPolicy(Qt.ClickFocus)
        self.FP2.setGeometry(QRect(14, 190, 106, 25))

        self.input_FP2 = QDoubleSpinBox(formaPago)
        self.input_FP2.setGeometry(QRect(140, 190, 54, 28))

        self.FP2_bs = QLabel(formaPago)
        self.FP2_bs.setGeometry(QRect(230, 190, 90, 28))
# ---------------------------------------------------------------------------------------------------
        self.FP3 = QComboBox(formaPago)
        self.FP3.setFocusPolicy(Qt.ClickFocus)
        self.FP3.setGeometry(QRect(14, 228, 106, 25))

        self.input_FP3 = QDoubleSpinBox(formaPago)
        self.input_FP3.setGeometry(QRect(140, 228, 54, 28))

        self.FP3_bs = QLabel(formaPago)
        self.FP3_bs.setGeometry(QRect(230, 228, 90, 28))
# ---------------------------------------------------------------------------------------------------
        self.FP4 = QComboBox(formaPago)
        self.FP4.setFocusPolicy(Qt.ClickFocus)
        self.FP4.setGeometry(QRect(14, 266, 106, 25))

        self.input_FP4 = QDoubleSpinBox(formaPago)
        self.input_FP4.setGeometry(QRect(140, 266, 54, 28))

        self.FP4_bs = QLabel(formaPago)
        self.FP4_bs.setGeometry(QRect(230, 266, 90, 28))
# ---------------------------------------------------------------------------------------------------

        self.input_voucher = QLineEdit(formaPago)
        self.input_voucher.setGeometry(QRect(14, 306, 108, 28))
        self.input_voucher.returnPressed.connect(self.use_voucher)
        self.input_voucher.setPlaceholderText("Voucher...")

        self.bvocher = QPushButton(formaPago)
        self.bvocher.setGeometry(QRect(140, 306, 32, 28))
        self.bvocher.setText("✓")
        self.bvocher.clicked.connect(self.use_voucher)
        self.bvocher.setCursor(QCursor(Qt.PointingHandCursor))
        self.bvocher.setStyleSheet('''
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.8, y2:0.8, stop:1 #11998E, stop:0 #38ef7d);
                font-size: 14px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                font-size: 16px;
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.4, y2:0.4, stop:1 #11998E, stop:0 #38ef7d);
                font-size: 14px
            }
            ''')

        self.bvocher_cancel = QPushButton(formaPago)
        self.bvocher_cancel.setGeometry(QRect(178, 306, 32, 28))
        self.bvocher_cancel.setText("✖")
        self.bvocher_cancel.clicked.connect(self.cancel_voucher)
        self.bvocher_cancel.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.bvocher_cancel.setStyleSheet('''
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.8, y2:0.8, stop:1 rgb(150, 2, 2), stop:0 rgb(242, 5, 5));
                font-size  : 14px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                font-size: 16px;
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.4, y2:0.4, stop:1 rgb(150, 2, 2), stop:0 rgb(242, 5, 5));
                font-size: 14px
            }
            ''')

        self.valor_voucher = QLabel(formaPago)
        self.valor_voucher.setGeometry(QRect(230, 306, 260, 28))

        line = QFrame(formaPago)
        line.setGeometry(QRect(0, 360, 320, 6))
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: rgb(40, 40, 40)")

        faltan = QLabel(formaPago)
        faltan.setGeometry(QRect(14, 380, 80, 30))
        faltan.setText("Faltan")

        self.faltan_dolar = QLabel(formaPago)
        self.faltan_dolar.setGeometry(
            QRect(100, 384, 200, 25))

        self.faltan_bs = QLabel(formaPago)
        self.faltan_bs.setGeometry(QRect(100, 410, 200, 25))

        line = QFrame(formaPago)
        line.setGeometry(QRect(0, 450, 320, 6))
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: rgb(40, 40, 40)")

  ######################################### Extras Payment #########################################

        extras = QLabel(formaPago)
        extras.setGeometry(QRect(14, 470, 150, 25))
        extras.setText("Ingresos Extras")
        extras.setStyleSheet("font-size: 18px; font-weight: bold;")

# ---------------------------------------------------------------------------------------------------
        self.extra1 = QComboBox(formaPago)
        self.extra1.setFocusPolicy(Qt.ClickFocus)
        self.extra1.setGeometry(QRect(14, 508, 106, 25))

        self.input_extra1 = QDoubleSpinBox(formaPago)
        self.input_extra1.setGeometry(QRect(140, 510, 54, 28))

        self.extra1_bs = QLabel(formaPago)
        self.extra1_bs.setGeometry(QRect(230, 515, 106, 20))
# ---------------------------------------------------------------------------------------------------
        self.extra2 = QComboBox(formaPago)
        self.extra2.setFocusPolicy(Qt.ClickFocus)
        self.extra2.setGeometry(QRect(14, 546, 106, 25))

        self.input_extra2 = QDoubleSpinBox(formaPago)
        self.input_extra2.setGeometry(QRect(140, 548, 54, 28))

        self.extra2_bs = QLabel(formaPago)
        self.extra2_bs.setGeometry(QRect(230, 551, 106, 20))
# ---------------------------------------------------------------------------------------------------
        self.extra3 = QComboBox(formaPago)
        self.extra3.setFocusPolicy(Qt.ClickFocus)
        self.extra3.setGeometry(QRect(14, 584, 106, 27))

        self.input_extra3 = QDoubleSpinBox(formaPago)
        self.input_extra3.setGeometry(QRect(140, 586, 54, 28))

        self.extra3_bs = QLabel(formaPago)
        self.extra3_bs.setGeometry(QRect(230, 589, 106, 20))

  ######################################### Total Amount #########################################

        total = QLabel(formaPago)
        total.setGeometry(QRect(14, 640, 90, 30))
        total.setText("TOTAL")

        self.total_dolar = QLabel(formaPago)
        self.total_dolar.setGeometry(QRect(106, 635, 180, 40))
        font = QFont()
        font.setPointSize(14)
        self.total_dolar.setFont(font)

        self.total_bs = QLabel(formaPago)
        self.total_bs.setGeometry(QRect(106, 670, 180, 40))
        font = QFont()
        font.setPointSize(14)
        self.total_bs.setFont(font)

  ######################################### Rest (not in frames) #########################################

        FRhab = QFrame()
        # FRhab.setFixedSize(210, 300)
        layout.addWidget(FRhab, 0, 3, 3, 1)

        self.habitacion = QLabel("Habitación:", FRhab)
        self.habitacion.setGeometry(QRect(10, 10, 100, 25))
        self.input_habitacion = QLabel("???", FRhab)
        self.input_habitacion.setGeometry(QRect(110, 10, 100, 25))

        self.habitacion_tipo = QLabel("Tipo:", FRhab)
        self.habitacion_tipo.setGeometry(QRect(10, 40, 100, 25))
        self.input_habitacion_tipo = QLabel("???", FRhab)
        self.input_habitacion_tipo.setGeometry(QRect(110, 40, 100, 25))

        self.observaciones_hab = QPlainTextEdit(FRhab)
        self.observaciones_hab.setGeometry(QRect(10, 80, 190, 100))
        self.observaciones_hab.setTabChangesFocus(True)
        self.observaciones_hab.setPlaceholderText(
            "Observaciones a la Habitación...")

        self.bbloquear = QPushButton(FRhab)
        self.bbloquear.setGeometry(QRect(10, 200, 92, 45))
        self.bbloquear.clicked.connect(self.hab_bloquear)
        self.bbloquear.setText("Bloquear\nHabitación")
        self.bbloquear.setToolTip('Bloquear Habitación')
        self.bbloquear.setCursor(QCursor(Qt.PointingHandCursor))
        self.bbloquear.setStyleSheet('''
                            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 #A27C22, stop:0 #FFBF00);
                            color: rgb(242, 242, 242);
                            border-radius: 2px;
                            font-size: 12px;
                            font-weight: bold;
                            ''')

        self.bhab_transaciones = QPushButton("Historial de\nHabitación", FRhab)
        self.bhab_transaciones.setGeometry(QRect(110, 200, 92, 45))
        self.bhab_transaciones.clicked.connect(self.hab_transacciones)
        self.bhab_transaciones.setToolTip('Historial de la Habitación')
        self.bhab_transaciones.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.bretoque = QPushButton(FRhab)
        self.bretoque.setGeometry(QRect(10, 260, 192, 30))
        self.bretoque.clicked.connect(self.retoque)
        self.bretoque.setCursor(
            QCursor(Qt.PointingHandCursor))

        VspacerItem = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(VspacerItem, 4, 3)

# ---------------------------------------------------------------------------------------------------

        botones = QFrame()
        botones.setFixedWidth(210)
        layout.addWidget(botones, 3, 3, 3, 1)

        self.precensia_huesped = QLabel("Huesped: ", botones)
        self.precensia_huesped.setGeometry(QRect(10, 10, 100, 25))
        self.input_precensia_huesped = QLabel("Presente", botones)
        self.input_precensia_huesped.setGeometry(
            QRect(110, 10, 100, 25))

        self.bprecensia_huesped = QPushButton("Entradas/Salidas", botones)
        self.bprecensia_huesped.setGeometry(QRect(10, 50, 190, 25))
        self.bprecensia_huesped.clicked.connect(self.precensia_huesped_tabla)
        self.bprecensia_huesped.setToolTip('Historial de la Habitación')
        self.bprecensia_huesped.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.observaciones_transaccion = QPlainTextEdit(botones)
        self.observaciones_transaccion.setGeometry(
            QRect(10, 110, 190, 80))
        self.observaciones_transaccion.setTabChangesFocus(True)
        self.observaciones_transaccion.setPlaceholderText(
            "Observaciones a la transacción...")

        self.bcambiar_hab = QPushButton(botones)
        self.bcambiar_hab.setGeometry(QRect(10, 200, 50, 50))
        self.bcambiar_hab.setText("Mover\nHuesped")
        self.bcambiar_hab.clicked.connect(self.cambiar_hab)
        self.bcambiar_hab.setToolTip('Mover al huesped de Habitación')
        self.bcambiar_hab.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.btrash = QPushButton(botones)
        self.btrash.setGeometry(QRect(70, 200, 50, 50))
        self.btrash.setIconSize(QSize(30, 30))
        self.btrash.setToolTip('Borrar Transacción')
        self.btrash.setIcon(QIcon(f"img/trash.png"))
        self.btrash.setCursor(QCursor(Qt.PointingHandCursor))
        self.btrash.setStyleSheet(f'''
                QPushButton:hover {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 rgb(150, 2, 2), stop:0 rgb(242, 5, 5));
                }}''')
        self.btrash.clicked.connect(self.trash)

        self.begresar = QPushButton(botones)
        self.begresar.setGeometry(QRect(10, 270, 190, 40))
        self.begresar.setCursor(QCursor(Qt.PointingHandCursor))
        self.begresar.setText("Egresar")
        self.begresar.clicked.connect(self.egreso_cliente)

        self.bingresar = QPushButton(botones)
        self.bingresar.setGeometry(QRect(10, 320, 190, 40))
        self.bingresar.setCursor(QCursor(Qt.PointingHandCursor))
        self.bingresar.setText("Ingresar")
        self.bingresar.clicked.connect(self.check_ingreso_cliente)


# --------------------------------- RENOVACION ---------------------------------------

        self.brenovar = QPushButton(botones)
        self.brenovar.setGeometry(
            QRect(10, 320, 190, 40))
        self.brenovar.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.brenovar.setText("Renovar")
        self.brenovar.clicked.connect(self.renovar)
        self.brenovar.setStyleSheet('''
                QPushButton {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(189, 195, 199), stop:1 rgb(36, 54, 70));
                    font-size: 18px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    font-size: 20px;
                }
                QPushButton:pressed {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(169, 175, 180), stop:1 rgb(10, 30, 50));
                    font-size: 18px
                }
                ''')

    ################################# SETING UP STYLESHEET #################################

        headers = [faltan, self.valor_voucher,
                   hab_costo, self.costo_dolar, self.faltan_dolar,
                   total, self.total_dolar, self.total_bs]

        self.bFP = [self.bparcial, self.bhospedaje]
# ---------------------------------------------------------------------------------------------------

        spinbox = [self.input_FP1, self.input_FP2, self.input_FP3, self.input_FP4,
                   self.input_extra1, self.input_extra2, self.input_extra3]

        for i in spinbox:
            i.setFixedWidth(70)
            i.setButtonSymbols(QAbstractSpinBox.NoButtons)
            i.setMaximum(999)
            i.valueChanged.connect(self.price_calculation)

        for i in headers:
            i.setStyleSheet('''
            background: rgba(0, 0, 0, 0);
            color: rgb(242, 242, 242);
            font-size: 26px;
            font-weight: bold
            ''')

        for i in self.bFP:
            font = QFont()
            font.setPointSize(4)
            font.setBold(True)
            i.setFont(font)
            i.setCursor(QCursor(Qt.PointingHandCursor))
            i.clicked.connect(self.tipo_de_tiempo)

    ################################# SETING UP FUNCTIONS #################################

    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def add_huesped_tab(self, index):
        new_tab = QWidget()
        layout = QFormLayout()

        new_tab.setStyleSheet('''
        QLabel {
            background: rgba(0, 0, 0, 0);
            color: rgb(242, 242, 242);
            font-size: 17px;
            font-weight: bold}
            ''')

        cedula = QLabel("Cedula / RIF ↵")
        self.input_cedula = QLineEdit()
        self.input_cedula.setValidator(self.int_validator)
        self.input_cedula.setMaxLength(10)
        self.input_cedula.returnPressed.connect(self.cliente_existe)
        self.input_cedula.setObjectName("input_cedula")
        layout.addRow(cedula, self.input_cedula)

        nombre = QLabel("Nombre")
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre Apellido")
        self.input_nombre.setObjectName("input_nombre")
        layout.addRow(nombre, self.input_nombre)

        self.fnacimiento = QLabel("Fecha Nacimiento")
        self.input_fnacimiento = QDateEdit()
        self.input_fnacimiento.setCalendarPopup(True)
        self.input_fnacimiento.calendarWidget().setLocale(QLocale(QLocale.Spanish))
        self.input_fnacimiento.setDisplayFormat("dd-MM-yyyy")
        self.input_fnacimiento.setDateRange(
            QDate.currentDate().addYears(-100), QDate.currentDate().addYears(-18))
        self.input_fnacimiento.setDate(QDate.currentDate().addYears(-17))
        self.input_fnacimiento.setObjectName("input_fnacimiento")
        layout.addRow(self.fnacimiento, self.input_fnacimiento)

        nacionalidad = QLabel("Nacionalidad")
        self.input_nacionalidad = QComboBox()
        self.input_nacionalidad.addItems(["Venezolano", "Extranjero"])
        self.input_nacionalidad.setEditable(True)
        self.input_nacionalidad.setObjectName("input_nacionalidad")
        layout.addRow(nacionalidad, self.input_nacionalidad)

        estado_civil = QLabel("Edo. Civil")
        self.input_estado_civil = QComboBox()
        self.input_estado_civil.addItems(
            ["Casado", "Soltero", "Divorciado", "Viudo"])
        self.input_estado_civil.setEditable(True)
        self.input_estado_civil.setObjectName("input_estado_civil")
        layout.addRow(estado_civil, self.input_estado_civil)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addRow(line)

        telefono = QLabel("Telefono")
        self.input_telefono = QLineEdit()
        self.input_telefono.setValidator(self.int_validator)
        self.input_telefono.setMaxLength(11)
        self.input_telefono.returnPressed.connect(self.next_line)
        self.input_telefono.setObjectName("input_telefono")
        layout.addRow(telefono, self.input_telefono)

        profesion = QLabel("Profesión")
        self.input_profesion = QComboBox()
        self.input_profesion.addItems([
            "Comerciante", "Contador", "Doctor", "Empresario", "Electricista",
            "Estudiante", "Ingeniero", "Licenciado", "Medico", "Mecanico",
            "Profesor", "Policia", "Tecnico"
        ])
        self.input_profesion.setEditable(True)
        self.input_profesion.setObjectName("input_profesion")
        layout.addRow(profesion, self.input_profesion)

        self.observaciones_cliente = QPlainTextEdit()
        self.observaciones_cliente.setTabChangesFocus(True)
        self.observaciones_cliente.setPlaceholderText(
            "Observaciones a el huesped...")

        self.observaciones_cliente.setObjectName("observaciones_cliente")
        layout.addRow(self.observaciones_cliente)

        self.breputacion = QPushButton()
        self.breputacion .setCursor(
            QCursor(Qt.PointingHandCursor))
        self.breputacion.setFixedWidth(120)
        self.breputacion.clicked.connect(self.bcliente_reputacion)
        self.breputacion.setToolTip('Modificar Reputación')
        self.breputacion.setObjectName("reputacion")

        self.bhistorial = QPushButton()
        self.bhistorial.setCursor(QCursor(Qt.PointingHandCursor))
        self.bhistorial.setCursor(QCursor(Qt.PointingHandCursor))
        self.bhistorial.setStyleSheet("border-radius: 2px; font-size: 14px;")
        self.bhistorial.clicked.connect(self.cliente_table)
        self.bhistorial.setObjectName("historial")

        layout.addRow(self.breputacion, self.bhistorial)

        # ----

        new_tab.setLayout(layout)
        self.tab_huespedes.addTab(new_tab, f"P{index + 1}")
        self.tab_huespedes.setCurrentIndex(index)

    def use_voucher(self):

        # 1. Validación de costo inicial
        if self.costo_dolar.text() == "0$":
            misk().errorMSG("No se puede usar un voucher cuando el costo es 0.00$", "Error")
            return

        # 2. Conexión a la Base de Datos
        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )
        c = db.cursor()

        # 3. Buscar y Validar Voucher
        c.execute(
            f"SELECT tipo, valor FROM vouchers WHERE codigo = %s", (self.input_voucher.text(),))
        data = c.fetchone()

        if not data:
            self.valor_voucher.setVisible(False)
            misk().errorMSG("Voucher no existe", "No Existe")
            c.close()
            db.close()
            return

        self.valor_voucher.setVisible(True)

        if self.valor_voucher.text():
            misk().errorMSG("Ya se ha aplicado un voucher", "Voucher Aplicado")
            c.close()
            db.close()
            return

        # Extraer detalles del voucher
        voucher_tipo = data[0]
        voucher_valor = data[1]

        # --- DETERMINACIÓN DEL CAMINO: ¿Existe Estancia Activa? ---
        id_estancia = getattr(self, 'id_estancia', None)
        hab_num = getattr(self, 'hab_num', None)
        result_costo = None
        id_estancia_habitacion = None

        # Solo buscamos si tenemos identificadores válidos
        if id_estancia and hab_num:
            # Búsqueda 1: Fila activa
            c.execute(
                "SELECT costo, id FROM estancia_habitaciones WHERE id_estancia = %s AND habitacion = %s AND fecha_fin_real IS NULL", (id_estancia, hab_num))
            result_costo = c.fetchone()

            if not result_costo:
                # Búsqueda 2: Última fila (por si ya se cerró)
                c.execute(
                    "SELECT costo, id FROM estancia_habitaciones WHERE id_estancia = %s AND habitacion = %s ORDER BY fecha_inicio DESC LIMIT 1", (id_estancia, hab_num))
                result_costo = c.fetchone()

        # --- CAMINO 1: ACTUALIZACIÓN PERSISTENTE (Estancia Encontrada) ---
        if result_costo:

            # Usar costo de la DB como fuente de verdad
            costo_actual_db, id_estancia_habitacion = result_costo
            costo_actual_num = float(costo_actual_db)

            log_tipo = "voucher"  # Tipo de log original
            log_identificador = hab_num

        # --- CAMINO 2: ACTUALIZACIÓN LOCAL EN UI (Estancia NO Encontrada) ---
        else:

            # Usar costo de la interfaz
            try:
                costo_actual_str_ui = self.costo_dolar.text().replace('$', '').strip()
                costo_actual_num = float(costo_actual_str_ui)
            except ValueError:
                misk().errorMSG("El formato del costo actual no es válido. Debe ser un número.", "Error Interno")
                c.close()
                db.close()
                return

            log_tipo = "voucher_ui_local"  # Nuevo tipo de log para distinguirlo
            log_identificador = hab_num if hab_num else "VENTA_RAPIDA"

        # --- Cálculo del Nuevo Precio (Común para ambos caminos) ---
        price = 0.0

        if voucher_tipo == '$':
            price = costo_actual_num - voucher_valor
        elif voucher_tipo == '%':
            price = costo_actual_num - (costo_actual_num * voucher_valor / 100)

        # Asegurar que el precio no sea negativo
        if price < 0:
            price = 0.0

        # --- Ejecución de Updates en DB (Condicional) ---
        if result_costo:
            # 1. Actualizar el costo en estancia_habitaciones
            c.execute("UPDATE estancia_habitaciones SET costo = %s WHERE id = %s",
                      (price, id_estancia_habitacion))

            # 2. Actualizar el voucher en estancias
            c.execute("UPDATE estancias SET voucher = %s WHERE id_estancia = %s",
                      (self.input_voucher.text(), id_estancia))

        misk().registrar_log("log_tipo", self.input_atendido_por.text(),
                             f"voucher {self.input_voucher.text()} usado ({costo_actual_num:.2f}$ -> {price:.2f}$)", log_identificador)
        db.commit()

        # --- Actualizar interfaz y Finalizar (Común para ambos caminos) ---
        self.costo_dolar.setText(f"{price:.2f}$")  # Se usa el precio calculado
        self.valor_voucher.setText(f"-{voucher_valor}{voucher_tipo}")
        self.input_voucher.setEnabled(False)
        self.price_calculation()

        misk().informationMSG("Voucher aplicado exitosamente", "Voucher aplicado")

        c.close()
        db.close()

    def cancel_voucher(self):
        print(self.valor_voucher.text())
        if self.valor_voucher.text() == "":
            misk().errorMSG("No ha agregado ningun voucher aún", "Error")
            return

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        # --- Obtener precio original de la habitación ---
        c.execute(
            f"SELECT parcial, hospedaje FROM habitaciones WHERE habitacion = %s", (self.hab_num,))
        result_hab = c.fetchone()
        if not result_hab:
            misk().errorMSG("No se encontró la habitación.", "Error Interno")
            c.close()
            db.close()
            return

        if self.estadia_type.text() == "parcial":
            price_original = result_hab[0]
        else:  # hospedaje
            price_original = result_hab[1] * self.input_estadia_dias.value()

        # --- Actualizar la base de datos ---
        # 1. Actualizar el costo en estancia_habitaciones (restaurar al original)
        # Asumimos que el descuento aplica a la habitación actual
        c.execute("UPDATE estancia_habitaciones SET costo = %s WHERE id_estancia = %s AND habitacion = %s AND fecha_fin_real IS NULL",
                  (price_original, self.id_estancia, self.hab_num))

        # 2. Actualizar el voucher en estancias a NULL
        c.execute(
            "UPDATE estancias SET voucher = NULL WHERE id_estancia = %s", (self.id_estancia,))

        misk().registrar_log("voucher", self.input_atendido_por.text(),
                             f"voucher {self.input_voucher.text()} eliminado ({self.costo_dolar.text()} -> {price_original}$)", self.hab_num)

        db.commit()

        # --- Actualizar interfaz ---
        self.costo_dolar.setText(f"{price_original}$")
        self.price_calculation()  # Recalcular totales si es necesario

        c.close()
        db.close()

        self.input_voucher.setText("")
        self.valor_voucher.setText("")
        self.input_voucher.setEnabled(True)
        self.valor_voucher.setVisible(False)

        misk().informationMSG("Voucher eliminado exitosamente", "Voucher eliminado")

    def trash(self):
        question = misk().questionMSG(
            # Cambié el mensaje
            "Esta seguro de borrar permanentemente esta estancia?", "Borrar Estancia")

        if question == QMessageBox.Ok:

            text, ok = QInputDialog.getText(
                # Cambié el mensaje
                self,  'Cancelar Estancia', 'Escriba el motivo por el que ha cancelado la estancia')

            if ok == True:

                db = mc.connect(
                    host=host_ip,
                    user=database_user,
                    password=database_password,
                    database="esmeralda_software",
                    use_pure=True
                )

                c = db.cursor()

                # --- Usar self.id_estancia directamente ---
                id_estancia = self.id_estancia

                # --- Marcar la estancia como cancelada ---
                # Actualizar estado, fecha_fin_real y observaciones
                c.execute("UPDATE estancias SET estado = 'cancelada', fecha_fin_real = NOW(), observaciones = CONCAT(observaciones, ' | Cancelada: ', %s) WHERE id_estancia = %s", (text.lower(), id_estancia))

                c.execute(
                    "SELECT transaccion FROM historial_transacciones WHERE id_estancia = %s", (id_estancia,))
                transacciones_estancia = [row[0] for row in c.fetchall()]
                # Luego anulamos los montos de esas transacciones
                if transacciones_estancia:
                    # Construir la parte IN de la consulta con placeholders
                    format_strings = ','.join(
                        ['%s'] * len(transacciones_estancia))
                    c.execute(
                        f"UPDATE historial_pagos SET monto = NULL WHERE id_historial IN ({format_strings})", transacciones_estancia)
                c.execute(
                    # Se quitó el filtro por habitación específica
                    "UPDATE estancia_habitaciones SET fecha_fin_real = NOW() WHERE id_estancia = %s AND fecha_fin_real IS NULL", (id_estancia,))

                c.execute(
                    # Asegura que es la habitación correcta de la estancia cancelada
                    f"UPDATE current_habitaciones SET id_estancia = NULL, estado = 'sucia' WHERE habitacion = %s AND id_estancia = %s", (self.hab_num, id_estancia))

                c.execute(
                    f"DELETE FROM current_personas WHERE identificador = '{self.id_estancia}'")

                # ------------------------------------ Add to Log -----------------------------------------

                db.commit()
                

                misk().registrar_log("estancia", self.input_atendido_por.text(),
                                     f"estancia cancelada debido a que {text.lower()}", id_estancia)

                self.temp_closeEvent = False
                self.close()
                self.temp_closeEvent = True
                self.reset_datos()

                c.close()
                db.close()

                misk().tg_message(
                    f"{self.input_atendido_por.text()} ha cancelado la estancia {id_estancia} (habitación {self.hab_num}) debido a que {text.lower()} 🗑️❌")

                misk().informationMSG("Estancia cancelada exitosamente",
                                      "Estancia cancelada")  # Cambié el mensaje

    def hab_transacciones(self):
        data = f'''
                SELECT
                    eh.habitacion AS Hab,
                    e.usuario_registro AS Usuario, -- o ht.usuario si se quiere el usuario de la transacción específica
                    e.tipo_estadia AS Estadia,
                    DATE_FORMAT(e.fecha_inicio_real, '%H:%i %d-%m-%Y') AS Entrada,
                    DATE_FORMAT(eh.fecha_fin_planificada, '%H:%i %d-%m-%Y') AS Salida_Planif,
                    DATE_FORMAT(eh.fecha_fin_real, '%H:%i %d-%m-%Y') AS Salida_Real,
                    CASE
                        WHEN eh.fecha_fin_real IS NOT NULL THEN
                            TIMESTAMPDIFF(SECOND, e.fecha_inicio_real, eh.fecha_fin_real) DIV 3600
                        ELSE
                            TIMESTAMPDIFF(SECOND, e.fecha_inicio_real, eh.fecha_fin_planificada) DIV 3600
                    END AS Duración_Horas,
                    CASE
                        WHEN eh.fecha_fin_real IS NOT NULL THEN
                            CONCAT(TIMESTAMPDIFF(SECOND, e.fecha_inicio_real, eh.fecha_fin_real) DIV 3600, 'h ',
                                (TIMESTAMPDIFF(SECOND, e.fecha_inicio_real, eh.fecha_fin_real) % 3600) DIV 60, 'm')
                        ELSE
                            CONCAT(TIMESTAMPDIFF(SECOND, e.fecha_inicio_real, eh.fecha_fin_planificada) DIV 3600, 'h ',
                                (TIMESTAMPDIFF(SECOND, e.fecha_inicio_real, eh.fecha_fin_planificada) % 3600) DIV 60, 'm')
                    END AS Duración_Formateada
                FROM historial_transacciones ht
                JOIN estancias e ON ht.id_estancia = e.id_estancia
                JOIN estancia_habitaciones eh ON e.id_estancia = eh.id_estancia
                WHERE eh.habitacion = '{self.hab_num}' -- Filtrar por la habitación específica (validada)
                ORDER BY e.fecha_inicio_real DESC; -- Ordenar por entrada real de la estancia
                '''
        self.TableViewData.open_table_view_data(data)

    def precensia_huesped_tabla(self):
        data = f'''
                SELECT
                    datetime as Fecha,
                    usuario as Usuario,
                    identificador AS Hab,
                    porton as Porton,
                    observaciones as Observaciones
                FROM historial_acceso 
                WHERE identificador = '{self.id_estancia}' 
                ORDER BY datetime DESC;
                '''
        self.TableViewData.open_table_view_data(data)

    def cliente_table(self):
        tab = self.tab_huespedes.widget(self.tab_huespedes.currentIndex())

        cedula_cliente = tab.findChild(QLineEdit, "input_cedula").text()

        if cedula_cliente == "":
            misk().errorMSG("Ingrese la cédula del huésped para poder su registro", "Ingresar cédula")
            return

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        query_metodos_pago = f"""
            SELECT DISTINCT hp.descripcion
            FROM historial_pagos hp
            JOIN historial_transacciones ht ON hp.id_historial = ht.transaccion
            JOIN estancias e ON ht.id_estancia = e.id_estancia
            JOIN estancia_clientes ec ON e.id_estancia = ec.id_estancia
            WHERE ec.cliente = '{cedula_cliente}'
        """
        c.execute(query_metodos_pago)
        metodos_pago = [row[0] for row in c.fetchall()]

        sum_cases_parts = [
            f"SUM(CASE WHEN hp.descripcion = '{metodo}' THEN hp.monto ELSE 0 END) AS `{metodo}`" for metodo in metodos_pago]
        sum_columns_str = ",\n    ".join(sum_cases_parts)

        query_parts_final = [
            "SELECT",
            "    eh.habitacion AS Hab,",  # Mapeado: ih.habitacion -> eh.habitacion
            # Mapeado: ih.usuario -> e.usuario_registro
            "    e.usuario_registro AS Usuario,",
            "    e.tipo_estadia AS Estadia,",  # Mapeado: ih.estadia -> e.tipo_estadia
            "    ec.cliente,",  # Mapeado: hc.cliente -> ec.cliente
        ]

        if sum_columns_str:
            query_parts_final.append(f"    {sum_columns_str},")
        else:
            # Si no hay métodos de pago registrados
            query_parts_final.append("    0 AS TotalMetodos,")

        query_parts_final.extend([
            "    SUM(hp.monto) AS TotalPagado",  # Mantenido igual
            # Cambiado: historial_clientes hc -> estancia_clientes ec
            "FROM estancia_clientes ec",
            # Cambiado: historial_transacciones ih -> estancias e
            "JOIN estancias e ON ec.id_estancia = e.id_estancia",
            # Unión para encontrar pagos
            "JOIN historial_transacciones ht ON e.id_estancia = ht.id_estancia",
            # Unión para encontrar habitación
            "JOIN estancia_habitaciones eh ON e.id_estancia = eh.id_estancia",
            # Asumiendo pagos en la transacción contenedora
            "LEFT JOIN historial_pagos hp ON ht.transaccion = hp.id_historial",
            # Cambiado: hc.cliente -> ec.cliente
            f"WHERE ec.cliente = '{cedula_cliente}'",
            # Agrupamos por estancia y por uso de habitación (por si el cliente cambió de cuarto dentro de una estancia)
            # Agrupar por estancia y por uso de habitación
            "GROUP BY e.id_estancia, eh.id, ec.cliente",
            # Mapeado: ORDER BY ih.dtentrada DESC (de la vieja consulta)
            # A: ORDER BY e.fecha_inicio_real DESC o eh.fecha_inicio DESC (elegir uno, fecha_inicio_real parece más general)
            "ORDER BY e.fecha_inicio_real DESC;"  # Ordenar por entrada real de la estancia
        ])

        data = "\n".join(query_parts_final)

        # Cerrar cursores y conexión antes de llamar a la vista
        c.close()
        db.close()

        # Llamar a la función original con la consulta SQL completa
        # Asumiendo que 'cedula_cliente' es segura de inyectar aquí.
        self.TableViewData.open_table_view_data(data)

    def set_days(self):
        if self.bingresar.isEnabled():
            self.costo_dolar.setText("0$")

            self.estadia_type.setText("???")
            self.FRcosto.setStyleSheet('''
                background-color: rgb(40, 40, 40);
                border-radius: 4px;
                ''')

    def edad_resta(self):
        today = QDate.currentDate()
        fecha = QDate.fromString(self.input_fnacimiento.text(), "dd-MM-yyyy")

        result = fecha.daysTo(today)/365

        self.fnacimiento.setText(f"Edad: {(math.floor(result))}")
        self.input_telefono.setFocus()

    def next_line(self):
        if str(self.sender().objectName()) == "input_nombre":
            self.input_fnacimiento.setFocus()

        else:
            print(self.sender().objectName())

# ---------------------------------------------------------------------------------------------------

    def cliente_existe(self):

        tab = self.tab_huespedes.widget(self.tab_huespedes.currentIndex())

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        # --- Consulta actualizada para usar estancia_clientes ---
        c.execute(
            f'''
            SELECT
                c.cedula,
                c.nombre,
                DATE_FORMAT(c.fecha_nacimiento, '%d-%m-%Y'),
                c.nacionalidad,
                c.estado_civil,
                c.direccion,
                c.telefono,
                c.profesion,
                c.reputacion,
                c.observaciones,
                
                (SELECT COUNT(*)
                FROM estancia_clientes ec
                JOIN estancias e ON ec.id_estancia = e.id_estancia
                WHERE ec.cliente = c.cedula) AS veces_repetido -- Opcional: excluir canceladas
            FROM clientes c
            WHERE c.cedula = %s
            ''', (tab.findChild(QLineEdit, "input_cedula").text(),)  # Usar placeholder
        )
        cliente = c.fetchone()

        c.execute(
            "SELECT config_value FROM config WHERE config_key = 'tv_display' OR config_key = 'tv_display_url'")
        tv_display = tuple(item[0] for item in c.fetchall())

        if int(tv_display[0]):
            endpoint = f"{tv_display[1]}/api/show/video"
            payload = {"video_name": "anuncio.mp4"}
            try:
                response = requests.post(endpoint, json=payload)
                response.raise_for_status()
                print(
                    f"   -> Servidor respondió: {response.json()['message']}")
            except requests.exceptions.RequestException as e:
                print(f"   -> Error: {e}")

        c.close()
        db.close()

        if cliente is None:
            misk().errorMSG("Huesped no existe en el sistema", "Nuevo Huesped")
            self.cliente_reputacion(
                self.tab_huespedes.currentIndex(), "positivo")
            tab.findChild(QLineEdit, "input_nombre").setFocus()

        else:
            tab.findChild(QLineEdit, "input_cedula").setText(str(cliente[0]))
            tab.findChild(QLineEdit, "input_nombre").setText(
                str(cliente[1].title()))
            tab.findChild(QDateEdit, "input_fnacimiento").setDate(
                QDate.fromString(cliente[2], "dd-MM-yyyy"))
            tab.findChild(QComboBox, "input_nacionalidad").setCurrentText(
                str(cliente[3]))
            tab.findChild(QComboBox, "input_estado_civil").setCurrentText(
                str(cliente[4]))
            tab.findChild(QLineEdit, "input_telefono").setText(str(cliente[6]))
            tab.findChild(QComboBox, "input_profesion").setCurrentText(
                str(cliente[7]))
            tab.findChild(QPlainTextEdit, "observaciones_cliente").setPlainText(
                cliente[9])
            tab.findChild(QPushButton, "historial").setText(
                # veces_repetido ahora viene de estancia_clientes
                f"Vino {cliente[10]} veces")

            self.input_procedencia.setCurrentText(str(cliente[5]))

            self.cliente_reputacion(
                self.tab_huespedes.currentIndex(), cliente[8])

            self.bparcial.setFocus()
            if cliente[8] == "negativo":
                misk().errorMSG("El cliente ingresado tiene reputación negativa, siga a su propio riesgo",
                                "Reputación Negativa")


# ---------------------------------------------------------------------------------------------------

    def bcliente_reputacion(self):

        tab = self.tab_huespedes.widget(self.tab_huespedes.currentIndex())

        if tab.findChild(QPushButton, "reputacion").text().lower() == "positivo":
            question = misk().questionMSG(
                "¿Desea cambiar la reputación del cliente a negativa?", "Reputación")

            if question == QMessageBox.Ok:
                self.cliente_reputacion(
                    self.tab_huespedes.currentIndex(), "negativo")

        elif tab.findChild(QPushButton, "reputacion").text().lower() == "negativo":
            question = misk().questionMSG(
                "¿Desea cambiar la reputación del cliente a positiva?", "Reputación")

            if question == QMessageBox.Ok:
                self.cliente_reputacion(
                    self.tab_huespedes.currentIndex(), "positivo")

    def cliente_reputacion(self, tab, reputacion):

        tab = self.tab_huespedes.widget(tab)

        if reputacion == "positivo":
            tab.findChild(QPushButton, "reputacion").setText("positivo")
            tab.findChild(QPushButton, "reputacion").setStyleSheet('''
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 #11998E, stop:0 #38ef7d);
                    color: rgb(242, 242, 242);
                    border-radius: 2px;
                    font-size: 14px;
                    font-weight: bold;
                    ''')
            self.breputacion.setEnabled(True)

        elif reputacion == "negativo":
            tab.findChild(QPushButton, "reputacion").setText("negativo")
            tab.findChild(QPushButton, "reputacion").setStyleSheet('''
                                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 rgb(150, 2, 2), stop:0 rgb(242, 5, 5));
                                color: rgb(242, 242, 242);
                                border-radius: 2px;
                                font-size: 14px;
                                font-weight: bold;
                                ''')
            self.breputacion.setEnabled(True)

        elif reputacion == "bloqueado":
            tab.findChild(QPushButton, "reputacion").setText("Reputación")
            tab.findChild(QPushButton, "reputacion").setStyleSheet('''
                                background-color:black;
                                font-size: 14px;
                                font-weight: bold;
                                ''')
            self.breputacion.setEnabled(False)

# ---------------------------------------------------------------------------------------------------

    def tipo_de_tiempo(self):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        price = 0

        c.execute(
            f"SELECT * FROM habitaciones WHERE habitacion = '{self.hab_num}'")
        data = c.fetchone()

        self.input_estadia_dias.setEnabled(True)
        self.input_estadia_dias.setMinimum(1)

        if self.sender().text() == "Parcial":

            self.input_estadia_dias.setEnabled(False)
            self.input_estadia_dias.setMinimum(0)

            c.execute(
                "SELECT config_value FROM config WHERE config_key = 'tiempo_parcial'")
            tiempo_parcial = int(c.fetchone()[0])*3600

            if self.input_fentrada.dateTime().addSecs(tiempo_parcial).date() > self.input_fentrada.date():
                self.input_estadia_dias.setValue(1)
            else:
                self.input_estadia_dias.setValue(0)

            self.input_fsalida.setDateTime(
                self.input_fentrada.dateTime().addSecs(tiempo_parcial))

            price = data[2]

            c.execute(
                f'''SELECT id_estancia 
                FROM estancia_habitaciones 
                WHERE habitacion = {self.hab_num}
                AND fecha_inicio  >= '{self.input_fentrada.dateTime().toPython()}'
                AND fecha_fin_planificada  <= '{self.input_fsalida.dateTime().toPython()}'
                ''')
            reservada = c.fetchone()

            if reservada:
                print(reservada)
                misk().errorMSG(f"La habitación ya habia sido reservada desde el {reservada[0]} hasta el {reservada[1]}, por favor seleccione otra fecha de entrada",
                                "Habitación ya reservada")
                self.set_days()
                return

            self.estadia_type.setText("parcial")
            self.FRcosto.setStyleSheet('''
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(180, 20, 20), stop:1 rgb(60, 0, 0));
            border-radius: 4px;
            ''')

        elif self.sender().text() == "Pasar a Hospedaje":

            question = misk().questionMSG(
                "Desea pasar de parcial a hospedaje?", "Extender Estadia")

            if question == QMessageBox.Ok:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.bhospedaje.setEnabled(False)
                self.bhospedaje.setText("Invalido")
                self.bhospedaje.setStyleSheet(
                    "background-color:black; font-size: 14px;")

                price = data[3]

                c.execute(
                    f"UPDATE estancia_habitaciones SET fecha_fin_planificada = '{self.input_fsalida.date().toPython()} 13:00:00' WHERE id_estancia = '{self.id_estancia}'")

                c.execute(
                    f"UPDATE estancias SET tipo_estadia = 'hospedaje', fecha_fin_planificada = '{self.input_fsalida.date().toPython()} 13:00:00' WHERE id_estancia = '{self.id_estancia}'")

                c.execute(
                    f"UPDATE current_habitaciones SET estado = 'hospedaje' WHERE habitacion = '{self.hab_num}'")

                # ------------------------------------ Add to Log -----------------------------------------

                misk().registrar_log("transaccion", self.input_atendido_por.text(),
                                     "habitacion pasó de parcial a hospedaje", self.hab_num)

                self.estadia_type.setText("hospedaje")
                self.FRcosto.setStyleSheet('''
                background-color:  qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(189, 195, 199), stop:1 rgb(36, 54, 70));
                border-radius: 4px;
                ''')

                QApplication.restoreOverrideCursor()
                misk().informationMSG(
                    f"La habitación {self.hab_num} pasó de ser Parcial a Hospedaje exitosamente (la diferencia son {str(int(data[3]) - int(data[2]))}$)", "Parcial a Hospedaje")
                misk().tg_message(
                    f"La habitación <b>{self.hab_num}</b> pasó de ser Parcial a Hospedaje <b>(la diferencia son {str(int(data[3]) - int(data[2]))}$)</b>")

        elif self.sender().text() == "Hospedaje":

            self.input_fsalida.setTime(QTime(13, 0))

            day_start = 0

            if self.input_fentrada.time() <= QTime(6, 0):
                day_start = -1

            if self.input_estadia_dias == 0:
                self.input_estadia_dias.setValue(1)

            self.input_fsalida.setDate(self.input_fentrada.date().addDays(
                self.input_estadia_dias.value() + day_start))

            c.execute(
                f'''SELECT id_estancia 
                FROM estancia_habitaciones 
                WHERE habitacion = '{self.hab_num}'
                AND fecha_inicio  >= '{self.input_fentrada.dateTime().toPython()}'
                AND fecha_fin_planificada  <= '{self.input_fsalida.dateTime().toPython()}'
                ''')
            reservada = c.fetchone()

            if reservada:
                print(reservada)
                misk().errorMSG(f"La habitación ya habia sido reservada desde el {reservada[0]} hasta el {reservada[1]}, por favor seleccione otra fecha de entrada",
                                "Habitación ya reservada")
                self.set_days()
                return

            price = float(data[3]) * self.input_estadia_dias.value()

            self.estadia_type.setText("hospedaje")
            self.FRcosto.setStyleSheet('''
            background-color:  qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(189, 195, 199), stop:1 rgb(36, 54, 70));
            border-radius: 4px;
            ''')

            dtentrada = QDateTime.fromString(
                f"{self.input_fentrada.text()}", "hh:mm / dd-MM-yyyy").toPython()
            dtsalida = QDateTime.fromString(
                f"{self.input_fsalida.text()}", "hh:mm / dd-MM-yyyy").toPython()

        self.costo_dolar.setText(f"{price}$")
        self.price_calculation()
        self.input_FP1.setFocus()

        db.commit()
        c.close()
        db.close()

# ---------------------------------------------------------------------------------------------------

    def price_calculation(self):

        try:
            FP_dolar_to_bs = [
                [self.input_FP1.value(), self.FP1_bs],
                [self.input_FP2.value(), self.FP2_bs],
                [self.input_FP3.value(), self.FP3_bs],
                [self.input_FP4.value(), self.FP4_bs],
                [self.input_extra1.value(), self.extra1_bs],
                [self.input_extra2.value(), self.extra2_bs],
                [self.input_extra3.value(), self.extra3_bs]]

            for i in FP_dolar_to_bs:
                int_FP = i[0] * self.dolarprice
                i[1].setText(str(round(int_FP, 2)))

            int_FP = float(self.costo_dolar.text().replace(
                '$', '')) * float(self.dolarprice)
            self.costo_bs.setText(str(round(int_FP, 2)) + " Bs")

        except ValueError as error:
            print(error)

        FP_dolar = [self.input_FP1, self.input_FP2,
                    self.input_FP3, self.input_FP4]

        FP_bs = [self.FP1_bs, self.FP2_bs, self.FP3_bs, self.FP4_bs]

        extra_dolar = [self.input_extra1,
                       self.input_extra2, self.input_extra3]

        self.extra_bs = [self.extra1_bs, self.extra2_bs, self.extra3_bs]

        try:
            for i in FP_dolar:

                dolar_int = [i.value() for i in FP_dolar]
                FPdolar_resultado = float(
                    self.costo_dolar.text().replace('$', '')) - sum(dolar_int)

            self.faltan_dolar.setText(str(FPdolar_resultado) + "$")

            for i in FP_bs:

                bs_int = [float(i.text()) for i in FP_bs]
                FPbs_resultado = float(
                    self.costo_bs.text().replace('Bs', '')) - sum(bs_int)

            self.faltan_bs.setText(str(round(FPbs_resultado, 2)) + " Bs")

            for i in extra_dolar:

                extradolar_int = [i.value() for i in extra_dolar]
                total_dolar_resultado = sum(
                    dolar_int) + sum(extradolar_int)

            for i in self.extra_bs:

                extrabs_float = [float(i.text()) for i in self.extra_bs]
                total_bs_resultado = sum(
                    bs_int) + sum(extrabs_float)

            self.total_dolar.setText(str(total_dolar_resultado) + "$")

            self.total_bs.setText(str(round(total_bs_resultado, 2)) + " Bs")

        except ValueError as error:
            print(error)

        finally:
            if self.faltan_dolar.text() != "0.0$":
                self.faltan_dolar.setStyleSheet('''
                color: rgb(242, 5, 5);
                font-size: 26px;
                font-weight: bold;''')
                self.faltan_bs.setStyleSheet('''
                color: rgb(242, 5, 5);
                font-size: 20px;
                font-weight: bold;''')
            else:
                self.faltan_dolar.setStyleSheet('''
                color: rgb(40, 190, 100);
                font-size: 26px;
                font-weight: bold;''')
                self.faltan_bs.setStyleSheet('''
                color: rgb(40, 190, 100);
                font-size: 20px;
                font-weight: bold;''')


# ---------------------------------------------------------------------------------------------------

    def dialog_mover_reservacion(self):
        """Abre el diálogo para mover o cancelar una reserva."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Mover Reservación")

        layout = QVBoxLayout(dlg)

        dtreservacion = QLabel(self)
        dtreservacion.setText(
            "Si desea mover Reservación, seleccione dia y hora a moverla")
        layout.addWidget(dtreservacion)

        # Asumiendo que self.dtmover_reservacion se crea aquí
        self.dtmover_reservacion = QDateTimeEdit(self)
        self.dtmover_reservacion.setCalendarPopup(True)
        self.dtmover_reservacion.calendarWidget().setLocale(QLocale(QLocale.Spanish))
        # Configurar rango de fechas razonable
        self.dtmover_reservacion.setDateRange(
            QDate.currentDate(), QDate.currentDate().addMonths(2))
        # Establecer la fecha/hora actual como predeterminada
        self.dtmover_reservacion.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.dtmover_reservacion)

        bmover = QPushButton(self)
        bmover.setText("Mover")
        # Conectar señal al método de la instancia principal (self)
        bmover.clicked.connect(lambda: self.mover_reservacion(dlg))
        bmover.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(bmover)

        bcancelar = QPushButton(self)
        bcancelar.setText("Cancelar Reservación")
        # Conectar señal al método de la instancia principal (self)
        bcancelar.clicked.connect(lambda: self.cancelar_reservacion(dlg))
        bcancelar.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(bcancelar)

        # Botón para cerrar el diálogo sin acción
        bcerrar = QPushButton(self)
        bcerrar.setText("Cerrar")
        bcerrar.clicked.connect(dlg.close)
        layout.addWidget(bcerrar)

        dlg.exec()

    def obtener_reserva_id_para_habitacion_y_fecha(self, habitacion, fecha_referencia):
        """
        Obtiene el reserva_id de una reserva activa para una habitación específica
        que tenga una fecha de entrada futura cercana a una fecha dada.
        """
        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )
        c = db.cursor()

        # Buscar reserva activa para la habitación con dtentrada >= fecha_referencia (o NOW())
        # y que esté cerca de la fecha_referencia para evitar coincidencias ambiguas.
        # Ajusta la lógica según tus criterios de "reserva actual".
        query = '''
            SELECT reserva_id FROM reservaciones
            WHERE habitacion = %s
            AND estado = 'activa'
            AND dtentrada >= %s
            ORDER BY ABS(TIMESTAMPDIFF(SECOND, dtentrada, %s))
            LIMIT 1
        '''
        c.execute(query, (habitacion, fecha_referencia, fecha_referencia))
        result = c.fetchone()
        reserva_id = result[0] if result else None

        c.close()
        db.close()
        return reserva_id

    def cancelar_reservacion(self, dialog):
        """
        Cancela una reserva existente.
        Asume que `self.reserva_id` contiene el ID de la reserva a cancelar.
        """
        # --- Conexión a la base de datos ---
        # Asumiendo que host_ip, database_user, database_password están definidos globalmente o como atributos de clase
        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        # --- 1. Actualizar datos del cliente principal ---
        # Asumiendo que hay un cliente principal y sus datos están en los campos de la UI
        # Si `self.cliente_principal_cedula` o similar existe, úsalo.
        # Si no, busca la cédula en el primer tab de huéspedes.
        cliente_principal_cedula = None
        tab_cliente_principal = self.tab_huespedes.widget(
            0) if self.tab_huespedes.count() > 0 else None
        if tab_cliente_principal:
            cliente_principal_cedula = tab_cliente_principal.findChild(
                QLineEdit, "input_cedula").text()

        if cliente_principal_cedula:
            # Actualizar cliente si existe (por si se modificaron datos antes de cancelar)
            query_cliente = '''
                UPDATE clientes SET
                    nombre = %s,
                    fecha_nacimiento = %s,
                    nacionalidad = %s,
                    estado_civil = %s,
                    direccion = %s, -- Dirección puede ser procedencia
                    telefono = %s,
                    profesion = %s,
                    reputacion = %s, -- Asumiendo que reputacion viene de un botón o campo
                    observaciones = %s
                WHERE cedula = %s
            '''
            params_cliente = (
                tab_cliente_principal.findChild(
                    QLineEdit, "input_nombre").text(),
                tab_cliente_principal.findChild(
                    QDateEdit, "input_fnacimiento").date().toPython(),
                tab_cliente_principal.findChild(
                    QComboBox, "input_nacionalidad").currentText(),
                tab_cliente_principal.findChild(
                    QComboBox, "input_estado_civil").currentText(),
                self.input_procedencia.currentText(),  # Dirección/procedencia
                tab_cliente_principal.findChild(
                    QLineEdit, "input_telefono").text(),
                tab_cliente_principal.findChild(
                    QComboBox, "input_profesion").currentText(),
                # O el valor del campo si no es un botón
                tab_cliente_principal.findChild(
                    QPushButton, "reputacion").text(),
                tab_cliente_principal.findChild(
                    QPlainTextEdit, "observaciones_cliente").toPlainText(),
                cliente_principal_cedula
            )
            c.execute(query_cliente, params_cliente)
        else:
            print(
                "Advertencia: No se encontró cédula de cliente principal para actualizar.")

        # --- 2. Cancelar la reserva en la tabla 'reservaciones' ---
        # Necesitamos identificar la reserva a cancelar.
        # Asumiendo que tienes un atributo `self.reserva_id` que identifica la reserva actual.
        if not hasattr(self, 'reserva_id'):
            misk().errorMSG("ID de reserva no disponible. No se puede cancelar la reserva.", "Error Interno")
            print("ERROR: self.reserva_id no está definido.")
            c.close()
            db.close()
            if dialog:
                dialog.close()  # Cerrar el diálogo si se pasó como argumento
            return

        # Actualizar el estado de la reserva a 'cancelada'
        # Opcionalmente, puedes agregar una razón en observaciones
        # Puedes obtener esto de un input si lo deseas
        razon_cancelacion = "Cancelada por el usuario."
        query_cancelar_reserva = '''
            UPDATE reservaciones SET
                estado = 'cancelada',
                observaciones = CONCAT(IFNULL(observaciones, ''), ' | Cancelada: ', %s)
            WHERE reserva_id = %s
        '''
        params_cancelar_reserva = (razon_cancelacion, self.reserva_id)
        c.execute(query_cancelar_reserva, params_cancelar_reserva)

        # Verificar si se actualizó alguna fila
        if c.rowcount == 0:
            misk().errorMSG(
                f"No se encontró la reserva con ID {self.reserva_id} para cancelar.", "Error")
            c.close()
            db.close()
            if dialog:
                dialog.close()
            return

        # --- 3. Actualizar current_habitaciones si es relevante ---
        # Si `current_habitaciones` tiene una entrada para esta reserva (por ejemplo, estado='reservada'),
        # puedes limpiarla o ponerla como 'sucia'/'limpia'. Depende de tu lógica de negocio.
        # Asumiendo que `current_habitaciones.id_estancia` apunta a la reserva o está NULL,
        # y que `current_habitaciones.estado` puede ser 'reservada'.
        # Al cancelar, se podría poner `estado = NULL` o `estado = 'sucia'`.
        # Por ahora, asumiremos que se limpia el estado y se desasocia cualquier ID.
        # Si `current_habitaciones` usa `id_estancia`, y la reserva no tiene `id_estancia` aún, este paso puede no ser necesario.
        # Si se usó `id_estancia` provisionalmente, se debería limpiar.
        # Para simplificar, solo actualizamos el estado a NULL si la habitación coincide.
        # Asumiendo que `self.hab_num` es la habitación de la reserva.
        c.execute(
            f"UPDATE current_habitaciones SET estado = NULL, id_estancia = NULL WHERE habitacion = %s AND (estado = 'reservada' OR id_estancia = (SELECT id_estancia FROM reservaciones WHERE reserva_id = %s))",
            (self.hab_num, self.reserva_id)
        )
        # Nota: La subconsulta puede fallar si `id_estancia` en `reservaciones` es NULL.
        # Una alternativa más segura podría ser solo:
        # c.execute(f"UPDATE current_habitaciones SET estado = NULL, id_estancia = NULL WHERE habitacion = %s AND estado = 'reservada'", (self.hab_num,))

        # --- 4. Registrar en usuario_log ---
        c.execute(f'''
            INSERT INTO usuario_log (datetime, tipo, usuario, descripcion, identificador) VALUES 
            (CURRENT_TIMESTAMP,
            "reserva", 
            %s, 
            %s, 
            %s)''',
                  (
                      self.input_atendido_por.text() if hasattr(
                          self, 'input_atendido_por') and self.input_atendido_por.text() else 'Desconocido',
                      f"Reserva {self.hab_num} cancelada.",
                      self.hab_num
                  )
                  )

        # --- Confirmar cambios y cerrar conexiones ---
        db.commit()
        c.close()
        db.close()
        if dialog:
            dialog.close()  # Cerrar el diálogo si se pasó como argumento

        # --- Mensajes al usuario ---
        misk().tg_message(
            f"El cliente que reservó la habitación <b>{self.hab_num}</b> NO SE PRESENTÓ, por lo tanto la reserva fue <b>CANCELADA</b> y la habitación quedará como limpia.")

        # Si `self` es una ventana, ciérrala si es necesario
        # self.temp_closeEvent = False
        # self.close()
        # self.temp_closeEvent = True

        misk().informationMSG("Se ha cancelado la reserva exitosamente", "Reserva cancelada")

    def check_ingreso_cliente(self):
        tab1 = self.tab_huespedes.widget(self.tab_huespedes.currentIndex())

        huespedes_incompletos = False

        for i in range(1, self.tab_huespedes.count()):
            tab = self.tab_huespedes.widget(i)
            if tab.findChild(QLineEdit, "input_cedula").text():
                if not tab.findChild(QLineEdit, "input_nombre").text() or not tab.findChild(QComboBox, "input_estado_civil").currentText() or not tab.findChild(QLineEdit, "input_telefono").text():
                    huespedes_incompletos = True
                    break

        if not tab1.findChild(QLineEdit, "input_cedula").text() or not tab1.findChild(QLineEdit, "input_nombre").text() or not tab1.findChild(QComboBox, "input_estado_civil").currentText() or not tab1.findChild(QLineEdit, "input_telefono").text():
            misk().errorMSG("Rellene los datos del huesped", "Datos Huesped")

        elif huespedes_incompletos:
            misk().errorMSG("Rellene los datos de los acompañantes", "Datos Acompañantes")

        elif self.estadia_type.text() == "???":
            misk().errorMSG("Eliga si la habitación sera Parcial o Hospedaje", "Elegir Tipo de Estadia")

        elif self.input_fentrada.dateTime() > QDateTime.currentDateTime().addSecs(1800):

            if self.faltan_dolar.text() != "0.0$":
                misk().questionMSG(
                    "No ingreso ningun tipo de pago o no cobro la habitación por completo para realizar una reservación", "Pago incompleto")

            else:
                question = misk().questionMSG("¿Desea realizar una Reservación?", "Reservación")

                if question == QMessageBox.Ok:
                    self.ingreso_cliente(reservacion=True)

        elif self.faltan_dolar.text() != "0.0$":
            question = misk().questionMSG(
                "No ingreso ningun tipo de pago o no cobro la habitación por completo\naun así desea continuar?", "Tipo de pago")
            if question == QMessageBox.Ok:
                self.ingreso_cliente()

        else:
            self.ingreso_cliente()

    def ingreso_cliente(self, reservacion=False):
        # Asumiendo conexión y variables globales
        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )
        c = db.cursor()

        # --- 1. PREPARACIÓN DE DATOS ---
        transaccion = f"{self.input_fentrada.dateTime().toPython().strftime('%y%m%d%H%M%S')}{self.hab_num}"

        # Consultas previas (último turno, conteo)
        c.execute(
            "SELECT datetime FROM usuario_log WHERE descripcion = 'cambio de turno realizado' ORDER BY datetime DESC LIMIT 1")
        last_cambio_turno = c.fetchone()[0]

        c.execute(
            f"SELECT COUNT(id_estancia) FROM estancias WHERE fecha_inicio_real >= %s", (last_cambio_turno,))
        hab_count = c.fetchone()[0]

        formatted_output = f'<b>{hab_count+1})</b> Ingresó la habitación: {self.hab_num} \n<b>| C.I / RIF:</b> '

        # Fechas
        dt_inicio_planif = self.input_fentrada.dateTime().toPython()
        dt_inicio_real = self.input_fentrada.dateTime().toPython()
        dt_fin_planif = self.input_fsalida.dateTime().toPython()
        voucher = None if not self.valor_voucher.isVisible() else self.input_voucher.text()

        # --- 2. PASO CRÍTICO: INSERTAR CLIENTES PRIMERO ---
        # Recorremos los tabs ANTES de crear la estancia para asegurar que el cliente exista en la BD.
        # Esto evita el error de Foreign Key en clientes nuevos.

        query_cliente = '''
            INSERT IGNORE INTO clientes
            (cedula, nombre, fecha_nacimiento, nacionalidad, estado_civil, direccion, telefono, profesion, reputacion, observaciones) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        # Iteramos para guardar clientes
        for i in range(self.tab_huespedes.count()):
            tab = self.tab_huespedes.widget(i)
            cedula_cliente = tab.findChild(QLineEdit, "input_cedula").text()

            if cedula_cliente:
                params_cliente = (
                    cedula_cliente,
                    tab.findChild(QLineEdit, "input_nombre").text(),
                    tab.findChild(
                        QDateEdit, "input_fnacimiento").date().toPython(),
                    tab.findChild(
                        QComboBox, "input_nacionalidad").currentText(),
                    tab.findChild(
                        QComboBox, "input_estado_civil").currentText(),
                    self.input_procedencia.currentText(),
                    tab.findChild(QLineEdit, "input_telefono").text(),
                    tab.findChild(QComboBox, "input_profesion").currentText(),
                    tab.findChild(QPushButton, "reputacion").text(),
                    tab.findChild(QPlainTextEdit,
                                  "observaciones_cliente").toPlainText()
                )
                c.execute(query_cliente, params_cliente)

        # --- 3. CREAR LA ESTANCIA LÓGICA ---
        # Ahora es seguro insertar la estancia porque el cliente principal ya fue procesado arriba

        id_estancia = f"EST-{transaccion}"
        estado_estancia = 'activa' if not reservacion else 'reservada'

        cliente_principal_cedula = self.tab_huespedes.widget(
            0).findChild(QLineEdit, "input_cedula").text()

        query_estancia = '''
            INSERT INTO estancias
            (id_estancia, cliente_principal, estado, fecha_inicio_planificada, fecha_inicio_real, fecha_fin_planificada, voucher, observaciones, tipo_estadia, procedencia, destino, usuario_registro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        params_estancia = (
            id_estancia,
            cliente_principal_cedula,
            estado_estancia,
            dt_inicio_planif,
            dt_inicio_real,
            dt_fin_planif,
            voucher,
            self.observaciones_transaccion.toPlainText(),
            self.estadia_type.text(),
            self.input_procedencia.currentText(),
            self.input_destino.currentText(),
            self.input_atendido_por.text()
        )

        c.execute(query_estancia, params_estancia)

        # --- 4. CREAR USO DE HABITACIÓN ---
        id_estancia_habitacion = f"EH-{transaccion}"
        costo_habitacion = float(self.costo_dolar.text().replace('$', ''))

        query_estancia_habitacion = '''
            INSERT INTO estancia_habitaciones
            (id, id_estancia, habitacion, fecha_inicio, fecha_fin_planificada, costo)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        c.execute(query_estancia_habitacion, (id_estancia_habitacion, id_estancia,
                  self.hab_num, dt_inicio_real, dt_fin_planif, costo_habitacion))

        # --- 5. TRANSACCIÓN FINANCIERA ---
        c.execute('''
            INSERT INTO historial_transacciones
            (transaccion, id_estancia, usuario, fecha_registro)
            VALUES (%s, %s, %s, NOW())
        ''', (transaccion, id_estancia, self.input_atendido_por.text()))

        # --- 6. VINCULAR CLIENTES A LA ESTANCIA (estancia_clientes) ---
        # Volvemos a iterar (o podrías guardar los datos en una lista en el primer loop)
        # para llenar la tabla intermedia estancia_clientes y armar el reporte.

        query_estancia_cliente = '''
            INSERT INTO estancia_clientes (id, id_estancia, cliente) VALUES (%s, %s, %s)
        '''

        for i in range(self.tab_huespedes.count()):
            tab = self.tab_huespedes.widget(i)
            cedula_cliente = tab.findChild(QLineEdit, "input_cedula").text()

            if cedula_cliente:
                # Insertamos en la tabla de unión
                params_estancia_cliente = (
                    f"{id_estancia}{i}", id_estancia, cedula_cliente)
                c.execute(query_estancia_cliente, params_estancia_cliente)

                # Agregamos al reporte
                formatted_output += f"{cedula_cliente}\n"

        # --- 7. PAGOS Y LOGS (Igual que antes) ---
        formatted_output += f"| Tasa del Dolar: {self.dolarprice}\n| Metodos de Pago usados:\n"

        pagos = [
            ["hab", self.FP1.currentText(), self.input_FP1.value()],
            ["hab", self.FP2.currentText(), self.input_FP2.value()],
            ["hab", self.FP3.currentText(), self.input_FP3.value()],
            ["hab", self.FP4.currentText(), self.input_FP4.value()],
            ["extra", self.extra1.currentText(), self.input_extra1.value()],
            ["extra", self.extra2.currentText(), self.input_extra2.value()],
            ["extra", self.extra3.currentText(), self.input_extra3.value()],
        ]

        for pago in pagos:
            if pago[2]:
                c.execute(f'''
                    INSERT INTO historial_pagos (id, id_historial, tipo, descripcion, monto, tasa) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (f"{transaccion}{pago[1]}", transaccion, pago[0], pago[1], pago[2], self.dolarprice))
                formatted_output += f"    • <b>{pago[1]}:</b> {pago[2]}$ ({pago[2]*self.dolarprice}Bs)\n"

        if self.valor_voucher.isVisible():
            formatted_output += f"\n🎟 Se uso el voucher <b>{self.input_voucher.text()}</b> ({self.valor_voucher.text()})"
            misk().registrar_log("voucher", self.input_atendido_por.text(),
                                 f"voucher {self.input_voucher.text()} ({self.valor_voucher.text()}) fue usado", self.hab_num)

        if self.observaciones_transaccion.toPlainText():
            formatted_output += f"\n<b>Observaciones:</b> {self.observaciones_transaccion.toPlainText()}"

        # --- CIERRE Y CONFIRMACIONES (Manejo de Reserva / Update Habitacion) ---
        if reservacion:
            misk().registrar_log("reserva", self.input_atendido_por.text(),
                                 f"habitación reservada para el {dt_inicio_planif}", self.hab_num)
        else:
            c.execute('''UPDATE current_habitaciones SET estado = %s, id_estancia = %s WHERE habitacion = %s''',
                      (self.estadia_type.text(), id_estancia, self.hab_num))

            misk().registrar_log("transaccion", self.input_atendido_por.text(),
                                 "habitación ingresada", self.hab_num)

        db.commit()
        c.close()
        db.close()

        try:
            hilo_sync = threading.Thread(
                target=self.sincronizar_estancia_completa, args=(id_estancia,), daemon=True)
            hilo_sync.start()
        except Exception as e:
            print(f"⚠️ Error iniciando hilo sync: {e}")

        if not reservacion:
            persona = {'rol': "cliente", 'nombre': f'HAB {self.hab_num}',
                       'identificador': id_estancia}
            misk().abrir_porton(self.input_atendido_por.text(),
                                [persona], "ENTRADA", "VEHICULAR")

        self.close()

    def sincronizar_estancia_completa(self, id_estancia_local):
        print(f"🔄 Recopilando datos COMPLETOS para Sync: {id_estancia_local}")

        # Conexión a la BD Local
        try:
            db = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )
            # Usamos dictionary=True para trabajar cómodamente con nombres de columnas
            cur = db.cursor(dictionary=True)

            # ---------------------------------------------------------
            # 1. OBTENER CABECERA DE LA ESTANCIA
            # ---------------------------------------------------------
            sql_estancia = """
                SELECT 
                    id_estancia as id,
                    cliente_principal as cliente_cedula,
                    estado,
                    fecha_inicio_planificada as fecha_entrada,
                    fecha_fin_planificada as fecha_salida,
                    fecha_inicio_real,
                    fecha_fin_real,
                    usuario_registro,
                    voucher,
                    tipo_estadia,
                    observaciones
                FROM estancias WHERE id_estancia = %s
            """
            cur.execute(sql_estancia, (id_estancia_local,))
            estancia_data = cur.fetchone()

            if not estancia_data:
                print("⚠️ Estancia no encontrada localmente.")
                return

            # ---------------------------------------------------------
            # 2. OBTENER HABITACIÓN Y COSTO
            # ---------------------------------------------------------
            # Buscamos en 'estancia_habitaciones' la asignación más reciente
            # Esto maneja el caso de que el cliente haya sido movido
            cur.execute("""
                SELECT habitacion, costo 
                FROM estancia_habitaciones 
                WHERE id_estancia = %s 
                ORDER BY fecha_inicio DESC LIMIT 1
            """, (id_estancia_local,))

            hab_row = cur.fetchone()

            if hab_row:
                estancia_data['habitacion'] = hab_row['habitacion']
                estancia_data['costo_total'] = hab_row['costo']
            else:
                estancia_data['habitacion'] = None
                estancia_data['costo_total'] = 0.0

            # ---------------------------------------------------------
            # 3. OBTENER PAGOS DETALLADOS (Con Moneda y Usuario)
            # ---------------------------------------------------------
            # JOIN TRIPLE:
            # 1. Estancia -> Historial Transacciones (Para saber quién y cuándo)
            # 2. Transacciones -> Historial Pagos (Para saber monto y método)
            # 3. Pagos -> Metodos de Pago (Para saber la MONEDA: USD/BS)
            sql_pagos = """
                SELECT 
                    p.descripcion as metodo,
                    p.monto,
                    p.tasa,
                    t.usuario as usuario,
                    t.fecha_registro as fecha,
                    
                    -- Si no encuentra la moneda en config, usa 'USD' por defecto
                    COALESCE(mp.moneda, 'USD') as moneda
                    
                FROM historial_transacciones t
                JOIN historial_pagos p ON t.transaccion = p.id_historial
                LEFT JOIN metodos_pago mp ON p.descripcion = mp.descripcion
                
                WHERE t.id_estancia = %s
            """
            cur.execute(sql_pagos, (id_estancia_local,))
            lista_pagos = cur.fetchall()

            estancia_data['pagos'] = lista_pagos

            # ---------------------------------------------------------
            # 4. EMPAQUETAR Y ENVIAR
            # ---------------------------------------------------------
            payload = {
                "hotel_id": HOTEL,  # <--- OJO: Asegúrate que esto coincida con tu hotel
                "estancias": [estancia_data]
            }

            # Llamada a la función maestra de sync en un hilo aparte
            hilo = threading.Thread(
                target=misk().sync_servidor,
                args=(payload, "/api/sync/estancias"),
                daemon=True
            )
            hilo.start()

        except Exception as e:
            print(f"❌ Error crítico recopilando estancia: {e}")
        finally:
            if 'cur' in locals():
                cur.close()
            if 'db' in locals():
                db.close()


# ---------------------------------------------------------------------------------------------------

    def egreso_cliente(self):

        tab1 = self.tab_huespedes.widget(self.tab_huespedes.currentIndex())
        huespedes_incompletos = False

        for i in range(1, self.tab_huespedes.count()):
            tab = self.tab_huespedes.widget(i)
            if tab.findChild(QLineEdit, "input_cedula").text():
                if not tab.findChild(QLineEdit, "input_nombre").text() or not tab.findChild(QComboBox, "input_estado_civil").currentText() or not tab.findChild(QLineEdit, "input_telefono").text():
                    huespedes_incompletos = True
                    break

        if not tab1.findChild(QLineEdit, "input_cedula").text() or not tab1.findChild(QLineEdit, "input_nombre").text() or not tab1.findChild(QComboBox, "input_estado_civil").currentText() or not tab1.findChild(QLineEdit, "input_telefono").text():
            misk().errorMSG("Rellene los datos del huesped principal", "Datos Huesped Principal")

        elif huespedes_incompletos:
            misk().errorMSG("Rellene los datos de los acompañantes", "Datos Acompañantes")

        elif self.faltan_dolar.text() != "0.0$":
            misk().errorMSG("No se puede egresar al huesped si no\nha pagado la habitación",
                            "Huesped no ha pagado")

        elif self.input_precensia_huesped.text() == "Ausente":
            misk().errorMSG("El huesped no se encuentra dentro del hotel", "Huesped fuera del hotel")

        else:
            db = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )

            c = db.cursor()

            # --- Actualizar datos de clientes ---
            for i in range(self.tab_huespedes.count()):
                tab = self.tab_huespedes.widget(i)
                if tab.findChild(QLineEdit, "input_cedula").text():

                    c.execute(
                        f'''UPDATE clientes SET
                                nombre = %s,
                                fecha_nacimiento = %s,
                                nacionalidad = %s,
                                estado_civil = %s,
                                direccion = %s,
                                telefono = %s,
                                profesion = %s,
                                reputacion = %s,
                                observaciones = %s
                            WHERE cedula = %s
                            ''',
                        (
                            tab.findChild(
                                QLineEdit, "input_nombre").text(),
                            tab.findChild(
                                QDateEdit, "input_fnacimiento").date().toPython(),
                            tab.findChild(
                                QComboBox, "input_nacionalidad").currentText(),
                            tab.findChild(
                                QComboBox, "input_estado_civil").currentText(),
                            self.input_procedencia.currentText(),  # Dirección puede ser procedencia
                            tab.findChild(
                                QLineEdit, "input_telefono").text(),
                            tab.findChild(
                                QComboBox, "input_profesion").currentText(),
                            tab.findChild(
                                QPushButton, "reputacion").text(),
                            tab.findChild(
                                QPlainTextEdit, "observaciones_cliente").toPlainText(),
                            tab.findChild(QLineEdit, "input_cedula").text()
                        )
                    )

            id_estancia = self.id_estancia

            if not id_estancia:
                misk().errorMSG("ID de estancia no disponible. No se pueden actualizar los pagos.", "Error Interno")
                print("ERROR: self.id_estancia es None o vacío.")
                # Opcional: Salir o manejar el error de otra manera
                return  # Salir de la función si no hay id_estancia

            # Consultar la transacción inicial
            c.execute(
                "SELECT transaccion FROM historial_transacciones WHERE id_estancia = %s ORDER BY fecha_registro ASC, transaccion ASC LIMIT 1", (id_estancia,))
            result_transaccion = c.fetchone()
            if not result_transaccion:
                misk().errorMSG(
                    f"No se encontró ninguna transacción para la estancia {id_estancia}. No se pueden actualizar los pagos.", "Error Interno")
                print(
                    f"ERROR: No se encontró transacción inicial para id_estancia {id_estancia}.")
                # Opcional: Salir o manejar el error de otra manera
                return  # Salir de la función si no hay transacción
            transaccion_inicial = result_transaccion[0]

            pagos = [
                ["hab", self.FP1.currentText(), self.input_FP1.value()],
                ["hab", self.FP2.currentText(), self.input_FP2.value()],
                ["hab", self.FP3.currentText(), self.input_FP3.value()],
                ["hab", self.FP4.currentText(), self.input_FP4.value()],

                ["extra", self.extra1.currentText(), self.input_extra1.value()],
                ["extra", self.extra2.currentText(), self.input_extra2.value()],
                ["extra", self.extra3.currentText(), self.input_extra3.value()],
            ]

            # Borrar pagos antiguos asociados a la transacción inicial
            c.execute(
                f"DELETE FROM historial_pagos WHERE id_historial = %s", (transaccion_inicial,))

            for pago in pagos:
                if pago[2]:  # Si tiene monto
                    c.execute(
                        f'''
                            INSERT INTO historial_pagos
                            (id, id_historial, tipo, descripcion, monto, tasa) VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s)
                            ''',
                        (f"{transaccion_inicial}{pago[1]}", transaccion_inicial,  # Usamos transaccion_inicial
                         pago[0], pago[1], pago[2], self.dolarprice)
                    )

            # --- Actualizar datos en historial_transacciones ---
            # Aunque no guarda fechas ni habitación, puede haber otros campos a actualizar (observaciones, usuario, voucher)
            # en la transacción inicial.

            # OJO: Esta actualización afecta solo la transacción contenedora inicial, no la estancia real.
            # Si necesitas actualizar campos como 'observaciones' en la estancia real, debes hacerlo en `estancias`.
            query_historial = '''
                    UPDATE historial_transacciones SET
                        usuario = %s,
                        observaciones = %s
                    WHERE transaccion = %s
                '''

            params_historial = (
                self.input_atendido_por.text(),
                self.observaciones_transaccion.toPlainText(),
                transaccion_inicial  # Usamos transaccion_inicial
            )

            c.execute(query_historial, params_historial)

            voucher = None if not self.valor_voucher.isVisible() else self.input_voucher.text()

            # --- Actualizar datos en estancias y estancia_habitaciones ---
            # Ya tenemos id_estancia
            # Actualizar la estancia principal
            query_estancia = '''
                    UPDATE estancias SET
                        fecha_fin_real = NOW(),
                        estado = 'finalizada',
                        voucher = %s,
                        observaciones = %s
                    WHERE id_estancia = %s
                '''
            # Concatenar nuevas observaciones con las existentes si es necesario
            # Por simplicidad, reemplazamos las observaciones de la estancia con las de la transacción de checkout
            c.execute(
                query_estancia, (voucher, self.observaciones_transaccion.toPlainText(), id_estancia))

            # Actualizar la/s fila/s en estancia_habitaciones para la habitación actual (self.hab_num)
            # Suponemos que la estancia en `self.hab_num` se está cerrando
            # Si la estancia usó múltiples habitaciones, solo actualizamos la que se está desocupando ahora.
            query_estancia_hab = '''
                    UPDATE estancia_habitaciones SET
                        fecha_fin_real = NOW()
                    WHERE id_estancia = %s AND habitacion = %s AND fecha_fin_real IS NULL
                '''  # Aseguramos no sobrescribir una fecha_fin_real ya existente
            c.execute(query_estancia_hab, (id_estancia, self.hab_num))

            # --- Actualizar current_habitaciones ---
            # AHORA: Se actualiza usando id_estancia en lugar de transaccion
            # Se desocupa la habitación específica y se marca como sucia
            c.execute(
                # Asegura que es la estancia correcta la que se libera
                f"UPDATE current_habitaciones SET id_estancia = NULL, estado = 'sucia' WHERE habitacion = %s AND id_estancia = %s", (self.hab_num, id_estancia))

            # Contar habitaciones sucias
            c.execute(
                "SELECT COUNT(habitacion) FROM current_habitaciones WHERE estado = 'sucia'")
            sucias_count = c.fetchone()[0]

            # ------------------------------------ Add to Log -----------------------------------------

            misk().registrar_log("habitacion", self.input_atendido_por.text(),
                                 "habitacion paso a sucia", self.hab_num)

            number = 20
            if sucias_count >= number:
                misk().errorMSG(
                    f"Hay muchas Habitaciones sucias ({sucias_count} en total) habitaciones sucias", "Muchas Habitaciones Sucias")
                misk().tg_message(
                    f"💩 <b>Hay muchas habitaciones sucias ({sucias_count} en total)</b> 💩")
            # ------------------------------------ Add to Log -----------------------------------------

            misk().registrar_log("habitacion", self.input_atendido_por.text(),
                                 "muchas habitaciones sucias", sucias_count)

            persona = {
                'rol': "cliente",
                'nombre': f'HAB {self.hab_num}',
                'identificador': id_estancia
            }

            misk().abrir_porton(self.input_atendido_por.text(),
                                [persona], "SALIDA", "VEHICULAR")

            db.commit()
            c.close()
            db.close()

            try:
                # self.id_estancia contiene el ID que acabamos de cerrar
                if id_estancia:
                    print(
                        f"🚀 Iniciando sincronización de Salida: {id_estancia}")
                    hilo_sync = threading.Thread(
                        target=self.sincronizar_estancia_completa,
                        args=(id_estancia,),
                        daemon=True
                    )
                    hilo_sync.start()
            except Exception as e:
                print(f"⚠️ Error iniciando hilo sync salida: {e}")

            self.temp_closeEvent = False
            self.close()
            self.temp_closeEvent = True


# ---------------------------------------------------------------------------------------------------


    def renovar(self):
        dias, ok = QInputDialog.getInt(
            self, 'Renovar Estadia', 'Ingrese el número de dias a renovar', 1, 1)

        if ok:
            db = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )

            c = db.cursor()

            id_estancia = self.id_estancia

            # --- Obtener precio de la habitación ---
            c.execute(
                f"SELECT {self.estadia_type.text()} FROM habitaciones WHERE habitacion = %s", (self.hab_num,))
            precio_hab = float(c.fetchone()[0])
            costo_renovacion = precio_hab * dias

            # --- Actualizar estancias.fecha_fin_planificada ---
            c.execute("UPDATE estancias SET fecha_fin_planificada = DATE_ADD(fecha_fin_planificada, INTERVAL %s DAY) WHERE id_estancia = %s", (dias, id_estancia))

            # --- Actualizar estancia_habitaciones.fecha_fin_planificada y costo ---
            # Suponemos que la transacción actual se refiere a la estancia en `self.hab_num`
            # y que es la fila activa (fecha_fin_real IS NULL)
            c.execute("""
                UPDATE estancia_habitaciones
                SET fecha_fin_planificada = DATE_ADD(fecha_fin_planificada, INTERVAL %s DAY),
                    costo = costo + %s
                WHERE id_estancia = %s AND habitacion = %s AND fecha_fin_real IS NULL
            """, (dias, costo_renovacion, id_estancia, self.hab_num))

            # --- Crear nueva transacción financiera para la renovación ---
            # Generar un nuevo ID único para la transacción de renovación
            # Puedes usar un prefijo para distinguirla
            print(QDateTime.currentDateTime().toPython())
            transaccion_renovacion = f"{self.transaccion}_R_{QDateTime.currentDateTime().toPython()}"
            print(transaccion_renovacion)

            # Insertar la nueva transacción contenedora
            c.execute(
                "INSERT INTO historial_transacciones (transaccion, id_estancia, usuario, fecha_registro) VALUES (%s, %s, %s, NOW())",
                (transaccion_renovacion, id_estancia,
                 self.input_atendido_por.text())
            )

            misk().registrar_log("habitacion", self.input_atendido_por.text(),
                                 f"habitación renovada por {dias} dia/s más", self.hab_num)

            db.commit()

            c.close()
            db.close()

            # --- Actualizar interfaz ---
            self.input_fsalida.setDate(self.input_fsalida.date().addDays(dias))
            self.input_estadia_dias.setValue(
                self.input_estadia_dias.value() + dias)

            # Actualizar costo total mostrado (sumar el costo de la renovación)
            costo_actual = float(self.costo_dolar.text().replace('$', ''))
            nuevo_costo = costo_actual + costo_renovacion
            self.costo_dolar.setText(f"{nuevo_costo}$")

            self.price_calculation()  # Recalcular totales si es necesario

            # Mantener estilo y tipo de estadía si es necesario
            # self.estadia_type.setText("hospedaje") # Esto probablemente no cambia en una renovación
            self.FRcosto.setStyleSheet('''
            background-color:  qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(189, 195, 199), stop:1 rgb(36, 54, 70));
            border-radius: 4px;
            ''')

            misk().tg_message(
                f"El cliente de la habitación {self.hab_num} ha renovado {dias} dia/s más")

            misk().informationMSG(
                f"Renovación efectuada exitosamente, fueron añadidos {dias} dias", "Renovación Exitosa")

    def closeEvent(self, event):

        if not self.begresar.isEnabled():
            self.reset_datos()

        elif not self.temp_closeEvent:
            self.reset_datos()

        else:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:

                db = mc.connect(
                    host=host_ip,
                    user=database_user,
                    password=database_password,
                    database="esmeralda_software",
                    use_pure=True
                )

                c = db.cursor()

                # Consultar la transacción inicial
                c.execute(
                    "SELECT transaccion FROM historial_transacciones WHERE id_estancia = %s ORDER BY fecha_registro ASC, transaccion ASC LIMIT 1", (self.id_estancia,))
                result_transaccion = c.fetchone()

                # Asignar la transacción inicial encontrada
                transaccion_inicial = result_transaccion[0]
                # Log para depuración
                print(
                    f"Transacción inicial encontrada para {self.id_estancia}: {transaccion_inicial}")

                # --- Actualizar datos de clientes ---
                for i in range(self.tab_huespedes.count()):
                    tab = self.tab_huespedes.widget(i)
                    if tab.findChild(QLineEdit, "input_cedula").text():

                        c.execute(
                            f'''UPDATE clientes SET
                                nombre = %s,
                                fecha_nacimiento = %s,
                                nacionalidad = %s,
                                estado_civil = %s,
                                direccion = %s,
                                telefono = %s,
                                profesion = %s,
                                reputacion = %s,
                                observaciones = %s
                            WHERE cedula = %s
                            ''',
                            (
                                tab.findChild(
                                    QLineEdit, "input_nombre").text(),
                                tab.findChild(
                                    QDateEdit, "input_fnacimiento").date().toPython(),
                                tab.findChild(
                                    QComboBox, "input_nacionalidad").currentText(),
                                tab.findChild(
                                    QComboBox, "input_estado_civil").currentText(),
                                self.input_procedencia.currentText(),  # Dirección puede ser procedencia
                                tab.findChild(
                                    QLineEdit, "input_telefono").text(),
                                tab.findChild(
                                    QComboBox, "input_profesion").currentText(),
                                tab.findChild(
                                    QPushButton, "reputacion").text(),
                                tab.findChild(
                                    QPlainTextEdit, "observaciones_cliente").toPlainText(),
                                tab.findChild(QLineEdit, "input_cedula").text()
                            )
                        )

                # --- Actualizar pagos ---
                # Ahora usamos transaccion_inicial para borrar e insertar pagos.
                pagos = [
                    ["hab", self.FP1.currentText(), self.input_FP1.value()],
                    ["hab", self.FP2.currentText(), self.input_FP2.value()],
                    ["hab", self.FP3.currentText(), self.input_FP3.value()],
                    ["hab", self.FP4.currentText(), self.input_FP4.value()],

                    ["extra", self.extra1.currentText(), self.input_extra1.value()],
                    ["extra", self.extra2.currentText(), self.input_extra2.value()],
                    ["extra", self.extra3.currentText(), self.input_extra3.value()],
                ]

                # Borrar TODOS los pagos antiguos asociados A LA TRANSACCION INICIAL
                # Log para depuración
                print(
                    f"Borrando pagos antiguos para transacción inicial: {transaccion_inicial}")
                c.execute(
                    f"DELETE FROM historial_pagos WHERE id_historial = %s", (transaccion_inicial,))

                # Insertar los pagos actuales (nuevos o modificados) en la transacción inicial
                for pago in pagos:
                    if pago[2]:  # Si tiene monto
                        # Generar un ID único para el pago basado en transacción y método
                        pago_id = f"{transaccion_inicial}{pago[1]}"
                        # Log para depuración
                        print(
                            f"Insertando pago: ID={pago_id}, Monto={pago[2]}, Transacción={transaccion_inicial}")
                        c.execute(
                            f'''
                            INSERT INTO historial_pagos
                            (id, id_historial, tipo, descripcion, monto, tasa) VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s)
                            ''',
                            (pago_id, transaccion_inicial,
                             pago[0], pago[1], pago[2], self.dolarprice)
                        )

                # --- Actualizar current_habitaciones ---
                # Solo actualiza el estado.
                # La habitación ya está asociada a la estancia correcta (y por lo tanto a la transacción) desde ingreso_cliente.
                # No se toca el id_estancia aquí.
                c.execute(
                    f"UPDATE current_habitaciones SET estado = %s WHERE habitacion = %s", (self.estadia_type.text(), self.hab_num))

                # --- Actualizar observaciones en estancias ---
                # Se usa self.id_estancia en lugar de self.transaccion
                c.execute(f'''UPDATE estancias SET observaciones = %s WHERE id_estancia = %s''',
                          (self.observaciones_transaccion.toPlainText(), self.id_estancia))

                # Opcional: Actualizar observaciones en historial_transacciones si también se desea
                # c.execute(f'''UPDATE historial_transacciones SET observaciones = %s WHERE transaccion = %s''',
                #           (self.observaciones_transaccion.toPlainText(), transaccion_inicial))

                # --- Lógica de TV Display ---
                c.execute(
                    "SELECT config_value FROM config WHERE config_key = 'tv_display' OR config_key = 'tv_display_url'")
                tv_display = tuple(item[0] for item in c.fetchall())

                if int(tv_display[0]):
                    endpoint = f"{tv_display[1]}/api/show/carousel"
                    print(endpoint)
                    try:
                        response = requests.post(endpoint)
                        response.raise_for_status()
                        print(
                            f"   -> Servidor respondió: {response.json()['message']}")
                    except requests.exceptions.RequestException as e:
                        print(f"   -> Error: {e}")

                db.commit()
                c.close()
                db.close()

                try:
                    # self.id_estancia contiene el ID de la estancia que se estaba editando
                    if self.id_estancia:
                        print(
                            f"🚀 Sincronizando actualización (closeEvent) de Estancia {self.id_estancia}")
                        hilo_sync = threading.Thread(
                            target=self.sincronizar_estancia_completa,
                            args=(self.id_estancia,),
                            daemon=True
                        )
                        hilo_sync.start()
                except Exception as e:
                    print(f"⚠️ Error iniciando sync en closeEvent: {e}")

                self.reset_datos()

            except ValueError as error:
                QApplication.restoreOverrideCursor()
                misk().errorMSG("Falta ingresar o hay algun dato incorrecto\nrevise nuevamente los datos ingresados",
                                "Dato incorrecto o faltante")
                print(error)
                event.ignore()

            except mc.Error as err:  # Capturar errores de MySQL específicamente
                db.rollback()  # Revertir cambios si hay error
                QApplication.restoreOverrideCursor()
                misk().errorMSG(
                    f"Error de base de datos: {err.msg}", "Error de Base de Datos")
                print(f"Error de MySQL: {err}")
                event.ignore()  # Evitar cierre si hay error de DB

            QApplication.restoreOverrideCursor()

    def reset_datos(self):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute(
            "SELECT config_value FROM config WHERE config_key = 'hotel_ciudad'")
        ciudad = c.fetchone()[0]

        c.execute(
            "SELECT config_value FROM config WHERE config_key = 'tv_display' OR config_key = 'tv_display_url'")
        tv_display = tuple(item[0] for item in c.fetchall())

        if int(tv_display[0]):
            endpoint = f"{tv_display[1]}/api/show/carousel"
            print(endpoint)
            try:
                response = requests.post(endpoint)
                response.raise_for_status()
                print(
                    f"   -> Servidor respondió: {response.json()['message']}")
            except requests.exceptions.RequestException as e:
                print(f"   -> Error: {e}")

        c.close()
        db.close()

        self.transaccion = ""

        for i in range(self.tab_huespedes.count()):
            tab = self.tab_huespedes.widget(i)
            tab.findChild(QLineEdit, "input_cedula").clear()
            tab.findChild(QLineEdit, "input_cedula").setReadOnly(False)
            tab.findChild(QLineEdit, "input_nombre").clear()
            tab.findChild(QDateEdit, "input_fnacimiento").clear()
            tab.findChild(QComboBox, "input_nacionalidad").setCurrentText(
                "Venezolano")
            tab.findChild(
                QComboBox, "input_estado_civil").setCurrentText("Soltero")
            tab.findChild(QLineEdit, "input_telefono").clear()
            tab.findChild(QComboBox, "input_profesion").setCurrentText(
                "Comerciante")
            tab.findChild(QPlainTextEdit,
                          "observaciones_cliente").setPlainText("")

            self.cliente_reputacion(i, "bloqueado")
            tab.findChild(QPushButton, "historial").setText("Vino 0 veces")

        self.tab_huespedes.setCurrentIndex(0)

        self.input_procedencia.setCurrentText(ciudad)
        self.input_destino.setCurrentText(ciudad)

        self.input_fentrada.setReadOnly(False)
        self.input_fentrada.setDateTime(QDateTime.currentDateTime())

        self.input_fsalida.setReadOnly(False)

        self.input_estadia_dias.setReadOnly(False)
        self.input_estadia_dias.setValue(1)

        self.costo_dolar.setText("0$")

        self.estadia_type.setText("???")
        self.FRcosto.setStyleSheet('''
            background-color: rgb(40, 40, 40);
            border-radius: 4px;
            ''')

        self.input_FP1.setValue(0)
        self.input_FP2.setValue(0)
        self.input_FP3.setValue(0)
        self.input_FP4.setValue(0)

        self.input_extra1.setValue(0)
        self.input_extra2.setValue(0)
        self.input_extra3.setValue(0)

        self.input_voucher.setText("")
        self.input_voucher.setEnabled(True)

        self.valor_voucher.setText("")
        self.valor_voucher.setVisible(False)

        self.observaciones_transaccion.setPlainText("")

        self.bparcial.setEnabled(True)
        self.bparcial.setText("Parcial")
        self.bparcial.setStyleSheet(
            '''background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(180, 20, 20), stop:1 rgb(60, 0, 0));
                color: rgb(242, 242, 242);
                font-size: 14px;''')

        self.bhospedaje.setEnabled(True)
        self.bhospedaje.setText("Hospedaje")
        self.bhospedaje.setStyleSheet(
            '''background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(189, 195, 199), stop:1 rgb(36, 54, 70));
                color: rgb(242, 242, 242);
                font-size: 14px;''')

        self.bcambiar_hab.setHidden(True)

        self.begresar.setEnabled(False)
        self.begresar.setStyleSheet('''
                background-color: black;
                color: rgb(242, 242, 242);
                border-radius: 2px;
                font-size: 18px;
                font-weight: bold;''')
        self.bingresar.setEnabled(True)

        self.bingresar.setStyleSheet('''
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.8, y2:0.8, stop:1 #11998E, stop:0 #38ef7d);
                font-size: 18px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                font-size: 20px;
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.4, y2:0.4, stop:1 #11998E, stop:0 #38ef7d);
                font-size: 18px
            }
            ''')

# ---------------------------------------------------------------------------------------------------

    def cambiar_hab(self):
        question = misk().questionMSG(
            "Desea cambiar el cliente\nde habitación?", "Cambiar Habitación")

        if question == QMessageBox.Ok:
            self.start = False
            motivo, ok = QInputDialog.getText(
                self, 'Razon del cambio', 'Describa el motivo del cambio:')

            if ok == True:
                self.mover_cliente(motivo)

    def retoque(self):
        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        if self.sender().text() == "Solicitar Retoque":
            print(self.id_estancia)
            c.execute(
                f"UPDATE current_habitaciones SET estado = 'retoque' WHERE id_estancia = '{self.id_estancia}'")
        elif self.sender().text() == "Realizar Retoque":
            c.execute(
                f"UPDATE current_habitaciones SET estado = '{self.estadia_type.text()}' WHERE id_estancia = '{self.id_estancia}'")

        db.commit()
        db.close()

        self.temp_closeEvent = False
        self.close()
        self.temp_closeEvent = True

    def hab_bloquear(self):

        question = misk().questionMSG(
            "Desea bloquear la habitación?", "Bloquear Habitación")

        if question == QMessageBox.Ok:

            db = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )

            c = db.cursor()

            c.execute(
                f"SELECT current_habitaciones.estado, habitaciones.razon_bloqueo FROM current_habitaciones JOIN habitaciones ON current_habitaciones.habitacion = habitaciones.habitacion WHERE current_habitaciones.habitacion = '{self.hab_num}'")
            data = c.fetchone()

            self.start = False
            problema, ok = QInputDialog.getText(
                self, 'Razon del bloqueo', 'Describa el problema de la habitación:')

            if ok == True:
                if not data or not data[0]:

                    c.execute(
                        f"UPDATE current_habitaciones SET estado = 'bloqueada' WHERE habitacion = '{self.hab_num}'")
                    c.execute(
                        f"UPDATE habitaciones SET razon_bloqueo = '{problema.lower()}' WHERE habitacion = '{self.hab_num}'")

                    misk().tg_message(
                        f"La habitación <b>{self.hab_num}</b> fue bloqueada debido a que <b>{problema.lower()}</b> 🚧👷‍♂️")
                    self.close()
                else:
                    self.mover_cliente(
                        problema + "\n\n🚧 Dicha habitación fue bloqueada hasta arreglar su falla 🚧")

                c.execute(
                    f"UPDATE current_habitaciones SET estado = 'bloqueada' WHERE habitacion = '{self.hab_num}'")
                c.execute(
                    f"UPDATE habitaciones SET razon_bloqueo = '{problema.lower()}' WHERE habitacion = '{self.hab_num}'")

                # ------------------------------------ Add to Log -----------------------------------------

                misk().registrar_log("habitacion", self.input_atendido_por.text(),
                                     f"habitacion bloqueada por {problema.lower()}", self.hab_num)

            db.commit()
            c.close()
            db.close()

            self.temp_closeEvent = False
            self.close()
            self.temp_closeEvent = True

    def mover_cliente(self, problema):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute(
            "SELECT habitacion FROM current_habitaciones WHERE estado IS NULL")
        data = c.fetchall()

        clean_habs = [i[0] for i in data]

        nueva_hab, ok = QInputDialog.getItem(
            self, 'Cambiar Habitación', 'A que habitación desea\npasar al cliente?', clean_habs)

        if ok == True:
            nueva_hab_precio = float

            # --- Usar self.id_estancia directamente ---
            # Asumiendo que self.id_estancia es el atributo que contiene el ID de la estancia actual
            id_estancia = self.id_estancia

            # --- Obtener precio de la nueva habitación ---
            if self.estadia_type.text() == "parcial":
                c.execute(
                    f"SELECT parcial FROM habitaciones WHERE habitacion = %s", (nueva_hab,))
                nueva_hab_precio = float(c.fetchone()[0])

            elif self.estadia_type.text() == "hospedaje":
                # Calcular precio basado en días restantes o planificados
                # Suponemos que self.input_estadia_dias.value() representa los días restantes
                dias_restantes = self.input_estadia_dias.value()
                c.execute(
                    f"SELECT hospedaje FROM habitaciones WHERE habitacion = %s", (nueva_hab,))
                precio_diario = float(c.fetchone()[0])
                nueva_hab_precio = precio_diario * dias_restantes

            else:
                # Si no es parcial ni hospedaje, usar el costo actual como base
                nueva_hab_precio = float(
                    self.costo_dolar.text().replace("$", ""))

            diferencia = nueva_hab_precio - \
                float(self.costo_dolar.text().replace('$', ''))

            # --- Actualizar estancia_habitaciones ---
            # 1. Cerrar la fila de la habitación actual (self.hab_num)
            # Suponemos que es la fila activa (fecha_fin_real IS NULL) para la estancia actual
            c.execute("""
                UPDATE estancia_habitaciones
                SET fecha_fin_real = NOW()
                WHERE id_estancia = %s AND habitacion = %s AND fecha_fin_real IS NULL
            """, (id_estancia, self.hab_num))

            # 2. Crear una nueva fila para la nueva habitación (nueva_hab)
            # Calcular fechas. Suponemos que la nueva habitación comienza ahora y termina cuando terminaba la anterior.
            # Opcional: Podrías querer mantener la fecha de salida original o actualizarla.
            # Por ahora, usamos la fecha_fin_planificada de la estancia como base.
            c.execute(
                "SELECT fecha_fin_planificada FROM estancias WHERE id_estancia = %s", (id_estancia,))
            result_fecha_fin = c.fetchone()
            if result_fecha_fin:
                fecha_fin_planif_nueva = result_fecha_fin[0]
            else:
                # Si no se encuentra, usar la fecha de la UI como fallback
                fecha_fin_planif_nueva = self.input_fsalida.dateTime().toPython()

            # Generar ID único
            # Reemplazamos ":" por "-" o "_" en la fecha para evitar problemas en el ID
            id_nueva_estancia_habitacion = f"{id_estancia}_HAB_{nueva_hab}_M_{QDateTime.currentDateTime().toPython()}"
            c.execute("""
                INSERT INTO estancia_habitaciones
                (id, id_estancia, habitacion, fecha_inicio, fecha_fin_planificada, costo)
                VALUES (%s, %s, %s, NOW(), %s, %s)
            """, (id_nueva_estancia_habitacion, id_estancia, nueva_hab, fecha_fin_planif_nueva, nueva_hab_precio))

            # --- Actualizar current_habitaciones ---
            # 1. Asignar la nueva habitación a la estancia actual (id_estancia)
            # Asumiendo que current_habitaciones.id_estancia apunta a la estancia correcta
            c.execute(
                f"UPDATE current_habitaciones SET id_estancia = %s, estado = %s WHERE habitacion = %s", (id_estancia, self.estadia_type.text(), nueva_hab))

            # 2. Desocupar la antigua habitación (id_estancia = NULL)
            c.execute(
                f"UPDATE current_habitaciones SET estado = NULL, id_estancia = NULL WHERE habitacion = %s", (self.hab_num,))

            c.execute(f"UPDATE current_personas SET nombre = %s WHERE identificador = %s",
                      (f'HAB {nueva_hab}', self.id_estancia,))

            # --- Registrar en usuario_log ---
            misk().registrar_log("transaccion", self.input_atendido_por.text(),
                                 f"cliente movido debido a que {problema.lower()}", f"{self.hab_num} - {nueva_hab}")

            db.commit()
            c.close()
            db.close()

            try:
                # id_estancia ya la definiste al inicio de la función
                if id_estancia:
                    print(
                        f"🚀 Sincronizando cambio de habitación para Estancia {id_estancia}")
                    hilo_sync = threading.Thread(
                        target=self.sincronizar_estancia_completa,
                        args=(id_estancia,),
                        daemon=True
                    )
                    hilo_sync.start()
            except Exception as e:
                print(f"⚠️ Error iniciando sync de movimiento: {e}")

            # --- Actualizar interfaz ---
            # Opcional: Actualizar el costo si cambió
            if diferencia != 0:
                costo_actual = float(self.costo_dolar.text().replace('$', ''))
                nuevo_costo = costo_actual + diferencia
                self.costo_dolar.setText(f"{nuevo_costo}$")
                self.price_calculation()  # Recalcular totales si es necesario

            # Actualizar la variable interna de la habitación
            self.hab_num = nueva_hab

            misk().tg_message(
                f"El cliente de la habitación <b>{self.hab_num}</b> fue movido a la <b>{nueva_hab}</b> debido a que <b>{problema}</b> (La diferencia fue de {diferencia}$)")

            self.temp_closeEvent = False
            self.close()
            self.temp_closeEvent = True

    def center(self):
        # qr = self.frameGeometry()
        # cp = QDesktopWidget().availableGeometry().center()
        # qr.moveCenter(cp)
        # self.move(qr.topLeft())
        None
      ######################################### Habitaciones Window #########################################

      ######################################### Habitaciones Window #########################################

      ######################################### Habitaciones Window #########################################


class Habitaciones(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Habitaciones')
        # self.setWindowFlags(Qt.WindowStaysOnBottomHint)
        self.setWindowState(Qt.WindowMaximized)
        self.setMinimumSize(1220, 820)
        self.setWindowIcon(QIcon(f"img/minilogo.ico"))

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        central_widget.setLayout(layout)

        self.sec_timer = QTimer()
        self.sec_timer.start(1000)

        self.PagoWindow = PagoWindow()
        self.misk = misk()
        self.SettingsWindow = SettingsWindow()
        self.InformacionWindow = InformacionWindow()
        self.TableViewData = TableViewData()
        self.NoticeIssueBoard = NoticeIssueBoard()
        self.ReservationsBoard = ReservationsBoard()

        HspacerItem = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout.addItem(HspacerItem)

        frame0 = QFrame()
        frame0.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        layout_frame0 = QVBoxLayout(frame0)
        layout.addWidget(frame0)
        frame0.setFixedSize(180, 800)

  ######################################### Logo #########################################

        self.blogo = QPushButton()
        self.blogo.setFixedSize(164, 50)
        layout_frame0.addWidget(self.blogo)
        self.blogo.setIcon(QIcon(f"img/banner.png"))
        self.blogo.setIconSize(QSize(164, 70))
        self.blogo.setCursor(QCursor(Qt.PointingHandCursor))
        self.blogo.clicked.connect(self.open_informacion)
        self.blogo.setToolTip(F"Información | {appversion}")
        self.blogo.setStyleSheet("QPushButton{ background: rgba(0, 0, 0, 0) }")

  ######################################### Count Habs #########################################

        FRhabStatus = QFrame()
        FRhabStatus.setFixedSize(160, 810)
        layout_frame0.addWidget(FRhabStatus)
# ---------------------------------------------------------------------------------------------------
        libres = QLabel(FRhabStatus)
        libres.setGeometry(QRect(20, 40, 120, 25))
        libres.setText("Libres")

        self.lcd_libres = QLabel(FRhabStatus)
        self.lcd_libres.setGeometry(QRect(20, 70, 120, 50))
        self.lcd_libres.setAlignment(Qt.AlignRight)
        self.lcd_libres.setStyleSheet('''
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(5, 117, 230), stop:1 rgb(2, 27, 121));
        color: white;
        font-size: 40px;
        padding: 4px 0px;
        font-family: arial
        ''')
# ---------------------------------------------------------------------------------------------------
        parciales = QLabel(FRhabStatus)
        parciales.setGeometry(QRect(20, 140, 120, 25))
        parciales.setText("Parciales")

        self.lcd_parciales = QLabel(FRhabStatus)
        self.lcd_parciales.setGeometry(QRect(20, 170, 120, 50))
        self.lcd_parciales.setAlignment(Qt.AlignRight)
        self.lcd_parciales.setStyleSheet('''
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(180, 20, 20), stop:1 rgb(60, 0, 0));
        color: white;
        font-size: 40px;
        padding: 4px 0px;
        font-family: arial
        ''')
# ---------------------------------------------------------------------------------------------------
        hospedajes = QLabel(FRhabStatus)
        hospedajes.setGeometry(QRect(20, 240, 120, 25))
        hospedajes.setText("Hospedajes")

        self.lcd_hospedajes = QLabel(FRhabStatus)
        self.lcd_hospedajes.setGeometry(QRect(20, 270, 120, 50))
        self.lcd_hospedajes.setAlignment(Qt.AlignRight)
        self.lcd_hospedajes.setStyleSheet('''
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(189, 195, 199), stop:1 rgb(36, 54, 70));
        color: white;
        font-size: 40px;
        padding: 4px 0px;
        font-family: arial
        ''')
# ---------------------------------------------------------------------------------------------------
        self.reservadas = QLabel(FRhabStatus)
        self.reservadas.setGeometry(QRect(20, 340, 120, 25))
        self.reservadas.setText("Reservadas")

        self.lcd_reservadas = QLabel(FRhabStatus)
        self.lcd_reservadas.setGeometry(QRect(20, 370, 120, 50))
        self.lcd_reservadas.setAlignment(Qt.AlignRight)
        self.lcd_reservadas.setStyleSheet('''
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(20, 171, 169), stop:1 rgb(10, 60, 130));
        color: white;
        font-size: 40px;
        padding: 4px 0px;
        font-family: arial
        ''')

        lcd_breservadas = QPushButton(FRhabStatus)
        lcd_breservadas.setGeometry(QRect(20, 370, 120, 50))
        lcd_breservadas.setStyleSheet("background-color: rgba(0,0,0,0)")
        lcd_breservadas.setCursor(QCursor(Qt.PointingHandCursor))
        lcd_breservadas.clicked.connect(self.start_Rtable)


# ---------------------------------------------------------------------------------------------------

        mantenimiento = QLabel(FRhabStatus)
        mantenimiento.setGeometry(QRect(20, 440, 120, 25))
        mantenimiento.setText("Retoque")

        self.lcd_mantenimiento = QLabel(FRhabStatus)
        self.lcd_mantenimiento.setGeometry(QRect(20, 470, 120, 50))
        self.lcd_mantenimiento.setAlignment(Qt.AlignRight)
        self.lcd_mantenimiento.setStyleSheet('''
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(120, 40, 240), stop:1 rgb(60, 10, 100));
        color: white;
        font-size: 40px;
        padding: 4px 0px;
        font-family: arial
        ''')

# ---------------------------------------------------------------------------------------------------
        sucias = QLabel(FRhabStatus)
        sucias.setGeometry(QRect(20, 540, 120, 25))
        sucias.setText("Sucias")

        self.lcd_sucias = QLabel(FRhabStatus)
        self.lcd_sucias.setGeometry(QRect(20, 570, 120, 50))
        self.lcd_sucias.setAlignment(Qt.AlignRight)
        self.lcd_sucias.setStyleSheet('''
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(220, 82, 45), stop:1 rgb(70, 40, 20));
        color: white;
        font-size: 40px;
        padding: 4px 0px;
        font-family: arial
        ''')
# ---------------------------------------------------------------------------------------------------
        bloqueadas = QLabel(FRhabStatus)
        bloqueadas.setGeometry(QRect(20, 640, 120, 25))
        bloqueadas.setText("Bloqueadas")

        self.lcd_bloqueadas = QLabel(FRhabStatus)
        self.lcd_bloqueadas.setGeometry(QRect(20, 670, 120, 50))
        self.lcd_bloqueadas.setAlignment(Qt.AlignRight)
        self.lcd_bloqueadas.setStyleSheet('''
        background-color: rgb(0, 0, 0);
        color: white;
        font-size: 40px;
        padding: 4px 0px;
        font-family: arial
        ''')
# ---------------------------------------------------------------------------------------------------

        Hab_Status_Label = (bloqueadas, sucias, mantenimiento, parciales,
                            libres, hospedajes, self.reservadas)

        for i in Hab_Status_Label:
            i.setAlignment(Qt.AlignCenter)
            i.setStyleSheet('''
            background: rgba(0, 0, 0, 0);
            color: rgb(242, 242, 242);
            font-size: 20px;
            font-weight: bold
            ''')

  ######################################### Habs Buttons #########################################

        self.frame = QFrame()
        self.frame.setFixedSize(810, 800)
        layout.addWidget(self.frame)

  ######################################### Dolar Tasa #########################################

        frame1 = QFrame()
        layout_frame1 = QVBoxLayout(frame1)
        layout.addWidget(frame1)
        frame1.setFixedSize(250, 800)

        FRdolar = QFrame()
        FRdolar.setFixedSize(230, 210)
        layout_frame1.addWidget(FRdolar)

# ---------------------------------------------------------------------------------------------------
        self.cargo = QLabel(FRdolar)
        self.cargo.setGeometry(QRect(10, 10, 120, 24))
        self.cargo.setStyleSheet('''
            background: rgba(0, 0, 0, 0);
            color: rgb(242, 242, 242);
            font-size: 18px;
            font-weight: bold
        ''')
        self.cargo.setAlignment(Qt.AlignLeading |
                                Qt.AlignLeft | Qt.AlignVCenter)
        self.cargo.setText("cargo")
# ---------------------------------------------------------------------------------------------------
        self.usuario = QLabel(FRdolar)
        self.usuario.setGeometry(QRect(10, 32, 180, 44))
        self.usuario.setStyleSheet('''
            background: rgba(0, 0, 0, 0);
            color: rgb(242, 242, 242);
            font-size: 34px;
            font-weight: bold
        ''')
        self.usuario.setAlignment(
            Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.usuario.setText("Usuario")

# ---------------------------------------------------------------------------------------------------
        self.input_usuario = QComboBox(FRdolar)
        self.input_usuario.setGeometry(QRect(10, 84, 110, 28))
        self.input_usuario.setToolTip('Seleccionar usuario')
# ---------------------------------------------------------------------------------------------------
        self.input_precio_dolar = QDoubleSpinBox(FRdolar)
        self.input_precio_dolar.setGeometry(QRect(136, 84, 60, 28))
        self.input_precio_dolar.setMaximum(999999)
        self.input_precio_dolar.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.input_precio_dolar.setToolTip('Ingresar tasa del dolar en Bs')

        self.bdolar_bcv = QPushButton(FRdolar)
        self.bdolar_bcv.setGeometry(QRect(184, 84, 34, 28))
        self.bdolar_bcv.setText("BCV")
        self.bdolar_bcv.clicked.connect(self.dolar_bcv)
        self.bdolar_bcv.setCursor(QCursor(Qt.PointingHandCursor))
        self.bdolar_bcv.setStyleSheet(
            "QPushButton {background-color: white; color: black} QPushButton:hover {font-weight: bold}")


# ---------------------------------------------------------------------------------------------------
        self.bactualizar_usuario_dolar = QPushButton(FRdolar)
        self.bactualizar_usuario_dolar.setGeometry(
            QRect(10, 172, 200, 28))
        self.bactualizar_usuario_dolar.setText("Actualizar")
        self.bactualizar_usuario_dolar.clicked.connect(self.cambio_usuario)
        self.bactualizar_usuario_dolar.clicked.connect(self.dolar_actualizado)
        self.bactualizar_usuario_dolar.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.bactualizar_usuario_dolar.setStyleSheet('''
        QPushButton {
            background-color: rgba(0,0,0,0);
            color: white;
            font-size: 12px;
        }
        QPushButton:hover {
            color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.8, y2:0.8, stop:1 #11998e, stop:0 #38ef7d);
            font-size: 14px;
        }
        QPushButton:pressed {
            color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.5, y2:0.5, stop:1 #11998e, stop:0 #38ef7d);
            font-size: 12px
        }
        ''')

        self.bcambio_turno = QPushButton(FRdolar)
        self.bcambio_turno.setGeometry(QRect(18, 130, 200, 36))
        self.bcambio_turno.setText("Cambiar de Turno")
        self.bcambio_turno.clicked.connect(self.cambio_turno_type)
        self.bcambio_turno.setStyleSheet('''
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.8, y2:0.8, stop:1 #11998E, stop:0 #38ef7d);
            font-size: 16px;
            font-weight: bold;
            color: white
        }
        QPushButton:hover {
            font-size: 18px;
        }
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.4, y2:0.4, stop:1 #11998E, stop:0 #38ef7d);
            font-size: 16px
        }
        ''')
        self.bcambio_turno.setCursor(
            QCursor(Qt.PointingHandCursor))

  ######################################### Timeout Table #########################################

        self.FRtimeout = QFrame()
        self.FRtimeout.setFixedSize(230, 600)
        layout_frame1.addWidget(self.FRtimeout)

        self.timeout_hab_num = QLabel(self.FRtimeout)
        self.timeout_hab_num.setGeometry(QRect(38, 20, 200, 20))
        self.timeout_hab_num.setText("Hab    Hora de Salida")
        self.timeout_hab_num.setStyleSheet('''
        font-size: 12pt;
        font-weight: bold;
        ''')

        self.timeout_table = QTableWidget(self.FRtimeout)
        self.timeout_table.setGeometry(QRect(30, 52, 210, 590))
        # TODO PYSIDE CHANGED
        # self.timeout_table.setFocusPolicy(0)
        self.timeout_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.timeout_table.verticalHeader().setVisible(False)
        self.timeout_table.horizontalHeader().setVisible(False)

        self.timeout_table.setColumnCount(2)

        self.timeout_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.timeout_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)

        self.timeout_table.setStyleSheet('''
        QTableWidget {
            qproperty-showGrid: "false";
            color: white;
            font-size: 12pt;
            background-color: rgba(0, 0, 0, 0)
        }
        ''')

  ######################################### Extras #########################################

        FRextra = QFrame()
        FRextra.setFixedSize(230, 150)
        layout_frame1.addWidget(FRextra)
        FRextra.setStyleSheet("QPushButton{ background: rgba(0, 0, 0, 0) }")

        self.bconfig = QPushButton(FRextra)
        self.bconfig.setGeometry(QRect(8, 10, 46, 46))
        self.bconfig.setIcon(QIcon(f"img/config.png"))
        self.bconfig.setIconSize(QSize(46, 46))
        self.bconfig.setCursor(QCursor(Qt.PointingHandCursor))
        self.bconfig.clicked.connect(self.config)
        self.bconfig.setToolTip('Configuraciones')

        self.bmessage = QPushButton(FRextra)
        self.bmessage.setGeometry(QRect(70, 10, 46, 46))
        self.bmessage.setIcon(QIcon(f"img/send-message.png"))
        self.bmessage.setIconSize(QSize(46, 46))
        self.bmessage.clicked.connect(self.tg_usuario_message)
        self.bmessage.setCursor(QCursor(Qt.PointingHandCursor))
        self.bmessage.setToolTip('Enviar comunicado al Grupo')

        self.beye = QPushButton(FRextra)
        self.beye.setGeometry(QRect(128, 11, 46, 46))
        self.beye.setIcon(QIcon(f"img/eye.png"))
        self.beye.setIconSize(QSize(44, 44))
        self.beye.setCursor(QCursor(Qt.PointingHandCursor))
        self.beye.clicked.connect(self.novedades)
        self.beye.setToolTip('Ver Novedades y Averías')

        self.bcalculator = QPushButton(FRextra)
        self.bcalculator.setGeometry(QRect(184, 10, 46, 46))
        self.bcalculator.setIcon(
            QIcon(f"img/calculator.png"))
        self.bcalculator.setIconSize(QSize(46, 46))
        self.bcalculator.setCursor(QCursor(Qt.PointingHandCursor))
        self.bcalculator.setToolTip('Calculadora')
        self.bcalculator.clicked.connect(self.calculator)

        self.bporton_entrada = QPushButton("ENTRADA", FRextra)
        self.bporton_entrada.setStyleSheet(
            "background: rgb(40, 190, 100); color: white; font-size: 17px; font-weight: bold; letter-spacing: 1px")
        self.bporton_entrada.setGeometry(QRect(8, 86, 104, 46))
        self.bporton_entrada.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.bporton_entrada.setToolTip('Portón Entrada')
        self.bporton_entrada.clicked.connect(
            lambda: self.dialog_porton("ENTRADA"))

        self.bporton_salida = QPushButton("SALIDA", FRextra)
        self.bporton_salida.setStyleSheet(
            "background: rgb(242, 5, 5); color: white; font-size: 17px; font-weight: bold; letter-spacing: 1px")
        self.bporton_salida.setGeometry(QRect(122, 86, 104, 46))
        self.bporton_salida.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.bporton_salida.setToolTip('Portón Salida')
        self.bporton_salida.clicked.connect(
            lambda: self.dialog_porton("SALIDA"))

        # basic shortcut
        self.shortcut = QShortcut(QKeySequence('C'), self)
        self.shortcut.activated.connect(self.config)

        # # basic shortcut
        # self.shortcut = QShortcut(QKeySequence('I'), self)
        # self.shortcut.activated.connect(self.config_inventario)

        layout.addItem(HspacerItem)

    ################################# RUN WHEN START APP #################################

        Xbsize = 50
        Ybsize = 60

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute(
            "SELECT datetime FROM usuario_log WHERE descripcion = 'cambio de turno realizado' ORDER BY datetime DESC LIMIT 1")
        last_cambio_turno = c.fetchone()

        print(last_cambio_turno)

        if not last_cambio_turno:
            db.commit()
            misk().registrar_log("habitacion", "otto", "cambio de turno realizado", "")

        # c.execute("SELECT config_value FROM config WHERE config_key = 'hab_distro'")
        # hab_distro = c.fetchone()[0]

        # exec(hab_distro)

# 3

        self.B01 = QPushButton(self.frame)
        self.B01.setGeometry(QRect(710, 660, Xbsize, Ybsize))

        self.B02 = QPushButton(self.frame)
        self.B02.setGeometry(QRect(650, 660, Xbsize, Ybsize))

        self.B03 = QPushButton(self.frame)
        self.B03.setGeometry(QRect(590, 660, Xbsize, Ybsize))

        self.B04 = QPushButton(self.frame)
        self.B04.setGeometry(QRect(530, 660, Xbsize, Ybsize))

        self.B05 = QPushButton(self.frame)
        self.B05.setGeometry(QRect(470, 660, Xbsize, Ybsize))

        self.B06 = QPushButton(self.frame)
        self.B06.setGeometry(QRect(410, 660, Xbsize, Ybsize))

        self.B07 = QPushButton(self.frame)
        self.B07.setGeometry(QRect(350, 660, Xbsize, Ybsize))

        self.B08 = QPushButton(self.frame)
        self.B08.setGeometry(QRect(290, 660, Xbsize, Ybsize))

        self.B09 = QPushButton(self.frame)
        self.B09.setGeometry(QRect(230, 660, Xbsize, Ybsize))

        self.B10 = QPushButton(self.frame)
        self.B10.setGeometry(QRect(170, 660, Xbsize, Ybsize))

        self.B11 = QPushButton(self.frame)
        self.B11.setGeometry(QRect(170, 470, Xbsize, Ybsize))

        self.B12 = QPushButton(self.frame)
        self.B12.setGeometry(QRect(230, 470, Xbsize, Ybsize))

        self.B13 = QPushButton(self.frame)
        self.B13.setGeometry(QRect(290, 470, Xbsize, Ybsize))

        self.B14 = QPushButton(self.frame)
        self.B14.setGeometry(QRect(350, 470, Xbsize, Ybsize))

        self.B15 = QPushButton(self.frame)
        self.B15.setGeometry(QRect(410, 470, Xbsize, Ybsize))

        self.B16 = QPushButton(self.frame)
        self.B16.setGeometry(QRect(470, 470, Xbsize, Ybsize))

        self.B17 = QPushButton(self.frame)
        self.B17.setGeometry(QRect(530, 470, Xbsize, Ybsize))

        self.B18 = QPushButton(self.frame)
        self.B18.setGeometry(QRect(590, 470, Xbsize, Ybsize))

        self.B19 = QPushButton(self.frame)
        self.B19.setGeometry(QRect(650, 470, Xbsize, Ybsize))

        self.B20 = QPushButton(self.frame)
        self.B20.setGeometry(QRect(710, 470, Xbsize, Ybsize))

        self.B21 = QPushButton(self.frame)
        self.B21.setGeometry(QRect(710, 380, Xbsize, Ybsize))

        self.B22 = QPushButton(self.frame)
        self.B22.setGeometry(QRect(650, 380, Xbsize, Ybsize))

        self.B23 = QPushButton(self.frame)
        self.B23.setGeometry(QRect(590, 380, Xbsize, Ybsize))

        self.B24 = QPushButton(self.frame)
        self.B24.setGeometry(QRect(530, 380, Xbsize, Ybsize))

        self.B25 = QPushButton(self.frame)
        self.B25.setGeometry(QRect(470, 380, Xbsize, Ybsize))

        self.B26 = QPushButton(self.frame)
        self.B26.setGeometry(QRect(410, 380, Xbsize, Ybsize))

        self.B27 = QPushButton(self.frame)
        self.B27.setGeometry(QRect(170, 180, Xbsize, Ybsize))

        self.B28 = QPushButton(self.frame)
        self.B28.setGeometry(QRect(230, 180, Xbsize, Ybsize))

        self.B29 = QPushButton(self.frame)
        self.B29.setGeometry(QRect(290, 180, Xbsize, Ybsize))

        self.B30 = QPushButton(self.frame)
        self.B30.setGeometry(QRect(410, 180, Xbsize, Ybsize))

        self.B31 = QPushButton(self.frame)
        self.B31.setGeometry(QRect(470, 180, Xbsize, Ybsize))

        self.B32 = QPushButton(self.frame)
        self.B32.setGeometry(QRect(530, 180, Xbsize, Ybsize))

        self.B33 = QPushButton(self.frame)
        self.B33.setGeometry(QRect(590, 180, Xbsize, Ybsize))

        self.B34 = QPushButton(self.frame)
        self.B34.setGeometry(QRect(650, 180, Xbsize, Ybsize))

        self.B35 = QPushButton(self.frame)
        self.B35.setGeometry(QRect(710, 180, Xbsize, Ybsize))

        self.B36 = QPushButton(self.frame)
        self.B36.setGeometry(QRect(710, 90, Xbsize, Ybsize))

        self.B37 = QPushButton(self.frame)
        self.B37.setGeometry(QRect(650, 90, Xbsize, Ybsize))

        self.B38 = QPushButton(self.frame)
        self.B38.setGeometry(QRect(590, 90, Xbsize, Ybsize))

        self.B39 = QPushButton(self.frame)
        self.B39.setGeometry(QRect(530, 90, Xbsize, Ybsize))

        self.B40 = QPushButton(self.frame)
        self.B40.setGeometry(QRect(470, 90, Xbsize, Ybsize))

        self.B41 = QPushButton(self.frame)
        self.B41.setGeometry(QRect(410, 90, Xbsize, Ybsize))

        self.B42 = QPushButton(self.frame)
        self.B42.setGeometry(QRect(350, 90, Xbsize, Ybsize))

        self.B43 = QPushButton(self.frame)
        self.B43.setGeometry(QRect(290, 90, Xbsize, Ybsize))

        self.B44 = QPushButton(self.frame)
        self.B44.setGeometry(QRect(230, 90, Xbsize, Ybsize))

        self.B45 = QPushButton(self.frame)
        self.B45.setGeometry(QRect(170, 90, Xbsize, Ybsize))

        self.B46 = QPushButton(self.frame)
        self.B46.setGeometry(QRect(110, 90, Xbsize, Ybsize))

        self.B47 = QPushButton(self.frame)
        self.B47.setGeometry(QRect(50, 90, Xbsize, Ybsize))

        self.B48 = QPushButton(self.frame)
        self.B48.setGeometry(QRect(330, 380, Xbsize, Ybsize))

        self.BAP1 = QPushButton(self.frame)
        self.BAP1.setGeometry(QRect(110, 730, Xbsize, Ybsize))

        self.BAP2 = QPushButton(self.frame)
        self.BAP2.setGeometry(QRect(50, 730, Xbsize, Ybsize))


# 3

        c.execute("SELECT habitacion, tipo FROM habitaciones")
        habitaciones = c.fetchall()

        for hab in habitaciones:
            eval(f"self.B{hab[0]}").setCursor(
                QCursor(Qt.PointingHandCursor))
            eval(f"self.B{hab[0]}").clicked.connect(self.hab_clicked)
            eval(f"self.B{hab[0]}").setText(f"{hab[0]}\n{hab[1][:2].upper()}")


# -------------------------------------------------------------------------------------------

        c.execute(
            "SELECT identificador FROM usuarios WHERE habilitado is TRUE ORDER BY rol DESC, identificador asc")
        users = c.fetchall()

        flat_list = [i for sub in users for i in sub]

        self.input_usuario.clear()
        self.input_usuario.addItems(flat_list)
        self.input_usuario.setEditable(False)

# -------------------------------------------------------------------------------------------

        # Fetch payment methods ordered by their index
        c.execute("SELECT descripcion, tipo FROM metodos_pago ORDER BY `index`")
        metodos_pago = c.fetchall()

        # Separate payment methods by type
        hab_methods = [desc for desc, tipo in metodos_pago if tipo == "hab"]
        extra_methods = [desc for desc,
                         tipo in metodos_pago if tipo == "extra"]

        # Assign widgets
        FP_labels = [self.PagoWindow.FP1, self.PagoWindow.FP2,
                     self.PagoWindow.FP3, self.PagoWindow.FP4]
        FP_extras_labels = [self.PagoWindow.extra1,
                            self.PagoWindow.extra2, self.PagoWindow.extra3]

        # Fill "hab" combo boxes
        for idx, combo in enumerate(FP_labels):
            combo.clear()
            combo.addItems(hab_methods)
            if idx < len(hab_methods):
                combo.setCurrentIndex(idx)

        # Fill "extra" combo boxes
        for idx, combo in enumerate(FP_extras_labels):
            combo.clear()
            combo.addItems(extra_methods)
            if idx < len(extra_methods):
                combo.setCurrentIndex(idx)

        self.PagoWindow.reset_datos()

# -------------------------------------------------------------------------------------------
        c.execute(f"SELECT habitacion FROM habitaciones")
        habitaciones = c.fetchall()
        flat_habitaciones = [i for sub in habitaciones for i in sub]

        self.SettingsWindow.precios_table.setVerticalHeaderLabels(
            flat_habitaciones)

        c.execute(
            "SELECT * FROM habitaciones")
        data = c.fetchall()

        self.SettingsWindow.precios_table.setRowCount(len(data))

        table_row = 0
        for row in data:
            self.SettingsWindow.precios_table.setItem(
                table_row, 0, QTableWidgetItem(row[0]))
            self.SettingsWindow.precios_table.setItem(
                table_row, 1, QTableWidgetItem(row[1]))
            self.SettingsWindow.precios_table.setItem(
                table_row, 2, QTableWidgetItem(str(row[2])))
            self.SettingsWindow.precios_table.setItem(
                table_row, 3, QTableWidgetItem(str(row[3])))
            self.SettingsWindow.precios_table.setItem(
                table_row, 4, QTableWidgetItem(row[4]))
            self.SettingsWindow.precios_table.setItem(
                table_row, 5, QTableWidgetItem(str(row[5])))
            table_row += 1

        self.SettingsWindow.inventario_table.resizeColumnsToContents()

        self.SettingsWindow.fill_table(
            self.SettingsWindow.inventario_table, "inventario", 6)

        self.SettingsWindow.fill_table(
            self.SettingsWindow.voucher_table, "vouchers", 4)

# -----------------------------------------------------------------------------------------------------------------

        # c.execute(
        #     "SELECT FP1, FP2, FP3, FP4, FP5, otros FROM config")
        # data = c.fetchone()

        # freportes = [self.SettingsWindow.bFP1, self.SettingsWindow.bFP2,
        #              self.SettingsWindow.bFP3, self.SettingsWindow.bFP4]

        # x = 0
        # for i in freportes:
        #     i.setText(data[x])
        #     x += 1

# -----------------------------------------------------------------------------------------------------------------

        c.execute(
            "SELECT * FROM config")
        config_table = c.fetchall()

        settings_inputs = {
            "hotel_nombre": self.SettingsWindow.input_hotel_nombre,
            "hotel_rif": self.SettingsWindow.input_hotel_rif,
            "hotel_direccion_fiscal":  self.SettingsWindow.input_hotel_direccion_fiscal,
            "hotel_estado":  self.SettingsWindow.input_hotel_estado,
            "hotel_ciudad":  self.SettingsWindow.input_hotel_ciudad,
            "hotel_municipio":  self.SettingsWindow.input_hotel_municipio,
            "hotel_parroquia":  self.SettingsWindow.input_hotel_parroquia,
            "hotel_telefono":  self.SettingsWindow.input_hotel_telefono,
            "hotel_correo":  self.SettingsWindow.input_hotel_correo,
            "hotel_whatsapp":  self.SettingsWindow.input_hotel_whatsapp,
            "hotel_instagram":  self.SettingsWindow.input_hotel_instagram,
            "url_reportes":  self.SettingsWindow.input_reportes,
            "tiempo_parcial":  self.SettingsWindow.input_tiempo_parcial,
            "camera_entrada": self.SettingsWindow.input_camera_url_entrada,
            "camera_salida": self.SettingsWindow.input_camera_url_salida,
            "tg_chat_id": self.SettingsWindow.input_chat_id,
            "tg_bot_token":  self.SettingsWindow.input_bot_token,
            "drive_folder_id":  self.SettingsWindow.input_drive_folder_id,
            "sound_path":  self.SettingsWindow.input_sound_path,
            "dolar_automatico_hora":  self.SettingsWindow.input_schedule_dolar_bcv,
            "tg_chucherias":  self.SettingsWindow.input_tg_chucherias,
            "tg_chat":  self.SettingsWindow.input_telegram,
            "tg_camera":  self.SettingsWindow.input_tg_camera_entrada,
            "drive":  self.SettingsWindow.input_drive_backup,
            "music":  self.SettingsWindow.input_sound,
            "dolar_automatico":  self.SettingsWindow.schedule_dolar_bcv,
            "wchucherias": self.SettingsWindow.input_chucherias,
            "tv_display": self.SettingsWindow.tv_display,
            "tv_display_url": self.SettingsWindow.input_tv_display,
        }

        instances = []
        # Iterar sobre lista1_data
        for config_key, config_value in config_table:
            # Obtener el valor de settings_inputs_dict si la clave existe, sino None
            instance = settings_inputs.get(config_key)
            instances.append((config_key, config_value, instance))

        for i in instances:
            if isinstance(i[2], QLineEdit):
                i[2].setText(str(i[1]))

            elif isinstance(i[2], QSpinBox):
                i[2].setValue(int(i[1]))

            # elif isinstance(i[2], QTimeEdit):
            #     i[2].setTime(QTime(i[1]))

            elif isinstance(i[2], QCheckBox):
                if int(i[1]):
                    i[2].setChecked(True)
                else:
                    i[2].setChecked(False)

        # if config[34]:  # ChucheriasWindow
        #     self.SettingsWindow.input_chucherias.setChecked(True)
        #     self.wchucherias = True
        # else:
        self.wchucherias = False

# -----------------------------------------------------------------------------------------------------------------

        c.execute(
            "SELECT identificador FROM usuarios WHERE habilitado is TRUE ORDER BY rol DESC, identificador asc")
        users = c.fetchall()

        flat_list = [i for sub in users for i in sub]

        self.SettingsWindow.input_eliminar.clear()
        self.SettingsWindow.input_eliminar.addItems(flat_list)

# -------------------------------------------------------------------------------------------

        c.execute(
            "SELECT config_value FROM config WHERE config_key = 'hotel_nombre'")
        hotel_nombre = c.fetchone()[0]

        self.InformacionWindow.input_hotel.setText(hotel_nombre.title())

        self.sec_timer.timeout.connect(self.hab_color)
        self.sec_timer.timeout.connect(self.clock)

        self.clock()
        self.hab_color()

        self.show()

# -------------------------------------------------------------------------------------------
        c.execute(
            "SELECT config_value FROM config WHERE config_key = 'tv_display'")
        tv_display = c.fetchone()[0]

        if int(tv_display):
            flask_thread = threading.Thread(
                target=misk().iniciar_servidor_flask, daemon=True)
            flask_thread.start()

    ################################# SETING UP FUNCTIONS #################################

    def novedades(self):
        if self.usuario.text() == "Usuario":
            misk().errorMSG("Debes registrarte para poder seguir", "Recuerda Registrate")
            return

        self.NoticeIssueBoard.update_table()
        self.NoticeIssueBoard.usuario = self.usuario.text()
        self.NoticeIssueBoard.generate_mock_data()
        self.NoticeIssueBoard.show()
        self.NoticeIssueBoard.raise_()

    def start_Rtable(self):
        # if self.usuario.text() == "Usuario":
        #     misk().errorMSG("Debes registrarte para poder seguir", "Recuerda Registrate")
        #     return

        # self.ReservationsBoard.update_table()
        self.ReservationsBoard.usuario = self.usuario.text()
        self.ReservationsBoard.load_future_reservations()
        self.ReservationsBoard.show()
        self.ReservationsBoard.raise_()

    def dolar_bcv(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        url = "https://ve.dolarapi.com/v1/dolares/oficial"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            price = data.get("promedio")
            self.input_precio_dolar.setValue(price)

            if self.SettingsWindow.tv_display.isChecked():
                endpoint = f"{self.SettingsWindow.input_tv_display.text()}/api/update/tasa"
                payload = {"tasa_bcv": price}

                try:
                    response = requests.post(
                        endpoint, json=payload, timeout=10)
                    response.raise_for_status()
                    print(
                        f"   -> Servidor respondió: {response.json()['message']}")

                except requests.exceptions.RequestException as e:
                    print(f"   -> Error al enviar a la TV: {e}")

            self.dolar_actualizado()

        except requests.exceptions.Timeout:
            print("Error: El tiempo de espera ha expirado.")
            misk().errorMSG(
                "La conexión tardó demasiado en responder",
                "Error de Tiempo de Espera"
            )
        except requests.exceptions.RequestException as error:
            # Esto captura errores de conexión (ConnectionError, DNS, etc.) y HTTP
            print(f"Error al obtener datos: {error}")
            misk().errorMSG(
                f"No se puede ejecutar su orden debido a problemas con la conexión:\n{error}",
                "Error de Conexión"
            )
        finally:
            QApplication.restoreOverrideCursor()

    def calculator(self):
        if platform.system() == 'Windows':    # Windows
            subprocess.Popen('C:\\Windows\\System32\\calc.exe')
        else:                                 # linux variants
            os.system(f"galculator")

    def config(self):

        if self.cargo.text() == "administrador":
            self.SettingsWindow.show()
            self.SettingsWindow.raise_()

        else:
            misk().errorMSG("Debe ser administrador para poder ingresar en este apartado",
                            "Cargo insuficiente")

    def config_inventario(self):

        if self.cargo.text() == "administrador":
            self.SettingsWindow.show()
            self.SettingsWindow.tabWidget.setCurrentIndex(2)
            self.SettingsWindow.raise_()

        else:
            misk().errorMSG("Debe ser administrador para poder ingresar en este apartado",
                            "Cargo insuficiente")

    def clock(self):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        # --- Check timeout for parcial ---
        # Se une current_habitaciones con estancias, luego con estancia_habitaciones para obtener fecha_fin_planificada
        # Asumiendo que current_habitaciones.id_estancia apunta directamente a estancias.id_estancia
        c.execute(
            '''
        SELECT 
            ch.habitacion, 
            eh.fecha_fin_planificada
        FROM 
            current_habitaciones ch -- Tabla con estado actual de habitaciones
        JOIN 
            estancias e ON e.id_estancia = ch.id_estancia -- Unión directa con estancias
        JOIN
            estancia_habitaciones eh ON e.id_estancia = eh.id_estancia -- Unión con usos de habitación
        WHERE 
            ch.estado = "parcial" -- Filtrar por estado en current_habitaciones
            AND eh.fecha_fin_real IS NULL -- Solo habitaciones activas en estancia_habitaciones
        ''')
        time_parciales = c.fetchall()
        parciales_count = len(time_parciales)

        self.timeout_list = []
        for i in time_parciales:

            dt_to_time = QDateTime.fromString(
                # i[1] es ahora fecha_fin_planificada
                str(i[1]), "yyyy-MM-dd hh:mm:ss")

            self.timeout_list.append(
                [i[0], f" {dt_to_time.toString('hh:mm')} / {round((QTime.secsTo(QTime.currentTime(), dt_to_time.time()))/60)} min"])

            if QDateTime.currentDateTime().secsTo(dt_to_time.addSecs(-900)) == 0:

                misk().errorMSG(
                    f"Recuerde que la parcial de la habitación {i[0]}\nsale a las {dt_to_time.toString('hh:mm')}", "Recordatorio")

            elif QDateTime.currentDateTime().secsTo(dt_to_time) == 0:
                misk().errorMSG(
                    f"Recuerde que ya es hora de que la parcial de la habitación {i[0]}\nsalga o renueve", "Recordatorio")

            elif QDateTime.currentDateTime().secsTo(dt_to_time.addSecs(600)) == 0:
                misk().errorMSG(
                    f"Recuerde que ya han pasado 10 minutos y la parcial de la habitación {i[0]}\ntiene que salir o renovar", "Recordatorio")
                misk().tg_message(
                    f"⚠ El cliente de la habitación {i[0]} de tipo parcial tenia que salir hace 10 minutos y aún no ha salido ⚠")

        # --- Check timeout for hospedaje ---
        # Similar a parcial, pero filtrando por hospedaje y fecha_fin_planificada = hoy
        # Asumiendo que current_habitaciones.id_estancia apunta directamente a estancias.id_estancia
        c.execute(
            '''
            SELECT COUNT(*) 
            FROM current_habitaciones ch -- Tabla con estado actual de habitaciones
            JOIN estancias e ON e.id_estancia = ch.id_estancia -- Unión directa con estancias
            JOIN estancia_habitaciones eh ON e.id_estancia = eh.id_estancia -- Unión con usos de habitación
            WHERE ch.estado = 'hospedaje' -- Filtrar por estado en current_habitaciones
                AND DATE(eh.fecha_fin_planificada) = CURDATE() -- Filtrar por fecha de hoy en estancia_habitaciones
                AND eh.fecha_fin_real IS NULL -- Solo habitaciones activas en estancia_habitaciones
            '''
        )
        time_hospedajes = c.fetchone()[0]

        # Añadir aquí la lógica para time_hospedajes si es necesario
        # Por ejemplo:
        if time_hospedajes > 0:
            current_time = QTime.currentTime()
            reminder_times = {
                QTime(12, 45, 00): "Recuerdele a los clientes en hospedaje que\nen 15 minutos tienen que salir o renovar",
                QTime(13, 00, 00): "Recuerde que ya es hora de que los\nhospedajes se vayan o renueven",
                QTime(13, 10, 00): "Recuerde que ya han pasado 10 minutos y\nlos hospedajes aún no se han ido o renovado"
            }

            for reminder_time, message in reminder_times.items():
                if current_time.secsTo(reminder_time) == 0:
                    misk().errorMSG(message, "Recordatorio")
                    # Only send Telegram message at 13:10
                    if reminder_time == QTime(13, 10, 00):
                        misk().tg_message(
                            f"⚠ Existen {time_hospedajes} clientes de tipo hospedaje que no se han ido y ya han pasado su tiempo por 10 minutos ⚠"
                        )

# ------------------------------------ Count Colored Habs ------------------------------------

        self.lcd_parciales.setText(str(parciales_count))

        c.execute("""
            SELECT 
                COUNT(CASE WHEN estado = 'hospedaje' THEN 1 END) AS hospedajes_count,
                COUNT(CASE WHEN estado = 'sucia' THEN 1 END) AS sucias_count,
                COUNT(CASE WHEN estado = 'bloqueada' THEN 1 END) AS bloqueadas_count,
                COUNT(CASE WHEN estado = 'retoque' THEN 1 END) AS retoque_count,
                COUNT(CASE WHEN estado IS NULL THEN 1 END) AS libres_count
            FROM current_habitaciones
        """)

        hospedajes_count, sucias_count, bloqueadas_count, retoque_count, libres_count = c.fetchone()

        c.execute("SELECT COUNT(estado) FROM estancias WHERE estado = 'reservada'")
        reservadas_count = c.fetchone()[0]

        self.lcd_hospedajes.setText(str(hospedajes_count))
        self.lcd_mantenimiento.setText(str(retoque_count))
        self.lcd_sucias.setText(str(sucias_count))
        self.lcd_bloqueadas.setText(str(bloqueadas_count))
        self.lcd_reservadas.setText(str(reservadas_count))
        self.lcd_libres.setText(str(libres_count))

# ------------------------------------ Check dolar automatico ------------------------------------

        # c.execute(
        #     "SELECT dolar_automatico, HOUR(hora_dolar_automatico) AS hour, MINUTE(hora_dolar_automatico) AS minute, SECOND(hora_dolar_automatico) AS second FROM config")
        # dolar_automatico = (c.fetchone())

        c.execute(
            "SELECT config_value FROM config WHERE config_key = 'dolar_automatico'")
        dolar_automatico = c.fetchone()[0]

        # # TODO CONF
        # if int(dolar_automatico[0]) == True:
        #     c.execute(
        #         "SELECT HOUR(config_value) AS hour, MINUTE(config_value) AS minute, SECOND(config_value) AS second FROM config WHERE config_key = 'dolar_automatico_hora'")
        #     hora_dolar_automatico = c.fetchone()

        #     if QTime.currentTime().secsTo(QTime(hora_dolar_automatico[0], hora_dolar_automatico[1], hora_dolar_automatico[2])) == 0:
        #         self.dolar_bcv()

        c.close()
        db.close()

# ------------------------------------ Fill up TimeOutTable ------------------------------------

        self.timeout_table.setRowCount(len(self.timeout_list))
        table_row = 0
        for row in self.timeout_list:
            row_item = 0
            for i in row:
                item = QTableWidgetItem(row[row_item])
                self.timeout_table.setItem(
                    table_row, row_item, item)
                item.setTextAlignment(Qt.AlignHCenter)
                row_item += 1
            table_row += 1

    def dialog_porton(self, tipo_porton):
        if self.usuario.text() == "Usuario":
            misk().errorMSG("Debes registrarte para poder seguir", "Recuerda Registrate")
            return

        tipos_identificadores = []

        def personas_seleccionadas():
            seleccionados = []
            for i in range(self.identificador_layout.count()):
                chk = self.identificador_layout.itemAt(i).widget()
                if isinstance(chk, QCheckBox) and chk.isChecked():
                    persona = {
                        'rol': input_rol.currentText(),
                        'nombre': chk.text(),
                        'identificador': chk.objectName()
                    }
                    seleccionados.append(persona)
            return seleccionados

        def start():
            db = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )
            c = db.cursor()

            if tipo_porton == "ENTRADA":
                c.execute('''
                        SELECT 'cliente' as 'rol', CONCAT('HAB ', habitacion) as 'nombre', id_estancia as 'identificador'
                        FROM current_habitaciones WHERE id_estancia IS NOT null AND ('cliente', id_estancia ) NOT IN (
                            SELECT rol, identificador FROM current_personas)
                        UNION
                        SELECT rol as 'rol', identificador as 'nombre', identificador as identificador 
                        FROM usuarios
                        WHERE (identificador) NOT IN (
                            SELECT identificador FROM current_personas);
                        ''')
            elif tipo_porton == "SALIDA":
                c.execute(
                    "SELECT rol, nombre, identificador FROM current_personas")

            resultados = c.fetchall()
            tipos_identificadores.clear()
            tipos_identificadores.extend(resultados)
            tipos_identificadores.extend(
                [('Otros', 'Delivery', 'Delivery'), ('Otros', 'Taxi', 'Taxi'), ('Otros', 'Otros', 'Otros')])

            # --- Poblamos los roles ---
            input_rol.clear()
            rols_unicos = sorted(set(t[0] for t in tipos_identificadores))
            input_rol.addItems(rols_unicos)

            # --- Poblamos los checkboxes ---
            update_identificador()

            if resultados:
                dlg.exec()
            else:
                misk().errorMSG("No hay personas dentro del Hotel", "Hotel Vacio")

        # 2. Función de actualización

        def update_identificador():
            # Limpia los checkboxes viejos
            for i in reversed(range(self.identificador_layout.count())):
                w = self.identificador_layout.itemAt(i).widget()
                if w:
                    w.setParent(None)
            # Crea uno por cada identificador válido
            selected_tipo = input_rol.currentText()
            for tipo, nombre, indet in tipos_identificadores:
                if tipo == selected_tipo:
                    chk = QCheckBox(nombre)
                    chk.setObjectName(indet)
                    self.identificador_layout.addWidget(chk)

        def accion_porton():
            # Obtenemos todos los identificadores marcados
            personas = personas_seleccionadas()

            if not personas:
                misk().errorMSG("Debe seleccionar al menos un identificador", "Sin selección")
                return

            elif input_rol.currentText() == "Otros" and input_observaciones.toPlainText() == "":
                misk().errorMSG("Debe rellenar las Observaciones al seleccionar ROL Otros",
                                "Observaciones Requeridas")
                return

            misk().abrir_porton(
                self.usuario.text(),
                personas,
                tipo_porton,
                input_observaciones.toPlainText()
            )
            dlg.close()
            print(personas)

            # misk().informationMSG("Proceso realizado con exito!", "Proceso Exitoso")

        dlg = QDialog(self)
        dlg.setMinimumSize(400, 200)
        dlg.setWindowTitle(f"Portón {tipo_porton}")

        layout = QFormLayout(dlg)

        dlg.setStyleSheet('''
        QPushButton {
            font-size: 14px;
            font-weight: bold;          
        }
        QLabel {
            background: rgba(0, 0, 0, 0);
            color: rgb(242, 242, 242);
            font-size: 14px;
            font-weight: bold
        }
        ''')

        # 1. Definición de los widgets
        tipo = QLabel("Tipo")
        input_rol = QComboBox()
        input_rol.currentIndexChanged.connect(update_identificador)
        layout.addRow(tipo, input_rol)

        identificador = QLabel("Identificador")
        layout.addRow(identificador)
        # Contenedor para los checkboxes
        identificador_group = QGroupBox()
        identificador_layout = QVBoxLayout()
        identificador_group.setLayout(identificador_layout)
        # Si esperas muchos items, podrías envolverlo en un QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(identificador_group)
        layout.addRow(scroll)

        # Guardamos referen­cias para usarlas en la función
        self.identificador_layout = identificador_layout

        input_observaciones = QPlainTextEdit()
        input_observaciones.setFixedHeight(70)
        input_observaciones.setPlaceholderText("Observaciones...")
        layout.addRow(input_observaciones)

        bvehicular = QPushButton("Abrir Portón")
        bvehicular.clicked.connect(accion_porton)
        bvehicular.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addRow(bvehicular)

        start()
        update_identificador()

    def FAQ(self):
        filenames = next(os.walk(f"tutorials/"),
                         (None, None, []))[2]
        question, ok = QInputDialog.getItem(
            self, 'Preguntas Frecuentes', 'Que quisiera saber?', filenames)

        if ok == True:
            if platform.system() == 'Windows':    # Windows
                os.startfile(
                    f"C:/Users/Cattivellio/Google Drive/{question}")
            else:                                   # linux variants
                subprocess.call(
                    ("xdg-open", "C:/Users/Cattivellio/Desktop/Family/daniella.jpg"))

    def tg_usuario_message(self):

        if self.usuario.text() == "Usuario":
            misk().errorMSG("Debes registrarte para poder seguir", "Recuerda Registrate")

        else:
            self.start = False
            text, ok = QInputDialog.getText(
                self, 'Enviar mensaje', 'Escriba su mensaje')

            if ok == True:
                misk().tg_message(
                    f"<b>{self.usuario.text()}</b> manda un mensaje diciendo: \n<b>{text}</b>")
                misk().informationMSG(
                    "Mensaje en proceso de envio, puede cerrar esta pestaña", "Procesando mensaje")

    def dolar_actualizado(self):

        self.PagoWindow.dolarprice = self.input_precio_dolar.value()
        misk().informationMSG(
            "El Dolar fue actualizado con Exito", "Dolar Actualizado")

    def hab_color(self):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute('''
            SELECT 
                ch.habitacion, 
                ch.estado, 
                eh.fecha_fin_planificada,
                ch.id_estancia -- Opcional: si necesitas el id_estancia en self.gradient_preset
            FROM 
                current_habitaciones ch -- Tabla con estado actual de habitaciones
            LEFT JOIN 
                estancias e ON e.id_estancia = ch.id_estancia -- Unión directa con estancias
            LEFT JOIN
                estancia_habitaciones eh ON e.id_estancia = eh.id_estancia AND eh.fecha_fin_real IS NULL -- Solo la fila activa de la estancia
        ''')

        data = c.fetchall()

        for i in data:
            # i[0] = habitacion # i[1] = estado # i[2] = fecha_fin_planificada (dtsalida) # i[3] = estancia

            if i[1] == 'parcial':
                self.gradient_preset(
                    i[0], "rgb(180, 20, 20)", "rgb(60, 0, 0)", i[2])

            elif i[1] == 'hospedaje':
                self.gradient_preset(
                    i[0], "rgb(189, 195, 199)", "rgb(36, 54, 70)", i[2])

            elif i[1] == 'sucia':
                self.gradient_preset(
                    i[0], "rgb(220, 82, 45)", "rgb(70, 40, 20)", i[2])

            elif i[1] == 'retoque':
                self.gradient_preset(
                    i[0], "rgb(120, 40, 240)", "rgb(60, 10, 100)", i[2])

            elif i[1] == 'bloqueada':
                self.gradient_preset(
                    i[0], "rgb(10, 10, 10)", "rgb(0, 0, 0)", i[2])
            else:
                self.gradient_preset(
                    i[0], "rgb(5, 117, 230)", "rgb(2, 27, 121)", i[2])

    def gradient_preset(self, hab, color1, color2, pasada_tiempo):

        border = "none"

        if pasada_tiempo:
            pasada_tiempo = True if QDateTime.currentDateTime().secsTo(
                pasada_tiempo) < 0 else False
            border = "5px solid rgb(242, 5, 5)" if pasada_tiempo else "none"

        eval(f"self.B{hab}").setStyleSheet(f'''
                QPushButton {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 {color1}, stop:1 {color2});
                    color: rgb(242, 242, 242);
                    border-radius: 2px;
                    font-size: 16px;
                    font-weight: bold;
                    border: {border};
                }}
                QPushButton:hover {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.5, y2:1.5, stop:0 {color1}, stop:1 {color2});
                    font-size: 19px;
                }}
                QPushButton:pressed {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.8, y2:0.8, stop:0 {color1}, stop:1 {color2});
                    font-size: 14px;
                }}''')

    def cambio_usuario(self):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute(
            f"SELECT identificador, clave, rol FROM usuarios WHERE identificador = '{self.input_usuario.currentText()}'")

        data = c.fetchone()

        if data[2] == "administrador":
            self.start = False
            text, ok = QInputDialog.getText(
                self, 'Ingrese su contraseña', 'Contraseña', QLineEdit.Password, "")

            if ok == True:
                if text != data[1]:
                    misk().errorMSG("La clave ingresada fue incorrecta", "Clave Invalida")
                else:
                    self.usuario.setText(data[0])
                    self.cargo.setText(data[2])

        else:
            self.usuario.setText(data[0])
            self.cargo.setText(data[2])

        self.SettingsWindow.usuario = data[0]

    def cambio_turno_type(self):

        if self.usuario.text() == "Usuario":
            misk().errorMSG("Debes registrarte para poder seguir", "Recuerda Registrate")

        else:
            question = misk().questionMSG(
                "Esta seguro de cambiar el turno? Al estar deacuerdo\nse creara un reporte de sus ventas", "Cambio de Turno")

            if question == QMessageBox.Ok:

                db = mc.connect(
                    host=host_ip,
                    user=database_user,
                    password=database_password,
                    database="esmeralda_software",
                    use_pure=True
                )

                c = db.cursor()

                c.execute(
                    "SELECT identificador FROM usuarios WHERE habilitado = TRUE")
                tuple_list = c.fetchall()
                list_users = [i[0] for i in tuple_list]

                self.start = False
                usuario, ok = QInputDialog.getItem(
                    self, "Cambio de turno", "Seleccione quien comenzara el nuevo turno:", list_users)

                if ok == True:

                    cl = QLocale(QLocale.Spanish)
                    viejo_usuario = self.usuario.text()

                    c.execute(
                        "SELECT datetime FROM usuario_log WHERE descripcion = 'cambio de turno realizado' ORDER BY datetime DESC LIMIT 1")
                    last_cambio_turno = c.fetchone()[0]

                    # ------------------------------------ Turno ------------------------------------
                    self.cambio_turno(
                        last_cambio_turno,
                        f"Acaba de finalizar el turno de <b>{self.usuario.text()} {last_cambio_turno.strftime('%H:%M')}-{QTime.toString(QTime.currentTime(), 'hh:mm')} | {last_cambio_turno.strftime('%d/%m/%Y')}</b> 💰",
                        False)

                    if last_cambio_turno.date() != QDate.currentDate().toPython():

                        # ------------------------------------ Semanal ------------------------------------

                        if True: #cl.toString(QDate.currentDate(), 'dddd') == "lunes":

                            c.execute(
                                f"SELECT datetime FROM usuario_log WHERE descripcion = 'cambio de turno realizado' AND datetime >= '{QDate.currentDate().addDays(-7).toString('yyyy-MM-dd')} 00:00:00' AND datetime < '{QDate.currentDate().addDays(-7).toString('yyyy-MM-dd')} 23:59:59'")
                            from_datetime_list = c.fetchone()

                            if from_datetime_list:
                                from_datetime = from_datetime_list[0]

                            else:
                                from_datetime = QDateTime.currentDateTime().addDays(-7).toPython()

                            self.cambio_turno(
                                from_datetime,
                                f"Acaba de terminar la <b>Semana {QDate.toString(QDate.currentDate().addDays(-7), 'dd-MM')} al {QDate.toString(QDate.currentDate(), 'dd-MM')}</b> 💰",
                                "la Semana")
                        # ------------------------------------ Mensual ------------------------------------
                        if QDate.toString(QDate.currentDate(), 'dd') == "01":
                            last_month = cl.toString(
                                QDate.currentDate().addMonths(-1), 'MMMM').title()

                            c.execute(
                                f"SELECT datetime FROM usuario_log WHERE descripcion = 'cambio de turno realizado' AND datetime >= '{QDate.currentDate().addMonths(-1).toString('yyyy-MM-01')} 00:00:00' AND datetime < '{QDate.currentDate().addMonths(-1).toString('yyyy-MM-01')} 23:59:59'")
                            from_datetime = c.fetchone()

                            if from_datetime:
                                from_datetime = from_datetime[0]
                            else:
                                from_datetime = QDateTime.currentDateTime().addMonths(-1).toPython()

                            self.cambio_turno(
                                from_datetime,
                                f"Acaba de terminar <b>{last_month}</b> 💰",
                                last_month
                            )

                    # ------------------------------------ Add to Log ------------------------------------

                    misk().registrar_log("usuario", viejo_usuario, "cambio de turno realizado", usuario)

                    misk().tg_message(
                        f"Esta empezando el turno de <b>{usuario} {QDate.currentDate().toString('dd-MM-yy')}</b> 😁")

                    c.execute(
                        f"SELECT rol FROM usuarios WHERE identificador = '{usuario}'")

                    data = c.fetchone()
                    self.usuario.setText(usuario)
                    self.cargo.setText(data[0])

                    self.input_usuario.setCurrentText(usuario)

                    db.commit()
                    c.close()
                    db.close()

                    # misk().backup_database_excel()

    def cambio_turno(self, from_datetime, message, extra_tiempo):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        # --- Reporte de pagos ---
        # Se une historial_pagos con historial_transacciones, luego con estancias para filtrar por fecha_inicio_real
        c.execute(f'''
                    SELECT 
                        mp.descripcion,
                        CONCAT(
                            ROUND(SUM(
                                CASE 
                                    WHEN LOWER(mp.moneda) = 'usd' THEN p.monto
                                    WHEN LOWER(mp.moneda) = 'bs' THEN p.monto / p.tasa
                                    ELSE p.monto
                                END
                            ), 2),
                            ' ',
                            mp.moneda
                        ) AS total
                    FROM historial_pagos p
                    JOIN historial_transacciones ht ON p.id_historial = ht.transaccion
                    JOIN estancias e ON ht.id_estancia = e.id_estancia
                    JOIN metodos_pago mp ON mp.descripcion = p.descripcion
                    WHERE 
                        e.fecha_inicio_real BETWEEN %s AND %s
                    GROUP BY mp.descripcion, mp.moneda;
                    ''', (from_datetime, QDateTime.currentDateTime().toPython()))
        transaciones = c.fetchall()

        # --- Contar clientes (estancias) ---
        # Contar estancias iniciadas en el rango
        c.execute(
            f"SELECT COUNT(*) FROM estancias WHERE fecha_inicio_real BETWEEN %s AND %s", (from_datetime, QDateTime.currentDateTime().toPython()))
        cantidad_clientes = c.fetchone()[0]

        if cantidad_clientes:

            # ------------------------------------ Telegram ------------------------------------
            formatted_output = "\n".join(
                f"• <b>{entry[0]}:</b> {entry[1]}$" for entry in transaciones
            )

            misk().tg_message(f'''
    {message}

    {formatted_output}

    Clientes ingresados: {cantidad_clientes}''')


        else:
            misk().tg_message(f"{message}\n\n No hubieron ingresos 😔")
            misk().errorMSG("No hay historial de ingresos", "Historial Vacio")

        # Cerrar conexión
        c.close()
        db.close()

    def hab_clicked(self):

        if self.usuario.text() == "Usuario":
            misk().errorMSG("Debes registrarte para poder seguir", "Recuerda Registrate")
            return

        elif self.input_precio_dolar.value() == 0.00:
            misk().errorMSG("Valor de dolar no ingrasado. Recueda precionar <b>ACTUALIZAR</b>", "Dolar Invalido")
            return

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        self.PagoWindow.close()

        # Obtener estado y id_estancia de la habitación
        # Asumiendo que current_habitaciones ahora tiene id_estancia y la FK apunta a estancias.id_estancia
        c.execute(
            f"SELECT estado, id_estancia FROM current_habitaciones WHERE habitacion = %s", (self.sender().text()[:-3],))
        estado = c.fetchone()[0]
        # id_estancia = c.fetchone()[1]

        self.PagoWindow.input_habitacion.setText(
            f"{self.sender().text()[:-3]}")

        self.PagoWindow.brenovar.hide()
        self.PagoWindow.btrash.hide()

        self.PagoWindow.input_voucher.setEnabled(True)
        self.PagoWindow.valor_voucher.setVisible(False)

        self.PagoWindow.input_fentrada.setDateRange(
            QDate.currentDate(), QDate.currentDate().addMonths(2))

        if estado == 'parcial' or estado == 'hospedaje' or estado == 'retoque':

            QApplication.setOverrideCursor(Qt.WaitCursor)

            self.PagoWindow.input_fentrada.setDateRange(
                QDate.currentDate().addMonths(-1), QDate.currentDate().addMonths(2))

            c.execute(
                f'''
                SELECT
                    ch.habitacion,
                    e.id_estancia, -- Ahora obtenemos el id_estancia
                    e.tipo_estadia, -- estado de la estancia
                    e.usuario_registro, -- usuario
                    e.procedencia,
                    e.destino,
                    eh.fecha_inicio, -- dtentrada
                    eh.fecha_fin_planificada, -- dtsalida
                    eh.costo, -- hab_costo
                    h.observaciones, -- observaciones de la habitación
                    e.voucher, -- voucher
                    v.valor, -- valor del voucher
                    v.tipo, -- tipo del voucher
                    e.observaciones -- observaciones de la estancia
                FROM
                    current_habitaciones ch
                JOIN
                    estancias e ON ch.id_estancia = e.id_estancia -- Vinculación directa a estancias
                JOIN
                    estancia_habitaciones eh ON e.id_estancia = eh.id_estancia AND eh.habitacion = ch.habitacion AND eh.fecha_fin_real IS NULL -- Solo la fila activa de la habitación
                JOIN
                    habitaciones h ON ch.habitacion = h.habitacion
                LEFT JOIN
                    vouchers v ON e.voucher = v.codigo
                WHERE
                    ch.habitacion = %s
                    AND ch.id_estancia = e.id_estancia -- Aseguramos que es la estancia correcta
                ''', (self.sender().text()[:-3],)  # Pasamos id_estancia_db como parámetro
            )
            estancia = c.fetchone()
            print(estancia)

            # transaccion ya no se usa como identificador primario de la estancia
            # self.PagoWindow.transaccion = estancia[1] # Antiguo
            self.PagoWindow.id_estancia = estancia[1]  # Nuevo: id_estancia
            # self.PagoWindow.estancia = None # Esta línea ya no es necesaria

            # estado de la estancia
            self.PagoWindow.estadia_type.setText(estancia[2])

            # usuario_registro
            self.PagoWindow.input_atendido_por.setText(estancia[3])
            self.PagoWindow.input_atendido_por.setReadOnly(True)

            # procedencia
            self.PagoWindow.input_procedencia.setCurrentText(
                estancia[4])
            # destino
            self.PagoWindow.input_destino.setCurrentText(estancia[5])

            self.PagoWindow.bcambiar_hab.setHidden(False)

            # fecha_inicio (dtentrada)
            self.PagoWindow.input_fentrada.setDateTime(
                QDateTime(estancia[6]))
            self.PagoWindow.input_fentrada.setReadOnly(True)

            # fecha_fin_planificada (dtsalida)
            self.PagoWindow.input_fsalida.setDateTime(
                QDateTime(estancia[7]))
            self.PagoWindow.input_fsalida.setReadOnly(True)

            # costo (hab_costo)
            self.PagoWindow.costo_dolar.setText(f"{estancia[8]}$")

            if estancia[2] == "parcial":
                self.disable_button(self.PagoWindow.bparcial)
                self.PagoWindow.bhospedaje.setEnabled(True)
                self.PagoWindow.bhospedaje.setText("Pasar a Hospedaje")
                self.PagoWindow.bhospedaje.setStyleSheet(
                    '''background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(189, 195, 199), stop:1 rgb(36, 54, 70));
                    color: rgb(242, 242, 242);
                    font-size: 12px;''')
                self.PagoWindow.FRcosto.setStyleSheet('''
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(180, 20, 20), stop:1 rgb(60, 0, 0));
                    border-radius: 4px;
                    ''')

            elif estancia[2] == "hospedaje":
                self.disable_button(self.PagoWindow.bparcial)
                self.disable_button(self.PagoWindow.bhospedaje)
                self.PagoWindow.FRcosto.setStyleSheet('''
                    background-color:  qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(189, 195, 199), stop:1 rgb(36, 54, 70));
                    border-radius: 4px;
                    ''')
                self.PagoWindow.brenovar.show()

            # 1. Obtener todos los métodos de pago ordenados por índice
            c.execute(
                "SELECT descripcion, tipo FROM metodos_pago ORDER BY `index`")
            metodos_pago = c.fetchall()

            # Separar métodos por tipo
            hab_methods = [desc for desc,
                           tipo in metodos_pago if tipo == "hab"]
            extra_methods = [desc for desc,
                             tipo in metodos_pago if tipo == "extra"]

            c.execute(f"""
                SELECT mp.descripcion, COALESCE(SUM(hp.monto), 0) AS monto_total
                FROM metodos_pago mp
                LEFT JOIN historial_transacciones ht ON ht.id_estancia = %s -- Todos los contenedores de la estancia
                LEFT JOIN historial_pagos hp ON mp.descripcion = hp.descripcion AND hp.id_historial = ht.transaccion -- Todos los pagos de esos contenedores
                GROUP BY mp.descripcion -- Agrupar por método de pago
                ORDER BY monto_total DESC -- Ordenar por monto total pagado
            """, (self.PagoWindow.id_estancia,))  # Usamos id_estancia
            pagos_ordenados = c.fetchall()

            # 3. Limpiar y preparar todos los combobox y spinbox
            pagos_names = [
                [self.PagoWindow.FP1, self.PagoWindow.input_FP1],
                [self.PagoWindow.FP2, self.PagoWindow.input_FP2],
                [self.PagoWindow.FP3, self.PagoWindow.input_FP3],
                [self.PagoWindow.FP4, self.PagoWindow.input_FP4],
                [self.PagoWindow.extra1, self.PagoWindow.input_extra1],
                [self.PagoWindow.extra2, self.PagoWindow.input_extra2],
                [self.PagoWindow.extra3, self.PagoWindow.input_extra3],
            ]

            # Limpiar todos los combobox y spinbox
            for combo, spinbox in pagos_names:
                combo.clear()
                spinbox.setValue(0.0)

            # 4. Asignar métodos de pago a los combobox según su tipo
            # Para los primeros 4 (tipo "hab")
            for combo, _ in pagos_names[:4]:
                combo.addItems(hab_methods)

            # Para los últimos 3 (tipo "extra")
            for combo, _ in pagos_names[4:]:
                combo.addItems(extra_methods)

            # 5. Asignar los montos a los spinbox correspondientes, ordenados de mayor a menor
            for i, (descripcion, monto_total) in enumerate(pagos_ordenados):
                if i < len(pagos_names):  # Asegurarnos de no exceder el número de widgets
                    combo, spinbox = pagos_names[i]

                    # Buscar el índice del método de pago en el combobox
                    index = combo.findText(descripcion)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                        # Asignamos el monto total de la estancia
                        spinbox.setValue(float(monto_total))

            self.PagoWindow.dolarprice = self.input_precio_dolar.value()
            # observaciones de la habitación
            self.PagoWindow.observaciones_hab.setPlainText(estancia[9])

            if estancia[10]:  # voucher
                print(f"Voucher found: {estancia[10]}")
                self.PagoWindow.valor_voucher.setVisible(True)
                self.PagoWindow.input_voucher.setText(estancia[10])
                self.PagoWindow.valor_voucher.setText(
                    # valor y tipo del voucher
                    f"{estancia[11]}{estancia[12]}")

            self.PagoWindow.begresar.setEnabled(True)
            self.PagoWindow.begresar.setStyleSheet('''
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.8, y2:0.8, stop:1 #11998E, stop:0 #38ef7d);
                font-size: 18px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                font-size: 20px;
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.4, y2:0.4, stop:1 #11998E, stop:0 #38ef7d);
                font-size: 18px
            }
            ''')
            self.PagoWindow.bingresar.setEnabled(False)
            self.PagoWindow.bingresar.setStyleSheet('''
                background-color: black;
                color: rgb(242, 242, 242);
                border-radius: 2px;
                font-size: 18px;
                font-weight: bold;''')

            self.PagoWindow.input_estadia_dias.setReadOnly(True)
            # Calcular días usando las nuevas fechas
            self.PagoWindow.input_estadia_dias.setValue(
                QDateTime(estancia[6]).daysTo(QDateTime(estancia[7])))

            self.PagoWindow.btrash.show()

            # --- Consulta de clientes actualizada ---
            # Usar estancia_clientes (vinculado a id_estancia)
            c.execute(
                f'''
                    SELECT
                        c.cedula,
                        c.nombre,
                        DATE_FORMAT(c.fecha_nacimiento, '%d-%m-%Y') AS fecha_nacimiento,
                        c.nacionalidad,
                        c.estado_civil,
                        c.telefono,
                        c.profesion,
                        c.observaciones,
                        c.reputacion,
                        (SELECT COUNT(*)
                        FROM estancia_clientes ec2
                        JOIN estancias e2 ON ec2.id_estancia = e2.id_estancia
                        WHERE ec2.cliente = c.cedula AND e2.estado != 'cancelada') AS veces_repetido -- Opcional: excluir canceladas
                    FROM
                        estancias e -- La estancia real
                    JOIN
                        estancia_clientes ec ON e.id_estancia = ec.id_estancia -- Los clientes de esa estancia
                    JOIN
                        clientes c ON ec.cliente = c.cedula -- Datos del cliente
                    WHERE
                        e.id_estancia = %s -- Filtrar por la estancia específica
                ''', (self.PagoWindow.id_estancia,)  # Usamos id_estancia
            )

            clientes = c.fetchall()

            for index, cliente in enumerate(clientes):
                tab = self.PagoWindow.tab_huespedes.widget(index)

                tab.findChild(QLineEdit, "input_cedula").setText(
                    cliente[0])
                tab.findChild(QLineEdit, "input_cedula").setReadOnly(True)
                tab.findChild(QLineEdit, "input_nombre").setText(
                    cliente[1])

                tab.findChild(QDateEdit, "input_fnacimiento").setDate(
                    QDate.fromString(cliente[2], "dd-MM-yyyy"))
                tab.findChild(QComboBox, "input_nacionalidad").setCurrentText(
                    cliente[3])
                tab.findChild(QComboBox, "input_estado_civil").setCurrentText(
                    cliente[4])
                tab.findChild(QLineEdit, "input_telefono").setText(
                    cliente[5])
                tab.findChild(QComboBox, "input_profesion").setCurrentText(
                    cliente[6])
                tab.findChild(QPlainTextEdit, "observaciones_cliente").setPlainText(
                    cliente[7])
                self.PagoWindow.cliente_reputacion(index, cliente[8])
                tab.findChild(QPushButton, "historial").setText(
                    f"Vino {cliente[9]} veces")

            if estado == "retoque":
                self.PagoWindow.bretoque.setText("Realizar Retoque")
            else:
                self.PagoWindow.bretoque.setText("Solicitar Retoque")

            c.execute(
                f"SELECT identificador FROM current_personas WHERE identificador = %s",
                (self.PagoWindow.id_estancia,)
            )
            presensia = c.fetchone()

            if presensia:
                self.PagoWindow.input_precensia_huesped.setText("Presente")
            else:
                self.PagoWindow.input_precensia_huesped.setText("Ausente")

            # observaciones de la estancia
            self.PagoWindow.observaciones_transaccion.setPlainText(
                estancia[13])

            self.start_pago_window()

            QApplication.restoreOverrideCursor()

        elif estado == "sucia":
            question = misk().questionMSG(
                "Desea limpiar la habitación?", "Limpiar Habitación")

            if question == QMessageBox.Ok:
                c.execute(
                    f"UPDATE current_habitaciones SET estado = NULL WHERE habitacion = %s", (self.sender().text()[:-3],))
                # ------------------------------------ Add to Log -----------------------------------------

                misk().registrar_log("habitacion", self.usuario.text(),
                                     "habitacion paso a limpia", self.sender().text()[:-3])

        elif estado == 'bloqueada':

            c.execute(
                f"SELECT razon_bloqueo FROM habitaciones WHERE habitacion  = %s",
                (self.sender().text()[:-3],)
            )

            razon_bloqueo = c.fetchone()[0]

            question = misk().questionMSG("Esta habitación fue bloqueada debido a que \n" +
                                          razon_bloqueo +
                                          "\n\nDesea Debloquearla?", "Desbloquear Habitación")
            if question == QMessageBox.Ok:

                c.execute(
                    f"UPDATE current_habitaciones SET estado = NULL WHERE habitacion = %s", (self.sender().text()[:-3],))
                c.execute(
                    f"UPDATE habitaciones SET razon_bloqueo = NULL WHERE habitacion = %s", (self.sender().text()[:-3],))

                misk().tg_message(
                    f"Se Desbloqueó la habitación <b>{self.sender().text()[:-3]}</b>, la cual se habia bloqueado debido a que <b>{razon_bloqueo}</b> 🎉")

                # ------------------------------------ Add to Log -----------------------------------------

                misk().registrar_log("habitacion", self.usuario.text(),
                                     "habitacion desbloqueada", self.sender().text()[:-3])

        else:
            # Para habitaciones libres
            self.PagoWindow.input_atendido_por.setText(self.usuario.text())
            self.PagoWindow.input_fentrada.setDateTime(QDateTime.currentDateTime())
            self.PagoWindow.id_estancia = ""  # Nuevo: id_estancia vacío
            # self.PagoWindow.reset_datos()
            self.start_pago_window()

        db.commit()
        c.close()
        db.close()

    def disable_button(self, button):

        button.setEnabled(False)
        button.setText("Invalido")
        button.setStyleSheet(
            "QPushButton:disabled {background-color:black; font-size: 14px}")

    def open_informacion(self):
        self.InformacionWindow.show()

    def start_pago_window(self):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute(
            f"SELECT tipo FROM habitaciones WHERE habitacion = '{self.sender().text()[:-3]}'")
        hab_tipo = c.fetchone()

        self.PagoWindow.input_habitacion_tipo.setText(hab_tipo[0].title())

        if hab_tipo[0] == "parcial":
            self.PagoWindow.FRcosto.setStyleSheet('''
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(180, 20, 20), stop:1 rgb(60, 0, 0));
            border-radius: 4px;
            ''')
        elif hab_tipo[0] == "hospedaje":
            self.PagoWindow.FRcosto.setStyleSheet('''
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1.2, y2:1.2, stop:0 rgb(189, 195, 199), stop:1 rgb(36, 54, 70));
            border-radius: 4px;
            ''')

        c.execute(
            f"SELECT descripcion FROM habitaciones WHERE habitacion = '{self.sender().text()[:-3]}'")
        hab_desc = c.fetchone()[0]

        c.close()
        db.close()

        self.PagoWindow.hab_num = str(self.sender().text()[:-3])
        self.PagoWindow.input_habitacion_tipo.setToolTip(hab_desc)
        tab = self.PagoWindow.tab_huespedes.widget(0)
        tab.findChild(QLineEdit, "input_cedula").setFocus()

        self.PagoWindow.price_calculation()
        self.PagoWindow.show()
        self.PagoWindow.raise_()

    ################################# GLOBAL FUNCTIONS #################################


class InformacionWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Información')
        self.setFixedSize(800, 400)
        self.setAttribute(Qt.WA_QuitOnClose, False)

        self.setStyleSheet('''
        font-size: 20px
        ''')

        logopic = QLabel(self)
        logopic.setGeometry(QRect(26, 30, 280, 80))
        pixmap = QPixmap('img/banner.png')
        logopic.setPixmap(pixmap)

        # Optional, resize window to image size
        logopic.resize(pixmap.width(), pixmap.height())

        self.logo_version = QLabel(self)
        self.logo_version.setGeometry(QRect(350, 108, 280, 28))
        self.logo_version.setText(f"<i>{appversion}</i>")

        self.hotel = QLabel(self)
        self.hotel.setGeometry(QRect(46, 180, 50, 50))
        pixmap = QPixmap('img/hotelg.png')
        self.hotel.setPixmap(pixmap)
        self.hotel.resize(44, 44)
        self.hotel.setScaledContents(True)

        self.input_hotel = QLabel(self)
        self.input_hotel.setGeometry(QRect(110, 186, 300, 28))

        whatsapp = QLabel(self)
        whatsapp.setGeometry(QRect(46, 250, 50, 50))
        pixmap = QPixmap('img/whatsappg.png')
        whatsapp.setPixmap(pixmap)
        whatsapp.resize(44, 44)
        whatsapp.setScaledContents(True)

        input_whatsapp = QLabel(self)
        input_whatsapp.setGeometry(QRect(110, 256, 300, 28))
        input_whatsapp.setText("Daniell 0412-677-8168")

        self.bback_up = QPushButton(self)
        self.bback_up.setGeometry(QRect(110, 330, 276, 28))
        self.bback_up.setText("Realizar copia de seguridad en la Nube")
        self.bback_up.clicked.connect(self.back_up)
        self.bback_up.setCursor(QCursor(Qt.PointingHandCursor))
        self.bback_up.setStyleSheet("font-size: 14px")

        derechos = QLabel(self)
        derechos.setGeometry(QRect(0, 364, 500, 20))
        derechos.setAlignment(Qt.AlignCenter)
        derechos.setText(
            "© Esmeralda Software Todos los derechos reservados.")
        derechos.setStyleSheet("font-size: 14px")

    def back_up(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        misk().backup_database_excel()
        QApplication.restoreOverrideCursor()
        misk().informationMSG("Copia de seguridad realizada de forma exitosa",
                              "Copia de seguridad exitosa")


class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ajustes')
        self.resize(800, 0)
        self.setMinimumSize(QSize(464, 0))
        self.setAttribute(Qt.WA_QuitOnClose, False)

        self.usuario = None
        self.TableViewData = TableViewData()

        self.setStyleSheet('''
            QLabel {
            background: rgba(0, 0, 0, 0);
            color: rgb(242, 242, 242);
            font-size: 14px
            }
                        
                           ''')

        self.verticalLayout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)

        HspacerItem = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        VspacerItem = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

    #################################  #################################

        self.precios = QWidget()
        self.tabWidget.addTab(self.precios, "Habitaciones")
        self.gridLayout_7 = QGridLayout(self.precios)

# ---------------------------------------------------------------------------------------------------

        self.precios_table = QTableWidget(self.precios)
        self.precios_table.verticalHeader().setVisible(False)
        self.precios_table.setColumnCount(6)

        self.precios_table.setHorizontalHeaderItem(
            0, QTableWidgetItem("Hab"))
        self.precios_table.setHorizontalHeaderItem(
            1, QTableWidgetItem("Tipo"))
        self.precios_table.setHorizontalHeaderItem(

            2, QTableWidgetItem("Parcial"))
        self.precios_table.setHorizontalHeaderItem(
            3, QTableWidgetItem("Hospedaje"))
        self.precios_table.setHorizontalHeaderItem(
            4, QTableWidgetItem("Caracteristicas"))
        self.precios_table.setHorizontalHeaderItem(
            5, QTableWidgetItem("Hab Kit"))

        self.precios_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.precios_table.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)

        self.gridLayout_7.addWidget(self.precios_table, 0, 0, 1, 3)


# ---------------------------------------------------------------------------------------------------
        nota = QLabel(self.precios)
        self.gridLayout_7.addWidget(nota, 2, 0)
        nota.setText(
            "<b>Nota:</b> Recordar ingresar los montos en Dolares")

        self.bactualizar_precios = QPushButton(self.precios)
        self.bactualizar_precios.setText("Guardar")
        self.gridLayout_7.addWidget(self.bactualizar_precios, 2, 2)
        self.bactualizar_precios.clicked.connect(self.bactualizar)
# ---------------------------------------------------------------------------------------------------
        self.gridLayout_7.addItem(HspacerItem, 2, 1)
        self.gridLayout_7.addItem(VspacerItem, 1, 1)

    ################################# reportes #################################

        self.reportes = QWidget(self)
        self.tabWidget.addTab(self.reportes, "Reportes")
        self.grid_reportes = QGridLayout(self.reportes)

# ---------------------------------------------------------------------------------------------------

        tipos_reporte = QLabel(self)
        tipos_reporte.setText("Seleccionar tipo de reporte:")
        self.grid_reportes.addWidget(tipos_reporte, 0, 0, 1, 2)

        self.tipos_reporte_input = QComboBox(self)
        self.tipos_reporte_input.clear()
        self.tipos_reporte_input.addItems(
            ["Policial", "Ventas", "Acciones", "Clientes"])
        self.grid_reportes.addWidget(self.tipos_reporte_input, 1, 0)
        self.tipos_reporte_input.currentIndexChanged.connect(
            self.tipos_reporte_changed)

        limite = QLabel(self)
        limite.setText("Seleccionar Limite:")
        self.grid_reportes.addWidget(limite, 0, 1)

        self.limite_input = QSpinBox(self)
        self.limite_input.setMaximum(1000000)
        self.limite_input.setValue(100)
        self.grid_reportes.addWidget(self.limite_input, 1, 1)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.grid_reportes.addWidget(line, 3, 0, 1, 2)

# ---------------------------------------------------------------------------------------------------

        self.rango_tiempo = QLabel(self)
        self.rango_tiempo.setText("Seleccionar rango de tiempo:")
        self.grid_reportes.addWidget(self.rango_tiempo, 4, 0, 1, 2)

        self.reportes_desde = QLabel(self.reportes)
        self.grid_reportes.addWidget(self.reportes_desde, 5, 0)
        self.reportes_desde.setText("Desde")

        self.reportes_desde_input = QDateTimeEdit(self.reportes)
        self.reportes_desde_input.setCalendarPopup(True)
        self.reportes_desde_input.calendarWidget().setLocale(QLocale(QLocale.Spanish))
        self.reportes_desde_input.setMaximumDate(QDate.currentDate())
        self.reportes_desde_input.setDate(QDate.currentDate().addDays(-7))
        self.reportes_desde_input.setDisplayFormat("hh:mm dd-MM-yyyy")
        self.grid_reportes.addWidget(self.reportes_desde_input, 6, 0)

        self.reportes_hasta = QLabel(self.reportes)
        self.grid_reportes.addWidget(self.reportes_hasta, 5, 1)
        self.reportes_hasta.setText("Hasta")

        self.reportes_hasta_input = QDateTimeEdit(self.reportes)
        self.reportes_hasta_input.setCalendarPopup(True)
        self.reportes_hasta_input.calendarWidget().setLocale(QLocale(QLocale.Spanish))
        self.reportes_hasta_input.setMaximumDate(QDate.currentDate())
        self.reportes_hasta_input.setDate(QDate.currentDate())
        self.reportes_hasta_input.setDisplayFormat("hh:mm dd-MM-yyyy")
        self.grid_reportes.addWidget(self.reportes_hasta_input, 6, 1)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.grid_reportes.addWidget(line, 7, 0, 1, 2)

# ---------------------------------------------------------------------------------------------------

        self.formas_pago = QLabel(self)
        self.formas_pago.setText("Seleccionar formas de pago:")
        self.grid_reportes.addWidget(self.formas_pago, 8, 0, 1, 2)

        self.bFP1 = QCheckBox(self)
        self.grid_reportes.addWidget(self.bFP1, 9, 0)

        self.bFP2 = QCheckBox(self)
        self.grid_reportes.addWidget(self.bFP2, 9, 1)

        self.bFP3 = QCheckBox(self)
        self.grid_reportes.addWidget(self.bFP3, 10, 0)

        self.bFP4 = QCheckBox(self)
        self.grid_reportes.addWidget(self.bFP4, 10, 1)

        self.bFP5 = QCheckBox(self)
        self.grid_reportes.addWidget(self.bFP5, 11, 0)

        self.bFP6 = QCheckBox(self)
        self.grid_reportes.addWidget(self.bFP6, 11, 1)

        self.grid_reportes.addItem(VspacerItem, 12, 0)

        self.bver_reporte = QPushButton(self)
        self.bver_reporte.setText("Ver Reporte")
        self.bver_reporte.clicked.connect(self.ver_reporte)
        self.bver_reporte.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.grid_reportes.addWidget(self.bver_reporte, 13, 0)

        self.breporte_exportar = QPushButton(self)
        self.breporte_exportar.setText("Exportar Reporte")
        self.breporte_exportar.clicked.connect(self.filter_exportar)
        self.breporte_exportar.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.grid_reportes.addWidget(self.breporte_exportar, 13, 1)

    ################################# Inventario #################################

        self.inventario = QWidget()
        self.tabWidget.addTab(self.inventario, "Inventario")

        self.grid_inventario = QGridLayout(self.inventario)

# ---------------------------------------------------------------------------------------------------

        self.inventario_table = QTableWidget(self.inventario)
        self.inventario_table.verticalHeader().setVisible(False)
        self.inventario_table.setColumnCount(7)

        self.inventario_table.setHorizontalHeaderItem(
            0, QTableWidgetItem("Producto"))
        self.inventario_table.setHorizontalHeaderItem(
            1, QTableWidgetItem("Unidad"))
        self.inventario_table.setHorizontalHeaderItem(

            2, QTableWidgetItem("E. Recep"))
        self.inventario_table.setHorizontalHeaderItem(
            3, QTableWidgetItem("E. Oficina"))
        self.inventario_table.setHorizontalHeaderItem(
            4, QTableWidgetItem("E. Galpon"))
        self.inventario_table.setHorizontalHeaderItem(
            5, QTableWidgetItem("E. Total"))
        self.inventario_table.setHorizontalHeaderItem(
            6, QTableWidgetItem("Hab Kit"))


# ---------------------------------------------------------------------------------------------------

        self.inventario_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.inventario_table.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)

        self.grid_inventario.addWidget(self.inventario_table, 0, 0, 1, 8)

# ---------------------------------------------------------------------------------------------------

        self.grid_inventario.addItem(VspacerItem, 1, 0)

        self.bmodify_inventario = QPushButton(self.precios)
        self.bmodify_inventario.setText("Agregar / Egresar")
        self.grid_inventario.addWidget(self.bmodify_inventario, 2, 0)
        self.bmodify_inventario.clicked.connect(self.dialog_inventario)

        self.binventario_precios = QPushButton(self.precios)
        self.binventario_precios.setText("Mover")
        self.grid_inventario.addWidget(self.binventario_precios, 2, 1)
        self.binventario_precios.clicked.connect(self.dialog_inventario)

        HspacerItem = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.grid_inventario.addItem(HspacerItem, 2, 2)

        self.bborrar_inventario = QPushButton(self.precios)
        self.bborrar_inventario.setText("Borrar")
        self.grid_inventario.addWidget(self.bborrar_inventario, 2, 4)
        self.bborrar_inventario.clicked.connect(self.borrar_inventario)

        self.bnuevo_inventario = QPushButton(self.precios)
        self.bnuevo_inventario.setText("Nuevo")
        self.grid_inventario.addWidget(self.bnuevo_inventario, 2, 5)
        self.bnuevo_inventario.clicked.connect(self.nuevo_inventario)

        self.binventario_precios = QPushButton(self.precios)
        self.binventario_precios.setText("Hab Kit")
        self.grid_inventario.addWidget(self.binventario_precios, 2, 6)
        self.binventario_precios.clicked.connect(self.dialog_inventario)

        self.brefrescar = QPushButton(self.precios)
        self.brefrescar.setText("Refrescar")
        self.grid_inventario.addWidget(self.brefrescar, 2, 7)
        self.brefrescar.clicked.connect(self.fill_table)

    ################################# Ventana de Pago #################################

        self.pago_window = QWidget()
        self.tabWidget.addTab(self.pago_window, "Ventana Pago")

        self.gridLayout = QGridLayout(self.pago_window)

# ---------------------------------------------------------------------------------------------------
        formas_de_pago = QLabel(self.pago_window)
        self.gridLayout.addWidget(formas_de_pago, 1, 0)
        formas_de_pago.setText("Formas de Pago")

        self.input_FP1 = QLineEdit(self.pago_window)
        self.input_FP1.setEnabled(False)
        self.gridLayout.addWidget(self.input_FP1, 2, 0)

        self.input_FP2 = QLineEdit(self.pago_window)
        self.gridLayout.addWidget(self.input_FP2, 3, 0)
        self.input_FP2.setMaxLength(13)

        self.input_FP3 = QLineEdit(self.pago_window)
        self.gridLayout.addWidget(self.input_FP3, 4, 0)
        self.input_FP3.setMaxLength(13)

        self.input_FP4 = QLineEdit(self.pago_window)
        self.gridLayout.addWidget(self.input_FP4, 5, 0)
        self.input_FP4.setMaxLength(13)

        self.input_FP5 = QLineEdit(self.pago_window)
        self.gridLayout.addWidget(self.input_FP5, 6, 0)
        self.input_FP5.setMaxLength(13)

        formas_de_pago = QLabel(self.pago_window)
        self.gridLayout.addWidget(formas_de_pago, 7, 0)
        formas_de_pago.setText("Tipos de otros\n(separar con coma)")

        self.input_otros = QLineEdit(self.pago_window)
        self.input_otros.setPlaceholderText("Ej: Efectivo,Credito,etc")
        self.gridLayout.addWidget(self.input_otros, 8, 0)
# ---------------------------------------------------------------------------------------------------
        line = QFrame(self.pago_window)
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.gridLayout.addWidget(line, 2, 1, 6, 1)
# ---------------------------------------------------------------------------------------------------
        tipos_extras = QLabel(self.pago_window)
        self.gridLayout.addWidget(tipos_extras, 1, 2)
        tipos_extras.setText("Tipos de Extras")

        self.input_extra1 = QLineEdit(self.pago_window)
        self.gridLayout.addWidget(self.input_extra1, 2, 2)

        self.input_extra2 = QLineEdit(self.pago_window)
        self.gridLayout.addWidget(self.input_extra2, 3, 2)

        formas_de_pago = QLabel(self.pago_window)
        self.gridLayout.addWidget(formas_de_pago, 4, 2)
        formas_de_pago.setText("Tipos de otros\n(separar con coma)")

        self.input_extra3 = QLineEdit(self.pago_window)
        self.input_extra3.setPlaceholderText("Ej: Daños Habitación,etc")
        self.gridLayout.addWidget(self.input_extra3, 5, 2)

        default_estadia = QLabel(self.pago_window)
        self.gridLayout.addWidget(default_estadia, 6, 2)
        default_estadia.setText("Estadia por Defecto")

        self.input_default_estadia = QComboBox(self.pago_window)
        self.input_default_estadia.clear()
        self.input_default_estadia.addItems(
            ["Ninguna", "Hospedaje", "Parcial"])
        self.gridLayout.addWidget(self.input_default_estadia, 7, 2)
# ---------------------------------------------------------------------------------------------------

        self.bactualizar_ventas = QPushButton(self.pago_window)
        self.bactualizar_ventas.setText("Guardar")
        self.gridLayout.addWidget(self.bactualizar_ventas, 14, 2)
        self.bactualizar_ventas.clicked.connect(self.bactualizar)

    ################################# Voucher #################################

        self.voucher = QWidget()
        self.tabWidget.addTab(self.voucher, "Vouchers")
        self.grid_voucher = QGridLayout(self.voucher)

# ---------------------------------------------------------------------------------------------------

        self.voucher_table = QTableWidget(self.voucher)
        self.voucher_table.verticalHeader().setVisible(False)
        self.voucher_table.setColumnCount(4)

        self.voucher_table.setHorizontalHeaderItem(
            0, QTableWidgetItem("Creado"))
        self.voucher_table.setHorizontalHeaderItem(
            1, QTableWidgetItem("Voucher"))
        self.voucher_table.setHorizontalHeaderItem(

            2, QTableWidgetItem("Tipo"))
        self.voucher_table.setHorizontalHeaderItem(
            3, QTableWidgetItem("Valor"))

        self.voucher_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.voucher_table.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)

        self.grid_voucher.addWidget(self.voucher_table, 0, 0, 1, 3)


# ---------------------------------------------------------------------------------------------------

        self.bborrar_voucher = QPushButton(self.voucher)
        self.bborrar_voucher.setText("Borrar")
        self.grid_voucher.addWidget(self.bborrar_voucher, 2, 1)
        self.bborrar_voucher.clicked.connect(self.eliminar_voucher)

        self.bnuevo_voucher = QPushButton(self.voucher)
        self.bnuevo_voucher.setText("Nuevo")
        self.grid_voucher.addWidget(self.bnuevo_voucher, 2, 2)
        self.bnuevo_voucher.clicked.connect(self.dialog_voucher)

# ---------------------------------------------------------------------------------------------------
        self.grid_voucher.addItem(HspacerItem, 2, 0)

    ################################# USUARIOS #################################

        self.gridLayout.addItem(HspacerItem, 14, 0, 1, 2)
        self.gridLayout.addItem(VspacerItem, 8, 0)

        self.usuarios = QWidget()
        self.tabWidget.addTab(self.usuarios, "Usuarios")
        self.gridLayout_2 = QGridLayout(self.usuarios)

        self.nuevo_usuario = QLabel("Agregar Nuevo Usuario")
        self.gridLayout_2.addWidget(self.nuevo_usuario, 0, 0)

        self.input_nombre = QLineEdit(self.usuarios)
        self.gridLayout_2.addWidget(self.input_nombre, 1, 0)
        self.input_nombre.setPlaceholderText("Identificador")
        self.input_nombre.setMaxLength(10)

        self.input_cargo = QComboBox(self.usuarios)
        sizePolicy = QSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(1)
        self.input_cargo.setSizePolicy(sizePolicy)
        self.gridLayout_2.addWidget(self.input_cargo, 1, 1)
        self.input_cargo.addItems(
            ["Recepcionista", "Administrador", "Tecnico"])

        self.input_clave = QLineEdit(self.usuarios)
        self.gridLayout_2.addWidget(self.input_clave, 1, 2)
        self.input_clave.setPlaceholderText("Clave")
        self.input_clave.setMaxLength(8)
        self.input_clave.setValidator(
            QRegularExpressionValidator(QRegularExpression(r'[0-9]+')))

        self.habilitado = QCheckBox("Habilitar uso del Sistema")
        sizePolicy = QSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        self.habilitado.setSizePolicy(sizePolicy)
        self.gridLayout_2.addWidget(self.habilitado, 2, 0)

        self.presencia = QCheckBox("¿Esta dentro del Hotel?")
        sizePolicy = QSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        self.presencia.setSizePolicy(sizePolicy)
        self.gridLayout_2.addWidget(self.presencia, 2, 1)

        self.bcheck1 = QPushButton(self.usuarios)
        self.gridLayout_2.addWidget(self.bcheck1, 2, 2)
        self.bcheck1.setText("Agregar")
        self.bcheck1.clicked.connect(self.bcheck1_agregar)

# ---------------------------------------------------------------------------------------------------

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.grid_reportes.addWidget(line, 3, 0, 1, 3)

# ---------------------------------------------------------------------------------------------------

        eliminar_usuario = QLabel(self.usuarios)
        self.gridLayout_2.addWidget(eliminar_usuario, 4, 0)
        eliminar_usuario.setText("Eliminar Usuario")

        self.input_eliminar = QComboBox(self.usuarios)
        self.gridLayout_2.addWidget(self.input_eliminar, 5, 0, 1, 3)

        self.bcheck2 = QPushButton(self.usuarios)
        self.gridLayout_2.addWidget(self.bcheck2, 5, 3)
        self.bcheck2.setText("Eliminar")
        self.bcheck2.setCursor(QCursor(Qt.PointingHandCursor))
        self.bcheck2.setStyleSheet('''
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 rgb(150, 2, 2), stop:0 rgb(242, 5, 5));
            font-size: 12px;
            color: white
        }
        QPushButton:hover {
            font-size: 12px;
            font-weight: bold;
        }
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 rgb(150, 2, 2), stop:0 rgb(242, 5, 5));
            font-size: 12px        
        }
        ''')
        self.bcheck2.clicked.connect(self.bcheck2_eliminar)
# ---------------------------------------------------------------------------------------------------
        self.gridLayout_2.addItem(HspacerItem, 1, 3)
        self.gridLayout_2.addItem(VspacerItem, 5, 1)

    ################################# HOTEL INFO #################################

        self.hotel_info = QWidget()
        self.tabWidget.addTab(self.hotel_info, "Hotel Info")

        self.gridLayout_hotel_info = QGridLayout(self.hotel_info)
# ---------------------------------------------------------------------------------------------------
        hotel_information = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            hotel_information, 0, 0, 1, 4)
        hotel_information.setText("Datos del Establecimiento")
        hotel_information.setStyleSheet(
            "font-size: 18px; font-weight: bold;")

# ---------------------------------------------------------------------------------------------------
        line = QFrame(self.pago_window)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.gridLayout_hotel_info.addWidget(line, 1, 0, 1, 4)
# ---------------------------------------------------------------------------------------------------
        hotel_nombre = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(hotel_nombre, 3, 0, 1, 2)
        hotel_nombre.setText("Nombre Fiscal")

        self.input_hotel_nombre = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_nombre, 4, 0, 1, 2)
# ---------------------------------------------------------------------------------------------------
        hotel_rif = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(hotel_rif, 3, 2, 1, 2)
        hotel_rif.setText("RIF")

        self.input_hotel_rif = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(self.input_hotel_rif, 4, 2, 1, 2)
        self.input_hotel_rif.setPlaceholderText("Ej: J-123456789-0")
# ---------------------------------------------------------------------------------------------------
        hotel_direccion_fiscal = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            hotel_direccion_fiscal, 5, 0)
        hotel_direccion_fiscal.setText("Direccion Fiscal")

        self.input_hotel_direccion_fiscal = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_direccion_fiscal, 6, 0, 1, 4)
# ---------------------------------------------------------------------------------------------------
        hotel_estado = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(hotel_estado, 7, 0)
        hotel_estado.setText("Estado")

        self.input_hotel_estado = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_estado, 8, 0)
# ---------------------------------------------------------------------------------------------------
        hotel_ciudad = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(hotel_ciudad, 7, 1)
        hotel_ciudad.setText("Ciudad")

        self.input_hotel_ciudad = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_ciudad, 8, 1)
# ---------------------------------------------------------------------------------------------------
        hotel_municipio = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(hotel_municipio, 7, 2)
        hotel_municipio.setText("Municipio")

        self.input_hotel_municipio = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_municipio, 8, 2)
# ---------------------------------------------------------------------------------------------------
        hotel_parroquia = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(hotel_parroquia, 7, 3)
        hotel_parroquia.setText("Parroquia")

        self.input_hotel_parroquia = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_parroquia, 8, 3)
# ---------------------------------------------------------------------------------------------------
        hotel_telefono = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(hotel_telefono, 11, 0, 1, 2)
        hotel_telefono.setText("Telefono")

        self.input_hotel_telefono = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_telefono, 12, 0, 1, 2)
# ---------------------------------------------------------------------------------------------------
        self.hotel_correo = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(self.hotel_correo, 11, 2, 1, 2)
        self.hotel_correo.setText("Correo")

        self.input_hotel_correo = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_correo, 12, 2, 1, 2)
# ---------------------------------------------------------------------------------------------------
        hotel_whatsapp = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(hotel_whatsapp, 21, 0, 1, 2)
        hotel_whatsapp.setText("WhatsApp")

        self.input_hotel_whatsapp = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_whatsapp, 22, 0, 1, 2)
        self.input_hotel_whatsapp.setPlaceholderText("Ej: 04126778168")
# ---------------------------------------------------------------------------------------------------
        hotel_instagram = QLabel(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(hotel_instagram, 21, 2, 1, 2)
        hotel_instagram.setText("Instagram")

        self.input_hotel_instagram = QLineEdit(self.hotel_info)
        self.gridLayout_hotel_info.addWidget(
            self.input_hotel_instagram, 22, 2, 1, 2)
        self.input_hotel_instagram.setPlaceholderText("Ej: @instagram_hotel")

        self.bactualizar_hotel_info = QPushButton(self.hotel_info)
        self.bactualizar_hotel_info.setText("Guardar")
        self.gridLayout_hotel_info.addWidget(
            self.bactualizar_hotel_info, 23, 3)
        self.bactualizar_hotel_info.clicked.connect(self.bactualizar)

    ################################# AVANZADO #################################

        self.avanzado = QWidget()
        self.tabWidget.addTab(self.avanzado, "Avanzado")

        self.gridLayout_3 = QGridLayout(self.avanzado)
# ---------------------------------------------------------------------------------------------------
        reportes = QLabel(self.avanzado)
        self.gridLayout_3.addWidget(reportes, 2, 0)
        reportes.setText("Reportes")

        self.input_reportes = QLineEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_reportes, 2, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------
        self.tiempo_parcial = QLabel(self.avanzado)
        self.gridLayout_3.addWidget(self.tiempo_parcial, 3, 0)
        self.tiempo_parcial.setText("Horas de Parcial")

        self.input_tiempo_parcial = QSpinBox(self.avanzado)
        self.gridLayout_3.addWidget(self.input_tiempo_parcial, 3, 1)
# ---------------------------------------------------------------------------------------------------
        self.input_tg_camera_entrada = QCheckBox(
            "Camera Entrada", self.avanzado)
        self.gridLayout_3.addWidget(self.input_tg_camera_entrada, 4, 0)
        self.input_tg_camera_entrada.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.input_camera_url_entrada = QLineEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_camera_url_entrada, 4, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------
        self.input_tg_camera_salida = QLabel("Camera Salida", self.avanzado)
        self.gridLayout_3.addWidget(self.input_tg_camera_salida, 5, 0)

        self.input_camera_url_salida = QLineEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_camera_url_salida, 5, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------

        self.input_telegram = QCheckBox("Chat ID", self.avanzado)
        self.gridLayout_3.addWidget(self.input_telegram, 6, 0)
        self.input_telegram.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.input_chat_id = QLineEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_chat_id, 6, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------
        self.bot_token = QLabel(self.avanzado)
        self.gridLayout_3.addWidget(self.bot_token, 7, 0)
        self.bot_token.setText("Bot Token")

        self.input_bot_token = QLineEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_bot_token, 7, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------

        self.input_drive_backup = QCheckBox("Drive FolderID", self.avanzado)
        self.gridLayout_3.addWidget(self.input_drive_backup, 8, 0)
        self.input_drive_backup.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.input_drive_folder_id = QLineEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_drive_folder_id, 8, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------

        self.input_sound = QCheckBox("Sonido Path", self.avanzado)
        self.gridLayout_3.addWidget(self.input_sound, 9, 0)
        self.input_sound.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.input_sound_path = QLineEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_sound_path, 9, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------
        self.schedule_dolar_bcv = QCheckBox("BCV Automatico", self.avanzado)
        self.gridLayout_3.addWidget(self.schedule_dolar_bcv, 10, 0)
        self.schedule_dolar_bcv.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.input_schedule_dolar_bcv = QTimeEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_schedule_dolar_bcv, 10, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------
        self.input_chucherias = QCheckBox("Tg Chucherias", self.avanzado)
        self.gridLayout_3.addWidget(self.input_chucherias, 11, 0)
        self.input_chucherias.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.input_tg_chucherias = QLineEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_tg_chucherias, 11, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------
        self.tv_display = QCheckBox("TV Display", self.avanzado)
        self.gridLayout_3.addWidget(self.tv_display, 12, 0)
        self.tv_display.setCursor(
            QCursor(Qt.PointingHandCursor))

        self.input_tv_display = QLineEdit(self.avanzado)
        self.gridLayout_3.addWidget(self.input_tv_display, 12, 1, 1, 2)
# ---------------------------------------------------------------------------------------------------
        self.bactualizar_avanzado = QPushButton(self.avanzado)
        self.bactualizar_avanzado.setText("Guardar")
        self.gridLayout_3.addWidget(self.bactualizar_avanzado, 15, 2)
        self.bactualizar_avanzado.clicked.connect(self.bactualizar)
# ---------------------------------------------------------------------------------------------------

        self.gridLayout_3.addItem(HspacerItem, 15, 1)
        self.gridLayout_3.addItem(VspacerItem, 11, 0)
# ---------------------------------------------------------------------------------------------------

        self.verticalLayout.addWidget(self.tabWidget)

        self.precios_table.setItemDelegateForColumn(0, EmptyDelegate(self))

        bactualiza_list = [self.bactualizar_precios,
                           self.bactualizar_ventas, self.bactualizar_avanzado, self.bcheck1, self.bactualizar_hotel_info]

        for i in bactualiza_list:
            i.setCursor(QCursor(Qt.PointingHandCursor))
            i.setStyleSheet('''
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.8, y2:0.8, stop:1 #11998E, stop:0 #38ef7d);
            font-size: 12px;
            color: white
        }
        QPushButton:hover {
            font-size: 12px;
            font-weight: bold;
        }
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.4, y2:0.4, stop:1 #11998E, stop:0 #38ef7d);
            font-size: 12px
        }
        ''')

    def inventario_nuevo(self):

        return

        # self.start = False
        # producto, ok = QInputDialog.getText(
        #     self, 'Ingrese el nombre del producto (Ejemplo: Detergente)', 'Producto Nombre')
        # unidad, ok = QInputDialog.getText(
        #     self, 'Ingrese la unidad de medición del producto (Ejemplo: Litros o LT)', 'Producto Unidad')
        # if ok == True:

        #     db = mc.connect(
        #         host=host_ip,
        #         user=database_user,
        #         password=database_password,
        #         database="esmeralda_software",
        #         use_pure=True
        #     )

        #     c = db.cursor()

        #     c.execute(
        #         f"SELECT * FROM inventario WHERE producto = '{producto.capitalize()}'")
        #     exist = c.fetchone()

        #     if exist:
        #         misk().errorMSG("Producto ya existe", "Producto existente")
        #     else:
        #         c.execute(
        #             f"INSERT INTO inventario (producto, unidad) VALUES '{producto.capitalize()}', '{unidad.upper()}'")

        #     db.commit()
        #     c.close()
        #     db.close()

    def ver_reporte(self):

        bFP = [self.bFP1, self.bFP2, self.bFP3,
               self.bFP4, self.bFP5, self.bFP6]

        used_FP = [
            f"FP{bFP.index(i) + 1}!=0" for i in bFP if i.isChecked() == True]

        data = None

        if self.tipos_reporte_input.currentText() == 'Ventas':

            db = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )

            c = db.cursor()

            c.execute(f"""
                SELECT DISTINCT descripcion FROM historial_pagos
                WHERE id_historial IN (
                    SELECT transaccion FROM historial_transacciones
                    WHERE dtentrada BETWEEN '{self.reportes_desde_input.dateTime().toPython()}' AND '{self.reportes_hasta_input.dateTime().toPython()}'
                )
            """)
            metodos_pago = [row[0] for row in c.fetchall()]

            columnas_pago = []
            for metodo in metodos_pago:
                columnas_pago.append(f"""
                    (
                        SELECT SUM(monto)
                        FROM historial_pagos
                        WHERE historial_pagos.id_historial = historial_transacciones.transaccion
                        AND descripcion = '{metodo}'
                    ) AS `{metodo}_USD`
                """)
            for metodo in metodos_pago:
                columnas_pago.append(f"""
                    (
                        SELECT SUM(monto * tasa)
                        FROM historial_pagos
                        WHERE historial_pagos.id_historial = historial_transacciones.transaccion
                        AND descripcion = '{metodo}'
                    ) AS `{metodo}_Bs`
                """)

            data = f'''
            SELECT habitacion AS Hab,
                usuario AS Usuario,
                estadia AS Tipo,
                DATE_FORMAT(dtentrada, '%H:%i %d-%m-%Y') AS Entrada,
                DATE_FORMAT(dtsalida, '%H:%i %d-%m-%Y') AS Salida,
                TIMEDIFF(dtsalida, dtentrada) As Duración,
                {', '.join(columnas_pago)},
                hab_costo AS Precio,
                voucher AS Voucher,
                observaciones AS Observaciones
            FROM historial_transacciones
            WHERE dtentrada >= '{self.reportes_desde_input.dateTime().toPython()}' AND dtentrada <= '{self.reportes_hasta_input.dateTime().toPython()}'
            ORDER BY `dtentrada` DESC
                '''

        elif self.tipos_reporte_input.currentText() == 'Policial':

            data = f'''
                    SELECT DISTINCT
                        eh.habitacion, -- Habitación de la estancia
                        e.fecha_inicio_real, -- Fecha de entrada real de la estancia
                        c.cedula, -- Cédula del cliente
                        c.nombre, -- Nombre del cliente
                        TIMESTAMPDIFF(YEAR, c.fecha_nacimiento, CURDATE()) AS edad, -- Edad calculada
                        c.nacionalidad, -- Nacionalidad del cliente
                        c.estado_civil, -- Estado civil del cliente
                        c.profesion, -- Profesión del cliente
                        e.procedencia, -- Procedencia de la estancia
                        e.destino, -- Destino de la estancia
                        eh.fecha_fin_planificada -- Fecha de salida planificada de la habitación
                    FROM estancia_clientes ec
                    INNER JOIN estancias e ON ec.id_estancia = e.id_estancia
                    INNER JOIN clientes c ON ec.cliente = c.cedula
                    INNER JOIN historial_transacciones ht ON e.id_estancia = ht.id_estancia -- Para encontrar pagos
                    INNER JOIN estancia_habitaciones eh ON e.id_estancia = eh.id_estancia -- Para habitación y salida
                    WHERE EXISTS (
                        SELECT 1
                        FROM historial_pagos hp
                        INNER JOIN metodos_pago mp ON hp.descripcion = mp.descripcion
                        WHERE hp.id_historial = ht.transaccion -- Pago asociado a la transacción de la estancia
                        AND mp.reporte = '0'
                    )
                    AND e.fecha_inicio_real >= {self.reportes_desde_input.dateTime().toPython()}
                    AND e.fecha_inicio_real <= {self.reportes_hasta_input.dateTime().toPython()}
                    -- No se filtra por eh.fecha_fin_real IS NULL aquí, ya que se quiere la info de la estancia,
                    -- no solo las habitaciones activas. Se asume que eh contiene la info de la estancia real.
                    ORDER BY e.fecha_inicio_real, c.cedula 
                    '''

        elif self.tipos_reporte_input.currentText() == 'Acciones':
            data = f'''SELECT DATE_FORMAT(datetime, '%H:%m %d-%m-%Y') AS Registro, usuario, descripcion, identificador FROM usuario_log WHERE
                datetime >= '{self.reportes_desde_input.dateTime().toPython()}'
                AND datetime <= '{self.reportes_hasta_input.dateTime().toPython()}'
                ORDER BY `datetime` DESC
            '''

        elif self.tipos_reporte_input.currentText() == 'Clientes':
            data = f'''SELECT * FROM clientes'''

        self.TableViewData.open_table_view_data(data)

    def bactualizar(self):

        question = misk().questionMSG(
            "Esta seguro de realizar los cambios?", "Actualizar Datos")
        if question == QMessageBox.Ok:

            db = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )

            c = db.cursor()

            settings_dict = {
                "default_estadia": self.input_default_estadia.currentText(),

                # Datos del hotel
                "hotel_nombre": self.input_hotel_nombre.text(),
                "hotel_rif": self.input_hotel_rif.text(),
                "hotel_direccion_fiscal": self.input_hotel_direccion_fiscal.text(),
                "hotel_estado": self.input_hotel_estado.text(),
                "hotel_ciudad": self.input_hotel_ciudad.text(),
                "hotel_municipio": self.input_hotel_municipio.text(),
                "hotel_parroquia": self.input_hotel_parroquia.text(),
                "hotel_telefono": self.input_hotel_telefono.text(),
                "hotel_correo": self.input_hotel_correo.text(),
                "hotel_whatsapp": self.input_hotel_whatsapp.text(),
                "hotel_instagram": self.input_hotel_instagram.text(),

                # Config avanzada
                "url_reportes": self.input_reportes.text(),
                "tiempo_parcial": str(self.input_tiempo_parcial.value()),
                "camera_entrada": self.input_camera_url_entrada.text(),
                "camera_salida": self.input_camera_url_salida.text(),
                "tg_chat_id": self.input_chat_id.text(),
                "tg_bot_token": self.input_bot_token.text(),
                "drive_folder_id": self.input_drive_folder_id.text(),
                "music_path": self.input_sound_path.text(),
                "tg_chucherias": self.input_tg_chucherias.text(),
                "tv_display_url": self.input_tv_display.text(),
            }

            # Ejecutar UPDATE por cada configuración
            for nombre, valor in settings_dict.items():
                c.execute(
                    "UPDATE config SET config_value = %s WHERE config_key = %s", (valor, nombre))

            lastlist = []
            for row in range(self.precios_table.rowCount()):
                temp_list = []
                for column in range(self.precios_table.columnCount()):
                    item = self.precios_table.item(row, column).text()
                    temp_list.append(item)
                lastlist.append(temp_list)

            query = """
            INSERT INTO habitaciones (habitacion, tipo, parcial, hospedaje, descripcion, amaneties)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            tipo=VALUES(tipo),
            parcial=VALUES(parcial),
            hospedaje=VALUES(hospedaje),
            descripcion=VALUES(descripcion),
            amaneties=VALUES(amaneties)
            """

            c.executemany(query, lastlist)

            checkable = [
                (self.input_sound, "music"),
                (self.input_chucherias, "wchucherias"),
                (self.input_tg_camera_entrada, "tg_camera"),
                (self.input_telegram, "tg_chat"),
                (self.input_drive_backup, "drive"),
                (self.tv_display, "tv_display"),
            ]

            for widget, nombre in checkable:
                valor = "1" if widget.isChecked() else "0"
                c.execute(
                    "UPDATE config SET config_value = %s WHERE config_key = %s", (valor, nombre))

            db.commit()
            db.close()

            misk().informationMSG("Cambios realizados con Exito!", "Cambios Exitosos")

            self.close()

    def tipos_reporte_changed(self):

        formas_pago = [self.formas_pago, self.bFP1, self.bFP2,
                       self.bFP3, self.bFP4, self.bFP5, self.bFP6]

        rango_tiempo = [self.rango_tiempo, self.reportes_desde,
                        self.reportes_desde_input, self.reportes_hasta, self.reportes_hasta_input]

        if self.tipos_reporte_input.currentText() == "Ventas":
            for i in formas_pago:
                i.hide()
            for i in rango_tiempo:
                i.show()

        elif self.tipos_reporte_input.currentText() == "Policial":
            for i in formas_pago:
                i.show()
            for i in rango_tiempo:
                i.show()

        elif self.tipos_reporte_input.currentText() == "Acciones":
            for i in formas_pago:
                i.hide()
            for i in rango_tiempo:
                i.show()

        elif self.tipos_reporte_input.currentText() == "Clientes":
            for i in formas_pago:
                i.hide()
            for i in rango_tiempo:
                i.hide()

    def filter_exportar(self):

        bFP = [self.bFP1, self.bFP2, self.bFP3,
               self.bFP4, self.bFP5, self.bFP6]

        used_FP = [
            f"FP{bFP.index(i) + 1}>0" for i in bFP if i.isChecked() == True]

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        if self.tipos_reporte_input.currentText() == 'Ventas':
            c.execute(f'''SELECT DATE_FORMAT(dtentrada, '%d-%m-%Y') FROM historial_transacciones
                WHERE
                dtentrada >= '{self.reportes_desde_input.dateTime().toPython()}'
                AND dtentrada <= '{self.reportes_hasta_input.dateTime().toPython()}'
                LIMIT {self.limite_input.value()}''')

            data = c.fetchall()

            if data == []:
                misk().errorMSG(
                    f"No hay transacciones entre {self.reportes_desde_input.dateTime().toString('hh:mm dd-MM-yyyy')} y {self.reportes_hasta_input.dateTime().toString('hh:mm dd-MM-yyyy')}", "No hay transacciones disponibles")
            else:
                filepath = QFileDialog.getSaveFileName(self, "Guardar Reporte de Ventas", f"Reporte de Ventas desde {data[0][0]} hasta el {data[-1][0]}",
                                                       "XLSX(*.xlsx);;All Files(*.*)")

                if bool(filepath[0]) == False:
                    None
                # else:
                    # self.excel_export(filepath[0], "Ventas", self.reportes_desde_input.dateTime().toPython(), self.reportes_hasta_input.dateTime().toPython())

                    # misk().open_file(filepath[0])

        elif self.tipos_reporte_input.currentText() == 'Policial':
            self.policial_export(self.reportes_desde_input.dateTime().toPython(),
                                 self.reportes_hasta_input.dateTime().toPython(),
                                 self.limite_input.value())

        elif self.tipos_reporte_input.currentText() == 'Acciones':
            data = pd.read_sql_query(f'''SELECT DATE_FORMAT(datetime, '%H:%m %d-%m-%Y') AS Registro, usuario, descripcion, identificador FROM usuario_log WHERE
                datetime >= '{self.reportes_desde_input.dateTime().toPython()}'
                AND datetime <= '{self.reportes_hasta_input.dateTime().toPython()}'
                LIMIT {self.limite_input.value()}''', db)

            if data.empty == True:
                misk().errorMSG(
                    f"No hay acciones entre {self.reportes_desde_input.dateTime().toString('hh:mm dd-MM-yyyy')} y {self.reportes_hasta_input.dateTime().toString('hh:mm dd-MM-yyyy')}", "No hay acciones disponibles")
            else:
                filepath = QFileDialog.getSaveFileName(self, "Guardar Log", f"Log - Registros",
                                                       "XLSX(*.xlsx);;All Files(*.*)")
                if bool(filepath[0]):
                    writer = pd.ExcelWriter(filepath[0], engine='xlsxwriter')

                    data.columns = map(str.upper, data.columns)

                    data.to_excel(writer, sheet_name=f"Log - Registros",
                                  freeze_panes=(1, 0), index=False)

                    workbook = writer.book
                    worksheet = writer.sheets["Log - Registros"]

                    formater = workbook.add_format(
                        {'border': 1, 'font_name': 'roboto'})
                    worksheet.set_column(0, len(data.columns), 15, formater)

                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'align': 'center',
                        'valign': 'vcenter',
                        'font_size': '13',
                        'fg_color': '#30d16d',
                        'border': 1})

                    for col_num, value in enumerate(data.columns.values):
                        worksheet.write(0, col_num, value, header_format)

                    for column in data:
                        column_length = max(data[column].astype(
                            str).map(len).max(), len(column))
                        col_idx = data.columns.get_loc(column)
                        worksheet.set_column(
                            col_idx, col_idx, column_length + 4)

                    writer.close()
                    misk().open_file(filepath[0])

        elif self.tipos_reporte_input.currentText() == 'Clientes':
            data = pd.read_sql_query(
                f'''SELECT * FROM clientes LIMIT {self.limite_input.value()}''', db)

            if data.empty == True:
                misk().errorMSG(
                    f"No hay Clientes registrados", "No hay Clientes registrados")
            else:
                filepath = QFileDialog.getSaveFileName(self, "Guardar Reporte Clientes", f"Reporte Clientes {QDate.currentDate().toString('dd-MM-yyyy')}",
                                                       "XLSX(*.xlsx);;All Files(*.*)")
                if bool(filepath[0]):
                    writer = pd.ExcelWriter(filepath[0], engine='xlsxwriter')

                    data.columns = map(str.upper, data.columns)

                    data.to_excel(writer, sheet_name=f"Clientes",
                                  freeze_panes=(1, 0), index=False)

                    workbook = writer.book
                    worksheet = writer.sheets["Clientes"]

                    formater = workbook.add_format(
                        {'border': 1, 'font_name': 'roboto'})
                    worksheet.set_column(0, len(data.columns), 15, formater)

                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'align': 'center',
                        'valign': 'vcenter',
                        'font_size': '13',
                        'fg_color': '#30d16d',
                        'border': 1})

                    for col_num, value in enumerate(data.columns.values):
                        worksheet.write(0, col_num, value, header_format)

                    for column in data:
                        column_length = max(data[column].astype(
                            str).map(len).max(), len(column))
                        col_idx = data.columns.get_loc(column)
                        worksheet.set_column(
                            col_idx, col_idx, column_length + 4)

                    writer.close()
                    misk().open_file(filepath[0])

    def policial_export(self, from_datetime, to_datetime, limit):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        query = '''
        SELECT DISTINCT
            eh.habitacion, -- Habitación de la estancia
            e.fecha_inicio_real, -- Fecha de entrada real de la estancia
            c.cedula, -- Cédula del cliente
            c.nombre, -- Nombre del cliente
            TIMESTAMPDIFF(YEAR, c.fecha_nacimiento, CURDATE()) AS edad, -- Edad calculada
            c.nacionalidad, -- Nacionalidad del cliente
            c.estado_civil, -- Estado civil del cliente
            c.profesion, -- Profesión del cliente
            e.procedencia, -- Procedencia de la estancia
            e.destino, -- Destino de la estancia
            eh.fecha_fin_planificada -- Fecha de salida planificada de la habitación
        FROM estancia_clientes ec
        INNER JOIN estancias e ON ec.id_estancia = e.id_estancia
        INNER JOIN clientes c ON ec.cliente = c.cedula
        INNER JOIN historial_transacciones ht ON e.id_estancia = ht.id_estancia -- Para encontrar pagos
        INNER JOIN estancia_habitaciones eh ON e.id_estancia = eh.id_estancia -- Para habitación y salida
        WHERE EXISTS (
            SELECT 1
            FROM historial_pagos hp
            INNER JOIN metodos_pago mp ON hp.descripcion = mp.descripcion
            WHERE hp.id_historial = ht.transaccion -- Pago asociado a la transacción de la estancia
            AND mp.reporte = '0'
        )
        AND e.fecha_inicio_real >= %s
        AND e.fecha_inicio_real <= %s
        -- No se filtra por eh.fecha_fin_real IS NULL aquí, ya que se quiere la info de la estancia,
        -- no solo las habitaciones activas. Se asume que eh contiene la info de la estancia real.
        ORDER BY e.fecha_inicio_real, c.cedula -- Opcional: para consistencia en los resultados con LIMIT
        LIMIT %s
        '''
        c.execute(query, (from_datetime, to_datetime, limit))
        data = c.fetchall()

        if not data:  # CORRECCIÓN: Agregar 'data' después de 'if not'
            print("No se encontraron registros en ese rango de fechas.")
            c.close()
            db.close()
            return

        # Datos del hotel
        c.execute("""
            SELECT
            MAX(CASE WHEN config_key = 'hotel_nombre' THEN config_value END),
            MAX(CASE WHEN config_key = 'hotel_rif' THEN config_value END),
            MAX(CASE WHEN config_key = 'hotel_direccion_fiscal' THEN config_value END),
            MAX(CASE WHEN config_key = 'hotel_estado' THEN config_value END),
            MAX(CASE WHEN config_key = 'hotel_ciudad' THEN config_value END),
            MAX(CASE WHEN config_key = 'hotel_municipio' THEN config_value END),
            MAX(CASE WHEN config_key = 'hotel_parroquia' THEN config_value END),
            MAX(CASE WHEN config_key = 'hotel_telefono' THEN config_value END),
            MAX(CASE WHEN config_key = 'hotel_correo' THEN config_value END),
            MAX(CASE WHEN config_key = 'reporte_policial_cantidad_exp' THEN config_value END),
            MAX(CASE WHEN config_key = 'reporte_policial_total_huespedes_default' THEN config_value END),
            MAX(CASE WHEN config_key = 'reporte_policial_huespedes_resta' THEN config_value END)
            FROM config;
        """)
        hotel_info = c.fetchone()

        # Convertir campos numéricos
        reporte_cantidad_exp = int(hotel_info[9]) + 1 if hotel_info[9] else 0
        reporte_resta = int(hotel_info[11]) if hotel_info[11] else 0

        # Crear tabla de huéspedes
        rows = ""
        for i in data:  # CORRECCIÓN: Usar 'data' en lugar de la variable vacía
            rows += f"""
                <tr>
                    <td>{i[0]}</td>
                    <td>{i[1].strftime("%d/%m")}</td>
                    <td>{i[2]}</td>
                    <td>{i[3]}</td>
                    <td>{i[4]}</td>
                    <td>{i[5]}</td>
                    <td>{i[6]}</td>
                    <td>{i[7]}</td>
                    <td>{i[8]}</td>
                    <td>{i[9]}</td>
                    <td>{i[10].strftime("%d/%m")}</td>
                </tr>
            """

        # Crear archivo HTML
        filepath = f"reportes_policiales/{from_datetime} al {to_datetime}.html"
        with open(filepath, "w", encoding="utf-8") as file_html:
            file_html.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8" />
                <style>
                    h1 {{
                        font-size: 140%;
                        font-family: Arial, sans-serif;
                        padding: 2% 0%;
                    }}
                    h2 {{
                        font-size: 120%;
                        font-family: Arial, sans-serif;
                    }}
                    .centered {{
                        text-align: center;
                    }}
                    td {{
                        text-align: center;
                        padding: 0.4%;
                        word-wrap: break-word;
                        max-width: 100px;
                    }}
                    th {{
                        text-align: center;
                        padding: 1% 0.4%;
                    }}
                    .h1_table {{
                        font-family: Arial, sans-serif;
                        font-size: 140%;
                        width: 100%;
                    }}
                    table {{
                        font-family: Arial, sans-serif;
                        font-size: 96%;
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    tr:nth-child(even) {{
                        background-color: #ebebeb;
                    }}
                    @media print {{
                        @page {{
                            size: letter landscape;
                            margin: 1cm;
                        }}
                        body {{
                            font-size: 11pt;
                            color: #000;
                        }}
                        h1, h2 {{
                            page-break-after: avoid;
                        }}
                        table {{
                            page-break-inside: avoid;
                        }}
                        .pagebreak {{
                            page-break-after: always;
                        }}
                    }}
                </style>
            </head>
            <body>
                <h1 class="centered">
                    {hotel_info[0]}<br>
                    {hotel_info[1]}<br><br>
                    Control de venezolanos y extranjeros en pensiones o sitios de hospedaje<br><br>
                    Fecha desde {data[0][1].strftime("%d/%m/%Y")} hasta el {data[-1][10].strftime("%d/%m/%Y")}<br><br>
                    Establecimiento: {hotel_info[0]} &nbsp;&nbsp;&nbsp;&nbsp;
                    Ciudad: {hotel_info[4]} &nbsp;&nbsp;&nbsp;&nbsp;
                    Número de Exp: {reporte_cantidad_exp}
                </h1>

                <table class="h1_table" cellspacing="0" border="1">
                    <tr>
                        <th>Total de Huéspedes del libro</th>
                        <th>Total de Huéspedes del período</th>
                        <th>Total de Huéspedes que restan</th>
                    </tr>
                    <tr>
                        <td>{hotel_info[10]}</td>
                        <td>{len(data)}</td>
                        <td>{reporte_resta - len(data)}</td>
                    </tr>
                </table>

                <div class="pagebreak"></div>

                <h1>Control de venezolanos y extranjeros en pensiones o sitios de hospedaje</h1>

                <h2>Nombre del Establecimiento: {hotel_info[0]} &nbsp;&nbsp;&nbsp;&nbsp; RIF: {hotel_info[1]}</h2>
                <h2>Dirección Fiscal: {hotel_info[2]}</h2>
                <h2>Teléfono: {hotel_info[7]} &nbsp;&nbsp;&nbsp;&nbsp; Correo: {hotel_info[8]}</h2>
                <h2>Estado: {hotel_info[3]} &nbsp;&nbsp;&nbsp;&nbsp;
                    Ciudad: {hotel_info[4]} &nbsp;&nbsp;&nbsp;&nbsp;
                    Municipio: {hotel_info[5]} &nbsp;&nbsp;&nbsp;&nbsp;
                    Parroquia: {hotel_info[6]}</h2>

                <table cellspacing="0" border="1">
                    <thead>
                        <tr>
                            <th>Hab</th>
                            <th>Fecha<br>Entrada</th>
                            <th>Doc. de<br>Identidad</th>
                            <th>Nombre y Apellido</th>
                            <th>Edad</th>
                            <th>Nacionalidad</th>
                            <th>Estado<br>Civil</th>
                            <th>Profesión</th>
                            <th>Procedencia</th>
                            <th>Destino</th>
                            <th>Fecha<br>Salida</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </body>
            </html>
            """)

        # Actualizar valores en config
        c.execute("""
            UPDATE config
            SET config_value = %s
            WHERE config_key = 'reporte_policial_cantidad_exp'
        """, (str(reporte_cantidad_exp),))

        c.execute("""
            UPDATE config
            SET config_value = %s
            WHERE config_key = 'reporte_policial_huespedes_resta'
        """, (str(max(reporte_resta - len(data), 0)),))

        db.commit()
        c.close()
        db.close()

        print(f"✅ Reporte generado: {filepath}")
        # webbrowser.open(filepath)
        # misk().open_file(filepath[0])

    def excel_export(self, filepath: str, sheet_name: str, from_datetime, to_datetime):

        def formatter(DFingresos, sheet_name, money_accent, writer):
            # Get the xlsxwriter workbook and worksheet objects.
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            formater = workbook.add_format({
                'text_wrap': True,
                'font_size': '12',
                'font_name': 'Roboto',
                'border': 1})
            worksheet.conditional_format(f'A2:T{len(DFingresos)+1}', {'type':     'no_blanks',
                                                                      'format':    formater})
            # Add a header format.
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                'font_size': '12',
                'font_name': 'Roboto',
                'fg_color': '#14E464',
                'border': 1})

            # Write the column headers with the defined format.
            for col_num, value in enumerate(DFingresos.columns.values):
                worksheet.write(0, col_num, value, header_format)

            parcial_format = workbook.add_format(
                {'bg_color': '#b41414', 'font_color': 'white', 'bold': True})
            hospedaje_format = workbook.add_format(
                {'bg_color': '#bdc3c7', 'font_color': 'black', 'bold': True})

            if money_accent:
                worksheet.conditional_format(f'C2:C{len(DFingresos)+1}', {'type':     'text',
                                                                          'criteria': 'containing',
                                                                          'value':     'parcial',
                                                                          'format':    parcial_format})
                worksheet.conditional_format(f'C2:C{len(DFingresos)+1}', {'type':     'text',
                                                                          'criteria': 'containing',
                                                                          'value':     'hospedaje',
                                                                          'format':    hospedaje_format})

            worksheet.set_tab_color('#14E464')
            # worksheet.protect('esmeralda')
            worksheet.set_row(0, 26)

            # Auto column width
            for column in DFingresos:
                column_length = max(DFingresos[column].astype(
                    str).map(len).max(), len(column))
                col_idx = DFingresos.columns.get_loc(column)
                worksheet.set_column(col_idx, col_idx, column_length + 4)

        writer = pd.ExcelWriter(f'{filepath}', engine='xlsxwriter')

        db = mc.connect(
            host=host_ip,
            user="otto",
            password="esmeralda",
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()
        # 1. Obtener métodos de pago usados en el rango
        c.execute(f"""
            SELECT DISTINCT descripcion FROM historial_pagos
            WHERE id_historial IN (
                SELECT transaccion FROM historial_transacciones
                WHERE dtentrada BETWEEN '{from_datetime}' AND '{to_datetime}'
            )
        """)
        metodos_pago = [row[0] for row in c.fetchall()]

        # 2. Construir columnas dinámicas por método de pago (según moneda registrada)
        columnas_pago = []
        for metodo in metodos_pago:
            columnas_pago.append(f"""
                (
                    SELECT SUM(
                        CASE 
                            WHEN moneda = 'USD' THEN monto
                            WHEN moneda = 'Bs' THEN monto * tasa
                        END
                    )
                    FROM historial_pagos
                    WHERE historial_pagos.id_historial = historial_transacciones.transaccion
                    AND descripcion = '{metodo}'
                ) AS `{metodo}`
            """)

        # 3. Armar la consulta principal
        query = pd.read_sql_query(f"""
            SELECT habitacion AS Hab,
                   usuario AS Usuario,
                   estadia AS Tipo,
                   DATE_FORMAT(dtentrada, '%H:%i %d-%m-%Y') AS Entrada,
                   DATE_FORMAT(dtsalida, '%H:%i %d-%m-%Y') AS Salida,
                   TIMEDIFF(dtsalida, dtentrada) AS Duración,
                   {', '.join(columnas_pago)},
                   hab_costo AS Precio,
                   voucher AS Voucher,
                   observaciones AS Observaciones
            FROM historial_transacciones
            WHERE dtentrada BETWEEN '{from_datetime}' AND '{to_datetime}'
        """, db)

        sheet_name = sheet_name
        query.to_excel(writer, sheet_name=sheet_name,
                       freeze_panes=(1, 0), index=False)

        # # RESUMEN
        # DFresumen_rows = pd.read_sql_query(
        #     f"SELECT DATE_FORMAT(dtentrada, '%d-%m-%Y') AS Fecha,COUNT(dtentrada) AS Clientes, SUM(FP1) AS '{config[1]}', SUM(FP2*tasa) '{config[2]}', SUM(FP3*tasa) AS '{config[3]}',SUM(FP4*tasa) AS '{config[4]}',SUM(FP5*tasa) AS '{config[5]}',SUM(otros) AS '{config[6]} - $',SUM(otros*tasa) AS '{config[6]} - Bs' FROM historial_transacciones WHERE dtentrada >= '{from_datetime}' AND dtentrada <= '{to_datetime}' GROUP BY Fecha", db)
        # DFresumen_total = pd.read_sql_query(
        #     f"SELECT 'TOTAL', COUNT(dtentrada), SUM(FP1), SUM(FP2*tasa), SUM(FP3*tasa), SUM(FP4*tasa), SUM(FP5*tasa),SUM(otros),SUM(otros*tasa) FROM historial_transacciones WHERE dtentrada >= '{from_datetime}' AND dtentrada <= '{to_datetime}'", db)

        # c.execute(
        #     F"SELECT SUM(FP1), (SUM(FP2*tasa) + SUM(FP3*tasa) + SUM(FP4*tasa) + SUM(FP5*tasa)) AS total_bs FROM historial_transacciones WHERE dtentrada >= '{from_datetime}' AND dtentrada <= '{to_datetime}'")
        # dato = c.fetchone()

        # # Copy colummn names
        # new_cols = {x: y for x, y in zip(
        #     DFresumen_total.columns, DFresumen_rows.columns)}
        # DFresumen = pd.concat([DFresumen_rows, DFresumen_total.rename(
        #     columns=new_cols)], ignore_index=True)

        # DFresumen["   Descripcion de Gastos   "] = "?"

        # DFresumen["Gastos $"] = "?"
        # DFresumen["Gastos Bs"] = "?"

        # ingresos_dolar = 777
        # ingresos_bs = 353
        # gastos = 0
        # viene_mes_anterior = "?"
        # disponible = "?"
        # prestamo_banco = "?"
        # queda_prox_mes = "?"  # disponible - prestamo_banco*3

        # df1 = pd.DataFrame({
        #     "   Descripcion de Gastos   ": ["", "Descripcion", "Ingresos", "Egresos", "Viene del Mes Anterior", "Disponible", "Pago prestamo Banco", "Queda para el prox Mes"],
        #     "Gastos $": ["", "Dolares", ingresos_dolar, gastos, viene_mes_anterior, disponible, prestamo_banco, queda_prox_mes],
        #     "Gastos Bs": ["", "Bolivares", ingresos_bs, gastos, viene_mes_anterior, disponible, prestamo_banco, queda_prox_mes]})

        # DFresumen = pd.concat([DFresumen, df1], ignore_index=True)

        # DFresumen_rows.columns = map(str.upper, DFresumen_rows.columns)

        # DFresumen.to_excel(writer, sheet_name=f"{sheet_name}_resumen",
        #                    freeze_panes=(1, 0), index=False)

        formatter(query, sheet_name, True, writer)
        # formatter(DFresumen, f"{sheet_name}_resumen", False, writer)
        writer.close()

        # ------------------------------  Inventario ------------------------------

    def borrar_inventario(self):
        return

        # question = misk().questionMSG(
        #     "Esta seguro de eliminar permanentemente un\nproducto del inventario?", "Eliminar Producto")

        # if question == QMessageBox.Ok:

        #     db = mc.connect(
        #         host=host_ip,
        #         user=database_user,
        #         password=database_password,
        #         database="esmeralda_software",
        #         use_pure=True
        #     )

        #     c = db.cursor()

        #     c.execute("SELECT producto FROM inventario")
        #     list_productos = c.fetchall()

        #     self.start = False
        #     producto, ok = QInputDialog.getItem(
        #         self, 'Seleccionar', 'Seleccione producto a eliminar:', [i[0] for i in list_productos])

        #     if ok == True:

        #         c.execute(
        #             f"DELETE FROM inventario WHERE producto = '{producto}'")

        #     db.commit()
        #     c.close()
        #     db.close()

    def nuevo_inventario(self):
        return

        # self.start = False
        # nombre, ok = QInputDialog.getText(
        #     self, 'Nombre', 'Ingrese el nombre del producto')

        # if ok == True:
        #     self.start = False
        #     unidad, ok = QInputDialog.getText(
        #         self, 'Unidad', 'Ingrese la unidad de medición del producto')
        #     if ok == True:

        #         db = mc.connect(
        #             host=host_ip,
        #             user=database_user,
        #             password=database_password,
        #             database="esmeralda_software",
        #             use_pure=True
        #         )

        #         c = db.cursor()

        #         c.execute(
        #             f"INSERT INTO inventario (producto, unidad) VALUES ('{nombre.title()}', '{unidad.title()}')")

        #         # ------------------------------------ Add to Log -----------------------------------------

        #         c.execute(f'''
        #             INSERT INTO usuario_log (datetime, tipo, usuario, descripcion, identificador) VALUES
        #             (CURRENT_TIMESTAMP,
        #             "inventario",
        #             "{self.usuario}",
        #             "producto creado",
        #             "{nombre.title()}")''')

        #     db.commit()
        #     db.close()

        #     self.fill_table(self.inventario_table, "inventario", 6)

    def dialog_inventario(self):

        dlg = QDialog(self)
        dlg.setWindowTitle("Inventario")

        dlg.setStyleSheet('''
                    QLabel {
                    background: rgba(0, 0, 0, 0);
                    color: rgb(242, 242, 242);
                    font-size: 13px;
                    padding: 4px;
                    }
                    
                    QComboBox {
                    color: rgb(20, 0, 0);
                    background-color: rgb(255, 255, 255);
                    border-radius: 2px;
                    padding: 4px;
                    font-size: 13px;
                    }

                    QPushButton {
                        background-color: rgb(44, 44, 44);
                        border-color: white;
                        color: rgb(242, 242, 242);
                        border-radius: 2px;
                        padding: 4px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: rgb(242, 242, 242);
                        color: black;
                    }
                    QPushButton:pressed {
                        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.4, y2:0.4, stop:1 #11998E, stop:0 #38ef7d);
                        color: white;
                    }

                    QPlainTextEdit {
                        background-color: 
                        white;
                        color: black;
                        border-radius: 2px;
                        font-size: 12px}
                    ''')

        self.formLayout = QFormLayout(dlg)

        producto = QLabel(self)
        producto.setText("Producto")
        self.formLayout.setWidget(
            1, QFormLayout.LabelRole, producto)

        self.producto_input = QComboBox(self)
        self.formLayout.setWidget(
            1, QFormLayout.FieldRole, self.producto_input)

        cantidad = QLabel(self)
        cantidad.setText("Cantidad")
        self.formLayout.setWidget(
            2, QFormLayout.LabelRole, cantidad)

        self.cantidad_input = QDoubleSpinBox(self)
        self.cantidad_input.setMaximum(1000000)
        self.formLayout.setWidget(
            2, QFormLayout.FieldRole, self.cantidad_input)

        self.deposito = QLabel(self)
        self.deposito.setText("Deposito")
        self.formLayout.setWidget(
            3, QFormLayout.LabelRole, self.deposito)

        self.deposito_input = QComboBox(self)
        self.formLayout.setWidget(
            3, QFormLayout.FieldRole, self.deposito_input)

        self.desde = QLabel(self)
        self.desde.setText("Desde")
        self.formLayout.setWidget(
            4, QFormLayout.LabelRole, self.desde)

        self.desde_input = QComboBox(self)
        self.formLayout.setWidget(
            4, QFormLayout.FieldRole, self.desde_input)

        self.hasta = QLabel(self)
        self.hasta.setText("Hasta")
        self.formLayout.setWidget(
            5, QFormLayout.LabelRole, self.hasta)

        self.hasta_input = QComboBox(self)
        self.formLayout.setWidget(
            5, QFormLayout.FieldRole, self.hasta_input)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.formLayout.setWidget(
            6, QFormLayout.SpanningRole, line)

        self.observaciones = QPlainTextEdit(self)
        self.observaciones.setPlaceholderText("Observaciones opcionales")
        self.observaciones.setMaximumHeight(60)
        self.formLayout.setWidget(
            7, QFormLayout.SpanningRole, self.observaciones)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.formLayout.setWidget(
            8, QFormLayout.SpanningRole, line)

        self.bagregar = QPushButton(self)
        self.bagregar.setText("Agregar")
        self.bagregar.clicked.connect(self.modify_inventario)
        self.bagregar.setCursor(QCursor(Qt.PointingHandCursor))
        self.formLayout.setWidget(
            9, QFormLayout.SpanningRole, self.bagregar)

        self.begresar = QPushButton(self)
        self.begresar.setText("Egresar")
        self.begresar.clicked.connect(self.modify_inventario)
        self.begresar.setCursor(QCursor(Qt.PointingHandCursor))
        self.formLayout.setWidget(
            10, QFormLayout.SpanningRole, self.begresar)

        self.bmover = QPushButton(self)
        self.bmover.setText("Mover")
        self.bmover.clicked.connect(self.move_inventario)
        self.bmover.setCursor(QCursor(Qt.PointingHandCursor))
        self.formLayout.setWidget(
            11, QFormLayout.SpanningRole, self.bmover)

        self.bmodificar_amaneties = QPushButton(self)
        self.bmodificar_amaneties.setText("Modificar Hab Kit")
        self.bmodificar_amaneties.clicked.connect(self.modify_amaneties)
        self.bmodificar_amaneties.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.formLayout.setWidget(
            12, QFormLayout.SpanningRole, self.bmodificar_amaneties)

        dinamic_modify = [
            self.deposito, self.deposito_input,
            self.bagregar,
            self.begresar,
        ]

        dinamic_mover = [
            self.desde, self.desde_input,
            self.hasta, self.hasta_input,

            self.bmover
        ]

        if self.sender().text() == 'Mover':
            for i in dinamic_mover:
                i.show()
            for i in dinamic_modify:
                i.hide()
            self.bmodificar_amaneties.hide()

        elif self.sender().text() == 'Hab Kit':
            dinamic_amaneties = dinamic_modify + dinamic_mover
            for i in dinamic_amaneties:
                i.hide()
            self.bmodificar_amaneties.show()

        else:
            for i in dinamic_modify:
                i.show()
            for i in dinamic_mover:
                i.hide()
            self.bmodificar_amaneties.hide()

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        # c.execute("SELECT producto FROM inventario")
        # list_productos = c.fetchall()

        # self.producto_input.addItems(
        #     [i for sub in list_productos for i in sub])

        c.execute("SELECT dp1, dp2, dp3 FROM config")
        list_dp = c.fetchone()

        for i in list_dp:
            self.deposito_input.addItems([i])
            self.desde_input.addItems([i])
            self.hasta_input.addItems([i])

        dlg.exec()

    def modify_amaneties(self):
        return

        # db = mc.connect(
        #     host=host_ip,
        #     user=database_user,
        #     password=database_password,
        #     database="esmeralda_software",
        #     use_pure=True
        # )

        # c = db.cursor()

        # c.execute(
        #     f"UPDATE inventario SET amaneties = {int(self.cantidad_input.value())} WHERE producto = '{self.producto_input.currentText()}'")

        # c.execute(
        #     f"UPDATE inventario SET dp1 = inventario.dp1/inventario.amaneties WHERE producto = 'Amaneties'")

        # db.commit()

        # self.fill_table(self.inventario_table, "inventario", 6)

        # misk().informationMSG("Cambios realizados exitosamente", "Hab Kit")

    def move_inventario(self):
        return

        # db = mc.connect(
        #     host=host_ip,
        #     user=database_user,
        #     password=database_password,
        #     database="esmeralda_software",
        #     use_pure=True
        # )

        # c = db.cursor()

        # c.execute(
        #     f"SELECT dep{self.desde_input.currentIndex() + 1}, dep{self.hasta_input.currentIndex() + 1} FROM inventario WHERE producto = '{self.producto_input.currentText()}'")

        # data = c.fetchone()

        # dp_from_stock = float(data[0])
        # dp_to_stock = float(data[1])

        # if self.cantidad_input.value() > dp_from_stock:
        #     misk().errorMSG("No se puede efectuar operacion", "Error")

        # else:
        #     dp_from_stock_changed = dp_from_stock - self.cantidad_input.value()
        #     dp_to_stock_changed = dp_to_stock + self.cantidad_input.value()

        #     question = misk().questionMSG(
        #         f"Se moveran {self.cantidad_input.value()} {self.producto_input.currentText()} desde {self.desde_input.currentText()} hasta {self.hasta_input.currentText()}\nEsta seguro seguro de realizar los cambios?", "Efectuar Cambios")

        #     if question == QMessageBox.Ok:

        #         c.execute(
        #             f"UPDATE inventario SET dep{self.desde_input.currentIndex() + 1} = {dp_from_stock_changed}, dep{self.hasta_input.currentIndex() + 1} = {dp_to_stock_changed} WHERE producto = '{self.producto_input.currentText()}'")

        #         if self.observaciones.toPlainText() != "":
        #             # ------------------------------------ Add to Log -----------------------------------------

        #             c.execute(f'''
        #                 INSERT INTO usuario_log (datetime, tipo, usuario, descripcion, identificador) VALUES
        #                 (CURRENT_TIMESTAMP,
        #                 "inventario",
        #                 "{self.usuario}",
        #                 "{self.cantidad_input.value()} movidos desde {self.desde_input.currentText()} hasta {self.hasta_input.currentText()} | Observaciones: {self.observaciones.toPlainText()}",
        #                 "{self.producto_input.currentText()}")''')

        #             c.execute(
        #                 f"INSERT INTO usuario_log (datetime, usuario, accion, hab) VALUES ('{QDateTime.currentDateTime().toPython()}', '{self.usuario}', '', '')")

        #             misk().tg_message(
        #                 f"<b>Movimiento de Inventario 🚚</b>\n{self.usuario} movió {self.cantidad_input.value()} {self.producto_input.currentText()} desde {self.desde_input.currentText()} hasta {self.hasta_input.currentText()}\n🗣️ <b>Observaciones:</b> {self.observaciones.toPlainText()}")

        #         else:
        #             # ------------------------------------ Add to Log -----------------------------------------

        #             c.execute(f'''
        #                 INSERT INTO usuario_log (datetime, tipo, usuario, descripcion, identificador) VALUES
        #                 (CURRENT_TIMESTAMP,
        #                 "inventario",
        #                 "{self.usuario}",
        #                 "{self.cantidad_input.value()} movidos desde {self.desde_input.currentText()} hasta {self.hasta_input.currentText()} | Observaciones: {self.observaciones.toPlainText()}",
        #                 "{self.producto_input.currentText()}")''')

        #             misk().tg_message(
        #                 f"<b>Movimiento de Inventario 🚚</b>\n{self.usuario} movió {self.cantidad_input.value()} {self.producto_input.currentText()} desde {self.desde_input.currentText()} hasta {self.hasta_input.currentText()}")

        #         misk() .informationMSG("Operacion realizada con exito", "Operacion Exitosa")
        # db.commit()

        # self.fill_table(self.inventario_table, "inventario", 6)

    def modify_inventario(self):
        return

        # db = mc.connect(
        #     host=host_ip,
        #     user=database_user,
        #     password=database_password,
        #     database="esmeralda_software",
        #     use_pure=True
        # )

        # c = db.cursor()

        # c.execute(
        #     f"SELECT dep{self.deposito_input.currentIndex() + 1}, total FROM inventario WHERE producto = '{self.producto_input.currentText()}'")
        # data = c.fetchone()

        # current_stock = float(data[0])
        # total_viejo = float(data[1])

        # if self.sender().text() == 'Egresar' and self.cantidad_input.value() > current_stock:
        #     misk().errorMSG("No se puede efectuar operacion", "Error")

        # else:

        #     if self.sender().text() == 'Egresar':
        #         stock_changed = current_stock - self.cantidad_input.value()
        #         message = f"<b>Egreso de Inventario</b> 📤\n{self.usuario} egresó {self.cantidad_input.value()} {self.producto_input.currentText()} (Pasó de {current_stock} a {stock_changed} en {self.deposito_input.currentText()})"
        #         log = f"Egreso de {self.cantidad_input.value()} {self.producto_input.currentText()} (Pasó de {current_stock} a {stock_changed})"
        #         total_nuevo = total_viejo - self.cantidad_input.value()

        #     elif self.sender().text() == 'Agregar':
        #         stock_changed = current_stock + self.cantidad_input.value()
        #         message = f"<b>Ingreso de Inventario</b> 📥\n{self.usuario} ingresó {self.cantidad_input.value()} {self.producto_input.currentText()} (Pasó de {current_stock} a {stock_changed} en {self.deposito_input.currentText()})"
        #         log = f"Ingreso de {self.cantidad_input.value()} {self.producto_input.currentText()} (Pasó de {current_stock} a {stock_changed})"
        #         total_nuevo = total_viejo + self.cantidad_input.value()

        #     question = misk().questionMSG(
        #         f"{self.producto_input.currentText()} pasara de {current_stock} a {stock_changed}\nEsta seguro seguro de realizar los cambios?", "Efectuar Cambios")

        #     if question == QMessageBox.Ok:

        #         c.execute(
        #             f"UPDATE inventario SET dep{self.deposito_input.currentIndex() + 1} = {stock_changed}, total = dp1+dp2+dp3 WHERE producto = '{self.producto_input.currentText()}'")

        #         if self.observaciones.toPlainText() != "":
        #             # ------------------------------------ Add to Log -----------------------------------------
        #             c.execute(
        #                 f"INSERT INTO usuario_log (datetime, usuario, accion, hab) VALUES ('{QDateTime.currentDateTime().toPython()}', '{self.usuario}', '{log} | Observaciones: {self.observaciones.toPlainText()}', '')")

        #             misk().tg_message(
        #                 f"{message}\n🗣️ <b>Observaciones:</b> {self.observaciones.toPlainText()}")
        #         else:
        #             # ------------------------------------ Add to Log -----------------------------------------
        #             c.execute(
        #                 f"INSERT INTO usuario_log (datetime, usuario, accion, hab) VALUES ('{QDateTime.currentDateTime().toPython()}', '{self.usuario}', '{log}', '')")

        #             misk().tg_message(message)

        #         misk().informationMSG("Operacion realizado con exito", "Operacion Exitosa")

        #     db.commit()

        #     self.fill_table(self.inventario_table, "inventario", 6)

    def fill_table(self, qt_table, db_table, col_num):
        return

        # QApplication.setOverrideCursor(Qt.WaitCursor)

        # db = mc.connect(
        #     host=host_ip,
        #     user=database_user,
        #     password=database_password,
        #     database="esmeralda_software",
        #     use_pure=True
        # )

        # c = db.cursor()

        # c.execute(f"SELECT * FROM {db_table}")
        # data = c.fetchall()

        # qt_table.setRowCount(len(data))

        # table_row = 0
        # for row in data:
        #     for i in range(col_num):
        #         qt_table.setItem(
        #             table_row, i, QTableWidgetItem(str(row[i])))
        #     table_row += 1

        # qt_table.resizeColumnsToContents()

        # try:
        #     QApplication.restoreOverrideCursor()
        # except:
        #     QApplication.restoreOverrideCursor()

        # ------------------------------  Vouchers ------------------------------

    def dialog_voucher(self):

        dlg = QDialog(self)
        dlg.setWindowTitle("Vouchers")

        dlg.setStyleSheet('''
                    QLabel {
                    background: rgba(0, 0, 0, 0);
                    color: rgb(242, 242, 242);
                    font-size: 14px;
                    padding: 4px;
                    }
                    
                    QComboBox {
                    color: rgb(20, 0, 0);
                    background-color: rgb(255, 255, 255);
                    border-radius: 2px;
                    padding: 4px;
                    font-size: 14px;
                    }

                    QPushButton {
                        background-color: rgb(44, 44, 44);
                        border-color: white;
                        color: rgb(242, 242, 242);
                        border-radius: 2px;
                        padding: 4px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: rgb(242, 242, 242);
                        color: black;
                    }
                    QPushButton:pressed {
                        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.4, y2:0.4, stop:1 #11998E, stop:0 #38ef7d);
                        color: white;
                    }
                    ''')

        no_space_validator = QRegularExpressionValidator(
            QRegularExpression("^[A-Za-z0-9]+"))

        formLayout = QFormLayout(dlg)

        codigo = QLabel(self)
        codigo.setText("Codigo")
        formLayout.setWidget(
            1, QFormLayout.LabelRole, codigo)

        self.codigo_input = QLineEdit(self)
        self.codigo_input.setMaxLength(20)
        self.codigo_input.setValidator(no_space_validator)
        formLayout.setWidget(
            1, QFormLayout.FieldRole, self.codigo_input)

        valor = QLabel(self)
        valor.setText("Valor")
        formLayout.setWidget(
            2, QFormLayout.LabelRole, valor)

        self.valor_input = QDoubleSpinBox(self)
        self.valor_input.setMaximum(1000000)
        formLayout.setWidget(
            2, QFormLayout.FieldRole, self.valor_input)

        tipo = QLabel(self)
        tipo.setText("Tipo")
        formLayout.setWidget(
            3, QFormLayout.LabelRole, tipo)

        self.tipo_input = QComboBox(self)
        self.tipo_input.addItems(["$ Neto", "% Porcentual"])
        formLayout.setWidget(
            3, QFormLayout.FieldRole, self.tipo_input)

        self.bcrear = QPushButton(self)
        self.bcrear.setText("Crear Voucher")
        self.bcrear.clicked.connect(self.crear_voucher)
        self.bcrear.setCursor(QCursor(Qt.PointingHandCursor))
        formLayout.setWidget(
            4, QFormLayout.SpanningRole, self.bcrear)

        dlg.exec()

    def crear_voucher(self):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute("SELECT codigo FROM vouchers")
        vouchers_existentes = c.fetchall()

        flat_vouchers_existentes = [
            i for sub in vouchers_existentes for i in sub]

        if self.codigo_input.text() == "" or self.valor_input.value() == 0:
            misk().errorMSG("Rellene todos los datos para continuar", "Rellene los Datos")

        elif self.codigo_input.text() in flat_vouchers_existentes:
            misk().errorMSG("Voucher ya existe", "Voucher ya existe")

        else:
            c.execute(
                f"INSERT INTO vouchers (dtcreacion, codigo, valor, tipo) VALUES ('{QDateTime.currentDateTime().toPython()}','{self.codigo_input.text()}', {self.valor_input.value()},'{self.tipo_input.currentText()[0]}')")

            # ------------------------------------ Add to Log -----------------------------------------
            misk().registrar_log("voucher", self.usuario,
                                 f"voucher {self.codigo_input} (-{self.valor_input}{self.tipo_input.currentText()[0]}) creado", self.codigo_input)

            db.commit()
            c.close()
            db.close()

            misk().informationMSG(
                f"Se ha creado exitosamente el voucher {self.codigo_input.text()}", "Voucher Creado")

            self.fill_table(self.voucher_table, "vouchers", 4)

    def eliminar_voucher(self):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute("SELECT codigo FROM vouchers")
        vouchers_existentes = c.fetchall()

        flat_vouchers_existentes = [
            i for sub in vouchers_existentes for i in sub]

        self.start = False
        voucher, ok = QInputDialog.getItem(
            self, 'Elminar Voucher', 'Seleccione el voucher a eliminar', flat_vouchers_existentes)

        if ok == True:

            c.execute(
                f"DELETE FROM vouchers WHERE codigo = '{voucher}'")

            # ------------------------------------ Add to Log -----------------------------------------

            misk().registrar_log("voucher", self.usuario, "voucher eliminado", voucher)

            db.commit()
            c.close()
            db.close()

            misk().informationMSG(
                f"Se ha eliminado exitosamente el voucher {voucher}", "Voucher Eliminado")

            self.fill_table(self.voucher_table, "vouchers", 4)


# ------------------------------  Usuarios ------------------------------


    def bcheck1_agregar(self):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute("SELECT identificador FROM usuarios")
        usuarios_existentes = c.fetchall()
        flat_usuarios_existentes = [
            i for sub in usuarios_existentes for i in sub]

        if self.input_nombre.text() == "" or self.input_clave.text() == "":
            misk().errorMSG("Rellene todos los datos para continuar", "Rellene los Datos")

        elif self.input_nombre.text().title() in flat_usuarios_existentes:
            misk().errorMSG("Usuario ya existente", "Identificador ya existente")

        else:
            question = misk().questionMSG(
                f"Esta seguro de agregar a {self.input_nombre.text().title()}?", "Agregar Usuario")
            if question == QMessageBox.Ok:

                c.execute(
                    f"INSERT IGNORE INTO usuarios (identificador, clave, rol, habilitado) VALUES ('{self.input_nombre.text().title()}','{self.input_clave.text()}','{self.input_cargo.currentText().lower()}', {1 if self.habilitado.isChecked() else 0})")

                if self.presencia.isChecked():
                    c.execute(
                        f"INSERT INTO current_personas (id, rol, identificador) VALUES ('{self.input_cargo.currentText().lower()}{self.input_nombre.text().title()}', '{self.input_cargo.currentText().lower()}', '{self.input_nombre.text().title()}')")

                db.commit()

                question = misk().questionMSG(
                    f"Se ha agragado exitosamente a {self.input_nombre.text().title()}, se necesita reiniciar el sistema para aplicar los cambios, desea reiniciarlo?", "Operación Existosa")
                if question == QMessageBox.Ok:
                    os.execl(sys.executable, sys.executable, *sys.argv)
                    # os.execv(sys.argv[0], sys.argv)

    def bcheck2_eliminar(self):

        if self.input_eliminar.currentText() == "otto":
            misk().errorMSG("Imposible eliminar usuario ya que es parte\nfundamental para el uso del sistema", "Imposible Eliminar")

        else:
            question = misk().questionMSG(
                f"Esta seguro de borrar a {self.input_eliminar.currentText()}", "Borrar Usuario")
            if question == QMessageBox.Ok:

                db = mc.connect(
                    host=host_ip,
                    user=database_user,
                    password=database_password,
                    database="esmeralda_software",
                    use_pure=True
                )

                c = db.cursor()

                c.execute(
                    f"DELETE FROM identificador WHERE usuario = '{self.input_eliminar.currentText()}'")

                db.commit()

                c.execute("SELECT identificador FROM usuarios")
                users = c.fetchall()

                flat_list = [i for sub in users for i in sub]

                self.input_eliminar.clear()
                self.input_eliminar.addItems(flat_list)

                question = misk().questionMSG(
                    f"Se ha eliminado usuario exitosamente, se necesita reiniciar el sistema para aplicar los cambios, desea reiniciarlo?", "Operación Existosa")
                if question == QMessageBox.Ok:
                    os.execl(sys.executable, sys.executable, *sys.argv)


# ------------------------------ Reservaciones ------------------------------

class ReservationsTableModel(QAbstractTableModel):
    def __init__(self, data=[], header=[], parent=None):
        super().__init__(parent)
        self._data = data
        self.header = header

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        row = index.row()
        column = index.column()

        if role == Qt.DisplayRole:
            value = self._data[row][column]

            # Formatear Fechas (Indices: 1=dtreservada, 5=inicio, 6=salida)
            if column in [1, 5, 6]:
                if value:
                    try:
                        # Si viene como string de MySQL
                        if isinstance(value, str):
                            date_obj = datetime.fromisoformat(
                                value.replace('T', ' '))
                        # Si viene como objeto datetime
                        else:
                            date_obj = value
                        return date_obj.strftime('%d/%m/%Y %H:%M')
                    except Exception:
                        pass
                return str(value)

            # Formatear Costo (Indice 7)
            if column == 7:
                try:
                    return f"${float(value):.2f}"
                except:
                    return str(value)

            return str(value) if value is not None else ""

        # Alineación al centro para fechas, habitación y costo
        elif role == Qt.TextAlignmentRole and column in [1, 2, 5, 6, 7]:
            return Qt.AlignCenter

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section < len(self.header):
                return self.header[section]
        return None
    

class ReservationsBoard(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Reservaciones Futuras')
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setMinimumSize(1100, 600)

        self.usuario = str

        # --- CONFIGURACIÓN UI ---
        self.table_view = QTableView(self)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        # Importante: Desactivamos la edición directa, ya que se maneja con clicks
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)

        # Conectar señal de clic
        self.table_view.clicked.connect(self.on_table_clicked)

        # Paginación (Reutilizando tu widget existente)
        self.pagination_widget = PaginationWidget(self)
        self.pagination_widget.set_disabled(True)
        self.pagination_widget.page_changed.connect(self.update_table)

        main_layout = QVBoxLayout()
        # Titulo o info extra si gustas
        info_label = QLabel("Listado de reservaciones planificadas y activas")
        info_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin: 10px;")

        main_layout.addWidget(info_label)
        main_layout.addWidget(self.table_view)
        main_layout.addWidget(self.pagination_widget)
        self.setLayout(main_layout)

        self.data = []
        # Definimos los headers. El ID (índice 0) lo ocultaremos después.
        self.header = [
            'id',
            'Reservada',        
            'Habitación',       
            'Usuario',          
            'Tipo',             
            'Fecha Entrada',
            'Fecha Salida',
            'Costo',
            'Voucher',
            'Observaciones'     
        ]

    def load_future_reservations(self):
        """Carga reservas activas cuya fecha de inicio sea hoy o en el futuro"""
        try:
            connection = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )
            cursor = connection.cursor()

            # NOTA: Incluyo reserva_id primero para tener la referencia,
            # aunque no lo pidió en la visual, es necesario para la lógica.
            query = """
                SELECT 
                    estancias.id_estancia,
                    estancias.fecha_inicio_real, 
                    estancia_habitaciones.habitacion, 
                    estancias.usuario_registro , 
                    estancias.tipo_estadia,
                    estancias.fecha_inicio_planificada, 
                    estancias.fecha_fin_planificada ,
                    estancia_habitaciones.costo, 
                    estancias.voucher, 
                    estancias.observaciones
                FROM estancias
                INNER JOIN estancia_habitaciones 
                    ON estancias.id_estancia = estancia_habitaciones.id_estancia
                WHERE estancias.estado = 'reservada' 
                ORDER BY estancias.fecha_inicio_planificada ASC;
            """

            cursor.execute(query)
            self.data = cursor.fetchall()
            print(self.data)

            if not self.data:
                self.pagination_widget.set_disabled(True)
                # Seteamos modelo vacío para limpiar vista
                empty_model = ReservationsTableModel([], self.header, self)
                self.table_view.setModel(empty_model)
            else:
                self.pagination_widget.set_disabled(False)
                self.update_table()

            connection.close()

        except mc.Error as err:
            QMessageBox.critical(
                self, "Error DB", f"Error cargando reservaciones: {err}")

    def update_table(self):
        # Lógica de paginación idéntica a tu código anterior
        page_size = 25
        total_pages = (len(self.data) + page_size - 1) // page_size
        self.pagination_widget.set_total_pages(total_pages)

        start_idx = (self.pagination_widget.current_page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_data = self.data[start_idx:end_idx]

        model = ReservationsTableModel(paginated_data, self.header, self)
        self.table_view.setModel(model)

        # --- CONFIGURACIÓN DE COLUMNAS ---
        # 1. Ocultar la columna ID (Indice 0) visualmente, pero los datos siguen ahí
        # self.table_view.setColumnHidden(0, True)

        # 2. Ajustar anchos
        self.table_view.resizeColumnsToContents()
        self.table_view.horizontalHeader().setSectionResizeMode(
            9, QHeaderView.Stretch)  # Observaciones estira

    def on_table_clicked(self, index):
        """Maneja el clic en una reserva"""
        if not index.isValid():
            return

        row = index.row()
        # Obtenemos el ID de la reserva (Columna 0 oculta)
        id_estancia = self.table_view.model().data(
            self.table_view.model().index(row, 0), Qt.DisplayRole)

        # Obtenemos nombre de usuario y habitación para mostrar en el título del dialogo
        usuario = self.table_view.model().data(
            self.table_view.model().index(row, 3), Qt.DisplayRole)
        habitacion = self.table_view.model().data(
            self.table_view.model().index(row, 2), Qt.DisplayRole)
        tipo_estadia = self.table_view.model().data(
            self.table_view.model().index(row, 4), Qt.DisplayRole)

        # Abrir el diálogo de opciones
        self.show_action_dialog(id_estancia, usuario, habitacion, tipo_estadia)

    def show_action_dialog(self, id_estancia, usuario, habitacion, tipo_estadia):
        dialog = QDialog(self)
        dialog.setWindowTitle(
            f"Gestión: {usuario} - Hab {habitacion} - {tipo_estadia}")
        dialog.setFixedWidth(300)

        layout = QVBoxLayout()

        lbl = QLabel(
            f"¿Qué desea hacer con la reserva seleccionada?")
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        # Botones solicitados
        btn_activar = QPushButton("Activar Reserva")
        btn_mover = QPushButton("Mover Reserva")
        btn_cancelar = QPushButton("Cancelar Reserva")

        # Estilos opcionales para diferenciar peligrosidad
        btn_activar.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 8px;")
        btn_mover.setStyleSheet(
            "background-color: #2196F3; color: white; padding: 8px;")
        btn_cancelar.setStyleSheet(
            "background-color: #f44336; color: white; padding: 8px;")

        # Conexiones (Aquí integras tu lógica luego)
        btn_activar.clicked.connect(
            lambda: self.action_activate(id_estancia, habitacion, tipo_estadia, dialog))
        btn_mover.clicked.connect(
            lambda: self.action_move(id_estancia, dialog))
        btn_cancelar.clicked.connect(
            lambda: self.action_cancel(id_estancia, dialog))

        layout.addWidget(btn_activar)
        # layout.addWidget(btn_mover)
        # layout.addWidget(btn_cancelar)

        dialog.setLayout(layout)
        dialog.exec()

    # --- Funciones placeholders para que integres tu lógica ---
    def action_activate(self, id_estancia, habitacion, tipo_estadia, dialog):
        connection = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        cursor = connection.cursor()

        query = """
        UPDATE estancias 
        SET estado = %s, fecha_inicio_real = %s
        WHERE id_estancia = %s
        """
        cursor.execute(query, ('activa', datetime.now(), id_estancia))

        query = """
        UPDATE current_habitaciones 
        SET id_estancia = %s, estado = %s
        WHERE habitacion = %s
        """
        cursor.execute(query, (id_estancia, tipo_estadia, habitacion))

        connection.commit()
        connection.close()

        dialog.accept()
        self.close()

        persona = {'rol': "cliente", 'nombre': f'HAB {habitacion}',
                    'identificador': id_estancia}

        misk().abrir_porton(self.usuario, [persona], 'entrada', f'Reservación pasó a {tipo_estadia} y se activó la habitación {habitacion}')

    def action_move(self, reserva_id, dialog):
        print(f"Lógica para MOVER reserva {reserva_id}")
        dialog.accept()
        self.close()

    def action_cancel(self, reserva_id, dialog):
        print(f"Lógica para CANCELAR reserva {reserva_id}")
        dialog.accept()
        self.close()

# ------------------------------  Novedades y Averías  ------------------------------


class StatusDelegate(QStyledItemDelegate):
    """Delegado para mostrar botones de estado en la columna de estado"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent

    def createEditor(self, parent, option, index):
        if index.column() == 4:  # Columna de estado
            combo = QComboBox(parent)
            combo.addItems(['activo', 'resuelto'])
            combo.currentTextChanged.connect(
                lambda text: self.on_status_changed(index.row(), text)
            )
            return combo
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            value = index.model().data(index, Qt.DisplayRole)
            editor.setCurrentText(value)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def on_status_changed(self, row, new_status):
        """Emitir señal de cambio de estado al widget padre"""
        if self.parent_widget and hasattr(self.parent_widget, 'on_status_changed'):
            self.parent_widget.on_status_changed(row, new_status)


class AddNoticeIssueDialog(QDialog):
    def __init__(self, parent=None, current_user="Usuario Actual"):
        super().__init__(parent)
        self.current_user = current_user
        self.setWindowTitle('Agregar Novedad/Avería')
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Mostrar usuario actual (solo lectura)
        self.user_label = QLabel(f"Usuario: {self.current_user}")
        layout.addWidget(self.user_label)

        # Campo de descripción
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        layout.addWidget(QLabel('Descripción:'))
        layout.addWidget(self.description_input)

        # Botones de tipo (ocupando toda la anchura)
        self.novedad_button = QPushButton('Novedad')
        self.averia_button = QPushButton('Avería')

        self.novedad_button.clicked.connect(
            lambda: self.select_type('novedad'))
        self.averia_button.clicked.connect(lambda: self.select_type('averia'))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.novedad_button)
        button_layout.addWidget(self.averia_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.selected_type = None

    def select_type(self, tipo):
        self.selected_type = tipo
        self.accept()

    def accept(self):
        """Validar y guardar los datos"""
        description = self.description_input.toPlainText().strip()
        if not description:
            QMessageBox.warning(
                self, "Error", "La descripción es obligatoria.", QMessageBox.Ok)
            return

        if self.selected_type is None:
            QMessageBox.warning(
                self, "Error", "Debe seleccionar tipo (Novedad o Avería).", QMessageBox.Ok)
            return

        # Simular guardado exitoso
        super().accept()

    def get_type(self):
        return self.selected_type


class NoticeIssueTableModel(QAbstractTableModel):
    def __init__(self, data=[], header=[], parent=None):
        super().__init__(parent)
        self._data = data
        self.header = header

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        row = index.row()
        column = index.column()

        # Verificar que la columna existe en los datos
        if column >= len(self._data[row]):
            return None

        if role == Qt.DisplayRole:
            value = str(self._data[row][column])
            # Formatear fechas
            if column in [1, 2]:  # creada, resolucion
                if value != 'None' and value:
                    try:
                        date_obj = datetime.fromisoformat(
                            value.replace('T', ' '))
                        return date_obj.strftime('%d/%m/%Y %H:%M')
                    except:
                        pass
            return value

        elif role == Qt.BackgroundRole:
            # Colorear filas según estado y tiempo sin resolver (solo para averías activas)
            status = self._data[row][5]  # Columna 'estado'
            record_type = self._data[row][4]  # Columna 'tipo'

            if record_type == 'averia' and status == 'activo':
                # Calcular días desde creación
                try:
                    created_date_str = self._data[row][1]
                    if created_date_str is not None:
                        # Convertir a datetime si es una cadena
                        if isinstance(created_date_str, str):
                            created_date = datetime.fromisoformat(
                                created_date_str.replace('T', ' '))
                        else:
                            created_date = created_date_str
                        days_since_creation = (
                            datetime.now() - created_date).days

                        if days_since_creation > 7:
                            # Rojo para más de 7 días
                            return QColor(141, 30, 12)
                        else:
                            # Amarillo para menos de 7 días
                            return QColor(190, 149, 51)
                except Exception as e:
                    print(f"Error al calcular días: {e}")

        # tipo y estado
        elif role == Qt.TextAlignmentRole and column in [4, 5]:
            return Qt.AlignCenter

        return None

    def setData(self, index, value, role=Qt.EditRole):
        """Método para actualizar el estado de una avería"""
        if role == Qt.EditRole and index.isValid():
            row = index.row()
            column = index.column()

            if column == 5:  # Columna de estado (índice 5)
                # Actualizar el estado en los datos
                old_data = list(self._data[row])
                old_data[5] = value
                self._data[row] = tuple(old_data)

                # Si es una avería activa, actualizar fecha de resolución
                if old_data[4] == 'averia' and value == 'resuelto' and old_data[2] is None:
                    # Actualizar fecha de resolución con la fecha actual
                    new_data = list(old_data)
                    new_data[2] = datetime.now().isoformat()
                    self._data[row] = tuple(new_data)

                self.dataChanged.emit(index, index)
                return True
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            headers_map = {
                'id': 'ID',
                'creada': 'Creada',
                'resolucion': 'Resolución',
                'usuario': 'Usuario',
                'tipo': 'Tipo',
                'estado': 'Estado',
                'descripcion': 'Descripción'
            }
            if section < len(self.header):
                return headers_map.get(self.header[section], self.header[section])
        return None


class NoticeIssueBoard(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Novedades y Averías')
        self.setMinimumSize(1000, 600)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.usuario = ""

        # --- 1. CONFIGURACIÓN UI (Solo una vez) ---
        self.table_view = QTableView(self)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setWordWrap(True)
        self.table_view.setTextElideMode(Qt.ElideNone)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.status_delegate = StatusDelegate(
            self)
        self.table_view.setItemDelegateForColumn(5, self.status_delegate)

        self.table_view.clicked.connect(self.on_table_clicked)

        self.add_button = QPushButton('Agregar Novedad/Avería', self)
        self.add_button.clicked.connect(self.add_new_item)

        self.pagination_widget = PaginationWidget(self)
        self.pagination_widget.set_disabled(True)
        self.pagination_widget.page_changed.connect(self.update_table)

        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        main_layout.addWidget(self.table_view)
        main_layout.addWidget(self.pagination_widget)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.add_button)
        self.setLayout(main_layout)

        self.data = []
        # Headers fijos, no cambian
        self.header = ['id', 'creada', 'resolucion',
                       'usuario', 'tipo', 'estado', 'descripcion']

    def generate_mock_data(self):
        """Cargar datos reales desde la base de datos"""
        try:
            connection = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )
        except mc.Error as err:
            QMessageBox.critical(
                self, "Error", f"Error connecting to MySQL: {err}", QMessageBox.Ok)
            return

        try:
            cursor = connection.cursor()
            # Consulta que incluye todas las columnas relevantes
            query = """
            SELECT id, creada, resolucion, usuario, tipo, estado, descripcion
            FROM novedades 
            ORDER BY creada DESC
            """
            cursor.execute(query)
            self.data = cursor.fetchall()
            self.original_data = self.data.copy()  # Para búsqueda
            self.header = ['id', 'creada', 'resolucion',
                           'usuario', 'tipo', 'estado', 'descripcion']

            if not self.data:
                QMessageBox.information(
                    self, "Información", "No hay novedades ni averías registradas.", QMessageBox.Ok)
                self.pagination_widget.set_disabled(True)
            else:
                self.pagination_widget.set_disabled(False)
                self.update_table()

            connection.close()

        except mc.Error as err:
            QMessageBox.critical(
                self, "Error", f"Error fetching data from MySQL: {err}", QMessageBox.Ok)
            if 'connection' in locals():
                connection.close()

    def update_table(self):
        """Actualizar SOLAMENTE los datos de la tabla"""
        try:
            conn = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )
            cursor = conn.cursor()
            query = """
            SELECT id, creada, resolucion, usuario, tipo, estado, descripcion
            FROM novedades 
            ORDER BY creada DESC
            """
            cursor.execute(query)
            self.data = cursor.fetchall()
            conn.close()
        except mc.Error as err:
            print(f"Error DB: {err}")
            return

        # Lógica de paginación
        page_size = 25
        total_pages = (len(self.data) + page_size - 1) // page_size
        self.pagination_widget.set_total_pages(total_pages)

        start_idx = (self.pagination_widget.current_page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_data = self.data[start_idx:end_idx]

        # Creamos el modelo con los nuevos datos
        table_model = NoticeIssueTableModel(paginated_data, self.header, self)

        # Al setear el modelo, la vista se refresca, pero el DELEGADO y la SEÑAL clicked se mantienen
        self.table_view.setModel(table_model)

        # Re-aplicar tamaños de columna (esto sí se pierde al cambiar de modelo a veces)
        self.table_view.resizeColumnsToContents()
        self.table_view.setColumnWidth(1, 150)
        self.table_view.setColumnWidth(2, 150)
        self.table_view.setColumnWidth(3, 120)
        self.table_view.setColumnWidth(4, 80)
        self.table_view.setColumnWidth(5, 80)
        self.table_view.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)

    def on_table_clicked(self, index):
        print("change")
        """Manejar clic en la tabla para toggle de estado"""
        row = index.row()
        record_type = self.table_view.model().data(
            self.table_view.model().index(row, 4), Qt.DisplayRole)  # Columna 'tipo'

        # Solo permitir toggle para averías
        if record_type == 'averia':
            current_status = self.table_view.model().data(
                self.table_view.model().index(row, 5), Qt.DisplayRole)  # Columna 'estado'
            new_status = 'resuelto' if current_status == 'activo' else 'activo'

            # Mostrar confirmación
            reply = QMessageBox.question(
                self,
                'Confirmar Cambio de Estado',
                f'¿Está seguro que desea cambiar el estado a "{new_status}"?'
            )

            if reply == QMessageBox.Yes:
                self.on_status_changed(row, new_status)

    def on_status_changed(self, row, new_status):
        try:
            connection = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )

            cursor = connection.cursor()
            novedad_id = self.original_data[row][0]

            if new_status == 'resuelto':
                # Actualizar estado y fecha de resolución
                query = """
                UPDATE novedades 
                SET estado = %s, resolucion = %s 
                WHERE id = %s
                """
                cursor.execute(query, (new_status, datetime.now(), novedad_id))
            else:
                # Actualizar solo estado
                query = """
                UPDATE novedades 
                SET estado = %s, resolucion = NULL 
                WHERE id = %s
                """
                cursor.execute(query, (new_status, novedad_id))

            connection.commit()

            try:
                # Usamos un cursor nuevo con dictionary=True para obtener la fila lista para JSON
                fetch_cursor = connection.cursor(dictionary=True)
                fetch_cursor.execute(
                    "SELECT * FROM novedades WHERE id = %s", (novedad_id,))
                fila_actualizada = fetch_cursor.fetchone()

                payload = {
                    "hotel_id": HOTEL,
                    "novedades": [fila_actualizada]
                }

                hilo_sync = threading.Thread(
                    target=misk().sync_servidor,
                    args=(payload, "/api/sync/novedades"),
                    daemon=True  # Daemon muere si cierras la app
                )
                hilo_sync.start()

            except Exception as e:
                print(
                    f"Error preparando sincronización (El dato local está seguro): {e}")

            connection.close()

            # Refrescar la tabla para mostrar los cambios desde la base de datos
            self.update_table()

            QMessageBox.information(
                self, "Éxito", f"Estado actualizado a: {new_status}", QMessageBox.Ok)

        except mc.Error as err:
            QMessageBox.critical(
                self, "Error", f"Error updating  {err}", QMessageBox.Ok)

    def add_new_item(self):
        """Abrir diálogo para agregar nueva novedad o avería"""
        dialog = AddNoticeIssueDialog(self, self.usuario)
        if dialog.exec() == QDialog.Accepted:
            try:
                connection = mc.connect(
                    host=host_ip,
                    user=database_user,
                    password=database_password,
                    database="esmeralda_software",
                    use_pure=True
                )

                cursor = connection.cursor()
                query = """
                    INSERT INTO novedades (usuario, tipo, descripcion, creada) 
                    VALUES (%s, %s, %s, NOW())
                    """
                # Nota: Agregué NOW() en el INSERT para asegurar que tenga fecha de creación local

                cursor.execute(query, (
                    self.usuario,
                    dialog.get_type(),
                    dialog.description_input.toPlainText()
                ))

                connection.commit()
                # --- INICIO BLOQUE DE SINCRONIZACIÓN ---
                try:
                    # 1. Obtener el ID autogenerado por MySQL
                    new_id = cursor.lastrowid

                    # 2. Consultar la fila completa
                    # Usamos dictionary=True para que el formato sea compatible con el JSON
                    fetch_cursor = connection.cursor(dictionary=True)
                    fetch_cursor.execute(
                        "SELECT * FROM novedades WHERE id = %s", (new_id,))
                    nuevo_registro = fetch_cursor.fetchone()

                    if nuevo_registro:
                        # 3. Preparar Payload
                        payload = {
                            "hotel_id": HOTEL,  # O usa self.hotel_id si lo tienes en una variable
                            "novedades": [nuevo_registro]
                        }

                        # 4. Iniciar Hilo (CORREGIDO)
                        # target: self.sync_servidor (el método de tu clase)
                        # args: (payload, endpoint) -> Aquí agregamos la ruta de la API
                        hilo = threading.Thread(
                            target=misk().sync_servidor,
                            args=(payload, "/api/sync/novedades"),
                            daemon=True
                        )
                        hilo.start()
                        print(
                            f"🚀 Sincronización iniciada para Novedad ID {new_id}")

                except Exception as e:
                    print(
                        f"⚠️ Error preparando sync (El dato local sí se guardó): {e}")
                # --- FIN BLOQUE DE SINCRONIZACIÓN ---
                connection.close()

                QMessageBox.information(
                    self, "Éxito", "Novedad/Avería agregada correctamente.", QMessageBox.Ok)
                self.generate_mock_data()  # Refrescar datos

            except mc.Error as err:
                QMessageBox.critical(
                    self, "Error", f"Error saving data: {err}", QMessageBox.Ok)

    def search_table(self, text):
        """Filtrar datos por texto"""
        if not text:
            self.data = self.original_data.copy()
        else:
            filtered_data = []
            for row in self.original_data:
                # Buscar en descripción, tipo, etc.
                row_str = ' '.join(str(cell) for cell in row if cell)
                if text.lower() in row_str.lower():
                    filtered_data.append(row)
            self.data = filtered_data

        self.update_table()

# ------------------------------------------------------------------------------


class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        return None


class MySQLTableModel(QAbstractTableModel):
    def __init__(self, data=[], header=[], parent=None):
        super(MySQLTableModel, self).__init__(parent)
        self._data = data
        self.header = header

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        row = index.row()
        column = index.column()

        if role == Qt.DisplayRole:
            return str(self._data[row][column])

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header[section]

        return None


class PaginationWidget(QWidget):
    page_changed = Signal()
    search_changed = Signal(str)

    def __init__(self, parent=None):
        super(PaginationWidget, self).__init__(parent)
        self.total_pages = 0
        self.current_page = 1

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input.textChanged.connect(self.on_search)

        self.prev_button = QPushButton("Anterior", self)
        self.prev_button.clicked.connect(self.previous_page)

        self.next_button = QPushButton("Siguiente", self)
        self.next_button.clicked.connect(self.next_page)

        self.page_label = QLabel(self)

        layout = QHBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_button)

        self.setLayout(layout)

        self.search_input.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_total_pages(self, total_pages):
        self.total_pages = total_pages
        self.update_page_label()

    def update_page_label(self):
        self.page_label.setText(
            f"Página {self.current_page} de {self.total_pages}")

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_page_label()
            self.page_changed.emit()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_page_label()
            self.page_changed.emit()

    def on_search(self):
        self.search_changed.emit(self.search_input.text())

    def reset(self):
        self.current_page = 1
        self.update_page_label()

    def set_disabled(self, disable):
        self.prev_button.setDisabled(disable)
        self.next_button.setDisabled(disable)

    def set_page(self, page):
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.update_page_label()
            self.page_changed.emit()

    def set_total_pages(self, total_pages):
        self.total_pages = total_pages
        self.update_page_label()


class TableViewData(QWidget):
    def __init__(self):
        super(TableViewData, self).__init__()

        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle('Vista de hoja de Calculo')

        self.table_view = QTableView(self)
        self.table_view.verticalHeader().setVisible(False)
        self.pagination_widget = PaginationWidget(self)
        self.pagination_widget.set_disabled(True)
        self.pagination_widget.page_changed.connect(self.update_table)
        self.pagination_widget.search_changed.connect(self.search_table)

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        layout.addWidget(self.pagination_widget)

        self.setLayout(layout)

        self.data = []
        self.header = []

    def fetch_data(self, mysql_command):
        try:
            self.connection = mc.connect(
                host=host_ip,
                user=database_user,
                password=database_password,
                database="esmeralda_software",
                use_pure=True
            )
        except mc.Error as err:
            QMessageBox.critical(
                self, "Error", f"Error connecting to MySQL: {err}", QMessageBox.Ok)
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(mysql_command)
            self.data = cursor.fetchall()
            self.header = [i[0] for i in cursor.description]

            if not self.data:
                QMessageBox.warning(
                    self, "Warning", "MySQL data is empty.", QMessageBox.Ok)
                return

            self.pagination_widget.set_disabled(False)
            self.update_table()
            self.show()

        except mc.Error as err:
            QMessageBox.critical(
                self, "Error", f"Error fetching data from MySQL: {err}", QMessageBox.Ok)

    def search_table(self, text):
        if not text:
            self.update_table()
            return

        filtered_data = [row for row in self.data if any(
            text.lower() in str(cell).lower() for cell in row)]
        self.update_table(filtered_data)

    def update_table(self, data=None):
        page_size = 50
        if data is None:
            data = self.data

        start_idx = (self.pagination_widget.current_page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_data = data[start_idx:end_idx]

        table_model = MySQLTableModel(paginated_data, self.header, self)
        self.table_view.setModel(table_model)

        total_pages = (len(data) + page_size - 1) // page_size
        self.pagination_widget.set_total_pages(total_pages)

        # Resize the columns to fit the table contents
        self.table_view.resizeColumnsToContents()

    def open_table_view_data(self, mysql_command):
        self.fetch_data(mysql_command)


class GPIOThread(threading.Thread):
    def __init__(self, event, porton_callback):
        super().__init__()
        self.event = event
        self.porton_callback = porton_callback
        self.daemon = True
        self.gpio_available = False

        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.gpio_available = True
            print("[INFO] GPIO disponible, iniciando monitoreo de botón...")
        except ImportError:
            print(
                "[INFO] Librería RPi.GPIO no disponible, omitiendo monitoreo de botón.")
            self.gpio_available = False

    def run(self):
        if not self.gpio_available:
            return  # No hacer nada si GPIO no está disponible

        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            last_state = GPIO.input(18)

            try:
                while True:
                    current_state = GPIO.input(18)
                    if current_state != last_state and current_state == 0:
                        self.event.set()
                        # Opcional: abrir portón al presionar botón
                        self.porton_callback("ENTRADA", "PEATONAL")
                    last_state = current_state
                    import time
                    time.sleep(0.01)
            except KeyboardInterrupt:
                GPIO.cleanup()
        except ImportError:
            print(
                "[INFO] Librería RPi.GPIO no disponible, omitiendo monitoreo de botón.")


class misk():
    def abrir_porton(self, usuario=str, personas=dict, tipo_porton=str, observaciones=""):

        self.activar_porton(tipo_porton)

        # 1. DATOS PREVIOS
        ahora = QDateTime.currentDateTime().toPython()
        str_ahora = ahora.strftime("%Y-%m-%d %H:%M:%S")   # Para SQL
        str_file_time = ahora.strftime(
            "%Y%m%d_%H%M%S")    # Para nombre archivo

        # 2. CAPTURAR FOTO (Una sola vez por evento de apertura)
        # Se guarda localmente en C:/.../temp_fotos/
        ruta_foto_evento = self.capturar_foto_unica(tipo_porton, str_file_time)

        db = mc.connect(
            host=host_ip, user=database_user, password=database_password,
            database="esmeralda_software", use_pure=True
        )
        c = db.cursor()

        output_nombres = ""
        lista_para_sync = []  # Aquí acumularemos los datos para enviarlos juntos al final

        try:
            for persona in personas:
                print(f"Procesando: {persona['nombre']}")

                # Lógica de 'current_personas' (Mantenemos tu lógica original)
                if persona['rol'] != "Otros":
                    if tipo_porton == "ENTRADA":
                        c.execute(
                            "INSERT INTO current_personas (identificador, rol, nombre, observaciones) VALUES (%s, %s, %s, %s)",
                            (persona['identificador'], persona['rol'],
                             persona['nombre'], observaciones)
                        )
                    elif tipo_porton == "SALIDA":
                        c.execute(
                            "DELETE FROM current_personas WHERE identificador = %s", (persona['identificador'],))

                # Generar ID Único para Historial (Timestamp + DNI para evitar colisiones)
                id_acceso = f"{ahora.strftime('%Y%m%d%H%M%S')}_{persona['identificador']}"

                # 3. INSERT LOCAL (Incluyendo la ruta de la foto y el nombre)
                c.execute(
                    """INSERT INTO historial_acceso 
                        (id, datetime, porton, usuario, rol, identificador, nombre, observaciones, foto_path) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (id_acceso, str_ahora, tipo_porton, usuario, persona['rol'],
                     persona['identificador'], persona['nombre'], observaciones, ruta_foto_evento)
                )

                output_nombres += f"• {persona['nombre']}\n"

                # Agregamos a la lista temporal para sincronizar luego
                lista_para_sync.append({
                    "id": id_acceso,
                    "datetime": str_ahora,
                    "porton": tipo_porton,
                    "usuario": usuario,
                    "rol": persona['rol'],
                    "identificador": persona['identificador'],
                    "nombre": persona['nombre'],
                    "observaciones": observaciones,
                    "foto_path": ruta_foto_evento  # Enviamos la ruta local
                })

            db.commit()

            # 6. DISPARAR SINCRONIZACIÓN (En segundo plano)
            if lista_para_sync:
                payload = {
                    "hotel_id": HOTEL,  # <--- OJO: Usa tu variable global de config
                    "accesos": lista_para_sync
                }
                hilo_sync = threading.Thread(
                    target=self.sync_servidor,
                    args=(payload, "/api/sync/accesos"),
                    daemon=True
                )
                hilo_sync.start()

            # 7. TELEGRAM (Opcional: Mantener tu aviso pero sin tomar otra foto)
            # Puedes adaptar tu función tg_message para enviar texto simple
            # self.tg_message(f"Portón {tipo_porton}\n{output_nombres}")

        except Exception as e:
            db.rollback()
            print(f"❌ Error en abrir_porton: {e}")
            # (Opcional) self.errorMSG("Error abriendo portón", str(e))
        finally:
            c.close()
            db.close()

    def activar_porton(self, tipo_porton):
        try:
            import gpiod
            import time
            from gpiod.line import Direction, Value, Bias

            lineas = {
                "ENTRADA": 112,
                "SALIDA": 111
            }

            if tipo_porton not in lineas:
                print(
                    f"[ERROR] Tipo porton inválido: {tipo_porton}. Usa 'ENTRADA' o 'SALIDA'.")
                return

            linea_objetivo = lineas[tipo_porton]
            print(f"[INFO] Abriendo porton {tipo_porton}...")

            try:
                with gpiod.request_lines(
                    "/dev/gpiochip1",
                    consumer="porton-control",
                    config={
                        linea_objetivo: gpiod.LineSettings(
                            direction=Direction.OUTPUT,
                            output_value=Value.INACTIVE  # Estado inactivo por defecto
                        )
                    }
                ) as request:
                    request.set_value(linea_objetivo, Value.ACTIVE)
                    time.sleep(1)
                    request.set_value(linea_objetivo, Value.INACTIVE)

                    print(
                        f"[INFO] Portón {tipo_porton} abierto correctamente.")
            except Exception as e:
                print(f"[ERROR] No se pudo abrir el porton {tipo_porton}: {e}")

        except ImportError:
            print("[INFO] Librería gpiod no disponible, omitiendo control de portón.")

    def sync_servidor(self, payload, endpoint):

        # --- CONFIGURACIÓN ---
        # Ajusta esto a tu URL real (Tunnel o IP Local)
        BASE_URL = "https://esm.30416967.xyz"
        TOKEN = "2003Cattivellio$"

        # Variables de conexión local (Asumo que existen en tu clase o son globales)
        LOCAL_DB_HOST = host_ip
        LOCAL_DB_USER = database_user
        LOCAL_DB_PASS = database_password
        LOCAL_DB_NAME = "esmeralda_software"

        # --- 1. VALIDACIÓN PREVIA ---
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception as e:
                print(f"❌ Error crítico: Payload no es JSON válido: {e}")
                return {"status": "error", "msg": "Payload inválido"}

        # --- 2. HELPER: ENCODER PERSONALIZADO ---
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (date, datetime)):
                    return str(obj)
                if isinstance(obj, Decimal):
                    return float(obj)
                if isinstance(obj, timedelta):
                    return str(obj)
                try:
                    return str(obj)
                except:
                    return "Unserializable_Data"

        # --- 3. HELPER: CONEXIÓN LOCAL ---
        def _get_local_conn():
            try:
                return mc.connect(
                    host=LOCAL_DB_HOST, user=LOCAL_DB_USER,
                    password=LOCAL_DB_PASS, database=LOCAL_DB_NAME, autocommit=True
                )
            except:
                return None

# --- 4. HELPER: SUBIR IMÁGENES (Con reporte de error en Observaciones) ---
        def _procesar_imagenes(data_dict):
            listas_a_revisar = data_dict.get('accesos', [])
            if not listas_a_revisar:
                return True

            hotel_id = data_dict.get('hotel_id', 'unknown')
            headers_auth = {"Authorization": f"Bearer {TOKEN}"}

            todas_subidas = True

            for item in listas_a_revisar:
                ruta = item.get('foto_path')

                # Validar si hay ruta
                if not ruta:
                    continue

                # Detectar si es ruta local (Windows o Linux)
                es_ruta_local = ":\\" in ruta or ruta.startswith(
                    "/") or ":/" in ruta

                if es_ruta_local:
                    # CASO A: El archivo SÍ existe -> Intentar subir
                    if os.path.exists(ruta):
                        print(f"📸 Subiendo: {ruta}")
                        try:
                            with open(ruta, 'rb') as f:
                                tipo_carpeta = item.get('porton') or 'general'
                                files = {'file': (os.path.basename(ruta), f)}
                                data_form = {'hotel_id': hotel_id,
                                             'tipo': tipo_carpeta}

                                resp = requests.post(
                                    f"{BASE_URL}/api/upload",
                                    files=files, data=data_form, headers=headers_auth, timeout=15
                                )

                                if resp.status_code == 200:
                                    minio_path = resp.json().get('path')
                                    print(f"   ✅ Subida OK: {minio_path}")
                                    # Actualizamos a URL nube
                                    item['foto_path'] = minio_path

                                    # Borrado seguro
                                    try:
                                        os.remove(ruta)
                                    except:
                                        pass
                                else:
                                    # Error del servidor (500, 400)
                                    error_server = f" | ⚠️ FOTO ERROR: Servidor rechazó subida ({resp.status_code})"
                                    item['observaciones'] = (
                                        item.get('observaciones') or "") + error_server
                                    print(f"   ⚠️ {error_server}")
                                    todas_subidas = False

                        except Exception as e:
                            # Error de conexión o archivo
                            error_msg = f" | ⚠️ FOTO ERROR: Excepción al subir ({str(e)})"
                            item['observaciones'] = (
                                item.get('observaciones') or "") + error_msg
                            print(f"   ❌ {error_msg}")
                            todas_subidas = False

                    # CASO B: El archivo NO existe -> Reportar en Observaciones
                    else:
                        print(f"🚨 ERROR: Archivo no encontrado: {ruta}")

                        # 1. Inyectamos el error en las observaciones para verlo en la WebApp
                        obs_actual = item.get('observaciones') or ""
                        mensaje_error = f" [⚠️ SYSTEM: Foto perdida. Ruta no encontrada: '{ruta}']"
                        item['observaciones'] = obs_actual + mensaje_error

                        # 2. Ponemos foto_path en None para no romper la imagen en la Web
                        item['foto_path'] = None

                        # Nota: No marcamos todas_subidas=False porque no ganamos nada reintentando,
                        # la foto ya no está en el disco. Mejor que suba la data (el texto).

            return todas_subidas

# --- 5. HELPER: ENVIAR HTTP ---
        def _enviar_http(url_endpoint, data_dict, es_reintento=False):
            # ... (código previo igual) ...

            try:
                json_data = json.dumps(data_dict, cls=CustomEncoder)

                if not es_reintento:
                    print(f"📤 Enviando JSON a {url_endpoint}...")

                # AQUÍ OCURRE EL CIERRE
                resp = requests.post(
                    full_url, data=json_data, headers=headers, timeout=10)

                if resp.status_code in [200, 201]:
                    if not es_reintento:
                        print("✅ Sincronización exitosa.")
                    return True
                else:
                    print(f"⚠️ Server rechazó ({resp.status_code}): {resp.text}")
                    return False

            # --- CAMBIO AQUÍ: Capturamos 'Exception' en lugar de solo RequestException ---
            except Exception as e:
                # Esto evitará que el programa se cierre y te mostrará el error real
                print(f"❌ ERROR CRÍTICO al conectar: {type(e).__name__}: {e}")
                
                # Opcional: Si quieres ver más detalles, importa traceback
                # import traceback
                # traceback.print_exc()
                
                if not es_reintento:
                    print("⚠️ Guardando en cola local debido al error.")
                return False

        # --- 5. HELPER: ENVIAR HTTP ---
        def _enviar_http(url_endpoint, data_dict, es_reintento=False):
            # PASO A: Intentar subir fotos primero
            if not _procesar_imagenes(data_dict):
                if not es_reintento:
                    print("⚠️ Fallo en fotos. Guardando en cola para reintentar luego.")
                return False  # Si fallan las fotos, abortamos para no guardar rutas rotas en el server

            # PASO B: Enviar JSON limpio
            full_url = f"{BASE_URL}{url_endpoint}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN}"
            }
            try:
                json_data = json.dumps(data_dict, cls=CustomEncoder)

                if not es_reintento:
                    print(f"📤 Enviando JSON a {url_endpoint}...")

                resp = requests.post(
                    full_url, data=json_data, headers=headers, timeout=10)

                if resp.status_code in [200, 201]:
                    if not es_reintento:
                        print("✅ Sincronización exitosa.")
                    return True
                else:
                    print(
                        f"⚠️ Server rechazó ({resp.status_code}): {resp.text}")
                    return False
            except requests.exceptions.RequestException:
                if not es_reintento:
                    print("⚠️ Sin conexión al servidor API.")
                return False

        # --- 6. HELPER: GUARDAR EN COLA LOCAL ---
        def _guardar_en_cola(url_endpoint, data_dict):
            conn = _get_local_conn()
            if not conn:
                return False
            try:
                cursor = conn.cursor()
                # Guardamos el dict original (con rutas locales C:/...)
                json_data = json.dumps(data_dict, cls=CustomEncoder)
                cursor.execute(
                    "INSERT INTO cola_servidor (endpoint, payload) VALUES (%s, %s)",
                    (url_endpoint, json_data)
                )
                print(f"💾 [OFFLINE] Guardado en cola local.")
                return True
            except Exception as e:
                print(f"❌ Error DB Local: {e}")
                return False
            finally:
                if conn.is_connected():
                    conn.close()

        # --- 7. HELPER: PROCESAR COLA PENDIENTE ---
        def _procesar_cola():
            conn = _get_local_conn()
            if not conn:
                return False
            
            try:
                # Usamos un bucle infinito que rompemos con 'break' cuando no hay más pendientes
                while True:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM cola_servidor ORDER BY id ASC LIMIT 1")
                    pendiente = cursor.fetchone()

                    if not pendiente:
                        return True  # Cola vacía, terminamos

                    print(f"🔄 Reintentando item ID {pendiente['id']} de la cola...")
                    
                    try:
                        datos_viejos = json.loads(pendiente['payload'])
                        enviado = _enviar_http(pendiente['endpoint'], datos_viejos, es_reintento=True)
                    except Exception as e:
                        print(f"Error procesando payload de cola: {e}")
                        # Si el JSON está corrupto, lo borramos para no trabar la cola
                        enviado = False
                        # Ojo: aquí decide si borrarlo o dejarlo. 
                        # Si falla el JSON (no la red), mejor borrarlo:
                        # conn.cursor().execute("DELETE FROM cola_servidor WHERE id=%s", (pendiente['id'],))

                    if enviado:
                        conn.cursor().execute("DELETE FROM cola_servidor WHERE id = %s", (pendiente['id'],))
                        print(f"   -> Recuperado exitosamente.")
                        # El while continúa automáticamente al siguiente
                    else:
                        # Si falló el envío (probablemente no hay internet de nuevo), paramos
                        return False 
                        
            except Exception as e:
                print(f"Error general en cola: {e}")
                return False
            finally:
                if conn.is_connected():
                    conn.close()

        # --- EJECUCIÓN PRINCIPAL ---
        print(f"--- Sync Iniciado: {endpoint} ---")

        # 1. Intentar vaciar la cola vieja primero
        cola_ok = _procesar_cola()

        if not cola_ok:
            _guardar_en_cola(endpoint, payload)
            return {"status": "queued", "msg": "Guardado localmente (Cola pendiente o sin red)"}

        # 2. Intentar enviar el dato actual
        if _enviar_http(endpoint, payload):
            return {"status": "success", "msg": "Sincronizado correctamente"}
        else:
            _guardar_en_cola(endpoint, payload)
            return {"status": "queued", "msg": "Fallo de red/fotos. Guardado localmente."}

    def registrar_log(self, tipo, usuario, descripcion, identificador):
        try:
            db = mc.connect(
                host=host_ip, user=database_user, password=database_password,
                database="esmeralda_software", use_pure=True
            )
            c = db.cursor()

            ahora = QDateTime.currentDateTime().toPython()

            # 1. INSERT LOCAL
            sql = """
                INSERT INTO usuario_log (datetime, tipo, usuario, descripcion, identificador) 
                VALUES (%s, %s, %s, %s, %s)
            """
            c.execute(sql, (ahora, tipo, usuario, descripcion, identificador))
            db.commit()

            # 2. CAPTURAR ID y DATA PARA SYNC
            new_id = c.lastrowid

            log_data = {
                "id": new_id,
                "datetime": ahora,  # El encoder lo pasará a string ISO
                "tipo": tipo,
                "usuario": usuario,
                "descripcion": descripcion,
                "identificador": identificador
            }

            payload = {
                "hotel_id": HOTEL,  # O self.hotel_id
                "logs": [log_data]
            }

            # 3. ENVIAR EN HILO
            threading.Thread(
                target=self.sync_servidor,
                args=(payload, "/api/sync/logs"),
                daemon=True
            ).start()

        except Exception as e:
            print(f"❌ Error registrando log: {e}")
        finally:
            if 'c' in locals():
                c.close()
            if 'db' in locals():
                db.close()

    def errorMSG(self, text, title):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(f"img/minilogo.ico"))
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        x = msg.exec()

    def informationMSG(self, text, title):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(f"img/minilogo.ico"))
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        x = msg.exec()

    def questionMSG(self, text, title):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(f"img/minilogo.ico"))
        msg.setIcon(QMessageBox.Question)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        x = msg.exec()
        return x

    def open_file(self, filepath):
        if platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))

    def tg_message(self, message_text):
        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute("SELECT config_value FROM config WHERE config_key = 'tg_bot_token' OR config_key = 'tg_chat' OR config_key = 'tg_chat_id'")
        data = tuple(item[0] for item in c.fetchall())

        if int(data[1]):
            QApplication.setOverrideCursor(Qt.WaitCursor)

            c.execute("SELECT chat_id, message_text FROM queued_telegram")
            queued_telegram = c.fetchall()

            try:
                tb = telebot.TeleBot(data[0])
                if queued_telegram:
                    for i in queued_telegram:
                        tb.send_message(i[0], i[1], parse_mode="HTML")
                        time.sleep(3)

                c.execute("TRUNCATE queued_telegram")

                tb.send_message(data[2], message_text, parse_mode="HTML")
                QApplication.restoreOverrideCursor()

            except Exception as error:
                QApplication.restoreOverrideCursor()
                self.errorMSG(
                    f"No se puede ejecutar su orden debido\na problemas de conexión\n\n{error}", "Error de internet")

                c.execute(
                    f"INSERT INTO queued_telegram (chat_id, message_text) VALUES ('{data[2]}', '{message_text}')")

            db.commit()

        else:
            print("Telegram option is off")

        c.close()
        db.close()

    def tg_cam_photo(self, text, porton):
        import cv2

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        if porton == "ENTRADA":
            c.execute("SELECT config_value FROM config WHERE config_key = 'camera_entrada' OR config_key = 'tg_bot_token' OR config_key = 'tg_camera' OR config_key = 'tg_chat_id'")
        else:
            c.execute("SELECT config_value FROM config WHERE config_key = 'camera_salida' OR config_key = 'tg_bot_token' OR config_key = 'tg_camera' OR config_key = 'tg_chat_id'")

        data = tuple(item[0] for item in c.fetchall())

        if int(data[2]) == True:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                # Intenta obtener la imagen de la cámara
                vidcap = cv2.VideoCapture(data[0])
                success, image = vidcap.read()
                if not success:
                    # Lanza un error si no se pudo leer el frame
                    raise ConnectionError(
                        "No se pudo obtener un frame de la cámara.")

                # Guarda y envía la foto por Telegram
                cv2.imwrite("temp/frame0.jpg", image)
                tb = telebot.TeleBot(data[1])
                photo = open("temp/frame0.jpg", "rb")
                tb.send_photo(data[3], photo, text, parse_mode="HTML")

            except Exception as e:  # Es mejor capturar excepciones específicas y ver el error
                # Imprime el error real para depurar
                print(f"Ocurrió un error: {e}")
                self.errorMSG(
                    "No se pudo enviar la foto por\nproblemas de conexión con la cámara.", "Error de Conexión")
                self.tg_message(
                    f"⚠️ <b>No se mando foto debido a problemas de conexión</b> ⚠️\n{text}")

            finally:
                # ESTO SE EJECUTARÁ SIEMPRE: después del try o después del except.
                QApplication.restoreOverrideCursor()
        else:
            self.tg_message(text)

        c.close()
        db.close()

    def tg_photo(self, directory, tg_text):


        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute(
            "SELECT config_value FROM config WHERE config_key = 'tg_bot_token' OR config_key = 'tg_chat_id'")
        data = tuple(item[0] for item in c.fetchall())

        tb = telebot.TeleBot(
            data[0])

        photo = open(directory, "rb")
        tb.send_photo(data[1], photo, tg_text, parse_mode="HTML")

        c.close()
        db.close()

    def tg_doc(self, directory, tg_text):

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute(
            "SELECT config_value FROM config WHERE config_key = 'tg_bot_token' OR config_key = 'tg_chat_id'")
        data = tuple(item[0] for item in c.fetchall())

        tb = telebot.TeleBot(
            data[0])

        doc = open(directory, "rb")

        tb.send_document(chat_id=data[1], document=doc,
                         caption=tg_text, parse_mode="HTML")

        c.close()
        db.close()

    def capturar_foto_unica(self, tipo_porton, timestamp_str):
        import cv2

        ruta_final = None
        url_camara = None

        # 1. Leer Configuración
        try:
            db = mc.connect(
                host=host_ip, user=database_user, password=database_password,
                database="esmeralda_software", use_pure=True
            )
            c = db.cursor()

            key = 'camera_entrada' if tipo_porton == "ENTRADA" else 'camera_salida'
            c.execute(
                "SELECT config_value FROM config WHERE config_key = %s", (key,))
            res = c.fetchone()

            if res:
                url_camara = res[0]
                # Si es un índice USB (ej: '0'), lo convertimos a entero
                if str(url_camara).isdigit():
                    url_camara = int(url_camara)

        except Exception as e:
            print(f"❌ Error DB Config: {e}")
            return None
        finally:
            if 'c' in locals():
                c.close()
            if 'db' in locals():
                db.close()

        if url_camara is None:
            print(f"⚠️ No hay cámara configurada para {tipo_porton}")
            return None

        # 2. Captura con Timeout Controlado
        try:
            carpeta = os.path.abspath("temp_fotos")
            os.makedirs(carpeta, exist_ok=True)
            nombre_archivo = f"{timestamp_str}_{tipo_porton}.jpg"
            ruta_final = os.path.join(carpeta, nombre_archivo)

            print(f"📸 Intentando conectar a cámara: {url_camara}")

            # --- TRUCO PARA QUE NO SE CONGELE 30 SEGUNDOS ---
            # Configura FFmpeg para que use TCP (más estable) y timeout de 3 seg (3000000 microsegundos)
            # OJO: Solo funciona si la URL es RTSP o HTTP stream. Si es USB (int), esto se ignora.
            if isinstance(url_camara, str):
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|timeout;3000000"

            # Usamos CAP_FFMPEG explícitamente para que lea las opciones de entorno
            vidcap = cv2.VideoCapture(url_camara, cv2.CAP_FFMPEG)

            if vidcap.isOpened():
                success, image = vidcap.read()
                if success:
                    cv2.imwrite(ruta_final, image)
                    print(f"✅ Foto capturada.")
                else:
                    print("❌ Conectó pero no entregó imagen (Stream vacío).")
                    ruta_final = None
            else:
                print("❌ No se pudo abrir la cámara (Timeout o URL errónea).")
                ruta_final = None

            vidcap.release()

        except Exception as e:
            print(f"❌ Error Crítico Cámara: {e}")
            ruta_final = None

        return ruta_final

    def export_chart(self, title, x, xlabel, y, ylabel, bars_color):
        return
        # import matplotlib.pyplot as plt

        # for i in range(len(x)):
        #     plt.text(i, y[i], y[i], ha="center", va="bottom")

        # y_pos = np.arange(len(x))

        # # Create bars
        # plt.bar(y_pos, y, fc=bars_color, ec="black")
        # # Create names on the x-axis
        # plt.xticks(y_pos, x)

        # fig = plt.gcf()
        # fig.set_size_inches(15, 5)

        # plt.title(title)
        # plt.xlabel(xlabel)
        # plt.ylabel(ylabel)

        # plt.savefig('temp/graph.png', bbox_inches='tight')
        # plt.clf()

    def iniciar_servidor_flask(self):
        from hotel_tv_display import flask_app

        flask_app.socketio.run(
            flask_app.app,
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False
        )

    def backup_database_excel(self):

        QApplication.setOverrideCursor(Qt.WaitCursor)

        db = mc.connect(
            host=host_ip,
            user=database_user,
            password=database_password,
            database="esmeralda_software",
            use_pure=True
        )

        c = db.cursor()

        c.execute(
            "SELECT config_value FROM config WHERE config_key = 'hotel_nombre'")
        hotel_name = c.fetchone()[0]

        c.close()
        db.close()

        # 1. Directorio donde guardar el .sql
        backup_dir = backup_dir or os.path.join(os.getcwd(), "back_up")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"{hotel_name}.sql")

        # 2. Detectar herramienta de volcado
        dump_exe = shutil.which(
            "mariadb-dump") or shutil.which("mysqldump")
        if not dump_exe:
            raise RuntimeError(
                "No se encontró ni 'mariadb-dump' ni 'mysqldump' en el PATH."
            )

        # 3. Construir comando como lista (más seguro que shell=True)
        cmd = [
            dump_exe,
            "--host", host_ip,
            "--user", database_user,
            f"--password={database_password}",
            "esmeralda_software"
        ]

        # 4. Ejecutar y capturar errores
        try:
            with open(backup_path, "w", encoding="utf-8") as f:
                proceso = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            if proceso.returncode != 0:
                # Si hay error, eliminar el archivo parcial
                os.remove(backup_path)
                raise RuntimeError(
                    f"Error durante el dump (code {proceso.returncode}):\n{proceso.stderr}"
                )

            print(f"✅ Backup exitoso: {backup_path}")

        except Exception as e:
            print(f"❌ Backup fallido: {e}")

# class SplashScreen(QSplashScreen):
#     def __init__(self):
#         super().__init__(QPixmap("img/splashy.png"))
#         QApplication.setOverrideCursor(Qt.WaitCursor)
#         # self.setFixedSize(400, 200)
#         self.setWindowTitle("Splash Screen with ProgressBar")
#         self.progress = QProgressBar(self)
#         self.progress.setFormat("")
#         self.progress.setGeometry(0, 220, 506, 8)
#         self.progress.setAlignment(Qt.AlignCenter)
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_progress)
#         self.progress_value = 0
#         self.timer.start(100)


#     def update_progress(self):
#         self.progress_value += 100
#         self.progress.setValue(self.progress_value)
#         if self.progress_value >= 100:
#             self.timer.stop()
#             self.close()
#             self.main_window = Habitaciones()
#             self.main_window.show()
#             QApplication.restoreOverrideCursor()
################################# SETING UP GLOBAL STYLESHEET #################################
# red-darkred: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 rgb(150, 2, 2), stop:0 rgb(242, 5, 5))
# green-cyan: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 #11998E, stop:0 #38ef7d)



# pruple-test: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 #5f0a87, stop:0 #bb43d7)
style = '''
        QMainWindow, QWidget {
            background-color: rgb(20, 20, 20);
            color: white;
            font-family: roboto
        }
        QFrame {
            background-color: rgb(30, 30, 30);
            border-radius: 8px;
            
        }
        QLineEdit {
            color: rgb(20, 0, 0);
            background-color: rgb(255, 255, 255);            
            border-radius: 4px;
            font-size: 15px;
            padding: 4px
        }
        QPushButton {
            background-color: rgb(44, 44, 44);
            border-color: white;
            color: rgb(242, 242, 242);
            border-radius: 2px;
            font-size: 12px;
            padding: 6px
        }

        QPushButton:hover {
            background-color: rgb(242, 242, 242);
            color: black;
        }
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.4, y2:0.4, stop:1 #11998E, stop:0 #38ef7d);
            color: white;
        }

        QPushButton:disabled {background-color:black; font-size: 14px}


        QInputDialog QLabel, QMessageBox QLabel{
            background-color: None;
            color: white;
            font-size: 14px;
        }
        QInputDialog QPushButton, QMessageBox QPushButton, QTabWidget QPushButton{
            padding: 5px 15px;
        }
        QLabel {
            background: rgba(0, 0, 0, 0);
            color: rgb(242, 242, 242);
            font-size: 12px;
        }
        QPlainTextEdit {
            color: rgb(20, 0, 0);
            background-color: rgb(255, 255, 255);
            border-radius: 2px;
            padding: 4px;
            font-size: 14px;
        }
        QComboBox {
            color: rgb(20, 0, 0);
            background-color: rgb(255, 255, 255);
            border-radius: 2px;
            padding: 4px;
            font-size: 13px;
        }
        QComboBox:item{
            color: white; 
            selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 #11998E, stop:0 #38ef7d);  
        }

        QTabWidget  { 
            border-color: (80, 80, 80); 
            background: rgb(245, 245, 245);
            border-radius: 2px;
        } 

        QTabWidget:pane { 
            border-color: (80, 80, 80); 
            border-radius: 2px;
        } 
        QTabBar:tab {
            background-color: rgb(40, 40, 40); 
            height: 24px;
            width: 92px;
            padding: 5px;
            border-radius: 4px;
            margin-top: 5px;
            font-size: 10pt;
        } 

        QTabBar:tab:disabled {
            background-color:black;
            height: 24px;
            width: 92px;
            padding: 5px;
            border-radius: 4px;
            margin-top: 5px;
            font-size: 10pt;
        } 

        QTabBar:tab:selected { 
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 #11998E, stop:0 #38ef7d);
            margin-top: 4px;
            border-radius: 4px;
            font-weight: bold;
        }

        QHeaderView:section {
            background-color: rgb(38,38,38);
            padding: 2px;
            color: white;
            border: 1px solid #fffff8;
            font-size: 10pt;
            font-weight: bold;
        }

        QTableView {
            font-size: 10pt;
            }

        QTableWidget {
            background-color: rgb(13,13,13);
            gridline-color: rgb(130,130,130);
            font-size: 10pt;
        }
        QScrollBar {
            background-color: rgb(80, 80, 80);
        }
        QToolTip{ 
            border: 2px solid rgb(44, 44, 44);
            background-color: rgb(44, 44, 44);
            color: white;
            font: 10pt;
            }
        QCheckBox {
            font-size: 14px;
        }
        QCheckBox::indicator {
            width: 15px;
            height: 15px;
            border-radius: 2px;
        }
        QCheckBox::indicator:checked {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 #11998E, stop:0 #38ef7d);
        }
        QCheckBox::indicator:unchecked {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:1 rgb(150, 2, 2), stop:0 rgb(242, 5, 5));
        }

        QTimeEdit {
            color: rgb(20, 0, 0);
            background-color: rgb(255, 255, 255);            
            border-radius: 4px;
            font-size: 14px;
            padding: 3px;
        }

        QSpinBox {
            color: rgb(20, 0, 0);
            background-color: rgb(255, 255, 255);            
            border-radius: 2px;
            font-size: 14px;
            padding: 3px;
        }

        QDoubleSpinBox {
            color: rgb(20, 0, 0);
            background-color: rgb(255, 255, 255);            
            border-radius: 4px;
            font-size: 14px;
            padding: 3px;
        }
        QDateEdit {
            color: rgb(20, 0, 0);
            background-color: rgb(255, 255, 255);            
            border-radius: 2px;
            font-size: 14px;
            padding: 2px;            
        }

        QDateTimeEdit {
            color: rgb(20, 0, 0);
            background-color: rgb(255, 255, 255);            
            border-radius: 2px;
            font-size: 14px;
            padding: 2px;            
        }

        QCalendarWidget QAbstractItemView:enabled {
            color: rgb(20, 0, 0);
            background-color: rgb(255, 255, 255);            
            border-radius: 2px;
            font-size: 12px;
            }

            
        QProgressBar {
            background-color: rgb(20, 20, 20);  
            color: rgb(20, 20, 20);    
        }

        QProgressBar::chunk {
            background-color: #24cb7c;    
            color: #24cb7c;
        }
        '''

################################# START APP #################################

if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setStyleSheet(style)
    app.setWindowIcon(QIcon('img/minilogo.ico'))

    appversion = "beta 1"

    window = Habitaciones()
    window.show()

    sys.exit(app.exec())

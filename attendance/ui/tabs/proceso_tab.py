from PySide6.QtCore import QObject, Signal, QThread
from proceso.behavior_processor import BehaviorProcessor
class AnalysisWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, session, user_identifier, fecha_inicio, fecha_fin):
        super().__init__()
        self.session = session
        self.user_identifier = user_identifier
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

    def run(self):
        try:
            processor = BehaviorProcessor(self.session)

            result = processor.process_user(
                user_identifier=self.user_identifier,
                fecha_inicio=self.fecha_inicio,
                fecha_fin=self.fecha_fin
            )

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QDateEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QHeaderView, QSizePolicy, QTableWidgetItem
from PySide6.QtWidgets import QMessageBox


from attendance.models import User


class ProcesoTab(QWidget):
    # ...existing code...
    def export_results(self, path=None):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        row_count = self.result_table.rowCount()
        col_count = self.result_table.columnCount()
        if row_count == 0:
            QMessageBox.information(self, "Sin datos", "No hay datos para exportar.")
            return
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "Exportar resultados", "resultados.xlsx", "Excel Files (*.xlsx)")
            if not path:
                return
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active if wb.active is not None else wb.create_sheet()
            # Escribir encabezados
            headers = []
            for i in range(col_count):
                item = self.result_table.horizontalHeaderItem(i)
                headers.append(item.text() if item is not None else "")
            ws.append(headers)
            # Escribir filas
            for row in range(row_count):
                values = []
                for col in range(col_count):
                    item = self.result_table.item(row, col)
                    values.append(item.text() if item is not None else "")
                ws.append(values)
            wb.save(path)
            QMessageBox.information(self, "Exportación exitosa", f"Resultados exportados a {path}")
        except ImportError:
            QMessageBox.warning(self, "Dependencia faltante", "Debe instalar openpyxl para exportar a Excel.\nEjecute: pip install openpyxl")
        except Exception as e:
            QMessageBox.warning(self, "Error de exportación", f"No se pudo exportar el archivo:\n{str(e)}")

    def __init__(self, session):
        super().__init__()

        self.session = session

        self.main_layout = QVBoxLayout(self)

        # ---------------------------
        # Filtros superiores
        # ---------------------------
        filters_layout = QHBoxLayout()


        self.user_selector = QComboBox()

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        self.analyze_button = QPushButton("Analizar")

        filters_layout.addWidget(QLabel("Usuario:"))
        filters_layout.addWidget(self.user_selector)
        filters_layout.addWidget(QLabel("Desde:"))
        filters_layout.addWidget(self.start_date)
        filters_layout.addWidget(QLabel("Hasta:"))
        filters_layout.addWidget(self.end_date)
        filters_layout.addWidget(self.analyze_button)

        self.main_layout.addLayout(filters_layout)

        # ---------------------------
        # Tabla de resultados
        # ---------------------------
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["Métrica", "Valor"])

        self.result_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)



        self.main_layout.addWidget(self.result_table)

        # Botón Exportar debajo de la tabla
        self.export_button = QPushButton("Exportar")
        self.export_button.clicked.connect(self.export_results)
        self.main_layout.addWidget(self.export_button)



        # ---------------------------
        # Conexión
        # ---------------------------

        self.analyze_button.clicked.connect(self.run_analysis)

        # Cargar usuarios después de inicializar todos los widgets
        self.load_users()

    def load_users(self):
        self.user_selector.clear()
        self.user_selector.addItem("Seleccione usuario", None)
        users = (
            self.session.query(User)
            .filter(User.is_active == True)
            .order_by(User.last_name, User.first_name)
            .all()
        )
        for user in users:
            display_text = f"{user.first_name or ''} {user.last_name or ''} ({user.identifier})".strip()
            self.user_selector.addItem(display_text, user.identifier)

    # -------------------------------------------------
    # Ejecutar análisis
    # -------------------------------------------------
    def run_analysis(self):
        user_identifier = self.user_selector.currentData()
        fecha_inicio = self.start_date.date().toPython()
        fecha_fin = self.end_date.date().toPython()

        # Validación defensiva previa
        if user_identifier is None:
            QMessageBox.warning(self, "Usuario requerido", "Debe seleccionar un usuario para analizar.")
            return
        if fecha_inicio and fecha_fin:
            # Convertir a date si es QDate
            if isinstance(fecha_inicio, QDate):
                fecha_inicio = fecha_inicio.toPython()
            if isinstance(fecha_fin, QDate):
                fecha_fin = fecha_fin.toPython()
            # Convertir a date si es datetime
            if hasattr(fecha_inicio, 'date'):
                fecha_inicio = fecha_inicio.date()
            if hasattr(fecha_fin, 'date'):
                fecha_fin = fecha_fin.date()
            if fecha_inicio > fecha_fin:
                QMessageBox.warning(self, "Error", "La fecha de inicio no puede ser mayor que la fecha de fin.")
                return

        self.analyze_button.setEnabled(False)

        thread = QThread()
        self.worker = AnalysisWorker(self.session, user_identifier, fecha_inicio, fecha_fin)
        self.worker.moveToThread(thread)
        thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.finished.connect(thread.quit)
        self.worker.error.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self.analyze_button.setEnabled(True))
        thread.start()

    def on_analysis_finished(self, result):
        self.display_results(result)

    def on_analysis_error(self, message):
        QMessageBox.warning(self, "Error de análisis", message)

    # -------------------------------------------------
    # Mostrar resultados
    # -------------------------------------------------
    def display_results(self, result):
        features = result.get("features", {})

        ordered_keys = [
            "avg_daily_minutes",
            "median_daily_minutes",
            "std_daily_minutes",
            "min_daily_minutes",
            "max_daily_minutes",
            "underwork_rate",
            "overwork_rate",
            "coefficient_variation",
            "inconsistency_count",
            "total_days",
            "trend_slope_minutes",
            "volatility_index",
            "sudden_drop_flag",
            "score",
            "risk"
        ]
        # Escribir encabezados
        headers = []
        for i in range(col_count):
            item = self.result_table.horizontalHeaderItem(i)
            headers.append(item.text() if item is not None else "")
        ws.append(headers)
        # Escribir filas
        for row in range(row_count):
            values = []
            for col in range(col_count):
                item = self.result_table.item(row, col)
                values.append(item.text() if item is not None else "")
            ws.append(values)
        wb.save(path)
        QMessageBox.information(self, "Exportación exitosa", f"Resultados exportados a {path}")
    except ImportError:
        QMessageBox.warning(self, "Dependencia faltante", "Debe instalar openpyxl para exportar a Excel.\nEjecute: pip install openpyxl")
    except Exception as e:
        QMessageBox.warning(self, "Error de exportación", f"No se pudo exportar el archivo:\n{str(e)}")
                elif key == "risk":
                    value = result.get("risk")
                else:
                    value = ""

                if key.endswith("_rate") and value is not None:
                    value = f"{value * 100:.1f}%"
                elif key in ["coefficient_variation", "volatility_index"] and value is not None:
                    value = f"{value:.3f}"
                elif key == "trend_slope_minutes" and value is not None:
                    value = f"{value:+.1f} min/día"
                elif key == "sudden_drop_flag" and value is not None:
                    value = "Sí" if value == 1 else "No"
                elif key == "score" and value is not None:
                    value = f"{int(value)}"
                elif key == "risk" and value is not None:
                    value = str(value).upper()
                else:
                    value = str(value)

                rows.append((label, value))

        self.result_table.setRowCount(len(rows))
        for row_index, (metric, value) in enumerate(rows):
            self.result_table.setItem(row_index, 0, QTableWidgetItem(metric))
            self.result_table.setItem(row_index, 1, QTableWidgetItem(value))
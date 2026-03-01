from PySide6.QtCore import QObject, Signal, QThread, QDate
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
    QHeaderView,
)
from proceso.behavior_processor import BehaviorProcessor
from attendance.models import User


# ==========================================================
# Worker para ejecución en segundo plano
# ==========================================================
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
                fecha_fin=self.fecha_fin,
            )

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


# ==========================================================
# TAB DE PROCESO
# ==========================================================
class ProcesoTab(QWidget):
    def __init__(self, session):
        super().__init__()

        self.session = session
        self.last_result = None

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
        self.result_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.main_layout.addWidget(self.result_table)

        # ---------------------------
        # Botón Exportar
        # ---------------------------
        self.export_button = QPushButton("Exportar")
        self.export_button.clicked.connect(self.export_results)
        self.main_layout.addWidget(self.export_button)

        # ---------------------------
        # Botón Panel Ejecutivo
        # ---------------------------
        self.executive_button = QPushButton("Ver Panel Ejecutivo")
        self.executive_button.clicked.connect(self.open_executive_panel)
        self.main_layout.addWidget(self.executive_button)

        # ---------------------------
        # Conexiones
        # ---------------------------
        self.analyze_button.clicked.connect(self.run_analysis)

        self.load_users()

    # ==========================================================
    # Cargar usuarios
    # ==========================================================
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
            display_text = (
                f"{user.first_name or ''} {user.last_name or ''} ({user.identifier})"
            ).strip()
            self.user_selector.addItem(display_text, user.identifier)

    # ==========================================================
    # Ejecutar análisis
    # ==========================================================
    def run_analysis(self):
        user_identifier = self.user_selector.currentData()
        fecha_inicio = self.start_date.date().toPython()
        fecha_fin = self.end_date.date().toPython()

        if user_identifier is None:
            QMessageBox.warning(
                self, "Usuario requerido", "Debe seleccionar un usuario."
            )
            return

        if fecha_inicio > fecha_fin:
            QMessageBox.warning(
                self, "Error", "La fecha de inicio no puede ser mayor a la fecha final."
            )
            return

        self.analyze_button.setEnabled(False)

        self.thread = QThread()
        self.worker = AnalysisWorker(
            self.session, user_identifier, fecha_inicio, fecha_fin
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.analyze_button.setEnabled(True))

        self.thread.start()

    def on_analysis_finished(self, result):
        self.display_results(result)

    def on_analysis_error(self, message):
        QMessageBox.warning(self, "Error de análisis", message)

    # ==========================================================
    # Mostrar resultados
    # ==========================================================
    def display_results(self, result):
        if not result:
            QMessageBox.information(self, "Sin datos", "No se encontraron registros.")
            return

        self.last_result = result

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
            "risk",
        ]

        label_map = {
            "avg_daily_minutes": "Promedio diario trabajado (min)",
            "median_daily_minutes": "Mediana diaria (min)",
            "std_daily_minutes": "Desviación estándar (min)",
            "min_daily_minutes": "Mínimo diario (min)",
            "max_daily_minutes": "Máximo diario (min)",
            "underwork_rate": "% Días por debajo de jornada",
            "overwork_rate": "% Días con sobrejornada",
            "coefficient_variation": "Índice de variabilidad",
            "inconsistency_count": "Registros inconsistentes",
            "total_days": "Días analizados",
            "trend_slope_minutes": "Tendencia diaria (min/día)",
            "volatility_index": "Índice de volatilidad",
            "sudden_drop_flag": "Indicador de caída abrupta",
            "score": "Puntaje de riesgo",
            "risk": "Nivel de riesgo",
        }

        rows = []

        for key in ordered_keys:
            if key in features or key in ["score", "risk"]:
                label = label_map.get(key, key)

                if key in features:
                    value = features[key]
                elif key == "score":
                    value = result.get("score")
                else:
                    value = result.get("risk")

                if key.endswith("_rate") and value is not None:
                    value = f"{value * 100:.1f}%"

                elif key == "std_daily_minutes" and value is not None:
                    value = f"{value:.2f}"

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

    # ==========================================================
    # Abrir Panel Ejecutivo
    # ==========================================================
    def open_executive_panel(self):
        if not self.last_result:
            QMessageBox.information(
                self, "Sin análisis", "Primero ejecute el análisis."
            )
            return

        from attendance.ui.executive_panel_dialog import ExecutivePanelDialog

        processor = BehaviorProcessor(self.session)

        dialog = ExecutivePanelDialog(
            result=self.last_result,
            session=self.session,
            processor=processor,
            fecha_inicio=self.start_date.date().toPython(),
            fecha_fin=self.end_date.date().toPython(),
            parent=self,
        )

        dialog.exec()

    # ==========================================================
    # Exportar resultados
    # ==========================================================
    def export_results(self, path=None):
        from PySide6.QtWidgets import QFileDialog
        import openpyxl

        if self.result_table.rowCount() == 0:
            QMessageBox.information(self, "Sin datos", "No hay datos para exportar.")
            return

        if not path:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar resultados",
                "resultados.xlsx",
                "Excel Files (*.xlsx)",
            )
            if not path:
                return

        wb = openpyxl.Workbook()
        ws = wb.active

        headers = [
            self.result_table.horizontalHeaderItem(i).text()
            for i in range(self.result_table.columnCount())
        ]
        ws.append(headers)

        for row in range(self.result_table.rowCount()):
            values = [
                self.result_table.item(row, col).text()
                for col in range(self.result_table.columnCount())
            ]
            ws.append(values)

        wb.save(path)

        QMessageBox.information(
            self, "Exportación exitosa", f"Resultados exportados a {path}"
        )
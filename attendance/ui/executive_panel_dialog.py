from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import timedelta


class ExecutivePanelDialog(QDialog):

    def __init__(self, result, session, processor, fecha_inicio, fecha_fin, parent=None):
        super().__init__(parent)

        self.result = result
        self.session = session
        self.processor = processor
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

        self.setWindowTitle("Panel Ejecutivo de Análisis")
        self.resize(1000, 650)

        layout = QVBoxLayout(self)

        title = QLabel("Panel Ejecutivo del Período Analizado")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.figure = Figure(figsize=(9, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.draw_chart()
        self.generate_summary()

    # ==============================================================

    def get_previous_period_result(self):
        delta = self.fecha_fin - self.fecha_inicio
        prev_end = self.fecha_inicio - timedelta(days=1)
        prev_start = prev_end - delta

        return self.processor.process_user(
            user_identifier=self.result["user_identifier"],
            fecha_inicio=prev_start,
            fecha_fin=prev_end
        )

    # ==============================================================

    def draw_chart(self):
        from matplotlib.figure import Figure

        features = self.result.get("features", {})
        daily_minutes = features.get("daily_minutes_map", {})

        if not daily_minutes:
            return

        self.figure.clear()

        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)

        # -------------------------
        # 📊 GRÁFICO 1 — Tendencia diaria
        # -------------------------
        ordered_days = sorted(daily_minutes.keys())
        values = [daily_minutes[d] for d in ordered_days]

        labels = [d.strftime("%d-%m") for d in ordered_days]

        ax1.plot(labels, values, marker="o", linewidth=2)

        expected_daily_minutes = 480  # Puedes hacerlo dinámico si quieres
        ax1.axhline(
            y=expected_daily_minutes,
            linestyle="--",
            linewidth=1.5
        )

        ax1.set_title("Tendencia Diaria Comparativa")
        ax1.set_ylabel("Minutos trabajados")
        ax1.set_xlabel("Día")
        ax1.tick_params(axis="x", rotation=45)

        ax1.legend(["Período actual", "Jornada esperada"])

        # -------------------------
        # 📊 GRÁFICO 2 — Comparación acumulada
        # -------------------------
        total_real = sum(values)
        total_esperado = expected_daily_minutes * len(values)

        ax2.bar(["Esperado", "Real"], [total_esperado, total_real])

        ax2.set_title("Comparación Total Acumulada")

        self.canvas.draw()

        real = features.get("total_worked_minutes", 0)
        expected = features.get("expected_total_minutes", 0)

        ax2.bar(["Esperado", "Real"], [expected, real])
        ax2.set_title("Comparación Total Acumulada")

        self.figure.tight_layout()
        self.canvas.draw()

    # ==============================================================

    def generate_summary(self):
        features = self.result.get("features", {})
        risk = self.result.get("risk", "SIN_REGLAS")
        score = self.result.get("score", 0)

        total_days = features.get("total_days", 0)
        avg = features.get("avg_daily_minutes", 0)
        diff = features.get("total_difference_minutes", 0)
        volatility = features.get("coefficient_variation", 0)

        lines = []
        lines.append("INFORME EJECUTIVO")
        lines.append("-" * 50)
        lines.append(f"Días analizados: {total_days}")
        lines.append(f"Promedio diario trabajado: {avg:.1f} minutos")

        if diff > 0:
            lines.append(f"Exceso acumulado: {diff:.0f} minutos respecto al esperado.")
        elif diff < 0:
            lines.append(f"Déficit acumulado: {abs(diff):.0f} minutos respecto al esperado.")
        else:
            lines.append("Tiempo trabajado acorde a lo esperado.")

        if volatility < 0.05:
            lines.append("Comportamiento altamente estable.")
        elif volatility > 0.2:
            lines.append("Alta variabilidad en el patrón horario.")

        lines.append("")
        lines.append(f"Nivel de riesgo detectado: {risk}")
        lines.append(f"Puntaje calculado: {score}")

        self.summary_text.setText("\n".join(lines))

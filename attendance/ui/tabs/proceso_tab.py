from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class ProcesoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("Módulo Proceso (externo)")
        layout.addWidget(label)
        self.setLayout(layout)

from PySide6.QtWidgets import QVBoxLayout

class LayoutManager:
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.layout = QVBoxLayout(self.parent_widget)

    def setup_layout(self, *widgets):
        for widget in widgets:
            self.layout.addWidget(widget)

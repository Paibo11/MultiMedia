from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QComboBox, QLabel, QCheckBox, QSlider)
from PySide6.QtCore import Qt
from scene_widget import SceneWidget
from enums import DisplayMode, ShadingMode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Визуализация")
        self.setMinimumSize(800, 600)
        
        # Создаем центральный виджет и основной layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Создаем виджет сцены
        self.scene_widget = SceneWidget()
        main_layout.addWidget(self.scene_widget, stretch=1)
        
        # Создаем панель управления
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(control_panel)
        
        # Режим отображения
        display_label = QLabel("Режим отображения:")
        control_layout.addWidget(display_label)
        
        display_combo = QComboBox()
        for mode in DisplayMode:
            display_combo.addItem(mode.value)
        display_combo.currentTextChanged.connect(self.on_display_mode_changed)
        control_layout.addWidget(display_combo)
        
        # Режим затенения
        shading_label = QLabel("Режим затенения:")
        control_layout.addWidget(shading_label)
        
        # shading_combo = QComboBox()
        # for mode in ShadingMode:
        #     shading_combo.addItem(mode.value)
        # shading_combo.currentTextChanged.connect(self.on_shading_mode_changed)
        # control_layout.addWidget(shading_combo)
        
        # Зеркальное отображение
        mirror_label = QLabel("Зеркальное отображение:")
        control_layout.addWidget(mirror_label)
        
        mirror_x = QCheckBox("По X")
        mirror_x.stateChanged.connect(lambda: self.scene_widget.set_mirror(0))
        control_layout.addWidget(mirror_x)
        
        mirror_y = QCheckBox("По Y")
        mirror_y.stateChanged.connect(lambda: self.scene_widget.set_mirror(1))
        control_layout.addWidget(mirror_y)
        
        mirror_z = QCheckBox("По Z")
        mirror_z.stateChanged.connect(lambda: self.scene_widget.set_mirror(2))
        control_layout.addWidget(mirror_z)

        # # Направление света
        # light_label = QLabel("Направление света:")
        # control_layout.addWidget(light_label)
        #
        # light_x = QSlider(Qt.Horizontal)
        # light_x.setMinimum(-100)
        # light_x.setMaximum(100)
        # light_x.setValue(50)
        # light_x.valueChanged.connect(lambda: self.update_light_direction())
        # control_layout.addWidget(QLabel("X:"))
        # control_layout.addWidget(light_x)
        #
        # light_y = QSlider(Qt.Horizontal)
        # light_y.setMinimum(-100)
        # light_y.setMaximum(100)
        # light_y.setValue(50)
        # light_y.valueChanged.connect(lambda: self.update_light_direction())
        # control_layout.addWidget(QLabel("Y:"))
        # control_layout.addWidget(light_y)
        #
        # light_z = QSlider(Qt.Horizontal)
        # light_z.setMinimum(-100)
        # light_z.setMaximum(100)
        # light_z.setValue(-100)
        # light_z.valueChanged.connect(lambda: self.update_light_direction())
        # control_layout.addWidget(QLabel("Z:"))
        # control_layout.addWidget(light_z)
        #
        # # Сохраняем слайдеры для обновления направления света
        # self.light_sliders = [light_x, light_y, light_z]
        #
        # # Добавляем растягивающийся элемент в конец
        # control_layout.addStretch()
        #
        # # Устанавливаем начальные значения
        # self.update_light_direction()
        
    def on_display_mode_changed(self, text):
        for mode in DisplayMode:
            if mode.value == text:
                self.scene_widget.set_display_mode(mode)
                break
                
    def on_shading_mode_changed(self, text):
        for mode in ShadingMode:
            if mode.value == text:
                self.scene_widget.set_shading_mode(mode)
                break

    # def update_light_direction(self):
    #     x = self.light_sliders[0].value() / 100.0
    #     y = self.light_sliders[1].value() / 100.0
    #     z = self.light_sliders[2].value() / 100.0
    #     self.scene_widget.set_light_direction(x, y, z)
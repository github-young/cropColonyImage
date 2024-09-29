# License: MIT
# Author: XY

import os
import sys

from PIL import Image, ImageDraw
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QProgressBar, \
    QHBoxLayout, QSpinBox, QStyle, QLineEdit


class ImageProcessor(QThread):
    progress_update = Signal(int)
    processing_finished = Signal()

    def __init__(self, input_folder, output_folder, crop_box, crop_radius):
        super().__init__()

        self.input_folder = input_folder
        self.output_folder = output_folder
        self.crop_box = crop_box
        self.crop_radius = crop_radius

    def run(self):
        total_images = len(
            [filename for filename in os.listdir(self.input_folder) if filename.lower().endswith(('.jpg', '.jpeg'))])
        processed_images = 0

        for filename in os.listdir(self.input_folder):
            if filename.lower().endswith(('.jpg', '.jpeg')):
                input_image_path = os.path.join(self.input_folder, filename)
                image = Image.open(input_image_path)

                cropped_image = image.crop(self.crop_box)

                mask = Image.new('L', cropped_image.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, self.crop_radius, self.crop_radius), fill=255)

                circular_image = Image.new('RGBA', cropped_image.size)
                circular_image.paste(cropped_image, (0, 0), mask)

                new_size = (1000, 1000)  # Output image size: px
                output_image_path = os.path.join(self.output_folder, f"{os.path.splitext(filename)[0]}_circular.png")
                circular_image = circular_image.resize(new_size)
                circular_image.save(output_image_path, 'PNG', optimized=True)

                processed_images += 1
                progress = int((processed_images / total_images) * 100)
                self.progress_update.emit(progress)

        self.processing_finished.emit()


class ImageCropperApp(QWidget):
    def __init__(self):
        super().__init__()

        icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        self.setWindowIcon(icon)

        self.setWindowTitle("Colony Image Cropper")
        self.resize(300, 360)
        layout = QVBoxLayout()

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hboxr = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()

        self.main_label = QLabel("Cropped area (px):")
        self.main_label.setStyleSheet(
            """QLabel{ font-weight: bold; }"""
        )
        layout.addWidget(self.main_label)

        spinBox_width = 100
        spinBox_max = 10000

        self.crop_box_left_label = QLabel("Left:")
        self.crop_box_left = QSpinBox()
        self.crop_box_left.setMaximum(spinBox_max)
        self.crop_box_left.setValue(0)
        self.crop_box_left.valueChanged.connect(self.update_crop_box)
        self.crop_box_left.setFixedWidth(spinBox_width)
        hbox1.addWidget(self.crop_box_left_label)
        hbox1.addWidget(self.crop_box_left)

        self.crop_box_upper_label = QLabel("Upper:")
        self.crop_box_upper = QSpinBox()
        self.crop_box_upper.setMaximum(spinBox_max)
        self.crop_box_upper.setValue(200)
        self.crop_box_upper.valueChanged.connect(self.update_crop_box)
        self.crop_box_upper.setFixedWidth(spinBox_width)
        hbox2.addWidget(self.crop_box_upper_label)
        hbox2.addWidget(self.crop_box_upper)

        self.crop_box_radius_label = QLabel("Radius:")
        self.crop_box_radius = QSpinBox()
        self.crop_box_radius.setMaximum(spinBox_max)
        self.crop_box_radius.setValue(2800)
        self.crop_box_radius.setFixedWidth(spinBox_width)
        self.crop_box_radius.valueChanged.connect(self.update_crop_box)
        hboxr.addWidget(self.crop_box_radius_label)
        hboxr.addWidget(self.crop_box_radius)

        self.crop_box_right_label = QLabel("Right:")
        self.crop_box_right = QLineEdit()
        self.crop_box_right.setText("2800")
        self.crop_box_right.setFixedWidth(spinBox_width)
        self.crop_box_right.setReadOnly(True)
        self.crop_box_right.setStyleSheet(
            """QLineEdit { color: gray }""")
        hbox3.addWidget(self.crop_box_right_label)
        hbox3.addWidget(self.crop_box_right)

        self.crop_box_lower_label = QLabel("Lower:")
        self.crop_box_lower = QLineEdit()
        self.crop_box_lower.setText("3000")
        self.crop_box_lower.setFixedWidth(spinBox_width)
        self.crop_box_lower.setReadOnly(True)
        self.crop_box_lower.setStyleSheet(
            """QLineEdit { color: gray }""")
        hbox4.addWidget(self.crop_box_lower_label)
        hbox4.addWidget(self.crop_box_lower)

        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addLayout(hboxr)
        layout.addLayout(hbox3)
        layout.addLayout(hbox4)

        self.input_folder_label = QLabel("Input Folder:")
        layout.addWidget(self.input_folder_label)

        self.output_folder_label = QLabel("Output Folder:")
        layout.addWidget(self.output_folder_label)

        self.select_input_button = QPushButton("Select Input Folder")
        self.select_input_button.clicked.connect(self.select_input_folder)
        layout.addWidget(self.select_input_button)

        self.select_output_button = QPushButton("Select Output Folder")
        self.select_output_button.clicked.connect(self.select_output_folder)
        layout.addWidget(self.select_output_button)

        self.crop_button = QPushButton("Crop Images")
        self.crop_button.clicked.connect(self.crop_images)
        layout.addWidget(self.crop_button)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        self.progress_bar.setValue(0)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

        self.show()

    def update_crop_box(self):
        crop_radius = self.crop_box_radius.value()
        crop_box_left = self.crop_box_left.value()
        crop_box_upper = self.crop_box_upper.value()
        crop_box_right = crop_box_left + crop_radius
        crop_box_lower = crop_box_upper + crop_radius

        self.crop_box_right.setText(str(crop_box_right))
        self.crop_box_lower.setText(str(crop_box_lower))

        return (crop_box_left, crop_box_upper, crop_box_right, crop_box_lower), crop_radius

    def select_input_folder(self):
        input_folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        self.input_folder_label.setText(f"Input Folder: {input_folder}")

    def select_output_folder(self):
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        self.output_folder_label.setText(f"Output Folder: {output_folder}")

    def crop_images(self):
        input_folder = self.input_folder_label.text().split(": ")[1]
        output_folder = self.output_folder_label.text().split(": ")[1]

        crop_box, crop_radius = self.update_crop_box()

        self.image_processor = ImageProcessor(input_folder, output_folder, crop_box, crop_radius)
        self.image_processor.progress_update.connect(self.update_progress)
        self.image_processor.processing_finished.connect(self.processing_finished)
        self.image_processor.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def processing_finished(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageCropperApp()
    sys.exit(app.exec())

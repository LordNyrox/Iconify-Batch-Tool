# FILE: iconify_batch.py

import sys
import os
import ctypes
from PIL import Image, ImageOps, ImageFilter

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QTableWidgetSelectionRange
)
from PyQt6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, QSize, QUrl

from Iconify_PyQtv3 import ImageEditorDialog, apply_icon_to_folder, create_icon_storage_directory

class BatchIconify(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iconify Batch Mode")
        self.setFixedSize(800, 500)
        self.setAcceptDrops(True)

        self.image_paths = []
        self.folder_paths = []
        self.template_path = None
        self.image_states = {}

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Image", "Image Name", "Folder", "Edited"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        top_layout = QHBoxLayout()
        self.template_label = QLineEdit("No template selected")
        self.template_label.setReadOnly(True)
        btn_template = QPushButton("Select Template")
        btn_template.clicked.connect(self.select_template)
        top_layout.addWidget(self.template_label)
        top_layout.addWidget(btn_template)
        layout.addLayout(top_layout)

        btn_row1 = QHBoxLayout()
        btn_add_images = QPushButton("Add Images")
        btn_add_images.clicked.connect(self.select_images)
        btn_clear_images = QPushButton("Clear Images")
        btn_clear_images.clicked.connect(self.clear_images)
        btn_row1.addWidget(btn_add_images)
        btn_row1.addWidget(btn_clear_images)
        layout.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        btn_add_folders = QPushButton("Add Folders")
        btn_add_folders.clicked.connect(self.select_folders)
        btn_clear_folders = QPushButton("Clear Folders")
        btn_clear_folders.clicked.connect(self.clear_folders)
        btn_row2.addWidget(btn_add_folders)
        btn_row2.addWidget(btn_clear_folders)
        layout.addLayout(btn_row2)

        self.shadow_checkbox = QCheckBox("Add 3D Shadow")
        self.shadow_checkbox.setChecked(True)
        layout.addWidget(self.shadow_checkbox)

        btn_edit = QPushButton("Edit All")
        btn_edit.clicked.connect(self.edit_all)
        layout.addWidget(btn_edit)

        btn_process = QPushButton("Generate and Apply Icons")
        btn_process.clicked.connect(self.batch_process)
        layout.addWidget(btn_process)

    def refresh_table(self):
        self.table.setRowCount(0)
        for i, img_path in enumerate(self.image_paths):
            folder = self.folder_paths[i] if i < len(self.folder_paths) else "[Not Set]"
            edited = "✔" if img_path in self.image_states else "✘"
            row = self.table.rowCount()
            self.table.insertRow(row)

            thumb = QPixmap(img_path).scaled(QSize(40, 40), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            item_thumb = QTableWidgetItem()
            item_thumb.setIcon(QIcon(thumb))
            self.table.setItem(row, 0, item_thumb)
            self.table.setItem(row, 1, QTableWidgetItem(os.path.basename(img_path)))
            self.table.setItem(row, 2, QTableWidgetItem(folder))
            self.table.setItem(row, 3, QTableWidgetItem(edited))

    def select_template(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Template", "", "Image Files (*.png)")
        if path:
            self.template_path = path
            self.template_label.setText(os.path.basename(path))

    def select_images(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg)")
        if paths:
            self.image_paths.extend(paths)
            self.refresh_table()

    def select_folders(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.folder_paths.append(path)
            self.refresh_table()

    def clear_images(self):
        self.image_paths.clear()
        self.image_states.clear()
        self.refresh_table()

    def clear_folders(self):
        self.folder_paths.clear()
        self.refresh_table()

    def edit_all(self):
        if not self.template_path:
            QMessageBox.warning(self, "Missing Template", "Select a template before editing.")
            return
        for img_path in self.image_paths:
            editor = ImageEditorDialog(img_path, self.template_path, self)
            if editor.exec():
                self.image_states[img_path] = editor.get_image_state()
        self.refresh_table()

    def batch_process(self):
        if not self.template_path or not self.image_states:
            QMessageBox.warning(self, "Incomplete", "Edit all images first and select template.")
            return

        success, storage_dir = create_icon_storage_directory()
        if not success:
            QMessageBox.critical(self, "Error", storage_dir)
            return

        for i, img_path in enumerate(self.image_paths):
            if i >= len(self.folder_paths):
                QMessageBox.warning(self, "Missing Folder", f"No folder set for image: {img_path}")
                continue

            try:
                pos, scale = self.image_states[img_path]
                template_pil = Image.open(self.template_path).convert("RGBA")
                user_img = Image.open(img_path).convert("RGBA")

                bg_img = ImageOps.fit(user_img, template_pil.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(15))
                template_mask = template_pil.getchannel('A')
                bg_img.putalpha(template_mask)

                scaled_width = int(template_pil.width * (user_img.width / user_img.height) / (template_pil.width / template_pil.height))
                scaled_height = template_pil.height
                if scaled_width < template_pil.width:
                    scaled_width = template_pil.width
                    scaled_height = int(template_pil.height * (user_img.height / user_img.width) * (template_pil.width / template_pil.width))

                fg_img = user_img.resize((scaled_width, scaled_height), Image.LANCZOS)
                final_size = (int(fg_img.width * scale), int(fg_img.height * scale))
                fg_img = fg_img.resize(final_size, Image.LANCZOS)

                fg_canvas = Image.new("RGBA", template_pil.size, (0, 0, 0, 0))
                paste_x, paste_y = int(pos.x()), int(pos.y())
                fg_canvas.paste(fg_img, (paste_x, paste_y), fg_img)

                final_image = Image.alpha_composite(bg_img, fg_canvas)
                final_image.putalpha(template_mask)
                final_image = Image.composite(final_image, Image.new("RGBA", final_image.size, (0, 0, 0, 0)), template_mask)

                if self.shadow_checkbox.isChecked():
                    shadow_offset = (8, 8)
                    shadow_layer = Image.new("RGBA", final_image.size, (0, 0, 0, 255))
                    shadow_layer.putalpha(template_mask)
                    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(5))
                    shadow_canvas = Image.new("RGBA", (final_image.width + shadow_offset[0], final_image.height + shadow_offset[1]), (0, 0, 0, 0))
                    shadow_canvas.paste(shadow_layer, shadow_offset, shadow_layer)
                    shadow_canvas.paste(final_image, (0, 0), final_image)
                    final_image = shadow_canvas

                base_name = os.path.splitext(os.path.basename(img_path))[0]
                ico_path = os.path.join(storage_dir, f"icon_{base_name}.ico")
                final_image.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

                folder = self.folder_paths[i]
                ok, msg = apply_icon_to_folder(folder, ico_path)
                if not ok:
                    QMessageBox.warning(self, "Failed", msg)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed processing {img_path}: {e}")
                continue

        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x1000, None, None)
        QMessageBox.information(self, "Done", "Batch iconify complete.")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.folder_paths.append(path)
            elif os.path.isfile(path) and path.lower().endswith((".png", ".jpg", ".jpeg")):
                self.image_paths.append(path)
        self.refresh_table()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = BatchIconify()
    win.show()
    sys.exit(app.exec())

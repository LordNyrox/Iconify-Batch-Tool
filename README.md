# Iconify-Batch-Tool

Iconify is a simple yet powerful desktop application for Windows that allows you to create custom folder icons from your images in batches. It provides an intuitive graphical user interface to apply a template, adjust your images, and generate .ico files that are automatically applied to your selected folders.
<img width="802" height="532" alt="image" src="https://github.com/user-attachments/assets/f0f94067-d6a6-4563-bc0f-6072efccf0b1" />

===================================================================================================================================================================================================

## Features

  * **Batch Processing**: Apply icons to multiple folders at once.
  * **Template-Based Design**: Use a PNG template to maintain a consistent style for all your icons.
  * **Image Editor**: A simple editor to position and scale each image within the template.
  * **3D Shadow Effect**: Automatically add a subtle shadow to your icons for a more professional look.
  * **Drag and Drop**: Easily add images and folders by dragging them into the application window.
  * **Safe Storage**: Generated `.ico` files are stored in a hidden `.icon_storage` directory in your user profile.

## How to Use

1.  **Prerequisites**: You need Python and PyQt6 installed. You can install the necessary libraries with pip:
    ```bash
    pip install PyQt6 Pillow
    ```
2.  **Run the application**:
    ```bash
    python Iconify_PyQtv6.py
    ```
3.  **Select a Template**: Click "Select Template" to choose a `.png` file that will serve as the frame or shape for your icons.
4.  **Add Images and Folders**:
      * Click "Add Images" to select the images you want to turn into icons.
      * Click "Add Folders" to select the folders you want the icons applied to.
      * *Alternatively, you can drag and drop images and folders into the window.*
5.  **Edit Images**: Click "Edit All" to open the editor for each image. Adjust the position and scale of each image within the template.
6.  **Generate**: Once you've edited all images, click "Generate and Apply Icons" to create the icons and apply them to the corresponding folders.

## Dependencies

  * Python 3.x
  * PyQt6
  * Pillow

-----

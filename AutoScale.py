from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import os, sys

# A program that sets scales on many images at once.
# Priority was to be as easy to use as possible for a specific microscope, so other cameras can require a bit of tweaking.

# Constants
ZOOM_10X = 2.604169
ZOOM_50X = 12.84722
ZOOM_100X = 25.5002

# List of image filenames
Valid_Filenames = [".jpeg", ".jpg", ".jfif", ".png", ".bmp", ".tif", ".tiff", ".gif"]

# Adds a scale to an image
def add_scale(input_image, pixel_per_unit = ZOOM_10X, bar_width_unit = 30, unit = "um", color = "white"):
    # Load image as drawable
    drawing = ImageDraw.Draw(input_image)
    
    # String to print
    if unit == "um":
        unit = "µm"
        
    scale_string = str(int(bar_width_unit)) + " " + str(unit)
    
    
    # Calculate location and size of scale bar
    bar_width = bar_width_unit * pixel_per_unit
    
    image_bbox = input_image.getbbox()
    
    scale_rect_end = (image_bbox[2] * 0.95, image_bbox[3] * 0.96)
    scale_rect_start = ((image_bbox[2] * 0.95) - bar_width, image_bbox[3] * 0.95)
    
    text_size = drawing.textsize(scale_string)[0]
    scale_text_position = ((image_bbox[2] * 0.95) - (bar_width / 2) - (text_size*2), image_bbox[3] * 0.92)
    
    # Add scale: text and bar
    font = ImageFont.truetype("C:\Windows\Fonts\\arial.ttf",int(40*image_bbox[2]/2096))
    drawing.text(scale_text_position, scale_string, font=font,fill=color)
    drawing.rectangle((scale_rect_start,scale_rect_end), fill=color) 
        
    return input_image

# Full image processing: open image, add scale, save image
def process_image(filename, input_dir, output_dir, extra_string = "_with_scale", pixel_per_unit = ZOOM_10X, bar_width_unit = 50, 
                    unit = "um", color = "white", lowercase = True):
                    
    # Get filename extension    
    filename_no_extension, filename_extension = os.path.splitext(filename)

    # Get the new path for the file if the output directory is not the same as the input
    if input_dir == output_dir:
        filename_new_path = filename_no_extension
    else:
        filename_new_path = filename_no_extension.replace(input_dir,output_dir)
        
    # Create directory if it doesn't exist
    directory = os.path.dirname(filename_new_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    if filename_extension.lower() not in Valid_Filenames:
        print("File " + filename + "is not an image file. Skipping...")
        return 1


    # If the image already has a scale, skip
    if extra_string in filename:
        print("File " + filename + " already has scale. Skipping...")
        return 1
        
    image = Image.open(filename)
    add_scale(image, pixel_per_unit,bar_width_unit,unit,color)
    
    if lowercase:
        filename_new_path = filename_new_path.lower()
    
    # Get new filename by taking the old one and adding the new string
    new_filename = filename_new_path + extra_string + filename_extension

    image.save(new_filename)
    
    return 1
    
    
class FileList:
    def __init__(self):
        self.files = []
        self.cwd = os.getcwd()
        self.output_dir = os.getcwd()
        self.subdirectories = False
        self.lowercase = False
        
    # Import a file
    def new_file(self,filename):
        newfile = {}
        newfile["filename"] = filename
        
        # Check if the filename can give a hint as to what the zoom level is
        if "100x" in filename or "x100" in filename:
            newfile["zoom"] = "100x"
            newfile["pixel_per_unit"] = ZOOM_100X
        elif "50x" in filename or "x50" in filename:
            newfile["zoom"] = "50x"
            newfile["pixel_per_unit"] = ZOOM_50X
        else: # Default case is equal to the 10x case
            newfile["zoom"] = "10x"
            newfile["pixel_per_unit"] = ZOOM_10X
            
        newfile["bar_width_unit"] = 50
        newfile["do"] = True
        newfile["unit"] = "um"
        newfile["color"] = "white"
        
        self.files.append(newfile)
    
    
    def get_all_images_in_folder(self,folder_path = None, run_subdirectories = None):
        self.files = []
        if folder_path is None:
            folder_path = self.cwd
        if run_subdirectories is None:
            run_subdirectories = self.subdirectories
            
        for r,d,f in os.walk(folder_path):
            for file in f:
                if '.tiff' in file or '.tif' in file or '.png' in file or '.jpg' in file or '.jpeg' in file:
                    self.new_file(os.path.join(r,file))
            
            if not run_subdirectories:
                break # Do not run in subdirectories
            
            # Else, run subdirectories
        
        return self.files
    
    def process_all_images(self):
        number_files = 0
        for file in self.files:
            if file["do"]:
                number_files = number_files + process_image(file["filename"], self.cwd, self.output_dir, pixel_per_unit = file["pixel_per_unit"],
                bar_width_unit = file["bar_width_unit"], unit=file["unit"], color = file["color"], lowercase = self.lowercase)
        return number_files
    
    def set_cwd(self, path):
        self.cwd = path
    
    def get_cwd(self):
        return self.cwd
        
    def set_output_dir(self, path):
        self.output_dir = path
        
    def get_output_dir(self):
        return self.output_dir
        
    def print_files(self):
        print(self.files)

    def set_subdirectories(self, set):
        self.subdirectories = set
    
    def do_subdirectories(self):
        self.subdirectories = True
    def skip_subdirectories(self):
        self.subdirectories = False
    def get_do_subdirectories(self):
        return self.subdirectories
    def set_lowercase(self, value):
        self.lowercase = value

# Visual frames for file selection. Contain file location info
class FileSelector(QWidget):
    def __init__(self,parent, fileList, is_output = False, other_selector = None):
        super().__init__()
        self.parent = parent
        self.is_output = is_output
        self.fileList = fileList
        self.other_selector = other_selector
        if is_output:
            self.labeltext = "Output folder: "
        else:
            self.labeltext = "Input folder: "
            
        self.fileText = os.getcwd()

        layout = QGridLayout(self)
        self.label = QLabel(self.labeltext)
        layout.addWidget(self.label,0,0)
        self.textBox = QLineEdit(self.fileText)
        layout.addWidget(self.textBox,0,1)
        self.button = QPushButton("Browse...",self)
        self.button.clicked.connect(self.on_click)
        layout.addWidget(self.button,0,2)
        if not is_output:
            self.run_subdirectories = QCheckBox("Also edit files in subfolders", self)
            self.run_subdirectories.clicked.connect(self.on_checkbox_click)
            layout.addWidget(self.run_subdirectories,1,1)
        else:
            self.isLowercase = QCheckBox("Turn all files into lowercase", self)
            self.isLowercase.clicked.connect(self.on_checkbox_click)
            layout.addWidget(self.isLowercase,1,1)

        
        
    def on_click(self):
        self.fileText = str(QFileDialog.getExistingDirectory(self, "Select folder",fileList.get_cwd()))
        self.textBox.setText(self.fileText)
        if not self.is_output:
            self.fileList.set_cwd(self.fileText)
            self.parent.refresh_file_list()
            self.other_selector.fileText = self.fileText
            self.other_selector.textBox.setText(self.fileText)
        else:
            self.fileList.set_output_dir(self.fileText)
    
    def on_checkbox_click(self):
        if not self.is_output:
            self.fileList.set_subdirectories(self.run_subdirectories.isChecked())
            self.parent.refresh_file_list()
        else:
            self.fileList.set_lowercase(self.isLowercase.isChecked())
        
    def set_other_selector(self,other_selector):
        self.other_selector = other_selector
    
    def get_file_path(self):
        self.fileText = self.textBox.text()
        return self.fileText
        
    
# Control buttons
class ControlsPane(QWidget):
    def __init__(self, parent, file_list_reference):
        super().__init__()
        self.parent = parent
        self.file_list_reference = file_list_reference
        layout = QVBoxLayout(self)
        self.refresh_button = QPushButton("Refresh",self)
        self.refresh_button.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_button)
        
        self.add_button = QPushButton("Add Scales", self)
        self.add_button.clicked.connect(self.do)
        layout.addWidget(self.add_button)
        
    # Get all files
    def refresh(self):
        self.parent.refresh_file_list()

    # Apply transformation
    def do(self):
        self.file_list_reference.set_cwd(self.input_selector.get_file_path())
        self.file_list_reference.set_output_dir(self.output_selector.get_file_path())
        number_of_files = self.file_list_reference.process_all_images()
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Information)
        if number_of_files == 1:
            dialog.setText("1 image processed.")
        else:
            dialog.setText(str(number_of_files) + " images processed.")
            
        dialog.setWindowTitle("Complete")
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()
        

class ImageListTable(QWidget):
    def __init__(self, parent, file_list_reference):
        super().__init__()
        self.parent = parent
        self.fileList = file_list_reference
        
        layout = QGridLayout(self)
        self.table = QTableWidget()
        self.rows = -1
        self.table.setRowCount(0)
        self.table.setColumnCount(7)
        
        self.table.setHorizontalHeaderLabels(["do","File","Zoom","Pixel per unit", "Bar size (Unit)", "Unit"])
        
        layout.addWidget(self.table,0,0,3,4)
        
        # Buttons for selection
        self.selectAll = QPushButton("Select All")
        self.selectAll.clicked.connect(self.select_all)
        layout.addWidget(self.selectAll,3,2)
        
        self.selectNone = QPushButton("Select None")
        self.selectNone.clicked.connect(self.select_none)
        layout.addWidget(self.selectNone,3,3)
        
        self.copySettings = QPushButton("Copy settings to other files")
        self.copySettings.clicked.connect(self.copy_settings)
        layout.addWidget(self.copySettings,3,1)
        
        self.table.resizeColumnsToContents()
        
    def add_file(self,file):
        self.rows = self.rows + 1
        currentRow = self.rows
        self.table.setRowCount(self.rows + 1)
        
        image_name = file["filename"].split('\\')[-1]
        
        checkbox = QTableWidgetItem(True)
        checkbox.setFlags((checkbox.flags() | Qt.ItemIsUserCheckable) & ~(Qt.ItemIsEditable))
        checkbox.setCheckState(Qt.Checked if file["do"] else Qt.Unchecked)
        self.table.setItem(self.rows,0, checkbox)
        imagenameitem = QTableWidgetItem(image_name)
        imagenameitem.setFlags(imagenameitem.flags() & ~(Qt.ItemIsEditable))
        self.table.setItem(self.rows,1, imagenameitem)
        zoom_options = ['10x','50x','100x','Custom']
        
        zoomitem = QComboBox()
        zoomitem.addItems(zoom_options)
        if file["zoom"] == '10x':
            zoomitem.setCurrentIndex(0)
        elif file["zoom"] == '50x':
            zoomitem.setCurrentIndex(1)
        elif file["zoom"] == '100x':
            zoomitem.setCurrentIndex(2)
        

        # Connect signal to check when the zoom is changed, as it requires a different method call.
        # We need to explicitly specify which file it is and that it is the zoom that is being changed.
        # That is why we use the lambda expression.
        zoomitem.currentIndexChanged.connect(lambda: self.update_file_of_selected_row(currentRow,2))

        self.table.setCellWidget(self.rows,2, zoomitem)
        self.table.setItem(self.rows,3, QTableWidgetItem(str(file["pixel_per_unit"])))
        self.remove_flag(self.rows,3,Qt.ItemIsEditable)
        self.table.setItem(self.rows,4, QTableWidgetItem(str(file["bar_width_unit"])))
        self.table.setItem(self.rows,5, QTableWidgetItem(str(file["unit"])))
        self.table.setItem(self.rows,6, QTableWidgetItem(str(file["color"])))
        
        # Connect signal to check when table was changed
        self.table.cellChanged.connect(self.update_file_of_selected_row)
                
    def add_all_files(self):
        self.clear_table()
        for file in self.fileList.files:
            self.add_file(file)
        
        self.table.resizeColumnsToContents()
        
    def clear_table(self):
        self.table.clear()
        self.table.setHorizontalHeaderLabels(["do","File","Zoom","Pixel per unit", "Bar size (Unit)", "Unit","Color"])
        self.rows = -1
        self.table.setRowCount(0)
        
    def get_value(self, row, col):
        item = self.table.item(row,col).text()
        
        return item
        
    def is_selected(self,row,col):
        item = self.table.item(row,col).checkState()
        return item == Qt.Checked
    
    def set_selected(self,row,col,state):
        widget = self.table.item(row,col)
        widget.setCheckState(Qt.Checked if state else ~(Qt.Checked))
    
    def get_selection(self, row, col):
        widget = self.table.cellWidget(row,col)
        return str(widget.currentText())
    
    def set_selection_by_text(self,row,col,text):
        widget = self.table.cellWidget(row,col)
        if text == "10x":
            widget.setCurrentIndex(0)
        elif text == "50x":
            widget.setCurrentIndex(1)
        elif text == "100x":
            widget.setCurrentIndex(2)
        else:
            widget.setCurrentIndex(3)
        
    def remove_flag(self,row,col,flag):
        widget = self.table.item(row,col)
        widget.setFlags(widget.flags() & ~flag)
    
    def add_flag(self,row,col,flag):
        widget = self.table.item(row,col)
        widget.setFlags(widget.flags() | flag)
        
    def change_text(self,row,col,text):
        widget = self.table.item(row,col)
        widget.setText(str(text))
        
    # Set all files to "do"
    def select_all(self):
        for row in range(0, self.rows+1):
            self.set_selected(row,0,True)
            self.fileList.files[row]["do"] = True
    
    # Set all files to "don't do"
    def select_none(self):
        for row in range(0, self.rows+1):
            self.set_selected(row,0,False)
            self.fileList.files[row]["do"] = False
            
        
    # Change settings to they are similar between files
    def copy_settings(self):
        # Get selected row
        selected_row = self.table.currentRow()
        
        # Save parameters
        zoom = self.fileList.files[selected_row]["zoom"]
        pixel_per_unit = self.fileList.files[selected_row]["pixel_per_unit"]
        bar_width_unit = self.fileList.files[selected_row]["bar_width_unit"]
        unit = self.fileList.files[selected_row]["unit"]
        color = self.fileList.files[selected_row]["color"]

        # Put parameters in other files and change values in table
        for row in range(0,self.rows+1):
            self.fileList.files[row]["zoom"] = zoom
            self.fileList.files[selected_row]["pixel_per_unit"] = pixel_per_unit
            self.fileList.files[selected_row]["bar_width_unit"] = bar_width_unit
            self.fileList.files[selected_row]["unit"] = unit
            self.fileList.files[selected_row]["color"] = color
            
            self.change_text(row,3,str(pixel_per_unit))
            self.change_text(row,4,str(bar_width_unit))
            self.change_text(row,5,str(unit))
            self.set_selection_by_text(row,2,str(zoom))
            self.change_text(row,6,str(color))

    # Update file information when an item is changed
    def update_file_of_selected_row(self, row, col):
        selectedFile = self.fileList.files[row]
        if col == 0:
            # do or do not
            self.fileList.files[row]["do"] = self.is_selected(row,col)
            
        elif col == 2:
            # 1 will never be chosen because it is the file name (non-editable)
            # 2 is the zoom level
            text = self.get_selection(row,col)
            self.fileList.files[row]["zoom"] = text
            if text == "10x":
                self.fileList.files[row]["pixel_per_unit"] = ZOOM_10X
                self.change_text(row,3,ZOOM_10X)
                self.remove_flag(row,3,(Qt.ItemIsEditable))
            elif text == "50x":
                self.fileList.files[row]["pixel_per_unit"] = ZOOM_50X
                self.change_text(row,3,ZOOM_50X)
                self.remove_flag(row,3,(Qt.ItemIsEditable))
            elif text == "100x":
                self.fileList.files[row]["pixel_per_unit"] = ZOOM_100X
                self.change_text(row,3,ZOOM_100X)
                self.remove_flag(row,3,(Qt.ItemIsEditable))
            
            else:
                self.add_flag(row,3,Qt.ItemIsEditable)
        
        elif col == 3:
            # Pixel per unit
            self.fileList.files[row]["pixel_per_unit"] = float(self.get_value(row,col))
            
        elif col == 4:
            # Bar width in units (um or something)
            self.fileList.files[row]["bar_width_unit"] = float(self.get_value(row,col))
        
        elif col == 5:
            # Unit name
            self.fileList.files[row]["unit"] = str(self.get_value(row,col))
                    
        elif col == 6:
            # Color
            self.fileList.files[row]["color"] = str(self.get_value(row,col))
            

class App(QMainWindow):
    def __init__(self,fileList):
        super().__init__()
        self.title = 'Micro Auto Scale'
        self.setWindowTitle(self.title)
        self.width = 680
        self.height = 50
        self.fileList = fileList
        self.resize(self.width,self.height)
        self._main = QWidget()
        self.setCentralWidget(self._main)
        
        layout = QGridLayout(self._main)
        
        # File selection menus
        self.inFileFrame  = FileSelector(self,fileList,is_output=False)
        self.outFileFrame = FileSelector(self,fileList,is_output=True,other_selector=self.inFileFrame)
        self.inFileFrame.set_other_selector(self.outFileFrame)
        
        layout.addWidget(self.inFileFrame,0,0,1,5)
        layout.addWidget(self.outFileFrame,1,0,1,5)
        
        # Controls pane
        self.controls = ControlsPane(self,fileList)
        self.controls.input_selector = self.inFileFrame
        self.controls.output_selector = self.outFileFrame
        layout.addWidget(self.controls,5,4)
        
        # Table
        self.table = ImageListTable(self,fileList)
        self.table.height = 500
        layout.addWidget(self.table,3,0,50,4)
        
        self.refresh_file_list()
        
        self.show()
    
    def refresh_file_list(self):
        self.fileList.set_cwd(self.inFileFrame.get_file_path())
        self.fileList.get_all_images_in_folder()
        self.table.add_all_files()

if __name__ == '__main__':
    fileList = FileList()
    if len(sys.argv) > 1:
        for image_filename in sys.argv[1:]:
            try:
                process_image(image_filename)
            except:
                print("Could not open " + image_filename)
    
            
    app = QApplication(sys.argv)
    ex = App(fileList)
    sys.exit(app.exec_())
"""

    Segmentation on DICOM medical files for regions of interest (ROI).

    Goal is to:
     - upload DICOM file.
     - apply filters, threshold or other technique to find lung aorta
     - pack everything into classes and methods
     - create user interface (GUI application)

    Language: Python
    Framework: PyCharm Community Edition
    Created by: Vukasin Vasiljevic, 2019

"""



# Required modules

import matplotlib.pylab as plt
import numpy as np
import pydicom
from skimage.filters import sobel
from skimage import morphology
import cv2
import sys
from PyQt5.QtWidgets import QMessageBox ,QApplication,QWidget,QCheckBox, QVBoxLayout, QPushButton, QFileDialog , QLabel, QTextEdit
from PyQt5.QtGui import QPixmap



# Segmentet Image class that consists of methods for filtering image
class SegmentedImage:


    # Loaded image save and display
    def displaySave(ds):
        pixel = ds.pixel_array
        fig = plt.figure()
        img = plt.imshow(pixel, cmap='bone')
        fig.savefig('dicom.jpg')
        #plt.show()

    # Show given threshold
    def thresholdDisplay(ds):
        fig, axes = plt.subplots(1, 2, figsize=(6, 4), sharey=True)
        axes[0].imshow(ds.pixel_array > 1200, cmap=plt.cm.gray, interpolation='nearest')
        axes[0].set_title('Threshold > 1200')
        axes[1].imshow(ds.pixel_array > 1300, cmap=plt.cm.gray, interpolation='nearest')
        axes[1].set_title('Threshold > 1300')
        #plt.show()

    # Do segmentation over threshold image via sobel module
    # save segmented image as segmented.jpg
    def segmentation(ds):
        image = ds.pixel_array
        markers = np.zeros_like(ds.pixel_array)
        markers[image < 1200] = 1  # everything below 1200 is 1
        markers[image > 1350] = 2  # everything above 1350 is 2
        elevation_map = sobel(image)
        segmentation = morphology.watershed(elevation_map, markers)
        fig, ax = plt.subplots()
        ax.imshow(segmentation, cmap=plt.cm.gray, interpolation='nearest')
        ax.set_title('Segmentation Threshold')
        # Saving segmentation figure as a segmented.jpg
        fig.savefig('segmented.jpg')
        #segmentation = ndi.binary_fill_holes(segmentation - 1)
        #labeled_contour, _ = ndi.label(segmentation)
        #image_label_overlay = label2rgb(labeled_contour, image=image)

    # Method for overlaying circles over image if aorta is found
    def find(segImg, output):

        # Image must be converted to gray scale
        gray = cv2.cvtColor(segImg, cv2.COLOR_RGB2GRAY)
        gray = cv2.medianBlur(gray, 5)
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 3)

        # detect circles in the image with minimum radius of 5 pixels
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 41, param1=40, param2=30, minRadius=5, maxRadius=15)

        # ensure that there are circles in image
        if circles is not None:
            # convert the (x,y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")

            # loop over the (x.y) coordinates and radius of the circles
            for (x, y, r) in circles:
               # if x and y have specific position (in the middle of the image) then show circles
                if ((x>290 and x<390) and (y>200 and y<350)):

                    # draw the circle in the output image
                    cv2.circle(output, (x, y), r, (0, 255, 0), 2)
                    # show the output image
                    cv2.imshow("Found", output)
                    cv2.waitKey()

                else:
                    # show error message
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Nothing found")
                    msg.setInformativeText('Try with another image')
                    msg.setWindowTitle("Error")
                    msg.exec_()

        else:

            # show error message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Nothing found")
            msg.setInformativeText('Try with another image')
            msg.setWindowTitle("Error")
            msg.exec_()

# Circle Image class for applying edge detection filter over threshold image
class CircleImage:

    # edge detection function (also used in SegmentedImage class)
    def edgeDetection(segImg):
        gray = cv2.cvtColor(segImg, cv2.COLOR_RGB2GRAY)
        gray = cv2.medianBlur(gray, 5)
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 3)
        plt.imshow(gray)




"""     Appalication UI     """

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Finding aorta in dicom files'
        self.left = 600
        self.top = 300
        self.width = 600
        self.height = 330
        self.InitWindow()

    # Main window layout with check boxes and button for opening image
    def InitWindow(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        vbox = QVBoxLayout()

        self.b1 = QCheckBox("Show original image", self)
        self.b1.move(20, 220)
        self.b1.resize(320, 40)

        self.b2 = QCheckBox("Show threshold image", self)
        self.b2.move(190, 220)
        self.b2.resize(320, 40)

        self.b3 = QCheckBox("Show edge detection image", self)
        self.b3.move(370, 220)
        self.b3.resize(320, 40)

        self.btn1 = QPushButton("Open Image", self)
        self.btn1.resize(150, 32)
        self.btn1.move(230, 270)
        self.btn1.clicked.connect(self.initUI)

        # Create widget
        label = QLabel(self)
        pixmap = QPixmap('lungs.jpeg')
        label.setPixmap(pixmap)
        label.resize(580,190)
        label.move(10,10)

        #vbox.addWidget(self.btn1)  # self.btn1
        self.setLayout(vbox)
        self.show()

    # Initialize name dialog
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.openFileNameDialog()
        #self.show()

    # Open file name dialog for browsing for image
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                 "All Files (*);;Python Files (*.py)", options=options)


        if fileName:

            # Try reading file as a dicom type of file
            # if exception is raised, show error message and finish
            try:
                ds = pydicom.dcmread(fileName)
                image = SegmentedImage

                # Check box that is for specific part of filtering
                if self.b1.isChecked():
                    image.displaySave(ds)
                    plt.show()
                    image.segmentation(ds)
                if self.b2.isChecked():
                    image.thresholdDisplay(ds)
                    plt.show()
                    image.segmentation(ds)

                if self.b3.isChecked():
                    image.segmentation(ds)
                    output = cv2.imread('./dicom.jpg')
                    copyImage = output.copy()
                    segImg = cv2.imread('./segmented.jpg')
                    circle = CircleImage
                    # circle.houghCircles(segImg)
                    circle.edgeDetection(segImg)
                    plt.show()



                # Finding aorta is by default
                image.displaySave(ds)
                image.segmentation(ds)
                output = cv2.imread('./dicom.jpg')
                copyImage = output.copy()
                segImg = cv2.imread('./segmented.jpg')
                circle = SegmentedImage
                circle.find(segImg,output)


            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Invalid file type!!!")
                #msg.setInformativeText(e)
                msg.setWindowTitle("Error")
                msg.exec_()



# Start application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())





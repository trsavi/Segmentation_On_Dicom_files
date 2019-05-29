# Segmentation_On_Dicom_files
Working with DICOM files and segmenting aorta on lung pictures if one exists. 

Program has GUI application, that makes easier interraction and it's more intuitive.

Application consists of choosing option to display some part of filtering image.

*** display original image
*** display threshold image
*** display edge detection image

Next is Open Image button. If the type of selected file is invalid, according message is displayed.

By default, final image is being displayed every time if there is aorta in picture or error message 
is displayed otherwise.

Problems during this projects:
 1. Not being able to segment region of interest on image just from threshold.
 2. Did not find solution for Tkinter or PyQt5 modules to put images that needs to be displayed
    in original main frame window of application.
 3. I had difficult time figuring out just the right threshold and edge detection filters and
    combining all that filters together.

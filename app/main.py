import vtkmodules.vtkRenderingCore
from vtkmodules.vtkCommonColor import vtkNamedColors
from functions import *
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import sys
from random import random
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

bg = vtkNamedColors() # Get vtk colors for background
colors = [(0.0, 0.0, 0.0),
          (0.0, 1.0, 240.0 / 255.0),
          (1.0, 0.0, 240.0 / 255.0),
          (1.0, 1.0, 0.1 / 255.0),
          (0.5, 1.0, 120.0 / 255.0),
          (0.5, 0.5, 240.0 / 255.0),
          (1.0, 0.5, 120.0 / 255.0),
          (1.0, 1.0, 240.0 / 255.0)] # Create list of segment colors

# Load the segmented file and separate it into segments
filename = sys.argv[1]
seg_list, img_values = get_segment_image(filename)

# Load the non-segmented file
actor_full = get_full_volume(sys.argv[2])

# Add all actors to a list, starting from the 2nd index because first one corresponds to the background value
actor_list = []
for i in range(7):
    actor_list.append(get_seg_volume(seg_list[i+1], img_values[i+1], colors[i+1]))

class Ui(QMainWindow):

    def __init__(self, actorlist, raw_actor):

        super(Ui, self).__init__()
        uic.loadUi('heart_layout.ui', self) # Load ui

        self.vtk_widget = QVTKRenderWindowInteractor(self.heart_frame)
        self.vtk_layout.addWidget(self.vtk_widget)

        self.vtk_widget2= QVTKRenderWindowInteractor(self.heart_frame_2)
        self.vtk_layout2.addWidget(self.vtk_widget2)

        self.iren = self.vtk_widget.GetRenderWindow().GetInteractor()

        self.ren = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.ren)
        self.ren.SetBackground(bg.GetColor3d("PowderBlue"))
        self.ren.ResetCamera()

        self.iren2 = self.vtk_widget2.GetRenderWindow().GetInteractor()

        self.ren2 = vtk.vtkRenderer()
        self.vtk_widget2.GetRenderWindow().AddRenderer(self.ren2)
        self.ren2.SetBackground(bg.GetColor3d("PowderBlue"))
        # self.ren2.SetActiveCamera(self.ren.GetActiveCamera())
        self.ren2.ResetCamera()
        self.ren2.AddActor(raw_actor)

        # Initialize all actors in this class
        self.LVM = actorlist[0]
        self.LAC = actorlist[1]
        self.LVC = actorlist[2]
        self.RAC = actorlist[3]
        self.RVC = actorlist[4]
        self.AA = actorlist[5]
        self.PA = actorlist[6]

        # Create list of actors as defined within our class
        segment_list = [self.LVM, self.LAC, self.LVC, self.RAC, self.RVC, self.AA, self.PA]

        # Create list of the Color checkboxes from Qt Designer
        box_list = [self.LVM_box, self.LAC_box, self.LVC_box, self.RAC_box, self.RVC_box, self.AA_box, self.PA_box]

        # Create list of the Visibility checkboxes from Qt Designer
        vis_list = [self.LVM_Vis, self.LAC_Vis, self.LVC_Vis, self.RAC_Vis, self.RVC_Vis, self.AA_Vis, self.PA_Vis]

        # Create list of the value of each actor
        segment_values = [205, 420, 500, 550, 600, 820, 850]

        for segment in segment_list: # Add all actors to the renderer
            self.ren.AddActor(segment)

        # Initialize stereo rendering
        self.vtk_widget.GetRenderWindow().GetStereoCapableWindow()
        self.vtk_widget.GetRenderWindow().StereoCapableWindowOn()
        # self.shareCam = self.vtk_widget.GetRenderWindow().AddObserver('ActiveCameraEvent', self.ShareCameraQt())
        self.vtk_widget.GetRenderWindow().Render()

        self.vtk_widget2.GetRenderWindow().GetStereoCapableWindow()
        self.vtk_widget2.GetRenderWindow().StereoCapableWindowOn()
        self.vtk_widget2.GetRenderWindow().Render()

        self.show()

        self.iren.Initialize()
        self.iren.Start()

        self.iren2.Initialize()
        self.iren2.Start()

        # Connect each checkbox to the change_color function
        for btn in range(len(box_list)):
            box_list[btn].clicked.connect(lambda _, change=btn: self.change_color(segment_list[change], segment_values[change],
                                                                                  box_list[change].isChecked()))

        # Connect each check box to the hide_actor function
        for btn in range(len(vis_list)):
            vis_list[btn].clicked.connect(lambda _, change=btn: self.hide_actor(segment_list[change]))

        # Connect pushbutton to activate_learning function
        self.Learning_mode.clicked.connect(lambda: self.activate_learning(segment_values, segment_list, box_list))

        # Connect checkbox to stereo_check function
        self.stereo_box.clicked.connect(lambda : self.stereo_check(self.stereo_box.isChecked()))

    def ShareCameraQt(self):
        self.vtk_widget2.GetRenderWindow().GetStereoCapableWindow()
        self.vtk_widget2.GetRenderWindow().StereoCapableWindowOn()
        self.vtk_widget2.GetRenderWindow().Render()


    def change_color(self, act, img_value, checked):

        """
        This function changes the color of each separate segment.
        If checked == true it will generate a random color for this segment
        If checked == false it will change into a white color.
        """

        if checked:
            r, g, b = random(), random(), random()
            col = vtk.vtkColorTransferFunction()
            col.AddRGBPoint(img_value, r, g, b)
            prop = act.GetProperty()
            prop.SetColor(col)
            self.vtk_widget.Render()

        if not checked:
            col = vtk.vtkColorTransferFunction()
            col.AddRGBPoint(img_value, 200, 200, 200)
            prop = act.GetProperty()
            prop.SetColor(col)
            self.vtk_widget.Render()


    def activate_learning(self, imagevalues, actors, box_list):
        """
        This function will hide all initialized segment colors and set all segments to white.
        """
        for a in range(len(actors)):
            col = vtk.vtkColorTransferFunction()
            col.AddRGBPoint(imagevalues[a], 200, 200, 200)
            prop = actors[a].GetProperty()
            prop.SetColor(col)
            self.vtk_widget.Render()
            
        for btn in range(len(box_list)): # uncheck all the boxes when segments are cleared
            box_list[btn].setChecked(False)

    def hide_actor(self, a):
        """
        Hides a segment upon unchecking the checkbox.
        """
        a.SetVisibility(not a.GetVisibility())
        self.vtk_widget.Render()


    def stereo_check(self, checked):
        """
        Stereo rendering
        """
        self.vtk_widget.GetRenderWindow().SetStereoRender(checked)
        self.vtk_widget.GetRenderWindow().SetStereoTypeToAnaglyph()
        self.vtk_widget.GetRenderWindow().Render()

        self.vtk_widget2.GetRenderWindow().SetStereoRender(checked)
        self.vtk_widget2.GetRenderWindow().SetStereoTypeToAnaglyph()
        self.vtk_widget2.GetRenderWindow().Render()

        # For final presentation
        # self.vtk_widget.GetRenderWindow().SetStereoTypeToCristalEyes()
        # self.vtk_widget2.GetRenderWindow().SetStereoTypeToCristalEyes()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Ui(actor_list, actor_full)
    window.show()
    sys.exit(app.exec_())

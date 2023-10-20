import SimpleITK as sitk
import numpy as np
import vtkmodules.all as vtk
from vtkmodules.util.numpy_support import numpy_to_vtk


def numpy_arr_to_vtk_img(arr):
    """
    Takes a numpy array and returns a vtk image object.
    """
    img = vtk.vtkImageData()
    shape = arr.shape
    flat_arr = arr.flatten()
    copy = numpy_to_vtk(flat_arr, deep=1, array_type=vtk.VTK_FLOAT)
    img.SetSpacing([1,1,1])
    img.SetOrigin([0,0,0])
    img.GetPointData().SetScalars(copy)
    img.SetDimensions(shape[0],shape[1],shape[2])

    return img


def img_to_arr(filename):
    """
    Takes an image and returns a numpy array.
    """
    reader = sitk.ImageFileReader()
    reader.SetFileName(filename)
    image = reader.Execute()
    array = sitk.GetArrayFromImage(image)

    return array


def get_segment_image(filename):
    """
    Separate the image into different segments. Returns a list of segments containing vtk image data objects and the
    corresponding values that were used to separate those.
    """
    img_arr = img_to_arr(filename)
    img_values = np.unique(img_arr)
    seg_list = []
    for i in range(len(img_values)):
        seg_tmp = np.where(img_arr == img_values[i], img_values[i], 0)
        seg_list.append(numpy_arr_to_vtk_img(seg_tmp))

    return seg_list, img_values


def get_seg_volume(img, img_value, color):
    """
    Takes a vtk image object, a value (int) in the Houndsfield scale and a color (tuple: (r, g, b)).
    Returns an actor with the given color, corresponding to the given segment value (img_value).
    """

    gaussian_radius = 1
    gaussian_standard_deviation = 1
    gaussian = vtk.vtkImageGaussianSmooth()
    gaussian.SetStandardDeviations(gaussian_standard_deviation, gaussian_standard_deviation,
                                   gaussian_standard_deviation)
    gaussian.SetRadiusFactors(gaussian_radius, gaussian_radius, gaussian_radius)
    gaussian.SetInputData(img)

    #vol_map = vtk.vtkFixedPointVolumeRayCastMapper()
    vol_map = vtk.vtkGPUVolumeRayCastMapper()
    vol_map.SetInputConnection(gaussian.GetOutputPort())
    vol_map.SetBlendModeToComposite()
    vol_map.SetScalarModeToUsePointData()

    ctfun = vtk.vtkColorTransferFunction()
    ctfun.AddRGBPoint(img_value, color[0], color[1], color[2])

    opacity = vtk.vtkPiecewiseFunction()
    opacity.AddPoint(0, 0.0)
    opacity.AddPoint(img_value-img_value/3, 0.5)
    opacity.AddPoint(img_value, 1.0)

    volume_gradient_opacity = vtk.vtkPiecewiseFunction()
    volume_gradient_opacity.AddPoint(0, 0.0)
    volume_gradient_opacity.AddPoint(img_value-img_value/3, 0.5)
    volume_gradient_opacity.AddPoint(img_value, 1.0)


    vol_prop = vtk.vtkVolumeProperty()
    vol_prop.SetColor(ctfun)
    vol_prop.SetScalarOpacity(opacity)
    vol_prop.SetGradientOpacity(volume_gradient_opacity)
    vol_prop.SetInterpolationTypeToLinear()
    vol_prop.ShadeOn()
    vol_prop.SetAmbient(0.4)
    vol_prop.SetDiffuse(0.6)
    #vol_prop.SetSpecular(0.2)
    vol_prop.IndependentComponentsOn()


    vol_actor = vtk.vtkVolume()
    vol_actor.SetMapper(vol_map)
    vol_actor.SetProperty(vol_prop)

    return vol_actor


def get_full_volume(img):
    """
    Loads a not segmented image and returns a single actor containing this volume.
    """
    reader_src = vtk.vtkNIFTIImageReader()
    reader_src.SetFileName(img)

    #vol_map = vtk.vtkFixedPointVolumeRayCastMapper()
    vol_map = vtk.vtkGPUVolumeRayCastMapper()
    vol_map.SetInputConnection(reader_src.GetOutputPort())

    ctfun = vtk.vtkColorTransferFunction()
    ctfun.AddHSVPoint(0, 0., 0., 0.)
    ctfun.AddHSVPoint(676.15, 0., 0, 0.3)
    ctfun.AddHSVPoint(1015.22, 0., 0, 0.4)
    ctfun.AddHSVPoint(1349.00, 0., 0, 0.6)
    ctfun.AddHSVPoint(2185.00, 0., 0., 1.)

    opacity = vtk.vtkPiecewiseFunction()
    opacity.AddPoint(0, 0.0)
    opacity.AddPoint(676.15, 0.)
    opacity.AddPoint(1015.22, 0.32)
    opacity.AddPoint(1349.0, 1.)
    opacity.AddPoint(2185.00, 1.)

    volume_gradient_opacity = vtk.vtkPiecewiseFunction()
    volume_gradient_opacity.AddPoint(0, 0.0)
    volume_gradient_opacity.AddPoint(90, 0.5)
    volume_gradient_opacity.AddPoint(100, 1.0)

    vol_prop = vtk.vtkVolumeProperty()
    vol_prop.SetColor(ctfun)
    vol_prop.SetScalarOpacity(opacity)
    vol_prop.SetGradientOpacity(volume_gradient_opacity)
    vol_prop.SetInterpolationTypeToLinear()
    vol_prop.ShadeOn()
    vol_prop.SetAmbient(0.4)
    vol_prop.SetDiffuse(0.6)
    vol_prop.SetSpecular(0.2)
    # vol_prop.IndependentComponentsOn()

    vol_actor = vtk.vtkVolume()
    vol_actor.SetMapper(vol_map)
    vol_actor.SetProperty(vol_prop)

    return vol_actor
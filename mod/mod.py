import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# mod
#

class mod(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "mod" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Patrycja Mehlich"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# modWidget
#

class modWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
  
    wybierz_model = ctk.ctkCollapsibleButton()
    wybierz_model.text = "Modele"
    self.layout.addWidget(wybierz_model)


    # Layout within the dummy collapsible button
    modelsFormLayout = qt.QFormLayout(wybierz_model)

	#
	#model_wejsciowy
	#
   
    self.modelsSelector = slicer.qMRMLNodeComboBox()
    self.modelsSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.modelsSelector.selectNodeUponCreation = True
    self.modelsSelector.addEnabled = False
    self.modelsSelector.removeEnabled = True
    self.modelsSelector.noneEnabled = True
    self.modelsSelector.showHidden = False
    self.modelsSelector.showChildNodeTypes = False
    self.modelsSelector.setMRMLScene( slicer.mrmlScene )
    self.modelsSelector.setToolTip( "Wybieranie modelu wejsciowego." )
    modelsFormLayout.addRow("Model wejsciowy: ", self.modelsSelector)


	
	#
	#przezroczystosc
	#
    
    self.modelOpacitySliderWidget = ctk.ctkSliderWidget()
    self.modelOpacitySliderWidget.singleStep = 0.1
    self.modelOpacitySliderWidget.minimum = 0
    self.modelOpacitySliderWidget.maximum = 100
    self.modelOpacitySliderWidget.value = 20
    self.modelOpacitySliderWidget.setToolTip("Ustawienie wartosci przezroczystosci modelu.")
    modelsFormLayout.addRow("Wartosc przezroczystosci:", self.modelOpacitySliderWidget)
	
	#
	# pokaz/ukryj
	#

    self.showButton = qt.QPushButton("Pokaz/ukryj")
    self.showButton.toolTip = "Wyswietla/ukrywa model."
    self.showButton.enabled = True
    modelsFormLayout.addRow(self.showButton)
    

    # connections
	
    self.showButton.connect('clicked(bool)', self.onShowButton)
    self.modelOpacitySliderWidget.connect('valueChanged(double)', self.onSliderValueChanged)

	 # Add vertical spacer
    self.layout.addStretch(1)
 

  def cleanup(self):
    pass


  def onShowButton(self):
    logic = modLogic()
    logic.showModel(self.modelsSelector.currentNode())

  def onSliderValueChanged(self):
    logic = modLogic()
    opacityValue = self.modelOpacitySliderWidget.value
    logic.changeOpacity(self.modelsSelector.currentNode(), opacityValue)
  
  



#
# modLogic
#

class modLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """


  def isValidModelData(self, modelNode):
    """Validates if the model is empty
      """
    if not modelNode:
      logging.debug('isValidAllData failed: no model node defined')
      return False
    return True

  def changeOpacity(self, model, opacityVal):
    if not self.isValidModelData( model):
      slicer.util.errorDisplay('Nieprawidlowy model wejsciowy.')
      return False
    n = model.GetDisplayNode()
    n.SetOpacity(opacityVal/100)
    return True

  def showModel(self, model):
    if not self.isValidModelData( model):
      slicer.util.errorDisplay('Nieprawidlowy model wejsciowy.')
      return False
    node = model.GetDisplayNode()
    visibility = node.GetVisibility()
    if (visibility==0):
      node.SetVisibility(1)
    else:
      node.SetVisibility(0)


class modTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_mod1()

  def test_mod1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = modLogic()
    self.assertTrue( logic.hasModelData(volumeNode) )
    self.delayDisplay('Test passed!')

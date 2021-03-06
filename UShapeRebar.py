# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 - Amritpal Singh <amrit3701@gmail.com>             *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "UShapeRebar"
__author__ = "Amritpal Singh"
__url__ = "https://www.freecadweb.org"

from PySide import QtCore, QtGui
from Rebarfunc import *
from PySide.QtCore import QT_TRANSLATE_NOOP
from RebarDistribution import runRebarDistribution, removeRebarDistribution
from PopUpImage import showPopUpImageDialog
import FreeCAD
import FreeCADGui
import ArchCommands
import os
import sys
import math

def getpointsOfUShapeRebar(FacePRM, r_cover, l_cover, b_cover, t_cover, orientation):
    """ getpointsOfUShapeRebar(FacePRM, RightCover, LeftCover, BottomCover, TopCover, Orientation):
    Return points of the UShape rebar in the form of array for sketch.
    It takes four different orientations input i.e. 'Bottom', 'Top', 'Left', 'Right'.
    """
    if orientation == "Bottom":
        x1 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y1 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
        x2 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y2 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
        x3 = FacePRM[1][0] - FacePRM[0][0] / 2 + FacePRM[0][0] - r_cover
        y3 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
        x4 = FacePRM[1][0] - FacePRM[0][0] / 2 + FacePRM[0][0] - r_cover
        y4 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
    elif orientation == "Top":
        x1 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y1 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
        x2 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y2 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
        x3 = FacePRM[1][0] - FacePRM[0][0] / 2 + FacePRM[0][0] - r_cover
        y3 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
        x4 = FacePRM[1][0] - FacePRM[0][0] / 2 + FacePRM[0][0] - r_cover
        y4 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
    elif orientation == "Left":
        x1 = FacePRM[1][0] - FacePRM[0][0] / 2 + FacePRM[0][0] - r_cover
        y1 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
        x2 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y2 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
        x3 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y3 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
        x4 = FacePRM[1][0] - FacePRM[0][0] / 2 + FacePRM[0][0] - r_cover
        y4 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
    elif orientation == "Right":
        x1 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y1 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
        x2 = FacePRM[1][0] - FacePRM[0][0] / 2 + FacePRM[0][0] - r_cover
        y2 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
        x3 = FacePRM[1][0] - FacePRM[0][0] / 2 + FacePRM[0][0] - r_cover
        y3 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
        x4 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y4 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
    return [FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0),\
           FreeCAD.Vector(x3, y3, 0), FreeCAD.Vector(x4, y4, 0)]

class _UShapeRebarTaskPanel:
    def __init__(self, Rebar = None):
        self.CustomSpacing = None
        if not Rebar:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]
        else:
            self.FaceName = Rebar.Base.Support[0][1][0]
            self.SelectedObj = Rebar.Base.Support[0][0]
        self.form = FreeCADGui.PySideUic.loadUi(os.path.splitext(__file__)[0] + ".ui")
        self.form.setWindowTitle(QtGui.QApplication.translate("RebarAddon", "U-Shape Rebar", None))
        self.form.orientation.addItems(["Bottom", "Top", "Right", "Left"])
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        self.form.customSpacing.clicked.connect(lambda: runRebarDistribution(self))
        self.form.removeCustomSpacing.clicked.connect(lambda: removeRebarDistribution(self))
        self.form.PickSelectedFace.clicked.connect(lambda: getSelectedFace(self))
        self.form.orientation.currentIndexChanged.connect(self.getOrientation)
        self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarBottom.svg"))
        self.form.toolButton.setIcon(self.form.toolButton.style().standardIcon(QtGui.QStyle.SP_DialogHelpButton))
        self.form.toolButton.clicked.connect(lambda: showPopUpImageDialog(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarDetailed.svg"))
        self.Rebar = Rebar

    def getOrientation(self):
        orientation = self.form.orientation.currentText()
        if orientation == "Bottom":
            self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarBottom.svg"))
        elif orientation == "Top":
            self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarTop.svg"))
        elif orientation == "Right":
            self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarRight.svg"))
        else:
            self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarLeft.svg"))

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Apply) | int(QtGui.QDialogButtonBox.Cancel)

    def clicked(self, button):
        if button == int(QtGui.QDialogButtonBox.Apply):
            self.accept(button)

    def accept(self, signal = None):
        f_cover = self.form.frontCover.text()
        f_cover = FreeCAD.Units.Quantity(f_cover).Value
        b_cover = self.form.bottomCover.text()
        b_cover = FreeCAD.Units.Quantity(b_cover).Value
        r_cover = self.form.r_sideCover.text()
        r_cover = FreeCAD.Units.Quantity(r_cover).Value
        l_cover = self.form.l_sideCover.text()
        l_cover = FreeCAD.Units.Quantity(l_cover).Value
        t_cover = self.form.topCover.text()
        t_cover = FreeCAD.Units.Quantity(t_cover).Value
        diameter = self.form.diameter.text()
        diameter = FreeCAD.Units.Quantity(diameter).Value
        rounding = self.form.rounding.value()
        orientation = self.form.orientation.currentText()
        amount_check = self.form.amount_radio.isChecked()
        spacing_check = self.form.spacing_radio.isChecked()
        if not self.Rebar:
            if amount_check:
                amount = self.form.amount.value()
                rebar = makeUShapeRebar(f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, True, amount, orientation, self.SelectedObj, self.FaceName)
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                rebar = makeUShapeRebar(f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, False, spacing, orientation, self.SelectedObj, self.FaceName)
        else:
            if amount_check:
                amount = self.form.amount.value()
                rebar = editUShapeRebar(self.Rebar, f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, True, amount, orientation, self.SelectedObj, self.FaceName)
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                rebar = editUShapeRebar(self.Rebar, f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, False, spacing, orientation, self.SelectedObj, self.FaceName)
        if self.CustomSpacing:
            rebar.CustomSpacing = self.CustomSpacing
            FreeCAD.ActiveDocument.recompute()
        self.Rebar = rebar
        if signal == int(QtGui.QDialogButtonBox.Apply):
            pass
        else:
            FreeCADGui.Control.closeDialog(self)

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


def makeUShapeRebar(f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, amount_spacing_check, amount_spacing_value, orientation = "Bottom", structure = None, facename = None):
    """ makeUShapeRebar(FrontCover, BottomCover, RightCover, LeftCover, Diameter, Topcover, Rounding, AmountSpacingCheck, AmountSpacingValue,
    Orientation, Structure, Facename): Adds the U-Shape reinforcement bar to the selected structural object.
    It takes four different types of orientations as input i.e 'Bottom', 'Top', 'Right', 'Left'.
    """
    if not structure and not facename:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object
        facename = selected_obj.SubElementNames[0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    #StructurePRM = getTrueParametersOfStructure(structure)
    FacePRM = getParametersOfFace(structure, facename)
    if not FacePRM:
        FreeCAD.Console.PrintError("Cannot identified shape or from which base object sturctural element is derived\n")
        return
    # Get points of U-Shape rebar
    points = getpointsOfUShapeRebar(FacePRM, r_cover, l_cover, b_cover, t_cover, orientation)
    import Part
    import Arch
    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject', 'Sketch')
    sketch.MapMode = "FlatFace"
    sketch.Support = [(structure, facename)]
    FreeCAD.ActiveDocument.recompute()
    sketch.addGeometry(Part.LineSegment(points[0], points[1]), False)
    sketch.addGeometry(Part.LineSegment(points[1], points[2]), False)
    import Sketcher
    sketch.addGeometry(Part.LineSegment(points[2], points[3]), False)
    if amount_spacing_check:
        rebar = Arch.makeRebar(structure, sketch, diameter, amount_spacing_value, f_cover)
        FreeCAD.ActiveDocument.recompute()
    else:
        size = (ArchCommands.projectToVector(structure.Shape.copy(), face.normalAt(0, 0))).Length
        rebar = Arch.makeRebar(structure, sketch, diameter, int((size - diameter) / amount_spacing_value), f_cover)
    rebar.Rounding = rounding
    # Adds properties to the rebar object
    rebar.ViewObject.addProperty("App::PropertyString", "RebarShape", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Shape of rebar")).RebarShape = "UShapeRebar"
    rebar.ViewObject.setEditorMode("RebarShape", 2)
    rebar.addProperty("App::PropertyDistance", "FrontCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Front cover of rebar")).FrontCover = f_cover
    rebar.setEditorMode("FrontCover", 2)
    rebar.addProperty("App::PropertyDistance", "RightCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Right Side cover of rebar")).RightCover = r_cover
    rebar.setEditorMode("RightCover", 2)
    rebar.addProperty("App::PropertyDistance", "LeftCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Left Side cover of rebar")).LeftCover = l_cover
    rebar.setEditorMode("LeftCover", 2)
    rebar.addProperty("App::PropertyDistance", "BottomCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Bottom cover of rebar")).BottomCover = b_cover
    rebar.setEditorMode("BottomCover", 2)
    rebar.addProperty("App::PropertyBool", "AmountCheck", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Amount radio button is checked")).AmountCheck
    rebar.setEditorMode("AmountCheck", 2)
    rebar.addProperty("App::PropertyDistance", "TopCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Top cover of rebar")).TopCover = t_cover
    rebar.setEditorMode("TopCover", 2)
    rebar.addProperty("App::PropertyDistance", "TrueSpacing", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Spacing between of rebars")).TrueSpacing = amount_spacing_value
    rebar.setEditorMode("TrueSpacing", 2)
    rebar.addProperty("App::PropertyString", "Orientation", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Shape of rebar")).Orientation = orientation
    rebar.setEditorMode("Orientation", 2)
    if amount_spacing_check:
        rebar.AmountCheck = True
    else:
        rebar.AmountCheck = False
        rebar.TrueSpacing = amount_spacing_value
    rebar.Label = "UShapeRebar"
    FreeCAD.ActiveDocument.recompute()
    return rebar

def editUShapeRebar(Rebar, f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, amount_spacing_check, amount_spacing_value, orientation, structure = None, facename = None):
    sketch = Rebar.Base
    if structure and facename:
        sketch.Support = [(structure, facename)]
    # Check if sketch support is empty.
    if not sketch.Support:
        showWarning("You have checked remove external geometry of base sketchs when needed.\nTo unchecked Edit->Preferences->Arch.")
        return
    # Assigned values
    facename = sketch.Support[0][1][0]
    structure = sketch.Support[0][0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    #StructurePRM = getTrueParametersOfStructure(structure)
    # Get parameters of the face where sketch of rebar is drawn
    FacePRM = getParametersOfFace(structure, facename)
    # Get points of U-Shape rebar
    points = getpointsOfUShapeRebar(FacePRM, r_cover, l_cover, b_cover, t_cover, orientation)
    sketch.movePoint(0, 1, points[0], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(0, 2, points[1], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(1, 1, points[1], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(1, 2, points[2], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(2, 1, points[2], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(2, 2, points[3], 0)
    FreeCAD.ActiveDocument.recompute()
    Rebar.OffsetStart = f_cover
    Rebar.OffsetEnd = f_cover
    if amount_spacing_check:
        Rebar.Amount = amount_spacing_value
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = True
    else:
        size = (ArchCommands.projectToVector(structure.Shape.copy(), face.normalAt(0, 0))).Length
        Rebar.Amount = int((size - diameter) / amount_spacing_value)
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = False
    Rebar.Diameter = diameter
    Rebar.FrontCover = f_cover
    Rebar.RightCover = r_cover
    Rebar.LeftCover = l_cover
    Rebar.BottomCover = b_cover
    Rebar.TopCover = t_cover
    Rebar.Rounding = rounding
    Rebar.TrueSpacing = amount_spacing_value
    Rebar.Orientation = orientation
    FreeCAD.ActiveDocument.recompute()
    return Rebar

def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _UShapeRebarTaskPanel(vobj.Object)
    obj.form.frontCover.setText(str(vobj.Object.FrontCover))
    obj.form.r_sideCover.setText(str(vobj.Object.RightCover))
    obj.form.l_sideCover.setText(str(vobj.Object.LeftCover))
    obj.form.bottomCover.setText(str(vobj.Object.BottomCover))
    obj.form.diameter.setText(str(vobj.Object.Diameter))
    obj.form.topCover.setText(str(vobj.Object.TopCover))
    obj.form.rounding.setValue(vobj.Object.Rounding)
    obj.form.orientation.setCurrentIndex(obj.form.orientation.findText(str(vobj.Object.Orientation)))
    if vobj.Object.AmountCheck:
        obj.form.amount.setValue(vobj.Object.Amount)
    else:
        obj.form.amount_radio.setChecked(False)
        obj.form.spacing_radio.setChecked(True)
        obj.form.amount.setDisabled(True)
        obj.form.spacing.setEnabled(True)
        obj.form.spacing.setText(str(vobj.Object.TrueSpacing))
    #obj.form.PickSelectedFace.setVisible(False)
    FreeCADGui.Control.showDialog(obj)

def CommandUShapeRebar():
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_UShapeRebarTaskPanel())

# SPDX-License-Identifier: LGPL-2.1-or-later
"""FDM Slicing workbench — mesh to G-code via external slicer CLI."""

import os

import FreeCAD
import FreeCADGui

__dirname__ = os.path.join(FreeCAD.getResourceDir(), "Mod", "FDM")


class FdmWorkbench(FreeCADGui.Workbench):
    """Workbench for FDM slicing (separate from CAM milling)."""

    def __init__(self):
        def QT_TRANSLATE_NOOP(ctx, txt):
            return txt

        self.__class__.Icon = os.path.join(__dirname__, "Resources", "icons", "FDMWorkbench.svg")
        self.__class__.MenuText = QT_TRANSLATE_NOOP("Workbench", "FDM Slicing")
        self.__class__.ToolTip = QT_TRANSLATE_NOOP(
            "Workbench",
            "Slice meshes to G-code using an external slicer (not CAM toolpaths).",
        )

    def Initialize(self):
        def QT_TRANSLATE_NOOP(context, text):
            return text

        FreeCADGui.addIconPath(os.path.join(__dirname__, "Resources", "icons"))
        import Commands

        self.appendToolbar(
            QT_TRANSLATE_NOOP("Workbench", "FDM"),
            ["FDM_SliceToGcode"],
        )
        self.appendMenu(
            QT_TRANSLATE_NOOP("Workbench", "&FDM"),
            ["FDM_SliceToGcode"],
        )

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(FdmWorkbench())

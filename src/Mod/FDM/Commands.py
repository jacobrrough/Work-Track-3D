# SPDX-License-Identifier: LGPL-2.1-or-later

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate


class CmdFDMSlice:
    """Open the FDM slice dialog (external slicer CLI)."""

    def GetResources(self):
        return {
            "Pixmap": "FDMWorkbench",
            "MenuText": translate("FDM", "Slice mesh to G-code…"),
            "ToolTip": translate(
                "FDM",
                "Export selection to STL and run an external FDM slicer (PrusaSlicer, CuraEngine, etc.).",
            ),
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        import fdm_dialog

        fdm_dialog.show_dialog()


FreeCADGui.addCommand("FDM_SliceToGcode", CmdFDMSlice())

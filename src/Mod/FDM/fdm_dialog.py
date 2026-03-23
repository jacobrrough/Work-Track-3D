# SPDX-License-Identifier: LGPL-2.1-or-later
"""Dialog for FDM slicing (external CLI)."""

from pathlib import Path

from PySide import QtCore, QtGui

import FreeCAD
import FreeCADGui

import fdm_slicer

translate = FreeCAD.Qt.translate


class FdmSliceDialog(QtGui.QDialog):
    """Configure slicer CLI and run slice on current selection."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translate("FDM", "FDM — Slice to G-code"))
        self.setMinimumWidth(520)
        self.p = fdm_slicer.get_preferences()

        layout = QtGui.QVBoxLayout(self)

        form = QtGui.QFormLayout()
        self.backend_combo = QtGui.QComboBox()
        self.backend_combo.addItem("PrusaSlicer / Orca / SuperSlicer (CLI)", "prusa")
        self.backend_combo.addItem("CuraEngine (CLI)", "cura")
        self.backend_combo.addItem(translate("FDM", "Custom (see preferences)"), "custom")
        form.addRow(translate("FDM", "Backend:"), self.backend_combo)

        self.exe_edit = QtGui.QLineEdit()
        self.exe_btn = QtGui.QPushButton(translate("FDM", "Browse…"))
        self.exe_btn.clicked.connect(self._browse_exe)
        exe_row = QtGui.QHBoxLayout()
        exe_row.addWidget(self.exe_edit)
        exe_row.addWidget(self.exe_btn)
        exe_wrap = QtGui.QWidget()
        exe_wrap.setLayout(exe_row)
        form.addRow(translate("FDM", "Slicer executable:"), exe_wrap)

        self.profile_edit = QtGui.QLineEdit()
        self.profile_btn = QtGui.QPushButton(translate("FDM", "Browse…"))
        self.profile_btn.clicked.connect(self._browse_profile)
        prof_row = QtGui.QHBoxLayout()
        prof_row.addWidget(self.profile_edit)
        prof_row.addWidget(self.profile_btn)
        prof_wrap = QtGui.QWidget()
        prof_wrap.setLayout(prof_row)
        form.addRow(translate("FDM", "Profile / config file:"), prof_wrap)

        self.output_edit = QtGui.QLineEdit()
        out_row = QtGui.QHBoxLayout()
        out_row.addWidget(self.output_edit)
        self.out_btn = QtGui.QPushButton(translate("FDM", "Browse…"))
        self.out_btn.clicked.connect(self._browse_output)
        out_row.addWidget(self.out_btn)
        out_wrap = QtGui.QWidget()
        out_wrap.setLayout(out_row)
        form.addRow(translate("FDM", "Output G-code:"), out_wrap)

        self.custom_edit = QtGui.QLineEdit()
        self.custom_edit.setPlaceholderText(
            "{exe} {input} --output {output} --load {profile}"
        )
        self.custom_label = QtGui.QLabel(translate("FDM", "Custom command template:"))
        form.addRow(self.custom_label, self.custom_edit)
        self.custom_label.hide()
        self.custom_edit.hide()

        self.backend_combo.currentIndexChanged.connect(self._on_backend_changed)

        layout.addLayout(form)

        hint = QtGui.QLabel(
            translate(
                "FDM",
                "Select a mesh (Mesh) or a Part object. Export uses STL. "
                "This is not the CAM milling workbench — install PrusaSlicer or CuraEngine separately.",
            )
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
        )
        buttons.accepted.connect(self._run)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._load_prefs()
        self._on_backend_changed()

    def _on_backend_changed(self):
        is_custom = self.backend_combo.currentData() == "custom"
        self.custom_label.setVisible(is_custom)
        self.custom_edit.setVisible(is_custom)

    def _load_prefs(self):
        b = self.p.GetString("SlicerBackend", "prusa")
        for i in range(self.backend_combo.count()):
            if self.backend_combo.itemData(i) == b:
                self.backend_combo.setCurrentIndex(i)
                break
        self.exe_edit.setText(self.p.GetString("SlicerExecutable", ""))
        self.profile_edit.setText(self.p.GetString("ProfilePath", ""))
        self.custom_edit.setText(self.p.GetString("CustomCommand", ""))
        out = self.p.GetString("LastGcodePath", "")
        if not out:
            out_dir = self.p.GetString("LastOutputDirectory", "")
            if out_dir:
                out = str(Path(out_dir) / "output.gcode")
        self.output_edit.setText(out)

    def _save_prefs(self):
        self.p.SetString("SlicerBackend", self.backend_combo.currentData())
        self.p.SetString("SlicerExecutable", self.exe_edit.text().strip())
        self.p.SetString("ProfilePath", self.profile_edit.text().strip())
        self.p.SetString("CustomCommand", self.custom_edit.text().strip())

    def _browse_exe(self):
        path, _ = QtGui.QFileDialog.getOpenFileName(
            self,
            translate("FDM", "Slicer executable"),
            self.exe_edit.text() or str(Path.home()),
        )
        if path:
            self.exe_edit.setText(path)

    def _browse_profile(self):
        path, _ = QtGui.QFileDialog.getOpenFileName(
            self,
            translate("FDM", "Profile / configuration"),
            self.profile_edit.text() or str(Path.home()),
            translate("FDM", "Config (*.ini *.cfg *.json);;All files (*.*)"),
        )
        if path:
            self.profile_edit.setText(path)

    def _browse_output(self):
        path, _ = QtGui.QFileDialog.getSaveFileName(
            self,
            translate("FDM", "Output G-code"),
            self.output_edit.text() or str(Path.home() / "output.gcode"),
            translate("FDM", "G-code (*.gcode *.gco *.nc);;All files (*.*)"),
        )
        if path:
            self.output_edit.setText(path)

    def _run(self):
        self._save_prefs()
        out = self.output_edit.text().strip()
        if not out:
            QtGui.QMessageBox.warning(
                self,
                translate("FDM", "FDM"),
                translate("FDM", "Set an output G-code path."),
            )
            return
        Path(out).parent.mkdir(parents=True, exist_ok=True)

        doc = FreeCAD.ActiveDocument
        if not doc:
            QtGui.QMessageBox.warning(self, translate("FDM", "FDM"), translate("FDM", "No active document."))
            return
        import tempfile

        with tempfile.TemporaryDirectory(prefix="fc_fdm_") as tmp:
            stl_path = str(Path(tmp) / "mesh.stl")
            if not fdm_slicer.export_selection_to_stl(doc, stl_path):
                return
            ok, msg = fdm_slicer.run_slicer(
                self.backend_combo.currentData(),
                self.exe_edit.text().strip(),
                stl_path,
                self.profile_edit.text().strip(),
                out,
            )

        if ok:
            self.p.SetString("LastOutputDirectory", str(Path(out).parent))
            self.p.SetString("LastGcodePath", out)
            QtGui.QMessageBox.information(
                self,
                translate("FDM", "FDM"),
                translate("FDM", "G-code written to:\n{}").format(out),
            )
            self.accept()
        else:
            QtGui.QMessageBox.critical(
                self,
                translate("FDM", "Slicer failed"),
                msg[:8000],
            )


def show_dialog():
    dlg = FdmSliceDialog(FreeCADGui.getMainWindow())
    dlg.exec_()

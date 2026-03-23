# SPDX-License-Identifier: LGPL-2.1-or-later
"""Run external FDM slicers (CLI). Not part of CAM milling toolpaths."""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import FreeCAD

translate = FreeCAD.Qt.translate


def get_preferences():
    """Return ParamGet for FDM module preferences."""
    return FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/FDM")


def export_selection_to_stl(doc, path: str) -> bool:
    """Export first selected mesh or shape to STL. Returns True on success."""
    import FreeCADGui

    sel = FreeCADGui.Selection.getSelection()
    if not sel:
        FreeCAD.Console.PrintError("FDM: No object selected.\n")
        return False
    obj = sel[0]
    path_p = Path(path)
    path_p.parent.mkdir(parents=True, exist_ok=True)

    if obj.isDerivedFrom("Mesh::Object"):
        obj.Mesh.write(str(path_p))
        return True
    if hasattr(obj, "Shape"):
        try:
            import MeshPart
        except ImportError:
            FreeCAD.Console.PrintError(
                "FDM: MeshPart is not available. Build the MeshPart module to tessellate solids.\n"
            )
            return False
        mesh = MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=0.2)
        mesh.write(str(path_p))
        return True
    FreeCAD.Console.PrintError("FDM: Selected object must be a mesh or a solid with Shape.\n")
    return False


def build_command(
    backend: str,
    exe: str,
    input_stl: str,
    profile: str,
    output_gcode: str,
) -> list[str]:
    """Build command line for the chosen backend."""
    exe = exe.strip()
    if not exe:
        raise ValueError("Slicer executable path is empty.")

    backend = backend.lower()
    inp = str(Path(input_stl).resolve())
    out = str(Path(output_gcode).resolve())
    prof = str(Path(profile).resolve()) if profile.strip() else ""

    if backend == "prusa":
        # PrusaSlicer / OrcaSlicer / SuperSlicer console
        if prof:
            cmd = [exe, "--load", prof, inp, "--export-gcode", "--output", out]
        else:
            cmd = [exe, inp, "--export-gcode", "--output", out]
        return cmd

    if backend == "cura":
        # CuraEngine: -j definitions folder or json; profile must point at machine definition
        if not prof:
            raise ValueError("CuraEngine backend requires a JSON settings file in profile field.")
        return [exe, "slice", "-v", "-j", prof, "-l", inp, "-o", out]

    if backend == "custom":
        custom = get_preferences().GetString("CustomCommand", "")
        if not custom:
            raise ValueError("Custom backend: set CustomCommand in preferences.")
        cmd = custom.format(
            exe=exe,
            input=inp,
            output=out,
            profile=prof,
        )
        return shlex.split(cmd, posix=os.name != "nt")

    raise ValueError(f"Unknown FDM backend: {backend}")


def run_slicer(
    backend: str,
    exe: str,
    input_stl: str,
    profile: str,
    output_gcode: str,
) -> tuple[bool, str]:
    """Execute slicer; returns (success, combined stdout/stderr)."""
    try:
        cmd = build_command(backend, exe, input_stl, profile, output_gcode)
    except Exception as e:
        return False, str(e)

    try:
        creationflags = 0
        if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,
            creationflags=creationflags,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            return False, f"Exit {proc.returncode}\n{out}"
        return True, out
    except subprocess.TimeoutExpired:
        return False, "Slicer timed out after 1 hour."
    except FileNotFoundError:
        return False, f"Executable not found: {cmd[0]}"
    except Exception as e:
        return False, str(e)


def slice_selection_to_gcode(output_path: Optional[str] = None) -> tuple[bool, str]:
    """Export selection to temp STL, run configured slicer, return (ok, message)."""
    p = get_preferences()
    backend = p.GetString("SlicerBackend", "prusa")
    exe = p.GetString("SlicerExecutable", "")
    profile = p.GetString("ProfilePath", "")

    if not output_path:
        out_dir = p.GetString("LastOutputDirectory", "")
        if not out_dir:
            out_dir = str(Path(FreeCAD.getUserAppDataDir()) / "FDM" / "output")
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        output_path = str(Path(out_dir) / "output.gcode")

    with tempfile.TemporaryDirectory(prefix="fc_fdm_") as tmp:
        stl_path = os.path.join(tmp, "mesh.stl")
        doc = FreeCAD.ActiveDocument
        if not doc:
            return False, "No active document."
        if not export_selection_to_stl(doc, stl_path):
            return False, "Could not export mesh to STL."

        ok, msg = run_slicer(backend, exe, stl_path, profile, output_path)
        if ok:
            p.SetString("LastOutputDirectory", str(Path(output_path).parent))
            p.SetString("LastGcodePath", output_path)
        return ok, msg

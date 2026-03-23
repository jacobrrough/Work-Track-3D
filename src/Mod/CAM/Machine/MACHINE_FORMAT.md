# CAM machine definitions (`.fcm`)

FreeCAD CAM stores **CNC machine** configuration as JSON files with the extension **`.fcm`**. They live under your CAM asset path in the **`Machines/`** subdirectory (see **Edit → Preferences → CAM → Assets**).

## Importing a machine

1. **Preferences:** CAM → Assets → **Import…** — copies the selected `.fcm` into `Machines/` and adds it to the list.
2. **Machine Editor:** **Import from file…** — loads a file for editing; use **Save** to write a copy into `Machines/`.

Built-in templates ship under `Mod/CAM/Machine/machines/` (e.g. `Generic_Grbl.fcm`).

## Jobs and post-processing

Assign a machine to a **CAM Job** (when the machine-based post workflow is enabled). Post-processing resolves the **Python postprocessor** from the machine definition and exports **G-code** — see the CAM Workbench documentation.

## Fusion 360 `.cps` and generic `.cfg`

**Autodesk Fusion 360 `.cps` post processors are JavaScript** and are **not** loaded by FreeCAD. CAM post-processing uses **Python** scripts under `Path/Post/scripts/`. To use a controller defined in Fusion, you must **port** settings to a FreeCAD `.fcm` plus a matching **Python** postprocessor (or adapt an existing one).

Vendor-specific **`.cfg`** files are not interchangeable unless you implement a **dedicated importer** for one format. Use FreeCAD-native `.fcm` and slicer-specific profiles for FDM (see the FDM slicer module documentation).

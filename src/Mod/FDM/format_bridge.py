# SPDX-License-Identifier: LGPL-2.1-or-later
"""
Placeholder for vendor-specific config importers.

See FORMAT_BRIDGE.md for the canonical formats used in this fork:

- CNC: FreeCAD-native ``.fcm`` + Python postprocessors (not Fusion ``.cps``).
- FDM: slicer CLI profiles (e.g. Prusa/Orca ``.ini``) or CustomCommand strings.

Implementations here should target **one** agreed file format per workflow.
"""


def import_fcm_from_json_file(path: str):
    """Load a machine definition — use ``MachineFactory.load_configuration`` instead."""
    raise NotImplementedError("Use Machine.models.machine.MachineFactory.load_configuration")


def import_fdm_profile_placeholder(path: str):
    """Future: map a single vendor profile format to slicer CLI arguments."""
    raise NotImplementedError("See FORMAT_BRIDGE.md — configure the FDM dialog or CustomCommand.")

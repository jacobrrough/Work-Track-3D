# SPDX-License-Identifier: LGPL-2.1-or-later

SET(FDM_SRCS
    Init.py
    InitGui.py
    Commands.py
    fdm_slicer.py
    fdm_dialog.py
    format_bridge.py
)

SET(FDM_DOCS
    README.md
    FORMAT_BRIDGE.md
)

SOURCE_GROUP("" FILES ${FDM_SRCS} ${FDM_DOCS})

ADD_CUSTOM_TARGET(FDM ALL SOURCES ${FDM_SRCS} ${FDM_DOCS})

fc_copy_sources(FDM "${CMAKE_BINARY_DIR}/Mod/FDM" ${FDM_SRCS} ${FDM_DOCS})

INSTALL(FILES ${FDM_SRCS} ${FDM_DOCS} DESTINATION Mod/FDM)

INSTALL(
    FILES
        Resources/icons/FDMWorkbench.svg
    DESTINATION
        Mod/FDM/Resources/icons
)

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/Resources/icons/FDMWorkbench.svg
     DESTINATION ${CMAKE_BINARY_DIR}/Mod/FDM/Resources/icons)

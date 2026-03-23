# Work Track 3D

This repository is the **Work Track 3D** project: a customized CAD/CAM workspace derived from the [FreeCAD](https://www.freecad.org) source tree, with your own branding, CAM/FDM workflows, and tooling.

## Repository name

- **Display name:** Work Track 3D  
- **Suggested remote name (GitHub):** `work-track-3d` or `WorkTrack3D` (no spaces in the URL)

## GitHub remote

- **Owner:** [jacobrrough](https://github.com/jacobrrough)
- **Repository URL:** https://github.com/jacobrrough/Work-Track-3D

The local `origin` remote should be:

`https://github.com/jacobrrough/Work-Track-3D.git`

After you **create** the empty repository `work-track-3d` on GitHub (no README/license), run:

```powershell
cd "c:\Users\jrrou\Downloads\FreeCAD-main\FreeCAD-main"
git push -u origin main
```

## First-time push note

The full FreeCAD tree is large. For the first commit you can either:

- Commit the whole project (may take a while and produce a large repo), or  
- Use **Git LFS** for big binaries if you add them later, or  
- Keep only the files you changed and track upstream FreeCAD separately (advanced).

## License

FreeCAD is LGPL-2.1-or-later; your modifications should stay compatible with that license. See `LICENSE` in the project root.

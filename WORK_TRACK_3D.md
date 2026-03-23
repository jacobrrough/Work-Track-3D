# Work Track 3D

This repository is the **Work Track 3D** project: a customized CAD/CAM workspace derived from the [FreeCAD](https://www.freecad.org) source tree, with your own branding, CAM/FDM workflows, and tooling.

## Repository name

- **Display name:** Work Track 3D  
- **Suggested remote name (GitHub):** `work-track-3d` or `WorkTrack3D` (no spaces in the URL)

## Create the remote (GitHub)

1. On GitHub: **New repository** → name it (e.g. `work-track-3d`) → create **without** adding a README (this tree already has one).
2. In this folder, add your remote and push:

```powershell
cd "c:\Users\jrrou\Downloads\FreeCAD-main\FreeCAD-main"
git remote add origin https://github.com/YOUR_USERNAME/work-track-3d.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and the repo name with yours.

## First-time push note

The full FreeCAD tree is large. For the first commit you can either:

- Commit the whole project (may take a while and produce a large repo), or  
- Use **Git LFS** for big binaries if you add them later, or  
- Keep only the files you changed and track upstream FreeCAD separately (advanced).

## License

FreeCAD is LGPL-2.1-or-later; your modifications should stay compatible with that license. See `LICENSE` in the project root.

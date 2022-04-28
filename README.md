# GPX Merge

This a small python utility to merge `GPX` and `TCX` files.

<!--ts-->
   * [GPX Merge](#gpx-merge)
      * [Install](#install)
      * [Run](#run)
         * [Merging all gpx and tcx files in a directory](#merging-all-gpx-and-tcx-files-in-a-directory)
         * [Converting tcx to gpx](#converting-tcx-to-gpx)

<!-- Added by: jose, at: jue 28 abr 2022 13:20:23 CEST -->

<!--te-->

## Install

```bash
pip install -r requirements.txt
```

## Run

### Merging all `gpx` and `tcx` files in a directory

```bash
python run.py <dir-with-files-to-merge> <output-gpx-file>
```

### Converting `tcx` to `gpx`

```bash
python -m gptcx.tcx <input-tcx-file> <output-gpx-file>

# GPX Merge

This a small python utility to merge `GPX` and `TCX` files.


<!--ts-->
   * [GPX Merge](#gpx-merge)
      * [Limitations](#limitations)
      * [Install](#install)
      * [Run](#run)
         * [Merging all gpx and tcx files in a directory](#merging-all-gpx-and-tcx-files-in-a-directory)
         * [Converting tcx to gpx](#converting-tcx-to-gpx)

<!-- Added by: jose, at: jue 28 abr 2022 15:43:53 CEST -->

<!--te-->

## Limitations

> ⚠️  Merging `gpx` with `tcx` files is yet not supported!
>
> ❌ Current `gpx` lib doesn't support missing `longitude` and `latitude`
>
> ❌ Current `gpx` lib doesn't support `heart rate` data

## Install

```bash
pip install -r requirements.txt
```

## Run

### Merging all `gpx` ~~and `tcx`~~ files in a directory

```bash
python run.py <dir-with-files-to-merge> <output-gpx-file>
```

### Converting `tcx` to `gpx`

```bash
python -m gptcx.tcx <input-tcx-file> <output-gpx-file>

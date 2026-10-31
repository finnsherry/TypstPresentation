# typst-presentation

Compile [Touying](https://touying-typ.github.io/) presentations to HTML, with
GIFs replaced by MP4 videos (much smaller, smoother playback).

The touying exporter renders each slide to SVG with the GIFs embedded as-is.
After compiling, every embedded GIF is matched to its source file by hash and
replaced by an autoplaying, looping, muted `<video>` of the MP4 next to it.
MP4s are created with ffmpeg when missing or older than the GIF. The Typst
source keeps using the GIFs, so PDF export is unaffected.

## Install

Requires `ffmpeg` on the `PATH`.

```
pip install -e path/to/typst-presentation
```

## Usage

```
presentation compile main.typ                      # writes main.html, videos embedded
presentation compile main.typ --external           # link to the .mp4 files instead
presentation compile main.typ --font-paths ~/fonts
```

Font directories can also be set once in your shell profile, as for the typst
CLI; these are used in addition to any `--font-paths`:

```
export TYPST_FONT_PATHS=~/fonts            # multiple: separate with ':'
```

GIFs are searched for recursively under `--root`, which defaults to the
directory of the input file.

When using `--external`, the .mp4 files must be packaged with the presentation,
with the same relative location as during compilation.
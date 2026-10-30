"""Compile a Touying presentation to HTML, replacing embedded GIFs by MP4 videos.

The touying exporter renders every slide to SVG, so animations end up as
`<image href="data:image/gif;...">` elements. Typst embeds the GIF bytes
unchanged, so each one can be matched to its source file by hash, and swapped
for an autoplaying, looping `<video>` of the MP4 with the same name (converted
with ffmpeg if missing or outdated). The Typst source keeps using the GIFs, so
PDF export is unaffected.
"""

import base64
import hashlib
import os
import re
import subprocess
from pathlib import Path

from touying import exporter

GIF_PATTERN = re.compile(
    r'<image(?P<attrs> (?:transform="[^"]*" )?)'
    r'xlink:href="data:image/gif;base64,(?P<data>[A-Za-z0-9+/=]+)" '
    r'width="(?P<w>[0-9.]+)" height="(?P<h>[0-9.]+)"[^>]*/>'
)


def md5(data):
    return hashlib.md5(data).hexdigest()


def gif_to_mp4(gif, silent=False):
    mp4 = gif.with_suffix(".mp4")
    if not mp4.exists() or mp4.stat().st_mtime < gif.stat().st_mtime:
        if not silent:
            print(f"Converting {gif} to MP4...")
        subprocess.run(
            [
                "ffmpeg", "-loglevel", "error", "-y", "-i", gif,
                "-movflags", "+faststart", "-pix_fmt", "yuv420p",
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                mp4,
            ],
            check=True,
        )
    return mp4


def video_tag(src, attrs, width, height):
    return (
        f'<foreignObject{attrs}width="{width}" height="{height}">'
        f'<video xmlns="http://www.w3.org/1999/xhtml" src="{src}" '
        'autoplay="" loop="" muted="" playsinline="" '
        'style="display:block;width:100%;height:100%;object-fit:fill"></video>'
        "</foreignObject>"
    )


def compile_html(
    input,
    output=None,
    root=None,
    font_paths=[],
    external=False,
    silent=False,
    sys_inputs={},
):
    """Compile `input` to HTML, replacing GIFs found under `root` by videos.

    `root` defaults to the directory of `input`. With `external`, the MP4s are
    referenced by relative path instead of embedded in the HTML.
    """
    input = Path(input)
    output = Path(output) if output is not None else input.with_suffix(".html")
    search_dir = Path(root) if root is not None else input.parent

    videos = {}
    for gif in search_dir.rglob("*.gif"):
        mp4 = gif_to_mp4(gif, silent=silent)
        if external:
            src = Path(os.path.relpath(mp4, output.parent)).as_posix()
        else:
            src = "data:video/mp4;base64," + base64.b64encode(mp4.read_bytes()).decode()
        videos[md5(gif.read_bytes())] = src

    exporter.to_html(
        str(input),
        root=root,
        font_paths=font_paths,
        output=str(output),
        silent=silent,
        sys_inputs=sys_inputs,
    )

    def replace(match):
        src = videos.get(md5(base64.b64decode(match["data"])))
        if src is None:
            return match[0]
        return video_tag(src, match["attrs"], match["w"], match["h"])

    html, n = GIF_PATTERN.subn(replace, output.read_text(encoding="utf8"))
    output.write_text(html, encoding="utf8")
    if not silent:
        print(f"Replaced {n} GIFs by videos in {output}")

"""CLI entry point: `presentation compile source.typ`."""

import argparse
import json

from .compiler import compile_html


def main():
    parser = argparse.ArgumentParser(
        description="Compile Touying presentations to HTML, with GIFs replaced by MP4 videos."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_compile = subparsers.add_parser("compile", help="Compile a file to HTML")
    parser_compile.add_argument("input", help="Input .typ file")
    parser_compile.add_argument(
        "--output", default=None, help="Output file (default: input with .html suffix)"
    )
    parser_compile.add_argument(
        "--root",
        default=None,
        help="Root directory for the typst file; GIFs are searched here "
        "(default: directory of the input file)",
    )
    parser_compile.add_argument(
        "--font-paths",
        nargs="*",
        default=[],
        help="Paths to custom fonts, in addition to those in $TYPST_FONT_PATHS",
    )
    parser_compile.add_argument(
        "--external",
        action="store_true",
        help="Reference the MP4s by relative path instead of embedding them",
    )
    parser_compile.add_argument(
        "--sys-inputs", default=None, help="JSON string to pass to typst's sys.inputs"
    )
    parser_compile.add_argument("--silent", action="store_true", help="Run silently")

    args = parser.parse_args()

    if args.command == "compile":
        compile_html(
            args.input,
            output=args.output,
            root=args.root,
            font_paths=args.font_paths,
            external=args.external,
            silent=args.silent,
            sys_inputs=json.loads(args.sys_inputs) if args.sys_inputs else {},
        )


if __name__ == "__main__":
    main()

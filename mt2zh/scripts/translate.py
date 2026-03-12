#!/usr/bin/env python3
"""
mt2zh - PDF translation tool using pdf2zh-next

Translates PDFs using OpenAI-compatible APIs.
Environment variables:
  MT_API_KEY   - OpenAI API key
  MT_BASE_URL  - OpenAI API base URL
  MT_MODEL     - Model name (default: qwen-plus)
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_MODEL = "qwen-plus"
DEFAULT_LANG_OUT = "zh"


def setup_env(model_override=None):
    """Map MT_* env vars to OPENAI_* env vars expected by pdf2zh."""
    env = os.environ.copy()
    model = model_override or env.get("MT_MODEL", DEFAULT_MODEL)

    if "MT_API_KEY" in env:
        env["OPENAI_API_KEY"] = env["MT_API_KEY"]
    if "MT_BASE_URL" in env:
        env["OPENAI_BASE_URL"] = env["MT_BASE_URL"]
    if model:
        env["OPENAI_MODEL"] = model

    return env, model


def collect_files(path_str, ext_list, recursive=True):
    """Recursively collect files with matching extensions from a directory."""
    path = Path(path_str)
    if not path.is_dir():
        print(f"Error: '{path_str}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    files = []
    for ext in ext_list:
        ext = ext.strip()
        if not ext.startswith("."):
            ext = "." + ext
        if recursive:
            files.extend(path.rglob(f"*{ext}"))
        else:
            files.extend(path.glob(f"*{ext}"))

    return sorted(str(f) for f in files)


def get_output_paths(input_file, output_dir=None):
    """Return expected (mono_path, dual_path) for a given input file."""
    stem = Path(input_file).stem
    out = Path(output_dir) if output_dir else Path(".")
    return out / f"{stem}-mono.pdf", out / f"{stem}-dual.pdf"


def run_translation(files, output_dir, lang_in, lang_out, threads, mode, model_override):
    """Build and run the pdf2zh command, then clean up per display mode."""
    if not files:
        print("No files to translate.", file=sys.stderr)
        return 1

    env, model = setup_env(model_override)

    cmd = ["pdf2zh", "--service", f"openai:{model}"]

    if lang_in:
        cmd += ["--lang-in", lang_in]
    cmd += ["--lang-out", lang_out]

    if output_dir:
        cmd += ["--output", output_dir]

    if threads == "auto":
        cpu = os.cpu_count() or 4
        cmd += ["--thread", str(cpu)]
        print(f"Using {cpu} threads (auto-detected CPU count).")
    elif threads is not None:
        cmd += ["--thread", str(threads)]

    cmd += files

    print(f"Model   : {model}")
    print(f"Files   : {len(files)}")
    print(f"Lang    : {lang_in or 'auto'} -> {lang_out}")
    print(f"Mode    : {mode}")
    print(f"Command : {' '.join(cmd)}\n")

    result = subprocess.run(cmd, env=env)

    if result.returncode != 0:
        return result.returncode

    # Display mode cleanup
    for f in files:
        mono, dual = get_output_paths(f, output_dir)
        if mode == "mono":
            if dual.exists():
                dual.unlink()
            if mono.exists():
                print(f"  [mono] {mono}")
        elif mode == "dual":
            if mono.exists():
                mono.unlink()
            if dual.exists():
                print(f"  [dual] {dual}")
        else:
            if mono.exists():
                print(f"  [mono] {mono}")
            if dual.exists():
                print(f"  [dual] {dual}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Translate PDF files using pdf2zh-next and OpenAI-compatible APIs."
    )
    parser.add_argument(
        "input", nargs="+",
        help="One or more PDF files, or a directory (use --dir flag).",
    )
    parser.add_argument(
        "--dir", action="store_true",
        help="Treat each INPUT as a directory and find all matching files.",
    )
    parser.add_argument(
        "--ext", default=".pdf",
        help="Comma-separated extensions for directory mode (default: .pdf).",
    )
    parser.add_argument(
        "--lang-in", default=None, metavar="LANG",
        help="Source language code, e.g. 'en'. Auto-detected if omitted.",
    )
    parser.add_argument(
        "--lang-out", default=DEFAULT_LANG_OUT, metavar="LANG",
        help=f"Target language code (default: {DEFAULT_LANG_OUT}).",
    )
    parser.add_argument(
        "--mode", choices=["both", "mono", "dual"], default="both",
        help="Output mode: both (default), mono (translation only), dual (bilingual).",
    )
    parser.add_argument(
        "--threads", default=None, metavar="N|auto",
        help="Thread count: integer, 'auto' (match CPU cores), or omit for pdf2zh default.",
    )
    parser.add_argument(
        "--output", default=None, metavar="DIR",
        help="Output directory (default: same directory as each input file).",
    )
    parser.add_argument(
        "--model", default=None,
        help="Override MT_MODEL env var for this run.",
    )

    args = parser.parse_args()

    # Parse threads
    threads = None
    if args.threads:
        if args.threads == "auto":
            threads = "auto"
        else:
            try:
                threads = int(args.threads)
            except ValueError:
                print(f"Invalid --threads value: {args.threads!r}. Use an integer or 'auto'.", file=sys.stderr)
                sys.exit(1)

    # Parse extensions
    ext_list = [e.strip() for e in args.ext.split(",")]

    # Collect files
    files = []
    for inp in args.input:
        p = Path(inp)
        if args.dir or p.is_dir():
            found = collect_files(inp, ext_list)
            if not found:
                print(f"Warning: no {args.ext} files found in '{inp}'.", file=sys.stderr)
            files.extend(found)
        elif p.is_file():
            files.append(str(p))
        else:
            print(f"Error: '{inp}' does not exist.", file=sys.stderr)
            sys.exit(1)

    if args.output:
        Path(args.output).mkdir(parents=True, exist_ok=True)

    return run_translation(
        files=files,
        output_dir=args.output,
        lang_in=args.lang_in,
        lang_out=args.lang_out,
        threads=threads,
        mode=args.mode,
        model_override=args.model,
    )


if __name__ == "__main__":
    sys.exit(main())

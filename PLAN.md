# SRT UTF-8 BOM Converter Plan

## Goal

Build a small command-line tool that takes a folder containing `.srt` files and writes converted `.srt` files to another folder using UTF-8 with BOM.

## Product Decisions

- Language: Python
- Entry point: `main.py`
- Input: one required source directory
- Output: one required destination directory
- Conversion mode: non-destructive, writing converted files to the destination directory
- File selection: process `.srt` files only from the top level of the input directory
- Directory behavior: create the output directory if it does not exist
- Success output: print a short summary with processed and failed file counts
- Failure output: print a clear error to stderr and exit with a non-zero code

## CLI Scope

### Initial version

Support this command shape:

```bash
python main.py path/to/input-folder path/to/output-folder
```

## Implementation Plan

1. Replace the placeholder program in `main.py`.
   Remove the current stub and create a proper CLI entry point with `argparse`.

2. Validate the input and output paths early.
   Reject cases where:
   - the input directory does not exist
   - the input path is not a directory
   - the output path exists but is not a directory

   Create the output directory if needed.

3. Discover source files.
   Enumerate `.srt` files from the input directory.

   The first version should process only the top-level directory and ignore subdirectories.

4. Implement decoding with an explicit fallback order.
   Try the most likely encodings in this order:
   - `utf-8-sig`
   - `utf-8`
   - `cp1252`
   - `latin-1`

   Record which encoding succeeded so it can be reported back to the user.

5. Convert and write using UTF-8 with BOM.
   Write the decoded text using `utf-8-sig`. This ensures the output contains a BOM.

6. Preserve output filenames.
   For each input file, write the converted result to the output directory using the same filename.

   Example:
   - input: `subs/movie.en.srt`
   - output: `converted/movie.en.srt`

7. Define duplicate and overwrite behavior.
   Decide whether existing files in the output directory should:
   - always be overwritten
   - be skipped
   - require a flag

   Recommended initial scope: overwrite existing output files.

8. Normalize error handling.
   Handle these cases cleanly:
   - input directory not found
   - invalid input/output path types
   - no `.srt` files found
   - permission denied
   - decode failure for all attempted encodings
   - write failure for one or more output files

9. Decide batch failure behavior.
   Recommended initial scope:
   - continue processing other files if one file fails
   - report failures at the end
   - exit with `0` only if all files were converted successfully
   - exit with `1` if any file failed or if setup validation failed

10. Add a final summary.
    Print a short report that includes:
    - number of `.srt` files found
    - number converted successfully
    - number failed
    - destination directory path

## Testing Plan

### Smoke tests

- test suite runs under `pytest`
- CI workflow executes tests on push and pull request

### Functional tests

Add tests for:

1. Acceptance test: `tests/input` produces output matching the fixture in `tests/expected`.
2. UTF-8 without BOM input becomes UTF-8 with BOM in the output file.
3. UTF-8 with BOM input remains readable and valid after conversion.
4. `cp1252` input is converted correctly.
5. Non-`.srt` files in the input directory are ignored.
6. Non-existent input directory returns an error.
7. Empty input directory is handled as expected.
8. A failing file does not prevent other files from being processed.

### Test strategy

- Use `pytest`
- Use temporary files and directories
- Assert both file contents and file bytes when checking BOM behavior
- Keep tests at the CLI boundary where practical
- Verify output filenames and output directory creation
- Treat `tests/input` and `tests/expected` as the primary acceptance fixtures

## Milestones

### Milestone 1

Create the CLI skeleton and input validation.

### Milestone 2

Implement directory scanning, encoding detection, and BOM output.

### Milestone 3

Add functional tests for successful batch conversion and partial-failure cases.

### Milestone 4

Confirm the GitHub Actions workflow passes with the new tests.

## Notes

- Python's `utf-8-sig` codec is the correct built-in choice for writing UTF-8 with BOM.
- `latin-1` will decode almost anything, so it should remain last in the fallback order.
- The current repository is intentionally minimal, so the first version should stay as a single-file program unless the code starts to sprawl.
- Recursive directory processing is out of scope for v1 and should be added only as an explicit follow-up.

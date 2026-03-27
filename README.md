# dx-sub

`dx-sub` is a small command-line tool for converting subtitle files from a source folder into UTF-8 with BOM in a separate output folder.

## What It Does

For each top-level `.srt` file in the input folder, the program:

- decodes the file using a fallback order of likely encodings
- converts the content to UTF-8 with BOM
- applies these character replacements:
  - `ã -> ă`
  - `Ã -> Ă` or `ă`, depending on context
  - `º -> ș`
  - `þ -> ț`
  - `Þ -> Ț` or `ț`, depending on context
  - `ª -> Ș`
- writes the converted file to the output folder using the same filename

Notes:

- only top-level `.srt` files are processed
- subdirectories are ignored
- the output directory is created if it does not exist
- if one file fails, the program continues processing the rest

## Requirements

- Python 3.14

## Run the Program

From the project root:

```powershell
.\.venv\Scripts\python.exe .\main.py .\path\to\input-folder .\path\to\output-folder
```

Example:

```powershell
.\.venv\Scripts\python.exe .\main.py .\tests\input .\out
```

## Output

On success, the program prints one line per converted file and a final summary.

If a file fails to convert, the program prints an error for that file and continues with the remaining files.

Exit codes:

- `0`: all files converted successfully
- `1`: setup failed, no `.srt` files were found, or at least one file failed

## Run the Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## Run Tests with Coverage

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=. --cov-report=term-missing
```

# join-pdfs

Consolidate PDF files by organization.

## Installation

```bash
uv tool install .
```

## Usage

```bash
join-pdfs -i <input_folder> [-o <output_folder>]
```

### Options

- `-i, --input-folder` - Path to folder containing PDF files (required)
- `-o, --output-folder` - Output folder path (default: `consolidated`)
- `--version` - Show version number

## File Naming Convention

Files must follow this naming format:

```
<integer> - <organization_name>.pdf
```

- Files with the same integer belong to the same organization
- The file with the shortest filename is the primary file
- Other files for that organization are merged into the primary file
- The organization ID is retained in the output filename
- Underscores are allowed in filenames but do not affect primary file selection

### Examples

**Input:**
```
pdfs/
├── 10 - African Vegan on a Budget.pdf
├── 10 - African Vegan on a Budget 990.pdf
├── 10 - African Vegan on a Budget TP.pdf
├── 17 - AEL Advocacy.pdf
└── 17 - AEL Advocacy 990.pdf
```

**Output:**
```
consolidated/
├── 10 - African Vegan on a Budget.pdf
└── 17 - AEL Advocacy.pdf
```

## Development

```bash
# Install dependencies
just sync

# Run tests
just test

# Lint
just lint

# Type check
just typecheck

# All checks
just all
```

## Requirements

- Python 3.14+

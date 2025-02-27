# CodeSnap
A Python tool to quickly capture a Markdown summary of source code and project structure from a folder or Git repository. It delivers:

- **File Content**: Code files in neat blocks, Markdown files as plain text.
- **Project Structure**: A tree-style overview in a Markdown code block.
- **Multi-Part Output**: Splits large summaries into manageable files if over 10,000 tokens, with instructions and structure in the first part.

## Features

- **Fast Scanning**: Explores local folders or Git repos (via shallow clone) for specified file types.
- **File Control**: Filters by extensions, skips unwanted directories or files.
- **Parallel Processing**: Uses multiprocessing with a `tqdm` progress bar for speed.
- **Customizable**: Tweak output name, extensions, exclusions, size, and token limits via flags or JSON config.
- **AI-Friendly**: Separates files with `---` dividers for easy parsing.
- **Logging**: Records actions in `codesnap.log` and console, with optional debug mode.
- **Rich Display**: Optional `rich` library for enhanced console output.
- **Test Mode**: Preview project structure with `--test`.

## Requirements

- Python 3.6+
- Required: `tqdm` (progress bar)
- Optional: `rich` (console styling)

Install:
```bash
pip install tqdm rich
```

## Usage

Snap a local folder or Git repo with ease.

### Local Folder
```bash
python codesnap.py /path/to/project
```

### Git Repository
Clone and summarize:
```bash
python codesnap.py --repo https://github.com/username/repo.git
```

### Options

- **folder**: Path to scan (optional, ignored with `--repo`).
- `-o, --output`: Output file base name (default: `codesnap`).
- `-e, --extensions`: File extensions to include (e.g., `.py .js`).
- `-x, --exclude`: Directories to skip (adds to defaults: `node_modules`, `.git`, `__pycache__`, `.vscode`, `.github`, `mocks`).
- `-f, --exclude-files`: Files to ignore by name (e.g., `README.md .gitignore`).
- `-m, --max-size`: Max file size in MB (default: 1).
- `-t, --max-tokens`: Max tokens per file (default: 10,000).
- `-c, --config`: JSON config file path.
- `-r, --repo`: Git repo URL to clone and scan.
- `-n, --no-subfolders`: Limit scan to root folder.
- `--test`: Display project structure and exit.
- `--debug`: Enable detailed logging.

## Customization

### Command-Line Example
Skip subfolders and specific files:
```bash
python codesnap.py /path/to/project --no-subfolders -f README.md -e .py .md
```

### Optional Config File
Create a `config.json` (optional):
```json
{
  "output": "my_snap",
  "extensions": [".py", ".md"],
  "exclude": ["tests"],
  "exclude_files": ["LICENSE"],
  "max_size": 2,
  "max_tokens": 5000
}
```
Run with:
```bash
python codesnap.py --repo https://github.com/username/repo.git --config config.json
```
Or use flags directly without a config file.

## How It Works

1. **Scan**: Grabs files from a folder or cloned repo, filtering by extensions and exclusions.
2. **Process**: Formats file contents—Markdown as text, others in code blocks—within size limits.
3. **Structure**: Builds a project tree, using the repo name if provided.
4. **Split**: Divides output into parts if over the token limit, with `---` separators.
5. **Save**: Creates Markdown files with AI-ready instructions.

## License

MIT License

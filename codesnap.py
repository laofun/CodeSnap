import os
import sys
import argparse
import logging
import json
import subprocess
import shutil
from datetime import datetime
from multiprocessing import Pool
from tqdm import tqdm

try:
    from rich.console import Console
except ImportError:
    Console = None

def setup_logging(log_file='codesnap.log'):
    """Configure logging to console and file."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handlers = [logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)]
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def read_file_content(file_path, max_size_mb=10):
    """Read file content if within size limit."""
    try:
        size = os.path.getsize(file_path) / (1024 * 1024)
        if size > max_size_mb:
            return f"File too large ({size:.2f}MB exceeds {max_size_mb}MB limit)"
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (OSError, Exception) as e:
        return f"Error reading file: {e}"

def process_file(args):
    """Process a single file and return formatted content."""
    file_path, folder_path, code_exts, max_size_mb = args
    file_name = os.path.basename(file_path)
    file_relative_path = os.path.relpath(file_path, folder_path)
    
    if any(file_name.lower().endswith(ext) for ext in code_exts):
        content = read_file_content(file_path, max_size_mb)
        ext = file_name.split('.')[-1].lower()
        separator = "---\n"
        if ext == 'md':
            return f"{separator}### File: {file_relative_path}\n\n{content}\n{separator}"
        return f"{separator}### File: {file_relative_path}\n```{ext}\n{content}\n```\n{separator}"
    return ""

def generate_project_structure(folder_path, exclude_dirs, repo_name=None):
    """Generate a tree-like structure of the project."""
    def inner_tree(path, prefix=""):
        lines = []
        try:
            entries = sorted(os.scandir(path), key=lambda e: e.name)
            entries = [e for e in entries if e.name not in exclude_dirs]
        except PermissionError:
            return [prefix + "└── [Permission Denied]"]
        for idx, entry in enumerate(entries):
            is_last = idx == len(entries) - 1
            connector = "└── " if is_last else "├── "
            line = prefix + connector + entry.name
            if entry.is_symlink():
                try:
                    line += " -> " + os.readlink(entry.path)
                except Exception:
                    line += " -> [Invalid Symlink]"
            lines.append(line)
            if entry.is_dir(follow_symlinks=False):
                sub_prefix = "    " if is_last else "│   "
                lines.extend(inner_tree(entry.path, prefix + sub_prefix))
        return lines

    root_name = repo_name if repo_name else os.path.basename(os.path.abspath(folder_path))
    return "\n".join([root_name] + inner_tree(folder_path))

def load_config(config_file):
    """Load configuration from a JSON file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {}

def approximate_token_count(text):
    """Estimate token count, assuming 1 token ≈ 4 characters."""
    return len(text) // 4

def collect_files_to_process(folder_path, exclude_dirs, exclude_files, code_exts, max_size_mb, logger, debug=False, scan_subfolders=True):
    """Collect files to process, excluding specified directories and files."""
    files_to_process = []
    try:
        for root, dirs, files in os.walk(folder_path, topdown=True):
            relative_path = os.path.relpath(root, folder_path)
            path_parts = relative_path.split(os.sep) if relative_path != "." else []
            
            if any(part in exclude_dirs for part in path_parts):
                dirs[:] = []
                logger.info(f"Excluded directory: {root} due to matching {exclude_dirs}")
                continue
            
            if not scan_subfolders and root != folder_path:
                break
            
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_relative_path = os.path.relpath(file_path, folder_path)
                file_path_parts = file_relative_path.split(os.sep)
                
                if any(part in exclude_dirs for part in file_path_parts) or file in exclude_files:
                    if debug:
                        logger.debug(f"Excluded file: {file_path} due to {exclude_dirs if any(part in exclude_dirs for part in file_path_parts) else exclude_files}")
                    continue
                
                if debug:
                    logger.debug(f"Adding file to process: {file_path}")
                files_to_process.append((file_path, folder_path, code_exts, max_size_mb))
    except Exception as e:
        logger.error(f"Error walking through directory {folder_path}: {e}")
    return files_to_process

def process_files_parallel(files_to_process, logger, debug=False):
    """Process files in parallel using multiprocessing Pool."""
    if not files_to_process:
        logger.warning("No files to process after filtering.")
        return []
    
    logger.info(f"Total files to process: {len(files_to_process)}")
    with Pool() as pool:
        return [r for r in tqdm(pool.imap(process_file, files_to_process), total=len(files_to_process), desc="Processing files") if r]

def split_and_write_parts(folder_path, results, output_base, max_tokens, repo_url, project_structure, logger, debug=False, repo_name=None):
    """Split content into parts and write to Markdown files."""
    prompt = (
        "# Instructions for AI\n\n"
        "This file summarizes a project's source code and structure for analysis. Please:\n"
        "1. Parse each file's content, marked by `---` separators, using paths under `### File:` headings.\n"
        "2. Examine the `Project Structure` tree (in part 1) to map directories and files.\n"
        "3. Identify relationships between files (e.g., imports, dependencies) and their roles in the project.\n"
        "4. Wait until all parts (e.g., `codesnap_part_X.md`) are collected before proceeding.\n"
        "5. Prepare to explain functionality, suggest optimizations, or flag issues (e.g., unread files due to size limits).\n\n"
        "Start processing only when all parts are available. Focus on code logic and project organization!\n"
    )
    
    parts = []
    current_content = ""
    for content in results:
        if approximate_token_count(current_content + content) > max_tokens and current_content:
            parts.append(current_content)
            current_content = ""
        current_content += content
    if current_content:
        parts.append(current_content)
    
    if not parts:
        logger.warning("No content to write after processing.")
        return
    
    for part_index, part_content in enumerate(parts):
        part_num = part_index + 1
        out_file = f"{output_base}_part_{part_num}.md"
        with open(out_file, 'w', encoding='utf-8') as f:
            folder_display_name = repo_name if repo_name else os.path.basename(folder_path)
            if part_index == 0:
                f.write(f"{prompt}\n# Code Summary (Part {part_num} of {len(parts)})\n"
                        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Folder: /{folder_display_name}\n")
                if repo_url:
                    f.write(f"Repository: {repo_url}\n")
                f.write(f"\n## Project Structure\n\n```\n{project_structure}\n```\n\n")
            else:
                f.write(f"# Code Summary (Part {part_num} of {len(parts)}) - Continued\n"
                        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Folder: /{folder_display_name}\n")
                if repo_url:
                    f.write(f"Repository: {repo_url}\n")
                f.write("\n")
            f.write(part_content)
        logger.info(f"Created file {out_file}")

def scan_folder_to_markdown(folder_path, output_base="codesnap", extensions=None, exclude_dirs=None,
                            exclude_files=None, max_size_mb=1, max_tokens=10000, repo_url=None,
                            debug=False, scan_subfolders=True, repo_name=None):
    """Scan folder, process files, and generate Markdown summary."""
    logger = logging.getLogger(__name__)
    exclude_dirs = exclude_dirs or []
    exclude_files = exclude_files or []
    code_exts = extensions or []
    
    if not code_exts:
        logger.warning("No extensions specified; no files will be processed.")
        return
    
    logger.info(f"Final exclude_dirs: {exclude_dirs}")
    if debug:
        logger.debug(f"Extensions: {code_exts}")
        logger.debug(f"Exclude files: {exclude_files}")
        logger.debug(f"Scan subfolders: {scan_subfolders}")
    
    project_structure = generate_project_structure(folder_path, exclude_dirs, repo_name)
    if Console:
        console = Console()
        console.print("[bold green]Project Structure:[/bold green]")
        console.print(f"```\n{project_structure}\n```")
    
    files_to_process = collect_files_to_process(folder_path, exclude_dirs, exclude_files, code_exts, max_size_mb, logger, debug, scan_subfolders)
    if not files_to_process:
        return
    
    results = process_files_parallel(files_to_process, logger, debug)
    if not results:
        return
    
    split_and_write_parts(folder_path, results, output_base, max_tokens, repo_url, project_structure, logger, debug, repo_name)

def clone_git_repo(repo_url):
    """Clone a Git repo to a temporary directory with shallow clone."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, "git_repo_temp")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    try:
        subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], check=True)
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return None

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Scan a folder or Git repository and generate a Markdown summary.")
    parser.add_argument("folder", nargs="?", help="Path to the folder to scan (ignored if --repo is provided)")
    parser.add_argument("-o", "--output", default="codesnap", help="Base name for output Markdown files")
    parser.add_argument("-e", "--extensions", nargs="+", help="File extensions to scan (e.g., .py .js)")
    parser.add_argument("-x", "--exclude", nargs="+", help="Directories to exclude (added to defaults)")
    parser.add_argument("-f", "--exclude-files", nargs="+", help="Files to exclude by name (e.g., README.md)")
    parser.add_argument("-m", "--max-size", type=float, default=1, help="Max file size to process (MB)")
    parser.add_argument("-t", "--max-tokens", type=int, default=10000, help="Max token count per output file")
    parser.add_argument("-c", "--config", help="Path to JSON config file")
    parser.add_argument("-r", "--repo", help="URL of the Git repository to scan")
    parser.add_argument("-n", "--no-subfolders", action="store_true", help="Disable scanning of subfolders")
    parser.add_argument("--test", action="store_true", help="Run unit tests and exit")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    default_excludes = ['node_modules', '.git', '__pycache__', '.vscode', '.github', 'mocks']
    exclude_dirs = list(set(default_excludes + (args.exclude or [])))
    default_extensions = ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.ts', '.go', '.md']
    extensions = list(set(default_extensions + (args.extensions or [])))
    exclude_files = args.exclude_files or []

    if args.config:
        config = load_config(args.config)
        for key, value in config.items():
            setattr(args, key, value)

    folder_to_scan = None
    temp_dir = None
    repo_name = None
    if args.repo:
        temp_dir = clone_git_repo(args.repo)
        if not temp_dir:
            sys.exit(1)
        folder_to_scan = temp_dir
        repo_name = args.repo.rstrip('/').split('/')[-1].replace('.git', '')
    else:
        if not args.folder or not os.path.isdir(args.folder):
            print(f"Folder '{args.folder}' does not exist!")
            sys.exit(1)
        folder_to_scan = args.folder
        repo_name = os.path.basename(folder_to_scan)

    if args.test:
        structure = generate_project_structure(folder_to_scan, exclude_dirs, repo_name)
        print("Unit Test - Project Structure:\n", structure)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        sys.exit(0)

    setup_logging()
    scan_folder_to_markdown(
        folder_path=folder_to_scan,
        output_base=args.output,
        extensions=extensions,
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        max_size_mb=args.max_size,
        max_tokens=args.max_tokens,
        repo_url=args.repo,
        debug=args.debug,
        scan_subfolders=not args.no_subfolders,
        repo_name=repo_name
    )

    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
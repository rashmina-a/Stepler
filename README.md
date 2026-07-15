# Stepler

Stepler is a simple Python‑based package manager that works with a custom archive format **`.step`**. It provides basic commands to install, remove, list, and search for packages.

## Features (initial)
- **Custom `.step` format** – a tar.gz archive containing a `metadata.json` file and the package files.
- `install` – extracts a `.step` archive to `~/.stepler/packages/<name>-<version>`.
- `remove` – deletes an installed package.
- `list` – shows all installed packages.
- `search` – looks for `.step` files in a local repository directory.

## Quick start
```bash
# Install the package manager (editable mode)
pip install -e .

# Create a .step package (example)
#   - Create a directory `myapp/` with your files
#   - Create a `metadata.json` inside the archive:
#       {"name": "myapp", "version": "1.0.0", "dependencies": []}
#   - Package it:
#       tar -czf myapp-1.0.0.step -C myapp . metadata.json

# Install a package
stepler install ./myapp-1.0.0.step

# List installed packages
stepler list

# Remove a package
stepler remove myapp 1.0.0

# Search a local repository for packages matching a name
stepler search myapp --repo ./repo
```

## Development
```bash
# Run tests (if added later)
pytest
```

## Quick start
```bash
# Install the package manager (editable mode)
pip install -e .

# Create a .step package (example)
#   1. Prepare a directory with your files, e.g. myapp/
mkdir -p myapp
echo "print('Hello from myapp')" > myapp/main.py

#   2. Add a `metadata.json` file. You can also specify optional fields:
#      * `"entrypoint"`: the script to execute when the package is launched
#        globally (relative to the package root).
#      * `"interpreter"`: the command used to run the entrypoint (e.g.
#        "python3", "node", "bash"). If omitted, `python3` is assumed for
#        backward compatibility.
cat > myapp/metadata.json <<'EOF'
{
	"name": "myapp",
	"version": "1.0.0",
	"dependencies": [],
	"entrypoint": "main.py"
}
EOF

#   3. Package it as a .step (tar.gz) archive:
tar -czf myapp-1.0.0.step -C myapp .

# Install the package
stepler install ./myapp-1.0.0.step

# After installation a wrapper script is created in `~/.local/bin`
# (make sure this directory is on your PATH). You can now run the app
# directly:
myapp

# List installed packages
stepler list

# Remove a package
stepler remove myapp 1.0.0

# Search a local repository for packages matching a name
stepler search myapp --repo ./repo
```

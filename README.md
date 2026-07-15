# Stepler

Stepler is a lightweight Python‑based package manager that works with a custom archive format **`.step`**. It provides commands to **install**, **remove**, **list**, and **search** packages.

## Features
* **Custom `.step` format** – a `tar.gz` archive containing a `metadata.json` file and the package files.
* **Entry‑point support** – specify an executable script and interpreter in `metadata.json`.
* **Wrapper script generation** – after installation a shim is placed in `~/.local/bin` (or `$VIRTUAL_ENV/bin` when using a virtual environment) so the package can be run directly from the command line.
* **Dependency handling** – future versions will resolve dependencies listed in `metadata.json`.
* **Local repository search** – locate `.step` packages in a directory tree.

## Installation

### From source (editable mode)
```bash
# Clone the repository and install in editable mode
git clone https://github.com/yourname/stepler.git
cd stepler
pip install -e .
```

### From PyPI (once published)
```bash
pip install stepler
```

> **Note**: After installation ensure that the directory containing the wrapper scripts is on your `PATH`. For a typical user install this is `~/.local/bin`. When using a virtual environment the scripts are placed in `$VIRTUAL_ENV/bin` which is automatically added to `PATH` when the environment is activated.

## Creating a `.step` package

1. **Prepare a package directory**
	```bash
	mkdir -p myapp
	echo "print('Hello from myapp')" > myapp/main.py
	```

2. **Add a `metadata.json` file** – include at least `name` and `version`. Optional fields:
	* `entrypoint` – script to run when the package is executed.
	* `interpreter` – command used to run the entrypoint (default `python3`).
	```json
	{
		 "name": "myapp",
		 "version": "1.0.0",
		 "dependencies": [],
		 "entrypoint": "main.py",
		 "interpreter": "python3"
	}
	```
	Save this as `myapp/metadata.json`.

3. **Package the directory**
	```bash
	tar -czf myapp-1.0.0.step -C myapp .
	```

## Using Stepler (CLI)

### Install a package
```bash
stepler install ./myapp-1.0.0.step
```

### List installed packages
```bash
stepler list
```

### Remove a package
```bash
stepler remove myapp 1.0.0
```

### Search a local repository
```bash
stepler search myapp --repo ./repo
```

## Troubleshooting

### Python virtual environments
* **Activate the environment** before installing or using Stepler:
  ```bash
  python -m venv .venv
  source .venv/bin/activate   # on Linux/macOS
  # or
  .venv\Scripts\activate.bat # on Windows
  ```
* **Installation inside a venv** – run `pip install -e .` while the venv is active. The wrapper script will be placed in `$VIRTUAL_ENV/bin` and will be available as soon as the environment is activated.
* **PATH issues** – if `stepler` or the installed package command is not found, ensure the appropriate `bin` directory is on your `PATH`:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"   # for user installs
  export PATH="$VIRTUAL_ENV/bin:$PATH"   # when using a venv
  ```
* **Permission errors** – when installing globally you may need `sudo` or use a virtual environment to avoid permission problems.

## Development

Run the test suite (once tests are added):
```bash
pytest
```

Feel free to contribute improvements or report issues on the project repository.

---
*Happy stepping!*

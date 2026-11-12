# Autotrainer - Core

This is the base module for functions and objects that used across most or all modules and applications.

Major Elements
* Observable object implementation
* Common Protocols used to bridge different modules
* General pub-sub notification hub implementation
* Event manager for structured application event recording
* Enhanced multiprocessing shared array behavior
* General "project" and animal subject data and management
* Fundamental data analysis operations that may be used ro replay/reprocess data, not just in live capture
* System configuration reading and persistence
* Misc utilities
  * Performance monitoring wrappers
  * Queue extensions

### Testing
Development environments are managed with [uv](https://docs.astral.sh/uv/). Python 3.8 is pinned in `.python-version`,
and `uv.lock` pins the development environment. Set up once, from the repository root:

```bash
uv python install 3.8
uv sync --extra test
```

Then run the tests, which use core's own pytest configuration in `pyproject.toml`:

```bash
uv run pytest
```

After changing dependencies in `pyproject.toml`, refresh the lock file with `uv lock`. The lock file applies only to this
repository's development environment: anything that installs `auto-trainer-core` as a package, with pip, uv or inside a
conda environment, uses the version ranges in `pyproject.toml`.

Pull requests to `main` run the same tests in CI, against a non-editable install of core, so they also exercise the
metadata that gets published.

Packages built on core reuse its test support by loading `autotrainer.core.testing` as a pytest plugin, either with
`-p autotrainer.core.testing` in `addopts` or with `pytest_plugins = ["autotrainer.core.testing"]` in a top-level
`conftest.py`, and by importing its helpers (`AlmostEqualFloat`, `increase_simulate_perf_now`, `has_api_event_kind`,
...). Never import its fixtures: a fixture imported into another module is registered a second time.

### Releases
Versions come from git tags through `setuptools_scm`: a build of a commit tagged `vX.Y.Z` is version `X.Y.Z`, and
builds between tags get development versions.

Pushing a `vX.Y.Z` tag runs the tests, builds core and publishes it to PyPI. The publish job fails when the built
version differs from the tag, and skips a version PyPI already has. Pushes to the `workflows-edit` branch publish a
development build to TestPyPI instead.

The first release from this repository is `v2.1.0`; `2.0.5` on PyPI predates the move. The `core-v2.0.2` to
`core-v2.0.4` tags come from the monorepo's history and are not used for versioning.

### Code Guidelines

_Note that the original code came from a different structure is not yet fully consistent.  The following
guidelines are in place for future additions and changes to help with and improve consistency._

* Style generally follows PEP8.  This is the default in most editors or lint tools.
* Core is a namespace package: `autotrainer.core` shares the `autotrainer` namespace with the other Autotrainer packages, so `src/autotrainer/` has no `__init__.py`.
* Code should be as platform-agnostic as possible despite having a current target (Jetson->Ubuntu 20.04).
  * Fallback support does not need to match the target platform behavior where is can not (e.g. CUDA), but allow the code to run as correctly as possible.
  * This is primarily for automated testing in other environments such as GitHub Actions.
  * Secondarily, it allows for development off-hardware when not available or not practical.
* Core should provide a well-defined interface to the rest of the system and not expose implementation details unless absolutely necessary.
  * There are multiple packages, scripts and applications that use the functionality in core.
  * Exposure to implementation details has a cascading effect of requiring more frequent updates to consumers that generally don't care.
* Public interfaces generally define a Protocol [1] for objects that fall into certain categories
  * Objects that have multiple implementations, such as the different hardware implementations
  * Objects that are likely to be mocked in automated testing.
    * Particularly needed for environments where hardware, inference models, or other unique elements are not present.  One environment is GitHub Actions that run automated testing for Pull Requests.
* `pip` and `pyproject.toml` are currently used.
  * `pyproject.toml` should be kept up to date.
* Versions in `pyproject.toml` generally need team-wide notification to update.
  * There are several dependencies whose version traces back to the specific environment that is currently required on the Jetson.
* Docstrings should be in the "Google" style.
  * A lot of existing docstrings are in "reStructuredText" (Sphinx) style, which may be confusing.
  * Documentation generation can be assumed to be using `mkdocs`.
    * Note: there is no place configured to privately publish the documentation at this time, so core has not been initialized with a `mkdocs` project yet.  This will change.

[1] This is primarily to enhance static type checking and code analysis in general.  Protocols were chosen
over Python ABCs or other options to allow as much flexibility as possible or needed in the implementation.

### Future Work
The Project class and functionality is largely geared towards the creation of projects, knowing where to save
data and created those folders and files where necessary.  It should be improved to make it easier to use as 
a reader for tools that need to be aware of those folders and files, but never create them.  This will be used
by the management console to read information without needed to burden the acquisition application directly.

System configuration files have been updated to use YAML tags for typing and with a new structure that better
aligns to the subsystems and their properties.  There is a still a step to separate a) device values that
are unlikely to change over time (e.g., hardware ports), b) values related to application that can change
between sessions, but would not be considered "training" variables and c) training variables that users
are likely to change regularly and in some cases may be changed by hand.

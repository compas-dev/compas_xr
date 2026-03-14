# Installation

This chapter provides a step-by-step guide for installing `compas_xr` on your system.
We highly recommend using [uv](https://docs.astral.sh/uv/) for managing
your Python environment and dependencies, as it is significantly faster and
more reliable. Alternatively, you can simply use standard `pip`.

## Install uv

If you do not have `uv` installed, follow the instructions on their website or run:

=== "Mac/Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

## Create a virtual environment

It is best practice to install `compas_xr` in a virtual environment.
Navigate to your project directory and run:

```bash
uv venv
```

This creates a virtual environment in `.venv`. Activate it with:

=== "Mac/Linux"

    ```bash
    source .venv/bin/activate
    ```

=== "Windows"

    ```powershell
    .venv\Scripts\activate
    ```

## Install compas_xr

With your virtual environment activated, install `compas_xr`:

```bash
uv pip install compas_xr
```

## Verify installation

Verify that `compas_xr` is available:

```bash
python -c "import compas_xr; print(compas_xr.__version__)"
```

If the version number is printed, the installation is complete.

## Install for Rhino

COMPAS XR is compatible with Rhino 8 and later versions. To use it, simply add the requirement header to the top of your script in the Rhino 8 Script Editor:

```python
# r: compas_xr
```

## COMPAS XR Unity - Phone Based AR Application

This chapter provides a step-by-step guide for installing compas_xr_unity on your device. The use and installation of
the application is supported by both Android and iOS devices. If you would like to install the application without
functionality or code modifications, the Android .apk file and iOS Xcode build can be found [here](https://nextcloud.ethz.ch/s/QyGgN84yx3LBfNs).

However, if you would like to modify any application functionalities or access the entire code base for the application,
it can be found and cloned from our [repository](https://github.com/compas-dev/compas_xr).

Additionally, both Android and iOS installation procedures can be found in the [Release Procedures](userguide.md#step-6-release-procedures) chapter of the documentation.

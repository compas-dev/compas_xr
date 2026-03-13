import os
import sys

# On macOS/Linux, pythonnet defaults to Mono, but we want to use .NET Core (dotnet)
# if available, especially for Rhino 8+ development.
if sys.platform != "win32":
    os.environ["PYTHONNET_RUNTIME"] = "coreclr"

from compas_invocations2 import build
from compas_invocations2 import docs
from compas_invocations2 import grasshopper
from compas_invocations2 import style
from compas_invocations2 import tests
from invoke import Collection

ns = Collection(
    docs.help,
    style.check,
    style.lint,
    style.format,
    docs.docs,
    docs.linkcheck,
    tests.test,
    tests.testdocs,
    build.prepare_changelog,
    build.clean,
    build.release,
    build.build_cpython_ghuser_components,
    grasshopper.yakerize,
    grasshopper.publish_yak,
)
ns.configure(
    {
        "base_folder": os.path.dirname(__file__),
        "ghuser_cpython": {
            "source_dir": "src/compas_xr/ghpython/components",
            "target_dir": "src/compas_xr/ghpython/components/ghuser",
        },
    }
)

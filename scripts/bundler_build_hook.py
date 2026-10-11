import os
import pathlib
import shutil
import subprocess

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class RollupBuildHook(BuildHookInterface):
    """Build the Fontra web client with npm.

    Environment switches for packagers:

    FONTRA_SKIP_BUNDLE=1   Do not run npm at all. src/fontra/client/ must
                           already contain the built client (for example
                           from a release sdist, or a previous bundle run).
    FONTRA_NPM_OFFLINE=1   Use `npm ci --offline`, with node_modules or the
                           npm cache already populated (Flatpak/RPM builds).
    """

    def initialize(self, version, build_data):
        root = pathlib.Path(__file__).resolve().parent.parent
        client = root / "src" / "fontra" / "client"

        if os.environ.get("FONTRA_SKIP_BUNDLE") == "1":
            if not client.is_dir() or not any(client.iterdir()):
                raise RuntimeError(
                    "FONTRA_SKIP_BUNDLE=1 but src/fontra/client/ is missing or "
                    "empty: build the client first (npm ci && npm run bundle)"
                )
            return

        thirdParty = client / "third-party"
        if thirdParty.exists():
            shutil.rmtree(thirdParty)

        npmCi = ["npm", "ci"]
        if os.environ.get("FONTRA_NPM_OFFLINE") == "1":
            npmCi.append("--offline")

        subprocess.check_call(npmCi, cwd=root)
        subprocess.check_call(["npm", "run", "bundle"], cwd=root)

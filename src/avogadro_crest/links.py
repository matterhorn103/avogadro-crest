# SPDX-FileCopyrightText: 2026 Matthew Milner <matterhorn103@proton.me>
# SPDX-License-Identifier: BSD-3-Clause


import logging
import platform
import subprocess
import webbrowser

import easyxtb


logger = logging.getLogger(__name__)


def open_calcs_dir(avo_input: dict) -> dict:
    # Have to detect os
    if platform.system() == "Windows":
        subprocess.run(["explorer.exe", easyxtb.CALCS_DIR])
    elif platform.system() == "Darwin":
        subprocess.run(["open", easyxtb.CALCS_DIR])
    else:
        subprocess.run(["xdg-open", easyxtb.CALCS_DIR])
    
    return {
        "moleculeFormat": "cjson",
        "cjson": avo_input["cjson"],
    }


def open_crest_docs(avo_input: dict) -> dict:
    crest_docs_url = "https://crest-lab.github.io/crest-docs/"
    logger.debug(f"Opening the CREST docs website at {crest_docs_url}")
    webbrowser.open(crest_docs_url)

    return {
        "message": "The CREST documentation should have opened in your browser.",
        "moleculeFormat": "cjson",
        "cjson": avo_input["cjson"],
    }


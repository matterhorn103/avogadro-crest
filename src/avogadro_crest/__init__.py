# SPDX-FileCopyrightText: 2026 Matthew Milner <matterhorn103@proton.me>
# SPDX-License-Identifier: BSD-3-Clause

"""Package initialization and entry point for the avogadro-crest Avogadro plugin."""

import argparse
import json
import logging
import sys
import traceback

import easyxtb

# Make sure stdout stream is always Unicode, as Avogadro expects
sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger(__name__)


# Piggyback the easyxtb config and add some extra plugin-specific things
plugin_defaults = {
    "energy_units": "kJ/mol",
    "xtb_opts": {},
    "crest_opts": {},
}
for k, v in plugin_defaults.items():
    if k not in easyxtb.config:
        easyxtb.config[k] = v


def run(
    avo_input: dict,
    feature: str,
    **args,  # Anything else
) -> dict:
    """Run the function corresponding to the selected feature."""
    match feature:
        case "conformers":
            from .conformers import conformers, get_conformers_options
            if args["user_options"]:
                output = {"userOptions": get_conformers_options()}
            else:
                output = conformers(avo_input)
        case "tautomers":
            from .tautomers import tautomerize
            output = tautomerize(avo_input)
        case "protonate":
            from .tautomers import protonate
            output = protonate(avo_input)
        case "deprotonate":
            from .tautomers import deprotonate
            output = deprotonate(avo_input)
        case "solvate":
            from .solvation import solvate, get_solvation_options
            if args["user_options"]:
                output = {"userOptions": get_solvation_options()}
            else:
                output = solvate(avo_input)
        case "open":
            from .links import open_calcs_dir
            output = open_calcs_dir(avo_input)
        case "docs":
            from .links import open_crest_docs
            output = open_crest_docs(avo_input)
        case "config":
            from .config import get_config_options, update_config
            if args["user_options"]:
                output = {"userOptions": get_config_options()}
            else:
                output = update_config(avo_input)
        case _:
            output = {"error": "The runtype was not recognized!"}

    # Save output to make debugging easier
    with open(easyxtb.TEMP_DIR / "output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    
    return output


def main():
    """Entry point for the plugin."""
    logger.debug("CLI input: " + " ".join(sys.argv))
    parser = argparse.ArgumentParser()
    # It is planned to offer multiple feature types in future
    # When the args for each feature differ, we have to delegate to subparsers
    subparsers = parser.add_subparsers(dest="feature")

    # Each feature gets its own subparser, where the `title` of each
    # subparser must match the `identifier` for the feature
    # We then add the arguments specific to each feature to its subparser

    # We can also define common shared arguments and have all feature parsers
    # inherit them without having to define them for every feature separately
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lang", nargs="?", default="en")
    common.add_argument("--debug", action="store_true")

    conformers_parser = subparsers.add_parser("conformers", parents=[common])
    conformers_parser.add_argument("--user-options", action="store_true")
    subparsers.add_parser("tautomers", parents=[common])
    subparsers.add_parser("protonate", parents=[common])
    subparsers.add_parser("deprotonate", parents=[common])
    subparsers.add_parser("solvate", parents=[common])
    subparsers.add_parser("open", parents=[common])
    config_parser = subparsers.add_parser("config", parents=[common])
    config_parser.add_argument("--user-options", action="store_true")
    subparsers.add_parser("docs", parents=[common])

    args = parser.parse_args()
    logger.debug(f"Parsed args: {str(args)}")

    # Read (initial) input from Avogadro
    avo_input = json.loads(sys.stdin.read())
    logger.debug(f"The following JSON object was received from Avogadro: {avo_input}")

    try:
        output = run(avo_input, **vars(args))
    except Exception as e:
        limit = None if args.debug else 3
        output = {"error": "".join(traceback.format_exception(e, limit=limit))}
        print(json.dumps(output))
        print()
        raise e

    print(json.dumps(output))
    logger.debug(f"The following JSON object was passed back to Avogadro: {output}")

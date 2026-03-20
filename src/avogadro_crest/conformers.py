# SPDX-FileCopyrightText: 2026 Matthew Milner <matterhorn103@proton.me>
# SPDX-License-Identifier: BSD-3-Clause

import logging

import easyxtb


logger = logging.getLogger(__name__)


def cleanup_after_opt(cjson: dict) -> dict:
    """Returns a cjson dict minus any data that is no longer meaningful after
    a geometry change."""

    cleaned = cjson

    # Frequencies and orbitals
    for field in ["vibrations", "basisSet", "orbitals", "cube"]:
        if field in cleaned:
            del cleaned[field]
    # Atomic charges
    if "formalCharges" in cleaned["atoms"]:
        del cleaned["atoms"]["formalCharges"]
    if "partialCharges" in cleaned["atoms"]:
        del cleaned["atoms"]["partialCharges"]

    return cleaned


def get_conformers_options() -> dict:
    """Dynamically generate the conformers dialog and populate its options.
    
    In fact, the only dynamic part is the energy units used."""

    user_options = {
        "ewin": {
            "order": 7.0,
            "label": "Keep all conformers within",
            "suffix": " kJ/mol",
            "type": "integer",
            "default": 25,
            "minimum": 1,
            "maximum": 1000,
        },
        "hess": {
            "order": 8.0,
            "label": "Calculate frequencies for conformers\nand re-weight ensemble on free energies",
            "type": "boolean",
            "default": False,
        },
        "help": {
            "order": 9.0,
            "label": "For help see",
            "type": "text",
            "default": "https://crest-lab.github.io/crest-docs/",
        },
    }
    # Display energy in kcal if user has insisted on it
    if easyxtb.config["energy_units"] == "kcal/mol":
        user_options["ewin"]["default"] = 6
        user_options["ewin"]["suffix"] = " kcal/mol"
    
    return user_options


def conformers(avo_input: dict) -> dict:
    cjson = avo_input["cjson"]
    geom = easyxtb.Geometry.from_cjson(cjson)

    # crest takes energies in kcal so convert if provided in kJ (default)
    if easyxtb.config["energy_units"] == "kJ/mol":
        ewin_kcal = avo_input["options"]["ewin"] / 4.184
    else:
        ewin_kcal = avo_input["options"]["ewin"]

    # Run calculation
    calc = easyxtb.Calculation.v3(
        geom,
        ewin=ewin_kcal,
        hess=avo_input["options"]["hess"],
        options=easyxtb.config["crest_opts"],
    )
    calc.run()

    best_cjson = calc.output_geometry.to_cjson()
    conformer_cjson = easyxtb.convert.conf_to_cjson(calc.conformers)

    # Get energy for Avogadro
    energies = easyxtb.convert.convert_energy(calc.energy, "hartree")

    # Catch errors in crest execution
    # TODO
    
    # Update CJSON
    # Remove anything that is now unphysical after the optimization
    cjson = cleanup_after_opt(cjson)

    # Add data from calculation
    cjson["atoms"]["coords"] = best_cjson["atoms"]["coords"]
    cjson["properties"]["totalEnergy"] = round(energies["eV"], 7)
    cjson["atoms"]["coords"]["3dSets"] = conformer_cjson["atoms"]["coords"]["3dSets"]
    cjson["properties"]["energies"] = conformer_cjson["properties"]["energies"]

    # Format output appropriately for Avogadro
    output = {"moleculeFormat": "cjson", "cjson": cjson}

    return output

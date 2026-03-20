# SPDX-FileCopyrightText: 2026 Matthew Milner <matterhorn103@proton.me>
# SPDX-License-Identifier: BSD-3-Clause

from copy import deepcopy

import easyxtb


def cleanup_after_taut(cjson: dict) -> dict:
    """Returns a copy of a cjson dict minus any data that is no longer meaningful after
    a CREST tautomerization/protonation/deprotonation procedure.
    
    Essentially gives an empty cjson, with only the total charge and spin retained.
    """

    output = deepcopy(easyxtb.convert.empty_cjson)
    output["properties"]["totalCharge"] = cjson["properties"]["totalCharge"]
    output["properties"]["totalSpinMultiplicity"] = cjson["properties"]["totalSpinMultiplicity"]

    return output


def post_calc_processing(original_cjson: dict, calc: easyxtb.Calculation) -> dict:
    """Do the processing common to all tautomerization and (de-)protonation calculations."""

    best_cjson = calc.output_geometry.to_cjson()
    tautomer_cjson = easyxtb.convert.taut_to_cjson(calc.tautomers)

    # Get energy for Avogadro
    energies = easyxtb.convert.convert_energy(calc.energy, "hartree")

    # Remove anything that is now unphysical after the optimization
    cjson = cleanup_after_taut(original_cjson)

    # Add data from calculation
    cjson["atoms"] = best_cjson["atoms"]
    cjson["properties"]["totalEnergy"] = round(energies["eV"], 7)
    cjson["atoms"]["coords"]["3dSets"] = tautomer_cjson["atoms"]["coords"]["3dSets"]
    cjson["properties"]["energies"] = tautomer_cjson["properties"]["energies"]

    # Format output appropriately for Avogadro
    output = {
        "moleculeFormat": "cjson",
        "cjson": cjson,
    }
    
    return output


def tautomerize(avo_input: dict) -> dict:
    cjson = avo_input["cjson"]
    geom = easyxtb.Geometry.from_cjson(cjson)

    # Run calculation; returns set of tautomers as well as Calculation object
    calc = easyxtb.Calculation.tautomerize(
        geom,
        options=easyxtb.config["crest_opts"],
    )
    calc.run()

    return post_calc_processing(cjson, calc)


def protonate(avo_input: dict) -> dict:
    cjson = avo_input["cjson"]
    geom = easyxtb.Geometry.from_cjson(cjson)

    # Run calculation; returns set of tautomers as well as Calculation object
    calc = easyxtb.Calculation.protonate(
        geom,
        options=easyxtb.config["crest_opts"],
    )
    calc.run()

    output = post_calc_processing(cjson, calc)

    # Make sure to adjust new charge
    output["cjson"]["properties"]["totalCharge"] += 1

    return output


def deprotonate(avo_input: dict) -> dict:
    cjson = avo_input["cjson"]
    geom = easyxtb.Geometry.from_cjson(cjson)

    # Run calculation
    calc = easyxtb.Calculation.deprotonate(
        geom,
        options=easyxtb.config["crest_opts"],
    )
    calc.run()

    output = post_calc_processing(cjson, calc)

    # Make sure to adjust new charge
    output["cjson"]["properties"]["totalCharge"] -= 1

    return output

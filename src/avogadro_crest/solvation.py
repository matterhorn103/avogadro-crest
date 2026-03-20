# SPDX-FileCopyrightText: 2026 Matthew Milner <matterhorn103@proton.me>
# SPDX-License-Identifier: BSD-3-Clause

import logging
from copy import deepcopy

import easyxtb


logger = logging.getLogger(__name__)


def split_cjson_by_layer(cjson: dict) -> list[dict]:
    """Separate a CJSON into multiple CJSONs according to which layer atoms are in.
    
    For now drops all data except atom and bond information.
    
    All layers are assumed to contain neutral singlets, except layer 0, which is given
    the total charge and multiplicity of the original CJSON.
    """
    output = []
    for layer_index in range(max(cjson["atoms"]["layer"]) + 1):
        layer = deepcopy(easyxtb.convert.empty_cjson)
        atoms_in_layer = []
        for atom_index, atom_layer in enumerate(cjson["atoms"]["layer"]):
            if atom_layer == layer_index:
                atoms_in_layer.append(atom_index)
        for atom_index in atoms_in_layer:
            layer["atoms"]["coords"]["3d"].extend(
                cjson["atoms"]["coords"]["3d"][3*atom_index:3*(atom_index+1)]
            )
            layer["atoms"]["elements"]["number"].append(
                cjson["atoms"]["elements"]["number"][atom_index]
            )
        for bond_index, bond_order in enumerate(cjson["bonds"]["order"]):
            bond_members = (
                cjson["bonds"]["connections"]["index"][2*bond_index:2*(bond_index+1)]
            )
            if all([atom in atoms_in_layer for atom in bond_members]):
                layer["bonds"]["connections"]["index"].extend(bond_members)
                layer["bonds"]["order"].append(bond_order)
        if layer_index == 0:
            layer["properties"]["totalCharge"] = cjson["properties"]["totalCharge"]
            layer["properties"]["totalSpinMultiplicity"] = cjson["properties"]["totalSpinMultiplicity"]
        output.append(layer)
    return output


def solvate(avo_input: dict) -> dict:
    cjson = avo_input["cjson"]
    # Sort atoms based on layer
    layers = split_cjson_by_layer(cjson)

    # Adjust for difference in indexing between what the user's choice was based on 
    # (Avogadro GUI uses 1-indexing) and what we receive (CJSON uses 0-indexing)
    solute_layer = avo_input["solute_layer"] - 1
    solvent_layer = avo_input["solvent_layer"] - 1

    solute_cjson = layers[solute_layer]
    solvent_cjson = layers[solvent_layer]
    solute_geom = easyxtb.Geometry.from_cjson(solute_cjson)
    solvent_geom = easyxtb.Geometry.from_cjson(solvent_cjson)

    # Run calculation; returns new Geometry
    output_geom = easyxtb.calculate.solvate(
        solute_geom,
        solvent_geom,
        nsolv=avo_input["nsolv"],
        options=easyxtb.config["crest_opts"],
    )

    # Add solute bonding information from input CJSON
    output_cjson = output_geom.to_cjson()
    output_cjson["bonds"] = solute_cjson["bonds"]

    # Format everything appropriately for Avogadro
    output = {
        "moleculeFormat": "cjson",
        "cjson": output_cjson,
    }
    
    return output

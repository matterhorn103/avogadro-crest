`avogadro-crest` is a plugin for Avogadro 2 that provides an in-app interface to the ensemble sampling procedures provided by the CREST program.

[`crest`](https://github.com/crest-lab/crest) (Conformer–Rotamer Ensemble Sampling Tool) uses the fast [GFNn-xTB](https://github.com/grimme-lab/xtb) methods of the Grimme group in Bonn to carry out sampling procedures for several interesting applications including conformer searches, thermochemistry, and solvation.

## Related projects

An [`avogadro-xtb`](https://github.com/matterhorn103/avo_xtb) plugin is also available, providing an interface to `xtb` for the calculation of optimized geometries, vibrational frequencies, and molecular orbitals.

Both plugins are themselves only thin wrappers around the [`easyxtb`](https://github.com/matterhorn103/easyxtb) Python package, which is written and maintained as part of this project.
`easyxtb` is published on the `PyPI` repository and can be used independently of the plugin from Python as an interface to `xtb` and `crest`.

For more details on using `easyxtb` via its Python API, see [the package's documentation](https://easyxtb.readthedocs.io/en/latest/).

## Capabilities

This plugin currently provides functionality to run the following calculation types and view the results directly in Avogadro:

* conformer searches
* protonation and deprotonation screening
* explicit solvent shell generation

Note that a bug in the current version of CREST (3.0.2) means that solvation is unfortunately usually unsuccessful at this moment in time.

## Data location

The core package that provides the calculation framework (`easyxtb`) uses a central location to run its calculations, store its configuration, and save its log file.
This location is `<user data>/easyxtb`, where `<user data>` is OS-dependent:

- Windows: `$USER_HOME\AppData\Local\easyxtb`
- macOS: `~/Library/Application Support/easyxtb`
- Linux: `~/.local/share/easyxtb`

Additionally, if the environment variable `XDG_DATA_HOME` is set its value will be respected and takes precedence over the above paths (on all OSes).

Normally calculations are run in a subfolder at this location, but this can be customized in the plugin's configuration dialog.

## Disclaimer

`crest` and `xtb` are distributed by the Grimme group under the LGPL license v3.
The authors of Avogadro and `avogadro-crest` bear no responsibility for CREST or xtb or the contents of the respective repositories.
Source code for the programs is available at the repositories linked above.

## Cite

For CREST:
* P. Pracht, S. Grimme, C. Bannwarth, F. Bohle, S. Ehlert, G. Feldmann, J. Gorges, M. Müller, T. Neudecker, C. Plett, S. Spicher, P. Steinbach, P. Wesołowski, F. Zeller, *J. Chem. Phys.*, **2024**, *160*, 114110. DOI: [10.1063/5.0197592](https://doi.org/10.1063/5.0197592)
* P. Pracht, F. Bohle, S. Grimme, *Phys. Chem. Chem. Phys.*, **2020**, 22, 7169-7192. DOI: [10.1039/C9CP06869D](https://dx.doi.org/10.1039/C9CP06869D)

General reference to `xtb` and the implemented GFN methods:
* C. Bannwarth, E. Caldeweyher, S. Ehlert, A. Hansen, P. Pracht, J. Seibert, S. Spicher, S. Grimme
  *WIREs Comput. Mol. Sci.*, **2020**, 11, e01493.
  DOI: [10.1002/wcms.1493](https://doi.org/10.1002/wcms.1493)

For GFN2-xTB (default method):
* C. Bannwarth, S. Ehlert and S. Grimme., *J. Chem. Theory Comput.*, **2019**, 15, 1652-1671. DOI: [10.1021/acs.jctc.8b01176](https://dx.doi.org/10.1021/acs.jctc.8b01176)

See the xtb and CREST GitHub repositories for other citations.

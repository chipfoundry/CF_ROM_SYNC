# CF_ROM_SYNC

## Overview

CF_ROM_SYNC is the ChipFoundry catalog name for a synchronous ROM hard-macro family
on SkyWater 130 nm. The catalog lists 4K, 8K, and 32K configurations. This repository
holds the **public** customer views only: abstract layout, a blackbox Verilog stub for
top-level integration, Liberty timing when present, and a Verilog behavioral model for
functional verification when present.

Full layout, schematics, and transistor-level netlists are not part of the license
grant. ChipFoundry merges the vault GDS at tapeout. Spice simulation models are not
delivered to customers.

## Installation

Install through IPM after a GitHub release exists:

```
pip install cf-ipm
ipm install CF_ROM_SYNC
```

In the digital flow, treat the stub as a blackbox (`VERILOG_FILES_BLACKBOX`) and add
the public LEF and abstract GDS as extra views (`EXTRA_LEFS`, `EXTRA_GDS`). Use the
behavioral Verilog under `verify/beh_model/` for functional simulation, not the stub
and not spice.

Until a release URL is published, this section documents the intended customer path.

## Features

- Synchronous ROM hard macro (catalog family: 4K / 8K / 32K)
- Public blackbox Verilog stub for connecting the macro in top-level RTL
- Verilog behavioral model for functional verification (not transistor-level)
- Abstract LEF and GDS (boundary, pins, keepouts) for place-and-route
- Liberty timing models when the vendor drop includes them
- README is the customer datasheet; a PDF is not required

## Block Diagram

A block diagram is not generated from geometry. Optional figures may be placed under
`doc/` when they are cleared for customers.

## Pin Description

Pin names and directions come from the blackbox Verilog stub in `hdl/gl/`. That file
is a port list only (empty module body) so synthesis and connectivity checking can
instantiate the macro. It is not a functional model.

## Specifications

Electrical and timing numbers belong in this README and in vendor Liberty. This
repository does not invent PVT tables. Functional simulation uses the behavioral
Verilog model. Spice is not provided.

## Timing Diagram

Timing diagrams are not synthesized from stubs. Clock, reset, and enable polarity
must match the behavioral model and Liberty when those files are present in a
release.

## Tapeout History

Not silicon-proven in this ChipFoundry package version until a shuttle returns.
Foundry merge uses vault GDS, never the public abstract.

# Programming CF_ROM_SYNC

`CF_ROM_SYNC` is a 1K×8 synchronous ROM. Address `A[9:0]` selects one of
1024 bytes. `DO[7:0]` is that byte. The image is mask-programmed. The
files in `hdl/gl/` and `verify/beh_model/` do not contain your image.
`verify/beh_model/CF_ROM_SYNC_core.v` reads as all zeros.

`scripts/program_cf_rom_sync.py` checks that image and writes a simulation
model plus the wrap netlist used for integration LVS. It does not edit the
public GDS. The public layout is an abstract, so the image is not drawn
into it.

## Image file

One hex byte per address, starting at address 0. Use 1024 bytes. Blank
lines and comments (`//` or `#`) are ignored. `0x` prefixes are optional.
Several bytes may share a line.

```text
// address 0
a5
00
# address 2
ff 01
```

The example above is only the start of a file. A real image continues
through address 1023.

## Generate the models

```bash
python3 scripts/program_cf_rom_sync.py image.hex \
  --sim build/CF_ROM_SYNC_sim.v \
  --lvs build/CF_ROM_SYNC_lvs.v \
  --image-out build/CF_ROM_SYNC.rom
```

The script prints the SHA-256 of the 1024 bytes. The same digest is
written at the top of both Verilog files. `CF_ROM_SYNC.rom` is the
normalized image: one lowercase byte per line, address 0 first. Submit
that file and the SHA-256 with the design. ChipFoundry programs the
protected leaf from that image when the full geometry is merged.

## Simulation

Compile `build/CF_ROM_SYNC_sim.v` instead of `hdl/gl/CF_ROM_SYNC.v` and
the zero model. It contains `CF_ROM_SYNC` and `CF_ROM_SYNC_core`.

The model is ideal and not silicon-verified:

* `RST` high on `posedge CLK` clears the output register
* `EN` high on `posedge CLK` captures `mem[A]`
* `OE` high drives `DO`; `OE` low is high-Z

Do not add the simulation file to OpenLane `VERILOG_FILES`. Place and
route with `hdl/gl/CF_ROM_SYNC.v` and `layout/lef/CF_ROM_SYNC.lef`.

## LVS

`build/CF_ROM_SYNC_lvs.v` has the same ports and hierarchy as `hdl/gl/`.
`CF_ROM_SYNC` ties the leaf wells (`vpb` to `vpwr`, `vnb` to `vgnd`).
`CF_ROM_SYNC_core` is an empty blackbox.

The public GDS and LEF are abstracts. LVS compares the wrap hierarchy and
pins. It does not check the programmed bytes. Use either `hdl/gl/` or the
generated LVS file against `layout/gds/CF_ROM_SYNC.gds`. Both describe the
same wrap.

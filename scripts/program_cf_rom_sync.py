#!/usr/bin/env python3
"""Program a CF_ROM_SYNC 1K×8 image for simulation and LVS.

The image is 1024 data bytes in address order. Address 0 is the first
byte. This writes:

* a simulation Verilog model of CF_ROM_SYNC with those bytes
* an LVS Verilog netlist of the public wrap and empty leaf

The LVS netlist matches hdl/gl. The public layout is an abstract, so the
mask image is not drawn into it. Submit the normalized image with the
design. ChipFoundry applies that image when the leaf geometry is merged.

Do not add the simulation file to OpenLane VERILOG_FILES.

  python3 scripts/program_cf_rom_sync.py image.hex \
      --sim build/CF_ROM_SYNC_sim.v \
      --lvs build/CF_ROM_SYNC_lvs.v \
      --image-out build/CF_ROM_SYNC.rom
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path


DEPTH = 1024
TOKEN = re.compile(r"^(?:0x)?([0-9a-fA-F]{1,2})$")


def parse_image(text, path):
    data = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("//", 1)[0].split("#", 1)[0].strip()
        if not line:
            continue
        for token in line.split():
            match = TOKEN.match(token)
            if match is None:
                raise SystemExit("%s:%d: expected a hex byte, got %r" % (path, lineno, token))
            data.append(int(match.group(1), 16))
    if len(data) != DEPTH:
        raise SystemExit("%s: expected %d bytes, got %d" % (path, DEPTH, len(data)))
    return data


def image_sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


def normalized_image(data):
    return "".join("%02x\n" % byte for byte in data)


def emit_sim(data):
    digest = image_sha256(data)
    lines = [
        "`timescale 1ns / 1ps",
        "",
        "// Ideal functional model of CF_ROM_SYNC with a programmed 1K×8 image.",
        "// Not silicon-verified. Do not add this file to OpenLane VERILOG_FILES.",
        "// Image sha256: %s" % digest,
        "//",
        "// Assumed protocol:",
        "//   * RST high on posedge CLK clears the output register",
        "//   * EN high on posedge CLK captures mem[A]",
        "//   * OE high drives DO; OE low is high-Z",
        "",
        "module CF_ROM_SYNC_core (",
        "    vpwr,",
        "    vgnd,",
        "    vpb,",
        "    vnb,",
        "    DO,",
        "    A,",
        "    EN,",
        "    CLK,",
        "    RST,",
        "    OE",
        ");",
        "    input vpwr;",
        "    input vgnd;",
        "    input vpb;",
        "    input vnb;",
        "    output [7:0] DO;",
        "    input [9:0] A;",
        "    input EN;",
        "    input CLK;",
        "    input RST;",
        "    input OE;",
        "",
        "    reg [7:0] mem [0:1023];",
        "    reg [7:0] q;",
        "",
        "    initial begin",
    ]
    for address, byte in enumerate(data):
        lines.append("        mem[%d] = 8'h%02x;" % (address, byte))
    lines.extend(
        [
            "        q = 8'h00;",
            "    end",
            "",
            "    always @(posedge CLK or posedge RST) begin",
            "        if (RST)",
            "            q <= 8'h00;",
            "        else if (EN)",
            "            q <= mem[A];",
            "    end",
            "",
            "    assign DO = OE ? q : 8'hzz;",
            "endmodule",
            "",
            "module CF_ROM_SYNC (",
            "    vpwr,",
            "    vgnd,",
            "    DO,",
            "    A,",
            "    EN,",
            "    CLK,",
            "    RST,",
            "    OE",
            ");",
            "    input vpwr;",
            "    input vgnd;",
            "    output [7:0] DO;",
            "    input [9:0] A;",
            "    input EN;",
            "    input CLK;",
            "    input RST;",
            "    input OE;",
            "    CF_ROM_SYNC_core u_core (",
            "        .vpwr(vpwr),",
            "        .vgnd(vgnd),",
            "        .vpb(vpwr),",
            "        .vnb(vgnd),",
            "        .DO(DO),",
            "        .A(A),",
            "        .EN(EN),",
            "        .CLK(CLK),",
            "        .RST(RST),",
            "        .OE(OE)",
            "    );",
            "endmodule",
            "",
        ]
    )
    return "\n".join(lines)


def emit_lvs(data):
    digest = image_sha256(data)
    return """// Integration netlist for LVS. Ports and hierarchy match hdl/gl.
// The public layout is an abstract, so the mask image is not in this netlist.
// Submit the normalized image with the design. Image sha256: %s

module CF_ROM_SYNC_core (
    vpwr,
    vgnd,
    vpb,
    vnb,
    DO,
    A,
    EN,
    CLK,
    RST,
    OE
);
    input vpwr;
    input vgnd;
    input vpb;
    input vnb;
    output [7:0] DO;
    input [9:0] A;
    input EN;
    input CLK;
    input RST;
    input OE;
endmodule

module CF_ROM_SYNC (
    vpwr,
    vgnd,
    DO,
    A,
    EN,
    CLK,
    RST,
    OE
);
    input vpwr;
    input vgnd;
    output [7:0] DO;
    input [9:0] A;
    input EN;
    input CLK;
    input RST;
    input OE;
    CF_ROM_SYNC_core u_core (
        .vpwr(vpwr),
        .vgnd(vgnd),
        .vpb(vpwr),
        .vnb(vgnd),
        .DO(DO),
        .A(A),
        .EN(EN),
        .CLK(CLK),
        .RST(RST),
        .OE(OE)
    );
endmodule
""" % digest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="1024 hex bytes in address order")
    parser.add_argument("--sim", help="simulation Verilog output")
    parser.add_argument("--lvs", help="LVS Verilog output")
    parser.add_argument("--image-out", help="normalized image to submit")
    args = parser.parse_args(argv)
    if not args.sim and not args.lvs and not args.image_out:
        raise SystemExit("name at least one of --sim, --lvs, or --image-out")

    path = Path(args.image)
    data = parse_image(path.read_text(), path)
    digest = image_sha256(data)
    print("bytes %d sha256 %s" % (len(data), digest))
    if args.sim:
        Path(args.sim).write_text(emit_sim(data))
        print("wrote %s" % args.sim)
    if args.lvs:
        Path(args.lvs).write_text(emit_lvs(data))
        print("wrote %s" % args.lvs)
    if args.image_out:
        Path(args.image_out).write_text(normalized_image(data))
        print("wrote %s" % args.image_out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit as exc:
        code = exc.code
        if code in (None, 0):
            sys.exit(0)
        if isinstance(code, str):
            print(code, file=sys.stderr)
            sys.exit(1)
        raise

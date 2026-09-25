`timescale 1ns / 1ps

// Ideal functional model of leaf CF_ROM_SYNC_core (1K×8 synchronous ROM).
// Drop this file in place of hdl/gl/CF_ROM_SYNC_core.v for simulation.
// Do not add it to OpenLane VERILOG_FILES.
//
// Assumed protocol (ideal, not silicon-verified):
//   * RST high on posedge CLK clears the output register
//   * EN high on posedge CLK captures mem[A]
//   * OE high drives DO; OE low is high-Z
//   * The public image is all zeros. The programmed image is not in this package.
// Wells are unused in this digital model.

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

    reg [7:0] mem [0:1023];
    reg [7:0] q;
    integer i;

    initial begin
        for (i = 0; i < 1024; i = i + 1)
            mem[i] = 8'h00;
        q = 8'h00;
    end

    always @(posedge CLK or posedge RST) begin
        if (RST)
            q <= 8'h00;
        else if (EN)
            q <= mem[A];
    end

    assign DO = OE ? q : 8'hzz;
endmodule

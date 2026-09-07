// Structural PG wrapper. Analog leaf is CF_ROM_SYNC_core.
// Customer rails are vpwr/vgnd; well taps vpb/vnb/vpbe are tied inside.
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

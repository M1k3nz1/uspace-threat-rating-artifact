"""SecRAM 2.0 (SESAR 2020, edition 02.00.00, 2017) risk matrix, Section 4.1 and 4.6.4 (identical in both places).
Rows of the printed table are likelihood 5..1, columns are (reviewed) impact 1..5. Values below: MATRIX[likelihood][impact]."""
MATRIX={5:["Low","High","High","High","High"],
        4:["Low","Medium","High","High","High"],
        3:["Low","Low","Medium","High","High"],
        2:["Low","Low","Low","Medium","High"],
        1:["Low","Low","Low","Medium","Medium"]}
def risk(l,i): return MATRIX[int(l)][int(i)-1]
CLS={"Low":0,"Medium":1,"High":2}

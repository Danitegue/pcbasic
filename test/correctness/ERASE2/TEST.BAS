1 REM PC-BASIC test 
2 REM test for memory release by ERASE 
5 OPEN "OUTPUT.TXT" FOR OUTPUT AS 1
10 DIM B[70]
20 DIM A[10]
25 PRINT#1, FRE(0), VARPTR(A(0)), VARPTR(B(0))
30 ERASE B
40 DIM B[70]
50 PRINT#1, FRE(0), VARPTR(A(0)), VARPTR(B(0))
60 CLOSE

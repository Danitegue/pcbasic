4 CLS: KEY OFF
7 DIM A%[400]
20 SCREEN 9
35 OPEN "OUTPUT.DAT" FOR OUTPUT AS 1
38 CLS:LINE(0,0)-(40,50), 4
40 GET(10,20)-(0,0),A%
45 GOSUB 2000
50 GET(10,0)-(0,20),A%
55 GOSUB 2000
60 GET(0,20)-(10,0),A%
65 GOSUB 2000
70 GET(0,0)-(10,20),A%
75 GOSUB 2000
999 END
2000 REM
2010 FOR K=0 TO 400
2020 PRINT#1, MKI$(A%[K]);
2030 NEXT
2050 RETURN


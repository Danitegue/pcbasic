10 REM PC-BASIC test
20 REM LEFT$ function
30 OPEN "OUTPUT.TXT" FOR OUTPUT AS 1
40 ON ERROR GOTO 10000
50 PRINT#1, LEFT$
60 PRINT#1, LEFT$(
70 PRINT#1, LEFT$("ABC"
80 PRINT#1, LEFT$(1
90 PRINT#1, LEFT$(1.5
100 PRINT#1, LEFT$(-1)
110 PRINT#1, LEFT$(1)
120 PRINT#1, LEFT$(-1.5)
130 PRINT#1, LEFT$(1.5)
140 PRINT#1, LEFT$(-1.5D2)
150 PRINT#1, LEFT$(1.5D2)
160 PRINT#1, LEFT$("ABC")
200 PRINT#1, LEFT$(0)
210 PRINT#1, LEFT$(256)
220 PRINT#1, LEFT$(32768)
230 PRINT#1, LEFT$(65536)
240 PRINT#1, LEFT$(1.701412E+38)
250 PRINT#1, LEFT$(1.701411834604692D+38)
300 PRINT#1, LEFT$(1)
310 PRINT#1, LEFT$(#1)
320 PRINT#1, LEFT$(1,1)
330 PRINT#1, LEFT $("ABC", 1)
340 PRINT#1, LEFT$ ("ABC", 1)
350 PRINT#1, LEFT $ ("ABC", 1)
1000 PRINT#1, LEFT$("ABC", "A")
1010 PRINT#1, LEFT$("", 2)
1020 PRINT#1, LEFT$("ABC", 1, 1)
1030 PRINT#1, LEFT$("ABC", 0)
1040 PRINT#1, LEFT$("ABC", -1)
1050 PRINT#1, LEFT$("ABC", 256)
1060 PRINT#1, LEFT$("ABC", 32768)
9999 END
10000 PRINT#1, ERR, ERL
10010 RESUME NEXT

4 TRON
5 OPEN "output" FOR OUTPUT AS 1
7 ON ERROR GOTO 1000
10 PRINT#1, "A"
20 GOTO 110
100 FOR I= 1 TO 10
110 PRINT#1, I
115 GOTO 130
120 NEXT
130 PRINT#1, "B"
999 CLOSE:END
1000 PRINT#1, "error:", ERR, ERL: PRINT ERR, ERL: RESUME NEXT

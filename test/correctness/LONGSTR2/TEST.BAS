10 OPEN "OUTPUT.TXT" FOR OUTPUT AS 1
15 ON ERROR GOTO 1000
20 A$=SPACE$(128)
30 PRINT#1, A$+A$
40 CLOSE
50 END
1000 PRINT#1, "error:", ERR, ERL
1010 RESUME NEXT


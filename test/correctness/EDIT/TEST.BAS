10 REM PC-BASIC test 
20 REM EDIT test
30 ON ERROR GOTO 100
40 END
100 OPEN "OUTPUT.TXT" FOR APPEND AS 1
110 PRINT#1, ERR, ERL
115 CLOSE
120 RESUME NEXT


4 TRON
5 OPEN "output" FOR OUTPUT AS 1
7 ON ERROR GOTO 1000
10 FOR A$="1" TO "10" STEP "2": NEXT A$
20 FOR A$=1 TO 10 STEP 2
30 FOR A%="1" TO 10 STEP 2
40 FOR A%=1 TO "10" STEP 2
50 FOR A%=1 TO 10 STEP "2"
130 FOR A!="1" TO 10 STEP 2
140 FOR A!=1 TO "10" STEP 2
150 FOR A!=1 TO 10 STEP "2"
230 FOR A#="1" TO 10 STEP 2
240 FOR A#=1 TO "10" STEP 2
250 FOR A#=1 TO 10 STEP "2"
300 FOR A=1 TO 10 STEP 2: NEXT "A"
310 FOR 5=1 TO 10 STEP 2: NEXT 5
320 FOR A=1 TO 10 STEP 2: NEXT 2
999 CLOSE:END
1000 PRINT#1, "error:", ERR, ERL: PRINT ERR, ERL: RESUME NEXT


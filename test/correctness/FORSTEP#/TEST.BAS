4 TRON
5 OPEN "output" FOR OUTPUT AS 1
7 ON ERROR GOTO 1000
120 FOR A#=1 TO 10 STEP 2: PRINT#1, A#: NEXT A#
220 FOR A#=20 TO 10 STEP -1: PRINT#1, A#: NEXT A#
320 FOR A#=1.4 TO 10.5 STEP 1.5: PRINT#1, A#: NEXT A#
420 FOR I#=I# TO I#+10 STEP I#+1: PRINT#1, I#: NEXT I#
520 FOR A#=1 TO 20 STEP 2: PRINT#1, A#: A# = A#*2: NEXT A#
620 FOR A#=20 TO 10: PRINT#1, A#: NEXT A#
720 A#=30: FOR A#=1 TO 10 STEP 2: PRINT#1, A#: NEXT A#
999 CLOSE: END
1000 PRINT#1, "error:", ERR, ERL: PRINT ERR, ERL: RESUME NEXT

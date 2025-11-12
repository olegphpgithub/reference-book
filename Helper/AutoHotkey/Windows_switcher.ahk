
v1Pid := 0
v2Pid := 0
v3Pid := 0
v4Pid := 0
v5Pid := 0
v6Pid := 0
v7Pid := 0
v8Pid := 0
v9Pid := 0

!0::
    WinGet, ThisPid, PID, A
    Gui, New
    Gui, Add, Text,, Alt+
    Gui, Add, Edit, vShortCut w200
    Gui, Add, Text,, PID:
    Gui, Add, Edit, vWinPid w200, %ThisPid%
    Gui, Add, Button, Default w80 gButtonOK, OK
    Gui, Add, Button, x+10 w80 gButtonCancel, Cancel
    Gui, Show,, Create shortcut
return

ButtonOK:
    Gui, Submit
    keystroke  = %ShortCut%
    if (keystroke == 1) {
        v1Pid = %WinPid%
    }
    if (keystroke == 2) {
        v2Pid = %WinPid%
    }
    if (keystroke == 3) {
        v3Pid = %WinPid%
    }
    if (keystroke == 4) {
        v4Pid = %WinPid%
    }
    if (keystroke == 5) {
        v5Pid = %WinPid%
    }
    if (keystroke == 6) {
        v6Pid = %WinPid%
    }
    if (keystroke == 7) {
        v7Pid = %WinPid%
    }
    if (keystroke == 8) {
        v8Pid = %WinPid%
    }
    if (keystroke == 9) {
        v9Pid = %WinPid%
    }
return

ButtonCancel:
    Gui, Destroy
return

!1::
    WinActivate, ahk_pid %v1Pid%
return

!2::
    WinActivate, ahk_pid %v2Pid%
return

!3::
    WinActivate, ahk_pid %v3Pid%
return

!4::
    WinActivate, ahk_pid %v4Pid%
return

!5::
    WinActivate, ahk_pid %v5Pid%
return

!6::
    WinActivate, ahk_pid %v6Pid%
return

!7::
    WinActivate, ahk_pid %v7Pid%
return

!8::
    WinActivate, ahk_pid %v8Pid%
return

!9::
    WinActivate, ahk_pid %v9Pid%
return

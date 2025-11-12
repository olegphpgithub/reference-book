
v1Pid := 0
v2Pid := 0
v3Pid := 0

^!0::
    WinGet, ThisPid, PID, A
    Gui, New
    Gui, Add, Text,, Alt+
    Gui, Add, Edit, vShortCut w200
    Gui, Add, Text,, Возраст:
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
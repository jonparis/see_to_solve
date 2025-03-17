Set WshShell = WScript.CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Check if the batch file exists
If Not fso.FileExists(WshShell.CurrentDirectory & "\src\see_to_solve_service_windows.bat") Then
    MsgBox "Error: Service batch file not found. Please make sure you're running this script from the correct directory.", vbCritical
    WScript.Quit
End If

' Check if the icon exists
If Not fso.FileExists(WshShell.CurrentDirectory & "\see_to_solve_chrome_ext\assets\icon-128.png") Then
    MsgBox "Error: Icon file not found. Please make sure you're running this script from the correct directory.", vbCritical
    WScript.Quit
End If

' Create a shortcut on the desktop
Set shortcut = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\See to Solve Service.lnk")
shortcut.TargetPath = WshShell.CurrentDirectory & "\src\see_to_solve_service_windows.bat"
shortcut.WorkingDirectory = WshShell.CurrentDirectory & "\src"
shortcut.IconLocation = WshShell.CurrentDirectory & "\see_to_solve_chrome_ext\assets\icon-128.png"
shortcut.Save

' Show a friendly message
MsgBox "See to Solve Service shortcut has been created on your desktop!" & vbCrLf & vbCrLf & "Double-click the shortcut to start the service.", vbInformation

' Run the service
WshShell.Run """" & WshShell.CurrentDirectory & "\src\see_to_solve_service_windows.bat""", 1, False
Set WshShell = Nothing 
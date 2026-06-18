Dim shell, fso, pasta, appPy
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
pasta = fso.GetParentFolderName(WScript.ScriptFullName)
appPy = pasta & "\app.py"
If Not fso.FileExists(appPy) Then
    MsgBox "Arquivo app.py nao encontrado!", vbCritical, "i-flash"
    WScript.Quit
End If
shell.Run "cmd /c pip install flask --quiet", 0, True
shell.Run "cmd /c cd /d """ & pasta & """ && python app.py", 0, False
WScript.Sleep 2500
shell.Run "cmd /c start """" ""http://localhost:5000""", 0, False
Dim ngrokPath
ngrokPath = pasta & "\ngrok.exe"
If fso.FileExists(ngrokPath) Then
    shell.Run "cmd /c cd /d """ & pasta & """ && ngrok http 5000", 1, False
Else
    MsgBox "Sistema i-flash iniciado!" & vbCrLf & vbCrLf & _
           "Acesso local: http://localhost:5000" & vbCrLf & vbCrLf & _
           "Para acesso externo (cliente ver de longe):" & vbCrLf & _
           "1. Baixe ngrok em: https://ngrok.com/download" & vbCrLf & _
           "2. Coloque ngrok.exe nesta pasta" & vbCrLf & _
           "3. Execute este VBS novamente" & vbCrLf & vbCrLf & _
           "Para instalar como app no celular:" & vbCrLf & _
           "Abra no Chrome > Menu > Adicionar a tela inicial", _
           vbInformation, "i-flash"
End If
Set shell = Nothing
Set fso = Nothing

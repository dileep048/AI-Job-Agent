Attribute VB_Name = "modAutoLogin"
Option Explicit

Public Sub AutoLoginSelectedClient()
    AutoLoginClientRow SelectedClientRow
End Sub

Public Sub AutoLoginClientRow(ByVal rowNum As Long)
    Dim username As String
    Dim password As String
    Dim gstin As String
    Dim clientName As String

    username = GetClientField(rowNum, COL_USERNAME)
    password = GetClientField(rowNum, COL_PASSWORD)
    gstin = GetClientField(rowNum, COL_GSTIN)
    clientName = GetClientField(rowNum, COL_CLIENT_NAME)

    If gstin = "" Then
        MsgBox "No GSTIN found on row " & rowNum & ". Add client details in Client Master.", vbExclamation, APP_NAME
        Exit Sub
    End If

    If Not ValidateGSTIN(gstin) Then
        MsgBox "GSTIN format looks invalid: " & gstin, vbExclamation, APP_NAME
    End If

    If username = "" Then
        MsgBox "Username is empty for " & clientName & ". Add credentials in Client Master.", vbExclamation, APP_NAME
        Exit Sub
    End If

    SetClipboardText username
    OpenUrl GST_LOGIN_URL
    MarkClientLogin rowNum

    MsgBox "GST login page opened." & vbCrLf & vbCrLf & _
           "Client: " & clientName & vbCrLf & _
           "GSTIN: " & gstin & vbCrLf & _
           "Username copied to clipboard — paste it on the portal." & vbCrLf & vbCrLf & _
           "Password is stored in Client Master (column E). Complete CAPTCHA/OTP manually.", _
           vbInformation, APP_NAME
End Sub

Public Sub CopyPasswordForSelectedClient()
    Dim rowNum As Long
    Dim password As String
    rowNum = SelectedClientRow
    password = GetClientField(rowNum, COL_PASSWORD)
    If password = "" Then
        MsgBox "No password stored for the selected client row.", vbExclamation, APP_NAME
        Exit Sub
    End If
    SetClipboardText password
    MsgBox "Password copied to clipboard for row " & rowNum & ".", vbInformation, APP_NAME
End Sub

Public Sub OpenGSTPortalHome()
    OpenUrl GST_HOME_URL
End Sub

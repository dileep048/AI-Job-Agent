Attribute VB_Name = "modConstants"
Option Explicit

' GST Auto Login Excel Utility — shared constants
Public Const APP_NAME As String = "GST Auto Login Utility"
Public Const GST_LOGIN_URL As String = "https://services.gst.gov.in/services/login"
Public Const GST_HOME_URL As String = "https://www.gst.gov.in/"
Public Const GST_RETURN_STATUS_URL As String = "https://services.gst.gov.in/services/auth/searchtp"
Public Const GST_TP_SEARCH_URL As String = "https://services.gst.gov.in/services/api/search/tp"
Public Const GST_RETURN_API_URL As String = "https://return.gst.gov.in/returns/auth/api/gstr1/filing-status"

Public Const SHEET_DASHBOARD As String = "Dashboard"
Public Const SHEET_CLIENTS As String = "Client Master"
Public Const SHEET_STATUS As String = "Return Status"
Public Const SHEET_SETTINGS As String = "Settings"
Public Const SHEET_HELP As String = "Help"

Public Const FY_2026_27 As String = "2026-27"
Public Const FY_2027_28 As String = "2027-28"

Public Const COL_CLIENT_ID As Long = 1
Public Const COL_CLIENT_NAME As Long = 2
Public Const COL_GSTIN As Long = 3
Public Const COL_USERNAME As Long = 4
Public Const COL_PASSWORD As Long = 5
Public Const COL_EMAIL As Long = 6
Public Const COL_CONTACT As Long = 7
Public Const COL_FILER_TYPE As Long = 8
Public Const COL_ACTIVE As Long = 9
Public Const COL_LAST_LOGIN As Long = 10
Public Const COL_NOTES As Long = 11

Public Const CLIENT_HEADER_ROW As Long = 4
Public Const CLIENT_FIRST_DATA_ROW As Long = 5

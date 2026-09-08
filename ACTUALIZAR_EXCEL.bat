@echo off
title Actualizador de Excel - Firebase

echo ==========================================
echo     ACTUALIZADOR FIREBASE - EXCEL
echo ==========================================
echo.

cd "Para excel"

python exportar_firebase_excel.py

echo.
echo ==========================================
echo     PROCESO TERMINADO
echo ==========================================
echo.

pause
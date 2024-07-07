# バージョンとしてビルドした日時を出力
$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$versionContent = "`BUILD_DATE` = `"$date`""
Set-Content -Path "src/version.py" -Value $versionContent

# ビルド
.venv\Scripts\pyinstaller.exe `
  --onefile `
  --name code2text.exe `
  src/main.py
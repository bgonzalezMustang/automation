powershell if((get-process -name "Python") -eq $Null){echo "No active python instance"} else{stop-process -name "Python"}

"C:\Users\bgonzalez\AppData\Local\Programs\Python\Python39\python.exe" "C:\Users\bgonzalez\OneDrive - Mustang Plumbing\Documents\Github\automation\TeamsBot\main.py"
pause


start /b "C:\Users\bgonzalez\AppData\Local\Programs\Python\Python39\python.exe" "C:\Users\bgonzalez\OneDrive - Mustang Plumbing\Documents\Github\automation\cadFileManagement\main.py"


pause
rem execute this from root of repo
set PYTHONDONTWRITEBYTECODE=1
pip install -r requirements.txt
cd .\src
python -B -u main.py %*
cd ..

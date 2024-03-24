rem execute this from root of repo
set PYTHONDONTWRITEBYTECODE=1
pip install -r requirements.txt
cd .\src
copy ..\tests\test_*.py .
copy ..\tests\pytest.ini .
python -B -u -m pytest
del .\test_*.py /Q
del .\pytest.ini /Q
rmdir .\.pytest_cache /s/q
cd ..

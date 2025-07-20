@echo off
chcp 65001 >nul 2>&1
REM 检查项目文件完整性

echo === 检查 GBaseMeetSub 项目文件 ===
echo.

REM 检查主文件
echo 检查主要文件...
if exist app.py (echo [OK] app.py) else (echo [缺失] app.py)
if exist requirements.txt (echo [OK] requirements.txt) else (echo [缺失] requirements.txt)
echo.

REM 检查目录结构
echo 检查目录结构...
if exist src\ (echo [OK] src/) else (echo [缺失] src/)
if exist templates\ (echo [OK] templates/) else (echo [缺失] templates/)
if exist static\ (echo [OK] static/) else (echo [缺失] static/)
if exist static\css\ (echo [OK] static/css/) else (echo [缺失] static/css/)
if exist static\js\ (echo [OK] static/js/) else (echo [缺失] static/js/)
echo.

REM 检查源代码文件
echo 检查源代码文件...
if exist src\__init__.py (echo [OK] src/__init__.py) else (echo [缺失] src/__init__.py)
if exist src\main_pipeline.py (echo [OK] src/main_pipeline.py) else (echo [缺失] src/main_pipeline.py)
if exist src\speech_recognizer.py (echo [OK] src/speech_recognizer.py) else (echo [缺失] src/speech_recognizer.py)
if exist src\term_manager.py (echo [OK] src/term_manager.py) else (echo [缺失] src/term_manager.py)
if exist src\term_corrector.py (echo [OK] src/term_corrector.py) else (echo [缺失] src/term_corrector.py)
if exist src\subtitle_generator.py (echo [OK] src/subtitle_generator.py) else (echo [缺失] src/subtitle_generator.py)
if exist src\accuracy_validator.py (echo [OK] src/accuracy_validator.py) else (echo [缺失] src/accuracy_validator.py)
echo.

REM 检查模板文件
echo 检查模板文件...
if exist templates\index.html (echo [OK] templates/index.html) else (echo [缺失] templates/index.html)
echo.

REM 检查静态文件
echo 检查静态文件...
if exist static\css\style.css (echo [OK] static/css/style.css) else (echo [缺失] static/css/style.css)
if exist static\js\main.js (echo [OK] static/js/main.js) else (echo [缺失] static/js/main.js)
echo.

REM 统计结果
echo === 检查完成 ===
echo 如果有文件缺失，请运行: git pull origin main
echo.
pause
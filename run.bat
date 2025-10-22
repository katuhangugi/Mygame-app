@echo off
REM --------------------------------------------
REM 通用启动脚本（保证exe能找到依赖文件）
REM 把此bat文件放到和你的exe同目录
REM 在PPT里超链接这个bat即可
REM --------------------------------------------

REM 切换到当前批处理所在目录
cd /d %~dp0

REM 这里改成你要运行的exe名字
set EXE_NAME=main.exe

REM 如果程序需要参数，可以写在后面，例如：%EXE_NAME% -config config.ini
start "" "%EXE_NAME%"

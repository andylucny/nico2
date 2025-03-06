@echo off
for /L %%i in (1,1,7) do (
    python generate.py %%i
)

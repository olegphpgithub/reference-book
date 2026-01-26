@echo off

set var=initial

echo Before: %var%

for %%i in (1 2 3) do (
    set var=new_value_%%i
    echo Inside loop: %var%
)

echo After: %var%
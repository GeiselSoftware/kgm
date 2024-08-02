#rm -f *.tsk
#rm -rf CMakeCache.txt CMakeFiles cmake_install.cmake Makefile
find . -name "*~" | xargs rm
find . -type d | xargs -i -n1 sh -c "cd \{}; rm -rf CMakeCache.txt CMakeFiles cmake_install.cmake Makefile *.tsk *.a"

rm -rf imgui.ini

rm -rf build-*
rm -rf build


# 1. Build release version
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j10
cd ..

echo release version build complete

# 2. Build debugging version
cd build-debug
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j10
cd ..

echo debug version build complete
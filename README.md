# LogicSyntaxBuilder
This is repository for my project of designing a computer, simulated using a game called Scrap Mechanic
## Progress
This computer is still in progress of building and it doesn't even work if you are reading this text. Gonna write update notes here later.
## Running
```bash
git clone https://github.com/vfosnar/LogicSyntaxBuilder.git
cd LogicSyntaxBuilder

# this will build the whole project and export it to blueprints directory.
# You need to restart steam after it if you are running this code for the first time
bash build_sm.sh /path/to/Scrap/Mechanic/Blueprints/some_uuid4/

# or you can simulate it without Scrap Mechanic
# using cpp and g++ compiler (prebuild for Linux-x86_64) RECOMMENDED
bash build_sim_cpp.sh

# using python3
bash build_sim.sh
```
## Building simulator.cpp
``` bash
cd CPPSimulator
rm simulator
make
```

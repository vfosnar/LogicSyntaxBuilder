#include <iostream>
#include <fstream>
#include <stdint.h>
using namespace std;

int step(uint32_t gateCount, bool* gateValues, unsigned char* gateTypes, uint32_t* gateParents)
{
    uint32_t i = 0;
    uint32_t parentCount;
    unsigned char gateType;
    bool gateActive;
    bool parentValue;

    bool gateValuesNew[gateCount];
    cout << "=== STEP ===" << endl;
    for(int iGate = 0; iGate < gateCount; iGate++)
    {
        parentCount = gateParents[i];
        i++;
        gateType = gateTypes[iGate];
        if(gateType == 0 || gateType == 3)
        {
            gateActive = parentCount > 0;
            for(uint32_t iParent = 0; iParent < parentCount; iParent++)
            {
                parentValue = gateValues[gateParents[i]];
                gateActive = gateActive && parentValue;

                i++;
            }
        }
        else if(gateType == 1 || gateType == 4)
        {
            gateActive = false;
            for(uint32_t iParent = 0; iParent < parentCount; iParent++)
            {
                parentValue = gateValues[gateParents[i]];
                gateActive = gateActive || parentValue;

                i++;
            }
        }
        else if(gateType == 2 || gateType == 5)
        {
            gateActive = false;
            for(uint32_t iParent = 0; iParent < parentCount; iParent++)
            {
                parentValue = gateValues[gateParents[i]];
                gateActive = gateActive ^ parentValue;

                i++;
            }
        }
        if(gateType >= 3)
            gateActive = !gateActive;
        gateValuesNew[iGate] = gateActive;
        cout << "Gate: " << iGate << " Value: " << gateActive << " Type: " << gateType+0 << endl;
        
    }
    for(int iGate = 0; iGate < gateCount; iGate++)
    {
        gateValues[iGate] = gateValuesNew[iGate];
    }
    return 0;
}

int main()
{
    /*
    ## FILE STRUCTURE ##
    4 byte                  = gateCount
    $SIZE bytes             = gateTypes
    4 bytes                 = dataSize (parent data)
    $dataSize bytes         = gateParents
    
    ## ARRAY ##
    4 byte                  = SIZE
    $SIZE of 4 byte items   = content

    */
    fstream file;
    file.open("data", ios::in);
    if(!file.is_open())
    {
        cerr << "File error" << endl;
        return 1;
    }
    uint32_t gateCount;
    file.read((char*)&gateCount, 4);

    // Local array of gate values
    bool gateValues[gateCount];

    // Simulation struction from packer.py
    unsigned char gateTypes[gateCount];

    for(int i = 0; i < gateCount; i++)
    {
        // clear gateValues
        gateValues[i] = false;
        file.read((char*)&gateTypes[i], 1);
        cout << gateTypes[i]+0 << endl;
    }

    uint32_t dataSize;
    file.read((char*)&dataSize, 4);
    uint32_t gateParents[dataSize];
    for(int i = 0; i < dataSize; i++)
    {
        file.read((char*)&gateParents[i], 4);
    }
    file.close();
    step(gateCount, gateValues, gateTypes, gateParents);
    step(gateCount, gateValues, gateTypes, gateParents);
    return 0;
}
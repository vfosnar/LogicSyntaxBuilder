#include <iostream>
#include <fstream>
#include <stdint.h>
using namespace std;
#include <chrono>
using namespace std::chrono;

int simStep(uint32_t gateCount, bool* gateValues, unsigned char* gateTypes, uint32_t* gateParents)
{
    uint32_t i = 0;
    uint32_t parentCount;
    unsigned char gateType;
    bool gateActive;
    bool parentValue;

    bool gateValuesNew[gateCount];
    for(uint32_t iGate = 0; iGate < gateCount; iGate++)
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
                gateActive = gateActive & parentValue;
                i++;
            }
        }
        else if(gateType == 1 || gateType == 4)
        {
            gateActive = false;
            for(uint32_t iParent = 0; iParent < parentCount; iParent++)
            {
                parentValue = gateValues[gateParents[i]];
                gateActive = gateActive | parentValue;
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
    }
    for(uint32_t iGate = 0; iGate < gateCount; iGate++)
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
        //cout << gateTypes[i]+0 << endl;
    }

    uint32_t dataSize;
    file.read((char*)&dataSize, 4);
    uint32_t gateParents[dataSize];
    for(int i = 0; i < dataSize; i++)
    {
        file.read((char*)&gateParents[i], 4);
    }
    file.close();

    fstream sim_file;
    sim_file.open("sim", ios::in);
    uint32_t outputCount;
    sim_file.read((char*)&outputCount, 4);
    uint32_t outputBegin[outputCount];
    uint32_t outputEnd[outputCount];
    for(uint32_t i = 0; i < outputCount; i++)
    {
        sim_file.read((char*)&outputBegin[i], 4);
        sim_file.read((char*)&outputEnd[i], 4);
    }
    
    uint32_t inputCount;
    sim_file.read((char*)&inputCount, 4);
    uint32_t inputSize;
    sim_file.read((char*)&inputSize, 4);

    bool inputs[inputCount][inputSize];
    for(uint32_t step = 0; step < inputCount; step++)
    {
        for(uint32_t i = 0; i < inputSize; i++)
        {
            sim_file.read((char*)&inputs[step][i], 1);
        }
    }

    sim_file.close();

    for(uint32_t step = 0; step < inputCount; step++)
    {
        cout << "=== STEP ===" << endl;
        auto start = high_resolution_clock::now(); 
        for(int x = 0; x < 120; x++)
        {
            for(uint32_t i = 0; i < inputSize; i++)
            {
                gateValues[i] = inputs[step][i];
            }
            simStep(gateCount, gateValues, gateTypes, gateParents);
        }
        auto stop = high_resolution_clock::now();
        auto duration = duration_cast<microseconds>(stop - start); 
        cout << duration.count()/1000 << "ms/step" << endl;
        
        cout << "|";
        for(uint32_t i = 0; i < outputCount; i++)
        {
            for(uint32_t iGate = outputBegin[i]; iGate < outputEnd[i]; iGate++)
            {
                cout << (gateValues[iGate] ? u8"█" : "_");
            }
            cout << "|";
        }
        cout << endl;
    }
    return 0;
}
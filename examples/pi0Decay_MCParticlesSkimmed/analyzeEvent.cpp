#include <cmath>
#include <rrdf.h>

using namespace ROOT;
using namespace ROOT::VecOps;
using namespace edm4hep;
using namespace rrdf;


struct Ans1
{
    RVec<double> pi0_E;
    RVec<double> ph_E1;
    RVec<double> ph_E2;
};

Ans1 analyzeEvent(rrdf::Event const &evt)
{
    Ans1 ans1;
    auto mcps = evt.getMCParticles("MCParticlesSkimmed");

    for(int i : range(mcps.size())) {
        auto mcp = mcps[i];
        
        if(mcp.getPDG() == rrdf::PID::pi_0) {
            ans1.pi0_E.push_back(mcp.getEnergy());
            auto daus = mcp.getDaughters();
            if(daus.size() == 2 &&
                daus[0].getPDG() == rrdf::PID::gamma &&
                daus[1].getPDG() == rrdf::PID::gamma) {
                ans1.ph_E1.push_back(daus[0].getEnergy());
                ans1.ph_E2.push_back(daus[1].getEnergy());                
            }
        }
    }
    return ans1;
}




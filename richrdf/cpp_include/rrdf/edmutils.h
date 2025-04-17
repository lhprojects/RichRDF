#ifndef _RRDF_UTILS_H
#define _RRDF_UTILS_H

#include "edm4hep/MCParticleData.h"
#include "edm4hep/MCParticle.h"
#include "podio/ObjectID.h"

#include "TLorentzVector.h"
#include "ROOT/RVec.hxx"
#include "TVector3.h"

#include <cmath>
#include <iostream>
#include <vector>
#include <exception>
#include <string>
#include <vector>

    
inline TVector3 GetV3(edm4hep::MCParticle const &mcp) { 
    return TVector3(mcp.getMomentum()[0], mcp.getMomentum()[1], mcp.getMomentum()[2]);
}

ROOT::VecOps::RVec<Double_t> SQ(ROOT::VecOps::RVec<Double_t>& x) { 
    return x*x;
}

double SQ(double x) { 
    return x*x;
}

Double_t GetP2(edm4hep::Vector3d const &momentum) { 
    Double_t p2 = momentum.x * momentum.x + 
                    momentum.y * momentum.y + 
                    momentum.z * momentum.z;
    return p2;
}

Double_t GetP2(edm4hep::MCParticleData const &x) { 
    return GetP2(x.momentum);
}


ROOT::VecOps::RVec<Double_t> GetP2(const ROOT::VecOps::RVec<edm4hep::Vector3d>& x) { 
    size_t n = x.size();
    ROOT::VecOps::RVec<Double_t> p2a(n);
    
    for (size_t i = 0; i < n; i++) {
        p2a[i] = GetP2(x[i]);
    }
    return p2a;
}

ROOT::VecOps::RVec<Double_t> GetP2(const ROOT::VecOps::RVec<edm4hep::MCParticleData>& x) { 
    size_t n = x.size();
    ROOT::VecOps::RVec<Double_t> p2a(n);
    
    for (size_t i = 0; i < n; i++) {
        p2a[i] = GetP2(x[i]);
    }
    return p2a;
}

Double_t GetE(edm4hep::MCParticleData const &x) {
    double p2 = GetP2(x);
    return sqrt(SQ(x.mass) + p2);
}

TLorentzVector GetV4(edm4hep::MCParticleData const &x) {
    return TLorentzVector(x.momentum[0], x.momentum[1], x.momentum[2], GetE(x));
}

ROOT::VecOps::RVec<Double_t> GetE(const ROOT::VecOps::RVec<edm4hep::MCParticleData>& x) { 
    ROOT::VecOps::RVec<Double_t> energy(x.size());    
    for (size_t i = 0; i < x.size(); i++) {
        energy[i] = GetE(x[i]);
    }
    return energy;
}



Double_t GetP(edm4hep::Vector3d const &momentum) { 
    return sqrt(GetP2(momentum));
}


Double_t GetP(edm4hep::MCParticleData const &x) { 
    return GetP(x.momentum);
}

         
ROOT::VecOps::RVec<Double_t> GetP(const ROOT::VecOps::RVec<edm4hep::Vector3d>& x) { 
    ROOT::VecOps::RVec<Double_t> p2a(x.size());
    
    for (size_t i = 0; i < x.size(); i++) {
        p2a[i] = GetP(x[i]);
    }
    return p2a;
}

ROOT::VecOps::RVec<Double_t> GetP(const ROOT::VecOps::RVec<edm4hep::MCParticleData>& x) { 
    ROOT::VecOps::RVec<Double_t> p2a(x.size());
    
    for (size_t i = 0; i < x.size(); i++) {
        p2a[i] = GetP(x[i]);
    }
    return p2a;
}


ROOT::VecOps::RVec<int> GetPDG(const ROOT::VecOps::RVec<edm4hep::MCParticleData>& x) { 
    ROOT::VecOps::RVec<int> ans(x.size());
    
    for (size_t i = 0; i < x.size(); i++) {
        ans[i] = x[i].PDG;
    }
    return ans;
}

ROOT::VecOps::RVec<int> GetPDG(const ROOT::VecOps::RVec<edm4hep::MCParticle>& x) { 
    ROOT::VecOps::RVec<int> ans(x.size());
    
    for (size_t i = 0; i < x.size(); i++) {
        ans[i] = x[i].getPDG();
    }
    return ans;
}


template <typename C>
auto ToRVec(C&& c) -> ROOT::VecOps::RVec<decltype(*begin(c))> {
    using T = decltype(*begin(c));
    ROOT::VecOps::RVec<T> x;
    for(auto &&v : c) {
        x.push_back(v);
    }
    return x;
}


template<typename T>
void formatVector(std::string &os, const T& vec, std::string_view sfmt, int slice_end)
{
    std::string smft_(sfmt.begin(), sfmt.end());

    auto convert_to_str = [&](std::string &os, const decltype(vec[0]) & v) {
        if (sfmt.empty()) {
            ana::format_to(os, "{}", v);
        } else {
            char buffer[100] = {};
            snprintf(buffer, sizeof(buffer)-2, smft_.c_str(), v);
            os += buffer;
        }
    };

    os += "[";
    size_t n = vec.size();
    if (n <= slice_end) {
        for (size_t i = 0; i < n; ++i) {
            convert_to_str(os, vec[i]);
            if (i != n - 1)
                os += ", ";
        }
    } else {
        for (size_t i = 0; i < slice_end; ++i) {
            convert_to_str(os, vec[i]);
            os += ", ";
        }
        os += "...";
    }
    os += "]";
}


template<typename T>
void printVector(const T& vec, size_t edge = 3) {
    std::string buf;
    formatVector(buf, vec, edge);
    std::cout << buf;
}


namespace ana {

namespace fmt
{    

    template <class Vec>
    static void vec_do_format(Vec const &value, std::string& buffer, const std::string& fmt)
    {
        int slice_end = 10;
        std::string_view sfmt;
        try {
            //print("{}", fmt);
            for(std::string_view en : split_by(fmt, " ")) {
                //print(" '{}'  ", en);
                
                if(en.empty()){
                    // nothing to do 
                } else if(en.starts_with("%")) {
                    sfmt = en;
                } else if(en.find(":") != std::string_view::npos) {
                    if(en.starts_with(":")) {
                        slice_end = std::stoi(fmt.substr(1));
                    }
                } else {
                    throw exception_t(ana::format("Unkown spec `{}'", en));
                }
            }
        } catch(const std::invalid_argument& e) {
            throw exception_t(ana::format("convert fmt({}) to edge failed", fmt), 
                exception_t(ana::format("{} invalid_argument", e.what())));
        } catch(const std::out_of_range& e) {
            throw exception_t(ana::format("convert fmt({}) to edge failed", fmt), 
                exception_t(ana::format("{} out_of_range", e.what())));
        } catch(exception_t e) {
            throw exception_t(ana::format("convert fmt({}) to edge failed", fmt), e);
        }    

        try {
            formatVector(buffer, value, sfmt, slice_end);
        } catch(exception_t e) {
            throw exception_t(ana::format("formatVector failed with slice_end = {}", slice_end), e);
        }
    }

    template <class T>
    struct formatter_t< ROOT::VecOps::RVec<T> > {
        static void do_format(ROOT::VecOps::RVec<T> const &value, std::string& buffer, const std::string& fmt)
        {
            vec_do_format(value, buffer, fmt);
        }
    };    

    template <class T>
    struct formatter_t< std::vector<T> > {
        static void do_format(std::vector<T> const &value, std::string& buffer, const std::string& fmt)
        {
            vec_do_format(value, buffer, fmt);
        }
    };    

    template < >
    struct formatter_t< podio::ObjectID > {
        static void do_format(podio::ObjectID const &value, std::string& buffer, const std::string& fmt)
        {
            buffer += "{" + std::to_string(value.index) + ", " + std::to_string(value.collectionID) + "}";
        }
    };       
}

}

#endif

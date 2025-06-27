#ifndef _RRDF_PIDUTILS_H_
#define _RRDF_PIDUTILS_H_

#include "pdgid.h"

namespace rrdf {

bool is_quark(int pdgid) {
    return (pdgid >= PID::d && pdgid <= PID::t) ||
           (pdgid <= PID::d_bar && pdgid >= PID::t_bar);
}

bool is_gluon(int pdgid) {
    return pdgid == PID::g;
}

bool is_neutrino(int pdgid) {
    return pdgid == PID::nu_e || pdgid == PID::nu_mu || pdgid == PID::nu_tau ||
           pdgid == PID::nu_e_bar || pdgid == PID::nu_mu_bar || pdgid == PID::nu_tau_bar;
}

bool is_charged_lepton(int pdgid) { // charged lepton
    return (pdgid >= PID::e_minus && pdgid <= PID::tau_minus) ||
           (pdgid >= PID::e_plus && pdgid <= PID::tau_plus);
}


} // namespace rrdf

#endif // _RRDF_PIDUTILS_H_

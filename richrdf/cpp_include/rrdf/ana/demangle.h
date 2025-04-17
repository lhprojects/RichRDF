#ifndef _ANA_DEMANGLE_H
#define _ANA_DEMANGLE_H

#include <typeinfo>
#include <cxxabi.h>
#include <memory>
#include <string>

namespace ana {

std::string cxxabi_demangle(char const *mangled) {
    int status = 0;
    char *ans = abi::__cxa_demangle(mangled, nullptr, nullptr, &status);
    std::string ret = ans;
    std::free(ans);
    return ret;
}
    
} // namespace ana

#endif


#ifndef _HAO_EXCEPTION_H
#define _HAO_EXCEPTION_H

#include <string>
#include <algorithm>
#include <memory>
#include <exception>

namespace ana {

struct exception_t;

struct exception_imp_t {
    exception_imp_t(std::string what, std::shared_ptr<exception_imp_t> cause);
    std::string _what;
    std::shared_ptr<exception_imp_t> _cause;
};


struct exception_t : std::exception {

    exception_t(std::shared_ptr<exception_imp_t> impl);
    exception_t(std::string what, exception_t cause);
    exception_t(std::string what);


    char const *what() const noexcept override { return _impl->_what.c_str(); }
    std::string trace_back();
    exception_t cause() { return _impl->_cause; }
    std::shared_ptr<exception_imp_t> _impl;

};


inline exception_t::exception_t(std::shared_ptr<exception_imp_t> impl) :
    _impl( std::move(impl) ) {
}

inline exception_t::exception_t(std::string what, exception_t cause) :
    _impl(std::make_shared<exception_imp_t>(std::move(what), std::move(cause._impl))) {
}
inline exception_t::exception_t(std::string what) :
    _impl(std::make_shared<exception_imp_t>(std::move(what), nullptr)) {
}

inline std::string exception_t::trace_back() {
    std::string buf;
    auto *cur = &_impl;
    for(;*cur;) {
        buf += (*cur)->_what.c_str();
        buf += "\n";
        cur = &(*cur)->_cause;
        if(*cur) {
            buf += "caused by ";
        }    
    }
    return buf;
}

inline exception_imp_t::exception_imp_t(std::string what, std::shared_ptr<exception_imp_t> cause) :
    _what(what), _cause(std::move(cause)) {
}


}

#endif

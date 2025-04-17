#ifndef _ANA_SPAN_H
#define _ANA_SPAN_H

#include "exception.h"
#include "demangle.h"
#include "format.h"
#include <type_traits>

namespace ana {

template<bool check_index_>
struct span_policy {
    static const bool check_index = check_index_;
};


// using dft_spn_plcy = span_policy<false>;
// following give short name
struct dft_spn_plcy : span_policy<false> {
};



template<typename T, typename Policy = dft_spn_plcy>
class span {
private:
    T* _begin;
    T* _end;


public:
    static bool const check_index = Policy::check_index;
    using element_type           = T;
    using value_type             = std::remove_cv_t<T>;
    using size_type              = size_t;
    using difference_type        = ptrdiff_t;
    using pointer                = T*;
    using const_pointer          = const T*;
    using reference              = element_type&;

// Constructors
    span() : _begin(nullptr), _end(nullptr) {}

    span(T* data, std::size_t size)
        : _begin(data), _end(data + size) {}

    span(T* begin, T* end)
        : _begin(begin), _end(end) { }

    template<typename Policy_>
    span(span<T, Policy_> const &r) : _begin(r.begin()), _end(r.end()) {
    }

    template<typename Container,
             typename = std::enable_if_t<
                 std::is_convertible_v<decltype(std::declval<Container>().data()), T*> &&
                 std::is_convertible_v<decltype(std::declval<Container>().data() + std::declval<Container>().size()), T*> > >
    span(Container const& r) : _begin(r.data()), _end(r.data() + r.size()) {        
    }

    template<typename Policy_>
    span & operator=(span<T, Policy_> const &r) {
        _begin = r.begin;
        _end = r.end;
    }

    // Iterators
    element_type* begin() const { return _begin; }
    element_type* end() const { return _end; }

    // Data access
    element_type* data() const { return _begin; }

    // Size
    std::size_t size() const { return _end - _begin; }
    std::ptrdiff_t ssize() const { return _end - _begin; }

    bool empty() const { return _begin == _end; }

    // Element access
    element_type & operator[](std::size_t index) const {
        if (check_index && (_begin + index >= _end)) 
            throw exception_t(ana::format("span<{}>::operator[] const OutOfRange: {}/{}", 
                cxxabi_demangle(typeid(T).name()), index, size()));
        return _begin[index];
    }

     element_type& at(std::size_t index) const {
        if ((_begin + index >= _end)) 
            throw exception_t(ana::format("span<{}>::operator[] const OutOfRange: {}/{}", 
                cxxabi_demangle(typeid(T).name()), index, size()));
        return _begin[index];
    }

    element_type& front() const {
        if (check_index && empty()) 
            throw exception_t(ana::format("span<{}>::front const OutOfRange {}", 
                cxxabi_demangle(typeid(T).name()), size()));
        return *_begin;
    }

    element_type& back() const {
        if (check_index && empty()) 
            throw exception_t(ana::format("span<{}>::back const OutOfRange {}", 
                cxxabi_demangle(typeid(T).name()), size()));
        return *(_end - 1);
    }
};


}

#endif


#ifndef _ANA_SPLIT_H
#define _ANA_SPLIT_H


namespace ana {


#include <string_view>
struct split_iter_end_t {};
    
struct split_iter_t {
    std::string_view _str;
    std::string_view _sep;
    size_t current;
    size_t next_sep;  // Cached find result

    explicit split_iter_t(std::string_view str, 
                        std::string_view sep,
                        size_t start = 0)
        : _str(str), _sep(sep), current(start),
        next_sep(_str.find(_sep, start)) {}

    bool operator!=(split_iter_end_t) const {
        // Continue if we have any characters left OR
        // there's a final empty token at the end
        return current != std::string_view::npos;
    }

    std::string_view operator*() const {
        return _str.substr(current, next_sep - current);
    }

    split_iter_t& operator++() {
        if (next_sep == std::string_view::npos) {
            current = next_sep;  // Set to npos to signal end
        } else {
            current = next_sep + _sep.size();
            next_sep = _str.find(_sep, current);
            
            // Handle case where we're at the end but need empty token
            if (current > _str.size()) {
                current = std::string_view::npos;
            }
        }
        return *this;
    }
};


struct split_by {
    std::string_view _str;
    std::string_view _sep;

    split_by(std::string_view str, std::string_view sep)
        : _str(str), _sep(sep) {}

    split_iter_t begin() const {
        return split_iter_t{_str, _sep, 0};
    }

    split_iter_end_t end() const {
        return split_iter_end_t{};
    }
};


} // namespace ana
#endif



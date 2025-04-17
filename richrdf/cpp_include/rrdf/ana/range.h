#ifndef _ANA_RANGE_H
#define _ANA_RANGE_H
#include <iostream>

namespace ana {
class range {
private:
    int start_;
    int stop_;
    int step_;
    
public:
    // Constructor for range(stop)
    range(int stop) : start_(0), stop_(stop), step_(1) {}
    
    // Constructor for range(start, stop[, step])
    range(int start, int stop, int step = 1)
        : start_(start), stop_(stop), step_(step) {
        if (step == 0) {
            throw std::invalid_argument("Range step cannot be zero");
        }
    }
    
    struct end_iterator_t {
        end_iterator_t(int stop) : _stop(stop) { }
        int _stop;
    };

    // Iterator class
    class iterator {
    private:
        int current_;
        int step_;
                
    public:
        iterator(int current, int step)
            : current_(current), step_(step){ }
        
        int operator*() const { return current_; }
        
        iterator& operator++() {
            current_ += step_;
            return *this;
        }
        
        bool operator!=(const end_iterator_t& other) const {
            return  current_ < other._stop;
        }
        bool operator!=(const iterator other) const {
            return  current_ < other.current_;
        }
    };
    
    iterator begin() const {
        return iterator(start_, step_);
    }
    
    end_iterator_t end() const {
        // The end iterator just needs to compare properly with other iterators
        return end_iterator_t(stop_);
    }
};


} //namespace ana

#endif

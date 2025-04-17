#ifndef _ANA_FORMAT_H
#define _ANA_FORMAT_H

#include "exception.h"

#include <string>
#include <sstream>
#include <vector>
#include <stdexcept>
#include <type_traits>
#include <utility>
#include <memory>
#include <string_view>
#include <mutex>
#include <fstream>
#include <iostream>

namespace ana
{
// Main format function
template <typename... Args>
std::string format(std::string_view fmt, Args &&...args);

// Main format function
template <typename... Args>
void format_to(std::string &os, std::string_view fmt, Args &&...args);

// Main format function
template <typename... Args>
int print(std::string_view fmt, Args &&...args);

// Main format function
template <typename... Args>
int println(std::string_view fmt, Args &&...args);

namespace fmt
{
    // Forward declarations
    class format_arg;

    template <typename T>
    struct formatter_t;

    // Storage for format arguments
    class format_arg
    {
    public:
        virtual ~format_arg() = default;
        virtual void format(std::string &buffer, const std::string &fmt) const = 0;
    };

    template <typename T>
    class format_arg_impl : public format_arg
    {
    public:
        explicit format_arg_impl(T const &value) : value_(value) {}

        void format(std::string &buffer, const std::string &fmt) const override
        {
            formatter_t<T>::do_format(value_, buffer, fmt);
        }

    private:
        T const &value_;
    };

    // Format context to hold arguments
    class format_context_t
    {
    public:
        template <typename T>
        void add_arg(T const &value)
        {
            args_.emplace_back(new format_arg_impl<T>(value));
        }

        const format_arg &get_arg(size_t index) const
        {
            if (index >= args_.size())
            {
                throw std::out_of_range("Argument index out of range");
            }
            return *args_[index];
        }

    private:
        std::vector<std::unique_ptr<format_arg>> args_;
    };

    // Default formatter implementation
    template <typename T>
    struct formatter_t
    {
        static void do_format(const T &value, std::string &buffer, const std::string &fmt)
        {
            if (!fmt.empty())
            {
                throw std::runtime_error("Format specifier not supported for this type");
            }
            std::ostringstream oss;
            oss << value;
            buffer += oss.str();
        }
    };

    // Common implementation for floating-point formatting
    template <typename T>
    void format_float(T value, std::string &buffer, const std::string &fmt)
    {
        std::ostringstream oss;

        if (fmt.empty())
        {
            oss << value;
        }
        else
        {
            if (fmt == "f")
            {
                oss << std::fixed << value;
            }
            else if (fmt == "e")
            {
                oss << std::scientific << value;
            }
            else if (fmt == "E")
            {
                oss << std::scientific << std::uppercase << value;
            }
            else if (fmt == "g")
            {
                oss << std::defaultfloat << value;
            }
            else if (fmt == "G")
            {
                oss << std::defaultfloat << std::uppercase << value;
            }
            else
            {
                throw exception_t(ana::format("Unsupported format specifier for float: {}", fmt));
            }
        }

        buffer += oss.str();
    }

    // Specializations for each floating-point type
    template <>
    struct formatter_t<float>
    {
        static void do_format(float value, std::string &buffer, const std::string &fmt)
        {
            format_float(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<double>
    {
        static void do_format(double value, std::string &buffer, const std::string &fmt)
        {
            format_float(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<long double>
    {
        static void do_format(long double value, std::string &buffer, const std::string &fmt)
        {
            format_float(value, buffer, fmt);
        }
    };

    // Forward declaration with single template parameter
    template <typename T>
    struct formatter_t;

    // Helper function for integral formatting
    template <typename T>
    void format_integral(T value, std::string &buffer, const std::string &fmt)
    {
        std::ostringstream oss;

        if (fmt.empty())
        {
            oss << value;
        }
        else
        {
            // Integer formatting options
            if (fmt == "x" || fmt == "X")
            {
                oss << std::hex << value;
                if (fmt == "X")
                    oss << std::uppercase;
                oss << std::dec;
            }
            else if (fmt == "o")
            {
                oss << std::oct << value << std::dec;
            }
            else if (fmt == "b")
            {
                // Binary output
                if constexpr (std::is_same_v<T, bool>)
                {
                    oss << (value ? "true" : "false");
                }
                else
                {
                    oss << "0b";
                    bool leading_zero = true;
                    for (int i = sizeof(T) * 8 - 1; i >= 0; --i)
                    {
                        if (value & (1ull << i))
                        {
                            leading_zero = false;
                            oss << '1';
                        }
                        else if (!leading_zero)
                        {
                            oss << '0';
                        }
                    }
                    if (leading_zero)
                        oss << '0';
                }
            }
            else
            {
                throw std::runtime_error("Unsupported format specifier for integer");
            }
        }

        buffer += oss.str();
    }

    // Explicit specializations for integral types
    template <>
    struct formatter_t<short>
    {
        static void do_format(short value, std::string &buffer, const std::string &fmt)
        {
            format_integral(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<unsigned short>
    {
        static void do_format(unsigned short value, std::string &buffer, const std::string &fmt)
        {
            format_integral(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<int>
    {
        static void do_format(int value, std::string &buffer, const std::string &fmt)
        {
            format_integral(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<unsigned int>
    {
        static void do_format(unsigned int value, std::string &buffer, const std::string &fmt)
        {
            format_integral(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<long>
    {
        static void do_format(long value, std::string &buffer, const std::string &fmt)
        {
            format_integral(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<unsigned long>
    {
        static void do_format(unsigned long value, std::string &buffer, const std::string &fmt)
        {
            format_integral(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<long long>
    {
        static void do_format(long long value, std::string &buffer, const std::string &fmt)
        {
            format_integral(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<unsigned long long>
    {
        static void do_format(unsigned long long value, std::string &buffer, const std::string &fmt)
        {
            format_integral(value, buffer, fmt);
        }
    };

    template <>
    struct formatter_t<bool>
    {
        static void do_format(bool value, std::string &buffer, const std::string &fmt)
        {
            format_integral(value, buffer, fmt);
        }
    };

    // Specialization for strings
    template <>
    struct formatter_t<std::string>
    {
        static void do_format(const std::string &value, std::string &buffer, const std::string &fmt)
        {
            if (!fmt.empty())
            {
                throw std::runtime_error("Format specifier not supported for string");
            }
            buffer += value;
        }
    };

    template <>
    struct formatter_t<const char *>
    {
        static void do_format(const char *value, std::string &buffer, const std::string &fmt)
        {
            if (!fmt.empty())
            {
                throw std::runtime_error("Format specifier not supported for const char*");
            }
            buffer += value;
        }
    };

    template <>
    struct formatter_t<std::string_view>
    {
        static void do_format(std::string_view value, std::string &buffer, const std::string &fmt)
        {
            if (!fmt.empty())
            {
                throw std::runtime_error("Format specifier not supported for const char*");
            }
            buffer += value;
        }
    };

    // Format string parser
    class format_parser
    {
    public:
        explicit format_parser(std::string_view fmt) : fmt_(fmt) {}

        void parse_to(std::string &result, format_context_t &ctx)
        {
            size_t pos = 0;
            size_t arg_index = 0;

            while (pos < fmt_.size())
            {
                if (fmt_[pos] == '{')
                {
                    if (pos + 1 < fmt_.size() && fmt_[pos + 1] == '{')
                    {
                        // Escaped {
                        result += '{';
                        pos += 2;
                    }
                    else
                    {
                        // Format specifier
                        size_t end = fmt_.find('}', pos);
                        if (end == std::string_view::npos)
                        {
                            throw std::runtime_error("Unclosed format specifier");
                        }

                        std::string_view spec(fmt_.data() + pos + 1, end - pos - 1);
                        process_spec(spec, ctx, result, arg_index);
                        pos = end + 1;
                        arg_index++;
                    }
                }
                else if (fmt_[pos] == '}')
                {
                    if (pos + 1 < fmt_.size() && fmt_[pos + 1] == '}')
                    {
                        // Escaped }
                        result += '}';
                        pos += 2;
                    }
                    else
                    {
                        throw std::runtime_error("Unmatched }");
                    }
                }
                else
                {
                    result += fmt_[pos++];
                }
            }

        }

    private:
        void process_spec(std::string_view spec, format_context_t &ctx, std::string &buffer, size_t arg_index)
        {
            size_t colon = spec.find(':');
            std::string fmt;

            if (colon != std::string_view::npos)
            {
                fmt = std::string(spec.substr(colon + 1));
            }

            ctx.get_arg(arg_index).format(buffer, fmt);
        }

        std::string_view fmt_;
    };

}


template <typename... Args>
void format_to(std::string &result, std::string_view fmt, Args &&...args) {
    fmt::format_context_t the_ctx;
    (the_ctx.add_arg(std::forward<Args>(args)), ...);

    fmt::format_parser parser(fmt);
    parser.parse_to(result, the_ctx);

}

// Main format function
template <typename... Args>
std::string format(std::string_view fmt, Args &&...args)
{
    std::string result;
    format_to(result, fmt, std::forward<Args>(args)...);
    return result;
}

// Main format function
template <typename... Args>
int print(std::string_view fmt, Args &&...args)
{
    std::string str = format(fmt, args...);
    std::cout << str;    
    return str.size();
}

// Main format function
template <typename... Args>
int println(std::string_view fmt, Args &&...args)
{
    std::string str = format(fmt, args...);
    str += "\n";

    printf("%s", str.c_str());        
    fflush(stdout);
    return str.size();
}

// Main format function


bool& debug_flag() {
    static bool enabled = true;
    return enabled;
}

std::mutex& debug_mutex() {
    static std::mutex mtx;
    return mtx;
}

void change_debug_flag(bool enable) {
    std::lock_guard<std::mutex> lock(debug_mutex());
    debug_flag() = enable;
}

bool if_debug() {
    std::lock_guard<std::mutex> lock(debug_mutex());
    return debug_flag();
}

void _debug(const std::string& msg) {

    static std::ofstream logFile("log.txt", std::ios::out);
    static std::mutex logFileMutex;

    std::lock_guard<std::mutex> lock(logFileMutex);
    std::cout << msg;
    std::cout.flush();
    logFile << msg;
    logFile.flush();
}

template <typename... Args>
int debugln(std::string_view fmt, Args &&...args)
{
    if (!if_debug()) return -1;
    std::string str = format(fmt, args...);
    str += "\n";
    _debug(str);
    return str.size();
}


} 

#endif

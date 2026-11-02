#pragma once

#include <string>
#include <vector>

namespace uncounted {

enum class LogLevel {
    Info,
    Warn,
    Error,
    Validation
};

struct LogEntry {
    LogLevel level;
    std::string message;
    float timestamp = 0.0f;
};

class Logger {
public:
    static void Init(const std::string& logFilePath);
    static void Info(const std::string& msg);
    static void Warn(const std::string& msg);
    static void Error(const std::string& msg);
    static void Validation(const std::string& file, const std::string& key, const std::string& reason);

    static const std::vector<LogEntry>& GetRecentEntries();
    static void ClearRecent();

private:
    static void Write(LogLevel level, const std::string& msg);
};

} // namespace uncounted

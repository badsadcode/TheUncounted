#include "core/Logger.h"
#include <iostream>
#include <fstream>
#include <mutex>
#include "raylib.h"

namespace uncounted {

static std::vector<LogEntry> s_entries;
static std::string s_logPath = "uncounted.log";
static std::mutex s_mutex;

void Logger::Init(const std::string& logFilePath) {
    std::lock_guard<std::mutex> lock(s_mutex);
    s_logPath = logFilePath;
    std::ofstream ofs(s_logPath, std::ios::trunc);
    if (ofs.is_open()) {
        ofs << "=== THE UNCOUNTED — Diagnostic & Runtime Log ===\n";
    }
}

void Logger::Write(LogLevel level, const std::string& msg) {
    std::lock_guard<std::mutex> lock(s_mutex);
    const char* prefix = "[INFO] ";
    if (level == LogLevel::Warn) prefix = "[WARN] ";
    else if (level == LogLevel::Error) prefix = "[ERROR] ";
    else if (level == LogLevel::Validation) prefix = "[VALIDATION] ";

    std::string formatted = std::string(prefix) + msg;
    std::cout << formatted << std::endl;

    std::ofstream ofs(s_logPath, std::ios::app);
    if (ofs.is_open()) {
        ofs << formatted << "\n";
    }

    s_entries.push_back({level, formatted, static_cast<float>(GetTime())});
    if (s_entries.size() > 64) {
        s_entries.erase(s_entries.begin());
    }
}

void Logger::Info(const std::string& msg) { Write(LogLevel::Info, msg); }
void Logger::Warn(const std::string& msg) { Write(LogLevel::Warn, msg); }
void Logger::Error(const std::string& msg) { Write(LogLevel::Error, msg); }

void Logger::Validation(const std::string& file, const std::string& key, const std::string& reason) {
    Write(LogLevel::Validation, "File: '" + file + "' | Key: '" + key + "' | " + reason);
}

const std::vector<LogEntry>& Logger::GetRecentEntries() {
    return s_entries;
}

void Logger::ClearRecent() {
    std::lock_guard<std::mutex> lock(s_mutex);
    s_entries.clear();
}

} // namespace uncounted

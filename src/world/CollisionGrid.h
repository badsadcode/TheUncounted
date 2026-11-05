#pragma once

#include "raylib.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <unordered_map>
#include <vector>

namespace uncounted {

// A flat 2D hash grid over world boxes (X/Z), so collision queries only look at boxes near the question being asked.
// Boxes are registered in every cell they overlap. Candidates come back in ascending index order, so anything that
// resolves boxes one after another behaves exactly as it would scanning the whole list.
class CollisionGrid {
public:
    void Build(const std::vector<BoundingBox>& boxes) {
        cells_.clear();
        stamps_.assign(boxes.size(), 0);
        stamp_ = 0;
        for (int i = 0; i < static_cast<int>(boxes.size()); i++) {
            const BoundingBox& b = boxes[i];
            const int x1 = Cell(b.max.x), z1 = Cell(b.max.z);
            for (int z = Cell(b.min.z); z <= z1; z++)
                for (int x = Cell(b.min.x); x <= x1; x++) cells_[Key(x, z)].push_back(i);
        }
    }

    // The boxes whose cells overlap this X/Z rectangle.
    const std::vector<int>& QueryRect(float minX, float minZ, float maxX, float maxZ) const {
        Begin();
        const int x1 = Cell(maxX), z1 = Cell(maxZ);
        for (int z = Cell(minZ); z <= z1; z++)
            for (int x = Cell(minX); x <= x1; x++) Gather(x, z);
        return Finish();
    }

    const std::vector<int>& QueryPoint(float x, float z) const { return QueryRect(x, z, x, z); }

    // The boxes in every cell a straight line passes through.
    const std::vector<int>& QuerySegment(float ax, float az, float bx, float bz) const {
        Begin();
        if (ax > bx) { std::swap(ax, bx); std::swap(az, bz); }
        const int x0 = Cell(ax), x1 = Cell(bx);
        const float slope = bx - ax > 1e-6f ? (bz - az) / (bx - ax) : 0.0f;
        for (int x = x0; x <= x1; x++) {
            // Where the line enters and leaves this column; a sliver of padding covers floating-point edges.
            const float from = std::max(ax, x * kCellSize), to = std::min(bx, (x + 1) * kCellSize);
            float z0 = az + (from - ax) * slope, z1 = az + (to - ax) * slope;
            if (bx - ax <= 1e-6f) { z0 = az; z1 = bz; }
            if (z0 > z1) std::swap(z0, z1);
            const int zEnd = Cell(z1 + 0.01f);
            for (int z = Cell(z0 - 0.01f); z <= zEnd; z++) Gather(x, z);
        }
        return Finish();
    }

private:
    static constexpr float kCellSize = 4.0f;
    static int Cell(float v) { return static_cast<int>(std::floor(v / kCellSize)); }
    static uint64_t Key(int x, int z) { return (static_cast<uint64_t>(static_cast<uint32_t>(x)) << 32) | static_cast<uint32_t>(z); }

    void Begin() const { stamp_++; found_.clear(); }
    void Gather(int x, int z) const {
        auto it = cells_.find(Key(x, z));
        if (it == cells_.end()) return;
        for (int i : it->second)
            if (stamps_[i] != stamp_) { stamps_[i] = stamp_; found_.push_back(i); }
    }
    const std::vector<int>& Finish() const {
        std::sort(found_.begin(), found_.end());
        return found_;
    }

    std::unordered_map<uint64_t, std::vector<int>> cells_;
    mutable std::vector<uint32_t> stamps_;   // each box is reported once per query
    mutable uint32_t stamp_ = 0;
    mutable std::vector<int> found_;
};

} // namespace uncounted

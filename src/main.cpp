#include "gameplay/GameEngine.h"

int main(int argc, char** argv) {
    uncounted::GameEngine engine;
    if (!engine.Init(argc, argv)) {
        engine.Shutdown();
        return 1;
    }
    if (engine.BenchRequested()) {
        engine.RunBenchmark();
        engine.Shutdown();
        return 0;
    }
    if (engine.BalanceRequested()) {
        engine.RunBalanceReport();
        engine.Shutdown();
        return 0;
    }
    if (engine.SelfTestRequested()) {
        int failures = engine.RunSelfTest();
        engine.Shutdown();
        return failures == 0 ? 0 : 2;
    }
    engine.Run();
    engine.Shutdown();
    return 0;
}

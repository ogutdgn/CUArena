#include "engine/LokEngine.h"

#include <dlfcn.h>
#include <cstdlib>

#include <LibreOfficeKit/LibreOfficeKit.hxx>
#include <LibreOfficeKit/LibreOfficeKitInit.h>

namespace mw {

namespace {
using ProcessEventsToIdleFn = void (*)();
using AcquireSolarMutexFn = void (*)(unsigned int);
using ReleaseSolarMutexFn = unsigned int (*)();

// Resolve the REAL public VCL symbol Scheduler::ProcessEventsToIdle() (Itanium-mangled
// `_ZN9Scheduler19ProcessEventsToIdleEv`). This is a PRODUCTION symbol exported by the engine
// — explicitly NOT the banned test-only `unit_lok_process_events_to_idle` the prototype used.
// After lok_init the engine lib is loaded in-process; try the global scope first, then the
// already-loaded merged lib by path.
ProcessEventsToIdleFn resolvePump(const std::string& installPath) {
    static const char* kSym = "_ZN9Scheduler19ProcessEventsToIdleEv";
    if (auto* f = dlsym(RTLD_DEFAULT, kSym)) {
        return reinterpret_cast<ProcessEventsToIdleFn>(f);
    }
    // The symbol lives in libvcllo.so (or libmergedlo.so in a merged-libs build); both are
    // already loaded transitively by lok_init. Re-open RTLD_GLOBAL so the symbol resolves.
    for (const char* lib : {"/libvcllo.so", "/libmergedlo.so"}) {
        const std::string path = installPath + lib;
        if (void* h = dlopen(path.c_str(), RTLD_NOW | RTLD_NOLOAD | RTLD_GLOBAL)) {
            if (auto* f = dlsym(h, kSym)) {
                return reinterpret_cast<ProcessEventsToIdleFn>(f);
            }
        }
    }
    return nullptr;
}

template <typename Fn>
Fn resolveVclSymbol(const std::string& installPath, const char* symbol) {
    if (auto* f = dlsym(RTLD_DEFAULT, symbol)) {
        return reinterpret_cast<Fn>(f);
    }
    for (const char* lib : {"/libvcllo.so", "/libmergedlo.so"}) {
        const std::string path = installPath + lib;
        if (void* h = dlopen(path.c_str(), RTLD_NOW | RTLD_NOLOAD | RTLD_GLOBAL)) {
            if (auto* f = dlsym(h, symbol)) {
                return reinterpret_cast<Fn>(f);
            }
        }
    }
    return nullptr;
}
}  // namespace

struct LokEngine::Impl {
    lok::Office* office = nullptr;
    lok::Document* doc = nullptr;
    ProcessEventsToIdleFn pump = nullptr;
    AcquireSolarMutexFn acquireSolarMutex = nullptr;
    ReleaseSolarMutexFn releaseSolarMutex = nullptr;
};

LokEngine::LokEngine() : impl_(new Impl) {}

LokEngine::~LokEngine() {
    delete impl_->doc;  // free the open document
    // Intentionally do NOT destroy the Office. LOK is one-Office-per-process with a fragile
    // shutdown path (DeInitVCL); the Office lives for the process lifetime and is reclaimed at
    // exit. Destroying it here aborts (observed: SIGABRT on teardown).
    delete impl_;
}

bool LokEngine::init(const std::string& installPath, const std::string& profileUrl) {
    // Canonicalize the install path. LO's bootstrap builds file:// URLs from it, and a path
    // containing ".." (e.g. ".../app/../libreoffice-codebase/...") breaks that URL resolution,
    // silently degrading the engine so documents load BLANK. realpath() strips the "..".
    char* real = realpath(installPath.c_str(), nullptr);
    const std::string inst = real ? std::string(real) : installPath;
    free(real);

    impl_->office = lok::lok_cpp_init(inst.c_str(), profileUrl.c_str());
    if (!impl_->office) {
        return false;
    }
    impl_->pump = resolvePump(inst);
    impl_->acquireSolarMutex =
        resolveVclSymbol<AcquireSolarMutexFn>(inst, "_ZN11Application17AcquireSolarMutexEj");
    impl_->releaseSolarMutex =
        resolveVclSymbol<ReleaseSolarMutexFn>(inst, "_ZN11Application17ReleaseSolarMutexEv");
    return impl_->pump && impl_->acquireSolarMutex && impl_->releaseSolarMutex;
}

bool LokEngine::loadDocument(const std::string& fileUrl) {
    if (!impl_->office) {
        return false;
    }
    delete impl_->doc;
    impl_->doc = impl_->office->documentLoad(fileUrl.c_str(), "Language=en-US");
    if (!impl_->doc) {
        return false;
    }
    impl_->doc->initializeForRendering(nullptr);  // required before tiled rendering
    long w = 0, h = 0;
    impl_->doc->getDocumentSize(&w, &h);  // force initial formatting/layout (synchronous)
    return true;
}

void LokEngine::pumpToIdle() {
    if (impl_->pump && impl_->acquireSolarMutex && impl_->releaseSolarMutex) {
        impl_->acquireSolarMutex(1);
        impl_->pump();
        impl_->releaseSolarMutex();
    }
}

void LokEngine::dispatch(const std::string& unoCommand, const std::string& argsJson) {
    if (!impl_->doc) {
        return;
    }
    // LOK's own desktop tests pair postUnoCommand() with Scheduler::ProcessEventsToIdle().
    // Selection updates are otherwise visible only after incidental host-side delay. Enter the
    // public VCL pump while holding the public Application SolarMutex.
    impl_->doc->postUnoCommand(unoCommand.c_str(),
                               argsJson.empty() ? nullptr : argsJson.c_str(),
                               /*bNotifyWhenFinished=*/true);
    pumpToIdle();
}

std::string LokEngine::selectedText() {
    if (!impl_->doc) {
        return std::string();
    }
    char* text = impl_->doc->getTextSelection("text/plain;charset=utf-8", nullptr);
    std::string out = text ? std::string(text) : std::string();
    if (text) {
        impl_->office->freeMemory(text);
    }
    return out;
}

bool LokEngine::saveAs(const std::string& fileUrl, const std::string& filterName) {
    if (!impl_->doc) {
        return false;
    }
    return impl_->doc->saveAs(fileUrl.c_str(), filterName.c_str(), nullptr);
}

bool LokEngine::isReady() const { return impl_->office && impl_->doc; }

}  // namespace mw

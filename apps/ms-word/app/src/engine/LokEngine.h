#pragma once

#include <string>

#include "core/RenderEngine.h"  // IRenderEngine, TwipRect, TileCache::Bytes

namespace mw {

// The LOK engine binding — the ONLY code that talks to LibreOfficeKit (Boundary A). Meant to
// run on the single dedicated LOK-owning thread. Wraps lok::Office / lok::Document and provides
// the synchronous step boundary the rest of the app observes: every dispatch() posts the UNO
// command and then pumps the VCL scheduler to idle so the document is settled before any read.
//
// Grounded in LO source (docs/engine-revendor-impact.md + the restored libreofficekit/qa +
// desktop/qa/desktop_lib reference): one Office per process; the pump is the REAL public
// Scheduler::ProcessEventsToIdle() — explicitly NOT the banned test-only
// `unit_lok_process_events_to_idle` symbol the prior prototype dlsym'd.
class LokEngine : public IRenderEngine {
public:
    LokEngine();
    ~LokEngine() override;
    LokEngine(const LokEngine&) = delete;
    LokEngine& operator=(const LokEngine&) = delete;

    // --- IRenderEngine: the render-path seam RenderController consumes ---
    // Document size in twips (0, 0, width, height).
    TwipRect documentSize() const override;
    // Render the document region `tileRectTwips` into a pixelW x pixelH buffer (BGRA, premul on
    // Linux) and return its bytes. The caller (RenderController) chooses the px/twip ratio == zoom.
    TileCache::Bytes paintTile(const TwipRect& tileRectTwips, int pixelW, int pixelH) override;

    // Boot LOK against the built engine. installPath = ".../instdir/program";
    // profileUrl = a writable "file://" URL for the user profile. One Office per process.
    bool init(const std::string& installPath, const std::string& profileUrl);

    // Load a document from a "file://" URL; calls initializeForRendering(). Replaces any open doc.
    bool loadDocument(const std::string& fileUrl);

    // Dispatch a .uno: command, then pump the scheduler to idle (the synchronous step boundary).
    void dispatch(const std::string& unoCommand, const std::string& argsJson = std::string());

    // The current text selection as plain text (after .uno:SelectAll + dispatch == the body text).
    std::string selectedText();

    // Save the open document to a "file://" URL with the given LO filter name (e.g.
    // "MS Word 2007 XML"). Returns the engine's success flag.
    bool saveAs(const std::string& fileUrl, const std::string& filterName);

    bool isReady() const;

private:
    void pumpToIdle();  // real Scheduler::ProcessEventsToIdle()

    struct Impl;
    Impl* impl_;
};

}  // namespace mw

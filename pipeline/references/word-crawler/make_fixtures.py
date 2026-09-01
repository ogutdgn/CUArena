"""Create p0-blank.docx and p0-text.docx once. Run from repo root:
   python parity/tools/ui_crawl/make_fixtures.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import config
from launcher import WordSession

config.FIXTURES.mkdir(parents=True, exist_ok=True)
s = WordSession.start()
s.doc.SaveAs2(str(config.FIXTURES / "p0-blank.docx"))
s.doc.Content.Text = "Alpha paragraph for selection.\rBravo paragraph, bold target.\r"
assert s.doc.Paragraphs.Count >= 2, "fixture must have >=2 paragraphs"
s.doc.Paragraphs(2).Range.Font.Bold = True
s.doc.SaveAs2(str(config.FIXTURES / "p0-text.docx"))
s.close()
print("fixtures written")

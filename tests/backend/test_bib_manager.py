from backend.app.models.core import Reference
from backend.app.services.bib_manager import BibManager


def test_bib_manager_deduplicate_and_format(tmp_path):
    references = [
        Reference(
            key="smith2020",
            title="Deep Learning for Science",
            authors=["Jane Smith"],
            venue="Science Journal",
            year=2020,
            doi="10.1000/dls",
            url="https://doi.org/10.1000/dls",
            source="crossref",
        ),
        Reference(
            key="smith2020",
            title="Deep Learning for Science",
            authors=["Jane Smith"],
            venue="Science Journal",
            year=2020,
            doi=None,
            url=None,
            source="openalex",
        ),
    ]
    manager = BibManager()
    db = manager.deduplicate(references)
    assert len(db.entries) == 1
    bibtex = manager.to_bibtex(db)
    assert "@article" in bibtex
    assert "10.1000/dls" in bibtex

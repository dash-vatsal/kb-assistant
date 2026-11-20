from kb.chunking import chunk_document, split_sections


def test_headings_become_paths():
    md = "# Title\n\nintro text that is long enough to keep around here.\n\n## Sub\n\nsub body that is long enough to keep around."
    secs = split_sections(md)
    assert [p for p, _ in secs] == ["Title", "Title > Sub"]


def test_long_section_is_split_and_overlaps():
    body = "\n\n".join(f"Paragraph {i} " + "x" * 300 for i in range(20))
    chunks = chunk_document("Doc", "# Doc\n\n" + body, target=1000, overlap=100)
    assert len(chunks) > 3
    assert all(len(c.text) <= 1300 for c in chunks)
    assert all(c.embed_text.startswith("Doc > Doc") for c in chunks)


def test_tiny_chunks_dropped():
    assert chunk_document("T", "# T\n\nhi") == []


def test_code_block_hashes_not_headings():
    md = "# T\n\n```\n# not a heading\n```\n\nsome sufficiently long body text for the chunker to keep."
    assert len(split_sections(md)) == 1

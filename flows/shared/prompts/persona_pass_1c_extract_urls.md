You are extracting primary text URLs from a merged research dossier about {{ name }}.

The dossier was produced by merging three independent research sources (Perplexity, Claude Deep Research, and Gemini). Each source may have included URLs to digitized primary texts in their Section 6 (PRIMARY TEXTS) output.

Your job: scan the entire merged dossier and extract every URL that points to a digitized primary text — that is, a machine-readable full text or substantial excerpt of a work BY or ABOUT this figure that the downstream pipeline can fetch and use for voice-grounding.

INCLUDE:
- Links to Perseus Digital Library, Project Gutenberg, archive.org, Wikisource, LacusCurtius, Sacred Texts, HathiTrust, JSTOR open-access, government archives, institutional repositories
- Links to specific works (dialogues, essays, novels, speeches, legal documents, scientific papers)
- DOI links to open-access scientific papers (for non-human organism voices)

EXCLUDE:
- Links to secondary scholarship ABOUT the figure (Wikipedia pages, encyclopedia entries, book reviews, Amazon pages)
- Links to paywalled content that cannot be freely fetched
- Links to image-only resources (coin photographs, relief images) — these are material culture, not fetchable text
- Links to video or audio content

Return a JSON object:

```json
{
  "primary_text_urls": [
    {
      "url": "https://...",
      "title": "Short title of the work or edition",
      "note": "One-sentence description of what this contains and why it's useful"
    }
  ],
  "extraction_notes": "Brief note on what you found — e.g. 'Found 8 URLs across all three sources; 3 were duplicates; 2 were secondary scholarship excluded.'"
}
```

If no primary text URLs are found in the dossier, return an empty array and note why in extraction_notes.

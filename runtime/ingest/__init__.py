"""AI Assembly Ingest — audio upload web app for conference producers.

Accepts audio from producers, normalizes it to 96 kbps mono AAC per spec,
writes it to the canonical `runs/{run}/01_transcription/{session_id}/`
layout, generates a session.json by joining sessions.json + speakers.json,
and triggers Stage 0 transcription as a detached subprocess.
"""

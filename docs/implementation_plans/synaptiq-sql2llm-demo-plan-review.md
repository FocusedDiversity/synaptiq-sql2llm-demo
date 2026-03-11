# Review: synaptiq-sql2llm-demo-plan.md

## Overall Assessment

Well-structured, comprehensive plan for a full-stack NL-to-SQL demo app. The scope is clearly defined, tech choices are sensible, and implementation order is logical. Ready for implementation with the recommendations below.

---

## Strengths

1. **Clear project structure** — Detailed file tree with clean separation of concerns (routes, services, prompts, seed generators).
2. **Two-call LLM optimization** — Combining viz recommendation + insight into a single Claude call is a smart latency reduction.
3. **Deterministic seeding** (`random.seed(42)`) — Ensures reproducible data, great for demos and debugging.
4. **SQL safety via whitelist** — SELECT-only validation is appropriate for a read-only demo.
5. **Realistic domain model** — 38 tables across 12 domains gives meaningful query diversity.
6. **Concrete verification steps** — Specific commands to validate the setup end-to-end.
7. **Implementation dependency table** — Clear ordering with explicit dependencies.

---

## Issues & Recommendations

### 1. Missing Error Handling Strategy (High Priority)

The plan doesn't address what happens when:
- Claude generates invalid SQL
- SQL passes validation but fails execution
- The API key is missing/invalid

**Recommendation:** Add retry logic or user-friendly error messages for bad SQL generation. Consider a fallback prompt if the first SQL attempt fails.

### 2. No Rate Limiting or Cost Controls (Medium Priority)

No mention of:
- Request rate limiting on the backend
- Token budget caps to prevent runaway costs
- Caching repeated queries (same NL input → cached response)

Even for a local demo, query caching would significantly improve the experience and reduce API costs.

### 3. Database Schema Size vs. Context Window (Medium Priority)

Sending the **full schema of 38 tables** as context in every NL-to-SQL call could consume significant tokens. Consider:
- Schema summarization or selective table inclusion based on the query
- At minimum, document the expected token count for the schema context

### 4. Missing Testing Strategy (High Priority)

Step 12 says "End-to-end testing and README" but doesn't specify:
- Unit tests for SQL validation service
- Unit tests for seed data generators (do they produce expected counts?)
- Integration tests for API endpoints
- Test frameworks (pytest? vitest?)

**Recommendation:** Add a testing section to the plan with framework choices and key test cases.

### 5. `ddx-library` Submodule Purpose Unclear (Low Priority)

The plan says it's "not a runtime dependency" but doesn't explain why it exists. If unused, consider removing it to avoid confusion. If used (e.g., shared types or utilities), document how.

### 6. No `.env` Variable Documentation (Medium Priority)

`.env.example` is listed but the plan doesn't specify variables. Based on `config.py` (pydantic-settings), should document:
- `ANTHROPIC_API_KEY`
- `DATABASE_PATH` (default: `data/carwash.db`)
- `CLAUDE_MODEL` (default model name)

### 7. Frontend Build/Deploy Not Addressed (Low Priority)

The plan covers dev mode (Vite proxy) but doesn't mention:
- Production build (`npm run build`)
- How FastAPI would serve the built frontend

Fine if purely a local dev demo, but worth stating explicitly.

### 8. Seed Data Volume (Low Priority)

~26,000+ records seeded across multiple tables. This is fine for SQLite but:
- Document expected seed time
- `setup.sh` should give progress feedback during seeding

### 9. Visualization Gaps (Low Priority)

Bar, Line, and Pie charts are listed, but some queries would benefit from:
- **Scatter plots** (e.g., correlation between rating and spend)
- **Stacked bar charts** (e.g., revenue by package by month)

Consider mentioning these as future extensions.

### 10. LIMIT 500 May Silently Truncate Results (Medium Priority)

For detail-level queries, `LIMIT 500` could truncate results without user awareness.

**Recommendation:** Add a `truncated: boolean` flag in the API response so the frontend can inform the user.

---

## Minor Nits

- `run.sh` should handle process cleanup (SIGTERM to both backend/frontend on Ctrl+C)
- `python -m backend.seed` entry point should be explicitly called in `setup.sh`
- Consider adding a `Makefile` as an alternative to shell scripts for cross-platform support

---

## Verdict

**The plan is solid and ready for implementation** with the above recommendations incorporated. The most impactful additions would be:

1. Error handling strategy for failed SQL generation
2. Query result caching
3. A basic testing strategy with framework choices and key test cases

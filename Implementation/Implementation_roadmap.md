## Implementation Roadmap/Checklist

> See [Readme.md](Readme.md) for the full workflow overview.

---

## Roadmap

### Phase 1 — Python based proof of concept *(current)*
- [ ] AES encryption using PyCryptodome
- [ ] AES decryption using PyCryptodome
- [ ] Random grid generation and ciphertext embedding
- [ ] Grid extraction and ciphertext recovery
- [ ] SecretKey dataclass, serialization/deserialization

### Phase 2 — Testing
- [ ] Unit tests for each module (Encryption + Decryption)
- [ ] Integration tests: full encrypt → transmit → decrypt round-trip
- [ ] Edge case tests: empty plaintext, max grid size, invalid keys
- [ ] Convert the python based proof of concept → reference implementation
- [ ] Verify C output matches Python reference implementation

### Phase 3 — C Library Implementation


### Phase 4 — Integration and CI Pipeline
- [ ] Build C library (cmake + ninja) via GitHub Actions
- [ ] Install Python deps + run pytest via GitHub Actions
- [ ] Integration tests: Python test suite calls C library via cffi
- [ ] Coverage reporting
- [ ] cffi bindings to call C library from Python

---
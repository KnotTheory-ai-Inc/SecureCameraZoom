## Implementation Roadmap/Checklist

> See [Readme.md](Readme.md) for the full workflow overview.

---

## Roadmap

### Phase 1 — Python based proof of concept *(current)*
- [ ] Level-1 encryption
- [ ] Level-1 decryption
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
- [ ] Install Python deps + run pytest via GitHub Actions
- [ ] Build python library
- [ ] Unit and Integration tests: Python test suite
- [ ] Coverage reporting

---
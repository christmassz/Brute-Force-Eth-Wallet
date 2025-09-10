# Background and Motivation
The user needs a brute-force utility that iterates over all BIP-39 English words for the 5th position of a known 24-word mnemonic, checking for the correct address.  This is an ad-hoc recovery scenario, not a production feature.

# Key Challenges and Analysis
- Need to load an almost-complete mnemonic from YAML while allowing one blank slot.
- Validate candidate mnemonics efficiently (wordlist, checksum).
- Derive Ethereum address with existing `WalletDeriver`, trying standard paths.

# High-level Task Breakdown
- [x] Create dedicated YAML config (`data/wallets/wallet_word5.yaml`) with blank 5th word.
  - Success criteria: YAML contains 24 elements with one empty string; lints clean.
- [x] Implement script `test2.py` at repo root.
  - Success criteria: imports resolve, no linter errors, runs without arguments, brute-forces over 2,048 words.
- [ ] Manual test / user confirmation that script finds or does not find the mnemonic.

# Project Status Board
- [x] Add YAML config for 5th word search
- [x] Add brute-force script `test2.py`
- [ ] Await user to execute script and verify results

# Current Status / Progress Tracking
Executor has implemented the YAML config and brute-force script.  Linter passes locally.

# Executor's Feedback or Assistance Requests
Please run `python test2.py` and confirm whether it identifies the correct mnemonic.  Let me know the outcome or provide any errors encountered so I can address them.

# Lessons
- Reused existing validation and derivation classes to avoid duplicate logic.

[OUTDATED] Previous project scope (word 5 brute-force) completed pending user verification.

---

# Background and Motivation (Trial 3)
The client now provides **correct words 10-24** (14 words, correct order). Words **1-9** are jumbled and **exactly one** of those nine words is incorrect. Additionally, we have a pool of **30 potential replacement words** that may contain the missing correct word. We must brute-force all possibilities to find the full 24-word mnemonic that produces the target Ethereum address.

# Key Challenges and Analysis (Trial 3)
- Search space **updated**: With the wrong index known, we have 30 replacement candidates × permutations of the remaining 8 known-but-scrambled words (8! = 40,320) → **≈ 1.2 M** mnemonics before checksum pruning. Much smaller than previous 98 M.
- Need efficient generation & checksum validation similar to existing `WalletRecovery`, but adapted for 9-word permutations and one-word substitution.
- YAML config must support:
  - `fixed_words` (positions 10-24, 14 items, correct order)
  - `scrambled_words` (list of 9 items for positions 1-9, **use an empty string "" at the known wrong index**)  
    e.g. `scrambled_words: ["wordA", "", "wordB", ...]`
  - `replacement_pool` (30 candidate words)
  - `target_address`, optional `derivation_path`, and settings.
- Script `trial3.py` should reuse `MnemonicHandler` & `WalletDeriver` with minimal duplication.
- Chunking/progress bar due to large search space.
- Unit tests to verify generation logic on small toy cases.

# High-level Task Breakdown (Trial 3)
- [ ] 1. Create YAML template `data/wallets/wallet_trial3.yaml` with example fields, **including blank string for the known-wrong index**.
      Success: file exists, lints, and loads via `yaml.safe_load`.
- [ ] 2. Implement combination generator utility:
        a. Insert each replacement word from pool into the blank slot.
        b. Generate permutations of the other 8 scrambled words (8!).
      Success: given toy words it yields correct total count and no duplicates.
- [ ] 3. Create `trial3.py`:
        a. Parse YAML, initialise `MnemonicHandler`, `WalletDeriver`.
        b. Stream candidate mnemonics, validate checksum, derive address(s).
      Success: runnable with no args, uses YAML path default, logs progress.
- [ ] 4. Unit tests under `tests/` covering:
        a. Word-list validation for YAML words.
        b. Generator counts on mock data (e.g., 3 scrambled, 2 pool → expected combos).
      Success: `pytest` passes.
- [ ] 5. Documentation: update README with Trial 3 usage section.
- [ ] 6. Manual run checklist & user confirmation.

# Project Status Board
- [ ] Trial 3 – YAML template created
- [ ] Trial 3 – Generator utility implemented
- [ ] Trial 3 – `trial3.py` main script implemented
- [ ] Trial 3 – Unit tests written & passing
- [ ] Trial 3 – User manual run & verification

# Current Status / Progress Tracking
Planner phase: requirements analysed, tasks enumerated. Awaiting user approval to proceed to Executor mode.

# Executor's Feedback or Assistance Requests
(none – planner phase)

# Lessons
- Extend existing modular architecture to new search formulas to avoid code duplication.

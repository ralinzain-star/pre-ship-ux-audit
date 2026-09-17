# Sections

This file defines the four audit layers, their ordering, impact levels, and
descriptions. The section ID (in parentheses) is the filename prefix used to
group rules.

Every finding belongs to exactly one layer. If a finding fits none of them, it is
a visual preference rather than an audit finding, and it should be dropped.

---

## 1. Flow Integrity (flow)

**Impact:** CRITICAL
**Description:** Broken steps or missing states. A user who cannot start, cannot
continue, or hits an undesigned state is blocked, and no amount of polish
elsewhere recovers that.

## 2. Control & Transparency (control)

**Impact:** CRITICAL
**Description:** Whether the user feels in control of the system. Covers exits,
undo, confirmation on irreversible actions, and whether the system explains what
it is doing and what it has done.

## 3. Trust & Copy (trust)

**Impact:** MAJOR
**Description:** Whether the experience builds confidence rather than anxiety.
Covers error messages, plain language, stated reasons behind system decisions,
and specific calls to action.

## 4. Edge Cases (edge)

**Impact:** MAJOR
**Description:** What happens when things go wrong. Missing data, network
failure, duplicate actions, interruptions, and the difference between a
first-time and a returning user.

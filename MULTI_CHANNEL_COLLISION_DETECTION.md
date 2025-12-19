# Multi-Channel Spatial Collision Detection for MEP Placement

## The Core Idea

Instead of asking "does equipment A collide with equipment B?" for every pair (O(n²) comparisons), we ask "what exists at each cell?" and let the grid answer all collision questions simultaneously.

Think of it like layers in Photoshop or GIS—each channel represents a different spatial property, and we combine them with simple arithmetic to detect constraint violations.

---

## The Channel Stack

Imagine the room as a stack of transparent sheets, each tracking one property:

```
        ┌─────────────────────────┐
       ╱                         ╱│
      ╱   Channel 3: Clearances ╱ │
     ├─────────────────────────┤  │
    ╱                         ╱│  │
   ╱   Channel 2: Cores      ╱ │  │
  ├─────────────────────────┤  │  │
 ╱                         ╱│  │  │
╱   Channel 1: Paths      ╱ │  │  ╱
├─────────────────────────┤  │  ╱
│                         │  │ ╱
│   Channel 0: Boundary   │  │╱
│                         │  ╱
│                         │ ╱
└─────────────────────────┴╱
```

Each cell (x, y) has a value in every channel. Reading the stack at any position tells you everything about that location.

---

## Channel Definitions

| Channel | Name | Cell Values | Purpose |
|---------|------|-------------|---------|
| 0 | **Boundary** | 0 or 1 | Defines room shape (1 = inside) |
| 1 | **Paths** | 0 or 1 | Access corridors (1 = path) |
| 2 | **Cores** | 0 or equipment ID | Which equipment's solid body occupies this cell |
| 3 | **Clearances** | 0, 1, 2, ... | Count of overlapping clearance zones |

---

## Equipment Anatomy

Each piece of equipment projects onto multiple channels:

```
Equipment "AHU" (ID = 1)
Clearances: North=2, South=1, East=1, West=1

Physical Representation:          Channel Projections:

     clearance                    CORES Channel:    CLEARANCES Channel:
    ┌─────────────┐               ┌───────────┐     ┌─────────────┐
    │ · · · · · · │               │ 0 0 0 0 0 │     │ 1 1 1 1 1 1 │
    │ · · · · · · │               │ 0 0 0 0 0 │     │ 1 1 1 1 1 1 │
    │ · ┌─────┐ · │               │ 0 1 1 1 0 │     │ 1 0 0 0 0 1 │
    │ · │ AHU │ · │   ──────►     │ 0 1 1 1 0 │     │ 1 0 0 0 0 1 │
    │ · └─────┘ · │               │ 0 0 0 0 0 │     │ 1 1 1 1 1 1 │
    └─────────────┘               └───────────┘     └─────────────┘
                                  (ID where core    (1 in clearance
                                   exists)           zone only)
```

The core channel stores the equipment ID (enabling "who is here?" queries).
The clearance channel stores counts (enabling "how many clearances overlap?" queries).

---

## The Mathematics of Constraint Checking

Each constraint becomes a simple logical or arithmetic operation on channels.

### Constraint 1: Cores Must Stay Inside Room

**Question:** Does the equipment core extend outside the room boundary?

**Operation:**

$$\text{violation} = \text{Core}_{\text{new}} \land \lnot\text{Boundary}$$

**Visual:**
```
New Core          Boundary           Result (AND NOT)
┌─────────┐       ┌─────────┐        ┌─────────┐
│ 0 0 0 0 │       │ 1 1 1 0 │        │ 0 0 0 0 │
│ 0 1 1 1 │   ∧   │ 1 1 1 0 │   =    │ 0 0 0 1 │ ← VIOLATION!
│ 0 1 1 1 │  NOT  │ 1 1 0 0 │        │ 0 0 1 1 │ ← Core outside
│ 0 0 0 0 │       │ 1 1 0 0 │        │ 0 0 0 0 │
└─────────┘       └─────────┘        └─────────┘

If any cell > 0: INVALID
```

---

### Constraint 2: Cores Cannot Overlap Each Other

**Question:** Would placing this core overlap an existing core?

**Operation:**

$$\text{violation} = \text{Core}_{\text{new}} \land (\text{Cores}_{\text{existing}} > 0)$$

**Visual:**
```
New Core          Existing Cores     Result (AND)
┌─────────┐       ┌─────────┐        ┌─────────┐
│ 0 0 0 0 │       │ 0 0 0 0 │        │ 0 0 0 0 │
│ 0 1 1 0 │   ∧   │ 0 0 2 2 │   =    │ 0 0 1 0 │ ← COLLISION!
│ 0 1 1 0 │       │ 0 0 2 2 │        │ 0 0 1 0 │
│ 0 0 0 0 │       │ 0 0 0 0 │        │ 0 0 0 0 │
└─────────┘       └─────────┘        └─────────┘

If any cell > 0: INVALID (cores overlap)
```

---

### Constraint 3: Cores Cannot Block Paths

**Question:** Does the equipment core sit on an access path?

**Operation:**

$$\text{violation} = \text{Core}_{\text{new}} \land \text{Paths}$$

**Visual:**
```
New Core          Paths              Result (AND)
┌─────────┐       ┌─────────┐        ┌─────────┐
│ 0 0 0 0 │       │ 0 0 0 0 │        │ 0 0 0 0 │
│ 0 1 1 0 │   ∧   │ 1 1 1 1 │   =    │ 0 1 1 0 │ ← BLOCKED!
│ 0 1 1 0 │       │ 0 0 0 0 │        │ 0 0 0 0 │
│ 0 0 0 0 │       │ 0 0 0 0 │        │ 0 0 0 0 │
└─────────┘       └─────────┘        └─────────┘

If any cell > 0: INVALID (core blocks path)
```

---

### Constraint 4: Clearances Cannot Be Blocked by OTHER Cores

**Question:** Does my clearance zone overlap another equipment's core?

**Operation:**

$$\text{violation} = \text{Clearance}_{\text{new}} \land (\text{Cores} > 0) \land (\text{Cores} \neq \text{my\_id})$$

**Visual:**
```
My Clearance      Other Cores        Result
(equipment 1)     (equipment 2)
┌─────────┐       ┌─────────┐        ┌─────────┐
│ 1 1 1 1 │       │ 0 0 0 0 │        │ 0 0 0 0 │
│ 1 0 0 1 │   ∧   │ 0 0 2 2 │   =    │ 0 0 0 1 │ ← BLOCKED!
│ 1 0 0 1 │       │ 0 0 2 2 │        │ 0 0 0 1 │
│ 1 1 1 1 │       │ 0 0 0 0 │        │ 0 0 0 0 │
└─────────┘       └─────────┘        └─────────┘

If any cell > 0: INVALID (can't access equipment for maintenance)
```

---

### Non-Constraint: Clearances MAY Overlap Paths

This is explicitly **allowed**—you can walk through a clearance zone.

```
My Clearance      Paths              Result
┌─────────┐       ┌─────────┐        ┌─────────┐
│ 1 1 1 1 │       │ 0 0 0 0 │        │ 0 0 0 0 │
│ 1 0 0 1 │   ∧   │ 1 1 1 1 │   =    │ 1 0 0 1 │ ← OK! (allowed)
│ 1 0 0 1 │       │ 0 0 0 0 │        │ 0 0 0 0 │
│ 1 1 1 1 │       │ 0 0 0 0 │        │ 0 0 0 0 │
└─────────┘       └─────────┘        └─────────┘

No violation check needed—this is valid by design.
```

---

### Non-Constraint: Clearances MAY Overlap Each Other

Two technicians can share space. We track the count but don't reject it.

```
Clearance A       Clearance B        Sum (Count)
┌─────────┐       ┌─────────┐        ┌─────────┐
│ 1 1 1 0 │       │ 0 0 1 1 │        │ 1 1 2 1 │
│ 1 0 1 0 │   +   │ 0 0 1 1 │   =    │ 1 0 2 1 │ ← 2 means overlap
│ 1 1 1 0 │       │ 0 0 1 1 │        │ 1 1 2 1 │    (allowed)
│ 0 0 0 0 │       │ 0 0 0 0 │        │ 0 0 0 0 │
└─────────┘       └─────────┘        └─────────┘

No maximum threshold—clearance stacking is permitted.
```

---

## Batch Validation: The Power of Summation

When checking an entire configuration, sum all cores into one aggregate mask:

$$\text{AllCores} = \sum_{i=1}^{n} \text{CoreMask}_i$$

```
Equipment 1       Equipment 2       Equipment 3       Sum
┌─────────┐       ┌─────────┐       ┌─────────┐       ┌─────────┐
│ 1 1 0 0 │       │ 0 0 0 0 │       │ 0 0 0 0 │       │ 1 1 0 0 │
│ 1 1 0 0 │   +   │ 0 0 1 1 │   +   │ 0 1 1 0 │   =   │ 1 2 2 1 │
│ 0 0 0 0 │       │ 0 0 1 1 │       │ 0 1 1 0 │       │ 0 1 2 1 │
│ 0 0 0 0 │       │ 0 0 0 0 │       │ 0 0 0 0 │       │ 0 0 0 0 │
└─────────┘       └─────────┘       └─────────┘       └─────────┘
                                                           ↑
                                                     max = 2 > 1
                                                     ∴ OVERLAP!
```

**Rule:** If max(AllCores) > 1, at least two cores overlap somewhere.

This validates all pairwise core collisions in **O(n)** instead of O(n²).

---

## Constraint Summary Table

| Constraint | Mathematical Form | Valid Condition |
|------------|-------------------|-----------------|
| Core inside room | $C_{\text{new}} \land \lnot B$ | $= 0$ everywhere |
| Core-core collision | $C_{\text{new}} \land (C_{\text{all}} > 0)$ | $= 0$ everywhere |
| Core blocks path | $C_{\text{new}} \land P$ | $= 0$ everywhere |
| Clearance blocked | $L_{\text{new}} \land (C_{\text{all}} > 0) \land (C_{\text{all}} \neq \text{id})$ | $= 0$ everywhere |
| Batch core overlap | $\sum C_i$ | $\max \leq 1$ |

Where:
- $C$ = Core mask
- $B$ = Boundary mask
- $P$ = Path mask
- $L$ = Clearance mask

---

## Why This Works

1. **Spatial Hashing**: The grid discretizes space into cells. Each cell is a bucket that knows its contents.

2. **Projection**: 3D objects (equipment with clearances) project onto 2D channel layers, separating concerns.

3. **Superposition**: Multiple properties can coexist at the same cell (clearance count = 3 means three equipment need that space for access).

4. **Set Operations via Arithmetic**:
   - AND → multiplication or `min(a, b)`
   - OR → `max(a, b)` or addition with clipping
   - COUNT → summation

5. **Parallelism**: All cells are independent—operations vectorize perfectly on GPU/TPU.

---

## Complexity Comparison

| Approach | Add Equipment | Check All Pairs | Memory |
|----------|---------------|-----------------|--------|
| Pairwise loops | O(1) | O(n²) | O(n) |
| Channel grid | O(cells in equip) | O(grid size) | O(grid size × channels) |

For a 100×100 room with 50 equipment pieces:
- Pairwise: 50 × 49 / 2 = **1,225 comparisons**
- Channel: 10,000 cells × 4 channels = **40,000 operations** (but vectorized, so ~instant)

The channel approach wins dramatically as equipment count grows, and enables batch validation of entire configurations in a single pass.

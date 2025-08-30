# Microcode Definition Language (MDL) - Specification

## 1. Overview

The Microcode Definition Language (MDL) is a domain-specific language designed to generate patterns for microcode ROMs. It provides a clear, expressive, and maintainable way to define bit fields, constants, and iterative patterns. A fundamental concept is the distinction between **signals** (single-bit flags) and **fields** (multi-bit values) and tools to provide an iterated pattern generator.

## 2. Core Concepts

### 2.1. Comments
Comments are ignored by the compiler/parser. They can be placed on their own line or at the end of a line.
```microcode
/* This is a single-line comment */
signal example : 3; /* This is an end-of-line comment */
```

### 2.2. Signals
A `signal` represents a single, specific bit in the control word. Its declaration defines its position. **Including a signal's name in a pattern block means that single bit is set to `1`.** Signals are not assigned a value; they are either activated (present) or not (absent).

**Syntax:**
```
signal <name> : <bit_position>;
```

**Usage in Pattern:**
```microcode
pattern "..." {
    <signal_name>; /* This sets the bit at <bit_position> to 1. */
}
```

**Example:**
```microcode
signal alu_en   : 0;  /* Bit 0 is the ALU enable flag */
signal mem_read : 7;  /* Bit 7 is the memory read flag */

pattern "00001111" {
    alu_en;   /* Bit 0 is set to 1. */
    mem_read; /* Bit 7 is set to 1. */
}
```

### 2.3. Fields
A `field` represents a multi-bit slice of the control word, used for multi-value controls like ALU operations or register selects. Unlike signals, fields **are** assigned a value.

**Syntax:**
```
field <name> : [<msb>:<lsb>];
```

**Usage in Pattern:**
```microcode
pattern "..." {
    <field_name> : <value>; /* Assigns <value> to the bits [msb:lsb] */
}
```

**Example:**
```microcode
field alu_op  : [5:2]; /* A 4-bit field controlling the ALU (bits 5,4,3,2) */
field reg_dst : [9:7]; /* A 3-bit field for the destination register */

pattern "00000000" {
    alu_op : 0b1010; /* Bits 5,4,3,2 are set to 1010. */
}
```

### 2.4. Constants
Constants (`const`) are named values that improve readability and maintainability by replacing "magic numbers."

**Syntax:**
```
const <NAME> = <value>;
```
`<value>` can be a decimal integer, a binary literal (`0b1010`), or a hexadecimal literal (`0xA`).

**Example:**
```microcode
const ALU_ADD  = 0b0000;
const ALU_SUB  = 0b0001;
const ALU_AND  = 0b0010;
```

## 3. Pattern Generation

### 3.1. Basic Pattern
A `pattern` block defines a specific microcode word or a template for generating multiple words.

**Syntax:**
```
pattern "<bit_pattern>" {
    [<signal_name>;]...
    [<field_name>  : <value>;]...
}
```
The `<bit_pattern>` is a string of `0`, `1`, and iterators (e.g., `{op:3}`).

**Example:**
```microcode
/* A simple, fixed pattern */
pattern "00001111" {
    alu_en;           /* Activate the ALU enable signal (bit 0) */
    alu_op : ALU_ADD; /* Assign the ALU_ADD constant to the alu_op field */
}
```

### 3.2. Iterators & Wildcards
Patterns can generate multiple words by using iterators and wildcards in the bit pattern string.

*   `{<name>:<width>}`: An iterator named `<name>` that generates all possible values for a `<width>`-bit field.
*   `-` (Dash): A wildcard bit, treated as "don't care". It does not generate multiple patterns but matches any value.

**Example:**
```microcode
/*
This will generate 8 (2^3) distinct patterns:
00000000, 00000001, 00000010, ..., 00000111
*/

pattern "00000{op:3}" {
    alu_en;        /* Set bit 0 for all generated patterns */
    alu_op : op;   /* Use the iterator's value for this field */
}

/* Use a wildcard for flexibility without generation */
pattern "1---0010" {
    mem_read; /* This is a single pattern where bits 6,5,4 are ignored. */
}
```

### 3.3. Assignments
Inside a pattern block:
*   List a **signal** to set its bit to `1`.
*   Assign a **field** a value using the `:` operator.

`<value>` can be a number, a constant, or an iterator name. `<expression>` can be a simple arithmetic or logical expression.

**Example:**
```microcode
pattern "00{src:2}{dst:2}" {
    alu_en;             /* Activate signal (set bit to 1) */
    alu_op   : ALU_ADD; /* Assign a constant to a field */
    reg_src  : src;     /* Assign an iterator value to a field */
    reg_dst  : dst + 1; /* Assign the result of an expression to a field */
}
```

## 4. Advanced Features

### 4.1. Default Block
A `default` block defines assignments that should be applied to *every* pattern unless explicitly overridden. This is useful for setting common default values (e.g., ensuring most signals are off by default).

**Syntax:**
```
default {
    [<signal_name>;]...    /* Signals to always activate */
    [<field_name>  : <value>;]... /* Fields to always set */
}
```
**Note:** A pattern can override a default field assignment but cannot "deactivate" a default signal. If a signal is listed in `default`, its bit is `1` in every output pattern. This makes `default` ideal for common enable signals but less so for signals that are usually off.

**Example:**
```microcode
/* A common clock signal is always pulsed */
default {
    clock_en; /* Set bit 0 to 1 in every pattern */
}

/* Patterns now only need to define other active signals */
pattern "00010001" {
    alu_en; /* clock_en is already active, alu_en is now also active. */
}
```

### 4.2. Pattern Groups
A `group` is a reusable pattern template. Patterns can inherit from a group to include its bit pattern and assignments, reducing code duplication.

**Syntax:**
```
group <group_name> "<bit_pattern>" {
    [<signal_name>;]...
    [<field_name>  : <value>;]...
}

pattern <group_name> {
    [<additional_assignments>] /* Inherits pattern and assignments from the group */
}
```

**Example:**
```microcode
/* Define a common group for ALU operations */
group alu_base "00{op:3}----" {
    alu_en;
    reg_write;
}

/* Patterns that build on the alu_base group 8/
pattern alu_base {
    alu_op : ALU_ADD; /* Final pattern: "00{op:3}----" with alu_en, reg_write, and alu_op set. */
}
```

### 4.3. Loop Generation
A `for` loop can be used to generate a series of patterns programmatically.

**Syntax:**
```
for <iterator_name> in <start>..<end> {
    pattern ... {
        ...]
    }
}
```

**Example:**
```microcode
/* Generate patterns for immediate values 0 to 7 */
for imm in 0..7 {
    pattern "01{imm:3}00" {
        use_immediate;
        immediate_value : imm;
    }
}
```

## 5. Full Example

```microcode
/* --- Microcode Definition --- */
signal clock_en : 0; /* Global clock enable */
signal alu_en   : 1; /* ALU Enable flag */
signal mem_write: 2; /* Memory Write flag */

field alu_op    : [5:3]; /* 3-bit field for ALU operation code */
field reg_addr  : [8:6]; /* 3-bit field for register address */

const ALU_ADD  = 0;
const ALU_SHIFT = 1;

/* The clock is enabled in every microinstruction */
default {
    clock_en;
}

/* Generate patterns for ALU operations on registers */
group reg_op "10{op:3}{reg:3}" {
    alu_en;
    reg_addr : reg;
}

pattern reg_op {
    alu_op : ALU_ADD; /* Pattern: "10{op:3}{reg:3}" with alu_en and clock_en active */
}

pattern reg_op {
    alu_op : ALU_SHIFT; /* Pattern: "10{op:3}{reg:3}" with alu_en and clock_en active */
}

/* A specific store operation */
pattern "11000101" {
    mem_write;        /* Activate the memory write signal */
    reg_addr : 0b101; /* Set register address to 5 */
                     /* (clock_en is active by default) */
}
```

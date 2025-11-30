# Automatic Short Name Generation for Research Groups

## Overview

When importing research groups from CSV files, some groups may not have a `Sigla` (short name) provided. The system now automatically generates meaningful short names using an acronym-based approach combined with campus codes.

## Generation Algorithm

### Step 1: Extract Significant Words
The algorithm filters out common articles, prepositions, and conjunctions in both Portuguese and English:

**Ignored words:**
- Portuguese: a, o, as, os, de, da, do, das, dos, em, no, na, nos, nas, e, ou, para, com, por, sobre, entre, sem, sob, ao, aos
- English: the, of, and, or, in, on, at, to, for, with, by, from

### Step 2: Create Acronym
Takes the first letter of each significant word and combines them into an acronym.

**Example:**
- "Análise e Desenvolvimento em Sistemas Mecânicos" → "ADSM"
  - Análise → A
  - Desenvolvimento → D
  - Sistemas → S
  - Mecânicos → M
  - (ignores: e, em)

### Step 3: Apply Length Constraints
- **Maximum length:** 10 characters (before campus code)
- **Minimum length:** 2 characters
  - If acronym is too short, uses first 2-4 characters of the first word

### Step 4: Append Campus Code
Adds a hyphen and the first 3 characters of the campus code for uniqueness.

**Format:** `{ACRONYM}-{CAMPUS_CODE}`

## Examples

| Group Name | Campus | Generated Short Name |
|------------|--------|---------------------|
| Ambiente Construído | Colatina | AC-COL |
| Análise e Desenvolvimento em Sistemas Mecânicos e Métodos Computacionais | Vitória | ADSMMC-VIT |
| Biodiversidade Urbana | Vitória | BU-VIT |
| Aplicações de Sistemas Inteligentes | Vitória | ASI-VIT |
| Biotecnologia e educação em meio ambiente, saúde e sustentabilidade | Vitória | BEMASS-VIT |
| Caracterização e Propriedades Físicas dos Materiais | Vitória | CPFM-VIT |
| Ciência e Tecnologia de Alimentos | Venda Nova do Imigrante | CTA-VEN |
| Clínica, Cirurgia e Reprodução Animal | Itapina | CCRA-ITA |
| Currículos, Culturas Juvenis e Processos de Subjetivação | Aracruz | CCJPS-ARA |

## Benefits

1. **Meaningful:** Acronyms are derived from the actual group name, making them recognizable
2. **Unique:** Campus code ensures uniqueness across different campuses
3. **Consistent:** Same algorithm applied to all groups without short names
4. **Readable:** Short enough to be practical, long enough to be meaningful

## Statistics from Current CSV

- **Total groups:** 328
- **Groups without Sigla:** 107 (32.6%)
- **Generated short names:** 107
- **Conflicts after generation:** 0 (excluding actual CSV duplicates)

## Implementation

The generation logic is implemented in:
- File: `apps/organizational_group/csv_import/group_handler.py`
- Method: `GroupHandler._generate_short_name(name, campus)`

## Usage

The short name generation is automatic during CSV import. No manual intervention is required.

```bash
python manage.py import_research_groups example/research_group/research_groups.csv
```

Groups without a `Sigla` column value will automatically receive a generated short name based on their full name and campus.

## Edge Cases

### Empty or Invalid Names
If a group name is empty or contains only whitespace, the system defaults to `"non-informed"`.

### Very Long Names
Acronyms longer than 10 characters are truncated to maintain readability.

### Single Word Names
If the name contains only one significant word, the first 2-4 characters of that word are used.

### Duplicate Entries
If the CSV contains actual duplicate entries (same short_name and campus), the import process will:
1. Import the first occurrence
2. Skip subsequent duplicates with a warning message

## Future Enhancements

Potential improvements for consideration:
1. Add sequential numbering for conflicts (e.g., "AC-COL-1", "AC-COL-2")
2. Allow custom acronym rules per knowledge area
3. Provide a preview mode to review generated names before import
4. Support manual override through a mapping file

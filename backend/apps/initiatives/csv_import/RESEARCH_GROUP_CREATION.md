# Research Group Creation During Initiative CSV Import

## Overview

When importing initiatives (research projects) from CSV, if a research group specified in the `GrupoPesquisaExterno` column doesn't exist in the database, it will be automatically created.

## Behavior

### When Research Group Doesn't Exist

If a research group name in **`GrupoPesquisa`** or **`GrupoPesquisaExterno`** is not found in the database, the system will:

1. **Create the research group** with the following properties:
   - **Name**: Normalized name from CSV (Title Case)
   - **Short Name**: Auto-generated acronym from the full name
   - **Type**: Research
   - **Organization**: "Default Organization"
   - **Campus**: Uses `CampusExecucao` from the CSV row
   - **Knowledge Area**: Uses `AreaConhecimento` from the CSV row (if provided)
   - **Leadership**: Created **without** any leaders

2. **Associate it** with the initiative as a partnership

### Campus Assignment

The campus for the newly created research group is determined by the `CampusExecucao` column in the CSV:

- **If `CampusExecucao` is provided**: Uses that campus name
  - If the campus doesn't exist, it will be created automatically
- **If `CampusExecucao` is empty**: Uses default "External" campus

## Example

### CSV Row:
```csv
CampusExecucao,Titulo,GrupoPesquisaExterno,AreaConhecimento
Serra,My Research Project,Grupo de Inteligência Artificial,Ciência da Computação
```

### Result:
If "Grupo de Inteligência Artificial" doesn't exist, it will be created with:
- **Name**: Grupo De Inteligência Artificial
- **Short Name**: GDIA (auto-generated)
- **Type**: Research
- **Organization**: Default Organization
- **Campus**: Serra (from CampusExecucao)
- **Knowledge Area**: Ciência Da Computação
- **Leaders**: None (no leadership assigned)

## CSV Columns for Research Groups

### GrupoPesquisa
- **Purpose**: Primary research group associated with the initiative
- **Behavior**: 
  - Looks up existing group first
  - If not found, creates it using `CampusExecucao`
  - Associates the initiative with this group
- **Format**: Single group name

### GrupoPesquisaExterno
- **Purpose**: External partnership research groups
- **Behavior**:
  - Looks up existing groups first
  - If not found, creates them using `CampusExecucao`
  - Associates as partnerships with the initiative
- **Format**: Multiple groups separated by commas

## Multiple Research Groups

The `GrupoPesquisaExterno` column supports multiple research groups separated by commas:

```csv
GrupoPesquisaExterno
Grupo A, Grupo B, Grupo C
```

Each group will be:
1. Created if it doesn't exist (using the same campus from `CampusExecucao`)
2. Associated with the initiative as a partnership

## Important Notes

### No Leadership Assigned

Research groups created during initiative import are created **without any leaders**. This is intentional because:
- The CSV doesn't contain leadership information for external groups
- Leadership should be managed separately through the research group admin interface
- This avoids creating incomplete or incorrect leadership records

### Campus Consistency

All research groups created from the same CSV row will use the **same campus** (from `CampusExecucao`). This ensures consistency within a single initiative.

### Duplicate Detection

The system checks for existing research groups by:
- **Name** (case-insensitive)
- **Short name** (case-insensitive)

If a match is found, the existing group is used instead of creating a new one.

### Organization

All research groups created during initiative import are assigned to the **"Default Organization"**. This is the same organization used for research groups imported via the organizational group CSV import.

## Comparison with Research Group CSV Import

| Aspect | Initiative CSV Import | Research Group CSV Import |
|--------|----------------------|---------------------------|
| **Campus Source** | `CampusExecucao` column | `Unidade` column |
| **Leadership** | Not assigned | Assigned from `Lideres` column |
| **Short Name** | Auto-generated | From `Sigla` column or auto-generated |
| **Purpose** | Create partnerships for initiatives | Create standalone research groups |
| **Organization** | Default Organization | Default Organization |

## Managing Created Research Groups

After import, you can:

1. **View the created groups** in Django Admin → Organizational Units
2. **Add leaders** through the admin interface
3. **Update details** (description, URL, etc.)
4. **Associate with more initiatives** as needed

## CSV Column Reference

### For Research Group Creation:
- `GrupoPesquisa`: Primary research group name (single group)
- `GrupoPesquisaExterno`: External partnership research group name(s) (comma-separated)

### Optional but Recommended:
- `CampusExecucao`: Campus name (determines where the group is located)
- `AreaConhecimento`: Knowledge area (helps categorize the group)

### Example CSV Structure:
```csv
CampusExecucao,Titulo,Coordenador,EmailCoordenador,GrupoPesquisaExterno,AreaConhecimento
Serra,Project A,John Doe,john@example.com,AI Research Group,Computer Science
Vitória,Project B,Jane Smith,jane@example.com,"Group X, Group Y",Engineering
```

## Troubleshooting

### Research Group Not Created

If a research group is not being created:
1. Check that `GrupoPesquisaExterno` column has a value
2. Verify the CSV is properly formatted
3. Check import logs for errors

### Wrong Campus Assigned

If the research group is created with the wrong campus:
1. Verify `CampusExecucao` column value in CSV
2. Check for typos in campus name
3. Update the campus through Django Admin if needed

### Duplicate Groups

If you see duplicate research groups:
1. They may have different names (check for typos)
2. They may be on different campuses (same name, different campus is allowed)
3. Use Django Admin to merge or delete duplicates if needed

## Related Documentation

- [Initiative CSV Import README](README.md)
- [Research Group CSV Import](../../organizational_group/csv_import/README.md)
- [Short Name Generation](../../organizational_group/csv_import/SHORT_NAME_GENERATION.md)

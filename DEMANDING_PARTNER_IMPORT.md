# Demanding Partner (ParceiroDemandante) CSV Import

## Overview
The initiatives CSV import now supports creating and associating demanding partner organizations with research projects. A demanding partner is an organization that requests, demands, or sponsors an initiative.

## New Feature: ParceiroDemandante Field

### CSV Column
- **Column Name:** `ParceiroDemandante`
- **Format:** Single organization name
- **Example:** `"Ministry of Agriculture"`, `"State Health Department"`, `"Local Government"`

### Behavior

When importing research projects, the system will:

1. **Parse Demanding Partner:** Read the `ParceiroDemandante` field
2. **Create if Not Exists:** For the demanding partner name:
   - Search for existing organizational unit (by name or short_name, case-insensitive)
   - If not found, create a new organizational unit with:
     - **Name:** Normalized to Title Case
     - **Short Name:** Auto-generated acronym or truncated name
     - **Type:** Extension (service/client organizations)
     - **Organization:** "Demanding Partners"
     - **Campus:** "Partner Organizations" (code: PARTNER)
     - **Knowledge Area:** Inherited from the initiative's knowledge area
3. **Associate with Initiative:** Set as the initiative's demanding partner
4. **Track Relationship:** The demanding partner can see all initiatives they've requested

### Auto-Generated Defaults

Demanding partner organizations are created with these defaults:

| Field | Value | Description |
|-------|-------|-------------|
| Organization | "Demanding Partners" | Special organization for client/stakeholder orgs |
| Campus | "Partner Organizations" (PARTNER) | Special campus for partner entities |
| Type | Extension | Organizational type for service/extension work |
| Short Name | Auto-generated | Acronym from words or truncated name |
| Knowledge Area | From initiative | Inherited from the research project |

## Database Changes

### New Field in Initiative Model

```python
demanding_partner = models.ForeignKey(
    'organizational_group.OrganizationalUnit',
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name='demanded_initiatives',
    help_text="Organization that demands/requests this initiative"
)
```

### Migration Required

After updating the code, run:
```bash
python manage.py makemigrations initiatives
python manage.py migrate initiatives
```

## CSV Format Example

```csv
Titulo,Coordenador,EmailCoordenador,Inicio,Fim,AreaConhecimento,ParceiroDemandante
"Agricultural Extension Project","Dr. Silva","silva@example.com","2024-01-01","2024-12-31","Agriculture","Ministry of Agriculture"
"Public Health Initiative","Dr. Santos","santos@example.com","2024-02-01","2024-11-30","Health Sciences","State Health Department"
```

## Use Cases

### 1. Government Partnerships
```csv
ParceiroDemandante: "Ministry of Education"
```
Government agencies requesting research or extension services.

### 2. Industry Clients
```csv
ParceiroDemandante: "Agribusiness Corporation"
```
Private companies requesting applied research or consulting.

### 3. Community Organizations
```csv
ParceiroDemandante: "Local Farmers Association"
```
Community groups requesting extension services or projects.

### 4. Public Institutions
```csv
ParceiroDemandante: "State Environmental Agency"
```
Public institutions requesting technical assistance or research.

## Differences: Types of Organizations

| Type | Purpose | CSV Field | Organization | Type |
|------|---------|-----------|--------------|------|
| **Internal Groups** | University research groups | `GrupoPesquisa` | Various | Research |
| **External Research** | Partner research institutions | `GrupoPesquisaExterno` | External Organizations | Research |
| **Demanding Partners** | Clients/stakeholders | `ParceiroDemandante` | Demanding Partners | Extension |

## Querying Demanding Partners

### From Initiative
```python
# Get the demanding partner
initiative = Initiative.objects.get(id=1)
partner = initiative.demanding_partner
print(f"Demanded by: {partner.name}")
```

### From Organization
```python
# Get all initiatives demanded by an organization
partner = OrganizationalUnit.objects.get(name="Ministry of Agriculture")
initiatives = partner.demanded_initiatives.all()
print(f"Demanded {initiatives.count()} initiatives")
```

## Admin Interface

The demanding partner will be visible in:
1. **Initiative Detail Page:** Shows which organization demanded the initiative
2. **Organizational Unit Detail Page:** Shows all initiatives demanded by that organization
3. **Filters:** Can filter initiatives by demanding partner

## Implementation Details

### Code Changes

1. **`apps/initiatives/models.py`**
   - Added `demanding_partner` ForeignKey field
   - Links initiative to the requesting organization

2. **`apps/initiatives/csv_import/group_handler.py`**
   - Added `get_or_create_demanding_partner()` method
   - Creates partner organizations with Extension type
   - Uses "Demanding Partners" organization and "PARTNER" campus

3. **`apps/initiatives/csv_import/processor.py`**
   - Added processing for `ParceiroDemandante` field
   - Associates demanding partner with initiative

### Database Impact

- Adds `demanding_partner_id` column to `initiatives_initiative` table
- Creates new records in `organizational_group_organizationalunit` table
- Creates "Demanding Partners" organization (once)
- Creates "Partner Organizations" campus (once)
- Creates or uses "Extension" organizational type

## Benefits

1. **Client Tracking:** Track which organizations request initiatives
2. **Automatic Creation:** No need to manually create partner organizations
3. **Service Reporting:** Generate reports on services provided to partners
4. **Relationship Management:** Maintain history of partnerships
5. **Knowledge Area Sync:** Partners automatically inherit knowledge areas

## Validation

The import will:
- ✅ Skip empty demanding partner names
- ✅ Normalize names to Title Case
- ✅ Handle duplicate names gracefully (reuses existing)
- ✅ Associate knowledge areas automatically
- ✅ Create missing default entities (organization, campus, type)
- ✅ Set NULL if demanding partner is not specified

## Complete CSV Example

```csv
Titulo,Coordenador,EmailCoordenador,Inicio,Fim,Pesquisadores,Estudantes,AreaConhecimento,GrupoPesquisa,GrupoPesquisaExterno,ParceiroDemandante
"Sustainable Agriculture Project","Dr. Maria Silva","maria@univ.edu","2024-01-01","2024-12-31","João Santos, Ana Costa","Pedro Lima","Agriculture","Internal Agro Lab","Embrapa, University of California","Ministry of Agriculture"
```

This creates:
- ✅ Initiative with coordinator and team
- ✅ Internal group association (GrupoPesquisa)
- ✅ External research partners (GrupoPesquisaExterno)
- ✅ Demanding partner organization (ParceiroDemandante)
- ✅ Knowledge area associations

## Reporting Capabilities

With demanding partners tracked, you can generate reports on:
- Initiatives by demanding partner
- Services provided to government agencies
- Industry partnerships
- Community engagement projects
- Extension service impact

## Future Enhancements

Potential improvements:
- Partner contact information
- Contract/agreement tracking
- Budget/funding from partners
- Partner satisfaction ratings
- Multi-partner initiatives (ManyToMany)

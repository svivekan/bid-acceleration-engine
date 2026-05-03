# Phase 3 Specification: Data Ingestion Agent

## Overview

The Data Ingestion Agent analyzes extracted RFP requirements and recommends the appropriate Azure ingestion pattern and services. It is the first agent in the data architecture pipeline, focusing on how data flows from source systems into Azure.

**Agent Type:** Specialist (Data Architecture)  
**Input:** `ExtractedRequirement[]` (from Phase 2)  
**Output:** `DataIngestionArchitecture` (Pydantic model)  
**Purpose:** Determine the optimal ingestion strategy and Azure services for the RFP

---

## Problem Statement

Government RFPs have diverse data sources and requirements:
- Multiple legacy systems (on-prem databases, files, APIs, streaming sources)
- Varying freshness requirements (batch daily, real-time streams)
- Different complexity levels (single source to complex orchestration)

A consultant needs to quickly recommend:
- **Which ingestion tool** (Fabric Pipelines, Data Factory, or Event Hubs + Stream Analytics)
- **Why** (decision rationale)
- **Complete architecture pattern** (how data flows, SHIR config, security layers)
- **Security & compliance approach** (UK data residency, GDPR, audit trails)

This agent encodes consulting expertise into deterministic decision logic.

---

## Inputs

### `ExtractedRequirement[]`

Array of requirements extracted from Phase 2, each containing:
- `source_text`: Full requirement text
- `category`: Technical, Security, Compliance, or Performance
- `priority`: High, Medium, Low
- `mandatory`: Boolean
- `section_heading`: Section where found

**Relevance:** Agent analyzes requirement text for:
- Data source mentions (Oracle, SQL Server, CSV, APIs, Kafka, etc.)
- On-premise vs cloud sources (critical for SHIR requirement)
- Volume indicators (GB, TB, PB, millions of records)
- Freshness/timing requirements (real-time, daily, batch, hourly)
- Orchestration complexity (dependencies, integrations)
- Governance/compliance needs (audit, SLA, enterprise, GDPR, UK data residency)

---

## Outputs

### `SHIRConfiguration` (Pydantic Model - for on-prem sources)

```python
class SHIRConfiguration(BaseModel):
    """SHIR deployment with complete security architecture."""
    
    model_config = ConfigDict(extra="forbid")
    
    required: bool
    placement: str  # "on-prem", "dmz", "azure-vm"
    
    # High Availability
    ha_required: bool
    ha_nodes: int  # 1 (single) or 3+ (multi-node cluster)
    failover_strategy: Optional[str]  # "auto-registered-nodes"
    
    # Network Security
    network_security_layer: str
    # "shir-only" (HTTPS outbound)
    # "shir-plus-vpn" (VPN tunnel + SHIR)
    # "shir-plus-expressroute" (ExpressRoute + SHIR, enterprise)
    
    firewall_rules: List[str]  # ["Allow SHIR IP to port 1433", ...]
    private_endpoints_required: bool  # Azure-side data protection
    
    # Authentication & Secrets
    credentials_storage: str  # "azure-key-vault"
    credentials_rotation_required: bool
    managed_identity_possible: bool
    authentication_method: str
    # "windows-auth" (domain), "sql-auth" (SQL in Key Vault),
    # "managed-identity" (modern, preferred)
    
    # Encryption
    encryption_in_transit: str  # "tls-1-2-plus"
    encryption_at_rest: bool
    column_level_encryption_for_pii: bool  # GDPR requirement
    
    # Data Residency & Compliance
    uk_region_required: bool
    azure_regions: List[str]  # ["UK South", "UK West"]
    gdpr_compliant: bool
    audit_logging_required: bool
    
    # Monitoring & Observability
    monitoring_enabled: bool
    shir_connection_monitoring: bool
    data_movement_audit_trail: bool
    alerting_on_failures: bool
    alerting_on_suspicious_access: bool
    
    # Performance
    concurrent_connections: Optional[int]
    estimated_daily_volume_gb: Optional[int]
    retry_strategy: str  # "exponential-backoff"
    
    # Security & Compliance Guidance
    security_recommendations: List[str]
    compliance_checklist: List[str]
```

### `DataIngestionArchitecture` (Pydantic Model - Main Output)

```python
class IngestionTool(str, Enum):
    """Recommended ingestion tool."""
    FABRIC_PIPELINE = "fabric_pipeline"
    DATA_FACTORY = "data_factory"
    EVENT_HUBS_STREAM_ANALYTICS = "event_hubs_stream_analytics"

class DataIngestionArchitecture(BaseModel):
    """Data ingestion architecture recommendation."""
    
    model_config = ConfigDict(extra="forbid")
    
    id: UUID
    tool: IngestionTool
    is_streaming: bool
    complexity_score: Optional[int] = None  # None if streaming
    
    # Detection & Analysis
    detected_sources: List[str]  # ["Oracle EBS", "CSV files", "Kafka topics"]
    on_premise_sources: List[str]  # ["SQL Server", "Oracle EBS"]
    detected_volume: Optional[str]  # "500GB", "2TB", "petabyte-scale"
    detected_freshness: Optional[str]  # "real-time", "daily batch", "hourly"
    detected_dependencies: Optional[int]  # Number of orchestration dependencies
    
    # Decision details
    tool_decision: str  # Explanation for tool choice
    complexity_factors: List[str]  # ["5+ sources", "enterprise governance"]
    
    # Architecture pattern
    architecture_pattern: str  # "On-Prem SQL Server → SHIR → Data Factory → Synapse"
    key_services: List[str]  # ["Data Factory", "Self-Hosted IR", "Synapse"]
    
    # SHIR Configuration (if on-prem sources detected)
    shir_config: Optional[SHIRConfiguration] = None
    
    # Constraints & considerations
    considerations: List[str]  # ["GDPR data residency", "CDC required", "HA needed"]
    assumptions: List[str]  # ["Daily batch refresh", "On-prem SHIR available"]
    
    created_at: datetime
```

---

## Decision Logic

### Phase 1: Streaming Detection

**Check if ANY streaming keyword appears in requirements:**

Keywords: `real-time`, `streaming`, `event`, `continuous`, `live`, `kafka`, `event hub`, `message queue`

**If match found:**
- Set `is_streaming = True`
- Set `tool = EVENT_HUBS_STREAM_ANALYTICS`
- Set `complexity_score = None`
- Pattern: "Event Hubs → Stream Analytics → Data Lake / Lakehouse"
- Services: ["Azure Event Hubs", "Azure Stream Analytics", "Azure Data Lake Storage"]
- Skip to Phase 3 (SHIR not needed for streaming from cloud sources)

---

### Phase 2: Batch Complexity Scoring

**If NOT streaming, calculate complexity score:**

| Factor | Threshold | Points | Condition |
|--------|-----------|--------|-----------|
| **Sources** | ≥ 5 sources | +2 | Multiple legacy systems, databases, files |
| **Volume** | > 5TB | +2 | Data volume exceeds medium scale |
| **Orchestration** | > 10 dependencies | +2 | Complex workflow with many steps |
| **Governance** | Enterprise SLA/audit required | +1 | Strict compliance, audit trails |

**Decision Threshold:**
- **Score ≥ 3** → Use **Data Factory**
- **Score < 3** → Use **Fabric Pipelines**

---

### Phase 3: SHIR Configuration (if on-prem sources detected)

**Trigger:** If any on-prem sources found (SQL Server, Oracle, file shares, legacy systems)

#### **3a. Placement Decision**
```
If on-prem SQL Server/Oracle found:
  → placement = "on-prem"  (same network as data source)

Else if no on-prem infrastructure:
  → placement = "azure-vm"  (Linux VM in Azure)

Else if DMZ security policy:
  → placement = "dmz"
```

#### **3b. High Availability Decision**
```
If uptime requirement ≥ 99.9% OR enterprise governance:
  → ha_required = True
  → ha_nodes = 3  (multi-node cluster)
  → failover_strategy = "auto-registered-nodes"

Else:
  → ha_required = False
  → ha_nodes = 1  (single node)
```

#### **3c. Network Security Decision**
```
If "enterprise" OR "multi-site" OR "high-security":
  → network_security_layer = "shir-plus-expressroute"
  → security_recommendations += ["Use ExpressRoute for dedicated connection"]

Else if "vpn" mentioned OR "site-to-site vpn":
  → network_security_layer = "shir-plus-vpn"

Else:
  → network_security_layer = "shir-only"  (HTTPS outbound, most common)
```

#### **3d. Authentication & Credentials Decision**
```
If Windows domain environment:
  → authentication_method = "windows-auth"  (Kerberos)
  → managed_identity_possible = False

Else if modern Azure environment:
  → authentication_method = "managed-identity"  (preferred)
  → managed_identity_possible = True
  → security_recommendations += ["Use Managed Identity instead of SQL credentials"]

Else:
  → authentication_method = "sql-auth"  (with Key Vault)
  → credentials_rotation_required = True
  → security_recommendations += ["Rotate SQL credentials quarterly"]

Always:
  → credentials_storage = "azure-key-vault"
```

#### **3e. Encryption Decision**
```
Always:
  → encryption_in_transit = "tls-1-2-plus"

If "GDPR" OR "PII" OR "healthcare" OR "government":
  → encryption_at_rest = True
  → column_level_encryption_for_pii = True
  → security_recommendations += ["Implement column-level encryption for PII"]

If healthcare (NHS):
  → security_recommendations += ["Implement NHS DSPT encryption standards"]
```

#### **3f. Data Residency & Compliance Decision**
```
If UK government RFP OR GDPR mentioned:
  → uk_region_required = True
  → azure_regions = ["UK South", "UK West"]
  → gdpr_compliant = True
  → audit_logging_required = True
  → compliance_checklist = [GDPR checklist items]

If NHS/healthcare:
  → compliance_checklist += [NHS DSPT items]
```

#### **3g. Monitoring & Observability Decision**
```
If enterprise governance OR compliance mentioned:
  → monitoring_enabled = True
  → shir_connection_monitoring = True
  → data_movement_audit_trail = True
  → alerting_on_failures = True
  → alerting_on_suspicious_access = True

Else if high-priority requirements:
  → monitoring_enabled = True
  → audit_logging_required = True
  → alerting_on_failures = True
```

#### **3h. Performance Estimation**
```
From detected_volume:
  Extract GB/TB from requirements
  → estimated_daily_volume_gb = X

From detected_sources count + freshness:
  If ≥5 sources AND daily refresh:
    → concurrent_connections = 10-20
  If ≥10 sources AND hourly refresh:
    → concurrent_connections = 50+
  Else:
    → concurrent_connections = 2-5

retry_strategy = "exponential-backoff"  (always)
```

---

### Determine Architecture Pattern

#### **Fabric Pipelines** (Simple Batch)
- Pattern: "On-Prem Source → Self-Hosted IR → Fabric Data Pipeline → Lakehouse"
- Services: ["Data Factory Self-Hosted IR", "Fabric Data Pipeline", "Fabric Lakehouse"]
- SHIR: Single node, monitoring basic
- Advantages: Unified licensing, integrated Lakehouse, Power BI native
- Typical: Daily batch refresh

#### **Data Factory** (Complex Batch)
- Pattern: "On-Prem Source → Self-Hosted IR → Data Factory → Synapse / Data Lake"
- Services: ["Data Factory", "Self-Hosted Integration Runtime", "Synapse Dedicated SQL Pool / Data Lake"]
- SHIR: Multi-node HA, comprehensive monitoring
- Advantages: Enterprise governance, complex orchestration, audit trails
- Supports: Batch and incremental loading

#### **Event Hubs + Stream Analytics** (Streaming)
- Pattern: "Event Source → Event Hubs → Stream Analytics → Data Lake / Lakehouse"
- Services: ["Azure Event Hubs", "Azure Stream Analytics", "Azure Data Lake / Lakehouse"]
- SHIR: Not needed (cloud-native sources)
- Advantages: Real-time processing, continuous ingestion
- Latency: < 1 second

---

## Acceptance Criteria

### 1. Streaming Detection
- ✅ Correctly identifies streaming requirements (ANY streaming keyword)
- ✅ Returns `EVENT_HUBS_STREAM_ANALYTICS` for streaming
- ✅ Sets `is_streaming = True`
- ✅ Returns `shir_config = None` for streaming (not needed)

### 2. On-Premise Source Detection
- ✅ Identifies on-prem sources (SQL Server, Oracle, legacy systems)
- ✅ Lists on-prem sources separately in `on_premise_sources`
- ✅ Triggers SHIR configuration if on-prem found
- ✅ Returns `shir_config = None` if no on-prem sources

### 3. Batch Complexity Scoring
- ✅ Detects number of data sources from requirement text
- ✅ Detects data volume indicators (GB, TB, PB, million records)
- ✅ Estimates orchestration dependencies (>10 = +2 points)
- ✅ Detects enterprise governance/SLA requirements
- ✅ Calculates complexity score correctly (sources +2, volume +2, orchestration +2, governance +1)

### 4. Tool Recommendation
- ✅ Streaming RFPs → Event Hubs + Stream Analytics
- ✅ Score ≥ 3 → Data Factory
- ✅ Score < 3 → Fabric Pipelines

### 5. SHIR Configuration (if on-prem)
- ✅ **Placement:** Recommends on-prem, DMZ, or Azure VM
- ✅ **HA:** Detects 99.9% uptime requirement → multi-node HA
- ✅ **Network Security:** Recommends SHIR-only, SHIR+VPN, or SHIR+ExpressRoute
- ✅ **Authentication:** Determines Windows auth, SQL auth, or Managed Identity
- ✅ **Encryption:** TLS 1.2+ always; PII column encryption if GDPR/healthcare
- ✅ **Data Residency:** Sets UK regions for UK government RFPs
- ✅ **Monitoring:** Audit logging required for government/compliance
- ✅ **Performance:** Estimates concurrent connections based on sources + freshness

### 6. Security Recommendations
- ✅ Provides `security_recommendations` list with actionable guidance
- ✅ Includes ExpressRoute for enterprise scenarios
- ✅ Includes Managed Identity recommendation for modern environments
- ✅ Includes column-level encryption for GDPR
- ✅ Includes NHS DSPT recommendations if healthcare

### 7. Compliance Checklist
- ✅ Generates `compliance_checklist` for GDPR if applicable
- ✅ Includes Cabinet Office security guidelines for UK government
- ✅ Includes NHS DSPT if healthcare sector
- ✅ Includes data residency checklist for UK regions

### 8. Architecture Pattern & Services
- ✅ Pattern aligns with recommended tool
- ✅ Pattern includes SHIR if on-prem sources
- ✅ Lists correct Azure services
- ✅ Services include data residency regions

### 9. Decision Rationale
- ✅ Provides clear explanation for tool choice
- ✅ Lists complexity factors that influenced decision
- ✅ Explains SHIR configuration rationale (placement, HA, security)
- ✅ References compliance and security considerations

### 10. Data Integrity
- ✅ All outputs properly typed (Pydantic models)
- ✅ JSON serialization round-trip works
- ✅ No data loss during transformation
- ✅ `shir_config` is None OR fully populated (no partial configs)

---

## Test Cases

### Test 1: Simple Batch (Single On-Prem Source)
```
Input: "Need to ingest from single on-prem SQL Server, daily batch, 500GB"
Expected:
  - tool: FABRIC_PIPELINE
  - complexity_score: 0
  - on_premise_sources: ["SQL Server"]
  - volume: "500GB"
  - shir_config.required: True
  - shir_config.placement: "on-prem"
  - shir_config.ha_required: False (single node)
  - shir_config.encryption_in_transit: "tls-1-2-plus"
  - shir_config.network_security_layer: "shir-only"
```

### Test 2: Complex Batch (Multi-Source, Enterprise)
```
Input: "Consolidate 8 legacy systems (Oracle, SQL Server, case management), 2TB, 
         daily refresh, enterprise governance, 99.9% uptime required"
Expected:
  - tool: DATA_FACTORY
  - complexity_score: 3 (≥5 sources +2, governance +1)
  - on_premise_sources: ["Oracle EBS", "SQL Server", "case management systems"]
  - shir_config.required: True
  - shir_config.ha_required: True (99.9% uptime)
  - shir_config.ha_nodes: 3
  - shir_config.monitoring_enabled: True
  - shir_config.data_movement_audit_trail: True
```

### Test 3: UK Government RFP (GDPR Compliance)
```
Input: "Local Council data integration, 5 legacy systems, GDPR compliance, 
         UK data residency required, audit trail mandatory"
Expected:
  - tool: DATA_FACTORY (complexity: 5 sources +2, governance +1)
  - shir_config.required: True
  - shir_config.uk_region_required: True
  - shir_config.azure_regions: ["UK South", "UK West"]
  - shir_config.gdpr_compliant: True
  - shir_config.audit_logging_required: True
  - shir_config.column_level_encryption_for_pii: True
  - shir_config.compliance_checklist: [GDPR items]
```

### Test 4: Streaming (Real-Time Events)
```
Input: "Ingest real-time streaming events from Kafka, continuous processing, 
         low-latency requirements"
Expected:
  - tool: EVENT_HUBS_STREAM_ANALYTICS
  - is_streaming: True
  - complexity_score: None
  - shir_config: None (streaming doesn't need SHIR)
  - pattern: "Event Hubs → Stream Analytics → Data Lake"
```

### Test 5: Enterprise Multi-Site with ExpressRoute
```
Input: "Multi-site on-prem Oracle + SQL Server, enterprise security, 
         high-security requirement, 99.95% uptime"
Expected:
  - tool: DATA_FACTORY
  - shir_config.required: True
  - shir_config.network_security_layer: "shir-plus-expressroute"
  - shir_config.ha_required: True
  - shir_config.security_recommendations includes: 
    ["Use ExpressRoute for dedicated connection"]
```

### Test 6: Healthcare (NHS DSPT Compliance)
```
Input: "NHS healthcare data integration, on-prem SQL Server, 
         DSPT compliance required, encryption mandatory"
Expected:
  - tool: DATA_FACTORY (healthcare requires robust architecture)
  - shir_config.required: True
  - shir_config.encryption_at_rest: True
  - shir_config.column_level_encryption_for_pii: True
  - shir_config.uk_region_required: True
  - shir_config.compliance_checklist includes: 
    ["NHS DSPT encryption standards", ...]
```

### Test 7: Cloud-Native Streaming (No On-Prem)
```
Input: "Real-time event streaming from cloud APIs, continuous processing, 
         no on-premise systems"
Expected:
  - tool: EVENT_HUBS_STREAM_ANALYTICS
  - is_streaming: True
  - shir_config: None (no on-prem sources)
  - on_premise_sources: []
```

### Test 8: Modern Azure Environment (Managed Identity)
```
Input: "Modern Azure environment, managed identity support, 
         on-prem SQL Server, single source"
Expected:
  - shir_config.required: True
  - shir_config.managed_identity_possible: True
  - shir_config.authentication_method: "managed-identity"
  - shir_config.security_recommendations includes: 
    ["Use Managed Identity instead of SQL credentials"]
```

### Test 9: Legacy Domain Environment (Windows Auth)
```
Input: "Windows domain environment, on-prem SQL Server, 
         Kerberos support available"
Expected:
  - shir_config.required: True
  - shir_config.authentication_method: "windows-auth"
  - shir_config.managed_identity_possible: False
```

### Test 10: Streaming False Positive
```
Input: "Real-time dashboards for streaming reports, on-prem SQL Server"
Expected:
  - is_streaming: False (dashboard use case, not true streaming)
  - tool: FABRIC_PIPELINE (simple, single source)
  - shir_config.required: True (on-prem SQL Server still needs SHIR)
```

---

## Implementation Checklist

### Schemas
- [ ] Create `schemas/data_ingestion.py` with:
  - [ ] `IngestionTool` enum
  - [ ] `SHIRConfiguration` Pydantic model
  - [ ] `DataIngestionArchitecture` Pydantic model

### Agent Implementation
- [ ] Create `agents/data_ingestion_agent/` directory
  - [ ] `__init__.py` - Module initialization
  - [ ] `agent.py` - Main `DataIngestionAgent` class orchestrating all phases
  - [ ] `detector.py` - Streaming detection and on-prem source detection
  - [ ] `analyzer.py` - Complexity scoring and dependency analysis
  - [ ] `recommender.py` - Tool recommendation (Fabric vs ADF)
  - [ ] `shir_configurator.py` - SHIR placement, HA, network security decisions
  - [ ] `security_analyzer.py` - Authentication, encryption, security recommendations
  - [ ] `compliance_checker.py` - GDPR, NHS DSPT, Cabinet Office compliance

### Testing
- [ ] Create `tests/agents/test_data_ingestion_spec.py` with all 10 test cases
- [ ] Test streaming detection (keywords, false positives)
- [ ] Test on-prem source detection
- [ ] Test complexity scoring accuracy
- [ ] Test SHIR configuration for all scenarios
- [ ] Test security recommendations
- [ ] Test compliance checklist generation
- [ ] Validate against all UK RFP fixtures (7 fixtures)
- [ ] Verify JSON serialization round-trip

### Integration & Validation
- [ ] Run against Local Council RFP fixture (should recommend Data Factory + SHIR HA + UK regions)
- [ ] Run against University fixture
- [ ] Run against all 7 UK RFP fixtures
- [ ] Verify output matches consulting company expertise
- [ ] Document any edge cases discovered
- [ ] Commit to GitHub

---

## Integration with Pipeline

**Input from:** Phase 2 (RequirementExtractionAgent)  
**Output to:** Phase 4 (Data Transformation Agent - future)

**Data Flow:**
```
BidDocument 
  → RequirementExtractionAgent 
    → ExtractedRequirement[] 
      → DataIngestionAgent 
        → DataIngestionArchitecture
          → (Phase 4) DataTransformationAgent
```

---

## Benchmarks & Validation

- ✅ Correctly recommend ingestion strategy for all 7 UK RFP fixtures
- ✅ Match consulting company's known patterns (Fabric for simple, ADF for complex)
- ✅ Handle edge cases (streaming false positives, volume detection, multi-cloud)
- ✅ Provide clear, auditable decision rationale


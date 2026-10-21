# CAMEO Ontology — Violence Codes & Bangladesh Extensions

## Standard CAMEO Violence Hierarchy

### Category 13: Threaten
| Code | Label |
|------|-------|
| 131 | Threaten non-force |
| 132 | Threaten with administrative sanctions |
| 133 | Threaten political dissent |
| 134 | Threaten with military force |
| 135 | Threaten with unconventional violence |
| 136 | Threaten with mass violence |
| 137 | Threaten to attack, destroy |
| 138 | Threaten with conventional attack |
| 139 | Give ultimatum |

### Category 14.5: Violent Protest / Riots
| Code | Label |
|------|-------|
| 145 | Violent protest, rioting |

### Category 17: Structural Violence
| Code | Label |
|------|-------|
| 171 | Confiscate / destroy property |
| 172 | Impose administrative sanctions (curfew, censorship) |
| 173 | Arrest, detain |
| 174 | Expel, deport |
| 175 | Use repressive force against civilians |

### Category 18: Unconventional Violence
| Code | Label |
|------|-------|
| 181 | Abduct, hijack, take hostage |
| 182 | Physically assault (includes killing, sexual assault, torture) |
| 183 | Non-military bombing (suicide, car, IED) |
| 184 | Use unconventional weapons / tactics |
| 185 | Attempt to assassinate |

### Category 19: Conventional Force
| Code | Label |
|------|-------|
| 191 | Impose blockade, restrict movement |
| 192 | Occupy territory |
| 193 | Fight with small arms, light weapons |
| 194 | Fight with artillery, heavy weapons |
| 195 | Air strike, missile attack |

### Category 20: Massive Unconventional Force
| Code | Label |
|------|-------|
| 201 | Use chemical / biological / radiological weapons |
| 202 | Detonate nuclear weapon |

---

## Bangladesh-Specific Extensions

Standard CAMEO doesn't capture the granularity of violence patterns specific to Bangladesh. These extensions add BD-contextual subcategories under the CAMEO hierarchy.

### Namespace
```
@prefix cameo-bd: <http://example.org/cameo/bd/> .
```

### Extended Codes

#### Political Violence (`cameo-bd:PV*`)

| Code | Label | CAMEO Parent | Description |
|------|-------|-------------|-------------|
| PV01 | Hartal-related violence | 145 | Violence during political strikes (hartals) — property damage, vehicle torching, clashes |
| PV02 | Political party clash | 193 | Intra- or inter-party armed clashes (often during elections) |
| PV03 | Election violence | 182/193 | Violence during or surrounding election periods |
| PV04 | Student political violence | 182/145 | Clashes between student wings of political parties on campuses |

#### State Violence (`cameo-bd:SV*`)

| Code | Label | CAMEO Parent | Description |
|------|-------|-------------|-------------|
| SV01 | Extrajudicial killing ("crossfire") | 182 | Deaths in alleged encounters with law enforcement (RAB, police) |
| SV02 | Enforced disappearance | 181 | Individuals taken by security forces, fate unknown |
| SV03 | Custodial torture / death | 182 | Torture or death while in police/military custody |
| SV04 | Excessive force during protest | 175 | Rubber bullets, tear gas, water cannon causing injuries/deaths |

#### Communal Violence (`cameo-bd:CV*`)

| Code | Label | CAMEO Parent | Description |
|------|-------|-------------|-------------|
| CV01 | Religious communal violence | 182/171 | Attacks on religious minorities (temples, homes, businesses) |
| CV02 | Land-related communal violence | 171/182 | Violence over land disputes, often targeting indigenous communities |
| CV03 | Ethnic minority violence | 182 | Violence against Chittagong Hill Tracts indigenous peoples |

#### Gender-Based Violence (`cameo-bd:GV*`)

| Code | Label | CAMEO Parent | Description |
|------|-------|-------------|-------------|
| GV01 | Acid attack | 182 | Acid thrown at victims (predominantly women) |
| GV02 | Domestic violence fatality | 182 | Death resulting from domestic violence |
| GV03 | Sexual assault / rape | 182 | Reported sexual assault cases |
| GV04 | Dowry violence | 182 | Violence related to dowry demands |

#### Labor / Industrial Violence (`cameo-bd:LV*`)

| Code | Label | CAMEO Parent | Description |
|------|-------|-------------|-------------|
| LV01 | Garment worker unrest | 145/182 | Violence during garment factory protests |
| LV02 | Industrial disaster | — | Factory fires, building collapses (not coded in CAMEO but critical for BD) |
| LV03 | Labor rights suppression | 175 | Crackdowns on labor organizers |

#### Organized Crime (`cameo-bd:OC*`)

| Code | Label | CAMEO Parent | Description |
|------|-------|-------------|-------------|
| OC01 | Drug-related killing | 182 | Killings linked to drug trade |
| OC02 | Extortion violence | 182/137 | Violence related to extortion rackets |
| OC03 | Mob justice / lynching | 182 | Extrajudicial mob killings |

---

## Ontology Modeling Notes

### RDF Representation
```turtle
cameo-bd:SV01
    a owl:Class ;
    rdfs:subClassOf cameo:Code182 ;
    rdfs:label "Extrajudicial Killing (Crossfire)"@en ;
    rdfs:comment "Deaths in alleged encounters with BD law enforcement, commonly reported as 'crossfire' or 'gunfight'"@en ;
    cameo-bd:localTerm "crossfire"@en, "বন্দুকযুদ্ধ"@bn ;
    cameo-bd:typicalActors "RAB", "Police", "BGB" ;
    cameo-bd:cameoParent cameo:Code182 .
```

### Trigger Words (for NLP mapping)

| BD Extension | English Triggers | Bangla Transliterations |
|-------------|-----------------|------------------------|
| PV01 (Hartal violence) | "hartal", "strike violence", "vehicle torched" | "হরতাল" |
| SV01 (Crossfire) | "crossfire", "gunfight", "encounter killing" | "ক্রসফায়ার", "বন্দুকযুদ্ধ" |
| SV02 (Disappearance) | "enforced disappearance", "disappeared", "picked up" | "গুম" |
| CV01 (Communal) | "temple attack", "communal violence", "minority attack" | "সাম্প্রদায়িক" |
| GV01 (Acid attack) | "acid attack", "acid throwing" | "এসিড নিক্ষেপ" |
| OC03 (Mob justice) | "lynching", "mob beating", "beaten to death by mob" | "গণপিটুনি" |

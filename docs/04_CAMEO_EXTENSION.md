# 04. CAMEO Ontology — Violence Codes & Bangladesh Extensions

> **Reading Order:** Part 04 of 09 · Prev: [`03_DECISIONS.md`](03_DECISIONS.md) · Next: [`05_SKILLS_AND_TOOLS.md`](05_SKILLS_AND_TOOLS.md)

---

## Standard CAMEO Conflict Taxonomy (Codes 13–20)

NeuroSym-BD utilizes the standard Conflict and Mediation Event Observations (**CAMEO 1.1b3**) event framework. The high-level conflict categories (13–20) are formally defined as follows:

### Category 13: Threaten
*Verbal or non-verbal communication of intent to inflict harm, impose penalties, or use force.*
| Code | Standard CAMEO Label | Scope & Definition |
|---|---|---|
| **130** | Threaten, not specified | Generic threat of non-specific action |
| **131** | Threaten non-force | Threaten boycotts, non-violent political protests |
| **132** | Threaten with administrative sanctions | Threaten curfews, legal penalties, license revocations |
| **133** | Threaten with political dissent, protest | Threaten strikes, demonstrations, or civil disobedience |
| **134** | Threaten to halt negotiations | Threaten diplomatic walkout or negotiation breakdown |
| **135** | Threaten to halt mediation | Threaten withdrawal from mediated talks |
| **136** | Threaten to halt international involvement | Threaten expulsion of observers or peacekeepers |
| **137** | Threaten with repression | Threaten police crackdowns, emergency law declaration |
| **138** | Threaten with military force | Threaten armed deployment, military strikes, invasion |
| **139** | Give ultimatum | Time-bound demands with explicit threat of escalation |

### Category 14: Protest
*Non-violent to turbulent civilian demonstrations, strikes, and civil disobedience.*
| Code | Standard CAMEO Label | Scope & Definition |
|---|---|---|
| **140** | Engage in political dissent, not specified | Unspecified protest activity |
| **141** | Demonstrate or rally | Peaceful marches, rallies, public gatherings |
| **142** | Conduct hunger strike | Fasting demonstrations |
| **143** | Conduct strike or boycott | Industrial, transport, or general trade strikes |
| **144** | Obstruct passage, to conduct hunger strike / blockade | Sit-ins, road blockades, highway obstructions |
| **145** | Protest violently, riot | Picket clashes, vehicle burning, stone-throwing demonstrations |

### Category 15: Exhibit Force Posture
*Demonstrations of armed, security, or police readiness without direct kinetic engagement.*
| Code | Standard CAMEO Label | Scope & Definition |
|---|---|---|
| **150** | Demonstrate military or police power, not specified | Generic show of force |
| **151** | Increase police alert status | Heightened police deployments, tactical patrols |
| **152** | Increase military alert status | Armed forces mobilization, troop readiness levels |
| **153** | Mobilize or exercise police power | Joint security taskforce exercises, armed checkpoints |
| **154** | Mobilize or exercise armed forces | Border reinforcement, military maneuvers |

### Category 16: Reduce Relations
*Official or diplomatic disengagement, sanctions, and cessation of routine cooperation.*
| Code | Standard CAMEO Label | Scope & Definition |
|---|---|---|
| **160** | Reduce relations, not specified | Generic reduction of ties |
| **161** | Reduce or break diplomatic relations | Recalling ambassadors, closing consulates |
| **162** | Reduce or stop aid | Freezing financial aid, development programs |
| **163** | Impose embargo, boycott, or sanctions | Trade restrictions, asset freezes |
| **164** | Halt negotiations | Suspending active talks or mediation |
| **165** | Break off negotiations | Terminating dialogue entirely |
| **166** | Expel or withdraw, not specified | Diplomatic or institutional expulsions |

### Category 17: Coerce
*Non-lethal physical compulsion, state repression, property seizure, and arrests.*
| Code | Standard CAMEO Label | Scope & Definition |
|---|---|---|
| **170** | Coerce, not specified | Generic coercive enforcement |
| **171** | Seize or damage property | Confiscating assets, demolitions, property impoundment |
| **172** | Impose administrative sanctions | Imposing curfews, bans on assembly, censorship |
| **173** | Arrest, detain, or charge with legal action | Law enforcement arrests, custodial detentions |
| **174** | Expel or deport individuals | Border pushbacks, forced repatriations |
| **175** | Use tactics of violent repression | Riot-control crackdowns, tear gas, baton charges |

### Category 18: Assault
*Direct kinetic physical violence, bodily harm, torture, abduction, and targeted lethality.*
| Code | Standard CAMEO Label | Scope & Definition |
|---|---|---|
| **180** | Use unconventional violence, not specified | Unspecified asymmetric or kinetic harm |
| **181** | Abduct, hijack, or take hostage | Enforced disappearances, hostage-taking, kidnappings |
| **182** | Physically assault | Physical beatings, mob lynchings, stabbings, shootings |
| **183** | Conduct suicide, car, or other non-military bombing | Improvised explosive devices (IEDs), vehicle bombs |
| **184** | Use as human shield | Placing civilians in harm's way to deter retaliation |
| **185** | Attempt to assassinate | Failed targeted killings of political or public figures |
| **186** | Assassinate | Successful targeted political killings |

### Category 19: Fight
*Bilateral conventional armed combat between organized armed factions or armed forces.*
| Code | Standard CAMEO Label | Scope & Definition |
|---|---|---|
| **190** | Use conventional military force, not specified | Generic armed conflict clashes |
| **191** | Impose blockade, restrict movement | Military cordons, riverine/naval blockades |
| **192** | Occupy territory | Seizing territory, occupying administrative posts |
| **193** | Fight with small arms and light weapons | Firefights, pitched armed battles between cadres |
| **194** | Fight with artillery and tanks | Heavy ordnance artillery shelling |
| **195** | Employ aerial weapons | Fixed-wing airstrikes, armed helicopter attacks |
| **196** | Violate ceasefire | Ceasefire and truce violations |

### Category 20: Use Unconventional Mass Violence
*Systematic catastrophic violence resulting in mass civilian casualties or collective destruction.*
| Code | Standard CAMEO Label | Scope & Definition |
|---|---|---|
| **200** | Use unconventional mass violence, not specified | Generic mass atrocity |
| **201** | Engage in mass expulsion | Systematic forced displacement of communities |
| **202** | Engage in mass killings | Massacres, indiscriminate mass shootings |
| **203** | Engage in ethnic cleansing | Coordinated violence aimed at ethnic erasure |
| **204** | Use weapons of mass destruction | Nuclear, chemical, biological, or radiological agents |

---

## Bangladesh CAMEO Extension (`cameo-bd:`)

Standard CAMEO was engineered primarily for interstate diplomatic interactions and lacks indigenous granularity for South Asian localized conflict archetypes. Our extension formulates **21 specialized OWL 2 subclasses across 6 regional macro-categories** in [`ontology/cameo_bd_extension.ttl`](../ontology/cameo_bd_extension.ttl):

```turtle
@prefix cameo:    <http://example.org/cameo/> .
@prefix cameo-bd: <http://example.org/cameo/bd/> .
```

### Complete 21 Subclass Taxonomy

| Macro-Category | Subcode | Parent CAMEO | Localized Bangla Socio-Political Context |
|---|---|---|---|
| **Political Violence (PV)** | `cameo-bd:PV01` | `cameo:Code145` | **Hartal-related strike violence**: Picket transport arson, vehicle torching, strike clashes |
| | `cameo-bd:PV02` | `cameo:Code193` | **Political party armed clash**: Intra- and inter-party clashes (Awami League vs BNP cadres) |
| | `cameo-bd:PV03` | `cameo:Code182` | **Election violence**: Polling day clashes, booth intimidation, candidate assault |
| | `cameo-bd:PV04` | `cameo:Code182` | **Student political violence**: Campus clashes between rival student political wings |
| **State Violence (SV)** | `cameo-bd:SV01` | `cameo:Code182` | **Extrajudicial encounter ("crossfire")**: Alleged encounter deaths / gunfights by RAB/Police |
| | `cameo-bd:SV02` | `cameo:Code181` | **Enforced disappearance**: Plainclothes abductions, unacknowledged state custody |
| | `cameo-bd:SV03` | `cameo:Code182` | **Custodial torture or death**: Fatalities and severe physical torture under detention |
| | `cameo-bd:SV04` | `cameo:Code175` | **Excessive force during protest**: Crowd dispersal, tear gas, rubber bullets, batons |
| **Communal Violence (CV)** | `cameo-bd:CV01` | `cameo:Code182` | **Religious communal violence**: Attacks targeting Hindu/minority temples, households, shops |
| | `cameo-bd:CV02` | `cameo:Code171` | **Land-related communal violence**: Coercive land grabbing clashes targeting minority lands |
| | `cameo-bd:CV03` | `cameo:Code182` | **Ethnic minority violence**: Attacks against Chittagong Hill Tracts (CHT) indigenous peoples |
| **Gender-Based Violence (GV)** | `cameo-bd:GV01` | `cameo:Code182` | **Acid attack**: Chemical disfigurement attacks predominantly targeting women |
| | `cameo-bd:GV02` | `cameo:Code182` | **Domestic violence fatality**: Intimate partner battery, domestic murder, burning |
| | `cameo-bd:GV03` | `cameo:Code182` | **Sexual assault or rape**: Reported rape, gang rape, and severe public gendered violence |
| | `cameo-bd:GV04` | `cameo:Code182` | **Dowry violence**: Physical battery or fatal assault over dowry demands |
| **Labor Violence (LV)** | `cameo-bd:LV01` | `cameo:Code145` | **Garment worker unrest**: RMG wage highway blockades, worker-police clashes |
| | `cameo-bd:LV02` | `cameo:Code145` | **Industrial disaster / unrest**: Factory fires, building collapses, lockouts, industrial casualties |
| | `cameo-bd:LV03` | `cameo:Code175` | **Labor rights suppression**: Police crackdowns on union organizers, strike arrests |
| **Organized Crime (OC)** | `cameo-bd:OC01` | `cameo:Code182` | **Drug-related killing**: Anti-narcotics raids, targeted killings of syndicate rivals |
| | `cameo-bd:OC02` | `cameo:Code182` | **Extortion violence (*Chandabaji*)**: Toll collection violence by local protection syndicates |
| | `cameo-bd:OC03` | `cameo:Code182` | **Mob justice or lynching (*Gonopituni*)**: Extrajudicial civilian mob beatings without trial |

---

## Action vs. Context Separation

As noted in methodological reviews, event classification must distinguish the **event action** from the **contextual setting**:
* **Action Predicate**: Represented by the standard CAMEO code (e.g., `cameo:hasCode cameo:Code182` for physical assault, `cameo:Code145` for violent protest).
* **Contextual Tag**: Represented by the localized domain ontology subclass (e.g., `cameo-bd:hasContext cameo-bd:PV03` for election-related violence, `cameo-bd:hasContext cameo-bd:LV01` for RMG labor unrest).
* **Public Harm & Disasters**: Industrial disasters (e.g., `cameo-bd:LV02` factory fires) are recorded under public safety graph profiles while isolating intentional political conflict actions.

---

## RDF Schema Example (Turtle)

```turtle
@prefix cameo:    <http://example.org/cameo/> .
@prefix cameo-bd: <http://example.org/cameo/bd/> .
@prefix prov:     <http://www.w3.org/ns/prov#> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .

# Class Definition
cameo-bd:SV01
    a owl:Class ;
    rdfs:subClassOf cameo:Code182 ;
    rdfs:label "Extrajudicial Killing (Crossfire)"@en ;
    rdfs:comment "Deaths in alleged encounters with law enforcement, commonly reported as 'crossfire' or 'gunfight'"@en ;
    cameo-bd:localTerm "crossfire"@en, "gunfight"@en, "বন্দুকযুদ্ধ"@bn ;
    cameo-bd:typicalActors "RAB", "Police", "BGB" ;
    cameo-bd:cameoParent cameo:Code182 .

# Instantiated Event Mention with W3C PROV-O Grounding
:event_2026_0114_01
    a cameo:Event, cameo-bd:SV01 ;
    cameo:hasCode cameo:Code182 ;
    cameo:actor "Police" ;
    cameo:target "Suspect" ;
    cameo:location :District_Feni ;
    prov:wasDerivedFrom <https://www.thedailystar.net/news/crime-justice/news-380124> ;
    prov:generatedAtTime "2026-01-14T04:30:00Z"^^xsd:dateTime .
```

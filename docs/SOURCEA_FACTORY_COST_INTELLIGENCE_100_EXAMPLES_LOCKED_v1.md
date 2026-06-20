# Factory Cost Intelligence Loop + 100 Evidence-Backed Examples — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T02:26:10Z · **Authority:** ASF SAVE+WORK
**Path:** `docs/SOURCEA_FACTORY_COST_INTELLIGENCE_100_EXAMPLES_LOCKED_v1.md`
**Machine SSOT:** `data/factory-cost-intelligence-loop-v1.json`

---

## 0. One law

> **Cost is a control variable — observe $/unit · orient baselines · decide with agents · act via MES/inbox · measure receipts.**

## 1. Six-layer cost intelligence loop

- **OBSERVE:** MES/SCADA/historian · ERP/tariffs/FX · energy/carbon meters
- **ORIENT:** unified namespace · SKU-line-plant cost baselines · cross-factory 
- **DECIDE:** prescriptive optimizer · factory manager agent + specialists
- **ACT:** MES schedule/setpoints · WMS/logistics · RUN INBOX work orders
- **MEASURE:** auditable receipts · KPI delta $/kWh/scrap/OEE
- **LEARN:** model retrain · playbook update · Lumina/GLN cross-ref

## 2. Auto-prompting (planner → executor)

- **planner:** `brain work-order / loop auto`
- **executor:** `Worker RUN INBOX`
- **receipt:** `outbound-factory receipt + execution_plane_honesty`
- **anti_theater:** `scripts/anti_theater_validator_loop_v1.py`

## 3. Evidence corpus

- WEF GLN total sites: **224** (verified 2026-01-15)
- WEF use cases / metrics: **1000+** / **2000+**
- Network averages: **50%+** productivity · **80%+** defect cut · **30%** CO₂
- ROI playbook: **2-3x** (3yr) · **4-5x** (5yr)

## 4. Registry — 100 factories (machine rows)

| ID | Company | Site | Country | Primary metric |
|----|---------|------|---------|----------------|
| FC-001 | Carl Zeiss Vision | Guangzhou | China | +400% personalized range; -29% lead time |
| FC-002 | Hisense Visual Technology | Qingdao | China | NPS 84%; -34% R&D cycle; -18% material cost |
| FC-003 | ACG Packaging Materials | Shirwal | India | -40% lead time; -71% defects; -31% energy |
| FC-004 | Bristol Myers Squibb | Devens | USA | -42% NPI time; +40% volume; -40% emissions |
| FC-005 | EVE Energy | Jingmen | China | -52% defects; -41% conversion cost; OEE 88% |
| FC-006 | Faurecia Automotive Systems | Yancheng | China | -94% customer complaints; -75.8% scrap |
| FC-007 | Ford Otosan | Yenikoy | Turkiye | 2x volume; +44% labor productivity |
| FC-008 | Haier Strauss Science & Technology | Qingdao | China | -40% defects; -72% quality cost |
| FC-009 | HiTHIUM Energy Storage | Chongqing | China | -37% conversion cost; +200% throughput |
| FC-010 | Huafon Chongqing Spandex | Chongqing | China | +60% labor productivity; +113% net margin |
| FC-011 | Kunlene Film Industries | Suzhou | China | -45% R&D lead time; -31% defects |
| FC-012 | Michelin Shenyang Tire | Shenyang | China | -71% MOQ; -36% defect rate |
| FC-013 | Siemens Numerical Control | Nanjing | China | -78% lead time; -28% Scope 1&2 |
| FC-014 | SOCAR Carbamide | Sumqayit | Azerbaijan | +21% throughput; +24% gas efficiency |
| FC-015 | Unilever | Pondicherry | India | +25% volume; -23% defects |
| FC-016 | Yueda Textile | Yancheng | China | +421% productivity; -90% defects |
| FC-017 | Midea Kitchen & Bath | Wuhu | China | -39% delivery lead time; -86% market defects |
| FC-018 | Unilever | Hefei | China | -75% lead time; -24% operating cost |
| FC-019 | CATL | Yibin | China | -56% carbon footprint; -45% Scope 3/unit |
| FC-020 | Foxconn Industrial Internet | Bac Ninh | Vietnam | -22% Scope 3; -34% Scope 1&2 |
| FC-021 | Unilever | Gandhidham | India | -90% Scope 1&2; +24% growth |
| FC-022 | AUO Corporation | Suzhou | China | -70% attrition; +29% production |
| FC-023 | Schneider Electric | Wuhan | China | Onboarding 75→15 days; -42% turnover |
| FC-024 | Eaton Electrical Equipment | Changzhou | China | -39% lead time; +129% revenue same headcount |
| FC-025 | Mettler-Toledo International | Changzhou | China | 98.4% OTD; -22% lead time |
| FC-026 | GlobalFoundries | Singapore | Singapore | +40% labor productivity; -30% NPI prototyping |
| FC-027 | Haier Washing Electrical | Shanghai | China | +37% production; -33% conversion cost |
| FC-028 | Qatar Shell GTL | Ras Laffan | Qatar | +9% throughput; 99% reliability |
| FC-029 | Tongwei Solar | Meishan | China | -41% defects; -37% conversion cost |
| FC-030 | Lenovo | Monterrey | Mexico | -85% lead time; +58% productivity |
| FC-031 | Midea Refrigeration | Si Racha | Thailand | -43% order lead time; -32% complaints |
| FC-032 | Tupras | Izmit | Turkiye | Delivery 85→95%; -75% truck loading time |
| FC-033 | Yunnan Baiyao Group | Kunming | China | -78% raw material returns; -38% inventory days |
| FC-034 | Hisensehitachi Air-conditioning | Qingdao | China | -48% Scope 1&2; -28% Scope 3 use phase |
| FC-035 | Schneider Electric | Evreux | France | -40% single-use plastic; -18% energy |
| FC-036 | Haier Refrigerator | Chongqing | China | -40% attrition; 61% participation |
| FC-037 | AstraZeneca | Wuxi | China | +55% output; -44% mfg lead time; -80% non-perfect batches |
| FC-038 | Beko Dishwasher Plant | Ankara | Turkiye | -46% time-to-market; -26.1% conversion cost |
| FC-039 | Coca-Cola | Tuas Bay | Singapore | +28% throughput; +70% labor productivity |
| FC-040 | Hisensehitachi | Qingdao | China | +37% dev speed; +49% labor; -35% mfg cost |
| FC-041 | AstraZeneca | Sodertalje | Sweden | +56% labor productivity; -67% development lead time |
| FC-042 | Aramco | North Ghawar | Saudi Arabia | +8.44% production; -8.21% Scope 1&2 |
| FC-043 | Valeo Interior Controls | Shenzhen | China | +60.2% productivity; -34.5% lead time |
| FC-044 | United Microelectronics Corporation | Tainan | Taiwan | ~97% yield via AI defect analysis |
| FC-045 | Continental | Brandys nad Labem | Czech Republic | GLN designated — automotive tires |
| FC-046 | Unilever | Tinsukia | India | GLN designated — personal care |
| FC-047 | CEAT | Sriperumbudur | India | GLN designated — tires |
| FC-048 | Haier | Qingdao | China | GLN designated — home appliances |
| FC-049 | Novelis | Uhrichsville | USA | GLN designated — non-ferrous metals |
| FC-050 | CITIC Dicastal | Ameur Seflia | Morocco | First African GLN site |
| FC-051 | Sanmen Nuclear | Taizhou | China | GLN designated — nuclear energy |
| FC-052 | Roche | Basel | Switzerland | GLN designated — pharmaceuticals |
| FC-053 | Beijing Shougang Cold Rolling | Beijing | China | GLN designated — steel |
| FC-054 | Nucor Corporation | Sedalia | USA | GLN designated — steel products |
| FC-055 | TZ Railway Transit | Taiyuan | China | GLN designated — mobility |
| FC-056 | Mengniu Dairy | Ningxia | China | GLN designated — food & beverage |
| FC-057 | Tsingtao Brewery | Qingdao | China | GLN designated — beverages |
| FC-058 | Haitian Flavouring & Food | Foshan | China | GLN designated — food |
| FC-059 | Sany Renewable Energy | Taizhou | China | GLN designated — wind power |
| FC-060 | Midea | Hefei | China | GLN designated — home appliances |
| FC-061 | Siemens | Furth | Germany | GLN designated — industrial automation |
| FC-062 | Siemens | Erlangen | Germany | AI blueprint factory with NVIDIA (2026) |
| FC-063 | GE Healthcare | Beijing | China | GLN designated — medical equipment |
| FC-064 | Ferrovial | London | UK | GLN E2E value chain |
| FC-065 | Agilent Technologies | Shanghai | China | GLN designated — lab equipment |
| FC-066 | Agilent Technologies | Penang | Malaysia | GLN designated — lab equipment |
| FC-067 | Jubilant Ingrevia | Bharuch | India | GLN designated — chemicals |
| FC-068 | Midea | Chongqing | China | GLN designated — appliances |
| FC-069 | Zhengzhou Coal Mining Machinery | Zhengzhou | China | GLN designated — mining equipment |
| FC-070 | Schneider Electric | Shanghai | China | GLN designated — industrial automation |
| FC-071 | Schneider Electric | Wuxi | China | GLN designated — energy/cost optimization lineage |
| FC-072 | Emirates Global Aluminium | Al Taweelah | UAE | GLN designated — aluminium |
| FC-073 | Foxconn Industrial Internet | Bac Giang | Vietnam | GLN designated — electronics |
| FC-074 | Foxconn Industrial Internet | Shenzhen | China | GLN designated — electronics |
| FC-075 | Schneider Electric | Monterrey | Mexico | GLN designated — industrial automation |
| FC-076 | Guiyang Tyre | Guiyang | China | GLN designated — tires |
| FC-077 | GlobalFoundries | Fab 7 Singapore | Singapore | 60+ 4IR use cases; +40% labor productivity |
| FC-078 | Foxconn | MoMClaw multi-site | Taiwan | 80% faster root cause; +15% labor productivity |
| FC-079 | Jotun | Global cross-factory network | Norway | 18-20% group energy performance |
| FC-080 | U.S. Polysilicon manufacturer | Anonymous site | USA | ~20% energy cost via agentic scheduling |
| FC-081 | DeepHow x Foxconn | GB300 Bianca assembly | Taiwan | +3% first-pass yield |
| FC-082 | McKinsey anonymized industrial network | Multi-site | Global | $100M+ savings identified across prioritized sites |
| FC-083 | Schneider Electric | Batam | Indonesia | 44% downtime reduction; 40% OTD improvement |
| FC-084 | Toyota North America | Unified data architecture | USA | 97% motion waste reduction; onboarding 33d→<1d |
| FC-085 | Bosch | 9,000-machine network | Germany | +13% output from standardized data access |
| FC-086 | HIROTEC | IIoT operations | Japan | 5-8% productivity improvement |
| FC-087 | Yokogawa | Site-wide energy digital twin | Global | Sustained energy cost + emissions reduction |
| FC-088 | PepsiCo | Evaluating adaptive manufacturing | USA | Siemens+NVIDIA adaptive manufacturing eval |
| FC-089 | HD Hyundai | Evaluating adaptive manufacturing | South Korea | Industrial AI OS eval |
| FC-090 | KION Group | Evaluating adaptive manufacturing | Germany | Digital Twin Composer eval |
| FC-091 | Mercedes-Benz | NVIDIA industrial software customer | Germany | GPU-accelerated design/manufacturing |
| FC-092 | Samsung | NVIDIA industrial software customer | South Korea | GPU-accelerated manufacturing |
| FC-093 | TSMC | NVIDIA industrial software customer | Taiwan | GPU-accelerated fab workflows |
| FC-094 | SK hynix | NVIDIA industrial software customer | South Korea | GPU-accelerated manufacturing |
| FC-095 | Honda | NVIDIA industrial software customer | Japan | GPU-accelerated manufacturing |
| FC-096 | Advantech | FOX blueprint early adopter | Taiwan | Autonomous factory manager agent deploy |
| FC-097 | Pegatron | FOX blueprint early adopter | Taiwan | Autonomous factory manager agent deploy |
| FC-098 | Wistron | FOX blueprint early adopter | Taiwan | Autonomous factory manager agent deploy |
| FC-099 | Procter & Gamble | GLN historical cohort | USA | GLN pioneer — consumer goods |
| FC-100 | Phoenix Contact | GLN historical cohort | Germany | GLN pioneer — industrial automation |

## 5. Wire

- Script: `scripts/factory_cost_intelligence_v1.py`
- Validator: `bash scripts/validate-factory-cost-intelligence-v1.sh`
- Receipt: `~/.sina/factory-cost-intelligence-receipt-v1.json`
- Live line: `cost_intelligence_line` on agent-live-surfaces


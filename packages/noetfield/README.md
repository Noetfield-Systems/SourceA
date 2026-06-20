# Noetfield SDK

Governance client for the Noetfield AI Factory Operating Platform.

```python
from noetfield import Governance

gov = Governance(hub_url="http://127.0.0.1:13020")
gov.check(factory_id="compliance-kyb-wrapper-v1", input={"legal_name": "Acme"})
gov.execute(factory_id="exchange-factory-v1", tenant="trustfield")
gov.audit(job_id="...")
gov.sign(receipt)
```

Config: `.noetfield.json` or `NOETFIELD_HUB_URL` + `FBE_INTERNAL_SECRET`.

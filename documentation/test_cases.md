# Test Cases

| ID | Test | Expected Result |
|---|---|---|
| TC01 | Valid admin login | Dashboard opens |
| TC02 | Invalid password | Error message |
| TC03 | Asset search | Matching assets shown |
| TC04 | Asset type filter | Only selected type shown |
| TC05 | Status filter | Only selected status shown |
| TC06 | Add valid asset | Asset inserted |
| TC07 | Duplicate asset code | Database rejects insert |
| TC08 | Open asset detail | Metrics/history/predictions shown |
| TC09 | Add maintenance | Record appears in history |
| TC10 | Completed maintenance update | Asset status can return to ACTIVE |
| TC11 | Add high-severity failure | Trigger creates maintenance schedule |
| TC12 | Failure insert | Asset becomes FAILED |
| TC13 | Predictions page | Stored predictions listed |
| TC14 | Predict without model | Friendly model-unavailable error |
| TC15 | Predict with model | Probability/risk stored |
| TC16 | High-risk API | JSON high-risk assets |
| TC17 | Asset API | JSON asset list |
| TC18 | Dashboard KPIs | Counts/cost render |
| TC19 | Advanced query execution | SQL returns expected analytical rows |
| TC20 | Foreign key integrity | Invalid asset reference rejected |
| TC21 | Empty search | Full asset list |
| TC22 | Database outage | App does not expose raw SQL traceback |

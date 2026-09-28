# Viva Questions and Answers

## DBMS fundamentals
1. **What is a DBMS?** A DBMS manages structured data with controlled storage, retrieval, integrity and transactions.
2. **Why MySQL?** It is a mature relational DBMS, easy to install locally and supports constraints, views, procedures, triggers and window functions.
3. **Primary key?** A column or set of columns that uniquely identifies each row.
4. **Foreign key?** A reference that enforces a relationship to a parent table.
5. **Why normalization?** To reduce redundancy and update anomalies.
6. **What is 1NF?** Atomic values and no repeating groups.
7. **What is 2NF?** 1NF plus no partial dependency on a composite key.
8. **What is 3NF?** 2NF plus no transitive dependency of non-key attributes.
9. **What is a JOIN?** It combines rows from related tables.
10. **Why LEFT JOIN?** To retain all rows from the left table even without matches.
11. **What is a subquery?** A query nested inside another SQL statement.
12. **Correlated subquery?** A subquery evaluated using a value from the outer query.
13. **CTE?** A named temporary result set defined with WITH, improving complex query readability.
14. **Window function?** Calculates across related rows without collapsing them, e.g. RANK or ROW_NUMBER.
15. **View?** A stored SQL query presented as a virtual table.
16. **Stored procedure?** A reusable database-side program that can accept parameters and return results.
17. **Trigger?** Automatically executes when a table event occurs.
18. **Index?** A data structure that accelerates lookups at the cost of storage/write overhead.
19. **ACID?** Atomicity, Consistency, Isolation, Durability.
20. **Why transactions?** To ensure related changes succeed or fail together.

## ML fundamentals
21. **What is predictive maintenance?** Using historical/real-time information to estimate future equipment failure and schedule maintenance proactively.
22. **Why classification?** The target is whether failure occurs within a defined future window.
23. **What is the target?** `failure_within_30_days`, where 1 means a qualifying recent failure label and 0 otherwise in this academic dataset.
24. **What is feature engineering?** Transforming raw database information into useful model variables.
25. **Why train/test split?** To evaluate performance on unseen data.
26. **Precision?** Of predicted failures, the fraction that are actual failures.
27. **Recall?** Of actual failures, the fraction detected by the model.
28. **F1?** Harmonic mean of precision and recall.
29. **ROC-AUC?** Ranking/discrimination ability across probability thresholds.
30. **Confusion matrix?** Counts true positives, false positives, true negatives and false negatives.
31. **Why not only accuracy?** Failure classes may be imbalanced, so accuracy can hide poor failure detection.
32. **Random Forest?** An ensemble of decision trees trained with randomized samples/features.
33. **Why compare two models?** It avoids assuming one algorithm is always best.
34. **What is a probability?** The model's estimated likelihood for the positive class, not a guarantee.
35. **Why store predictions in MySQL?** For auditability, history, dashboarding and integration with maintenance decisions.

## Project-specific examiner questions
36. **Why is this primarily a DBMS project?** The operational source of truth, history, relationships, analytics and prediction ledger are implemented in MySQL; AI consumes and writes back to this relational layer.
37. **Which trigger is most useful?** A high/critical failure trigger creates a follow-up maintenance schedule automatically.
38. **How does a failure affect asset status?** The failure insert trigger marks the asset FAILED.
39. **How does maintenance interact with status?** Completed maintenance can restore an asset from MAINTENANCE/FAILED to ACTIVE through the trigger.
40. **What tables feed ML?** Assets, asset_metrics, failures and maintenance.
41. **What features are used?** Asset age, telemetry, error count, uptime, failure history, maintenance gap/count/cost and criticality.
42. **How is risk assigned?** Project thresholds map probability to LOW (<0.40), MEDIUM (0.40–0.69), HIGH (>=0.70).
43. **What is the health score?** A separate 0–100 project-defined indicator used for operational interpretation; it is not the same thing as failure probability.
44. **How are factors explained?** The demo highlights threshold-crossing telemetry/history indicators such as temperature, errors, maintenance gap and prior failures.
45. **What happens if the model file is missing?** The prediction endpoint returns a friendly error instructing the operator to train the model; the submission package also includes a validated model artifact.
46. **How can this scale?** Partition/aggregate time-series metrics, add caching, optimize indexes, batch ML feature queries, and move model inference into a service.
47. **What is a limitation?** The dataset is synthetic and the target label is constructed for academic demonstration rather than production incident forecasting.
48. **What would improve production readiness?** Real telemetry integration, stronger labeling, monitoring/drift detection, role-based permissions and secure password hashing. These controls are implemented in the revised project.
49. **Why use database views?** They centralize repeatable analytical logic and simplify application queries.
50. **What makes the architecture maintainable?** Flask blueprints, isolated ML modules, SQL scripts, configuration via environment variables and a consistent schema.

## Additional project-specific questions
51. Why store metrics historically instead of only current values?
52. How would you prevent duplicate predictions?
53. Which indexes matter most for a dashboard query?
54. How would you handle a new asset type?
55. How would you validate a prediction model after deployment?

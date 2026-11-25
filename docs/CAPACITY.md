# Capacity and Scalability

## 1. Purpose

This report estimates corpus capacity using the current downloaded files. It distinguishes measured local data from projections.

Report generated: 2026-11-25 06:18 UTC

## 2. Measured Current Corpus

| Metric | Measured value |
|---|---:|
| Downloaded source files | 10 |
| Successfully parsed files | 10 |
| Parser-generated pages | 203 |
| Heading path entries | 188 |
| Extracted tables | 0 |
| Extracted characters | 69,618 |
| Raw source size | 83,198 bytes |
| Extracted UTF-8 text size | 69,618 bytes |
| Estimated tokens | 17,404 |

Token estimate = extracted characters / 4. This is a planning estimate, not an exact tokenizer result.

## 3. Full Target Projection

The requested planning target is **4,000 files/rules**. This is a projection, not a claim that the target has been collected.

- Average estimated tokens per downloaded file: 1,740.4
- Projected tokens at the full target: 6,961,600
- Approximate 500-token chunks at the full target: 13,924

The projection assumes the average size of the current corpus remains representative. The actual full corpus may be substantially different.

## 4. Embedding Cost

No embedding provider or model is configured, so an actual embedding cost cannot currently be calculated.

- Current estimated input: 17,404 tokens.
- Full-target estimated input: 6,961,600 tokens.
- Cost formula: (input tokens / 1,000,000) × provider price per million tokens.
- Convert the provider's price to INR using the applicable exchange rate when estimating rupee cost.

**Question: Is embedding cost a problem?** It cannot be determined until a provider and model price are selected. The full-target token estimate above is the input needed for that calculation.

## 5. PostgreSQL Storage

The extracted text alone occupies 69,618 UTF-8 bytes locally. This is not a measurement of PostgreSQL storage.

Database storage also includes row, index, JSONB, and database overhead. Vector storage cannot be estimated reliably until the embedding dimensions and storage format are selected.

**Question: Do vectors and text fit in free PostgreSQL?** Check the actual database provider dashboard for its current storage limit and current usage. Compare those values with a database-side measurement after loading the full corpus. Do not treat local text bytes as total database size.

## 6. Least Certain Estimate

The least certain number is the full-target token projection because it assumes the current files represent all future rules and documents.

A better measurement is to collect a representative sample across all target operating systems and file types, count tokens using the selected embedding model's tokenizer, and then project by source category.

## 7. What Changes at 10x Corpus Size?

- At 10x the current corpus, the rough estimate is 174,040 tokens and 349 chunks of 500 tokens each.
- Re-measure database storage, indexing, ingestion time, query latency, and embedding cost; do not assume they scale linearly.

## 8. Current Limitations

- No embedding provider or model is configured.
- Token count is estimated rather than measured with a model tokenizer.
- PostgreSQL storage usage and provider quota have not been measured here.
- Vector dimensions and vector storage overhead are not yet known.
- The full target corpus has not been collected.
- Production load and query performance have not been benchmarked.

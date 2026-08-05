# Experimental Setup

## Where the parameters live

Every executed constant is declared in
`src/from_russia_with_love/scenario.py`, which is the single source of truth
shared by the mission adapter, the manuscript token generator, and both figure
generators. `manuscript/config.yaml` restates the headline mission parameters
for a human reader and supplies the paper metadata (title, authors, keywords);
`manuscript_variables.validate_mission_config()` compares the two on every
manuscript build and raises if they disagree, so the restatement cannot drift
away from the code silently.

The token generator reads `config.yaml` for paper metadata only. Every
quantitative token below is computed by running the engines.

## Mission parameters

| Parameter | Value |
|---|---|
| Objectives | {{LURES_NUM_OBJECTIVES}} |
| Fixed seed | {{LURES_SEED}} |
| Bait profiles | {{LURES_NUM_BAIT_PROFILES}} |
| Engagement threshold | {{LURES_ENGAGEMENT_THRESHOLD}} |
| Allocation targets | {{LURES_ALLOC_TARGETS}} |
| Lure strength | {{LURES_ALLOC_LURE_STRENGTH}} |
| Lure budget (units) | {{LURES_ALLOC_BUDGET}} |
| Message length (bytes) | {{LURES_MESSAGE_BYTES}} |
| Cipher layers | {{LURES_CIPHER_LAYERS}} |
| Requested channel SNR | {{LURES_SNR_DB}} dB |
| TDOA intercept sites | {{LURES_NUM_RECEIVERS}} |
| TDOA timing noise (s) | {{LURES_TDOA_NOISE_STD}} |
| Candidate rendezvous | {{LURES_SCHEDULE_TOTAL}} |

## Software Environment

| Component | Value |
|---|---|
| Python | {{PYTHON_VERSION}} |
| Platform | {{PLATFORM}} |
| numpy | {{NUMPY_VERSION}} |
| Package version | {{BOND_VERSION}} |
| Generated | {{GENERATION_TIMESTAMP}} |

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
| Analytical engines | {{LURES_NUM_ENGINES}} |
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
| TDOA receiver coordinates | {{LURES_TDOA_RECEIVER_COORDS}} |
| TDOA true transmitter | {{LURES_TDOA_TRANSMITTER}} |
| TDOA minimum site spacing (coordinate units) | {{LURES_TDOA_SITE_SPACING}} |
| TDOA timing noise (s) | {{LURES_TDOA_NOISE_STD}} |
| Candidate rendezvous | {{LURES_SCHEDULE_TOTAL}} |
| Greedy-witness targets / budget | {{LURES_WITNESS_TARGETS}} / {{LURES_WITNESS_BUDGET}} |

Receiver and transmitter positions are dimensionless coordinates in the
scenario frame, and `TDOA_SPEED` is 1.0, so distance and time share units. The
localisation error reported in §3.3 is therefore in these coordinate units;
the site spacing row is what converts it to units of site spacing.

## Software Environment

| Component | Value |
|---|---|
| Python | {{PYTHON_VERSION}} |
| Platform | {{PLATFORM}} |
| numpy | {{NUMPY_VERSION}} |
| Package version | {{BOND_VERSION}} |
| Manuscript date (`config.yaml` `paper.date`) | {{MANUSCRIPT_DATE}} |

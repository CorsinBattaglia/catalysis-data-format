# Catalysis Data Format (.cdf)

> **Fork notice:** This project is a fork of [battery-data-alliance/battery-data-format](https://github.com/battery-data-alliance/battery-data-format), adapted for electrolyser and catalysis time-series data. The core I/O, validation, and metadata infrastructure is inherited from the upstream Battery Data Format (BDF); the column registry, file extension, package name, and scope have been updated for the catalysis domain.

## Why introduce a standard format for electrolyser data?

Electrolyser and catalysis laboratories generate vast amounts of time-series data across dozens of instrument vendors and software versions. Inconsistent column naming, unit conventions, and file formats make it difficult to compare results across labs or feed data into shared models.

The **Catalysis Data Format (CDF)** addresses this by providing:

- **Data Consistency**: A fixed table schema with canonical column names and SI units, eliminating per-vendor inconsistencies.
- **Model Compatibility**: A unified format that allows electrolyser model developers to accept CDF data without custom parsing for each source.

## Initial Scope of the CDF

- The initial scope covers electrolyser and electrocatalysis cycler time-series data.
- The CDF provides a fixed table schema supplemented with a machine-readable application ontology for integration with the Semantic Web.
- The column ontology reuses the BattINFO / Battery Data Alliance base where applicable and extends it with catalysis-specific quantities.

## Defining the CDF for Electrolyser Time-Series Data

1. **Each file contains time-series data for one and only one test object.**
   - Multiple files can be provided for the same device.

2. **Required quantities**

| Preferred Label       | Machine-readable name   | IRI                                                                                         | Description                                                                 |
|-----------------------|--------------------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Test Time / s         | `test_time_second`       | [battery-data-format#test_time_second](https://w3id.org/battery-data-alliance/ontology/battery-data-format#test_time_second)      | Elapsed time since the start of the test, recorded in seconds              |
| Voltage / V           | `voltage_volt`           | [battery-data-format#voltage_volt](https://w3id.org/battery-data-alliance/ontology/battery-data-format#voltage_volt)          | Instantaneous cell voltage (or stack voltage) measured during the test      |
| Current / A           | `current_ampere`         | [battery-data-format#current_ampere](https://w3id.org/battery-data-alliance/ontology/battery-data-format#current_ampere)        | Instantaneous current applied to or drawn from the test object             |

3. **Recommended quantities**

| Preferred Label              | Machine-readable name         | IRI                                                                                               | Description                                                                 |
|-------------------------------|--------------------------------|----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Unix Time / s                 | `unix_time_second`             | [battery-data-format#unix_time_second](https://w3id.org/battery-data-alliance/ontology/battery-data-format#unix_time_second)            | Timestamp in Unix time format (seconds since 1970-01-01 UTC)               |
| Cycle Count / 1               | `cycle_count`                  | [battery-data-format#cycle_count](https://w3id.org/battery-data-alliance/ontology/battery-data-format#cycle_count)                 | Monotonically increasing index of test cycles                              |
| Step Count / 1                | `step_count`                   | [battery-data-format#step_count](https://w3id.org/battery-data-alliance/ontology/battery-data-format#step_count)                  | Monotonically increasing index of steps within the program                 |
| Ambient Temperature / degC    | `ambient_temperature_celsius`  | [battery-data-format#ambient_temperature_celsius](https://w3id.org/battery-data-alliance/ontology/battery-data-format#ambient_temperature_celsius)     | Temperature of the surrounding environment during testing                  |

4. **Optional quantities**

| Preferred Label                        | Machine-readable name                    | IRI                                                                                                     | Description                                                                              |
|----------------------------------------|------------------------------------------|---------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| Step Index / 1                         | `step_index`                             | [battery-data-format#step_index](https://w3id.org/battery-data-alliance/ontology/battery-data-format#step_index)                      | Index indicating the position of the data point within a step                           |
| Charging Capacity / Ah                 | `charging_capacity_ah`                   | [battery-data-format#charging_capacity_ah](https://w3id.org/battery-data-alliance/ontology/battery-data-format#charging_capacity_ah)            | Capacity accumulated during charging within a given interval                            |
| Discharging Capacity / Ah              | `discharging_capacity_ah`                | [battery-data-format#discharging_capacity_ah](https://w3id.org/battery-data-alliance/ontology/battery-data-format#discharging_capacity_ah)         | Capacity delivered during discharging within a given interval                           |
| Step Capacity / Ah                     | `step_capacity_ah`                       | [battery-data-format#step_capacity_ah](https://w3id.org/battery-data-alliance/ontology/battery-data-format#step_capacity_ah)                | Net capacity change over a given step                                                   |
| Net Capacity / Ah                      | `net_capacity_ah`                        | [battery-data-format#net_capacity_ah](https://w3id.org/battery-data-alliance/ontology/battery-data-format#net_capacity_ah)                 | Charging capacity minus discharging capacity within a given interval                    |
| Cumulative Capacity / Ah               | `cumulative_capacity_ah`                 | [battery-data-format#cumulative_capacity_ah](https://w3id.org/battery-data-alliance/ontology/battery-data-format#cumulative_capacity_ah)          | Total capacity accumulated over a given interval                                        |
| Charging Energy / Wh                   | `charging_energy_wh`                     | [battery-data-format#charging_energy_wh](https://w3id.org/battery-data-alliance/ontology/battery-data-format#charging_energy_wh)              | Energy input during charging, computed as ∫V·I·dt over a charging interval             |
| Discharging Energy / Wh                | `discharging_energy_wh`                  | [battery-data-format#discharging_energy_wh](https://w3id.org/battery-data-alliance/ontology/battery-data-format#discharging_energy_wh)           | Energy output during discharging, computed as ∫V·I·dt over a discharging interval      |
| Step Energy / Wh                       | `step_energy_wh`                         | [battery-data-format#step_energy_wh](https://w3id.org/battery-data-alliance/ontology/battery-data-format#step_energy_wh)                  | Net energy change during the current step                                               |
| Net Energy / Wh                        | `net_energy_wh`                          | [battery-data-format#net_energy_wh](https://w3id.org/battery-data-alliance/ontology/battery-data-format#net_energy_wh)                   | Charging energy minus discharging energy over a given interval                          |
| Cumulative Energy / Wh                 | `cumulative_energy_wh`                   | [battery-data-format#cumulative_energy_wh](https://w3id.org/battery-data-alliance/ontology/battery-data-format#cumulative_energy_wh)            | Total energy accumulated over a given interval                                          |
| Power / W                              | `power_watt`                             | [battery-data-format#power_watt](https://w3id.org/battery-data-alliance/ontology/battery-data-format#power_watt)                      | Instantaneous power calculated as the product of voltage and current                    |
| Internal Resistance / ohm              | `internal_resistance_ohm`                | [battery-data-format#internal_resistance_ohm](https://w3id.org/battery-data-alliance/ontology/battery-data-format#internal_resistance_ohm)         | Internal resistance of the test object                                                  |
| Ambient Pressure / Pa                  | `ambient_pressure_pa`                    | [battery-data-format#ambient_pressure_pa](https://w3id.org/battery-data-alliance/ontology/battery-data-format#ambient_pressure_pa)             | Ambient air pressure recorded during testing                                            |
| Applied Pressure / Pa                  | `applied_pressure_pa`                    | [battery-data-format#applied_pressure_pa](https://w3id.org/battery-data-alliance/ontology/battery-data-format#applied_pressure_pa)             | External pressure applied to the test object                                            |
| Surface Temperature T1 / degC         | `temperature_t1_celsius`                 | [battery-data-format#temperature_t1_celsius](https://w3id.org/battery-data-alliance/ontology/battery-data-format#temperature_t1_celsius)          | Temperature at external sensor location T1 on the test object                           |
| Surface Temperature T2 / degC         | `temperature_t2_celsius`                 | [battery-data-format#temperature_t2_celsius](https://w3id.org/battery-data-alliance/ontology/battery-data-format#temperature_t2_celsius)          | Temperature at external sensor location T2 on the test object                           |
| Surface Temperature T3 / degC         | `temperature_t3_celsius`                 | [battery-data-format#temperature_t3_celsius](https://w3id.org/battery-data-alliance/ontology/battery-data-format#temperature_t3_celsius)          | Temperature at external sensor location T3 on the test object                           |
| Surface Temperature T4 / degC         | `temperature_t4_celsius`                 | [battery-data-format#temperature_t4_celsius](https://w3id.org/battery-data-alliance/ontology/battery-data-format#temperature_t4_celsius)          | Temperature at external sensor location T4 on the test object                           |
| Surface Temperature T5 / degC         | `temperature_t5_celsius`                 | [battery-data-format#temperature_t5_celsius](https://w3id.org/battery-data-alliance/ontology/battery-data-format#temperature_t5_celsius)          | Temperature at external sensor location T5 on the test object                           |
| Working Electrode Potential / V        | `working_electrode_potential_volt`       | [catalysis-data-format#working_electrode_potential_volt](https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#working_electrode_potential_volt) | Potential measured at the working electrode vs. the reference electrode                 |
| Counter Electrode Potential / V        | `counter_electrode_potential_volt`       | [catalysis-data-format#counter_electrode_potential_volt](https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#counter_electrode_potential_volt) | Potential measured at the counter electrode                                             |
| Reference Electrode Potential / V      | `reference_electrode_potential_volt`     | [catalysis-data-format#reference_electrode_potential_volt](https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#reference_electrode_potential_volt) | Absolute potential of the reference electrode                                           |
| Cell Resistance / ohm                  | `cell_resistance_ohm`                    | [catalysis-data-format#cell_resistance_ohm](https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#cell_resistance_ohm)           | Total ohmic resistance of the electrolyser cell                                         |
| Faradaic Efficiency / %                | `faradaic_efficiency_percent`            | [catalysis-data-format#faradaic_efficiency_percent](https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#faradaic_efficiency_percent)     | Ratio of measured product yield to theoretical yield from charge passed                 |
| Gas Flow Rate / mL/min                 | `gas_flow_rate_ml_min`                   | [catalysis-data-format#gas_flow_rate_ml_min](https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#gas_flow_rate_ml_min)          | Volumetric flow rate of product gas measured at the cell outlet                         |
| Electrolyte pH / 1                     | `electrolyte_ph`                         | [catalysis-data-format#electrolyte_ph](https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#electrolyte_ph)                | pH of the electrolyte solution during the experiment                                    |
| Product Concentration / mol/L          | `product_concentration_mol_l`            | [catalysis-data-format#product_concentration_mol_l](https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#product_concentration_mol_l)    | Molar concentration of the target product in the electrolyte or gas phase               |

5. **Data structure**:
   - The first row contains a header row with the preferred label of the quantity in the corresponding column.
   - The units of the quantities are fixed.
   - All rows must match the initial header in column count, ensuring consistent formatting.

6. **File naming conventions**:
   - Recommended format:
     ```
     InstitutionCode__DeviceName__YYYYMMDD_XXX.cdf.csv
     ```
     Example:
     ```
     Empa__EL0001__20250101_001.cdf.csv
     ```
   - Additional metadata should be stored in a parallel metadata file (JSON-LD sidecar).

7. **File extension**:
   - Files using text-based serialization are saved with the `.cdf` extension prefix.
   - Binary formats: `example.cdf.parquet`, `example.cdf.feather`
   - Compressed CSV: `example.cdf.csv.gz`
   - It is assumed that `.cdf` files adhere to the CDF conventions; validator functions enforce this.

## Install the Python Package

```bash
pip install catalysisdf
# Interactive plotting (hvplot/bokeh)
pip install catalysisdf[hvplot]
# Polars + fast NDA backend
pip install catalysisdf[polars]
# Force numpy 2.x
pip install catalysisdf[numpy2]
# for docs/dev: pip install -e .[dev,docs]
```

PyPI distribution name is `catalysisdf`; Python import and CLI use `cdf`.

### Quickstart

```python
import cdf

# Read raw or CDF; plugin auto-detects
df = cdf.read("path/to/file.cdf.csv")

# Read Neware .nda/.ndax (supported by default)
df = cdf.read("path/to/file.nda")

# Interactive exploration
cdf.explore(df, xdata="Test Time / s", ydata="Voltage / V", yydata="Current / A", backend="plotly")

# Validate
report = cdf.validate(df, report=True, raise_on_error=False)

# Repair time/outliers
df_clean, rep = cdf.clean(df, time_fix="segment", outlier="none")

# Plot
cdf.plot(df_clean, xdata="Test Time / s", ydata=["Voltage / V"], save="plot.png")

# Ingest a folder of raw files into CDF artifacts
summary = cdf.ingest("data/raw", out_dir="data/cdf", format="parquet")
```

CLI examples:

```bash
cdf validate data/sample.cdf.csv
cdf clean data/sample.cdf.csv --out cleaned.cdf.csv
cdf convert raw/vendor.csv --to output.cdf.csv
cdf plot data/sample.cdf.csv --save plot.png
cdf meta-jsonld data/sample.cdf.csv --title "My dataset" --description "..." --creator "Name|ORCID|Affiliation"
cdf templates contribution battery excel --root my-contribution
cdf ingest my-contribution --raw-dir timeseries/raw --data-dir timeseries
```

### Documentation

Full docs (API, CLI, examples) are built with Sphinx/pydata theme. After build, browse `docs/_build/html/index.html`.

## Fork Attribution

This project is a community fork of the [Battery Data Format](https://github.com/battery-data-alliance/battery-data-format) by the Battery Data Alliance (a Linux Foundation Energy project), released under the Apache-2.0 licence. The CDF diverges in scope (electrolyser/catalysis instead of battery cyclers), column registry, file extension (`.cdf`), and package name (`catalysisdf` / `cdf`). All upstream contributions are gratefully acknowledged.

## FAQ

### Which label should I use for my column headings?

Use the Preferred Label for column headings. It follows IUPAC/SI notation (`Quantity / Unit`) and corresponds to the `csvw:titles` property in the table schema.

### What is the difference between the preferred label and the machine-readable name?

The preferred label is human-readable and follows IUPAC/SI guidelines. The machine-readable name is a snake_case alias suitable for use in software. Both are linked in the CDF ontology and the CSVW table schema.

### Why do we use a slash between the quantity and the unit?

This follows IUPAC and SI recommendations. The slash comes from the algebraic convention: if `Voltage = 4.2 V`, dividing both sides by `V` gives `Voltage / V = 4.2`.

### How can I check if my file is a valid CDF instance?

```bash
cdf validate path/to/file.cdf.csv
```

Or in Python:

```python
import cdf
report = cdf.validate("path/to/file.cdf.csv", report=True)
```

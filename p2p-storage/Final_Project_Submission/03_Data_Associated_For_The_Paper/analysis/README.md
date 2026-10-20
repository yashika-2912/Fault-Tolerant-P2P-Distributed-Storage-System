# Analysis files

`collect_results.py` normalizes the preserved harness measurements and checks replica mappings against SQLite metadata and isolated node files. Run it with the same base Python environment used for the experiments if refreshing environment package versions. `analyze_results.py` calculates means, medians and sample standard deviations, writes the Excel workbook, and regenerates plots; it requires Matplotlib and XlsxWriter (available in the documentation environment).

Plots: upload latency, download latency, effective decimal Mbps throughput, and failure detection/recovery. Error bars show sample standard deviation across three trials. All plotted points come from measured CSV rows.

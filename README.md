# CityJSON: does (file) size matter?
MSc Geomatics thesis

- benchmark_ia: contains raw benchmark results for "compression in advance".
- benchmark_otf: contains raw benchmark results for "compression on the fly".
- benchmark_other: contains files for other benchmarking parts.
- code: contains code of the different compression types and the two server implementations.
- datasets: to place the datasets in (separate download).
- files: folder for temporary storage, used by some compression scripts.
- P5: contains the thesis.

I have only updated OTF compression to be easier to use and also will provide an explanation for that one. However, as for the other server implementation, things work similarly.

Download link to datasets:
https://drive.google.com/file/d/1lZENt6a1r1yH4fTY_OXD1ixmsExCQ4dm/view?usp=sharing

If the link is ever down in the future, try the original sources (as found in Section 5.5 of the thesis) or use your own datasets!


Running the server + benchmark:
1. Place the datasets that you want to use in `/datasets/original`. All files in this folder would be benchmarked by the benchmarking script.
1. Make sure Flask is installed.
1. cd to `/code/cjflask_otf/cjflask`.
1. Add `FLASK_APP=cjflask` to path (Windows: `set FLASK_APP=cjflask`).
1. `flask run` — the server should now be running.
1. Run `/code/flask_benchmark.py` to start benchmark (update the `base_url` variable with the local address on which Flask serves the app). It will output raw results in `/code/benchmark`.
1. First run `/code/benchmark_report.py` to create `.csv` of results (in which results are compared to performance with original datasets), then run `plot_performance.R` to create plots in `/code/benchmark`.

Customising the benchmark:
* If you want to only perform some of the operations, alter `flask_urls` and `tasks` in `flask_benchmark.py` accordingly.
* The amount of test iterations can be altered by both changing `test_i` in `flask_benchmark.py` and `cjrest.py`.
* If you are using other datasets, you need to add information on it in `code/benchmark_info.json` which is used for the query operations.

Other remarks:
* If you want to use Draco compression, place the build in the main folder of the repo.

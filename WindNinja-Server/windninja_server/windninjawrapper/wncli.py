from datetime import datetime
import pytz
import dateutil.parser
import dateutil.tz
import glob
import logging
import os
import shutil
import re

from string import Template
from config import CONFIG
from utility import execute_shell_process

_tzinfos = {
    "EST": dateutil.tz.gettz("America/New_York"),
    "EDT": dateutil.tz.gettz("America/New_York"),
    "CST": dateutil.tz.gettz("America/Chicago"),
    "CDT": dateutil.tz.gettz("America/Chicago"),
    "MST": dateutil.tz.gettz("America/Denver"),
    "MDT": dateutil.tz.gettz("America/Denver"),
    "PST": dateutil.tz.gettz("America/Los_Angeles"),
    "PDT": dateutil.tz.gettz("America/Los_Angeles"),
    "AKST": dateutil.tz.gettz("America/Anchorage"),
    "AKDT": dateutil.tz.gettz("America/Anchorage"),
}

_sim_time_line_pattern = (
    "Run \d*: Simulation time is \d*-[A-Za-z]*-\d* \d*:\d*:\d* [A-Z]{3,4}"
)
_sim_time_line_sep = " is "

_sim_shp_name_template = "{}_{:%m-%d-%Y_%H%M}_*m.*"
_sim_shp_rename_template = "{:%Y%m%dT%H%M}{}"

_sim_asc_types = ["vel", "ang", "cld"]
_sim_asc_name_template = "{}_{:%m-%d-%Y_%H%M}_*m_{}.*"
_sim_asc_rename_template = "{:%Y%m%dT%H%M}_{}{}"

_sim_wx_name_template = "{}-{:%m-%d-%Y_%H%M}.*"
_sim_wx_rename_template = "WX_{:%Y%m%dT%H%M}{}"


def parse_shell_output(output):
    simulation_times = []
    # find all the simulation time lines and convert to date objects
    # excluding past forecasts expect for the currenst hour
    utc_now = pytz.utc.localize(datetime.utcnow())
    max_total_seconds = 60 * 60
    lines = re.findall(_sim_time_line_pattern, output)
    for l in lines:
        parts = l.partition(" is ")
        dt = dateutil.parser.parse(parts[2], tzinfos=_tzinfos)
        if (dt > utc_now) or ((utc_now - dt).total_seconds() <= max_total_seconds):
            simulation_times.append(dt)

    return simulation_times


def process_sim_shpfiles(in_folder, out_folder, dem_name, sim_times):
    shp = []
    for sim in sim_times:
        file_pattern = _sim_shp_name_template.format(dem_name, sim)
        file_search = os.path.join(in_folder, file_pattern)
        for f in glob.glob(file_search):
            ext = os.path.splitext(f)[1]
            new_name = _sim_shp_rename_template.format(sim, ext)
            new_file = os.path.join(out_folder, new_name)
            os.rename(f, new_file)
            if ext == ".shp":
                shp.append(new_name)

    return shp


def process_sim_ascfiles(in_folder, out_folder, dem_name, sim_times):
    asc = []
    for sim in sim_times:
        for t in _sim_asc_types:
            file_pattern = _sim_asc_name_template.format(dem_name, sim, t)
            file_search = os.path.join(in_folder, file_pattern)
            for f in glob.glob(file_search):
                ext = os.path.splitext(f)[1]
                new_name = _sim_asc_rename_template.format(sim, t, ext)
                new_file = os.path.join(out_folder, new_name)
                os.rename(f, new_file)
                if ext == ".asc":
                    asc.append(new_name)
    return asc


def process_sim_wxfiles(in_folder, out_folder, forecast_name, sim_times):
    wx = []
    for sim in sim_times:
        file_pattern = _sim_wx_name_template.format(forecast_name, sim)
        file_search = os.path.join(in_folder, file_pattern)
        for f in glob.glob(file_search):
            ext = os.path.splitext(f)[1]
            new_name = _sim_wx_rename_template.format(sim, ext)
            new_file = os.path.join(out_folder, new_name)
            os.rename(f, new_file)
            if ext == ".shp":
                wx.append(new_name)

    return wx


def execute_wncli(working_dir, override_args_dict, dem_path, forecast, shp, asc, wxshp):

    # process inputs
    dem_name = os.path.splitext(os.path.basename(dem_path))[0]

    # create the cli results folder
    output_folder = os.path.join(working_dir, "output")
    os.makedirs(output_folder)
    logging.debug("WN CLI output folder: {}".format(output_folder))

    # defaults
    cli = CONFIG.WN_CLI_DEFAULTS.copy()

    # overrides
    cli.update(override_args_dict)

    # mandatory
    cli["output_path"] = output_folder
    cli["initialization_method"] = (
        "domainAverageInitialization"
        if (forecast == "NONE")
        else "wxModelInitialization"
    )
    cli["elevation_file"] = dem_path
    cli["wx_model_type"] = forecast

    # outputs
    cli["write_shapefile_output"] = "true" if (shp) else "false"
    cli["write_ascii_output"] = "true" if (asc) else "false"
    cli["write_wx_model_shapefile_output"] = "true" if (wxshp) else "false"

    # create the correct command line template
    if forecast == "NONE":
        cli_template = Template(
            "{0} {1}".format(CONFIG.WN_CLI_PATH, CONFIG.WN_CLI_ARGS_DA)
        )
    else:
        cli_template = Template(
            "{0} {1}".format(CONFIG.WN_CLI_PATH, CONFIG.WN_CLI_ARGS_WX)
        )

    # execute the command
    command = cli_template.substitute(cli)
    env = CONFIG.WN_CLI_ENV
    shell_result = execute_shell_process(command, working_dir, env=env)

    # process results
    if shell_result[0]:
        # create a folder to handle the processes files
        result_folder = os.path.join(working_dir, "results")
        os.makedirs(result_folder)
        logging.debug("WN CLI result folder: {}".format(result_folder))

        # get the simulation times
        simulations = parse_shell_output(shell_result[1])
        # TODO: filter out any "past" results and forecasts

        # get the output files
        windninja_ascfiles = process_sim_ascfiles(
            output_folder, result_folder, dem_name, simulations
        )
        logging.debug("ASC output files: {0}".format(windninja_ascfiles))

        weather_shapefiles = process_sim_wxfiles(
            output_folder, result_folder, forecast, simulations
        )
        logging.debug("WX output files: {0}".format(weather_shapefiles))

        windninja_shapefiles = process_sim_shpfiles(
            output_folder, result_folder, dem_name, simulations
        )
        logging.debug("SHP output files: {0}".format(windninja_shapefiles))

        if shp and len(windninja_shapefiles) == 0:
            result = (
                False,
                "WindNinjaCLI did not produce windninja shapefile outputs for the job parameters",
            )
        elif asc and len(windninja_ascfiles) == 0:
            result = (
                False,
                "WindNinjaCLI did not produce windninja ascii outputs for the job parameters",
            )
        elif wxshp and len(weather_shapefiles) == 0:
            result = (
                False,
                "WindNinjaCLI did not produce weather shapefiles outputs for the job parameters",
            )
        else:
            result = (
                True,
                result_folder,
                simulations,
                windninja_shapefiles,
                windninja_ascfiles,
                weather_shapefiles,
            )

        # cleanup the unnecessary files, but ignore any errors while trying
        # TODO: create config flag to skip for easier review/triage of failures
        shutil.rmtree(output_folder, ignore_errors=True)

    else:
        # pass error result back
        result = shell_result

    return result


if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.debug("Starting test...")

    # with open(r"T:\temp\wn_examples\filestore\job\1a111111111111111111111111111111\wncli\cli3.txt") as f:
    #    txt = f.read()
    # _test_shell_output = (True,txt)

    # _test_shell_output = (True, r"Run 0: Reading elevation file...\nRun 1: Reading elevation file...\nRun 0: Simulation time is 2017-Sep-18 14:00:00 MST\nRun 1: Simulation time is 2017-Sep-18 17:00:00 MST\nRun 0: Run number 0 started with 1 threads.\nRun 0: Generating mesh...\nRun 1: Run number 1 started with 1 threads.\nRun 1: Generating mesh...\nRun 0: Initializing flow...\nRun 1: Initializing flow...\nRun 0: Building equations...\nRun 1: Building equations...\nRun 0: Solving...\nRun 1: Solving...\nRun 0 (solver): 21% complete\nRun 1 (solver): 21% complete\nRun 0 (solver): 41% complete\nRun 1 (solver): 40% complete\nRun 0 (solver): 65% complete\nRun 1 (solver): 64% complete\nRun 0 (solver): 83% complete\nRun 1 (solver): 83% complete\nRun 0 (solver): 93% complete\nRun 1 (solver): 93% complete\nRun 1 (solver): 98% complete\nRun 0 (solver): 99% complete\nRun 1 (solver): 100% complete\nRun 0 (solver): 100% complete\nRun 1: Writing output files...\nRun 0: Writing output files...\nRun 1: Meshing time was 0.017949 seconds.\nRun 1: Initialization time was 0.254373 seconds.\nRun 1: Equation building time was 0.926174 seconds.\nRun 1: Solver time was 2.843869 seconds.\nRun 1: Output writing time was 0.529173 seconds.\nRun 1: Total simulation time was 4.951126 seconds.\nRun 1: Run number 1 done!\nRun 0: Meshing time was 0.017775 seconds.\nRun 0: Initialization time was 0.200980 seconds.\nRun 0: Equation building time was 0.926766 seconds.\nRun 0: Solver time was 2.924539 seconds.\nRun 0: Output writing time was 0.552882 seconds.\nRun 0: Total simulation time was 4.984620 seconds.\nRun 0: Run number 0 done!")
    # _test_folder=r"T:\temp\wn_examples\wn_cli\output"
    # _test_dem_name = "dem"
    # _test_forecast_name = "NOMADS-NAM-CONUS-12-KM"

    # sims, clnup = parse_shell_output(_test_shell_output[1])
    # print(sims)
    # print(clnup)

    # shp = process_sim_shpfiles(_test_folder, sims, _test_dem_name)
    # print(shp)

    # asc = process_sim_ascfiles(_test_folder, sims, _test_dem_name)
    # print(asc)

    # wx = process_sim_wxfiles(_test_folder, sims, _test_forecast_name)
    # print(wx)
    wncli_folder = r"T:\temp\wn_examples\1a111111111111111111111111111111\wncli"
    override_args = {
        ptr.split(":")[0]: ptr.split(":")[1]
        for ptr in "forecast_duration:6;vegetation:trees;mesh_choice:fine".split(";")
    }
    demPath = r"T:\temp\wn_examples\1a111111111111111111111111111111\wncli\dem.tif"
    forecast = "NOMADS-NAM-CONUS-12-KM"
    result = execute_wncli(
        wncli_folder, override_args, demPath, forecast, True, True, True
    )
    print(result)

    logging.debug("...test complete")

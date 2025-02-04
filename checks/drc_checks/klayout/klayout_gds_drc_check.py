import argparse
import logging
import subprocess
from pathlib import Path


def klayout_gds_drc_check(check_name, drc_script_path, gds_input_file_path, output_directory, klayout_cmd_extra_args=[]):
    report_file_path = output_directory / 'outputs/reports' / f'{check_name}_check.xml'
    logs_directory = output_directory / 'logs'
    run_drc_check_cmd = ['klayout', '-b', '-r', drc_script_path,
                         '-rd', f"input={gds_input_file_path}",
                         '-rd', f"report={report_file_path}"]
    run_drc_check_cmd.extend(klayout_cmd_extra_args)

    log_file_path = logs_directory / f'{check_name}_check.log'
    with open(log_file_path, 'w') as klayout_drc_log:
        subprocess.run(run_drc_check_cmd, stderr=klayout_drc_log, stdout=klayout_drc_log)

    with open(report_file_path) as klayout_xml_report:
        drc_content = klayout_xml_report.read()
        drc_count = drc_content.count('<item>')
        total_file_path = logs_directory / f'{check_name}_check.total'
        with open(total_file_path, 'w') as drc_total:
            drc_total.write(f"{drc_count}")
        if drc_count == 0:
            logging.info("No DRC Violations found")
            return True
        else:
            logging.error(f"Total # of DRC violations is {drc_count} Please check {report_file_path} For more details")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format=f"%(asctime)s | %(levelname)-7s | %(message)s", datefmt='%d-%b-%Y %H:%M:%S')
    parser = argparse.ArgumentParser(description='Runs magic and klayout drc checks on a given GDS.')
    parser.add_argument('--gds_input_file_path', '-g', required=True, help='GDS File to apply DRC checks on')
    parser.add_argument('--output_directory', '-o', required=True, help='Output Directory')
    parser.add_argument('--pdk_root', '-p', required=True, help='PDK Path')
    parser.add_argument('--design_name', '-d', required=True, help='Design Name')
    args = parser.parse_args()

    gds_input_file_path = Path(args.gds_input_file_path)
    output_directory = Path(args.output_directory)
    pdk_root = Path(args.pdk_root)
    design_name = args.design_name

    klayout_sky130A_mr_drc_script_path = Path(__file__).parent.parent.parent / "tech-files/sky130A_mr.drc"

    if gds_input_file_path.exists() and gds_input_file_path.suffix == ".gds":
        if output_directory.exists() and output_directory.is_dir():
            if klayout_gds_drc_check("klayout_feol_drc", gds_input_file_path, klayout_sky130A_mr_drc_script_path, output_directory, ["-rd", "feol=true"]):
                logging.info("Klayout GDS DRC Clean")
            else:
                logging.info("Klayout GDS DRC Dirty")
        else:
            logging.error(f"{output_directory} is not valid")
    else:
        logging.error(f"{gds_input_file_path} is not valid")

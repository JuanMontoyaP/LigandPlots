"""
This script is the main script for the project. It will be used to run the project.
"""
from pathlib import Path
import logging
import click

from gromacs import GromacsData
from plots import Plots

logging.basicConfig(
    format='[%(asctime)s] - %(levelname)s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s',
    level=logging.DEBUG
)


class LigandPlots:
    """
    Class
    """

    def __init__(self, path: Path, protein: str, run_gromacs: bool) -> None:
        self.path: Path = path
        self.protein: str = protein
        self.run_gromacs: bool = run_gromacs

    def generate_gromacs_data(self):
        gromacs = GromacsData(self.path)

        logging.info('Generating minimization data')
        energy_minimization = gromacs.generate_minimization_data()
        logging.info(energy_minimization)

        logging.info('Generating NVT data')
        temperature_data = gromacs.generate_nvt_data()
        logging.info(temperature_data)

        logging.info('Generating NPT data')
        npt_data = gromacs.generate_npt_data()
        logging.info(npt_data)

        if self.run_gromacs:
            logging.info('Generate final XTC file')
            gromacs.generate_final_xtc_file()
            periodicity = gromacs.fix_periodicity()
            logging.info(periodicity)

        logging.info('Generate initial configuration file')
        gromacs.get_initial_configuration()

        logging.info('Generate last configuration file')
        gromacs.get_latest_configuration()

        # TODO: Add RNSD calculation and radius of gyration calculation for the protein

        # TODO: Add rmsd between ligand and protein

    def generate_ligand_plots(self):
        plots = Plots(self.path, self.protein)

        logging.info("Plotting energy minimization")
        plots.plot_energy_minimization()

        logging.info("Plotting temperature")
        plots.plot_temperature()

        logging.info("Plotting pressure")
        plots.plot_pressure()

        logging.info("Plotting density")
        plots.plot_density()

    def Run(self):
        """
        Runs the ligand plot generation process.

        This method generates Gromacs data and then generates ligand plots using
        the generated data.

        Returns:
            None
        """
        logging.info('Running LigandPlots')
        self.generate_gromacs_data()

        logging.info('Generating gromacs plots')
        self.generate_ligand_plots()


@click.command()
@click.option(
    '--path',
    type=click.Path(
        exists=True,
        dir_okay=True,
        readable=True
    ),
    required=True,
    help="Path to the folder where the Gromacs data is."
)
@click.option(
    '--protein',
    type=str,
    required=True,
    help="Name of the protein to be analyzed."
)
@click.option(
    '--run-gromacs',
    is_flag=True,
    help="Run Gromacs data generation.",
    default=False
)
def cli(
    path: Path,
    protein: str,
    run_gromacs: bool = False
) -> None:
    """
    Run LigandPlots for a given path and protein.

    Args:
        path (Path): The path to the LigandPlots directory.
        protein (str): The name of the protein.

    Returns:
        None
    """
    ligand_plots = LigandPlots(
        path,
        protein,
        run_gromacs
    )
    ligand_plots.Run()


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
